import { useState } from 'react';
import { FileTreeView } from '@/modules/files';

/**
 * 文件管理主界面
 *
 * 布局：
 * - 顶部工具栏：刷新、新增文件、搜索（占位）
 * - 侧边栏：U 盘选择（占位）、视图切换（占位）
 * - 主内容区：FileTreeView（文件树 + 右键菜单）
 *
 * Phase 3.5 MVP：
 * - ✅ 集成 FileTreeView
 * - ⏳ 工具栏占位（功能在 Phase 4 实现）
 * - ⏳ 侧边栏占位（功能在 Phase 4 实现）
 */
export function FileManagementView() {
  const [rootPath] = useState(''); // Phase 4: 从 U 盘选择器设置

  return (
    <div className="file-management-view">
      {/* 顶部工具栏 */}
      <header className="toolbar">
        <div className="toolbar-left">
          <h1>📁 文件管理</h1>
        </div>
        <div className="toolbar-right">
          <button className="btn-secondary" disabled title="Phase 4">
            🔍 搜索
          </button>
          <button className="btn-secondary" disabled title="Phase 4">
            ➕ 新增文件
          </button>
          <button className="btn-secondary" disabled title="Phase 4">
            🔄 刷新
          </button>
        </div>
      </header>

      {/* 主内容区 */}
      <div className="content-area">
        {/* 侧边栏（占位） */}
        <aside className="sidebar">
          <section className="sidebar-section">
            <h2>U 盘选择</h2>
            <p className="placeholder-text">Phase 4 实现</p>
          </section>
          <section className="sidebar-section">
            <h2>视图切换</h2>
            <p className="placeholder-text">
              • 物理视图 ✅<br />
              • 标签视图 (Phase 4)
            </p>
          </section>
        </aside>

        {/* 文件树主区域 */}
        <main className="main-content">
          {rootPath ? (
            <FileTreeView rootPath={rootPath} />
          ) : (
            <div className="empty-state">
              <p>📂</p>
              <p>请从侧边栏选择 U 盘以开始</p>
              <p className="hint">Phase 4 将支持 U 盘自动检测和选择</p>
            </div>
          )}
        </main>
      </div>

      <style>{`
        .file-management-view {
          display: flex;
          flex-direction: column;
          height: 100vh;
          background: var(--bg-app);
        }

        /* 顶部工具栏 */
        .toolbar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--space-4) var(--space-6);
          background: var(--bg-card);
          border-bottom: 1px solid var(--color-border);
          box-shadow: var(--shadow-1);
        }

        .toolbar-left h1 {
          margin: 0;
          font-size: var(--text-xl);
          font-weight: 700;
          color: var(--text-primary);
        }

        .toolbar-right {
          display: flex;
          gap: var(--space-2);
        }

        .btn-secondary {
          padding: var(--space-2) var(--space-3);
          background: var(--bg-surface);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          font-size: var(--text-sm);
          color: var(--text-primary);
          cursor: pointer;
          transition: background var(--duration-fast) var(--ease-out);
        }

        .btn-secondary:hover:not(:disabled) {
          background: var(--bg-elevated);
        }

        .btn-secondary:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        /* 主内容区 */
        .content-area {
          display: flex;
          flex: 1;
          overflow: hidden;
        }

        /* 侧边栏 */
        .sidebar {
          width: 240px;
          background: var(--bg-card);
          border-right: 1px solid var(--color-border);
          padding: var(--space-4);
          overflow-y: auto;
        }

        .sidebar-section {
          margin-bottom: var(--space-6);
        }

        .sidebar-section h2 {
          margin: 0 0 var(--space-2) 0;
          font-size: var(--text-sm);
          font-weight: 600;
          color: var(--text-secondary);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .placeholder-text {
          margin: 0;
          font-size: var(--text-xs);
          color: var(--text-secondary);
          line-height: 1.6;
        }

        /* 文件树主区域 */
        .main-content {
          flex: 1;
          padding: var(--space-4);
          overflow: auto;
        }

        /* 空状态 */
        .empty-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: var(--text-secondary);
        }

        .empty-state p:first-child {
          font-size: 4rem;
          margin: 0;
        }

        .empty-state p:nth-child(2) {
          margin: var(--space-2) 0;
          font-size: var(--text-lg);
          font-weight: 600;
          color: var(--text-primary);
        }

        .empty-state .hint {
          margin: var(--space-2) 0 0 0;
          font-size: var(--text-xs);
          color: var(--text-secondary);
        }

        /* 响应式 */
        @media (max-width: 768px) {
          .sidebar {
            display: none; /* 移动端隐藏侧边栏 */
          }

          .toolbar {
            padding: var(--space-3) var(--space-4);
          }

          .toolbar-left h1 {
            font-size: var(--text-lg);
          }

          .toolbar-right {
            gap: var(--space-1);
          }
        }
      `}</style>
    </div>
  );
}
