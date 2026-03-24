/**
 * 标签验证规则
 * 纯函数，无副作用，无 IO 操作
 */

/**
 * 标签名称长度限制
 */
export const TAG_NAME_LIMITS = {
  MIN_LENGTH: 1,
  MAX_LENGTH: 50,
} as const;

/**
 * 标签颜色验证规则
 */
export const TAG_COLOR_PATTERN = /^#[0-9A-Fa-f]{6}$/;

/**
 * 标签层级限制
 */
export const TAG_HIERARCHY_LIMITS = {
  MAX_DEPTH: 5, // 最大层级深度
  MAX_CHILDREN: 100, // 单个标签最多子标签数
} as const;

/**
 * 标签验证结果
 */
export interface TagValidationResult {
  valid: boolean;
  errors: string[];
}

/**
 * 验证标签名称
 *
 * @param name - 标签名称
 * @returns 验证结果
 */
export function validateTagName(name: string): TagValidationResult {
  const errors: string[] = [];

  if (!name || name.trim().length === 0) {
    errors.push('标签名称不能为空');
  } else if (name.length < TAG_NAME_LIMITS.MIN_LENGTH) {
    errors.push(`标签名称至少需要 ${TAG_NAME_LIMITS.MIN_LENGTH} 个字符`);
  } else if (name.length > TAG_NAME_LIMITS.MAX_LENGTH) {
    errors.push(`标签名称不能超过 ${TAG_NAME_LIMITS.MAX_LENGTH} 个字符`);
  }

  // 检查特殊字符（只允许字母、数字、中文、空格、下划线、连字符）
  const invalidChars = /[^\w\s\u4e00-\u9fa5-]/;
  if (invalidChars.test(name)) {
    errors.push('标签名称包含非法字符（仅允许字母、数字、中文、空格、下划线、连字符）');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * 验证标签颜色
 *
 * @param color - 颜色值（可选，HEX 格式，如 #FF5733）
 * @returns 验证结果
 */
export function validateTagColor(color?: string): TagValidationResult {
  const errors: string[] = [];

  // 颜色是可选的
  if (!color) {
    return { valid: true, errors: [] };
  }

  if (!TAG_COLOR_PATTERN.test(color)) {
    errors.push('颜色格式无效（需要 HEX 格式，如 #FF5733）');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * 验证标签层级深度
 *
 * @param level - 当前层级（根节点为 0）
 * @returns 验证结果
 */
export function validateTagLevel(level: number): TagValidationResult {
  const errors: string[] = [];

  if (level < 0) {
    errors.push('标签层级不能为负数');
  } else if (level >= TAG_HIERARCHY_LIMITS.MAX_DEPTH) {
    errors.push(`标签层级不能超过 ${TAG_HIERARCHY_LIMITS.MAX_DEPTH} 层`);
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * 验证子标签数量
 *
 * @param childrenCount - 子标签数量
 * @returns 验证结果
 */
export function validateChildrenCount(childrenCount: number): TagValidationResult {
  const errors: string[] = [];

  if (childrenCount < 0) {
    errors.push('子标签数量不能为负数');
  } else if (childrenCount > TAG_HIERARCHY_LIMITS.MAX_CHILDREN) {
    errors.push(`单个标签的子标签数量不能超过 ${TAG_HIERARCHY_LIMITS.MAX_CHILDREN} 个`);
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * 验证创建标签参数
 *
 * @param params - 创建标签参数
 * @returns 验证结果
 */
export function validateCreateTagParams(params: {
  name: string;
  color?: string;
}): TagValidationResult {
  const allErrors: string[] = [];

  // 验证标签名称
  const nameResult = validateTagName(params.name);
  allErrors.push(...nameResult.errors);

  // 验证标签颜色
  const colorResult = validateTagColor(params.color);
  allErrors.push(...colorResult.errors);

  return {
    valid: allErrors.length === 0,
    errors: allErrors,
  };
}

/**
 * 检查标签名称是否重复
 *
 * @param name - 要检查的标签名称
 * @param existingNames - 已存在的标签名称列表
 * @param excludeId - 排除的标签 ID（编辑时使用）
 * @returns 是否重复
 */
export function isDuplicateTagName(
  name: string,
  existingNames: string[],
  _excludeId?: string
): boolean {
  // Note: _excludeId 保留用于未来实现（需要配合完整的 Tag 对象列表）
  // 当前简化实现仅检查名称是否在列表中存在
  const normalizedName = name.trim().toLowerCase();
  return existingNames.some(
    (existing) => existing.trim().toLowerCase() === normalizedName
  );
}

/**
 * 检测循环依赖
 *
 * @param tagId - 当前标签 ID
 * @param newParentId - 新父标签 ID
 * @param getParentId - 获取父标签 ID 的函数
 * @returns 是否存在循环依赖
 */
export function hasCircularDependency(
  tagId: string,
  newParentId: string | undefined,
  getParentId: (id: string) => string | undefined
): boolean {
  if (!newParentId) {
    return false; // 无父标签，不存在循环
  }

  if (tagId === newParentId) {
    return true; // 自己不能作为自己的父标签
  }

  // 向上遍历父标签链，检查是否出现当前标签
  let currentId: string | undefined = newParentId;
  const visited = new Set<string>();

  while (currentId) {
    if (visited.has(currentId)) {
      return true; // 检测到循环
    }

    if (currentId === tagId) {
      return true; // 找到当前标签，存在循环
    }

    visited.add(currentId);
    currentId = getParentId(currentId);
  }

  return false;
}
