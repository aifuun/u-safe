/**
 * Tag 域（Domains Layer）
 *
 * 纯业务逻辑，无 IO 依赖
 * 提供标签实体定义、验证规则等核心功能
 */

// 实体导出
export type { Tag, CreateTagParams, TagTreeNode } from './entities/Tag';

// 验证规则导出
export {
  TAG_NAME_LIMITS,
  TAG_COLOR_PATTERN,
  TAG_HIERARCHY_LIMITS,
  validateTagName,
  validateTagColor,
  validateTagLevel,
  validateChildrenCount,
  validateCreateTagParams,
  isDuplicateTagName,
  hasCircularDependency,
} from './rules/validation';

export type { TagValidationResult } from './rules/validation';
