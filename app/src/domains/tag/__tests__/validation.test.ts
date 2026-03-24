import { describe, it, expect } from 'vitest';
import {
  TAG_NAME_LIMITS,
  TAG_LEVEL_LIMITS,
  RESERVED_TAG_NAMES,
  TAG_COLOR_REGEX,
  validateTagName,
  validateTagColor,
  validateTagLevel,
  validateTagCreation,
  validateTagUpdate,
  hasCircularReference,
} from '../rules/validation';
import type { Tag } from '../entities/Tag';

describe('Tag Validation Rules', () => {
  describe('validateTagName', () => {
    it('should pass for valid tag names', () => {
      expect(validateTagName('工作')).toBeNull();
      expect(validateTagName('项目A')).toBeNull();
      expect(validateTagName('Personal')).toBeNull();
      expect(validateTagName('长标签名称测试 123')).toBeNull();
    });

    it('should reject empty names', () => {
      const result = validateTagName('');
      expect(result).toMatchObject({
        field: 'name',
        reason: 'empty',
      });
    });

    it('should reject whitespace-only names', () => {
      const result = validateTagName('   ');
      expect(result).toMatchObject({
        field: 'name',
        reason: 'empty',
      });
    });

    it('should reject names that are too long', () => {
      const longName = 'a'.repeat(TAG_NAME_LIMITS.MAX + 1);
      const result = validateTagName(longName);
      expect(result).toMatchObject({
        field: 'name',
        reason: 'too_long',
      });
    });

    it('should reject reserved tag names', () => {
      for (const reserved of RESERVED_TAG_NAMES) {
        const result = validateTagName(reserved);
        expect(result).toMatchObject({
          field: 'name',
          reason: 'reserved',
        });
      }
    });

    it('should reject reserved names case-insensitively', () => {
      const result1 = validateTagName('SYSTEM');
      const result2 = validateTagName('System');
      const result3 = validateTagName('sYsTeM');

      expect(result1?.reason).toBe('reserved');
      expect(result2?.reason).toBe('reserved');
      expect(result3?.reason).toBe('reserved');
    });
  });

  describe('validateTagColor', () => {
    it('should pass for valid hex colors', () => {
      expect(validateTagColor('#FF5733')).toBeNull();
      expect(validateTagColor('#000000')).toBeNull();
      expect(validateTagColor('#FFFFFF')).toBeNull();
      expect(validateTagColor('#abc123')).toBeNull();
    });

    it('should pass for undefined color (optional field)', () => {
      expect(validateTagColor(undefined)).toBeNull();
    });

    it('should reject invalid color formats', () => {
      const invalidColors = [
        'FF5733',      // 缺少 #
        '#FF57',       // 长度不够
        '#FF57339',    // 长度过长
        '#GGGGGG',     // 非十六进制字符
        'red',         // 颜色名称
        'rgb(255,0,0)', // RGB 格式
      ];

      for (const color of invalidColors) {
        const result = validateTagColor(color);
        expect(result).toMatchObject({
          field: 'color',
          reason: 'invalid_format',
        });
      }
    });
  });

  describe('validateTagLevel', () => {
    it('should pass for valid levels', () => {
      expect(validateTagLevel(0)).toBeNull();
      expect(validateTagLevel(1)).toBeNull();
      expect(validateTagLevel(TAG_LEVEL_LIMITS.MAX - 1)).toBeNull();
    });

    it('should reject negative levels', () => {
      const result = validateTagLevel(-1);
      expect(result).toMatchObject({
        field: 'level',
        reason: 'invalid_format',
      });
    });

    it('should reject levels exceeding max depth', () => {
      const result = validateTagLevel(TAG_LEVEL_LIMITS.MAX);
      expect(result).toMatchObject({
        field: 'level',
        reason: 'max_depth',
      });
    });
  });

  describe('validateTagCreation', () => {
    it('should pass for valid tag creation (root tag)', () => {
      const result = validateTagCreation('工作', '#FF5733', -1);
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should pass for valid tag creation (child tag)', () => {
      const result = validateTagCreation('项目A', '#00FF00', 0);
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should pass without color', () => {
      const result = validateTagCreation('工作', undefined, -1);
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should collect multiple validation errors', () => {
      const result = validateTagCreation('', 'invalid-color', TAG_LEVEL_LIMITS.MAX);
      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(1);
    });

    it('should reject tags that would exceed max depth', () => {
      const result = validateTagCreation('深层标签', '#FF5733', TAG_LEVEL_LIMITS.MAX - 1);
      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.reason === 'max_depth')).toBe(true);
    });
  });

  describe('validateTagUpdate', () => {
    it('should pass for valid updates', () => {
      const result1 = validateTagUpdate('新名称');
      expect(result1.valid).toBe(true);

      const result2 = validateTagUpdate(undefined, '#123456');
      expect(result2.valid).toBe(true);

      const result3 = validateTagUpdate('新名称', '#654321');
      expect(result3.valid).toBe(true);
    });

    it('should reject invalid name updates', () => {
      const result = validateTagUpdate('');
      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.field === 'name')).toBe(true);
    });

    it('should reject invalid color updates', () => {
      const result = validateTagUpdate(undefined, 'invalid');
      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.field === 'color')).toBe(true);
    });
  });

  describe('hasCircularReference', () => {
    // 创建测试用的标签树
    const tags: Tag[] = [
      {
        id: 'tag-1',
        name: '工作',
        parentId: null,
        level: 0,
        fullPath: '工作',
        usageCount: 0,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      },
      {
        id: 'tag-2',
        name: '项目A',
        parentId: 'tag-1',
        level: 1,
        fullPath: '工作/项目A',
        usageCount: 0,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      },
      {
        id: 'tag-3',
        name: '文档',
        parentId: 'tag-2',
        level: 2,
        fullPath: '工作/项目A/文档',
        usageCount: 0,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      },
    ];

    const tagMap = new Map(tags.map(t => [t.id, t]));

    it('should detect direct self-reference', () => {
      const result = hasCircularReference('tag-1', 'tag-1', tagMap);
      expect(result).toBe(true);
    });

    it('should detect circular reference (child -> parent)', () => {
      // 尝试将 tag-1 的父级设为 tag-2（它的子级）
      const result = hasCircularReference('tag-1', 'tag-2', tagMap);
      expect(result).toBe(true);
    });

    it('should detect circular reference (grandparent -> grandchild)', () => {
      // 尝试将 tag-1 的父级设为 tag-3（它的孙子级）
      const result = hasCircularReference('tag-1', 'tag-3', tagMap);
      expect(result).toBe(true);
    });

    it('should allow setting parent to sibling', () => {
      // 创建一个兄弟标签
      const sibling: Tag = {
        id: 'tag-4',
        name: '项目B',
        parentId: 'tag-1',
        level: 1,
        fullPath: '工作/项目B',
        usageCount: 0,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      };

      const extendedMap = new Map([...tagMap, [sibling.id, sibling]]);

      // tag-2 设置父级为 tag-4（兄弟关系）
      const result = hasCircularReference('tag-2', 'tag-4', extendedMap);
      expect(result).toBe(false);
    });

    it('should allow setting parent to null (making it root)', () => {
      const result = hasCircularReference('tag-2', null, tagMap);
      expect(result).toBe(false);
    });

    it('should allow moving to unrelated branch', () => {
      // 创建一个无关的标签树
      const unrelated: Tag = {
        id: 'tag-other',
        name: '个人',
        parentId: null,
        level: 0,
        fullPath: '个人',
        usageCount: 0,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      };

      const extendedMap = new Map([...tagMap, [unrelated.id, unrelated]]);

      // 将 tag-2 移动到 tag-other 下
      const result = hasCircularReference('tag-2', 'tag-other', extendedMap);
      expect(result).toBe(false);
    });
  });
});
