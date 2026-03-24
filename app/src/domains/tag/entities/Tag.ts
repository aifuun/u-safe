/**
 * 标签实体
 * 表示系统中的标签及其元数据
 *
 * 这是纯数据类型，不包含 IO 操作或副作用
 */
export interface Tag {
  /** 标签唯一标识符 */
  id: string;

  /** 标签名称 */
  name: string;

  /** 标签颜色（用于 UI 显示） */
  color?: string;

  /** 父标签 ID（用于层级结构） */
  parentId?: string;

  /** 创建时间（ISO 8601 字符串） */
  createdAt: string;

  /** 最后修改时间（ISO 8601 字符串） */
  updatedAt: string;

  /** 关联的文件数量（可选，用于统计） */
  fileCount?: number;
}

/**
 * 标签创建参数
 * 用于创建新标签的最小必需字段
 */
export interface CreateTagParams {
  name: string;
  color?: string;
  parentId?: string;
}

/**
 * 标签树节点
 * 用于表示层级结构的标签树
 */
export interface TagTreeNode extends Tag {
  /** 子标签列表 */
  children: TagTreeNode[];

  /** 层级深度（根节点为 0） */
  level: number;
}
