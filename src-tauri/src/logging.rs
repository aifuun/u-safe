// 日志系统模块
// 功能：日志文件持久化、日志轮转、日志级别控制

use std::path::PathBuf;
use tracing_appender::rolling::{RollingFileAppender, Rotation};
use tracing_subscriber::{fmt, layer::SubscriberExt, registry::Registry, EnvFilter, Layer};
use tracing::level_filters::LevelFilter;

/// 初始化日志系统
///
/// 配置：
/// - 主日志文件：.u-safe/logs/app-{date}.log（所有级别）
/// - 错误日志文件：.u-safe/logs/error-{date}.log（仅 ERROR）
/// - 日志轮转：每天轮转
/// - 日志级别：默认 INFO，可通过 RUST_LOG 环境变量控制
/// - 日志格式：[时间戳] [级别] 消息
pub fn init_logging() -> Result<(), Box<dyn std::error::Error>> {
    let log_dir = get_log_dir()?;

    // 主日志 appender（所有级别：INFO/WARN/ERROR）
    let main_appender = RollingFileAppender::new(
        Rotation::DAILY,
        log_dir.clone(),
        "app.log"
    );

    // 错误日志 appender（仅 ERROR 级别）
    let error_appender = RollingFileAppender::new(
        Rotation::DAILY,
        log_dir,
        "error.log"
    );

    // 配置日志级别过滤
    // 默认级别 INFO，可通过 RUST_LOG 环境变量覆盖
    let env_filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("u_safe_lib=info"));

    // 主日志层（所有级别）
    let main_layer = fmt::layer()
        .with_writer(main_appender)
        .with_ansi(false)
        .with_target(false)
        .with_filter(env_filter);

    // 错误日志层（仅 ERROR 级别）
    let error_layer = fmt::layer()
        .with_writer(error_appender)
        .with_ansi(false)
        .with_target(false)
        .with_filter(LevelFilter::ERROR);

    // 组合多个日志层
    let subscriber = Registry::default()
        .with(main_layer)
        .with(error_layer);

    tracing::subscriber::set_global_default(subscriber)?;

    Ok(())
}

/// 获取日志目录路径
///
/// 路径：.u-safe/logs/
/// 如果目录不存在，自动创建
fn get_log_dir() -> Result<PathBuf, Box<dyn std::error::Error>> {
    let data_dir = crate::usb_detection::get_data_dir();
    let log_dir = data_dir.join("logs");
    std::fs::create_dir_all(&log_dir)?;
    Ok(log_dir)
}

/// 写入系统信息文件
///
/// 生成文件：.u-safe/logs/system-info.txt
/// 内容：应用版本、操作系统、架构、生成时间
pub fn write_system_info() -> Result<(), Box<dyn std::error::Error>> {
    use chrono::Local;

    let log_dir = get_log_dir()?;
    let system_info_path = log_dir.join("system-info.txt");

    let info = format!(
        "U-Safe System Information\n\
         ========================\n\
         App Version: {}\n\
         OS: {}\n\
         Arch: {}\n\
         Generated: {}\n",
        env!("CARGO_PKG_VERSION"),
        std::env::consts::OS,
        std::env::consts::ARCH,
        Local::now().to_rfc3339()
    );

    std::fs::write(system_info_path, info)?;
    Ok(())
}

/// 清理旧日志文件
///
/// 扫描 logs 目录，删除 7 天前的日志文件
/// 保留 system-info.txt（不参与清理）
pub fn cleanup_old_logs() -> Result<(), Box<dyn std::error::Error>> {
    use chrono::{Duration, Local};

    let log_dir = get_log_dir()?;
    let cutoff_date = Local::now() - Duration::days(7);

    // 扫描日志目录
    for entry in std::fs::read_dir(&log_dir)? {
        let entry = entry?;
        let path = entry.path();

        // 只处理文件（跳过目录）
        if !path.is_file() {
            continue;
        }

        // 跳过 system-info.txt（不参与清理）
        if let Some(filename) = path.file_name() {
            if filename == "system-info.txt" {
                continue;
            }
        }

        // 检查文件修改时间
        if let Ok(metadata) = path.metadata() {
            if let Ok(modified) = metadata.modified() {
                let modified_time = chrono::DateTime::<chrono::Local>::from(modified);

                // 如果文件超过 7 天，删除
                if modified_time < cutoff_date {
                    match std::fs::remove_file(&path) {
                        Ok(_) => {
                            log::info!("[cleanup] 删除旧日志: {:?}", path.file_name());
                        }
                        Err(e) => {
                            log::warn!("[cleanup] 删除日志失败: {:?}, 原因: {}", path.file_name(), e);
                        }
                    }
                }
            }
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use std::path::PathBuf;
    use chrono::Local;

    /// 测试辅助函数：创建测试用的临时日志目录
    fn setup_test_log_dir() -> PathBuf {
        let temp_dir = std::env::temp_dir().join(format!("u-safe-test-{}", Local::now().timestamp_millis()));
        fs::create_dir_all(&temp_dir).unwrap();
        temp_dir
    }

    /// 测试辅助函数：清理测试目录
    fn cleanup_test_dir(dir: &PathBuf) {
        let _ = fs::remove_dir_all(dir);
    }

    #[test]
    fn test_get_log_dir_creates_directory() {
        // 测试 get_log_dir 能够正确创建日志目录
        let result = get_log_dir();
        assert!(result.is_ok());

        let log_dir = result.unwrap();
        assert!(log_dir.exists());
        assert!(log_dir.is_dir());
        assert!(log_dir.ends_with("logs"));
    }

    #[test]
    fn test_write_system_info() {
        // 测试系统信息文件生成
        let result = write_system_info();
        assert!(result.is_ok());

        // 验证文件存在
        let log_dir = get_log_dir().unwrap();
        let system_info_path = log_dir.join("system-info.txt");
        assert!(system_info_path.exists());

        // 验证文件内容
        let content = fs::read_to_string(&system_info_path).unwrap();
        assert!(content.contains("U-Safe System Information"));
        assert!(content.contains("App Version:"));
        assert!(content.contains("OS:"));
        assert!(content.contains("Arch:"));
        assert!(content.contains("Generated:"));
    }

    #[test]
    fn test_cleanup_old_logs() {
        use std::fs::File;
        use std::time::SystemTime;

        // 使用实际的日志目录（因为 cleanup_old_logs 使用 get_log_dir）
        let log_dir = get_log_dir().unwrap();

        // 创建一个测试用的旧日志文件
        let old_log_name = format!("test-old-{}.log", Local::now().timestamp_millis());
        let old_log_path = log_dir.join(&old_log_name);
        File::create(&old_log_path).unwrap();

        // 修改文件时间为 8 天前
        let eight_days_ago = SystemTime::now()
            - std::time::Duration::from_secs(8 * 24 * 60 * 60);
        filetime::set_file_mtime(&old_log_path, filetime::FileTime::from_system_time(eight_days_ago)).unwrap();

        // 创建一个新日志文件（应该保留）
        let new_log_name = format!("test-new-{}.log", Local::now().timestamp_millis());
        let new_log_path = log_dir.join(&new_log_name);
        File::create(&new_log_path).unwrap();

        // 执行清理
        let result = cleanup_old_logs();
        assert!(result.is_ok());

        // 验证旧日志已删除
        assert!(!old_log_path.exists());

        // 验证新日志保留
        assert!(new_log_path.exists());

        // 清理测试文件
        let _ = fs::remove_file(&new_log_path);
    }

    #[test]
    fn test_cleanup_preserves_system_info() {
        // 测试清理不会删除 system-info.txt

        // 确保 system-info.txt 存在
        write_system_info().unwrap();

        let log_dir = get_log_dir().unwrap();
        let system_info_path = log_dir.join("system-info.txt");
        assert!(system_info_path.exists());

        // 执行清理
        cleanup_old_logs().unwrap();

        // 验证 system-info.txt 仍然存在
        assert!(system_info_path.exists());
    }
}
