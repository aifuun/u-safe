// Database module
pub mod db;
mod usb_detection;
mod system_info;
mod theme;
mod logging;

// Crypto module (加密模块)
pub mod crypto;

// File I/O module (文件 I/O 模块)
pub mod file;

// Models module (数据模型)
pub mod models;

// Commands module (IPC 命令)
mod commands;
use commands::{
    scan_file_tree, encrypt_file, decrypt_file, delete_file, rename_file, create_tag,
    is_master_key_set, derive_master_key, verify_password,
    get_reset_stats, reset_app
};
use theme::get_theme;

use db::{Database, get_default_db_path};
use crypto::password::PasswordManager;

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/

/// 迁移旧数据到新的统一数据目录
///
/// 检查系统目录下是否存在旧数据（密码哈希和主密钥），
/// 如果存在则迁移到新的 .u-safe/ 目录
fn migrate_old_data() -> Result<(), String> {
    // 获取旧的系统数据目录路径
    let old_data_dir = dirs::data_dir()
        .ok_or_else(|| "无法获取系统数据目录".to_string())?
        .join(".u-safe");

    // 获取新的统一数据目录路径
    let new_data_dir = usb_detection::get_data_dir();

    // 如果旧目录不存在，无需迁移
    if !old_data_dir.exists() {
        log::info!("[migrate] 未检测到旧数据，无需迁移");
        return Ok(());
    }

    // 如果新旧路径相同，无需迁移
    if old_data_dir == new_data_dir {
        log::info!("[migrate] 数据目录已是最新，无需迁移");
        return Ok(());
    }

    log::info!("[migrate:start] 开始迁移数据: {:?} -> {:?}", old_data_dir, new_data_dir);

    // 确保新目录的 keys 子目录存在
    let new_keys_dir = new_data_dir.join("keys");
    std::fs::create_dir_all(&new_keys_dir)
        .map_err(|e| format!("创建新 keys 目录失败: {}", e))?;

    let old_keys_dir = old_data_dir.join("keys");

    // 迁移密码哈希文件
    let old_password_hash = old_keys_dir.join("password.hash");
    let new_password_hash = new_keys_dir.join("password.hash");

    if old_password_hash.exists() && !new_password_hash.exists() {
        std::fs::copy(&old_password_hash, &new_password_hash)
            .map_err(|e| format!("迁移密码哈希文件失败: {}", e))?;
        log::info!("[migrate] 密码哈希文件已迁移: {:?}", new_password_hash);
    }

    // 迁移主密钥文件
    let old_master_key = old_keys_dir.join("master.key");
    let new_master_key = new_keys_dir.join("master.key");

    if old_master_key.exists() && !new_master_key.exists() {
        std::fs::copy(&old_master_key, &new_master_key)
            .map_err(|e| format!("迁移主密钥文件失败: {}", e))?;
        log::info!("[migrate] 主密钥文件已迁移: {:?}", new_master_key);
    }

    log::info!("[migrate:complete] 数据迁移完成");
    log::info!("[migrate:note] 旧数据已保留在: {:?}", old_data_dir);
    log::info!("[migrate:note] 建议手动验证后删除旧数据");

    Ok(())
}

#[tauri::command]
fn hello_world() -> String {
    "Hello World from Rust!".to_string()
}

#[tauri::command]
fn test_db_connection() -> Result<String, String> {
    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| e.to_string())?;

    // Test query
    let version: String = db.connection()
        .query_row("SELECT sqlite_version()", [], |row| row.get(0))
        .map_err(|e| e.to_string())?;

    Ok(format!("SQLite version: {}", version))
}

#[tauri::command]
fn check_system() -> Result<String, String> {
    system_info::check_system_requirements()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // 初始化日志系统（文件持久化 + 日志轮转）
    if let Err(e) = logging::init_logging() {
        eprintln!("日志系统初始化失败: {}", e);
    }

    // 写入系统信息文件
    if let Err(e) = logging::write_system_info() {
        log::error!("[app:init] 系统信息写入失败: {}", e);
    }

    // 清理旧日志（7 天前）
    if let Err(e) = logging::cleanup_old_logs() {
        log::warn!("[app:init] 日志清理失败: {}", e);
    }

    log::info!("[app:start] U-Safe v{} 启动", env!("CARGO_PKG_VERSION"));

    // 迁移旧数据（如果存在）
    if let Err(e) = migrate_old_data() {
        log::error!("[migrate:failed] {}", e);
        // 迁移失败不应阻止应用启动
    }

    // 初始化密码管理器 (从文件加载密码哈希)
    let password_manager = PasswordManager::load()
        .expect("[app:start] 无法加载密码管理器");

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(password_manager)
        .invoke_handler(tauri::generate_handler![
            hello_world,
            test_db_connection,
            check_system,
            scan_file_tree,
            encrypt_file,
            decrypt_file,
            delete_file,
            rename_file,
            create_tag,
            get_theme,
            is_master_key_set,
            derive_master_key,
            verify_password,
            get_reset_stats,
            reset_app
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");

    log::info!("[app:stop] U-Safe application stopped");
}
