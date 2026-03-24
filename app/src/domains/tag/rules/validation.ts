/**
 * 标签验证业务规则
 * 纯函数，无 IO 依赖
 */

import type { Tag } from '../entities/Tag';

// ========== 常量 ==========

/** 标签名称长度限制 */
export const TAG_NAME_LIMITS = {
  /** 最小长度 */
  MIN: 1,
  /** 最大长度 */
  MAX: 50,
} as const;

/** 标签层级深度限制 */
export const TAG_LEVEL_LIMITS = {
  /** 最大层级深度（包含根标签在内） */
  MAX: 5,
} as const;

/** 保留的系统标签名称 */
export const RESERVED_TAG_NAMES = [
  'system',
  'default',
  'all',
  'none',
] as const;

/** 标签颜色验证正则（十六进制颜色代码） */
export const TAG_COLOR_REGEX = /^#[0-9A-Fa-f]{6}$/;

// ========== 类型定义 ==========

export interface TagValidationError {
  field: 'name' | 'color' | 'level' | 'parent';
  reason: 'empty' | 'too_long' | 'reserved' | 'invalid_format' | 'max_depth' | 'circular_reference';
  message: string;
}

export interface TagValidationResult {
  valid: boolean;
  errors: TagValidationError[];
}

// ========== 验证规则 ==========

/**
 * 验证标签名称
 * 返回 null 表示通过，否则返回错误信息
 */
export function validateTagName(name: string): TagValidationError | null {
  // 检查是否为空
  const trimmedName = name.trim();
  if (trimmedName.length === 0) {
    return {
      field: 'name',
      reason: 'empty',
      message: '标签名称不能为空',
    };
  }

  // 检查长度
  if (trimmedName.length < TAG_NAME_LIMITS.MIN) {
    return {
      field: 'name',
      reason: 'empty',
      message: `标签名称至少需要 ${TAG_NAME_LIMITS.MIN} 个字符`,
    };
  }

  if (trimmedName.length > TAG_NAME_LIMITS.MAX) {
    return {
      field: 'name',
      reason: 'too_long',
      message: `标签名称不能超过 ${TAG_NAME_LIMITS.MAX} 个字符`,
    };
  }

  // 检查保留名称
  if (RESERVED_TAG_NAMES.includes(trimmedName.toLowerCase() as any)) {
    return {
      field: 'name',
      reason: 'reserved',
      message: `"${trimmedName}" 是系统保留名称，请使用其他名称`,
    };
  }

  return null;
}

/**
 * 验证标签颜色
 * 返回 null 表示通过，否则返回错误信息
 */
export function validateTagColor(color: string | undefined): TagValidationError | null {
  // 颜色是可选的
  if (!color) {
    return null;
  }

  // 检查格式（#RRGGBB）
  if (!TAG_COLOR_REGEX.test(color)) {
    return {
      field: 'color',
      reason: 'invalid_format',
      message: '标签颜色必须是十六进制格式（例如 #FF5733）',
    };
  }

  return null;
}

/**
 * 验证标签层级深度
 * 返回 null 表示通过，否则返回错误信息
 */
export function validateTagLevel(level: number): TagValidationError | null {
  if (level < 0) {
    return {
      field: 'level',
      reason: 'invalid_format',
      message: '标签层级不能为负数',
    };
  }

  if (level >= TAG_LEVEL_LIMITS.MAX) {
    return {
      field: 'level',
      reason: 'max_depth',
      message: `标签层级深度不能超过 ${TAG_LEVEL_LIMITS.MAX} 层`,
    };
  }

  return null;
}

/**
 * 验证标签创建参数
 * @param name 标签名称
 * @param color 标签颜色（可选）
 * @param parentLevel 父标签层级（如果是根标签则为 -1）
 */
export function validateTagCreation(
  name: string,
  color: string | undefined,
  parentLevel: number = -1
): TagValidationResult {
  const errors: TagValidationError[] = [];

  // 验证名称
  const nameError = validateTagName(name);
  if (nameError) {
    errors.push(nameError);
  }

  // 验证颜色
  const colorError = validateTagColor(color);
  if (colorError) {
    errors.push(colorError);
  }

  // 验证层级深度
  const newLevel = parentLevel + 1;
  const levelError = validateTagLevel(newLevel);
  if (levelError) {
    errors.push(levelError);
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * 验证标签更新参数
 * @param name 新的标签名称（可选）
 * @param color 新的标签颜色（可选）
 */
export function validateTagUpdate(
  name?: string,
  color?: string
): TagValidationResult {
  const errors: TagValidationError[] = [];

  // 如果提供了名称，则验证
  if (name !== undefined) {
    const nameError = validateTagName(name);
    if (nameError) {
      errors.push(nameError);
    }
  }

  // 如果提供了颜色，则验证
  if (color !== undefined) {
    const colorError = validateTagColor(color);
    if (colorError) {
      errors.push(colorError);
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * 检查是否存在循环引用
 * @param tagId 要检查的标签 ID
 * @param newParentId 新的父标签 ID
 * @param allTags 所有标签的映射
 */
export function hasCircularReference(
  tagId: string,
  newParentId: string | null,
  allTags: Map<string, Tag>
): boolean {
  if (!newParentId) {
    return false; // 设置为根标签，不会循环
  }

  // 检查是否将自己设为父标签
  if (tagId === newParentId) {
    return true;
  }

  // 检查新父标签的祖先链中是否包含当前标签
  let currentId: string | null = newParentId;
  const visited = new Set<string>();

  while (currentId) {
    if (visited.has(currentId)) {
      // 检测到循环（不应该发生在正常数据中）
      return true;
    }

    if (currentId === tagId) {
      // 找到了当前标签，说明存在循环引用
      return true;
    }

    visited.add(currentId);
    const parent = allTags.get(currentId);
    currentId = parent?.parentId ?? null;
  }

  return false;
}
