use crate::db::{Database, get_default_db_path};
use crate::models::{Tag, CreateTagRequest, UpdateTagRequest, TagNode};
use rusqlite::params;
use uuid::Uuid;
use std::collections::HashMap;

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
