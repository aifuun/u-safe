import { create } from 'zustand';
import type { FileNode, FileTreeState } from '../types';

interface FileTreeActions {
  /** 设置根节点 */
  setRoot: (root: FileNode | null) => void;
  /** 切换节点展开/折叠 */
  toggleExpanded: (path: string) => void;
  /** 展开节点 */
  expand: (path: string) => void;
  /** 折叠节点 */
  collapse: (path: string) => void;
  /** 选中节点 */
  select: (path: string | null) => void;
  /** 设置加载状态 */
  setLoading: (loading: boolean) => void;
  /** 设置错误 */
  setError: (error: string | null) => void;
  /** 重置状态 */
  reset: () => void;
}

type FileTreeStore = FileTreeState & FileTreeActions;

const initialState: FileTreeState = {
  root: null,
  expandedPaths: new Set(),
  selectedPath: null,
  loading: false,
  error: null,
};

/**
 * 文件树状态管理 Store
 *
 * 使用 Zustand 管理文件树的展开/折叠、选中状态
 */
export const useFileTreeStore = create<FileTreeStore>((set) => ({
  ...initialState,

  setRoot: (root) => set({ root, error: null }),

  toggleExpanded: (path) =>
    set((state) => {
      const newExpanded = new Set(state.expandedPaths);
      if (newExpanded.has(path)) {
        newExpanded.delete(path);
      } else {
        newExpanded.add(path);
      }
      return { expandedPaths: newExpanded };
    }),

  expand: (path) =>
    set((state) => {
      const newExpanded = new Set(state.expandedPaths);
      newExpanded.add(path);
      return { expandedPaths: newExpanded };
    }),

  collapse: (path) =>
    set((state) => {
      const newExpanded = new Set(state.expandedPaths);
      newExpanded.delete(path);
      return { expandedPaths: newExpanded };
    }),

  select: (path) => set({ selectedPath: path }),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error, loading: false }),

  reset: () => set(initialState),
}));
