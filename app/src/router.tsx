import { createBrowserRouter, Navigate } from 'react-router-dom';
import { SetupPasswordView } from './views/setup';
import { LoginView } from './views/login';
import { FileManagementView } from './views/files';
import { ProtectedRoute } from './views/ProtectedRoute';
import { ResetWarningView, ResetConfirmView } from './views/reset';
import { ChangePasswordView, SettingsView } from './views/settings';

/**
 * U-Safe 路由配置
 *
 * 路由表：
 * - / → 重定向到 /login（默认）
 * - /setup → 首次密码设置（已登录用户不可访问）
 * - /login → 密码验证/登录
 * - /reset-warning → 密码重置警告页面
 * - /reset-confirm → 密码重置确认页面
 * - /files → 文件管理主界面（需要认证）
 * - /settings → 设置主页面（需要认证）
 * - /settings/change-password → 修改密码（需要认证）
 *
 * 路由守卫：
 * - ProtectedRoute with requireAuth=true → 保护需要登录的路由
 * - ProtectedRoute with requireAuth=false → 保护不应登录后访问的路由
 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/login" replace />,
  },
  {
    path: '/setup',
    element: (
      <ProtectedRoute requireAuth={false}>
        <SetupPasswordView />
      </ProtectedRoute>
    ),
  },
  {
    path: '/login',
    element: <LoginView />,
  },
  {
    path: '/reset-warning',
    element: <ResetWarningView />,
  },
  {
    path: '/reset-confirm',
    element: <ResetConfirmView />,
  },
  {
    path: '/files',
    element: (
      <ProtectedRoute requireAuth={true}>
        <FileManagementView />
      </ProtectedRoute>
    ),
  },
  {
    path: '/settings',
    element: (
      <ProtectedRoute requireAuth={true}>
        <SettingsView />
      </ProtectedRoute>
    ),
  },
  {
    path: '/settings/change-password',
    element: (
      <ProtectedRoute requireAuth={true}>
        <ChangePasswordView />
      </ProtectedRoute>
    ),
  },
  {
    path: '*',
    element: <Navigate to="/login" replace />,
  },
]);
