// Database module
pub mod db;
mod usb_detection;
mod system_info;

use db::{Database, get_default_db_path};

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

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            hello_world,
            test_db_connection,
            check_system
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");

    log::info!("[app:stop] U-Safe application stopped");
}
