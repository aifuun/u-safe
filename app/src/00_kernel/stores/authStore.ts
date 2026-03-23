/// <reference types="vite/client" />
import { createStore } from 'zustand/vanilla';
import { invoke } from '@tauri-apps/api/core';
import { logger } from '@/kernel/services/logService';

/**
 * 认证状态
 */
export interface AuthState {
  // 状态
  isAuthenticated: boolean;
  isSetupComplete: boolean;

  // 操作
  login: () => void;
  logout: () => void;
  checkSetupStatus: () => Promise<void>;
  setSetupComplete: (complete: boolean) => void;
}

/**
 * 认证状态管理（Zustand Vanilla Store）
 *
 * 功能：
 * - 管理登录状态（isAuthenticated）
 * - 管理设置完成状态（isSetupComplete）
 * - 持久化到 localStorage
 * - 提供 login/logout 操作
 *
 * 使用示例：
 * ```tsx
 * import { useStore } from 'zustand';
 * import { authStore } from '@/kernel/stores';
 *
 * function MyComponent() {
 *   const isAuthenticated = useStore(authStore, (s) => s.isAuthenticated);
 *   const login = useStore(authStore, (s) => s.login);
 *   // ...
 * }
 * ```
 */
export const authStore = createStore<AuthState>()((set, get) => {
  // 从 localStorage 恢复状态
  const loadPersistedState = (): Partial<AuthState> => {
    try {
      const saved = localStorage.getItem('u-safe-auth');
      if (!saved) return {};

      const data = JSON.parse(saved);

      // 检查是否过期（24 小时）
      const ONE_DAY_MS = 24 * 60 * 60 * 1000;
      const isExpired = Date.now() - data.timestamp > ONE_DAY_MS;

      if (isExpired) {
        localStorage.removeItem('u-safe-auth');
        return {};
      }

      return {
        isAuthenticated: data.isAuthenticated ?? false,
        isSetupComplete: data.isSetupComplete ?? false,
      };
    } catch {
      return {};
    }
  };

  // 持久化到 localStorage
  const persistState = (state: AuthState) => {
    try {
      localStorage.setItem(
        'u-safe-auth',
        JSON.stringify({
          isAuthenticated: state.isAuthenticated,
          isSetupComplete: state.isSetupComplete,
          timestamp: Date.now(),
        })
      );
    } catch (error) {
      logger.error('authStore:persist:failed', { error });
    }
  };

  // 初始状态（从 localStorage 恢复）
  const initialState = {
    isAuthenticated: false,
    isSetupComplete: false,
    ...loadPersistedState(),
  };

  return {
    // 初始状态
    ...initialState,

    // 操作：登录
    login: () => {
      set({ isAuthenticated: true });
      const state = get();
      persistState(state);
    },

    // 操作：登出
    logout: () => {
      set({ isAuthenticated: false });
      const state = get();
      persistState(state);
    },

    // 操作：检查设置状态（调用 IPC）
    checkSetupStatus: async () => {
      try {
        const isSetup = await invoke<boolean>('is_master_key_set');
        set({ isSetupComplete: isSetup });
        const state = get();
        persistState(state);
      } catch (error) {
        logger.error('authStore:checkSetup:failed', { error });
      }
    },

    // 操作：设置完成状态
    setSetupComplete: (complete: boolean) => {
      set({ isSetupComplete: complete });
      const state = get();
      persistState(state);
    },
  };
});

/**
 * 订阅 authStore 变化（用于调试）
 */
if (import.meta.env.DEV) {
  authStore.subscribe((state) => {
    logger.debug('authStore:state:changed', {
      isAuthenticated: state.isAuthenticated,
      isSetupComplete: state.isSetupComplete,
    });
  });
}
