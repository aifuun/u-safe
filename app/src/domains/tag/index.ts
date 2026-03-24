/**
 * Tag Domain - Domains Layer (Layer 1)
 *
 * 纯业务逻辑层，不依赖 IO 或框架
 * 使用路径别名: @/domains/tag
 */

// ========== 实体 ==========
export type {
  Tag,
  CreateTagParams,
  UpdateTagParams,
  TagTreeNode,
} from './entities/Tag';

// ========== 验证规则 ==========
export {
  // 常量
  TAG_NAME_LIMITS,
  TAG_LEVEL_LIMITS,
  RESERVED_TAG_NAMES,
  TAG_COLOR_REGEX,

  // 类型
  type TagValidationError,
  type TagValidationResult,

  // 验证函数
  validateTagName,
  validateTagColor,
  validateTagLevel,
  validateTagCreation,
  validateTagUpdate,
  hasCircularReference,
} from './rules/validation';

// ========== 层级规则 ==========
export {
  // 路径操作
  buildFullPath,
  parseFullPath,
  getParentPath,

  // 树操作
  buildTagTree,
  getAllDescendantIds,
  getAncestors,
  getChildren,
  isAncestor,

  // 统计信息
  getSubtreeDepth,
  getChildrenCount,
  getDescendantCount,
} from './rules/hierarchy';
