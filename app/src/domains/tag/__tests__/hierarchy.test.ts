import { describe, it, expect } from 'vitest';
import {
  buildFullPath,
  parseFullPath,
  getParentPath,
  buildTagTree,
  getAllDescendantIds,
  getAncestors,
  getChildren,
  isAncestor,
  getSubtreeDepth,
  getChildrenCount,
  getDescendantCount,
} from '../rules/hierarchy';
import type { Tag } from '../entities/Tag';

describe('Tag Hierarchy Rules', () => {
  // 测试用的标签数据
  const sampleTags: Tag[] = [
    {
      id: 'tag-1',
      name: '工作',
      parentId: null,
      level: 0,
      fullPath: '工作',
      usageCount: 10,
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
    },
    {
      id: 'tag-2',
      name: '项目A',
      parentId: 'tag-1',
      level: 1,
      fullPath: '工作/项目A',
      usageCount: 5,
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
    },
    {
      id: 'tag-3',
      name: '项目B',
      parentId: 'tag-1',
      level: 1,
      fullPath: '工作/项目B',
      usageCount: 3,
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
    },
    {
      id: 'tag-4',
      name: '文档',
      parentId: 'tag-2',
      level: 2,
      fullPath: '工作/项目A/文档',
      usageCount: 2,
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
    },
    {
      id: 'tag-5',
      name: '个人',
      parentId: null,
      level: 0,
      fullPath: '个人',
      usageCount: 8,
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
    },
  ];

  describe('buildFullPath', () => {
    it('should build root tag path', () => {
      expect(buildFullPath('工作', '')).toBe('工作');
    });

    it('should build child tag path', () => {
      expect(buildFullPath('项目A', '工作')).toBe('工作/项目A');
    });

    it('should build nested tag path', () => {
      expect(buildFullPath('文档', '工作/项目A')).toBe('工作/项目A/文档');
    });
  });

  describe('parseFullPath', () => {
    it('should parse root tag path', () => {
      expect(parseFullPath('工作')).toEqual(['工作']);
    });

    it('should parse nested path', () => {
      expect(parseFullPath('工作/项目A/文档')).toEqual(['工作', '项目A', '文档']);
    });

    it('should handle empty segments', () => {
      expect(parseFullPath('工作//项目A')).toEqual(['工作', '项目A']);
    });

    it('should handle trailing slash', () => {
      expect(parseFullPath('工作/项目A/')).toEqual(['工作', '项目A']);
    });
  });

  describe('getParentPath', () => {
    it('should return empty string for root tags', () => {
      expect(getParentPath('工作')).toBe('');
    });

    it('should return parent path for child tags', () => {
      expect(getParentPath('工作/项目A')).toBe('工作');
    });

    it('should return parent path for nested tags', () => {
      expect(getParentPath('工作/项目A/文档')).toBe('工作/项目A');
    });
  });

  describe('buildTagTree', () => {
    it('should build correct tree structure', () => {
      const tree = buildTagTree(sampleTags);

      // 应该有 2 个根节点
      expect(tree).toHaveLength(2);

      // 检查根节点（按名称排序）
      expect(tree[0].name).toBe('个人');
      expect(tree[1].name).toBe('工作');

      // 检查工作节点的子节点
      const workNode = tree[1];
      expect(workNode.children).toHaveLength(2);
      expect(workNode.children[0].name).toBe('项目A');
      expect(workNode.children[1].name).toBe('项目B');

      // 检查项目A的子节点
      const projectANode = workNode.children[0];
      expect(projectANode.children).toHaveLength(1);
      expect(projectANode.children[0].name).toBe('文档');
    });

    it('should handle empty tag list', () => {
      const tree = buildTagTree([]);
      expect(tree).toHaveLength(0);
    });

    it('should handle orphaned tags (parent not found)', () => {
      const orphanedTags: Tag[] = [
        {
          id: 'orphan',
          name: '孤儿标签',
          parentId: 'non-existent',
          level: 1,
          fullPath: '不存在/孤儿标签',
          usageCount: 0,
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T00:00:00Z',
        },
      ];

      const tree = buildTagTree(orphanedTags);
      // 孤儿标签应该被视为根节点
      expect(tree).toHaveLength(1);
      expect(tree[0].name).toBe('孤儿标签');
    });
  });

  describe('getAllDescendantIds', () => {
    it('should return all descendants including self', () => {
      const descendants = getAllDescendantIds('tag-1', sampleTags);
      expect(descendants).toContain('tag-1'); // 自身
      expect(descendants).toContain('tag-2'); // 子级
      expect(descendants).toContain('tag-3'); // 子级
      expect(descendants).toContain('tag-4'); // 孙级
      expect(descendants).toHaveLength(4);
    });

    it('should return only self for leaf tags', () => {
      const descendants = getAllDescendantIds('tag-4', sampleTags);
      expect(descendants).toEqual(['tag-4']);
    });

    it('should handle root tag with no children', () => {
      const descendants = getAllDescendantIds('tag-5', sampleTags);
      expect(descendants).toEqual(['tag-5']);
    });
  });

  describe('getAncestors', () => {
    it('should return empty array for root tags', () => {
      const ancestors = getAncestors('tag-1', sampleTags);
      expect(ancestors).toHaveLength(0);
    });

    it('should return direct parent for first-level child', () => {
      const ancestors = getAncestors('tag-2', sampleTags);
      expect(ancestors).toHaveLength(1);
      expect(ancestors[0].id).toBe('tag-1');
    });

    it('should return all ancestors in order (root to parent)', () => {
      const ancestors = getAncestors('tag-4', sampleTags);
      expect(ancestors).toHaveLength(2);
      expect(ancestors[0].id).toBe('tag-1'); // 根
      expect(ancestors[1].id).toBe('tag-2'); // 父
    });
  });

  describe('getChildren', () => {
    it('should return all root tags when parentId is null', () => {
      const children = getChildren(null, sampleTags);
      expect(children).toHaveLength(2);
      expect(children.map(c => c.id)).toContain('tag-1');
      expect(children.map(c => c.id)).toContain('tag-5');
    });

    it('should return direct children only', () => {
      const children = getChildren('tag-1', sampleTags);
      expect(children).toHaveLength(2);
      expect(children.map(c => c.id)).toContain('tag-2');
      expect(children.map(c => c.id)).toContain('tag-3');
      expect(children.map(c => c.id)).not.toContain('tag-4'); // 孙级不包括
    });

    it('should return empty array for leaf tags', () => {
      const children = getChildren('tag-4', sampleTags);
      expect(children).toHaveLength(0);
    });

    it('should sort children by name', () => {
      const children = getChildren('tag-1', sampleTags);
      expect(children[0].name).toBe('项目A');
      expect(children[1].name).toBe('项目B');
    });
  });

  describe('isAncestor', () => {
    it('should return true for direct parent', () => {
      expect(isAncestor('tag-1', 'tag-2', sampleTags)).toBe(true);
    });

    it('should return true for grandparent', () => {
      expect(isAncestor('tag-1', 'tag-4', sampleTags)).toBe(true);
    });

    it('should return false for non-ancestors', () => {
      expect(isAncestor('tag-2', 'tag-3', sampleTags)).toBe(false);
      expect(isAncestor('tag-5', 'tag-1', sampleTags)).toBe(false);
    });

    it('should return false for self', () => {
      expect(isAncestor('tag-1', 'tag-1', sampleTags)).toBe(false);
    });
  });

  describe('getSubtreeDepth', () => {
    it('should return 0 for leaf tags', () => {
      expect(getSubtreeDepth('tag-4', sampleTags)).toBe(0);
      expect(getSubtreeDepth('tag-5', sampleTags)).toBe(0);
    });

    it('should return correct depth for tags with children', () => {
      expect(getSubtreeDepth('tag-2', sampleTags)).toBe(1); // tag-2 -> tag-4
      expect(getSubtreeDepth('tag-1', sampleTags)).toBe(2); // tag-1 -> tag-2 -> tag-4
    });
  });

  describe('getChildrenCount', () => {
    it('should return 0 for leaf tags', () => {
      expect(getChildrenCount('tag-4', sampleTags)).toBe(0);
    });

    it('should return direct children count only', () => {
      expect(getChildrenCount('tag-1', sampleTags)).toBe(2); // tag-2, tag-3
      expect(getChildrenCount('tag-2', sampleTags)).toBe(1); // tag-4
    });
  });

  describe('getDescendantCount', () => {
    it('should return 0 for leaf tags', () => {
      expect(getDescendantCount('tag-4', sampleTags)).toBe(0);
    });

    it('should return all descendants count', () => {
      // tag-1 has tag-2, tag-3 (children) and tag-4 (grandchild)
      expect(getDescendantCount('tag-1', sampleTags)).toBe(3);
      // tag-2 has tag-4 (child)
      expect(getDescendantCount('tag-2', sampleTags)).toBe(1);
    });
  });
});
