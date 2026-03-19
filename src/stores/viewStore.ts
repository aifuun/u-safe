import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// 视图类型定义
export type ViewType = 'all-files' | 'tag-view' | 'encrypted-only' | 'recent';

// 过滤模式类型
export type FilterMode = 'AND' | 'OR';

// 视图状态接口
interface ViewStore {
  // 当前视图
  currentView: ViewType;
  setView: (view: ViewType) => void;

  // 标签视图特定状态
  selectedTagIds: string[];
  setSelectedTagIds: (tagIds: string[]) => void;

  // 过滤模式
  filterMode: FilterMode;
  setFilterMode: (mode: FilterMode) => void;

  // 递归查询子标签
  recursive: boolean;
  setRecursive: (recursive: boolean) => void;

  // 搜索查询
  searchQuery: string;
  setSearchQuery: (query: string) => void;

  // 重置函数
  resetTagView: () => void;
  resetAll: () => void;
}

// 初始状态
const initialState = {
  currentView: 'all-files' as ViewType,
  selectedTagIds: [],
  filterMode: 'OR' as FilterMode,
  recursive: false,
  searchQuery: '',
};

/**
 * 视图状态管理 Store
 *
 * 功能:
 * - 管理当前视图类型（全部文件、标签视图、仅加密、最近）
 * - 管理标签视图的过滤条件（选中标签、过滤模式、递归）
 * - 管理搜索查询
 * - 使用 localStorage 持久化部分状态（视图偏好）
 *
 * 持久化策略:
 * - 持久化: currentView, filterMode, recursive（用户偏好）
 * - 不持久化: selectedTagIds, searchQuery（会话特定）
 */
export const useViewStore = create<ViewStore>()(
  persist(
    (set) => ({
      ...initialState,

      // 设置当前视图
      setView: (view: ViewType) => {
        console.info('[view:switch]', { to: view });
        set({ currentView: view });
      },

      // 设置选中的标签 ID
      setSelectedTagIds: (tagIds: string[]) => {
        console.info('[view:tag:select]', { count: tagIds.length });
        set({ selectedTagIds: tagIds });
      },

      // 设置过滤模式
      setFilterMode: (mode: FilterMode) => {
        console.info('[view:filter:mode]', { mode });
        set({ filterMode: mode });
      },

      // 设置递归查询
      setRecursive: (recursive: boolean) => {
        console.info('[view:recursive]', { recursive });
        set({ recursive });
      },

      // 设置搜索查询
      setSearchQuery: (query: string) => {
        console.info('[view:search]', { query: query.substring(0, 20) });
        set({ searchQuery: query });
      },

      // 重置标签视图状态
      resetTagView: () => {
        console.info('[view:tag:reset]');
        set({
          selectedTagIds: [],
          filterMode: 'OR',
          recursive: false,
          searchQuery: '',
        });
      },

      // 重置所有状态
      resetAll: () => {
        console.info('[view:reset:all]');
        set(initialState);
      },
    }),
    {
      name: 'u-safe-view-storage', // localStorage key
      partialize: (state) => ({
        // 只持久化用户偏好，不持久化会话状态
        currentView: state.currentView,
        filterMode: state.filterMode,
        recursive: state.recursive,
        // 不持久化: selectedTagIds, searchQuery
      }),
    }
  )
);
