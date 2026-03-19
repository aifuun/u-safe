use serde::{Deserialize, Serialize};

/// Tag 数据结构
/// 对应数据库 tags 表，支持层级标签系统
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Tag {
    /// 标签 ID (UUID v4)
    pub tag_id: String,

    /// 标签名称 (e.g., "工作")
    pub tag_name: String,

    /// 颜色代码 (e.g., "#FF5733")
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tag_color: Option<String>,

    /// 父标签 ID (NULL 表示根标签)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub parent_tag_id: Option<String>,

    /// 层级深度 (0=根, 1=一级子标签...)
    pub tag_level: i32,

    /// 完整路径 (e.g., "工作/项目A/文档")
    pub full_path: String,

    /// 创建时间 (ISO 8601)
    pub created_at: String,

    /// 更新时间 (ISO 8601)
    pub updated_at: String,

    /// 使用次数（优化搜索排序）
    pub usage_count: i32,
}

/// 创建标签请求
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreateTagRequest {
    /// 标签名称（必填，≤50字符）
    pub name: String,

    /// 父标签 ID（可选）
    #[serde(skip_serializing_if = "Option::is_none")]
    pub parent_id: Option<String>,

    /// 颜色代码（可选）
    #[serde(skip_serializing_if = "Option::is_none")]
    pub color: Option<String>,
}

/// 更新标签请求
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateTagRequest {
    /// 标签 ID
    pub id: String,

    /// 新标签名称（可选）
    #[serde(skip_serializing_if = "Option::is_none")]
    pub name: Option<String>,

    /// 新颜色代码（可选）
    #[serde(skip_serializing_if = "Option::is_none")]
    pub color: Option<String>,
}

impl Tag {
    /// 创建新标签实例
    pub fn new(
        tag_id: String,
        tag_name: String,
        tag_color: Option<String>,
        parent_tag_id: Option<String>,
        tag_level: i32,
        full_path: String,
    ) -> Self {
        let now = chrono::Utc::now().to_rfc3339();
        Self {
            tag_id,
            tag_name,
            tag_color,
            parent_tag_id,
            tag_level,
            full_path,
            created_at: now.clone(),
            updated_at: now,
            usage_count: 0,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tag_creation() {
        let tag = Tag::new(
            "test-id".to_string(),
            "工作".to_string(),
            Some("#FF5733".to_string()),
            None,
            0,
            "工作".to_string(),
        );

        assert_eq!(tag.tag_name, "工作");
        assert_eq!(tag.tag_level, 0);
        assert_eq!(tag.usage_count, 0);
        assert!(tag.parent_tag_id.is_none());
    }

    #[test]
    fn test_create_tag_request() {
        let request = CreateTagRequest {
            name: "项目A".to_string(),
            parent_id: Some("parent-id".to_string()),
            color: Some("#00FF00".to_string()),
        };

        assert_eq!(request.name, "项目A");
        assert!(request.parent_id.is_some());
    }
}
