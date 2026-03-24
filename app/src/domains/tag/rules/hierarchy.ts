/**
 * 标签层级关系业务规则
 * 纯函数，处理标签树的构建和操作
 */

import type { Tag, TagTreeNode } from '../entities/Tag';

// ========== 路径操作 ==========

/**
 * 构建标签的完整路径
 * @param tagName 当前标签名称
 * @param parentPath 父标签的完整路径（如果是根标签则为空字符串）
 * @returns 完整路径（例如 "工作/项目A"）
 */
export function buildFullPath(tagName: string, parentPath: string): string {
  if (!parentPath) {
    return tagName;
  }
  return `${parentPath}/${tagName}`;
}

/**
 * 解析完整路径为层级数组
 * @param fullPath 完整路径（例如 "工作/项目A/文档"）
 * @returns 层级数组 ["工作", "项目A", "文档"]
 */
export function parseFullPath(fullPath: string): string[] {
  return fullPath.split('/').filter(segment => segment.length > 0);
}

/**
 * 获取父标签路径
 * @param fullPath 完整路径（例如 "工作/项目A/文档"）
 * @returns 父标签路径（例如 "工作/项目A"），如果是根标签则返回空字符串
 */
export function getParentPath(fullPath: string): string {
  const segments = parseFullPath(fullPath);
  if (segments.length <= 1) {
    return '';
  }
  return segments.slice(0, -1).join('/');
}

// ========== 树操作 ==========

/**
 * 将标签列表构建为树结构
 * @param tags 标签列表
 * @returns 根标签节点数组
 */
export function buildTagTree(tags: Tag[]): TagTreeNode[] {
  // 创建标签映射以便快速查找
  const tagMap = new Map<string, TagTreeNode>();

  // 初始化所有标签节点
  for (const tag of tags) {
    tagMap.set(tag.id, { ...tag, children: [] });
  }

  // 构建树结构
  const roots: TagTreeNode[] = [];

  for (const node of tagMap.values()) {
    if (node.parentId === null) {
      // 根标签
      roots.push(node);
    } else {
      // 子标签，添加到父标签的 children 中
      const parent = tagMap.get(node.parentId);
      if (parent) {
        parent.children.push(node);
      } else {
        // 父标签不存在，将其视为根标签（数据不一致的情况）
        roots.push(node);
      }
    }
  }

  // 按名称排序（递归）
  function sortTree(nodes: TagTreeNode[]): void {
    nodes.sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'));
    for (const node of nodes) {
      sortTree(node.children);
    }
  }

  sortTree(roots);

  return roots;
}

/**
 * 获取标签的所有子标签 ID（包括子孙标签）
 * @param tagId 标签 ID
 * @param tags 所有标签列表
 * @returns 子标签 ID 数组（包括自身）
 */
export function getAllDescendantIds(tagId: string, tags: Tag[]): string[] {
  const result = [tagId];

  function collectChildren(currentId: string): void {
    for (const tag of tags) {
      if (tag.parentId === currentId) {
        result.push(tag.id);
        collectChildren(tag.id);
      }
    }
  }

  collectChildren(tagId);
  return result;
}

/**
 * 获取标签的所有祖先标签
 * @param tagId 标签 ID
 * @param tags 所有标签列表
 * @returns 祖先标签数组（从根到父，不包括自身）
 */
export function getAncestors(tagId: string, tags: Tag[]): Tag[] {
  const ancestors: Tag[] = [];
  const tagMap = new Map(tags.map(t => [t.id, t]));

  let current = tagMap.get(tagId);
  while (current && current.parentId) {
    const parent = tagMap.get(current.parentId);
    if (parent) {
      ancestors.unshift(parent); // 添加到开头，保持从根到父的顺序
      current = parent;
    } else {
      break;
    }
  }

  return ancestors;
}

/**
 * 获取标签的直接子标签
 * @param tagId 标签 ID（null 表示获取所有根标签）
 * @param tags 所有标签列表
 * @returns 子标签数组
 */
export function getChildren(tagId: string | null, tags: Tag[]): Tag[] {
  return tags
    .filter(tag => tag.parentId === tagId)
    .sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'));
}

/**
 * 检查标签是否为另一个标签的祖先
 * @param ancestorId 可能的祖先标签 ID
 * @param descendantId 后代标签 ID
 * @param tags 所有标签列表
 */
export function isAncestor(
  ancestorId: string,
  descendantId: string,
  tags: Tag[]
): boolean {
  const ancestors = getAncestors(descendantId, tags);
  return ancestors.some(tag => tag.id === ancestorId);
}

// ========== 统计信息 ==========

/**
 * 计算标签树的深度
 * @param tagId 标签 ID
 * @param tags 所有标签列表
 * @returns 从该标签到最深子标签的深度
 */
export function getSubtreeDepth(tagId: string, tags: Tag[]): number {
  const children = getChildren(tagId, tags);

  if (children.length === 0) {
    return 0;
  }

  const childDepths = children.map(child => getSubtreeDepth(child.id, tags));
  return 1 + Math.max(...childDepths);
}

/**
 * 计算标签的子标签数量（不包括子孙标签）
 * @param tagId 标签 ID
 * @param tags 所有标签列表
 */
export function getChildrenCount(tagId: string, tags: Tag[]): number {
  return tags.filter(tag => tag.parentId === tagId).length;
}

/**
 * 计算标签的所有后代数量（包括子孙标签）
 * @param tagId 标签 ID
 * @param tags 所有标签列表
 */
export function getDescendantCount(tagId: string, tags: Tag[]): number {
  return getAllDescendantIds(tagId, tags).length - 1; // 减去自身
}
