import { useNavigate } from 'react-router-dom';

/**
 * 设置主页面
 *
 * Features:
 * - 修改主密码入口
 * - 其他设置选项（占位符）
 */
export function SettingsView() {
  const navigate = useNavigate();

  return (
    <div className="settings-view">
      <div className="header">
        <button
          className="back-button"
          onClick={() => navigate('/files')}
          aria-label="返回文件管理"
        >
          ← 返回
        </button>
        <h1>⚙️ 设置</h1>
      </div>

      <div className="settings-sections">
        {/* 安全设置 */}
        <section className="settings-section">
          <h2 className="section-title">安全</h2>
          <div className="setting-list">
            <button
              className="setting-item"
              onClick={() => navigate('/settings/change-password')}
            >
              <div className="setting-icon">🔑</div>
              <div className="setting-content">
                <h3>修改主密码</h3>
                <p>更改用于加密文件的主密码</p>
              </div>
              <div className="setting-arrow">→</div>
            </button>

            {/* 占位符：未来功能 */}
            <div className="setting-item disabled">
              <div className="setting-icon">🔐</div>
              <div className="setting-content">
                <h3>恢复密钥</h3>
                <p>导出恢复密钥以防密码丢失（即将推出）</p>
              </div>
            </div>
          </div>
        </section>

        {/* 数据管理 */}
        <section className="settings-section">
          <h2 className="section-title">数据管理</h2>
          <div className="setting-list">
            <div className="setting-item disabled">
              <div className="setting-icon">📊</div>
              <div className="setting-content">
                <h3>存储统计</h3>
                <p>查看加密文件占用的空间（即将推出）</p>
              </div>
            </div>

            <div className="setting-item disabled">
              <div className="setting-icon">🗑️</div>
              <div className="setting-content">
                <h3>清理缓存</h3>
                <p>清除临时文件和缓存数据（即将推出）</p>
              </div>
            </div>
          </div>
        </section>

        {/* 关于 */}
        <section className="settings-section">
          <h2 className="section-title">关于</h2>
          <div className="setting-list">
            <div className="setting-item disabled">
              <div className="setting-icon">ℹ️</div>
              <div className="setting-content">
                <h3>应用信息</h3>
                <p>版本、许可证和帮助文档（即将推出）</p>
              </div>
            </div>
          </div>
        </section>
      </div>

      <style>{`
        .settings-view {
          max-width: 800px;
          margin: 0 auto;
          padding: var(--space-6);
        }

        .header {
          margin-bottom: var(--space-6);
        }

        .back-button {
          background: none;
          border: none;
          color: var(--color-primary);
          font-size: var(--text-sm);
          cursor: pointer;
          padding: var(--space-2);
          margin-bottom: var(--space-3);
          transition: opacity var(--duration-fast) var(--ease-out);
        }

        .back-button:hover {
          opacity: 0.7;
        }

        .back-button:focus-visible {
          outline: 2px solid var(--color-primary);
          outline-offset: 2px;
          border-radius: var(--radius-sm);
        }

        h1 {
          font-size: var(--text-2xl);
          font-weight: 700;
          color: var(--text-primary);
          margin: 0;
        }

        .settings-sections {
          display: flex;
          flex-direction: column;
          gap: var(--space-6);
        }

        .settings-section {
          background: var(--bg-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: var(--space-5);
        }

        .section-title {
          font-size: var(--text-lg);
          font-weight: 600;
          color: var(--text-primary);
          margin: 0 0 var(--space-4) 0;
        }

        .setting-list {
          display: flex;
          flex-direction: column;
          gap: var(--space-2);
        }

        .setting-item {
          display: flex;
          align-items: center;
          gap: var(--space-4);
          padding: var(--space-4);
          background: var(--bg-default);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          cursor: pointer;
          transition: all var(--duration-fast) var(--ease-out);
          text-align: left;
          width: 100%;
        }

        .setting-item:not(.disabled):hover {
          background: var(--bg-hover);
          border-color: var(--color-primary);
          transform: translateX(4px);
        }

        .setting-item:not(.disabled):focus-visible {
          outline: 2px solid var(--color-primary);
          outline-offset: 2px;
        }

        .setting-item.disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .setting-item.disabled:hover {
          transform: none;
          border-color: var(--color-border);
          background: var(--bg-default);
        }

        .setting-icon {
          font-size: var(--text-2xl);
          flex-shrink: 0;
        }

        .setting-content {
          flex: 1;
        }

        .setting-content h3 {
          font-size: var(--text-base);
          font-weight: 600;
          color: var(--text-primary);
          margin: 0 0 var(--space-1) 0;
        }

        .setting-content p {
          font-size: var(--text-sm);
          color: var(--text-secondary);
          margin: 0;
        }

        .setting-arrow {
          font-size: var(--text-xl);
          color: var(--text-muted);
          flex-shrink: 0;
          transition: transform var(--duration-fast) var(--ease-out);
        }

        .setting-item:not(.disabled):hover .setting-arrow {
          transform: translateX(4px);
        }

        /* 响应式设计 */
        @media (max-width: 768px) {
          .settings-view {
            padding: var(--space-4);
          }

          .settings-section {
            padding: var(--space-4);
          }

          .setting-item {
            padding: var(--space-3);
          }

          .setting-icon {
            font-size: var(--text-xl);
          }
        }

        /* 减少动画（可访问性） */
        @media (prefers-reduced-motion: reduce) {
          .setting-item,
          .setting-arrow,
          .back-button {
            transition: none;
          }

          .setting-item:hover {
            transform: none;
          }

          .setting-item:hover .setting-arrow {
            transform: none;
          }
        }
      `}</style>
    </div>
  );
}
