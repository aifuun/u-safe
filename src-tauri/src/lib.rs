// Database module
pub mod db;
mod usb_detection;
mod system_info;
mod theme;

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
    // Initialize logging
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info"))
        .init();

    log::info!("[app:start] U-Safe application starting");

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
