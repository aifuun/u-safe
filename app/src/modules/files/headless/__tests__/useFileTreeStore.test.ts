import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useFileTreeStore } from '../useFileTreeStore';
import type { FileNode } from '../../types';

describe('useFileTreeStore', () => {
  beforeEach(() => {
    // Reset store before each test
    const { reset } = useFileTreeStore.getState();
    reset();
  });

  describe('initial state', () => {
    it('should have correct initial values', () => {
      const { result } = renderHook(() => useFileTreeStore());

      expect(result.current.root).toBeNull();
      expect(result.current.expandedPaths).toEqual(new Set());
      expect(result.current.selectedPath).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });
  });

  describe('setRoot', () => {
    it('should set root node', () => {
      const { result } = renderHook(() => useFileTreeStore());
      const mockRoot: FileNode = {
        path: '/test',
        name: 'test',
        size: 0,
        is_dir: true,
        children: [],
      };

      act(() => {
        result.current.setRoot(mockRoot);
      });

      expect(result.current.root).toEqual(mockRoot);
      expect(result.current.error).toBeNull();
    });

    it('should clear error when setting root', () => {
      const { result } = renderHook(() => useFileTreeStore());

      act(() => {
        result.current.setError('Some error');
      });

      expect(result.current.error).toBe('Some error');

      act(() => {
        result.current.setRoot({ path: '/test', name: 'test', size: 0, is_dir: true });
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('toggleExpanded', () => {
    it('should add path to expanded set when not present', () => {
      const { result } = renderHook(() => useFileTreeStore());

      act(() => {
        result.current.toggleExpanded('/test/dir1');
      });

      expect(result.current.expandedPaths.has('/test/dir1')).toBe(true);
    });

    it('should remove path from expanded set when present', () => {
      const { result } = renderHook(() => useFileTreeStore());

      act(() => {
        result.current.expand('/test/dir1');
        result.current.toggleExpanded('/test/dir1');
      });

      expect(result.current.expandedPaths.has('/test/dir1')).toBe(false);
    });

    it('should toggle multiple paths independently', () => {
      const { result } = renderHook(() => useFileTreeStore());

      act(() => {
        result.current.toggleExpanded('/test/dir1');
        result.current.toggleExpanded('/test/dir2');
      });

      expect(result.current.expandedPaths.has('/test/dir1')).toBe(true);
      expect(result.current.expandedPaths.has('/test/dir2')).toBe(true);

      act(() => {
        result.current.toggleExpanded('/test/dir1');
      });

      expect(result.current.expandedPaths.has('/test/dir1')).toBe(false);
      expect(result.current.expandedPaths.has('/test/dir2')).toBe(true);
    });
  });

  describe('expand', () => {
    it('should add path to expanded set', () => {
      const { result } = renderHook(() => useFileTreeStore());

      act(() => {
        result.current.expand('/test/dir1');
      });

      expect(result.current.expandedPaths.has('/test/dir1')).toBe(true);
    });

    it('should be idempotent', () => {
      const { result } = renderHook(() => useFileTreeStore());

      act(() => {
        result.current.expand('/test/dir1');
        result.current.expand('/test/dir1');
      });

      expect(result.current.expandedPaths.size).toBe(1);
      expect(result.current.expandedPaths.has('/test/dir1')).toBe(true);
    });
  });

  describe('collapse', () => {
    it('should remove path from expanded set', () => {
      const { result } = renderHook(() => useFileTreeStore());

      act(() => {
        result.current.expand('/test/dir1');
        result.current.collapse('/test/dir1');
      });

      expect(result.current.expandedPaths.has('/test/dir1')).toBe(false);
    });

    it('should be idempotent', () => {
      const { result } = renderHook(() => useFileTreeStore());

      act(() => {
        result.current.expand('/test/dir1');
        result.current.collapse('/test/dir1');
        result.current.collapse('/test/dir1');
      });

      expect(result.current.expandedPaths.has('/test/dir1')).toBe(false);
    });
  });

  describe('select', () => {
    it('should set selected path', () => {
      const { result } = renderHook(() => useFileTreeStore());

      act(() => {
        result.current.select('/test/file.txt');
      });

      expect(result.current.selectedPath).toBe('/test/file.txt');
    });

    it('should clear selected path with null', () => {
      const { result } = renderHook(() => useFileTreeStore());

      act(() => {
        result.current.select('/test/file.txt');
        result.current.select(null);
      });

      expect(result.current.selectedPath).toBeNull();
    });

    it('should replace previous selection', () => {
      const { result } = renderHook(() => useFileTreeStore());

      act(() => {
        result.current.select('/test/file1.txt');
        result.current.select('/test/file2.txt');
      });

      expect(result.current.selectedPath).toBe('/test/file2.txt');
    });
  });

  describe('setLoading', () => {
    it('should set loading state', () => {
      const { result } = renderHook(() => useFileTreeStore());

      act(() => {
        result.current.setLoading(true);
      });

      expect(result.current.loading).toBe(true);

      act(() => {
        result.current.setLoading(false);
      });

      expect(result.current.loading).toBe(false);
    });
  });

  describe('setError', () => {
    it('should set error message', () => {
      const { result } = renderHook(() => useFileTreeStore());

      act(() => {
        result.current.setError('Test error');
      });

      expect(result.current.error).toBe('Test error');
      expect(result.current.loading).toBe(false);
    });

    it('should clear error with null', () => {
      const { result } = renderHook(() => useFileTreeStore());

      act(() => {
        result.current.setError('Test error');
        result.current.setError(null);
      });

      expect(result.current.error).toBeNull();
    });

    it('should set loading to false when setting error', () => {
      const { result } = renderHook(() => useFileTreeStore());

      act(() => {
        result.current.setLoading(true);
        result.current.setError('Test error');
      });

      expect(result.current.loading).toBe(false);
    });
  });

  describe('reset', () => {
    it('should reset all state to initial values', () => {
      const { result } = renderHook(() => useFileTreeStore());

      act(() => {
        result.current.setRoot({ path: '/test', name: 'test', size: 0, is_dir: true });
        result.current.expand('/test/dir1');
        result.current.select('/test/file.txt');
        result.current.setLoading(true);
        result.current.setError('Test error');

        result.current.reset();
      });

      expect(result.current.root).toBeNull();
      expect(result.current.expandedPaths).toEqual(new Set());
      expect(result.current.selectedPath).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });
  });
});
