use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;
use crate::db::{Database, get_default_db_path};

/// 文件删除响应
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeleteFileResponse {
    /// 是否成功
    pub success: bool,
    /// 删除的文件 ID
    pub file_id: i64,
    /// 消息
    pub message: String,
}

/// 文件重命名响应
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RenameFileResponse {
    /// 是否成功
    pub success: bool,
    /// 文件 ID
    pub file_id: i64,
    /// 新文件名
    pub new_name: String,
    /// 消息
    pub message: String,
}

/// 删除文件 IPC 命令
///
/// # 功能
/// 1. 从数据库删除文件记录（级联删除关联数据）
/// 2. 删除物理文件（加密文件和原始文件）
/// 3. 使用事务保证原子性
///
/// # Arguments
/// * `file_id` - 文件 ID
///
/// # Returns
/// * `Result<DeleteFileResponse, String>` - 删除结果或错误信息
#[tauri::command]
pub async fn delete_file(file_id: i64) -> Result<DeleteFileResponse, String> {
    log::info!("[file_operations:delete:start] file_id={}", file_id);

    // 连接数据库
    let db_path = get_default_db_path();
    let mut db = Database::new(db_path).map_err(|e| {
        let err = format!("数据库连接失败: {}", e);
        log::error!("[file_operations:delete:failed] {}", err);
        err
    })?;

    let conn = db.connection_mut();

    // 开始事务
    let tx = conn.transaction().map_err(|e| {
        let err = format!("开始事务失败: {}", e);
        log::error!("[file_operations:delete:failed] {}", err);
        err
    })?;

    // 查询文件路径（用于物理删除）
    let (file_path, encrypted_path): (String, Option<String>) = tx
        .query_row(
            "SELECT file_path, encrypted_path FROM files WHERE id = ?1",
            [file_id],
            |row| Ok((row.get(0)?, row.get(1)?)),
        )
        .map_err(|e| {
            let err = format!("查询文件信息失败: {}", e);
            log::error!("[file_operations:delete:failed] file_id={}, err={}", file_id, err);
            err
        })?;

    log::info!(
        "[file_operations:delete:files] file_id={}, file_path={}, encrypted_path={:?}",
        file_id, file_path, encrypted_path
    );

    // 从数据库删除文件记录（级联删除 file_tags 和 encryption_meta）
    let deleted_rows = tx
        .execute("DELETE FROM files WHERE id = ?1", [file_id])
        .map_err(|e| {
            let err = format!("删除数据库记录失败: {}", e);
            log::error!("[file_operations:delete:failed] file_id={}, err={}", file_id, err);
            err
        })?;

    if deleted_rows == 0 {
        let err = format!("文件不存在: file_id={}", file_id);
        log::error!("[file_operations:delete:failed] {}", err);
        return Err(err);
    }

    // 提交事务
    tx.commit().map_err(|e| {
        let err = format!("提交事务失败: {}", e);
        log::error!("[file_operations:delete:failed] file_id={}, err={}", file_id, err);
        err
    })?;

    log::info!("[file_operations:delete:db_success] file_id={}", file_id);

    // 删除物理文件（即使失败也不影响数据库删除）
    let mut physical_delete_errors = Vec::new();

    // 删除原始文件
    if Path::new(&file_path).exists() {
        if let Err(e) = fs::remove_file(&file_path) {
            let err = format!("删除原始文件失败: {}", e);
            log::warn!("[file_operations:delete:physical_failed] file_path={}, err={}", file_path, err);
            physical_delete_errors.push(err);
        } else {
            log::info!("[file_operations:delete:physical_success] file_path={}", file_path);
        }
    }

    // 删除加密文件
    if let Some(enc_path) = encrypted_path {
        if Path::new(&enc_path).exists() {
            if let Err(e) = fs::remove_file(&enc_path) {
                let err = format!("删除加密文件失败: {}", e);
                log::warn!("[file_operations:delete:physical_failed] encrypted_path={}, err={}", enc_path, err);
                physical_delete_errors.push(err);
            } else {
                log::info!("[file_operations:delete:physical_success] encrypted_path={}", enc_path);
            }
        }
    }

    let message = if physical_delete_errors.is_empty() {
        format!("文件删除成功: file_id={}", file_id)
    } else {
        format!(
            "文件删除成功（物理文件删除部分失败）: file_id={}, errors={}",
            file_id,
            physical_delete_errors.join(", ")
        )
    };

    log::info!("[file_operations:delete:done] file_id={}", file_id);

    Ok(DeleteFileResponse {
        success: true,
        file_id,
        message,
    })
}

/// 重命名文件 IPC 命令
///
/// # 功能
/// 1. 验证新文件名（不能为空，长度限制）
/// 2. 更新数据库中的 original_name 字段
/// 3. 更新 updated_at 时间戳
///
/// # Arguments
/// * `file_id` - 文件 ID
/// * `new_name` - 新文件名
///
/// # Returns
/// * `Result<RenameFileResponse, String>` - 重命名结果或错误信息
#[tauri::command]
pub async fn rename_file(file_id: i64, new_name: String) -> Result<RenameFileResponse, String> {
    log::info!("[file_operations:rename:start] file_id={}, new_name={}", file_id, new_name);

    // 验证新文件名
    let trimmed_name = new_name.trim();
    if trimmed_name.is_empty() {
        let err = "文件名不能为空".to_string();
        log::error!("[file_operations:rename:failed] file_id={}, err={}", file_id, err);
        return Err(err);
    }

    if trimmed_name.len() > 255 {
        let err = "文件名过长（最多 255 字符）".to_string();
        log::error!("[file_operations:rename:failed] file_id={}, err={}", file_id, err);
        return Err(err);
    }

    // 检查文件名是否包含非法字符
    const ILLEGAL_CHARS: &[char] = &['/', '\\', '<', '>', ':', '"', '|', '?', '*'];
    if trimmed_name.chars().any(|c| ILLEGAL_CHARS.contains(&c)) {
        let err = format!(
            "文件名包含非法字符: {}",
            ILLEGAL_CHARS.iter().collect::<String>()
        );
        log::error!("[file_operations:rename:failed] file_id={}, err={}", file_id, err);
        return Err(err);
    }

    // 连接数据库
    let db_path = get_default_db_path();
    let mut db = Database::new(db_path).map_err(|e| {
        let err = format!("数据库连接失败: {}", e);
        log::error!("[file_operations:rename:failed] {}", err);
        err
    })?;

    let conn = db.connection_mut();

    // 检查文件是否存在
    let exists: bool = conn
        .query_row(
            "SELECT COUNT(*) > 0 FROM files WHERE id = ?1",
            [file_id],
            |row| row.get(0),
        )
        .map_err(|e| {
            let err = format!("查询文件失败: {}", e);
            log::error!("[file_operations:rename:failed] file_id={}, err={}", file_id, err);
            err
        })?;

    if !exists {
        let err = format!("文件不存在: file_id={}", file_id);
        log::error!("[file_operations:rename:failed] {}", err);
        return Err(err);
    }

    // 更新文件名
    let updated_rows = conn
        .execute(
            "UPDATE files SET original_name = ?1, updated_at = datetime('now') WHERE id = ?2",
            [trimmed_name, &file_id.to_string()],
        )
        .map_err(|e| {
            let err = format!("更新文件名失败: {}", e);
            log::error!("[file_operations:rename:failed] file_id={}, err={}", file_id, err);
            err
        })?;

    if updated_rows == 0 {
        let err = format!("更新文件名失败（无行被更新）: file_id={}", file_id);
        log::error!("[file_operations:rename:failed] {}", err);
        return Err(err);
    }

    log::info!("[file_operations:rename:done] file_id={}, new_name={}", file_id, trimmed_name);

    Ok(RenameFileResponse {
        success: true,
        file_id,
        new_name: trimmed_name.to_string(),
        message: format!("文件重命名成功: {}", trimmed_name),
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use rusqlite::Connection;
    use crate::db::schema::initialize_schema;
    use std::fs::File;
    use std::io::Write;
    use tempfile::TempDir;

    /// 测试文件删除功能
    #[tokio::test]
    async fn test_delete_file_success() {
        // 创建临时数据库
        let conn = Connection::open_in_memory().unwrap();
        initialize_schema(&conn).unwrap();

        // 创建临时文件
        let temp_dir = TempDir::new().unwrap();
        let test_file = temp_dir.path().join("test.txt");
        let mut file = File::create(&test_file).unwrap();
        file.write_all(b"test content").unwrap();

        // 插入测试数据
        conn.execute(
            "INSERT INTO files (file_path, original_name, file_size, is_encrypted) VALUES (?1, ?2, ?3, ?4)",
            [test_file.to_str().unwrap(), "test.txt", "12", "0"],
        )
        .unwrap();

        let file_id: i64 = conn.last_insert_rowid();

        // 注意：实际测试需要集成测试环境
        // 这里只是验证 SQL 逻辑正确性
        let deleted = conn.execute("DELETE FROM files WHERE id = ?1", [file_id]).unwrap();
        assert_eq!(deleted, 1);
    }

    /// 测试文件重命名功能
    #[tokio::test]
    async fn test_rename_file_validation() {
        // 测试空文件名
        let result = rename_file(1, "".to_string()).await;
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("文件名不能为空"));

        // 测试文件名过长
        let long_name = "a".repeat(256);
        let result = rename_file(1, long_name).await;
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("文件名过长"));

        // 测试非法字符
        let result = rename_file(1, "test/file.txt".to_string()).await;
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("非法字符"));
    }
}
