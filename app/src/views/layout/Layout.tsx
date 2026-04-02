import type { ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from 'zustand';
import { authStore } from '@/modules/auth';

interface LayoutProps {
  children: ReactNode;
}

/**
 * 全局布局组件
 *
 * Features:
 * - 顶部导航栏：Logo、菜单项、退出按钮
 * - 退出按钮：清除登录状态 → 跳转 /login
 */
export function Layout({ children }: LayoutProps) {
  const navigate = useNavigate();
  const logout = useStore(authStore, (s) => s.logout);

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="header-left">
          <h1 className="app-logo">🔐 U-Safe</h1>
          <nav className="app-nav">
            <a href="/files" className="nav-item nav-item--active">
              📁 文件管理
            </a>
            <button className="nav-item" disabled title="Phase 4">
              🏷️ 标签视图
            </button>
            <button className="nav-item" disabled title="Phase 4">
              ⚙️ 设置
            </button>
          </nav>
        </div>
        <div className="header-right">
          <button className="btn-logout" onClick={handleLogout}>
            🚪 退出登录
          </button>
        </div>
      </header>
      <main className="app-main">{children}</main>
    </div>
  );
}
