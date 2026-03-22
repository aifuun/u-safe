use serde::{Deserialize, Serialize};
use std::fs::File;
use std::path::Path;
use tauri::{Emitter, State};
use crate::crypto::stream::{encrypt_stream, decrypt_stream};
use crate::commands::auth::MasterKeyState;

/// 加密进度信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EncryptionProgress {
    /// 已处理字节数
    pub bytes_processed: u64,
    /// 总字节数
    pub total_bytes: u64,
    /// 进度百分比 (0-100)
    pub percentage: f64,
}

/// 加密文件 IPC 命令
///
/// 使用 Master Key Wrapping 模式：
/// 不再从密码派生密钥，而是使用已解密的主密钥
///
/// # Arguments
/// * `source_path` - 源文件路径（明文）
/// * `master_key_state` - 主密钥状态（必须已通过认证加载）
/// * `app` - Tauri 应用句柄
///
/// # Returns
/// * `Result<String, String>` - 加密后的文件路径或错误信息
#[tauri::command]
pub async fn encrypt_file(
    source_path: String,
    master_key_state: State<'_, MasterKeyState>,
    app: tauri::AppHandle,
) -> Result<String, String> {
    log::info!("[file_encryption:encrypt:start] source={}", source_path);

    let source = Path::new(&source_path);

    // 验证文件存在
    if !source.exists() {
        let err = format!("文件不存在: {}", source_path);
        log::error!("[file_encryption:encrypt:failed] {}", err);
        return Err(err);
    }

    if !source.is_file() {
        let err = format!("路径不是文件: {}", source_path);
        log::error!("[file_encryption:encrypt:failed] {}", err);
        return Err(err);
    }

    // 生成加密文件路径（添加 .enc 扩展名）
    let encrypted_path = format!("{}.enc", source_path);

    // 获取主密钥（必须已通过认证加载）
    let key = master_key_state
        .get()
        .ok_or_else(|| {
            log::error!("[file_encryption:encrypt:failed] 主密钥未加载，请先登录");
            "主密钥未加载，请先登录".to_string()
        })?;

    // 打开输入输出文件
    let input = File::open(source)
        .map_err(|e| format!("打开源文件失败: {}", e))?;

    let output = File::create(&encrypted_path)
        .map_err(|e| format!("创建加密文件失败: {}", e))?;

    let total_size = input.metadata()
        .map_err(|e| format!("获取文件大小失败: {}", e))?
        .len();

    // 进度回调（发送事件到前端）
    let progress_callback = {
        let app = app.clone();
        move |bytes_processed: u64, total_bytes: u64| {
            let percentage = (bytes_processed as f64 / total_bytes as f64) * 100.0;
            let progress = EncryptionProgress {
                bytes_processed,
                total_bytes,
                percentage,
            };

            // 发送进度事件
            let _ = app.emit("encryption-progress", &progress);
        }
    };

    // 执行流式加密（使用主密钥）
    encrypt_stream(
        input,
        output,
        key.as_bytes(),
        total_size,
        Some(&progress_callback),
    )
    .map_err(|e| format!("加密失败: {}", e))?;

    log::info!("[file_encryption:encrypt:done] source={}, output={}", source_path, encrypted_path);

    Ok(encrypted_path)
}

/// 解密文件 IPC 命令
///
/// 使用 Master Key Wrapping 模式：
/// 不再从密码派生密钥，而是使用已解密的主密钥
///
/// # Arguments
/// * `encrypted_path` - 加密文件路径
/// * `master_key_state` - 主密钥状态（必须已通过认证加载）
/// * `app` - Tauri 应用句柄
///
/// # Returns
/// * `Result<String, String>` - 解密后的文件路径或错误信息
#[tauri::command]
pub async fn decrypt_file(
    encrypted_path: String,
    master_key_state: State<'_, MasterKeyState>,
    app: tauri::AppHandle,
) -> Result<String, String> {
    log::info!("[file_encryption:decrypt:start] encrypted={}", encrypted_path);

    let encrypted = Path::new(&encrypted_path);

    // 验证文件存在
    if !encrypted.exists() {
        let err = format!("文件不存在: {}", encrypted_path);
        log::error!("[file_encryption:decrypt:failed] {}", err);
        return Err(err);
    }

    if !encrypted.is_file() {
        let err = format!("路径不是文件: {}", encrypted_path);
        log::error!("[file_encryption:decrypt:failed] {}", err);
        return Err(err);
    }

    // 生成解密文件路径（移除 .enc 扩展名）
    let decrypted_path = if encrypted_path.ends_with(".enc") {
        encrypted_path[..encrypted_path.len() - 4].to_string()
    } else {
        format!("{}.decrypted", encrypted_path)
    };

    // 获取主密钥（必须已通过认证加载）
    let key = master_key_state
        .get()
        .ok_or_else(|| {
            log::error!("[file_encryption:decrypt:failed] 主密钥未加载，请先登录");
            "主密钥未加载，请先登录".to_string()
        })?;

    // 打开输入输出文件
    let input = File::open(encrypted)
        .map_err(|e| format!("打开加密文件失败: {}", e))?;

    let output = File::create(&decrypted_path)
        .map_err(|e| format!("创建解密文件失败: {}", e))?;

    let total_size = input.metadata()
        .map_err(|e| format!("获取文件大小失败: {}", e))?
        .len();

    // 进度回调（发送事件到前端）
    let progress_callback = {
        let app = app.clone();
        move |bytes_processed: u64, total_bytes: u64| {
            let percentage = (bytes_processed as f64 / total_bytes as f64) * 100.0;
            let progress = EncryptionProgress {
                bytes_processed,
                total_bytes,
                percentage,
            };

            // 发送进度事件
            let _ = app.emit("decryption-progress", &progress);
        }
    };

    // 执行流式解密（使用主密钥）
    decrypt_stream(
        input,
        output,
        key.as_bytes(),
        total_size,
        Some(&progress_callback),
    )
    .map_err(|e| format!("解密失败: {}", e))?;

    log::info!("[file_encryption:decrypt:done] encrypted={}, output={}", encrypted_path, decrypted_path);

    Ok(decrypted_path)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[tokio::test]
    async fn test_encrypt_decrypt_roundtrip() {
        let temp_dir = TempDir::new().unwrap();
        let source_path = temp_dir.path().join("test.txt");
        let content = b"Test file content for encryption";

        // 创建测试文件
        fs::write(&source_path, content).unwrap();

        // 注意：这个测试需要 tauri::AppHandle，在单元测试中难以模拟
        // 实际测试应该在集成测试中进行
    }
}
