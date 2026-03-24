/**
 * 标签实体
 * 表示系统中的标签及其层级关系
 *
 * 这是纯数据类型，不包含 IO 操作或副作用
 */
export interface Tag {
  /** 标签唯一标识符 */
  id: string;

  /** 标签名称 */
  name: string;

  /** 标签颜色（可选，十六进制颜色代码） */
  color?: string;

  /** 父标签 ID（如果是根标签则为 null） */
  parentId: string | null;

  /** 标签层级深度（0 = 根标签，1 = 一级子标签，依此类推） */
  level: number;

  /** 完整路径（例如 "工作/项目A/文档"） */
  fullPath: string;

  /** 使用次数（用于搜索排序优化） */
  usageCount: number;

  /** 创建时间（ISO 8601 字符串） */
  createdAt: string;

  /** 最后更新时间（ISO 8601 字符串） */
  updatedAt: string;
}

/**
 * 标签创建参数
 * 用于创建新标签实体的最小必需字段
 */
export interface CreateTagParams {
  /** 标签名称 */
  name: string;

  /** 父标签 ID（如果创建根标签则为 null） */
  parentId: string | null;

  /** 标签颜色（可选） */
  color?: string;
}

/**
 * 标签更新参数
 * 用于更新标签的可修改字段
 */
export interface UpdateTagParams {
  /** 标签名称（可选） */
  name?: string;

  /** 标签颜色（可选） */
  color?: string;
}

/**
 * 标签树节点
 * 用于表示层级结构的标签
 */
export interface TagTreeNode extends Tag {
  /** 子标签列表 */
  children: TagTreeNode[];
}
