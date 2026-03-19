/**
 * 标签数据类型定义
 * 对应 Rust 模型 src-tauri/src/models/tag.rs
 */

/**
 * 标签基础结构
 */
export interface Tag {
  tag_id: string;
  tag_name: string;
  tag_color?: string;
  parent_tag_id?: string;
  tag_level: number;
  full_path: string;
  created_at: string;
  updated_at: string;
  usage_count: number;
}

/**
 * 标签树节点（包含子标签）
 */
export interface TagNode {
  // 标签基础信息（展平）
  tag_id: string;
  tag_name: string;
  tag_color?: string;
  parent_tag_id?: string;
  tag_level: number;
  full_path: string;
  created_at: string;
  updated_at: string;
  usage_count: number;

  // 子标签列表
  children: TagNode[];
}

/**
 * 创建标签请求
 */
export interface CreateTagRequest {
  name: string;
  parent_id?: string;
  color?: string;
}

/**
 * 更新标签请求
 */
export interface UpdateTagRequest {
  id: string;
  name?: string;
  color?: string;
}
