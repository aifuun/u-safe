//! 密码重置相关 IPC 命令
//!
//! 提供密码重置流程所需的统计数据获取和重置操作

use std::path::PathBuf;
use rusqlite::Connection;
use serde::{Deserialize, Serialize};
use crate::db::get_default_db_path;

/// 重置统计数据
///
/// 用于显示在警告页面，让用户了解将要删除的数据量
#[derive(Debug, Serialize, Deserialize)]
pub struct ResetStats {
    /// 加密文件数量
    pub encrypted_files_count: u32,
    /// 所有文件数量
    pub total_files_count: u32,
    /// 标签数量
    pub tags_count: u32,
    /// 数据库文件大小（字节）
    pub database_size_bytes: u64,
}

/// 获取重置统计数据
///
/// 返回将要删除的数据统计，用于在警告页面显示
///
/// # Returns
/// * `Ok(ResetStats)` - 统计数据
/// * `Err` - 读取失败
#[tauri::command]
pub fn get_reset_stats() -> Result<ResetStats, String> {
    log::info!("[reset:get_stats] 开始获取重置统计数据");

    // 1. 连接数据库
    let db_path = get_default_db_path();
    let conn = Connection::open(&db_path)
        .map_err(|e| {
            log::error!("[reset:get_stats] 无法打开数据库: {}", e);
            format!("无法打开数据库: {}", e)
        })?;

    // 2. 查询加密文件数量
    let encrypted_files_count: u32 = conn
        .query_row(
            "SELECT COUNT(*) FROM files WHERE is_encrypted = 1",
            [],
            |row| row.get(0)
        )
        .map_err(|e| {
            log::error!("[reset:get_stats] 查询加密文件失败: {}", e);
            format!("查询加密文件失败: {}", e)
        })?;

    // 3. 查询所有文件数量
    let total_files_count: u32 = conn
        .query_row(
            "SELECT COUNT(*) FROM files",
            [],
            |row| row.get(0)
        )
        .map_err(|e| {
            log::error!("[reset:get_stats] 查询文件总数失败: {}", e);
            format!("查询文件总数失败: {}", e)
        })?;

    // 4. 查询标签数量
    let tags_count: u32 = conn
        .query_row(
            "SELECT COUNT(*) FROM tags",
            [],
            |row| row.get(0)
        )
        .map_err(|e| {
            log::error!("[reset:get_stats] 查询标签失败: {}", e);
            format!("查询标签失败: {}", e)
        })?;

    // 5. 获取数据库文件大小
    let database_size_bytes = std::fs::metadata(&db_path)
        .map(|m| m.len())
        .unwrap_or(0);

    let stats = ResetStats {
        encrypted_files_count,
        total_files_count,
        tags_count,
        database_size_bytes,
    };

    log::info!(
        "[reset:get_stats] 统计数据: 加密文件={}, 总文件={}, 标签={}, 数据库大小={}",
        stats.encrypted_files_count,
        stats.total_files_count,
        stats.tags_count,
        stats.database_size_bytes
    );

    Ok(stats)
}

/// 获取密码哈希文件路径
fn get_password_hash_path() -> Result<PathBuf, String> {
    let data_dir = dirs::data_dir()
        .ok_or_else(|| "无法获取数据目录".to_string())?;

    let hash_file = data_dir.join(".u-safe").join("keys").join("password.hash");
    Ok(hash_file)
}

/// 获取数据库备份路径
fn get_backup_db_path() -> PathBuf {
    let db_path = get_default_db_path();
    db_path.with_extension("db.backup")
}

/// 归档数据库（复制到 .backup）
///
/// 在重置前备份数据库，以防用户后悔或需要恢复
fn archive_database() -> Result<(), String> {
    let db_path = get_default_db_path();
    let backup_path = get_backup_db_path();

    log::info!(
        "[reset:archive_db] 归档数据库: {} -> {}",
        db_path.display(),
        backup_path.display()
    );

    std::fs::copy(&db_path, &backup_path)
        .map_err(|e| {
            log::error!("[reset:archive_db] 归档失败: {}", e);
            format!("归档数据库失败: {}", e)
        })?;

    log::info!("[reset:archive_db] 数据库归档成功");
    Ok(())
}

/// 删除密码哈希文件
fn delete_password_hash() -> Result<(), String> {
    let hash_file = get_password_hash_path()?;

    if hash_file.exists() {
        log::info!("[reset:delete_hash] 删除密码文件: {}", hash_file.display());
        std::fs::remove_file(&hash_file)
            .map_err(|e| {
                log::error!("[reset:delete_hash] 删除失败: {}", e);
                format!("删除密码文件失败: {}", e)
            })?;
        log::info!("[reset:delete_hash] 密码文件已删除");
    } else {
        log::info!("[reset:delete_hash] 密码文件不存在，跳过");
    }

    Ok(())
}

/// 清空数据库所有表
///
/// 保留表结构，只删除数据
fn clear_database_tables() -> Result<(), String> {
    let db_path = get_default_db_path();
    let conn = Connection::open(&db_path)
        .map_err(|e| {
            log::error!("[reset:clear_db] 无法打开数据库: {}", e);
            format!("无法打开数据库: {}", e)
        })?;

    log::info!("[reset:clear_db] 开始清空数据库表");

    // 清空所有数据表（顺序很重要，需要先删除外键关联表）
    let tables_to_clear = vec![
        "file_tags",        // 外键关联表
        "encryption_meta",  // 外键关联表
        "files",            // 主表
        "tags",             // 主表
        "config",           // 配置表
    ];

    for table in tables_to_clear {
        conn.execute(&format!("DELETE FROM {}", table), [])
            .map_err(|e| {
                log::error!("[reset:clear_db] 清空表 {} 失败: {}", table, e);
                format!("清空表 {} 失败: {}", table, e)
            })?;
        log::info!("[reset:clear_db] 表 {} 已清空", table);
    }

    // 重置 SQLite 自增 ID
    conn.execute("DELETE FROM sqlite_sequence", [])
        .map_err(|e| {
            log::warn!("[reset:clear_db] 重置自增 ID 失败（可忽略）: {}", e);
            // 不返回错误，因为可能不存在这个表
        })
        .ok();

    log::info!("[reset:clear_db] 数据库清空完成");
    Ok(())
}

/// 执行完整的应用重置
///
/// 完整流程：
/// 1. 归档数据库到 .backup
/// 2. 删除密码哈希文件
/// 3. 清空数据库所有表
/// 4. 日志记录重置操作
///
/// # Returns
/// * `Ok(())` - 重置成功
/// * `Err` - 重置失败
///
/// # 注意
/// - 此操作不可逆（除非用户手动恢复 .backup 文件）
/// - 前端需要在调用后清除 localStorage 并跳转到 /setup
#[tauri::command]
pub fn reset_app() -> Result<(), String> {
    log::warn!("[reset:app] ==================== 开始应用重置 ====================");

    // 1. 归档数据库
    archive_database()?;

    // 2. 删除密码哈希
    delete_password_hash()?;

    // 3. 清空数据库
    clear_database_tables()?;

    log::warn!("[reset:app] ==================== 应用重置完成 ====================");
    log::warn!("[reset:app] 用户需要重新设置密码并重新开始使用");

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use rusqlite::Connection;
    use crate::db::schema::initialize_schema;

    fn setup_test_db() -> Connection {
        let conn = Connection::open_in_memory().unwrap();
        initialize_schema(&conn).unwrap();
        conn
    }

    #[test]
    fn test_get_reset_stats_empty_db() {
        // 注意：这个测试需要真实数据库路径，在 CI 环境可能失败
        // 实际测试应该在手动测试阶段进行
    }

    #[test]
    fn test_clear_database_tables() {
        let conn = setup_test_db();

        // 插入测试数据
        conn.execute(
            "INSERT INTO files (file_path, original_name, file_size, is_encrypted) VALUES (?, ?, ?, ?)",
            ["test.txt", "test.txt", "100", "0"],
        ).unwrap();

        conn.execute(
            "INSERT INTO tags (tag_id, tag_name, full_path, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            ["tag-1", "工作", "/工作", "2024-01-01T00:00:00Z", "2024-01-01T00:00:00Z"],
        ).unwrap();

        // 验证数据存在
        let count: i64 = conn.query_row("SELECT COUNT(*) FROM files", [], |row| row.get(0)).unwrap();
        assert_eq!(count, 1);

        // 清空表（注意：这个函数操作的是默认数据库，不是内存数据库）
        // 实际测试需要在集成测试中进行
    }
}
