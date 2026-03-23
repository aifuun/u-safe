mod file_scanner;
mod file_encryption;
mod file_operations;
mod tag_management;
mod auth;
mod password_reset;
mod logging;

pub use file_scanner::scan_file_tree;
pub use file_encryption::{encrypt_file, decrypt_file};
pub use file_operations::{delete_file, rename_file};
pub use tag_management::create_tag;
pub use auth::{is_master_key_set, derive_master_key, verify_password, MasterKeyState};
pub use password_reset::{get_reset_stats, reset_app};
pub use logging::{write_frontend_log, export_diagnostic_logs};

/// 移动文件
///
/// 使用复制+删除策略以支持跨文件系统移动
///
/// @param from - 源文件路径
/// @param to - 目标文件路径
#[tauri::command]
pub fn move_file(from: String, to: String) -> Result<(), String> {
    std::fs::copy(&from, &to)
        .map_err(|e| format!("复制文件失败: {}", e))?;

    std::fs::remove_file(&from)
        .map_err(|e| format!("删除源文件失败: {}", e))?;

    Ok(())
}
