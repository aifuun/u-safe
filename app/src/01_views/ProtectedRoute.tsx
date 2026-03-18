import React from 'react';
import { Navigate } from 'react-router-dom';
import { useStore } from 'zustand';
import { authStore } from '../00_kernel/stores';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean; // true = 需要登录，false = 需要未登录
}

/**
 * 路由守卫组件
 *
 * 功能：
 * - requireAuth=true: 未登录 → 重定向 /login
 * - requireAuth=false: 已登录 → 重定向 /files
 *
 * 使用示例：
 * ```tsx
 * // 保护需要登录的路由
 * <Route
 *   path="/files"
 *   element={
 *     <ProtectedRoute requireAuth={true}>
 *       <FileManagementView />
 *     </ProtectedRoute>
 *   }
 * />
 *
 * // 保护不应登录后访问的路由（如 setup）
 * <Route
 *   path="/setup"
 *   element={
 *     <ProtectedRoute requireAuth={false}>
 *       <SetupPasswordView />
 *     </ProtectedRoute>
 *   }
 * />
 * ```
 */
export function ProtectedRoute({
  children,
  requireAuth = true,
}: ProtectedRouteProps) {
  // 从 authStore 读取登录状态
  const isAuthenticated = useStore(authStore, (s) => s.isAuthenticated);

  // 需要登录但未登录 → 重定向到登录页
  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // 不需要登录但已登录 → 重定向到文件管理（防止重复设置密码）
  if (!requireAuth && isAuthenticated) {
    return <Navigate to="/files" replace />;
  }

  // 权限验证通过，渲染子组件
  return <>{children}</>;
}
