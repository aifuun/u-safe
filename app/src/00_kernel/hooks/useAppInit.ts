import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { invoke } from '@tauri-apps/api/core';
import { logger } from '@/00_kernel/services/logService';

interface AppInitState {
  isLoading: boolean;
  isSetupComplete: boolean | null;
  isAuthenticated: boolean;
}

/**
 * 应用初始化 Hook
 *
 * 功能：
 * - 检测是否已设置主密码（查询 config 表 master_key_hash）
 * - 根据状态自动导航：
 *   1. 未设置密码 → /setup
 *   2. 已设置但未登录 → /login
 *   3. 已登录 → /files
 *
 * 使用示例：
 * ```tsx
 * function App() {
 *   const { isLoading } = useAppInit();
 *   if (isLoading) return <LoadingScreen />;
 *   return <Router>...</Router>;
 * }
 * ```
 */
export function useAppInit(): AppInitState {
  const navigate = useNavigate();
  const [state, setState] = useState<AppInitState>({
    isLoading: true,
    isSetupComplete: null,
    isAuthenticated: false,
  });

  useEffect(() => {
    const checkAppStatus = async () => {
      try {
        // 1. 检查是否已设置主密码
        const setupComplete = await invoke<boolean>('is_master_key_set');

        if (!setupComplete) {
          // 未设置密码 → 跳转到设置页
          setState({
            isLoading: false,
            isSetupComplete: false,
            isAuthenticated: false,
          });
          navigate('/setup', { replace: true });
          return;
        }

        // 2. 检查是否已登录（从 authStore 读取或检查 session）
        // 注意：这里简化处理，实际应该从 authStore 读取
        const authenticated = checkAuthentication();

        if (!authenticated) {
          // 已设置密码但未登录 → 跳转到登录页
          setState({
            isLoading: false,
            isSetupComplete: true,
            isAuthenticated: false,
          });
          navigate('/login', { replace: true });
          return;
        }

        // 3. 已登录 → 跳转到文件管理
        setState({
          isLoading: false,
          isSetupComplete: true,
          isAuthenticated: true,
        });
        navigate('/files', { replace: true });
      } catch (error) {
        logger.error('useAppInit:check:failed', { error });
        // 出错时默认跳转登录页（安全做法）
        setState({
          isLoading: false,
          isSetupComplete: true,
          isAuthenticated: false,
        });
        navigate('/login', { replace: true });
      }
    };

    checkAppStatus();
  }, [navigate]);

  return state;
}

/**
 * 检查用户是否已登录
 *
 * 策略：
 * - 优先从 localStorage 读取 auth token
 * - 如果 token 存在，验证是否过期
 * - 未来可以集成 authStore
 */
function checkAuthentication(): boolean {
  try {
    const authData = localStorage.getItem('u-safe-auth');
    if (!authData) return false;

    const { isAuthenticated, timestamp } = JSON.parse(authData);

    // 检查是否过期（24 小时后自动失效）
    const ONE_DAY_MS = 24 * 60 * 60 * 1000;
    const isExpired = Date.now() - timestamp > ONE_DAY_MS;

    return isAuthenticated && !isExpired;
  } catch {
    return false;
  }
}
