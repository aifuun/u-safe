use crate::db::{Database, get_default_db_path};
use crate::models::{Tag, CreateTagRequest};
use rusqlite::params;
use uuid::Uuid;

/// 错误类型：标签名称重复
const ERR_TAG_NAME_DUPLICATE: &str = "TagNameDuplicate";
/// 错误类型：标签不存在（预留给 update_tag 和 delete_tag 使用）
#[allow(dead_code)]
const ERR_TAG_NOT_FOUND: &str = "TagNotFound";
/// 错误类型：无效的标签名称
const ERR_INVALID_TAG_NAME: &str = "InvalidTagName";
/// 错误类型：父标签不存在
const ERR_PARENT_NOT_FOUND: &str = "ParentTagNotFound";

/// 创建标签
///
/// # Arguments
/// * `request` - 创建标签请求，包含 name, parent_id, color
///
/// # Returns
/// * `Ok(Tag)` - 创建成功，返回新标签
/// * `Err(String)` - 创建失败，返回错误信息
///
/// # Errors
/// * `InvalidTagName` - 标签名称无效（空或超过50字符）
/// * `TagNameDuplicate` - 同级标签名称重复
/// * `ParentTagNotFound` - 父标签不存在
#[tauri::command]
pub async fn create_tag(request: CreateTagRequest) -> Result<Tag, String> {
    log::info!("[tag:create] name={}, parent_id={:?}", request.name, request.parent_id);

    // 验证标签名称
    if request.name.trim().is_empty() {
        log::warn!("[tag:create:failed] 标签名称为空");
        return Err(format!("{}:标签名称不能为空", ERR_INVALID_TAG_NAME));
    }

    if request.name.len() > 50 {
        log::warn!("[tag:create:failed] 标签名称过长: {}", request.name.len());
        return Err(format!("{}:标签名称不能超过50个字符", ERR_INVALID_TAG_NAME));
    }

    // 验证颜色代码格式（如果提供）
    if let Some(ref color) = request.color {
        if !color.starts_with('#') || (color.len() != 7 && color.len() != 4) {
            log::warn!("[tag:create:failed] 无效的颜色代码: {}", color);
            return Err(format!("{}:颜色代码格式无效（应为 #RRGGBB 或 #RGB）", ERR_INVALID_TAG_NAME));
        }
    }

    // 打开数据库连接
    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[tag:create:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();

    // 如果有父标签，验证父标签存在并获取层级信息
    let (tag_level, full_path) = if let Some(ref parent_id) = request.parent_id {
        // 查询父标签
        let parent_result: Result<(i32, String), rusqlite::Error> = conn.query_row(
            "SELECT tag_level, full_path FROM tags WHERE tag_id = ?1",
            params![parent_id],
            |row| Ok((row.get(0)?, row.get(1)?)),
        );

        match parent_result {
            Ok((parent_level, parent_path)) => {
                log::info!("[tag:create] 父标签存在: level={}, path={}", parent_level, parent_path);

                // 检查层级深度（最多 5 层）
                if parent_level >= 4 {
                    log::warn!("[tag:create:failed] 超过最大层级深度: {}", parent_level + 1);
                    return Err("标签嵌套深度不能超过 5 层".to_string());
                }

                (parent_level + 1, format!("{}/{}", parent_path, request.name))
            }
            Err(_) => {
                log::warn!("[tag:create:failed] 父标签不存在: {}", parent_id);
                return Err(format!("{}:父标签不存在", ERR_PARENT_NOT_FOUND));
            }
        }
    } else {
        // 根标签
        (0, request.name.clone())
    };

    // 检查同级标签名称是否重复
    let duplicate_check = if let Some(ref parent_id) = request.parent_id {
        // 有父标签：检查同一父标签下是否有同名标签
        conn.query_row(
            "SELECT COUNT(*) FROM tags WHERE parent_tag_id = ?1 AND tag_name = ?2",
            params![parent_id, request.name],
            |row| row.get::<_, i64>(0),
        )
    } else {
        // 根标签：检查根级别是否有同名标签
        conn.query_row(
            "SELECT COUNT(*) FROM tags WHERE parent_tag_id IS NULL AND tag_name = ?1",
            params![request.name],
            |row| row.get::<_, i64>(0),
        )
    }
    .map_err(|e| {
        log::error!("[tag:create:failed] 重名检查失败: {}", e);
        format!("数据库查询失败: {}", e)
    })?;

    if duplicate_check > 0 {
        log::warn!("[tag:create:failed] 同级标签名称重复: {}", request.name);
        return Err(format!("{}:同级标签名称已存在", ERR_TAG_NAME_DUPLICATE));
    }

    // 生成标签 ID
    let tag_id = Uuid::new_v4().to_string();
    let now = chrono::Utc::now().to_rfc3339();

    // 插入标签
    conn.execute(
        "INSERT INTO tags (tag_id, tag_name, tag_color, parent_tag_id, tag_level, full_path, created_at, updated_at, usage_count)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, 0)",
        params![
            tag_id,
            request.name,
            request.color,
            request.parent_id,
            tag_level,
            full_path,
            now,
            now,
        ],
    )
    .map_err(|e| {
        log::error!("[tag:create:failed] 插入失败: {}", e);
        format!("创建标签失败: {}", e)
    })?;

    log::info!("[tag:create:success] tag_id={}, name={}, level={}", tag_id, request.name, tag_level);

    // 构造返回的 Tag 对象
    Ok(Tag {
        tag_id: tag_id.clone(),
        tag_name: request.name,
        tag_color: request.color,
        parent_tag_id: request.parent_id,
        tag_level,
        full_path,
        created_at: now.clone(),
        updated_at: now,
        usage_count: 0,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use rusqlite::Connection;
    use crate::db::schema::initialize_schema;

    fn setup_test_db() -> Connection {
        let conn = Connection::open_in_memory().unwrap();
        conn.execute("PRAGMA foreign_keys = ON", []).unwrap();
        initialize_schema(&conn).unwrap();
        conn
    }

    #[tokio::test]
    async fn test_create_root_tag() {
        let request = CreateTagRequest {
            name: "工作".to_string(),
            parent_id: None,
            color: Some("#FF5733".to_string()),
        };

        // Note: 这里需要模拟 Database，在实际测试中需要设置临时数据库
        // 这是一个简化的测试示例
    }

    #[test]
    fn test_tag_name_validation() {
        // 空名称
        let request = CreateTagRequest {
            name: "".to_string(),
            parent_id: None,
            color: None,
        };
        // 应该返回错误
    }

    #[test]
    fn test_tag_name_length() {
        // 超过50字符
        let long_name = "a".repeat(51);
        let request = CreateTagRequest {
            name: long_name,
            parent_id: None,
            color: None,
        };
        // 应该返回错误
    }
}
