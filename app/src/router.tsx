import { createBrowserRouter, Navigate } from 'react-router-dom';
import { SetupPasswordView } from './01_views/setup';
import { LoginView } from './01_views/login';
import { FileManagementView } from './01_views/files';
import { ProtectedRoute } from './01_views/ProtectedRoute';

/**
 * U-Safe 路由配置
 *
 * 路由表：
 * - / → 重定向到 /login（默认）
 * - /setup → 首次密码设置（已登录用户不可访问）
 * - /login → 密码验证/登录
 * - /files → 文件管理主界面（需要认证）
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
    path: '/files',
    element: (
      <ProtectedRoute requireAuth={true}>
        <FileManagementView />
      </ProtectedRoute>
    ),
  },
  {
    path: '*',
    element: <Navigate to="/login" replace />,
  },
]);
