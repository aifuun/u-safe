/**
 * 系统主题 Hook
 *
 * 自动检测和监听系统主题变化
 * 参考: .claude/rules/desktop/tauri-ipc.md
 */

import { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { logger } from '@/00_kernel/services/logService';

/**
 * 系统主题类型（与 Rust SystemTheme 对应）
 */
export type SystemTheme = 'light' | 'dark';

/**
 * 主题配置
 */
export interface ThemeConfig {
  /** 当前主题 */
  theme: SystemTheme;
  /** 是否自动跟随系统 */
  followSystem: boolean;
  /** 手动设置主题 */
  setTheme: (theme: SystemTheme) => void;
  /** 切换自动跟随系统 */
  setFollowSystem: (follow: boolean) => void;
}

/**
 * 系统主题 Hook
 *
 * @returns ThemeConfig
 *
 * @example
 * ```tsx
 * const { theme, followSystem, setTheme, setFollowSystem } = useSystemTheme();
 *
 * // 手动设置主题
 * setTheme('dark');
 *
 * // 开启自动跟随系统
 * setFollowSystem(true);
 * ```
 */
export function useSystemTheme(): ThemeConfig {
  const [theme, setThemeState] = useState<SystemTheme>('light');
  const [followSystem, setFollowSystemState] = useState(true);

  // 获取系统主题
  const fetchSystemTheme = async () => {
    try {
      const systemTheme = await invoke<SystemTheme>('get_theme');
      logger.info('useSystemTheme:fetch', { systemTheme });
      return systemTheme;
    } catch (error) {
      logger.error('useSystemTheme:fetch:failed', { error });
      return 'light' as SystemTheme; // 默认亮色
    }
  };

  // 初始化：从 localStorage 读取配置
  useEffect(() => {
    const storedTheme = localStorage.getItem('theme') as SystemTheme | null;
    const storedFollowSystem = localStorage.getItem('followSystem');

    if (storedFollowSystem === 'false') {
      // 用户手动禁用了自动跟随
      setFollowSystemState(false);
      if (storedTheme) {
        setThemeState(storedTheme);
        document.documentElement.setAttribute('data-theme', storedTheme);
      }
    } else {
      // 自动跟随系统
      setFollowSystemState(true);
      fetchSystemTheme().then((systemTheme) => {
        setThemeState(systemTheme);
        document.documentElement.setAttribute('data-theme', systemTheme);
      });
    }
  }, []);

  // 监听系统主题变化（仅在自动跟随时）
  useEffect(() => {
    if (!followSystem) return;

    // 使用 matchMedia 监听系统主题变化
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = (e: MediaQueryListEvent) => {
      const newTheme: SystemTheme = e.matches ? 'dark' : 'light';
      logger.info('useSystemTheme:change', { newTheme });
      setThemeState(newTheme);
      document.documentElement.setAttribute('data-theme', newTheme);
    };

    // 添加监听器
    mediaQuery.addEventListener('change', handleChange);

    // 初始检测
    const initialTheme: SystemTheme = mediaQuery.matches ? 'dark' : 'light';
    setThemeState(initialTheme);
    document.documentElement.setAttribute('data-theme', initialTheme);

    // 清理监听器
    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, [followSystem]);

  // 手动设置主题
  const setTheme = (newTheme: SystemTheme) => {
    logger.info('useSystemTheme:setTheme', { newTheme });
    setThemeState(newTheme);
    setFollowSystemState(false);
    localStorage.setItem('theme', newTheme);
    localStorage.setItem('followSystem', 'false');
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  // 切换自动跟随系统
  const setFollowSystem = (follow: boolean) => {
    logger.info('useSystemTheme:setFollowSystem', { follow });
    setFollowSystemState(follow);
    localStorage.setItem('followSystem', follow.toString());

    if (follow) {
      // 重新获取系统主题
      fetchSystemTheme().then((systemTheme) => {
        setThemeState(systemTheme);
        document.documentElement.setAttribute('data-theme', systemTheme);
      });
    }
  };

  return {
    theme,
    followSystem,
    setTheme,
    setFollowSystem,
  };
}
