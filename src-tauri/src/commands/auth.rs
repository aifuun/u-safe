//! 认证相关 IPC 命令
//!
//! 提供主密码设置、验证和状态查询命令

use tauri::State;
use crate::crypto::password::PasswordManager;

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
/// # Arguments
/// * `password` - 用户输入的主密码
///
/// # Returns
/// * `Ok(Vec<u8>)` - 派生的 32 字节密钥
/// * `Err` - 设置失败（已设置或派生失败）
#[tauri::command]
pub fn derive_master_key(
    password: String,
    password_manager: State<PasswordManager>
) -> Result<Vec<u8>, String> {
    log::info!("[auth:derive_master_key] 开始设置主密码");

    // 1. 检查是否已设置密码
    if password_manager.is_password_set() {
        log::error!("[auth:derive_master_key] 密码已设置,无法重复设置");
        return Err("密码已设置,无法重复设置".to_string());
    }

    // 2. 设置密码并持久化
    password_manager
        .set_password(&password)
        .map_err(|e| {
            log::error!("[auth:derive_master_key] 设置密码失败: {}", e);
            e.to_string()
        })?;

    // 3. 验证并返回密钥
    let key = password_manager
        .verify_password(&password)
        .map_err(|e| {
            log::error!("[auth:derive_master_key] 验证密码失败: {}", e);
            e.to_string()
        })?;

    log::info!("[auth:derive_master_key] 主密码设置成功");

    // 4. 返回 Vec<u8> (可序列化)
    Ok(key.to_vec())
}

/// 验证主密码
///
/// # Arguments
/// * `password` - 用户输入的密码
///
/// # Returns
/// * `Ok(Vec<u8>)` - 验证成功,返回 32 字节密钥
/// * `Err` - 验证失败（密码错误、账户锁定等）
#[tauri::command]
pub fn verify_password(
    password: String,
    password_manager: State<PasswordManager>
) -> Result<Vec<u8>, String> {
    log::info!("[auth:verify_password] 开始验证密码");

    password_manager
        .verify_password(&password)
        .map(|key| {
            log::info!("[auth:verify_password] 密码验证成功");
            key.to_vec()  // [u8; 32] → Vec<u8>
        })
        .map_err(|e| {
            log::warn!("[auth:verify_password] 密码验证失败: {}", e);
            e.to_string()
        })
}
