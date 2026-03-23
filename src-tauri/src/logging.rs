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

/// 收集系统信息（字符串格式）
///
/// 返回格式化的系统信息字符串，包含：
/// - 应用版本
/// - 操作系统信息
/// - 硬件信息
/// - 日志文件统计
pub fn collect_system_info() -> Result<String, String> {
    use chrono::Local;
    use sysinfo::System;

    let mut sys = System::new_all();
    sys.refresh_all();

    let log_dir = get_log_dir().map_err(|e| e.to_string())?;

    let info = format!(
        r#"# U-Safe 系统信息
生成时间: {}

## 应用信息
版本: {}
平台: Tauri 2.0
架构: {}

## 系统信息
操作系统: {} {}
内核版本: {}
主机名: {}

## 硬件信息
CPU: {} 核心
总内存: {} GB
可用内存: {} GB

## 日志文件统计
日志目录: {}
文件数量: {}
总大小: {} MB
"#,
        Local::now().format("%Y-%m-%d %H:%M:%S"),
        env!("CARGO_PKG_VERSION"),
        std::env::consts::ARCH,
        System::name().unwrap_or_else(|| "未知".to_string()),
        System::os_version().unwrap_or_else(|| "未知".to_string()),
        System::kernel_version().unwrap_or_else(|| "未知".to_string()),
        System::host_name().unwrap_or_else(|| "未知".to_string()),
        sys.cpus().len(),
        sys.total_memory() / 1024 / 1024 / 1024,
        sys.available_memory() / 1024 / 1024 / 1024,
        log_dir.display(),
        count_log_files().unwrap_or(0),
        calculate_log_size_mb().unwrap_or(0),
    );

    Ok(info)
}

/// 统计日志文件数量
fn count_log_files() -> Result<usize, String> {
    let log_dir = get_log_dir().map_err(|e| e.to_string())?;
    let count = std::fs::read_dir(log_dir)
        .map_err(|e| e.to_string())?
        .filter_map(|entry| entry.ok())
        .filter(|entry| {
            entry.path()
                .extension()
                .and_then(|ext| ext.to_str())
                == Some("log")
        })
        .count();
    Ok(count)
}

/// 计算日志文件总大小（MB）
fn calculate_log_size_mb() -> Result<u64, String> {
    let log_dir = get_log_dir().map_err(|e| e.to_string())?;
    let total_size: u64 = std::fs::read_dir(log_dir)
        .map_err(|e| e.to_string())?
        .filter_map(|entry| entry.ok())
        .filter_map(|entry| entry.metadata().ok())
        .map(|metadata| metadata.len())
        .sum();
    Ok(total_size / 1024 / 1024)
}

/// 写入系统信息文件
///
/// 生成文件：.u-safe/logs/system-info.txt
/// 内容：应用版本、操作系统、架构、生成时间
pub fn write_system_info() -> Result<(), Box<dyn std::error::Error>> {
    let log_dir = get_log_dir()?;
    let system_info_path = log_dir.join("system-info.txt");

    let info = collect_system_info().map_err(|e| e.to_string())?;

    std::fs::write(system_info_path, info)?;
    Ok(())
}

/// 导出诊断日志
///
/// 功能：
/// 1. 收集最近 7 天的日志文件
/// 2. 生成系统信息文件
/// 3. 创建 ZIP 压缩包
/// 4. 返回 ZIP 文件路径
///
/// 返回值：ZIP 文件的绝对路径
#[tauri::command]
pub async fn export_diagnostic_logs() -> Result<String, String> {
    use chrono::Local;
    use std::fs;

    log::info!("[logging:export:start] 开始导出诊断日志");

    // 1. 创建临时目录
    let temp_dir = std::env::temp_dir().join(format!("u-safe-logs-export-{}", Local::now().timestamp()));
    fs::create_dir_all(&temp_dir).map_err(|e| format!("创建临时目录失败: {}", e))?;

    // 2. 收集日志文件（最近 7 天）
    let log_files = collect_recent_logs(7)?;
    log::info!("[logging:export:collect] 收集到 {} 个日志文件", log_files.len());

    // 3. 生成系统信息文件
    let system_info = collect_system_info()?;
    let system_info_path = temp_dir.join("system-info.txt");
    fs::write(&system_info_path, system_info).map_err(|e| format!("写入系统信息失败: {}", e))?;

    // 4. 创建 ZIP 文件
    let zip_filename = format!("u-safe-logs-{}.zip", Local::now().format("%Y-%m-%d"));
    let zip_path = temp_dir.join(&zip_filename);
    create_log_zip(&zip_path, &log_files, &system_info_path)?;

    log::info!("[logging:export:done] ZIP 文件已创建: {}", zip_path.display());

    Ok(zip_path.to_string_lossy().to_string())
}

/// 收集最近 N 天的日志文件
///
/// @param days - 收集的天数
/// @return 日志文件路径列表
fn collect_recent_logs(days: i64) -> Result<Vec<PathBuf>, String> {
    use chrono::{Duration, Local};
    use std::fs;

    let log_dir = get_log_dir().map_err(|e| e.to_string())?;
    let cutoff_date = Local::now() - Duration::days(days);

    let mut log_files = Vec::new();

    for entry in fs::read_dir(log_dir).map_err(|e| e.to_string())? {
        let entry = entry.map_err(|e| e.to_string())?;
        let path = entry.path();

        // 只收集 .log 文件
        if path.extension().and_then(|s| s.to_str()) != Some("log") {
            continue;
        }

        // 检查文件修改时间
        if let Ok(metadata) = path.metadata() {
            if let Ok(modified) = metadata.modified() {
                let modified_chrono: chrono::DateTime<Local> = modified.into();
                if modified_chrono > cutoff_date {
                    log_files.push(path);
                }
            }
        }
    }

    // 按文件名排序（确保时间顺序）
    log_files.sort();

    Ok(log_files)
}

/// 创建日志 ZIP 压缩包
///
/// @param zip_path - ZIP 文件输出路径
/// @param log_files - 要打包的日志文件列表
/// @param system_info_path - 系统信息文件路径
fn create_log_zip(
    zip_path: &std::path::Path,
    log_files: &[PathBuf],
    system_info_path: &std::path::Path,
) -> Result<(), String> {
    use std::fs::File;
    use std::io::{Read, Write};
    use zip::write::FileOptions;
    use zip::ZipWriter;

    let file = File::create(zip_path).map_err(|e| format!("创建 ZIP 文件失败: {}", e))?;
    let mut zip = ZipWriter::new(file);

    let options = FileOptions::default()
        .compression_method(zip::CompressionMethod::Deflated)
        .unix_permissions(0o755);

    // 添加系统信息文件
    add_file_to_zip(&mut zip, system_info_path, "system-info.txt", options)?;

    // 添加所有日志文件
    for log_file in log_files {
        if let Some(filename) = log_file.file_name() {
            add_file_to_zip(&mut zip, log_file, filename.to_str().unwrap(), options)?;
        }
    }

    zip.finish().map_err(|e| format!("完成 ZIP 文件失败: {}", e))?;

    Ok(())
}

/// 添加单个文件到 ZIP
fn add_file_to_zip<W: std::io::Write + std::io::Seek>(
    zip: &mut zip::ZipWriter<W>,
    file_path: &std::path::Path,
    zip_filename: &str,
    options: zip::write::FileOptions,
) -> Result<(), String> {
    use std::fs::File;
    use std::io::{Read, Write};

    zip.start_file(zip_filename, options)
        .map_err(|e| format!("添加文件到 ZIP 失败: {}", e))?;

    let mut file = File::open(file_path)
        .map_err(|e| format!("打开文件失败: {}", e))?;
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)
        .map_err(|e| format!("读取文件失败: {}", e))?;

    zip.write_all(&buffer)
        .map_err(|e| format!("写入 ZIP 失败: {}", e))?;

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
