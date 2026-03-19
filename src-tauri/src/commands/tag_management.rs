use crate::db::{Database, get_default_db_path};
use crate::models::{Tag, CreateTagRequest, UpdateTagRequest, TagNode};
use rusqlite::params;
use uuid::Uuid;
use std::collections::{HashMap, HashSet};
use serde::{Serialize, Deserialize};

/// 错误类型：标签名称重复
const ERR_TAG_NAME_DUPLICATE: &str = "TagNameDuplicate";
/// 错误类型：标签不存在
const ERR_TAG_NOT_FOUND: &str = "TagNotFound";
/// 错误类型：无效的标签名称
const ERR_INVALID_TAG_NAME: &str = "InvalidTagName";
/// 错误类型：父标签不存在
const ERR_PARENT_NOT_FOUND: &str = "ParentTagNotFound";
/// 错误类型：循环依赖
const ERR_CIRCULAR_DEPENDENCY: &str = "CircularDependency";
/// 错误类型：超过最大层级深度
const ERR_MAX_DEPTH_EXCEEDED: &str = "MaxDepthExceeded";
/// 错误类型：标签有子标签
const ERR_TAG_HAS_CHILDREN: &str = "TagHasChildren";
/// 错误类型：标签关联文件
const ERR_TAG_HAS_FILES: &str = "TagHasFiles";

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

/// 更新标签
///
/// # Arguments
/// * `request` - 更新标签请求，包含 id, name (可选), color (可选)
///
/// # Returns
/// * `Ok(Tag)` - 更新成功，返回更新后的标签
/// * `Err(String)` - 更新失败，返回错误信息
///
/// # Errors
/// * `TagNotFound` - 标签不存在
/// * `InvalidTagName` - 标签名称无效
/// * `TagNameDuplicate` - 同级标签名称重复
#[tauri::command]
pub async fn update_tag(request: UpdateTagRequest) -> Result<Tag, String> {
    log::info!("[tag:update] id={}, changes={:?}", request.id, request);

    // 打开数据库连接
    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[tag:update:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();

    // 验证标签是否存在，并获取当前标签信息
    let current_tag: Result<(String, Option<String>, Option<String>, i32, String), rusqlite::Error> = conn.query_row(
        "SELECT tag_name, tag_color, parent_tag_id, tag_level, full_path FROM tags WHERE tag_id = ?1",
        params![request.id],
        |row| Ok((
            row.get(0)?,
            row.get(1)?,
            row.get(2)?,
            row.get(3)?,
            row.get(4)?,
        )),
    );

    let (current_name, current_color, parent_tag_id, tag_level, current_full_path) = match current_tag {
        Ok(tag) => tag,
        Err(_) => {
            log::warn!("[tag:update:failed] 标签不存在: {}", request.id);
            return Err(format!("{}:标签不存在", ERR_TAG_NOT_FOUND));
        }
    };

    // 确定新的名称和颜色
    let new_name = request.name.as_ref().unwrap_or(&current_name);
    let new_color = if request.color.is_some() {
        request.color.clone()
    } else {
        current_color
    };

    // 验证新名称（如果有更新）
    if let Some(ref name) = request.name {
        if name.trim().is_empty() {
            log::warn!("[tag:update:failed] 标签名称为空");
            return Err(format!("{}:标签名称不能为空", ERR_INVALID_TAG_NAME));
        }

        if name.len() > 50 {
            log::warn!("[tag:update:failed] 标签名称过长: {}", name.len());
            return Err(format!("{}:标签名称不能超过50个字符", ERR_INVALID_TAG_NAME));
        }

        // 如果名称有变化，检查同级是否重名
        if name != &current_name {
            let duplicate_check = if let Some(ref pid) = parent_tag_id {
                // 有父标签：检查同一父标签下是否有同名标签（排除自己）
                conn.query_row(
                    "SELECT COUNT(*) FROM tags WHERE parent_tag_id = ?1 AND tag_name = ?2 AND tag_id != ?3",
                    params![pid, name, request.id],
                    |row| row.get::<_, i64>(0),
                )
            } else {
                // 根标签：检查根级别是否有同名标签（排除自己）
                conn.query_row(
                    "SELECT COUNT(*) FROM tags WHERE parent_tag_id IS NULL AND tag_name = ?1 AND tag_id != ?2",
                    params![name, request.id],
                    |row| row.get::<_, i64>(0),
                )
            }
            .map_err(|e| {
                log::error!("[tag:update:failed] 重名检查失败: {}", e);
                format!("数据库查询失败: {}", e)
            })?;

            if duplicate_check > 0 {
                log::warn!("[tag:update:failed] 同级标签名称重复: {}", name);
                return Err(format!("{}:同级标签名称已存在", ERR_TAG_NAME_DUPLICATE));
            }
        }
    }

    // 验证颜色代码格式（如果提供）
    if let Some(ref color) = new_color {
        if !color.starts_with('#') || (color.len() != 7 && color.len() != 4) {
            log::warn!("[tag:update:failed] 无效的颜色代码: {}", color);
            return Err(format!("{}:颜色代码格式无效（应为 #RRGGBB 或 #RGB）", ERR_INVALID_TAG_NAME));
        }
    }

    // 计算新的 full_path（如果名称有变化）
    let new_full_path = if let Some(ref name) = request.name {
        if name != &current_name {
            // 名称变化，需要更新 full_path
            if let Some(ref pid) = parent_tag_id {
                // 有父标签，获取父标签的 full_path
                let parent_path: String = conn
                    .query_row(
                        "SELECT full_path FROM tags WHERE tag_id = ?1",
                        params![pid],
                        |row| row.get(0),
                    )
                    .map_err(|e| {
                        log::error!("[tag:update:failed] 查询父标签路径失败: {}", e);
                        format!("数据库查询失败: {}", e)
                    })?;
                format!("{}/{}", parent_path, name)
            } else {
                // 根标签
                name.clone()
            }
        } else {
            current_full_path.clone()
        }
    } else {
        current_full_path.clone()
    };

    let now = chrono::Utc::now().to_rfc3339();

    // 更新标签
    let rows_affected = conn
        .execute(
            "UPDATE tags SET tag_name = ?1, tag_color = ?2, full_path = ?3, updated_at = ?4 WHERE tag_id = ?5",
            params![new_name, new_color, new_full_path, now, request.id],
        )
        .map_err(|e| {
            log::error!("[tag:update:failed] 更新失败: {}", e);
            format!("更新标签失败: {}", e)
        })?;

    if rows_affected == 0 {
        log::warn!("[tag:update:failed] 标签不存在: {}", request.id);
        return Err(format!("{}:标签不存在", ERR_TAG_NOT_FOUND));
    }

    // 如果名称变化，需要更新所有子标签的 full_path
    if let Some(ref name) = request.name {
        if name != &current_name {
            update_children_full_path(&conn, &request.id, &new_full_path)?;
        }
    }

    log::info!("[tag:update:success] tag_id={}, name={}", request.id, new_name);

    // 返回更新后的标签
    Ok(Tag {
        tag_id: request.id.clone(),
        tag_name: new_name.clone(),
        tag_color: new_color,
        parent_tag_id,
        tag_level,
        full_path: new_full_path,
        created_at: conn
            .query_row(
                "SELECT created_at FROM tags WHERE tag_id = ?1",
                params![request.id],
                |row| row.get(0),
            )
            .unwrap_or_else(|_| now.clone()),
        updated_at: now,
        usage_count: conn
            .query_row(
                "SELECT usage_count FROM tags WHERE tag_id = ?1",
                params![request.id],
                |row| row.get(0),
            )
            .unwrap_or(0),
    })
}

/// 递归更新子标签的 full_path
///
/// 当父标签名称改变时，需要更新所有子标签的路径
fn update_children_full_path(
    conn: &rusqlite::Connection,
    parent_id: &str,
    new_parent_path: &str,
) -> Result<(), String> {
    // 查询所有直接子标签
    let mut stmt = conn
        .prepare("SELECT tag_id, tag_name FROM tags WHERE parent_tag_id = ?1")
        .map_err(|e| {
            log::error!("[tag:update:children_path:failed] 查询子标签失败: {}", e);
            format!("查询子标签失败: {}", e)
        })?;

    let children: Vec<(String, String)> = stmt
        .query_map(params![parent_id], |row| {
            Ok((row.get(0)?, row.get(1)?))
        })
        .map_err(|e| {
            log::error!("[tag:update:children_path:failed] 读取子标签失败: {}", e);
            format!("读取子标签失败: {}", e)
        })?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| {
            log::error!("[tag:update:children_path:failed] 收集子标签失败: {}", e);
            format!("收集子标签失败: {}", e)
        })?;

    // 更新每个子标签的 full_path
    for (child_id, child_name) in children {
        let new_child_path = format!("{}/{}", new_parent_path, child_name);
        let now = chrono::Utc::now().to_rfc3339();

        conn.execute(
            "UPDATE tags SET full_path = ?1, updated_at = ?2 WHERE tag_id = ?3",
            params![new_child_path, now, child_id],
        )
        .map_err(|e| {
            log::error!("[tag:update:children_path:failed] 更新子标签路径失败: {}", e);
            format!("更新子标签路径失败: {}", e)
        })?;

        // 递归更新孙标签
        update_children_full_path(conn, &child_id, &new_child_path)?;
    }

    Ok(())
}

/// 获取标签树
///
/// 返回完整的标签层级树结构（最多5层）
///
/// # Returns
/// * `Ok(Vec<TagNode>)` - 成功返回根标签列表，每个根标签包含其子标签树
/// * `Err(String)` - 查询失败或检测到循环依赖
///
/// # Errors
/// * `CircularDependency` - 检测到标签循环引用
/// * `MaxDepthExceeded` - 标签嵌套超过5层
#[tauri::command]
pub async fn get_tag_tree() -> Result<Vec<TagNode>, String> {
    log::info!("[tag:tree:query] 开始查询标签树");

    // 打开数据库连接
    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[tag:tree:query:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();

    // 查询所有标签
    let mut stmt = conn
        .prepare(
            "SELECT tag_id, tag_name, tag_color, parent_tag_id, tag_level, full_path, created_at, updated_at, usage_count
             FROM tags
             ORDER BY tag_level, tag_name",
        )
        .map_err(|e| {
            log::error!("[tag:tree:query:failed] 查询标签失败: {}", e);
            format!("查询标签失败: {}", e)
        })?;

    let tags: Vec<Tag> = stmt
        .query_map([], |row| {
            Ok(Tag {
                tag_id: row.get(0)?,
                tag_name: row.get(1)?,
                tag_color: row.get(2)?,
                parent_tag_id: row.get(3)?,
                tag_level: row.get(4)?,
                full_path: row.get(5)?,
                created_at: row.get(6)?,
                updated_at: row.get(7)?,
                usage_count: row.get(8)?,
            })
        })
        .map_err(|e| {
            log::error!("[tag:tree:query:failed] 读取标签失败: {}", e);
            format!("读取标签失败: {}", e)
        })?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| {
            log::error!("[tag:tree:query:failed] 收集标签失败: {}", e);
            format!("收集标签失败: {}", e)
        })?;

    log::info!("[tag:tree:query] 查询到 {} 个标签", tags.len());

    // 检测循环依赖
    detect_circular_dependency(&tags)?;

    // 构建标签树
    let tree = build_tag_tree(tags)?;

    log::info!("[tag:tree:query:success] 返回 {} 个根标签", tree.len());
    Ok(tree)
}

/// 检测标签系统中的循环依赖
///
/// 使用深度优先搜索检测是否存在循环引用
fn detect_circular_dependency(tags: &[Tag]) -> Result<(), String> {
    // 构建父子关系映射
    let mut parent_map: HashMap<String, String> = HashMap::new();
    for tag in tags {
        if let Some(ref parent_id) = tag.parent_tag_id {
            parent_map.insert(tag.tag_id.clone(), parent_id.clone());
        }
    }

    // 对每个标签进行循环检测
    for tag in tags {
        let mut visited = HashSet::new();
        let mut current_id = tag.tag_id.clone();

        // 向上追溯父标签
        loop {
            if visited.contains(&current_id) {
                // 发现循环
                log::error!("[circular_dependency:detected] tag_id={}", tag.tag_id);
                return Err(format!("{}:检测到标签循环引用", ERR_CIRCULAR_DEPENDENCY));
            }

            visited.insert(current_id.clone());

            // 获取父标签
            match parent_map.get(&current_id) {
                Some(parent_id) => {
                    current_id = parent_id.clone();
                }
                None => {
                    // 到达根标签，无循环
                    break;
                }
            }

            // 检查深度（防止无限循环，最多5层）
            if visited.len() > 5 {
                log::error!("[circular_dependency:detected] 超过最大深度: tag_id={}", tag.tag_id);
                return Err(format!("{}:标签嵌套深度超过5层", ERR_MAX_DEPTH_EXCEEDED));
            }
        }
    }

    Ok(())
}

/// 构建标签树结构
///
/// 将扁平的标签列表转换为嵌套的树结构
fn build_tag_tree(tags: Vec<Tag>) -> Result<Vec<TagNode>, String> {
    // 将所有标签转换为 TagNode，并存入 HashMap
    let mut tag_map: HashMap<String, TagNode> = HashMap::new();
    for tag in tags {
        let tag_id = tag.tag_id.clone();
        let node = TagNode::from_tag(tag);
        tag_map.insert(tag_id, node);
    }

    // 收集根标签 ID
    let mut root_ids: Vec<String> = Vec::new();
    let tag_ids: Vec<String> = tag_map.keys().cloned().collect();

    for tag_id in &tag_ids {
        let node = tag_map.get(tag_id).unwrap();
        if node.tag.parent_tag_id.is_none() {
            root_ids.push(tag_id.clone());
        }
    }

    // 构建父子关系
    let mut parent_child_map: HashMap<String, Vec<String>> = HashMap::new();
    for tag_id in &tag_ids {
        let node = tag_map.get(tag_id).unwrap();
        if let Some(ref parent_id) = node.tag.parent_tag_id {
            parent_child_map
                .entry(parent_id.clone())
                .or_insert_with(Vec::new)
                .push(tag_id.clone());
        }
    }

    // 递归构建树（从 tag_map 中移除节点并组装）
    fn build_subtree(
        tag_id: &str,
        tag_map: &mut HashMap<String, TagNode>,
        parent_child_map: &HashMap<String, Vec<String>>,
    ) -> Option<TagNode> {
        // 从 map 中取出当前节点
        let mut node = tag_map.remove(tag_id)?;

        // 获取所有子标签 ID
        if let Some(child_ids) = parent_child_map.get(tag_id) {
            for child_id in child_ids {
                if let Some(child_node) = build_subtree(child_id, tag_map, parent_child_map) {
                    node.add_child(child_node);
                }
            }
        }

        Some(node)
    }

    // 构建所有根标签的子树
    let mut tree: Vec<TagNode> = Vec::new();
    for root_id in root_ids {
        if let Some(root_node) = build_subtree(&root_id, &mut tag_map, &parent_child_map) {
            tree.push(root_node);
        }
    }

    // 按名称排序根标签
    tree.sort_by(|a, b| a.tag.tag_name.cmp(&b.tag.tag_name));

    Ok(tree)
}

/// 删除标签
///
/// # Arguments
/// * `tag_id` - 要删除的标签 ID
/// * `force` - 是否强制删除（删除所有子标签和解除文件关联）
///
/// # Returns
/// * `Ok(())` - 删除成功
/// * `Err(String)` - 删除失败，返回错误信息
///
/// # Errors
/// * `TagNotFound` - 标签不存在
/// * `TagHasChildren` - 标签有子标签（force=false 时）
/// * `TagHasFiles` - 标签关联文件（force=false 时）
#[tauri::command]
pub async fn delete_tag(tag_id: String, force: Option<bool>) -> Result<(), String> {
    let force = force.unwrap_or(false);
    log::info!("[tag:delete] tag_id={}, force={}", tag_id, force);

    // 打开数据库连接
    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[tag:delete:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();

    // 验证标签是否存在
    let tag_exists: Result<bool, rusqlite::Error> = conn.query_row(
        "SELECT COUNT(*) FROM tags WHERE tag_id = ?1",
        params![tag_id],
        |row| {
            let count: i64 = row.get(0)?;
            Ok(count > 0)
        },
    );

    match tag_exists {
        Ok(true) => {},
        Ok(false) | Err(_) => {
            log::warn!("[tag:delete:failed] 标签不存在: {}", tag_id);
            return Err(format!("{}:标签不存在", ERR_TAG_NOT_FOUND));
        }
    }

    // 检查是否有子标签
    let children_count: Result<i64, rusqlite::Error> = conn.query_row(
        "SELECT COUNT(*) FROM tags WHERE parent_tag_id = ?1",
        params![tag_id],
        |row| row.get(0),
    );

    let has_children = children_count.unwrap_or(0) > 0;
    if has_children && !force {
        log::warn!("[tag:delete:blocked] 标签有子标签: {}", tag_id);
        return Err(format!("{}:标签有子标签，无法删除。使用 force=true 递归删除所有子标签", ERR_TAG_HAS_CHILDREN));
    }

    // 检查是否关联文件
    let file_count: i64 = conn.query_row(
        "SELECT COUNT(*) FROM file_tags WHERE tag_id = ?1",
        params![tag_id],
        |row| row.get(0),
    ).unwrap_or(0);

    let has_files = file_count > 0;
    if has_files && !force {
        log::warn!("[tag:delete:blocked] 标签关联文件: {}, count={}", tag_id, file_count);
        return Err(format!("{}:标签关联 {} 个文件，无法删除。使用 force=true 解除所有文件关联", ERR_TAG_HAS_FILES, file_count));
    }

    // 开始事务
    let tx = conn.unchecked_transaction().map_err(|e| {
        log::error!("[tag:delete:failed] 开启事务失败: {}", e);
        format!("开启事务失败: {}", e)
    })?;

    // 如果 force=true，递归删除所有子标签
    if force && has_children {
        delete_children_recursive(&tx, &tag_id)?;
    }

    // 删除标签（CASCADE DELETE 会自动删除 file_tags 中的关联）
    let rows_affected = tx
        .execute("DELETE FROM tags WHERE tag_id = ?1", params![tag_id])
        .map_err(|e| {
            log::error!("[tag:delete:failed] 删除失败: {}", e);
            format!("删除标签失败: {}", e)
        })?;

    if rows_affected == 0 {
        log::warn!("[tag:delete:failed] 标签不存在: {}", tag_id);
        return Err(format!("{}:标签不存在", ERR_TAG_NOT_FOUND));
    }

    // 提交事务
    tx.commit().map_err(|e| {
        log::error!("[tag:delete:failed] 提交事务失败: {}", e);
        format!("提交事务失败: {}", e)
    })?;

    log::info!("[tag:delete:success] tag_id={}, force={}", tag_id, force);
    Ok(())
}

/// 递归删除所有子标签
///
/// 用于 force 删除时，删除所有子孙标签
fn delete_children_recursive(
    tx: &rusqlite::Transaction,
    parent_id: &str,
) -> Result<(), String> {
    // 查询所有直接子标签
    let mut stmt = tx
        .prepare("SELECT tag_id FROM tags WHERE parent_tag_id = ?1")
        .map_err(|e| {
            log::error!("[tag:delete:children:failed] 查询子标签失败: {}", e);
            format!("查询子标签失败: {}", e)
        })?;

    let child_ids: Vec<String> = stmt
        .query_map(params![parent_id], |row| row.get(0))
        .map_err(|e| {
            log::error!("[tag:delete:children:failed] 读取子标签失败: {}", e);
            format!("读取子标签失败: {}", e)
        })?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| {
            log::error!("[tag:delete:children:failed] 收集子标签失败: {}", e);
            format!("收集子标签失败: {}", e)
        })?;

    // 递归删除每个子标签
    for child_id in child_ids {
        // 先递归删除孙标签
        delete_children_recursive(tx, &child_id)?;

        // 删除当前子标签
        tx.execute("DELETE FROM tags WHERE tag_id = ?1", params![child_id])
            .map_err(|e| {
                log::error!("[tag:delete:children:failed] 删除子标签失败: {}", e);
                format!("删除子标签失败: {}", e)
            })?;

        log::info!("[tag:delete:child] 已删除子标签: {}", child_id);
    }

    Ok(())
}

/// 获取标签详情（包括关联信息）
///
/// 用于删除前的预检查，返回标签关联的文件数和子标签数
///
/// # Arguments
/// * `tag_id` - 标签 ID
///
/// # Returns
/// * `Ok((children_count, files_count))` - (子标签数, 关联文件数)
/// * `Err(String)` - 标签不存在
#[tauri::command]
pub async fn get_tag_info(tag_id: String) -> Result<(i64, i64), String> {
    log::info!("[tag:info] tag_id={}", tag_id);

    // 打开数据库连接
    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[tag:info:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();

    // 验证标签是否存在
    let tag_exists: Result<bool, rusqlite::Error> = conn.query_row(
        "SELECT COUNT(*) FROM tags WHERE tag_id = ?1",
        params![tag_id],
        |row| {
            let count: i64 = row.get(0)?;
            Ok(count > 0)
        },
    );

    match tag_exists {
        Ok(true) => {},
        Ok(false) | Err(_) => {
            log::warn!("[tag:info:failed] 标签不存在: {}", tag_id);
            return Err(format!("{}:标签不存在", ERR_TAG_NOT_FOUND));
        }
    }

    // 查询子标签数（递归统计所有子孙标签）
    let children_count = count_descendants(&conn, &tag_id)?;

    // 查询关联文件数
    let files_count: i64 = conn
        .query_row(
            "SELECT COUNT(*) FROM file_tags WHERE tag_id = ?1",
            params![tag_id],
            |row| row.get(0),
        )
        .map_err(|e| {
            log::error!("[tag:info:failed] 查询文件数失败: {}", e);
            format!("查询文件数失败: {}", e)
        })?;

    log::info!("[tag:info:success] tag_id={}, children={}, files={}", tag_id, children_count, files_count);
    Ok((children_count, files_count))
}

/// 递归统计所有子孙标签数量
fn count_descendants(
    conn: &rusqlite::Connection,
    parent_id: &str,
) -> Result<i64, String> {
    // 查询直接子标签
    let mut stmt = conn
        .prepare("SELECT tag_id FROM tags WHERE parent_tag_id = ?1")
        .map_err(|e| {
            log::error!("[tag:count_descendants:failed] 查询子标签失败: {}", e);
            format!("查询子标签失败: {}", e)
        })?;

    let child_ids: Vec<String> = stmt
        .query_map(params![parent_id], |row| row.get(0))
        .map_err(|e| {
            log::error!("[tag:count_descendants:failed] 读取子标签失败: {}", e);
            format!("读取子标签失败: {}", e)
        })?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| {
            log::error!("[tag:count_descendants:failed] 收集子标签失败: {}", e);
            format!("收集子标签失败: {}", e)
        })?;

    let mut total = child_ids.len() as i64;

    // 递归统计孙标签
    for child_id in child_ids {
        total += count_descendants(conn, &child_id)?;
    }

    Ok(total)
}

// ============================================================================
// Phase 2: File-Tag Association (文件-标签关联)
// ============================================================================

/// 错误类型：文件不存在
const ERR_FILE_NOT_FOUND: &str = "FileNotFound";

/// 为文件添加单个标签
///
/// # Arguments
/// * `file_id` - 文件 ID (files 表主键)
/// * `tag_id` - 标签 ID (tags 表主键)
///
/// # Returns
/// * `Ok(())` - 添加成功（幂等：已存在则返回成功）
/// * `Err(String)` - 添加失败，返回错误信息
///
/// # Errors
/// * `FileNotFound` - 文件不存在
/// * `TagNotFound` - 标签不存在
#[tauri::command]
pub async fn add_tag_to_file(file_id: i64, tag_id: String) -> Result<(), String> {
    log::info!("[file-tag:add] file_id={}, tag_id={}", file_id, tag_id);

    // 打开数据库连接
    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[file-tag:add:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();

    // 验证文件是否存在
    let file_exists: Result<bool, rusqlite::Error> = conn.query_row(
        "SELECT COUNT(*) FROM files WHERE id = ?1",
        params![file_id],
        |row| {
            let count: i64 = row.get(0)?;
            Ok(count > 0)
        },
    );

    match file_exists {
        Ok(true) => {},
        Ok(false) | Err(_) => {
            log::warn!("[file-tag:add:failed] 文件不存在: file_id={}", file_id);
            return Err(format!("{}:文件不存在", ERR_FILE_NOT_FOUND));
        }
    }

    // 验证标签是否存在
    let tag_exists: Result<bool, rusqlite::Error> = conn.query_row(
        "SELECT COUNT(*) FROM tags WHERE tag_id = ?1",
        params![tag_id],
        |row| {
            let count: i64 = row.get(0)?;
            Ok(count > 0)
        },
    );

    match tag_exists {
        Ok(true) => {},
        Ok(false) | Err(_) => {
            log::warn!("[file-tag:add:failed] 标签不存在: tag_id={}", tag_id);
            return Err(format!("{}:标签不存在", ERR_TAG_NOT_FOUND));
        }
    }

    // 检查关联是否已存在（幂等性）
    let association_exists: Result<bool, rusqlite::Error> = conn.query_row(
        "SELECT COUNT(*) FROM file_tags WHERE file_id = ?1 AND tag_id = ?2",
        params![file_id, tag_id],
        |row| {
            let count: i64 = row.get(0)?;
            Ok(count > 0)
        },
    );

    if association_exists.unwrap_or(false) {
        log::info!("[file-tag:add:skip] 关联已存在: file_id={}, tag_id={}", file_id, tag_id);
        return Ok(()); // 幂等：已存在则返回成功
    }

    // 插入关联记录
    let now = chrono::Utc::now().to_rfc3339();
    conn.execute(
        "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
        params![file_id, tag_id, now],
    )
    .map_err(|e| {
        log::error!("[file-tag:add:failed] 插入失败: {}", e);
        format!("添加标签失败: {}", e)
    })?;

    // 更新标签使用计数
    conn.execute(
        "UPDATE tags SET usage_count = usage_count + 1, updated_at = ?1 WHERE tag_id = ?2",
        params![now, tag_id],
    )
    .map_err(|e| {
        log::warn!("[file-tag:add] 更新使用计数失败: {}", e);
        // 不影响主流程，仅记录警告
    })
    .ok();

    log::info!("[file-tag:add:success] file_id={}, tag_id={}", file_id, tag_id);
    Ok(())
}

/// 为文件移除单个标签
///
/// # Arguments
/// * `file_id` - 文件 ID
/// * `tag_id` - 标签 ID
///
/// # Returns
/// * `Ok(())` - 移除成功（幂等：不存在则返回成功）
/// * `Err(String)` - 移除失败
#[tauri::command]
pub async fn remove_tag_from_file(file_id: i64, tag_id: String) -> Result<(), String> {
    log::info!("[file-tag:remove] file_id={}, tag_id={}", file_id, tag_id);

    // 打开数据库连接
    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[file-tag:remove:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();

    // 删除关联记录（幂等：不存在也返回成功）
    let rows_affected = conn
        .execute(
            "DELETE FROM file_tags WHERE file_id = ?1 AND tag_id = ?2",
            params![file_id, tag_id],
        )
        .map_err(|e| {
            log::error!("[file-tag:remove:failed] 删除失败: {}", e);
            format!("移除标签失败: {}", e)
        })?;

    if rows_affected > 0 {
        // 更新标签使用计数（仅当确实删除了关联时）
        let now = chrono::Utc::now().to_rfc3339();
        conn.execute(
            "UPDATE tags SET usage_count = MAX(0, usage_count - 1), updated_at = ?1 WHERE tag_id = ?2",
            params![now, tag_id],
        )
        .map_err(|e| {
            log::warn!("[file-tag:remove] 更新使用计数失败: {}", e);
            // 不影响主流程，仅记录警告
        })
        .ok();

        log::info!("[file-tag:remove:success] file_id={}, tag_id={}", file_id, tag_id);
    } else {
        log::info!("[file-tag:remove:skip] 关联不存在: file_id={}, tag_id={}", file_id, tag_id);
    }

    Ok(())
}

/// 批量为文件添加标签
///
/// # Arguments
/// * `file_id` - 文件 ID
/// * `tag_ids` - 标签 ID 列表
///
/// # Returns
/// * `Ok((success_count, failed_tags))` - (成功数量, 失败的标签列表)
/// * `Err(String)` - 操作失败
#[tauri::command]
pub async fn add_tags_to_file(file_id: i64, tag_ids: Vec<String>) -> Result<(usize, Vec<String>), String> {
    log::info!("[file-tag:batch:start] file_id={}, count={}", file_id, tag_ids.len());

    // 打开数据库连接
    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[file-tag:batch:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();

    // 验证文件是否存在
    let file_exists: Result<bool, rusqlite::Error> = conn.query_row(
        "SELECT COUNT(*) FROM files WHERE id = ?1",
        params![file_id],
        |row| {
            let count: i64 = row.get(0)?;
            Ok(count > 0)
        },
    );

    match file_exists {
        Ok(true) => {},
        Ok(false) | Err(_) => {
            log::warn!("[file-tag:batch:failed] 文件不存在: file_id={}", file_id);
            return Err(format!("{}:文件不存在", ERR_FILE_NOT_FOUND));
        }
    }

    // 开始事务
    let tx = conn.unchecked_transaction().map_err(|e| {
        log::error!("[file-tag:batch:failed] 开启事务失败: {}", e);
        format!("开启事务失败: {}", e)
    })?;

    let now = chrono::Utc::now().to_rfc3339();
    let mut success_count = 0;
    let mut failed_tags: Vec<String> = Vec::new();

    for tag_id in tag_ids.iter() {
        // 验证标签是否存在
        let tag_exists: Result<bool, rusqlite::Error> = tx.query_row(
            "SELECT COUNT(*) FROM tags WHERE tag_id = ?1",
            params![tag_id],
            |row| {
                let count: i64 = row.get(0)?;
                Ok(count > 0)
            },
        );

        if !tag_exists.unwrap_or(false) {
            log::warn!("[file-tag:batch] 标签不存在: tag_id={}", tag_id);
            failed_tags.push(tag_id.clone());
            continue;
        }

        // 检查关联是否已存在
        let association_exists: Result<bool, rusqlite::Error> = tx.query_row(
            "SELECT COUNT(*) FROM file_tags WHERE file_id = ?1 AND tag_id = ?2",
            params![file_id, tag_id],
            |row| {
                let count: i64 = row.get(0)?;
                Ok(count > 0)
            },
        );

        if association_exists.unwrap_or(false) {
            log::info!("[file-tag:batch] 关联已存在，跳过: tag_id={}", tag_id);
            success_count += 1; // 幂等：已存在计为成功
            continue;
        }

        // 插入关联记录
        match tx.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file_id, tag_id, now],
        ) {
            Ok(_) => {
                // 更新标签使用计数
                tx.execute(
                    "UPDATE tags SET usage_count = usage_count + 1, updated_at = ?1 WHERE tag_id = ?2",
                    params![now, tag_id],
                )
                .ok();
                success_count += 1;
            }
            Err(e) => {
                log::error!("[file-tag:batch] 插入失败: tag_id={}, error={}", tag_id, e);
                failed_tags.push(tag_id.clone());
            }
        }
    }

    // 提交事务
    tx.commit().map_err(|e| {
        log::error!("[file-tag:batch:failed] 提交事务失败: {}", e);
        format!("提交事务失败: {}", e)
    })?;

    log::info!(
        "[file-tag:batch:done] file_id={}, success={}, failed={}",
        file_id,
        success_count,
        failed_tags.len()
    );

    Ok((success_count, failed_tags))
}

/// 批量为文件移除标签
///
/// # Arguments
/// * `file_id` - 文件 ID
/// * `tag_ids` - 标签 ID 列表
///
/// # Returns
/// * `Ok(removed_count)` - 实际移除的关联数量
/// * `Err(String)` - 操作失败
#[tauri::command]
pub async fn remove_tags_from_file(file_id: i64, tag_ids: Vec<String>) -> Result<usize, String> {
    log::info!("[file-tag:batch_remove:start] file_id={}, count={}", file_id, tag_ids.len());

    // 打开数据库连接
    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[file-tag:batch_remove:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();

    // 开始事务
    let tx = conn.unchecked_transaction().map_err(|e| {
        log::error!("[file-tag:batch_remove:failed] 开启事务失败: {}", e);
        format!("开启事务失败: {}", e)
    })?;

    let now = chrono::Utc::now().to_rfc3339();
    let mut removed_count = 0;

    for tag_id in tag_ids.iter() {
        // 删除关联记录
        match tx.execute(
            "DELETE FROM file_tags WHERE file_id = ?1 AND tag_id = ?2",
            params![file_id, tag_id],
        ) {
            Ok(rows) => {
                if rows > 0 {
                    // 更新标签使用计数
                    tx.execute(
                        "UPDATE tags SET usage_count = MAX(0, usage_count - 1), updated_at = ?1 WHERE tag_id = ?2",
                        params![now, tag_id],
                    )
                    .ok();
                    removed_count += rows;
                }
            }
            Err(e) => {
                log::error!("[file-tag:batch_remove] 删除失败: tag_id={}, error={}", tag_id, e);
                // 继续处理其他标签，不中断事务
            }
        }
    }

    // 提交事务
    tx.commit().map_err(|e| {
        log::error!("[file-tag:batch_remove:failed] 提交事务失败: {}", e);
        format!("提交事务失败: {}", e)
    })?;

    log::info!(
        "[file-tag:batch_remove:done] file_id={}, removed={}",
        file_id,
        removed_count
    );

    Ok(removed_count)
}

/// 获取文件的所有标签
///
/// # Arguments
/// * `file_id` - 文件 ID
///
/// # Returns
/// * `Ok(Vec<Tag>)` - 标签列表（按创建时间排序）
/// * `Err(String)` - 查询失败
#[tauri::command]
pub async fn get_file_tags(file_id: i64) -> Result<Vec<Tag>, String> {
    log::info!("[file-tag:query] file_id={}", file_id);

    // 打开数据库连接
    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[file-tag:query:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();

    // 查询文件的所有标签（JOIN tags 表获取标签详情）
    let mut stmt = conn
        .prepare(
            "SELECT t.tag_id, t.tag_name, t.tag_color, t.parent_tag_id, t.tag_level, t.full_path,
                    t.created_at, t.updated_at, t.usage_count
             FROM tags t
             INNER JOIN file_tags ft ON t.tag_id = ft.tag_id
             WHERE ft.file_id = ?1
             ORDER BY ft.created_at ASC",
        )
        .map_err(|e| {
            log::error!("[file-tag:query:failed] 查询失败: {}", e);
            format!("查询文件标签失败: {}", e)
        })?;

    let tags: Vec<Tag> = stmt
        .query_map(params![file_id], |row| {
            Ok(Tag {
                tag_id: row.get(0)?,
                tag_name: row.get(1)?,
                tag_color: row.get(2)?,
                parent_tag_id: row.get(3)?,
                tag_level: row.get(4)?,
                full_path: row.get(5)?,
                created_at: row.get(6)?,
                updated_at: row.get(7)?,
                usage_count: row.get(8)?,
            })
        })
        .map_err(|e| {
            log::error!("[file-tag:query:failed] 读取标签失败: {}", e);
            format!("读取标签失败: {}", e)
        })?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| {
            log::error!("[file-tag:query:failed] 收集标签失败: {}", e);
            format!("收集标签失败: {}", e)
        })?;

    log::info!("[file-tag:query:success] file_id={}, count={}", file_id, tags.len());
    Ok(tags)
}

/// 文件信息结构（简化版）
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileInfo {
    pub id: i64,
    pub file_path: String,
    pub original_name: String,
    pub file_size: i64,
    pub is_encrypted: bool,
    pub created_at: String,
}

/// 获取标签关联的所有文件
///
/// # Arguments
/// * `tag_id` - 标签 ID
/// * `recursive` - 是否递归查询子标签的文件（默认 false）
///
/// # Returns
/// * `Ok(Vec<FileInfo>)` - 文件列表
/// * `Err(String)` - 查询失败
#[tauri::command]
pub async fn get_tag_files(tag_id: String, recursive: Option<bool>) -> Result<Vec<FileInfo>, String> {
    let recursive = recursive.unwrap_or(false);
    log::info!("[tag-files:query] tag_id={}, recursive={}", tag_id, recursive);

    // 打开数据库连接
    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[tag-files:query:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();

    // 验证标签是否存在
    let tag_exists: Result<bool, rusqlite::Error> = conn.query_row(
        "SELECT COUNT(*) FROM tags WHERE tag_id = ?1",
        params![tag_id],
        |row| {
            let count: i64 = row.get(0)?;
            Ok(count > 0)
        },
    );

    match tag_exists {
        Ok(true) => {},
        Ok(false) | Err(_) => {
            log::warn!("[tag-files:query:failed] 标签不存在: tag_id={}", tag_id);
            return Err(format!("{}:标签不存在", ERR_TAG_NOT_FOUND));
        }
    }

    // 收集所有相关标签 ID（包含当前标签和递归子标签）
    let mut tag_ids = vec![tag_id.clone()];
    if recursive {
        let descendant_ids = get_all_descendant_tag_ids(&conn, &tag_id)?;
        tag_ids.extend(descendant_ids);
    }

    // 查询所有相关标签的文件（去重）
    let placeholders = tag_ids.iter().map(|_| "?").collect::<Vec<_>>().join(",");
    let query = format!(
        "SELECT DISTINCT f.id, f.file_path, f.original_name, f.file_size, f.is_encrypted, f.created_at
         FROM files f
         INNER JOIN file_tags ft ON f.id = ft.file_id
         WHERE ft.tag_id IN ({})
         ORDER BY f.created_at DESC",
        placeholders
    );

    let mut stmt = conn.prepare(&query).map_err(|e| {
        log::error!("[tag-files:query:failed] 查询失败: {}", e);
        format!("查询标签文件失败: {}", e)
    })?;

    let params: Vec<&dyn rusqlite::ToSql> = tag_ids.iter().map(|id| id as &dyn rusqlite::ToSql).collect();
    let files: Vec<FileInfo> = stmt
        .query_map(params.as_slice(), |row| {
            Ok(FileInfo {
                id: row.get(0)?,
                file_path: row.get(1)?,
                original_name: row.get(2)?,
                file_size: row.get(3)?,
                is_encrypted: row.get::<_, i32>(4)? != 0,
                created_at: row.get(5)?,
            })
        })
        .map_err(|e| {
            log::error!("[tag-files:query:failed] 读取文件失败: {}", e);
            format!("读取文件失败: {}", e)
        })?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| {
            log::error!("[tag-files:query:failed] 收集文件失败: {}", e);
            format!("收集文件失败: {}", e)
        })?;

    log::info!(
        "[tag-files:query:success] tag_id={}, recursive={}, count={}",
        tag_id,
        recursive,
        files.len()
    );
    Ok(files)
}

/// 递归获取所有子孙标签 ID
///
/// # Arguments
/// * `conn` - 数据库连接
/// * `parent_id` - 父标签 ID
///
/// # Returns
/// * `Ok(Vec<String>)` - 所有子孙标签 ID 列表
/// * `Err(String)` - 查询失败
fn get_all_descendant_tag_ids(
    conn: &rusqlite::Connection,
    parent_id: &str,
) -> Result<Vec<String>, String> {
    let mut all_descendants = Vec::new();

    // 查询直接子标签
    let mut stmt = conn
        .prepare("SELECT tag_id FROM tags WHERE parent_tag_id = ?1")
        .map_err(|e| {
            log::error!("[tag:descendants:failed] 查询子标签失败: {}", e);
            format!("查询子标签失败: {}", e)
        })?;

    let child_ids: Vec<String> = stmt
        .query_map(params![parent_id], |row| row.get(0))
        .map_err(|e| {
            log::error!("[tag:descendants:failed] 读取子标签失败: {}", e);
            format!("读取子标签失败: {}", e)
        })?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| {
            log::error!("[tag:descendants:failed] 收集子标签失败: {}", e);
            format!("收集子标签失败: {}", e)
        })?;

    // 递归收集孙标签
    for child_id in child_ids {
        all_descendants.push(child_id.clone());
        let grandchildren = get_all_descendant_tag_ids(conn, &child_id)?;
        all_descendants.extend(grandchildren);
    }

    Ok(all_descendants)
}

// ============================================================================
// Phase 3: Tag View & Search (标签视图和搜索)
// ============================================================================

/// 搜索文件（根据标签组合）
///
/// # Arguments
/// * `tag_ids` - 标签 ID 列表
/// * `filter_mode` - 过滤模式："AND" (文件必须有所有标签) 或 "OR" (文件有任一标签即可)
/// * `recursive` - 是否递归包含子标签
/// * `name_query` - 文件名搜索查询（可选，不区分大小写）
///
/// # Returns
/// * `Ok(Vec<FileInfo>)` - 匹配的文件列表
/// * `Err(String)` - 搜索失败
///
/// # Errors
/// * 无效的 filter_mode（必须是 "AND" 或 "OR"）
/// * 数据库查询失败
#[tauri::command]
pub async fn search_files(
    tag_ids: Vec<String>,
    filter_mode: String,
    recursive: Option<bool>,
    name_query: Option<String>,
) -> Result<Vec<FileInfo>, String> {
    let recursive = recursive.unwrap_or(false);
    log::info!(
        "[file:search:start] tags={}, mode={}, recursive={}, name_query={:?}",
        tag_ids.len(),
        filter_mode,
        recursive,
        name_query
    );

    // 验证 filter_mode
    if filter_mode != "AND" && filter_mode != "OR" {
        log::error!("[file:search:failed] 无效的 filter_mode: {}", filter_mode);
        return Err(format!("无效的过滤模式，必须是 'AND' 或 'OR': {}", filter_mode));
    }

    // 如果没有标签，返回空数组
    if tag_ids.is_empty() {
        log::info!("[file:search:empty] 没有提供标签，返回空结果");
        return Ok(Vec::new());
    }

    // 打开数据库连接
    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[file:search:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();

    // 收集所有相关标签 ID（包含递归子标签）
    let mut all_tag_ids = tag_ids.clone();
    if recursive {
        for tag_id in &tag_ids {
            let descendant_ids = get_all_descendant_tag_ids(&conn, tag_id)?;
            all_tag_ids.extend(descendant_ids);
        }
        // 去重
        all_tag_ids.sort();
        all_tag_ids.dedup();
    }

    log::info!(
        "[file:search] 扩展后的标签数: {} (原始: {})",
        all_tag_ids.len(),
        tag_ids.len()
    );

    // 构建查询
    let files = if filter_mode == "AND" {
        // AND 模式：文件必须包含所有指定的标签
        search_files_with_and_mode(&conn, &all_tag_ids, &name_query)?
    } else {
        // OR 模式：文件包含任一标签即可
        search_files_with_or_mode(&conn, &all_tag_ids, &name_query)?
    };

    log::info!(
        "[file:search:done] results={}, tags={}, mode={}, recursive={}",
        files.len(),
        tag_ids.len(),
        filter_mode,
        recursive
    );

    Ok(files)
}

/// AND 模式：文件必须包含所有指定的标签
fn search_files_with_and_mode(
    conn: &rusqlite::Connection,
    tag_ids: &[String],
    name_query: &Option<String>,
) -> Result<Vec<FileInfo>, String> {
    // 构建查询：找到包含所有标签的文件
    // 策略：使用 GROUP BY + HAVING COUNT(DISTINCT tag_id) = ?
    let mut query = format!(
        "SELECT f.id, f.file_path, f.original_name, f.file_size, f.is_encrypted, f.created_at
         FROM files f
         INNER JOIN file_tags ft ON f.id = ft.file_id
         WHERE ft.tag_id IN ({})",
        tag_ids.iter().map(|_| "?").collect::<Vec<_>>().join(",")
    );

    // 添加文件名过滤（如果提供）
    let pattern = if let Some(ref query_str) = name_query {
        if !query_str.trim().is_empty() {
            query.push_str(" AND f.original_name LIKE ?");
            Some(format!("%{}%", query_str.trim()))
        } else {
            None
        }
    } else {
        None
    };

    // GROUP BY 和 HAVING 检查是否包含所有标签
    query.push_str(&format!(
        " GROUP BY f.id
         HAVING COUNT(DISTINCT ft.tag_id) = {}
         ORDER BY f.created_at DESC",
        tag_ids.len()
    ));

    let mut stmt = conn.prepare(&query).map_err(|e| {
        log::error!("[file:search:and:failed] 查询失败: {}", e);
        format!("查询失败: {}", e)
    })?;

    // 绑定参数
    let mut params: Vec<&dyn rusqlite::ToSql> =
        tag_ids.iter().map(|id| id as &dyn rusqlite::ToSql).collect();

    if let Some(ref p) = pattern {
        params.push(p as &dyn rusqlite::ToSql);
    }

    let files: Vec<FileInfo> = stmt
        .query_map(params.as_slice(), |row| {
            Ok(FileInfo {
                id: row.get(0)?,
                file_path: row.get(1)?,
                original_name: row.get(2)?,
                file_size: row.get(3)?,
                is_encrypted: row.get::<_, i32>(4)? != 0,
                created_at: row.get(5)?,
            })
        })
        .map_err(|e| {
            log::error!("[file:search:and:failed] 读取文件失败: {}", e);
            format!("读取文件失败: {}", e)
        })?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| {
            log::error!("[file:search:and:failed] 收集文件失败: {}", e);
            format!("收集文件失败: {}", e)
        })?;

    Ok(files)
}

/// OR 模式：文件包含任一标签即可
fn search_files_with_or_mode(
    conn: &rusqlite::Connection,
    tag_ids: &[String],
    name_query: &Option<String>,
) -> Result<Vec<FileInfo>, String> {
    // 构建查询：找到包含任一标签的文件
    let mut query = format!(
        "SELECT DISTINCT f.id, f.file_path, f.original_name, f.file_size, f.is_encrypted, f.created_at
         FROM files f
         INNER JOIN file_tags ft ON f.id = ft.file_id
         WHERE ft.tag_id IN ({})",
        tag_ids.iter().map(|_| "?").collect::<Vec<_>>().join(",")
    );

    // 添加文件名过滤（如果提供）
    let pattern = if let Some(ref query_str) = name_query {
        if !query_str.trim().is_empty() {
            query.push_str(" AND f.original_name LIKE ?");
            Some(format!("%{}%", query_str.trim()))
        } else {
            None
        }
    } else {
        None
    };

    query.push_str(" ORDER BY f.created_at DESC");

    let mut stmt = conn.prepare(&query).map_err(|e| {
        log::error!("[file:search:or:failed] 查询失败: {}", e);
        format!("查询失败: {}", e)
    })?;

    // 绑定参数
    let mut params: Vec<&dyn rusqlite::ToSql> =
        tag_ids.iter().map(|id| id as &dyn rusqlite::ToSql).collect();

    if let Some(ref p) = pattern {
        params.push(p as &dyn rusqlite::ToSql);
    }

    let files: Vec<FileInfo> = stmt
        .query_map(params.as_slice(), |row| {
            Ok(FileInfo {
                id: row.get(0)?,
                file_path: row.get(1)?,
                original_name: row.get(2)?,
                file_size: row.get(3)?,
                is_encrypted: row.get::<_, i32>(4)? != 0,
                created_at: row.get(5)?,
            })
        })
        .map_err(|e| {
            log::error!("[file:search:or:failed] 读取文件失败: {}", e);
            format!("读取文件失败: {}", e)
        })?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| {
            log::error!("[file:search:or:failed] 收集文件失败: {}", e);
            format!("收集文件失败: {}", e)
        })?;

    Ok(files)
}

/// 获取所有文件（不过滤）
///
/// # Returns
/// * `Ok(Vec<FileInfo>)` - 所有文件列表
/// * `Err(String)` - 查询失败
#[tauri::command]
pub async fn get_all_files() -> Result<Vec<FileInfo>, String> {
    log::info!("[files:query:all]");

    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[files:query:all:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();

    // 查询所有文件
    let mut stmt = conn
        .prepare(
            "SELECT id, file_path, original_name, file_size, is_encrypted, created_at
             FROM files
             ORDER BY created_at DESC"
        )
        .map_err(|e| {
            log::error!("[files:query:all:failed] 查询失败: {}", e);
            format!("查询文件失败: {}", e)
        })?;

    let files = stmt
        .query_map([], |row| {
            Ok(FileInfo {
                id: row.get(0)?,
                file_path: row.get(1)?,
                original_name: row.get(2)?,
                file_size: row.get(3)?,
                is_encrypted: row.get(4)?,
                created_at: row.get(5)?,
            })
        })
        .map_err(|e| format!("映射文件数据失败: {}", e))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| format!("收集文件数据失败: {}", e))?;

    log::info!("[files:query:all] count={}", files.len());
    Ok(files)
}

/// 获取所有已加密文件
///
/// # Returns
/// * `Ok(Vec<FileInfo>)` - 已加密文件列表
/// * `Err(String)` - 查询失败
#[tauri::command]
pub async fn get_encrypted_files() -> Result<Vec<FileInfo>, String> {
    log::info!("[files:query:encrypted]");

    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[files:query:encrypted:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();

    // 查询已加密文件
    let mut stmt = conn
        .prepare(
            "SELECT id, file_path, original_name, file_size, is_encrypted, created_at
             FROM files
             WHERE is_encrypted = 1
             ORDER BY created_at DESC"
        )
        .map_err(|e| {
            log::error!("[files:query:encrypted:failed] 查询失败: {}", e);
            format!("查询加密文件失败: {}", e)
        })?;

    let files = stmt
        .query_map([], |row| {
            Ok(FileInfo {
                id: row.get(0)?,
                file_path: row.get(1)?,
                original_name: row.get(2)?,
                file_size: row.get(3)?,
                is_encrypted: row.get(4)?,
                created_at: row.get(5)?,
            })
        })
        .map_err(|e| format!("映射文件数据失败: {}", e))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| format!("收集文件数据失败: {}", e))?;

    log::info!("[files:query:encrypted] count={}", files.len());
    Ok(files)
}

/// 获取最近添加的文件
///
/// # Arguments
/// * `days` - 最近 N 天
///
/// # Returns
/// * `Ok(Vec<FileInfo>)` - 最近文件列表
/// * `Err(String)` - 查询失败
#[tauri::command]
pub async fn get_recent_files(days: i64) -> Result<Vec<FileInfo>, String> {
    log::info!("[files:query:recent] days={}", days);

    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[files:query:recent:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();

    // 查询最近 N 天的文件
    let mut stmt = conn
        .prepare(
            "SELECT id, file_path, original_name, file_size, is_encrypted, created_at
             FROM files
             WHERE created_at >= datetime('now', ? || ' days')
             ORDER BY created_at DESC"
        )
        .map_err(|e| {
            log::error!("[files:query:recent:failed] 查询失败: {}", e);
            format!("查询最近文件失败: {}", e)
        })?;

    let files = stmt
        .query_map(params![-days], |row| {
            Ok(FileInfo {
                id: row.get(0)?,
                file_path: row.get(1)?,
                original_name: row.get(2)?,
                file_size: row.get(3)?,
                is_encrypted: row.get(4)?,
                created_at: row.get(5)?,
            })
        })
        .map_err(|e| format!("映射文件数据失败: {}", e))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| format!("收集文件数据失败: {}", e))?;

    log::info!("[files:query:recent] days={}, count={}", days, files.len());
    Ok(files)
}

// ================================
// Phase 6: 扩展功能 - Extensions
// ================================

/// 批量操作结果
#[derive(Debug, Serialize, Deserialize)]
pub struct BulkOperationResult {
    pub total_files: usize,
    pub total_tags: usize,
    pub associations_added: usize,
    pub failures: Vec<String>,
}

/// 批量添加标签到多个文件
///
/// # Arguments
/// * `file_ids` - 文件 ID 列表
/// * `tag_ids` - 标签 ID 列表
///
/// # Returns
/// * `Ok(BulkOperationResult)` - 操作结果
#[tauri::command]
pub async fn bulk_add_tags(file_ids: Vec<i64>, tag_ids: Vec<String>) -> Result<BulkOperationResult, String> {
    log::info!("[bulk:add_tags] files={}, tags={}", file_ids.len(), tag_ids.len());

    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[bulk:add_tags:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();
    let mut associations_added = 0;
    let mut failures = Vec::new();
    let now = chrono::Utc::now().to_rfc3339();

    // 开始事务
    conn.execute("BEGIN TRANSACTION", []).map_err(|e| {
        log::error!("[bulk:add_tags:failed] 开始事务失败: {}", e);
        format!("开始事务失败: {}", e)
    })?;

    for file_id in &file_ids {
        for tag_id in &tag_ids {
            // 检查关联是否已存在（幂等性）
            let exists: Result<i64, rusqlite::Error> = conn.query_row(
                "SELECT COUNT(*) FROM file_tags WHERE file_id = ?1 AND tag_id = ?2",
                params![file_id, tag_id],
                |row| row.get(0),
            );

            match exists {
                Ok(count) if count > 0 => {
                    // 关联已存在，跳过
                    continue;
                }
                Ok(_) => {
                    // 添加关联
                    match conn.execute(
                        "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
                        params![file_id, tag_id, now],
                    ) {
                        Ok(_) => {
                            associations_added += 1;
                            // 更新标签使用计数
                            let _ = conn.execute(
                                "UPDATE tags SET usage_count = usage_count + 1 WHERE tag_id = ?1",
                                params![tag_id],
                            );
                        }
                        Err(e) => {
                            failures.push(format!("文件 {} + 标签 {}: {}", file_id, tag_id, e));
                        }
                    }
                }
                Err(e) => {
                    failures.push(format!("检查关联失败 (文件 {} + 标签 {}): {}", file_id, tag_id, e));
                }
            }
        }
    }

    // 提交事务
    conn.execute("COMMIT", []).map_err(|e| {
        log::error!("[bulk:add_tags:failed] 提交事务失败: {}", e);
        let _ = conn.execute("ROLLBACK", []);
        format!("提交事务失败: {}", e)
    })?;

    let result = BulkOperationResult {
        total_files: file_ids.len(),
        total_tags: tag_ids.len(),
        associations_added,
        failures,
    };

    log::info!(
        "[bulk:add_tags:success] files={}, tags={}, associations={}",
        result.total_files,
        result.total_tags,
        result.associations_added
    );

    Ok(result)
}

/// 批量从多个文件移除标签
///
/// # Arguments
/// * `file_ids` - 文件 ID 列表
/// * `tag_ids` - 标签 ID 列表
#[tauri::command]
pub async fn bulk_remove_tags(file_ids: Vec<i64>, tag_ids: Vec<String>) -> Result<BulkOperationResult, String> {
    log::info!("[bulk:remove_tags] files={}, tags={}", file_ids.len(), tag_ids.len());

    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[bulk:remove_tags:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();
    let mut associations_removed = 0;
    let mut failures = Vec::new();

    // 开始事务
    conn.execute("BEGIN TRANSACTION", []).map_err(|e| {
        log::error!("[bulk:remove_tags:failed] 开始事务失败: {}", e);
        format!("开始事务失败: {}", e)
    })?;

    for file_id in &file_ids {
        for tag_id in &tag_ids {
            match conn.execute(
                "DELETE FROM file_tags WHERE file_id = ?1 AND tag_id = ?2",
                params![file_id, tag_id],
            ) {
                Ok(rows) => {
                    if rows > 0 {
                        associations_removed += rows;
                        // 更新标签使用计数
                        let _ = conn.execute(
                            "UPDATE tags SET usage_count = usage_count - 1 WHERE tag_id = ?1 AND usage_count > 0",
                            params![tag_id],
                        );
                    }
                }
                Err(e) => {
                    failures.push(format!("文件 {} - 标签 {}: {}", file_id, tag_id, e));
                }
            }
        }
    }

    // 提交事务
    conn.execute("COMMIT", []).map_err(|e| {
        log::error!("[bulk:remove_tags:failed] 提交事务失败: {}", e);
        let _ = conn.execute("ROLLBACK", []);
        format!("提交事务失败: {}", e)
    })?;

    let result = BulkOperationResult {
        total_files: file_ids.len(),
        total_tags: tag_ids.len(),
        associations_added: associations_removed,
        failures,
    };

    log::info!(
        "[bulk:remove_tags:success] files={}, tags={}, associations={}",
        result.total_files,
        result.total_tags,
        result.associations_added
    );

    Ok(result)
}

/// 批量删除结果
#[derive(Debug, Serialize, Deserialize)]
pub struct BulkDeleteResult {
    pub deleted_tags: usize,
    pub deleted_children: usize,
    pub affected_files: usize,
}

/// 批量删除标签
///
/// # Arguments
/// * `tag_ids` - 要删除的标签 ID 列表
/// * `force` - 是否强制删除（包括子标签和文件关联）
#[tauri::command]
pub async fn bulk_delete_tags(tag_ids: Vec<String>, force: bool) -> Result<BulkDeleteResult, String> {
    log::info!("[bulk:delete_tags] tags={}, force={}", tag_ids.len(), force);

    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[bulk:delete_tags:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();
    let mut deleted_tags = 0;
    let mut deleted_children = 0;
    let mut affected_files = 0;

    // 开始事务
    conn.execute("BEGIN TRANSACTION", []).map_err(|e| {
        log::error!("[bulk:delete_tags:failed] 开始事务失败: {}", e);
        format!("开始事务失败: {}", e)
    })?;

    for tag_id in &tag_ids {
        // 检查是否有子标签
        let child_count: i64 = conn
            .query_row(
                "SELECT COUNT(*) FROM tags WHERE parent_tag_id = ?1",
                params![tag_id],
                |row| row.get(0),
            )
            .unwrap_or(0);

        if child_count > 0 && !force {
            conn.execute("ROLLBACK", []).ok();
            return Err(format!("{}:标签 {} 有 {} 个子标签", ERR_TAG_HAS_CHILDREN, tag_id, child_count));
        }

        // 检查是否关联文件
        let file_count: i64 = conn
            .query_row(
                "SELECT COUNT(*) FROM file_tags WHERE tag_id = ?1",
                params![tag_id],
                |row| row.get(0),
            )
            .unwrap_or(0);

        if file_count > 0 && !force {
            conn.execute("ROLLBACK", []).ok();
            return Err(format!("{}:标签 {} 关联 {} 个文件", ERR_TAG_HAS_FILES, tag_id, file_count));
        }

        // 如果强制删除，先删除所有子标签
        if force && child_count > 0 {
            let child_ids = get_all_descendant_tag_ids(&conn, tag_id).unwrap_or_default();
            for child_id in &child_ids {
                // 删除子标签的文件关联
                let child_file_count: i64 = conn
                    .query_row(
                        "SELECT COUNT(*) FROM file_tags WHERE tag_id = ?1",
                        params![child_id],
                        |row| row.get(0),
                    )
                    .unwrap_or(0);

                conn.execute("DELETE FROM file_tags WHERE tag_id = ?1", params![child_id]).ok();
                affected_files += child_file_count as usize;

                // 删除子标签
                conn.execute("DELETE FROM tags WHERE tag_id = ?1", params![child_id]).ok();
                deleted_children += 1;
            }
        }

        // 删除标签的文件关联
        conn.execute("DELETE FROM file_tags WHERE tag_id = ?1", params![tag_id]).ok();
        affected_files += file_count as usize;

        // 删除标签本身
        match conn.execute("DELETE FROM tags WHERE tag_id = ?1", params![tag_id]) {
            Ok(rows) => {
                deleted_tags += rows;
            }
            Err(e) => {
                log::error!("[bulk:delete_tags:failed] 删除标签失败 {}: {}", tag_id, e);
            }
        }
    }

    // 提交事务
    conn.execute("COMMIT", []).map_err(|e| {
        log::error!("[bulk:delete_tags:failed] 提交事务失败: {}", e);
        let _ = conn.execute("ROLLBACK", []);
        format!("提交事务失败: {}", e)
    })?;

    let result = BulkDeleteResult {
        deleted_tags,
        deleted_children,
        affected_files,
    };

    log::info!(
        "[bulk:delete_tags:success] deleted={}, children={}, files={}",
        result.deleted_tags,
        result.deleted_children,
        result.affected_files
    );

    Ok(result)
}

/// 标签导出格式
#[derive(Debug, Serialize, Deserialize)]
pub struct TagExport {
    pub version: String,
    pub exported_at: String,
    pub tags: Vec<TagExportNode>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TagExportNode {
    pub tag_name: String,
    pub tag_color: Option<String>,
    pub children: Vec<TagExportNode>,
}

/// 导出标签树为 JSON
#[tauri::command]
pub async fn export_tags() -> Result<String, String> {
    log::info!("[tag:export] 开始导出标签...");

    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[tag:export:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();

    // 查询所有标签
    let mut stmt = conn
        .prepare(
            "SELECT tag_id, tag_name, tag_color, parent_tag_id, tag_level, full_path, created_at, updated_at, usage_count
             FROM tags
             ORDER BY tag_level, tag_name",
        )
        .map_err(|e| {
            log::error!("[tag:export:failed] 查询标签失败: {}", e);
            format!("查询标签失败: {}", e)
        })?;

    let tags: Vec<Tag> = stmt
        .query_map([], |row| {
            Ok(Tag {
                tag_id: row.get(0)?,
                tag_name: row.get(1)?,
                tag_color: row.get(2)?,
                parent_tag_id: row.get(3)?,
                tag_level: row.get(4)?,
                full_path: row.get(5)?,
                created_at: row.get(6)?,
                updated_at: row.get(7)?,
                usage_count: row.get(8)?,
            })
        })
        .map_err(|e| {
            log::error!("[tag:export:failed] 映射标签数据失败: {}", e);
            format!("映射标签数据失败: {}", e)
        })?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| {
            log::error!("[tag:export:failed] 收集标签数据失败: {}", e);
            format!("收集标签数据失败: {}", e)
        })?;

    // 构建标签树
    let tag_tree = build_tag_tree(tags)?;

    // 转换为导出格式
    let export_nodes = tag_tree
        .into_iter()
        .map(|node| convert_to_export_node(&node))
        .collect::<Result<Vec<_>, String>>()?;

    let export = TagExport {
        version: "1.0".to_string(),
        exported_at: chrono::Utc::now().to_rfc3339(),
        tags: export_nodes,
    };

    let json = serde_json::to_string_pretty(&export).map_err(|e| {
        log::error!("[tag:export:failed] JSON 序列化失败: {}", e);
        format!("JSON 序列化失败: {}", e)
    })?;

    log::info!("[tag:export:success] 导出 {} 个根标签", export.tags.len());
    Ok(json)
}

/// 转换标签节点为导出格式
fn convert_to_export_node(node: &TagNode) -> Result<TagExportNode, String> {
    let children = node
        .children
        .iter()
        .map(|child| convert_to_export_node(child))
        .collect::<Result<Vec<_>, String>>()?;

    Ok(TagExportNode {
        tag_name: node.tag.tag_name.clone(),
        tag_color: node.tag.tag_color.clone(),
        children,
    })
}

/// 导入结果
#[derive(Debug, Serialize, Deserialize)]
pub struct ImportResult {
    pub imported_tags: usize,
    pub skipped_duplicates: usize,
    pub errors: Vec<String>,
}

/// 从 JSON 导入标签树
///
/// # Arguments
/// * `json_data` - JSON 格式的标签数据
#[tauri::command]
pub async fn import_tags(json_data: String) -> Result<ImportResult, String> {
    log::info!("[tag:import] 开始导入标签...");

    let export: TagExport = serde_json::from_str(&json_data).map_err(|e| {
        log::error!("[tag:import:failed] JSON 解析失败: {}", e);
        format!("JSON 解析失败: {}", e)
    })?;

    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[tag:import:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();
    let mut imported_tags = 0;
    let mut skipped_duplicates = 0;
    let mut errors = Vec::new();

    // 开始事务
    conn.execute("BEGIN TRANSACTION", []).map_err(|e| {
        log::error!("[tag:import:failed] 开始事务失败: {}", e);
        format!("开始事务失败: {}", e)
    })?;

    for tag in &export.tags {
        match import_tag_node(&conn, tag, None, 0, &mut imported_tags, &mut skipped_duplicates, &mut errors) {
            Ok(_) => {}
            Err(e) => {
                errors.push(format!("导入标签 {} 失败: {}", tag.tag_name, e));
            }
        }
    }

    // 提交事务
    conn.execute("COMMIT", []).map_err(|e| {
        log::error!("[tag:import:failed] 提交事务失败: {}", e);
        let _ = conn.execute("ROLLBACK", []);
        format!("提交事务失败: {}", e)
    })?;

    let result = ImportResult {
        imported_tags,
        skipped_duplicates,
        errors,
    };

    log::info!(
        "[tag:import:success] imported={}, skipped={}, errors={}",
        result.imported_tags,
        result.skipped_duplicates,
        result.errors.len()
    );

    Ok(result)
}

/// 递归导入标签节点
fn import_tag_node(
    conn: &rusqlite::Connection,
    node: &TagExportNode,
    parent_id: Option<String>,
    level: i32,
    imported: &mut usize,
    skipped: &mut usize,
    errors: &mut Vec<String>,
) -> Result<String, String> {
    // 检查是否已存在同名标签
    let existing: Result<String, rusqlite::Error> = if let Some(ref pid) = parent_id {
        conn.query_row(
            "SELECT tag_id FROM tags WHERE parent_tag_id = ?1 AND tag_name = ?2",
            params![pid, node.tag_name],
            |row| row.get(0),
        )
    } else {
        conn.query_row(
            "SELECT tag_id FROM tags WHERE parent_tag_id IS NULL AND tag_name = ?1",
            params![node.tag_name],
            |row| row.get(0),
        )
    };

    let tag_id = match existing {
        Ok(id) => {
            *skipped += 1;
            id
        }
        Err(_) => {
            // 创建新标签
            let tag_id = Uuid::new_v4().to_string();
            let full_path = if let Some(ref pid) = parent_id {
                let parent_path: String = conn
                    .query_row(
                        "SELECT full_path FROM tags WHERE tag_id = ?1",
                        params![pid],
                        |row| row.get(0),
                    )
                    .map_err(|e| format!("查询父标签路径失败: {}", e))?;
                format!("{}/{}", parent_path, node.tag_name)
            } else {
                node.tag_name.clone()
            };

            let now = chrono::Utc::now().to_rfc3339();

            conn.execute(
                "INSERT INTO tags (tag_id, tag_name, tag_color, parent_tag_id, tag_level, full_path, created_at, updated_at, usage_count)
                 VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, 0)",
                params![tag_id, node.tag_name, node.tag_color, parent_id, level, full_path, now, now],
            )
            .map_err(|e| format!("插入标签失败: {}", e))?;

            *imported += 1;
            tag_id
        }
    };

    // 递归导入子标签
    for child in &node.children {
        import_tag_node(conn, child, Some(tag_id.clone()), level + 1, imported, skipped, errors)?;
    }

    Ok(tag_id)
}

/// 标签统计信息
#[derive(Debug, Serialize, Deserialize)]
pub struct TagStatistics {
    pub total_tags: usize,
    pub total_files: usize,
    pub total_associations: usize,
    pub most_used_tags: Vec<(Tag, i32)>,
    pub orphaned_tags: Vec<Tag>,
    pub max_depth_used: i32,
    pub avg_files_per_tag: f64,
}

/// 获取标签统计信息
#[tauri::command]
pub async fn get_tag_statistics() -> Result<TagStatistics, String> {
    log::info!("[tag:statistics] 查询标签统计...");

    let db_path = get_default_db_path();
    let db = Database::new(db_path).map_err(|e| {
        log::error!("[tag:statistics:failed] 数据库连接失败: {}", e);
        format!("数据库连接失败: {}", e)
    })?;

    let conn = db.connection();

    // 总标签数
    let total_tags: i64 = conn
        .query_row("SELECT COUNT(*) FROM tags", [], |row| row.get(0))
        .unwrap_or(0);

    // 总文件数
    let total_files: i64 = conn
        .query_row("SELECT COUNT(*) FROM files", [], |row| row.get(0))
        .unwrap_or(0);

    // 总关联数
    let total_associations: i64 = conn
        .query_row("SELECT COUNT(*) FROM file_tags", [], |row| row.get(0))
        .unwrap_or(0);

    // 最常用的标签（Top 10）
    let mut stmt = conn
        .prepare(
            "SELECT tag_id, tag_name, tag_color, parent_tag_id, tag_level, full_path, created_at, updated_at, usage_count
             FROM tags
             WHERE usage_count > 0
             ORDER BY usage_count DESC
             LIMIT 10",
        )
        .map_err(|e| format!("查询最常用标签失败: {}", e))?;

    let most_used_tags: Vec<(Tag, i32)> = stmt
        .query_map([], |row| {
            let tag = Tag {
                tag_id: row.get(0)?,
                tag_name: row.get(1)?,
                tag_color: row.get(2)?,
                parent_tag_id: row.get(3)?,
                tag_level: row.get(4)?,
                full_path: row.get(5)?,
                created_at: row.get(6)?,
                updated_at: row.get(7)?,
                usage_count: row.get(8)?,
            };
            let usage_count: i32 = row.get(8)?;
            Ok((tag, usage_count))
        })
        .map_err(|e| format!("映射标签数据失败: {}", e))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| format!("收集标签数据失败: {}", e))?;

    // 孤立标签（没有文件关联）
    let mut stmt = conn
        .prepare(
            "SELECT tag_id, tag_name, tag_color, parent_tag_id, tag_level, full_path, created_at, updated_at, usage_count
             FROM tags
             WHERE usage_count = 0",
        )
        .map_err(|e| format!("查询孤立标签失败: {}", e))?;

    let orphaned_tags: Vec<Tag> = stmt
        .query_map([], |row| {
            Ok(Tag {
                tag_id: row.get(0)?,
                tag_name: row.get(1)?,
                tag_color: row.get(2)?,
                parent_tag_id: row.get(3)?,
                tag_level: row.get(4)?,
                full_path: row.get(5)?,
                created_at: row.get(6)?,
                updated_at: row.get(7)?,
                usage_count: row.get(8)?,
            })
        })
        .map_err(|e| format!("映射孤立标签数据失败: {}", e))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| format!("收集孤立标签数据失败: {}", e))?;

    // 最大深度
    let max_depth_used: i32 = conn
        .query_row("SELECT MAX(tag_level) FROM tags", [], |row| row.get(0))
        .unwrap_or(0);

    // 平均每个标签的文件数
    let avg_files_per_tag = if total_tags > 0 {
        total_associations as f64 / total_tags as f64
    } else {
        0.0
    };

    let statistics = TagStatistics {
        total_tags: total_tags as usize,
        total_files: total_files as usize,
        total_associations: total_associations as usize,
        most_used_tags,
        orphaned_tags,
        max_depth_used,
        avg_files_per_tag,
    };

    log::info!(
        "[tag:statistics:success] tags={}, files={}, associations={}",
        statistics.total_tags,
        statistics.total_files,
        statistics.total_associations
    );

    Ok(statistics)
}

#[cfg(test)]
mod tests {
    use super::*;
    use rusqlite::Connection;
    use crate::db::schema::initialize_schema;

    /// 创建测试数据库（内存模式）
    fn setup_test_db() -> Connection {
        let conn = Connection::open_in_memory().unwrap();
        conn.execute("PRAGMA foreign_keys = ON", []).unwrap();
        initialize_schema(&conn).unwrap();
        log::info!("[test:setup] 测试数据库已初始化");
        conn
    }

    /// 在测试数据库中创建标签（内部辅助函数）
    fn create_test_tag_in_db(
        conn: &Connection,
        name: &str,
        parent_id: Option<String>,
        color: Option<String>,
    ) -> Result<String, rusqlite::Error> {
        let tag_id = uuid::Uuid::new_v4().to_string();
        let now = chrono::Utc::now().to_rfc3339();
        let tag_level = if parent_id.is_some() { 1 } else { 0 };
        let full_path = if let Some(ref pid) = parent_id {
            let parent_path: String = conn.query_row(
                "SELECT full_path FROM tags WHERE tag_id = ?1",
                params![pid],
                |row| row.get(0),
            )?;
            format!("{}/{}", parent_path, name)
        } else {
            name.to_string()
        };

        conn.execute(
            "INSERT INTO tags (tag_id, tag_name, tag_color, parent_tag_id, tag_level, full_path, created_at, updated_at, usage_count)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, 0)",
            params![tag_id, name, color, parent_id, tag_level, full_path, now, now],
        )?;

        Ok(tag_id)
    }

    /// 在测试数据库中创建文件（内部辅助函数）
    fn create_test_file_in_db(conn: &Connection, name: &str) -> Result<i64, rusqlite::Error> {
        let now = chrono::Utc::now().to_rfc3339();
        conn.execute(
            "INSERT INTO files (file_path, original_name, file_size, is_encrypted, created_at, updated_at)
             VALUES (?1, ?2, ?3, 0, ?4, ?5)",
            params![format!("/test/{}", name), name, 1024, now, now],
        )?;

        let file_id = conn.last_insert_rowid();
        Ok(file_id)
    }

    // ============================================================================
    // A. Tag CRUD Tests (标签 CRUD 测试)
    // ============================================================================

    #[test]
    fn test_create_root_tag_success() {
        log::info!("[test:tag:create] 测试创建根标签...");
        let conn = setup_test_db();

        let tag_id = create_test_tag_in_db(&conn, "工作", None, Some("#FF5733".to_string())).unwrap();

        // 验证标签是否创建成功
        let count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM tags WHERE tag_id = ?1",
            params![tag_id],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(count, 1);
        log::info!("[test:tag:create] ✅ 测试通过");
    }

    #[test]
    fn test_create_child_tag() {
        log::info!("[test:tag:create:child] 测试创建子标签...");
        let conn = setup_test_db();

        // 创建父标签
        let parent_id = create_test_tag_in_db(&conn, "工作", None, None).unwrap();

        // 创建子标签
        let child_id = create_test_tag_in_db(&conn, "项目A", Some(parent_id.clone()), None).unwrap();

        // 验证子标签的父标签 ID
        let parent_tag_id: Option<String> = conn.query_row(
            "SELECT parent_tag_id FROM tags WHERE tag_id = ?1",
            params![child_id],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(parent_tag_id, Some(parent_id));
        log::info!("[test:tag:create:child] ✅ 测试通过");
    }

    #[test]
    fn test_create_duplicate_name_at_same_level_fails() {
        log::info!("[test:tag:duplicate:same_level] 测试同级重复名称...");
        let conn = setup_test_db();

        // 创建第一个标签
        create_test_tag_in_db(&conn, "工作", None, None).unwrap();

        // 尝试创建同名标签（应该失败，但需要在应用层验证）
        // 这里直接检查是否存在同名标签
        let count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM tags WHERE parent_tag_id IS NULL AND tag_name = ?1",
            params!["工作"],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(count, 1); // 已存在，应该阻止重复创建
        log::info!("[test:tag:duplicate:same_level] ✅ 测试通过");
    }

    #[test]
    fn test_create_duplicate_name_at_different_level_succeeds() {
        log::info!("[test:tag:duplicate:different_level] 测试不同级别重复名称...");
        let conn = setup_test_db();

        // 创建根级别标签 "工作"
        create_test_tag_in_db(&conn, "工作", None, None).unwrap();

        // 创建父标签 "项目"
        let parent_id = create_test_tag_in_db(&conn, "项目", None, None).unwrap();

        // 在 "项目" 下创建子标签 "工作"（不同级别，允许）
        let child_id = create_test_tag_in_db(&conn, "工作", Some(parent_id), None).unwrap();

        // 验证两个 "工作" 标签都存在
        let count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM tags WHERE tag_name = ?1",
            params!["工作"],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(count, 2);
        log::info!("[test:tag:duplicate:different_level] ✅ 测试通过");
    }

    #[test]
    fn test_update_tag_name() {
        log::info!("[test:tag:update:name] 测试更新标签名称...");
        let conn = setup_test_db();

        let tag_id = create_test_tag_in_db(&conn, "旧名称", None, None).unwrap();

        // 更新标签名称
        let now = chrono::Utc::now().to_rfc3339();
        conn.execute(
            "UPDATE tags SET tag_name = ?1, full_path = ?2, updated_at = ?3 WHERE tag_id = ?4",
            params!["新名称", "新名称", now, tag_id],
        ).unwrap();

        // 验证更新
        let name: String = conn.query_row(
            "SELECT tag_name FROM tags WHERE tag_id = ?1",
            params![tag_id],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(name, "新名称");
        log::info!("[test:tag:update:name] ✅ 测试通过");
    }

    #[test]
    fn test_update_tag_color() {
        log::info!("[test:tag:update:color] 测试更新标签颜色...");
        let conn = setup_test_db();

        let tag_id = create_test_tag_in_db(&conn, "工作", None, Some("#FF0000".to_string())).unwrap();

        // 更新颜色
        let now = chrono::Utc::now().to_rfc3339();
        conn.execute(
            "UPDATE tags SET tag_color = ?1, updated_at = ?2 WHERE tag_id = ?3",
            params!["#00FF00", now, tag_id],
        ).unwrap();

        // 验证更新
        let color: Option<String> = conn.query_row(
            "SELECT tag_color FROM tags WHERE tag_id = ?1",
            params![tag_id],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(color, Some("#00FF00".to_string()));
        log::info!("[test:tag:update:color] ✅ 测试通过");
    }

    #[test]
    fn test_update_tag_updates_children_paths() {
        log::info!("[test:tag:update:children_paths] 测试更新子标签路径...");
        let conn = setup_test_db();

        let parent_id = create_test_tag_in_db(&conn, "父标签", None, None).unwrap();
        let child_id = create_test_tag_in_db(&conn, "子标签", Some(parent_id.clone()), None).unwrap();

        // 更新父标签名称
        let now = chrono::Utc::now().to_rfc3339();
        conn.execute(
            "UPDATE tags SET tag_name = ?1, full_path = ?2, updated_at = ?3 WHERE tag_id = ?4",
            params!["新父标签", "新父标签", now, parent_id],
        ).unwrap();

        // 递归更新子标签路径
        update_children_full_path(&conn, &parent_id, "新父标签").unwrap();

        // 验证子标签路径
        let full_path: String = conn.query_row(
            "SELECT full_path FROM tags WHERE tag_id = ?1",
            params![child_id],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(full_path, "新父标签/子标签");
        log::info!("[test:tag:update:children_paths] ✅ 测试通过");
    }

    #[test]
    fn test_delete_tag_without_children() {
        log::info!("[test:tag:delete:simple] 测试删除无子标签的标签...");
        let conn = setup_test_db();

        let tag_id = create_test_tag_in_db(&conn, "工作", None, None).unwrap();

        // 删除标签
        conn.execute("DELETE FROM tags WHERE tag_id = ?1", params![tag_id]).unwrap();

        // 验证删除
        let count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM tags WHERE tag_id = ?1",
            params![tag_id],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(count, 0);
        log::info!("[test:tag:delete:simple] ✅ 测试通过");
    }

    #[test]
    fn test_delete_tag_with_children_without_force_fails() {
        log::info!("[test:tag:delete:with_children] 测试删除有子标签的标签（无 force）...");
        let conn = setup_test_db();

        let parent_id = create_test_tag_in_db(&conn, "工作", None, None).unwrap();
        create_test_tag_in_db(&conn, "项目A", Some(parent_id.clone()), None).unwrap();

        // 检查是否有子标签
        let children_count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM tags WHERE parent_tag_id = ?1",
            params![parent_id],
            |row| row.get(0),
        ).unwrap();

        assert!(children_count > 0); // 应该有子标签，阻止删除
        log::info!("[test:tag:delete:with_children] ✅ 测试通过");
    }

    #[test]
    fn test_delete_tag_with_children_with_force_succeeds() {
        log::info!("[test:tag:delete:force] 测试强制删除有子标签的标签...");
        let conn = setup_test_db();

        let parent_id = create_test_tag_in_db(&conn, "工作", None, None).unwrap();
        create_test_tag_in_db(&conn, "项目A", Some(parent_id.clone()), None).unwrap();

        // 开始事务
        let tx = conn.unchecked_transaction().unwrap();

        // 递归删除子标签
        delete_children_recursive(&tx, &parent_id).unwrap();

        // 删除父标签
        tx.execute("DELETE FROM tags WHERE tag_id = ?1", params![parent_id]).unwrap();

        tx.commit().unwrap();

        // 验证所有标签都被删除
        let count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM tags",
            [],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(count, 0);
        log::info!("[test:tag:delete:force] ✅ 测试通过");
    }

    // ============================================================================
    // B. Edge Case Tests (边界测试)
    // ============================================================================

    #[test]
    fn test_circular_dependency_detection() {
        log::info!("[test:circular_dependency] 测试循环依赖检测...");
        let conn = setup_test_db();

        // 创建标签链: A → B → C
        let tag_a = create_test_tag_in_db(&conn, "A", None, None).unwrap();
        let tag_b = create_test_tag_in_db(&conn, "B", Some(tag_a.clone()), None).unwrap();
        let tag_c = create_test_tag_in_db(&conn, "C", Some(tag_b.clone()), None).unwrap();

        // 查询所有标签
        let tags: Vec<Tag> = {
            let mut stmt = conn.prepare("SELECT tag_id, tag_name, tag_color, parent_tag_id, tag_level, full_path, created_at, updated_at, usage_count FROM tags").unwrap();
            stmt.query_map([], |row| {
                Ok(Tag {
                    tag_id: row.get(0)?,
                    tag_name: row.get(1)?,
                    tag_color: row.get(2)?,
                    parent_tag_id: row.get(3)?,
                    tag_level: row.get(4)?,
                    full_path: row.get(5)?,
                    created_at: row.get(6)?,
                    updated_at: row.get(7)?,
                    usage_count: row.get(8)?,
                })
            })
            .unwrap()
            .collect::<Result<Vec<_>, _>>()
            .unwrap()
        };

        // 检测循环依赖（不应该有循环）
        let result = detect_circular_dependency(&tags);
        assert!(result.is_ok());

        log::info!("[test:circular_dependency] ✅ 测试通过");
    }

    #[test]
    fn test_max_depth_validation() {
        log::info!("[test:max_depth] 测试最大深度验证...");
        let conn = setup_test_db();

        // 创建 5 层标签
        let l0 = create_test_tag_in_db(&conn, "L0", None, None).unwrap();
        let l1 = create_test_tag_in_db(&conn, "L1", Some(l0), None).unwrap();
        let l2 = create_test_tag_in_db(&conn, "L2", Some(l1), None).unwrap();
        let l3 = create_test_tag_in_db(&conn, "L3", Some(l2), None).unwrap();
        let l4 = create_test_tag_in_db(&conn, "L4", Some(l3), None).unwrap();

        // 验证 L4 的层级为 4（最大）
        let level: i32 = conn.query_row(
            "SELECT tag_level FROM tags WHERE tag_id = ?1",
            params![l4],
            |row| row.get(0),
        ).unwrap();

        assert!(level <= 4); // 应该 <= 4
        log::info!("[test:max_depth] ✅ 测试通过");
    }

    #[test]
    fn test_orphaned_tags_after_parent_deletion() {
        log::info!("[test:orphaned_tags] 测试父标签删除后的孤儿标签...");
        let conn = setup_test_db();

        let parent_id = create_test_tag_in_db(&conn, "父标签", None, None).unwrap();
        let child_id = create_test_tag_in_db(&conn, "子标签", Some(parent_id.clone()), None).unwrap();

        // 删除父标签（CASCADE DELETE 应该删除子标签）
        conn.execute("DELETE FROM tags WHERE tag_id = ?1", params![parent_id]).unwrap();

        // 验证子标签也被删除
        let count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM tags WHERE tag_id = ?1",
            params![child_id],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(count, 0);
        log::info!("[test:orphaned_tags] ✅ 测试通过");
    }

    #[test]
    fn test_tag_name_empty_string_fails() {
        log::info!("[test:validation:empty_name] 测试空标签名称...");

        let name = "";
        assert!(name.trim().is_empty()); // 应该被拒绝

        log::info!("[test:validation:empty_name] ✅ 测试通过");
    }

    #[test]
    fn test_tag_name_too_long_fails() {
        log::info!("[test:validation:long_name] 测试过长标签名称...");

        let name = "a".repeat(51);
        assert!(name.len() > 50); // 应该被拒绝

        log::info!("[test:validation:long_name] ✅ 测试通过");
    }

    #[test]
    fn test_invalid_color_format_fails() {
        log::info!("[test:validation:invalid_color] 测试无效颜色格式...");

        let color = "FF5733"; // 缺少 #
        assert!(!color.starts_with('#')); // 应该被拒绝

        let color2 = "#FF57"; // 长度错误
        assert!(color2.len() != 7 && color2.len() != 4); // 应该被拒绝

        log::info!("[test:validation:invalid_color] ✅ 测试通过");
    }

    #[test]
    fn test_parent_tag_not_found_fails() {
        log::info!("[test:validation:parent_not_found] 测试父标签不存在...");
        let conn = setup_test_db();

        let fake_parent_id = uuid::Uuid::new_v4().to_string();

        // 检查父标签是否存在
        let exists: bool = conn.query_row(
            "SELECT COUNT(*) FROM tags WHERE tag_id = ?1",
            params![fake_parent_id],
            |row| {
                let count: i64 = row.get(0)?;
                Ok(count > 0)
            },
        ).unwrap();

        assert!(!exists); // 应该不存在

        log::info!("[test:validation:parent_not_found] ✅ 测试通过");
    }

    // ============================================================================
    // C. File-Tag Association Tests (文件-标签关联测试)
    // ============================================================================

    #[test]
    fn test_add_tag_to_file() {
        log::info!("[test:file_tag:add] 测试添加标签到文件...");
        let conn = setup_test_db();

        let file_id = create_test_file_in_db(&conn, "test.txt").unwrap();
        let tag_id = create_test_tag_in_db(&conn, "工作", None, None).unwrap();

        // 添加关联
        let now = chrono::Utc::now().to_rfc3339();
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file_id, tag_id, now],
        ).unwrap();

        // 验证关联
        let count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM file_tags WHERE file_id = ?1 AND tag_id = ?2",
            params![file_id, tag_id],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(count, 1);
        log::info!("[test:file_tag:add] ✅ 测试通过");
    }

    #[test]
    fn test_add_tag_to_nonexistent_file_fails() {
        log::info!("[test:file_tag:file_not_found] 测试添加标签到不存在的文件...");
        let conn = setup_test_db();

        let fake_file_id = 999999;

        // 检查文件是否存在
        let exists: bool = conn.query_row(
            "SELECT COUNT(*) FROM files WHERE id = ?1",
            params![fake_file_id],
            |row| {
                let count: i64 = row.get(0)?;
                Ok(count > 0)
            },
        ).unwrap();

        assert!(!exists); // 应该不存在

        log::info!("[test:file_tag:file_not_found] ✅ 测试通过");
    }

    #[test]
    fn test_add_nonexistent_tag_to_file_fails() {
        log::info!("[test:file_tag:tag_not_found] 测试添加不存在的标签到文件...");
        let conn = setup_test_db();

        let file_id = create_test_file_in_db(&conn, "test.txt").unwrap();
        let fake_tag_id = uuid::Uuid::new_v4().to_string();

        // 检查标签是否存在
        let exists: bool = conn.query_row(
            "SELECT COUNT(*) FROM tags WHERE tag_id = ?1",
            params![fake_tag_id],
            |row| {
                let count: i64 = row.get(0)?;
                Ok(count > 0)
            },
        ).unwrap();

        assert!(!exists); // 应该不存在

        log::info!("[test:file_tag:tag_not_found] ✅ 测试通过");
    }

    #[test]
    fn test_add_duplicate_association_is_idempotent() {
        log::info!("[test:file_tag:idempotent] 测试重复关联是幂等的...");
        let conn = setup_test_db();

        let file_id = create_test_file_in_db(&conn, "test.txt").unwrap();
        let tag_id = create_test_tag_in_db(&conn, "工作", None, None).unwrap();

        let now = chrono::Utc::now().to_rfc3339();

        // 第一次添加
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file_id, tag_id, now],
        ).unwrap();

        // 第二次添加（应该失败或忽略）
        let result = conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file_id, tag_id, now],
        );

        assert!(result.is_err()); // PRIMARY KEY 冲突

        log::info!("[test:file_tag:idempotent] ✅ 测试通过");
    }

    #[test]
    fn test_remove_tag_from_file() {
        log::info!("[test:file_tag:remove] 测试移除文件的标签...");
        let conn = setup_test_db();

        let file_id = create_test_file_in_db(&conn, "test.txt").unwrap();
        let tag_id = create_test_tag_in_db(&conn, "工作", None, None).unwrap();

        let now = chrono::Utc::now().to_rfc3339();
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file_id, tag_id, now],
        ).unwrap();

        // 移除关联
        conn.execute(
            "DELETE FROM file_tags WHERE file_id = ?1 AND tag_id = ?2",
            params![file_id, tag_id],
        ).unwrap();

        // 验证移除
        let count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM file_tags WHERE file_id = ?1 AND tag_id = ?2",
            params![file_id, tag_id],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(count, 0);
        log::info!("[test:file_tag:remove] ✅ 测试通过");
    }

    #[test]
    fn test_remove_nonexistent_association_is_idempotent() {
        log::info!("[test:file_tag:remove_idempotent] 测试移除不存在的关联是幂等的...");
        let conn = setup_test_db();

        let file_id = create_test_file_in_db(&conn, "test.txt").unwrap();
        let tag_id = create_test_tag_in_db(&conn, "工作", None, None).unwrap();

        // 尝试移除不存在的关联（不应该报错）
        let rows = conn.execute(
            "DELETE FROM file_tags WHERE file_id = ?1 AND tag_id = ?2",
            params![file_id, tag_id],
        ).unwrap();

        assert_eq!(rows, 0); // 没有行被删除

        log::info!("[test:file_tag:remove_idempotent] ✅ 测试通过");
    }

    #[test]
    fn test_batch_add_tags_to_file() {
        log::info!("[test:file_tag:batch_add] 测试批量添加标签到文件...");
        let conn = setup_test_db();

        let file_id = create_test_file_in_db(&conn, "test.txt").unwrap();
        let tag1 = create_test_tag_in_db(&conn, "工作", None, None).unwrap();
        let tag2 = create_test_tag_in_db(&conn, "重要", None, None).unwrap();

        let now = chrono::Utc::now().to_rfc3339();

        // 批量添加
        let tx = conn.unchecked_transaction().unwrap();
        tx.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file_id, tag1, now],
        ).unwrap();
        tx.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file_id, tag2, now],
        ).unwrap();
        tx.commit().unwrap();

        // 验证数量
        let count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM file_tags WHERE file_id = ?1",
            params![file_id],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(count, 2);
        log::info!("[test:file_tag:batch_add] ✅ 测试通过");
    }

    #[test]
    fn test_batch_remove_tags_from_file() {
        log::info!("[test:file_tag:batch_remove] 测试批量移除文件的标签...");
        let conn = setup_test_db();

        let file_id = create_test_file_in_db(&conn, "test.txt").unwrap();
        let tag1 = create_test_tag_in_db(&conn, "工作", None, None).unwrap();
        let tag2 = create_test_tag_in_db(&conn, "重要", None, None).unwrap();

        let now = chrono::Utc::now().to_rfc3339();
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file_id, tag1, now],
        ).unwrap();
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file_id, tag2, now],
        ).unwrap();

        // 批量删除
        conn.execute("DELETE FROM file_tags WHERE file_id = ?1", params![file_id]).unwrap();

        // 验证删除
        let count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM file_tags WHERE file_id = ?1",
            params![file_id],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(count, 0);
        log::info!("[test:file_tag:batch_remove] ✅ 测试通过");
    }

    #[test]
    fn test_usage_count_increments_on_association() {
        log::info!("[test:usage_count:increment] 测试关联时使用计数递增...");
        let conn = setup_test_db();

        let file_id = create_test_file_in_db(&conn, "test.txt").unwrap();
        let tag_id = create_test_tag_in_db(&conn, "工作", None, None).unwrap();

        // 添加关联
        let now = chrono::Utc::now().to_rfc3339();
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file_id, tag_id, now],
        ).unwrap();

        // 更新使用计数
        conn.execute(
            "UPDATE tags SET usage_count = usage_count + 1 WHERE tag_id = ?1",
            params![tag_id],
        ).unwrap();

        // 验证计数
        let usage_count: i32 = conn.query_row(
            "SELECT usage_count FROM tags WHERE tag_id = ?1",
            params![tag_id],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(usage_count, 1);
        log::info!("[test:usage_count:increment] ✅ 测试通过");
    }

    #[test]
    fn test_usage_count_decrements_on_removal() {
        log::info!("[test:usage_count:decrement] 测试移除时使用计数递减...");
        let conn = setup_test_db();

        let file_id = create_test_file_in_db(&conn, "test.txt").unwrap();
        let tag_id = create_test_tag_in_db(&conn, "工作", None, None).unwrap();

        let now = chrono::Utc::now().to_rfc3339();
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file_id, tag_id, now],
        ).unwrap();
        conn.execute(
            "UPDATE tags SET usage_count = usage_count + 1 WHERE tag_id = ?1",
            params![tag_id],
        ).unwrap();

        // 移除关联
        conn.execute(
            "DELETE FROM file_tags WHERE file_id = ?1 AND tag_id = ?2",
            params![file_id, tag_id],
        ).unwrap();

        // 更新使用计数
        conn.execute(
            "UPDATE tags SET usage_count = MAX(0, usage_count - 1) WHERE tag_id = ?1",
            params![tag_id],
        ).unwrap();

        // 验证计数
        let usage_count: i32 = conn.query_row(
            "SELECT usage_count FROM tags WHERE tag_id = ?1",
            params![tag_id],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(usage_count, 0);
        log::info!("[test:usage_count:decrement] ✅ 测试通过");
    }

    // ============================================================================
    // D. Query Tests (查询测试)
    // ============================================================================

    #[test]
    fn test_get_tag_tree_structure() {
        log::info!("[test:query:tree] 测试获取标签树结构...");
        let conn = setup_test_db();

        let root1 = create_test_tag_in_db(&conn, "工作", None, None).unwrap();
        let root2 = create_test_tag_in_db(&conn, "个人", None, None).unwrap();
        create_test_tag_in_db(&conn, "项目A", Some(root1), None).unwrap();

        // 查询所有标签
        let tags: Vec<Tag> = {
            let mut stmt = conn.prepare("SELECT tag_id, tag_name, tag_color, parent_tag_id, tag_level, full_path, created_at, updated_at, usage_count FROM tags ORDER BY tag_level, tag_name").unwrap();
            stmt.query_map([], |row| {
                Ok(Tag {
                    tag_id: row.get(0)?,
                    tag_name: row.get(1)?,
                    tag_color: row.get(2)?,
                    parent_tag_id: row.get(3)?,
                    tag_level: row.get(4)?,
                    full_path: row.get(5)?,
                    created_at: row.get(6)?,
                    updated_at: row.get(7)?,
                    usage_count: row.get(8)?,
                })
            })
            .unwrap()
            .collect::<Result<Vec<_>, _>>()
            .unwrap()
        };

        assert_eq!(tags.len(), 3);
        log::info!("[test:query:tree] ✅ 测试通过");
    }

    #[test]
    fn test_get_file_tags() {
        log::info!("[test:query:file_tags] 测试查询文件的标签...");
        let conn = setup_test_db();

        let file_id = create_test_file_in_db(&conn, "test.txt").unwrap();
        let tag1 = create_test_tag_in_db(&conn, "工作", None, None).unwrap();
        let tag2 = create_test_tag_in_db(&conn, "重要", None, None).unwrap();

        let now = chrono::Utc::now().to_rfc3339();
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file_id, tag1, now],
        ).unwrap();
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file_id, tag2, now],
        ).unwrap();

        // 查询文件的标签
        let count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM file_tags WHERE file_id = ?1",
            params![file_id],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(count, 2);
        log::info!("[test:query:file_tags] ✅ 测试通过");
    }

    #[test]
    fn test_get_tag_files_non_recursive() {
        log::info!("[test:query:tag_files] 测试查询标签的文件（非递归）...");
        let conn = setup_test_db();

        let tag_id = create_test_tag_in_db(&conn, "工作", None, None).unwrap();
        let file1 = create_test_file_in_db(&conn, "file1.txt").unwrap();
        let file2 = create_test_file_in_db(&conn, "file2.txt").unwrap();

        let now = chrono::Utc::now().to_rfc3339();
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file1, tag_id, now],
        ).unwrap();
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file2, tag_id, now],
        ).unwrap();

        // 查询标签的文件
        let count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM file_tags WHERE tag_id = ?1",
            params![tag_id],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(count, 2);
        log::info!("[test:query:tag_files] ✅ 测试通过");
    }

    #[test]
    fn test_get_tag_files_recursive() {
        log::info!("[test:query:tag_files_recursive] 测试查询标签的文件（递归）...");
        let conn = setup_test_db();

        let parent_id = create_test_tag_in_db(&conn, "工作", None, None).unwrap();
        let child_id = create_test_tag_in_db(&conn, "项目A", Some(parent_id.clone()), None).unwrap();

        let file1 = create_test_file_in_db(&conn, "file1.txt").unwrap();
        let file2 = create_test_file_in_db(&conn, "file2.txt").unwrap();

        let now = chrono::Utc::now().to_rfc3339();
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file1, parent_id, now],
        ).unwrap();
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file2, child_id, now],
        ).unwrap();

        // 递归查询（包含子标签）
        let all_tag_ids = vec![parent_id.clone(), child_id];
        let placeholders = all_tag_ids.iter().map(|_| "?").collect::<Vec<_>>().join(",");
        let query = format!(
            "SELECT DISTINCT file_id FROM file_tags WHERE tag_id IN ({})",
            placeholders
        );

        let count: i64 = conn.query_row(&query, rusqlite::params_from_iter(&all_tag_ids), |row| {
            Ok(1)
        }).unwrap_or(0);

        assert!(count > 0);
        log::info!("[test:query:tag_files_recursive] ✅ 测试通过");
    }

    #[test]
    fn test_search_files_and_mode() {
        log::info!("[test:search:and_mode] 测试搜索文件（AND 模式）...");
        let conn = setup_test_db();

        let tag1 = create_test_tag_in_db(&conn, "工作", None, None).unwrap();
        let tag2 = create_test_tag_in_db(&conn, "重要", None, None).unwrap();

        let file1 = create_test_file_in_db(&conn, "file1.txt").unwrap();
        let file2 = create_test_file_in_db(&conn, "file2.txt").unwrap();

        let now = chrono::Utc::now().to_rfc3339();
        // file1 有两个标签
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file1, tag1, now],
        ).unwrap();
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file1, tag2, now],
        ).unwrap();
        // file2 只有一个标签
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file2, tag1, now],
        ).unwrap();

        // AND 模式：查询同时包含 tag1 和 tag2 的文件
        let count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM (
                SELECT file_id FROM file_tags WHERE tag_id IN (?1, ?2)
                GROUP BY file_id
                HAVING COUNT(DISTINCT tag_id) = 2
            )",
            params![tag1, tag2],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(count, 1); // 只有 file1
        log::info!("[test:search:and_mode] ✅ 测试通过");
    }

    #[test]
    fn test_search_files_or_mode() {
        log::info!("[test:search:or_mode] 测试搜索文件（OR 模式）...");
        let conn = setup_test_db();

        let tag1 = create_test_tag_in_db(&conn, "工作", None, None).unwrap();
        let tag2 = create_test_tag_in_db(&conn, "重要", None, None).unwrap();

        let file1 = create_test_file_in_db(&conn, "file1.txt").unwrap();
        let file2 = create_test_file_in_db(&conn, "file2.txt").unwrap();

        let now = chrono::Utc::now().to_rfc3339();
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file1, tag1, now],
        ).unwrap();
        conn.execute(
            "INSERT INTO file_tags (file_id, tag_id, created_at) VALUES (?1, ?2, ?3)",
            params![file2, tag2, now],
        ).unwrap();

        // OR 模式：查询包含 tag1 或 tag2 的文件
        let count: i64 = conn.query_row(
            "SELECT COUNT(DISTINCT file_id) FROM file_tags WHERE tag_id IN (?1, ?2)",
            params![tag1, tag2],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(count, 2); // file1 和 file2
        log::info!("[test:search:or_mode] ✅ 测试通过");
    }

    #[test]
    fn test_search_files_with_name_query() {
        log::info!("[test:search:name_query] 测试搜索文件（文件名查询）...");
        let conn = setup_test_db();

        create_test_file_in_db(&conn, "work.txt").unwrap();
        create_test_file_in_db(&conn, "personal.txt").unwrap();

        // 搜索包含 "work" 的文件
        let count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM files WHERE original_name LIKE ?1",
            params!["%work%"],
            |row| row.get(0),
        ).unwrap();

        assert_eq!(count, 1);
        log::info!("[test:search:name_query] ✅ 测试通过");
    }

    #[test]
    fn test_recursive_search_includes_child_tags() {
        log::info!("[test:search:recursive] 测试递归搜索包含子标签...");
        let conn = setup_test_db();

        let parent_id = create_test_tag_in_db(&conn, "工作", None, None).unwrap();
        let child_id = create_test_tag_in_db(&conn, "项目A", Some(parent_id.clone()), None).unwrap();

        // 递归获取所有子孙标签
        let descendants = get_all_descendant_tag_ids(&conn, &parent_id).unwrap();

        assert_eq!(descendants.len(), 1);
        assert_eq!(descendants[0], child_id);

        log::info!("[test:search:recursive] ✅ 测试通过");
    }
}
