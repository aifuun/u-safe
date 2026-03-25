//! 认证相关 IPC 命令
//!
//! 提供主密码设置、验证和状态查询命令

use tauri::State;
use std::sync::Mutex;
use crate::crypto::password::PasswordManager;
use crate::crypto::keystore::KeyStore;
use crate::crypto::key::SecretKey;

/// 全局主密钥状态
///
/// 存储解密后的主密钥，供加密/解密操作使用
/// 注意：为了内存安全，不直接存储 SecretKey，而是存储其字节数组
pub struct MasterKeyState {
    key_bytes: Mutex<Option<[u8; 32]>>,
}

impl MasterKeyState {
    pub fn new() -> Self {
        MasterKeyState {
            key_bytes: Mutex::new(None),
        }
    }

    pub fn set(&self, key: SecretKey) {
        let mut guard = self.key_bytes.lock().unwrap();
        let mut bytes = [0u8; 32];
        bytes.copy_from_slice(key.as_slice());
        *guard = Some(bytes);
        log::info!("[master_key_state] 主密钥已设置到内存");
    }

    pub fn get(&self) -> Option<SecretKey> {
        let guard = self.key_bytes.lock().unwrap();
        guard.as_ref().map(|bytes| SecretKey::new(*bytes))
    }

    pub fn clear(&self) {
        let mut guard = self.key_bytes.lock().unwrap();
        if let Some(ref mut bytes) = *guard {
            // 清零内存
            for b in bytes.iter_mut() {
                *b = 0;
            }
        }
        *guard = None;
        log::info!("[master_key_state] 主密钥已从内存清除");
    }
}

/// 检查是否已设置主密码
///
/// # Returns
/// * `Ok(true)` - 已设置主密码
/// * `Ok(false)` - 尚未设置主密码
#[tauri::command]
pub fn is_master_key_set(
    password_manager: State<PasswordManager>
) -> Result<bool, String> {
    let is_set = password_manager.is_password_set();
    log::info!("[auth:is_master_key_set] 密码已设置: {}", is_set);
    Ok(is_set)
}

/// 设置主密码（首次设置）
///
/// 使用 Master Key Wrapping 模式：
/// 1. 检查是否首次设置（password.hash 和 master.key 都不存在）
/// 2. 设置密码并持久化 password.hash
/// 3. 生成随机主密钥（32字节）
/// 4. 用密码派生密钥加密主密钥，保存到 master.key
/// 5. 将解密后的主密钥保存到内存供后续使用
///
/// # Arguments
/// * `password` - 用户输入的主密码
/// * `password_manager` - 密码管理器状态
/// * `master_key_state` - 主密钥状态（存储解密后的主密钥）
///
/// # Returns
/// * `Ok(())` - 设置成功
/// * `Err` - 设置失败
#[tauri::command]
pub fn derive_master_key(
    password: String,
    password_manager: State<PasswordManager>,
    master_key_state: State<MasterKeyState>,
) -> Result<(), String> {
    log::info!("[auth:derive_master_key] 开始设置主密码");

    // 1. 检查是否已设置密码
    if password_manager.is_password_set() {
        log::error!("[auth:derive_master_key] 密码已设置,无法重复设置");
        return Err("密码已设置,无法重复设置".to_string());
    }

    // 2. 检查主密钥文件是否已存在
    let keystore = KeyStore::new();
    if keystore.exists() {
        log::error!("[auth:derive_master_key] 主密钥文件已存在,数据不一致");
        return Err("主密钥文件已存在，请联系技术支持".to_string());
    }

    // 3. 设置密码并持久化 password.hash
    password_manager
        .set_password(&password)
        .map_err(|e| {
            log::error!("[auth:derive_master_key] 设置密码失败: {}", e);
            e.to_string()
        })?;

    // 4. 从密码派生密钥（用于加密主密钥）
    let password_key = password_manager
        .verify_password(&password)
        .map_err(|e| {
            log::error!("[auth:derive_master_key] 密码派生失败: {}", e);
            e.to_string()
        })?;

    // 5. 生成随机主密钥并用密码密钥加密存储
    let master_key = keystore
        .generate_and_store(&password_key)
        .map_err(|e| {
            log::error!("[auth:derive_master_key] 生成主密钥失败: {}", e);
            e.to_string()
        })?;

    // 6. 将主密钥保存到内存供后续使用
    master_key_state.set(master_key);

    log::info!("[auth:derive_master_key] 主密码设置成功，主密钥已生成并存储");

    Ok(())
}

/// 验证主密码
///
/// 使用 Master Key Wrapping 模式：
/// 1. 验证密码（检查 password.hash）
/// 2. 用密码派生密钥解密主密钥（从 master.key 读取）
/// 3. 将解密后的主密钥保存到内存供后续使用
///
/// # Arguments
/// * `password` - 用户输入的密码
/// * `password_manager` - 密码管理器状态
/// * `master_key_state` - 主密钥状态
///
/// # Returns
/// * `Ok(())` - 验证成功
/// * `Err` - 验证失败（密码错误、账户锁定、主密钥损坏等）
#[tauri::command]
pub fn verify_password(
    password: String,
    password_manager: State<PasswordManager>,
    master_key_state: State<MasterKeyState>,
) -> Result<(), String> {
    log::info!("[auth:verify_password] 开始验证密码");

    // 1. 验证密码（检查 password.hash）
    let password_key = password_manager
        .verify_password(&password)
        .map_err(|e| {
            log::warn!("[auth:verify_password] 密码验证失败: {}", e);
            e.to_string()
        })?;

    // 2. 检查主密钥文件是否存在
    let keystore = KeyStore::new();
    if !keystore.exists() {
        log::error!("[auth:verify_password] 主密钥文件不存在");
        return Err("主密钥文件损坏，请联系技术支持".to_string());
    }

    // 3. 解密主密钥
    let master_key = keystore
        .load(&password_key)
        .map_err(|e| {
            log::error!("[auth:verify_password] 解密主密钥失败: {}", e);
            "密码错误或主密钥损坏".to_string()
        })?;

    // 4. 将主密钥保存到内存
    master_key_state.set(master_key);

    log::info!("[auth:verify_password] 密码验证成功，主密钥已加载");

    Ok(())
}

/// 修改主密码
///
/// 使用 Master Key Wrapping 架构的优势：
/// - 修改密码只需重新包装主密钥，无需重新加密所有文件
/// - 修改瞬间完成（<1秒）
///
/// 流程：
/// 1. 验证旧密码（防止未授权修改）
/// 2. 派生新密码的密钥
/// 3. 用新密钥重新加密主密钥（KeyStore::rewrap）
/// 4. 更新密码哈希文件（PasswordManager::update_password_hash）
///
/// # Arguments
/// * `old_password` - 用户当前密码
/// * `new_password` - 用户新密码
/// * `password_manager` - 密码管理器状态
///
/// # Returns
/// * `Ok(())` - 修改成功
/// * `Err` - 修改失败（旧密码错误、新密码不符合规则等）
#[tauri::command]
pub fn change_password(
    old_password: String,
    new_password: String,
    password_manager: State<PasswordManager>,
) -> Result<(), String> {
    log::info!("[auth:change_password] 开始修改密码");

    // 1. 验证旧密码
    let old_password_key = password_manager
        .verify_password(&old_password)
        .map_err(|e| {
            log::warn!("[auth:change_password] 旧密码验证失败: {}", e);
            format!("旧密码错误: {}", e)
        })?;

    log::info!("[auth:change_password] 旧密码验证成功");

    // 2. 派生新密码的密钥
    let (new_password_key, new_password_hash) = crate::crypto::kdf::derive_key(&new_password)
        .map_err(|e| {
            log::error!("[auth:change_password] 新密码派生失败: {}", e);
            format!("新密码派生失败: {}", e)
        })?;

    log::info!("[auth:change_password] 新密码密钥已派生");

    // 3. 用新密钥重新加密主密钥
    let keystore = KeyStore::new();
    keystore
        .rewrap(&old_password_key, &new_password_key)
        .map_err(|e| {
            log::error!("[auth:change_password] 重新包装主密钥失败: {}", e);
            format!("主密钥重新加密失败: {}", e)
        })?;

    log::info!("[auth:change_password] 主密钥已用新密码重新加密");

    // 4. 更新密码哈希
    password_manager
        .update_password_hash(&new_password_hash)
        .map_err(|e| {
            log::error!("[auth:change_password] 更新密码哈希失败: {}", e);
            format!("更新密码哈希失败: {}", e)
        })?;

    log::info!("[auth:change_password] 密码修改成功");

    Ok(())
}
