use crate::db::{Database, get_default_db_path};
use crate::models::{Tag, CreateTagRequest, UpdateTagRequest, TagNode};
use rusqlite::params;
use uuid::Uuid;
use std::collections::{HashMap, HashSet};

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
