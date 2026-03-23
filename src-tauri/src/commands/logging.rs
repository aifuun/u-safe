use serde::{Deserialize, Serialize};

// Re-export export_diagnostic_logs from the main logging module
pub use crate::logging::export_diagnostic_logs;

/// 前端日志级别
#[derive(Debug, Deserialize, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum FrontendLogLevel {
    Info,
    Warn,
    Error,
    Debug,
}

/// 前端日志 IPC 命令
///
/// 功能：接收前端发送的日志，写入后端日志系统
/// 参数：
///   - level: 日志级别（info/warn/error/debug）
///   - event: 事件标识（例如："file:encrypt:start"）
///   - context: 可选的上下文数据（JSON 字符串）
///
/// 日志格式：[frontend:{event}] {context}
#[tauri::command]
pub fn write_frontend_log(
    level: FrontendLogLevel,
    event: String,
    context: Option<String>,
) -> Result<(), String> {
    let ctx = context.unwrap_or_default();

    match level {
        FrontendLogLevel::Info => {
            log::info!("[frontend:{}] {}", event, ctx);
        }
        FrontendLogLevel::Warn => {
            log::warn!("[frontend:{}] {}", event, ctx);
        }
        FrontendLogLevel::Error => {
            log::error!("[frontend:{}] {}", event, ctx);
        }
        FrontendLogLevel::Debug => {
            log::debug!("[frontend:{}] {}", event, ctx);
        }
    }

    Ok(())
}
