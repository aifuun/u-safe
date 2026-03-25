import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useNavigate } from 'react-router-dom';

/**
 * 重置统计数据接口
 * 与 Rust 后端的 ResetStats 结构对应
 */
interface ResetStats {
  encrypted_files_count: number;
  total_files_count: number;
  tags_count: number;
  database_size_bytes: number;
}

/**
 * 密码重置警告页面
 *
 * 显示将要删除的数据统计，警告用户数据将永久丢失
 * 用户点击「继续」后跳转到确认页面
 */
export function ResetWarningView() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<ResetStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  /**
   * 加载重置统计数据
   */
  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await invoke<ResetStats>('get_reset_stats');
        setStats(data);
      } catch (err) {
        console.error('[reset:warning] 获取统计失败:', err);
        setError(err as string || '获取数据失败');
      } finally {
        setIsLoading(false);
      }
    };

    loadStats();
  }, []);

  /**
   * 取消重置，返回登录页面
   */
  const handleCancel = () => {
    navigate('/login');
  };

  /**
   * 继续重置流程，跳转到确认页面
   */
  const handleContinue = () => {
    navigate('/reset-confirm');
  };

  /**
   * 格式化文件大小
   */
  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  };

  return (
    <div className="reset-warning-view">
      <div className="reset-warning-card">
        {/* 警告标题 */}
        <div className="warning-header">
          <div className="warning-icon">⚠️</div>
          <h1>密码重置警告</h1>
        </div>

        {/* 加载中 */}
        {isLoading && (
          <div className="loading-state">
            <p>正在加载数据统计...</p>
          </div>
        )}

        {/* 加载失败 */}
        {error && (
          <div className="error-message" role="alert">
            <p>{error}</p>
            <button onClick={handleCancel} className="btn-secondary">
              返回登录
            </button>
          </div>
        )}

        {/* 显示统计数据 */}
        {!isLoading && !error && stats && (
          <>
            <div className="warning-content">
              <p className="warning-text">
                <strong>重置密码将删除所有数据，此操作不可撤销！</strong>
              </p>
              <p className="warning-subtext">
                以下数据将被永久删除：
              </p>

              {/* 数据统计 */}
              <div className="stats-list">
                <div className="stat-item">
                  <span className="stat-icon">🔒</span>
                  <span className="stat-label">加密文件</span>
                  <span className="stat-value">{stats.encrypted_files_count} 个</span>
                </div>
                <div className="stat-item">
                  <span className="stat-icon">📄</span>
                  <span className="stat-label">所有文件记录</span>
                  <span className="stat-value">{stats.total_files_count} 个</span>
                </div>
                <div className="stat-item">
                  <span className="stat-icon">🏷️</span>
                  <span className="stat-label">标签</span>
                  <span className="stat-value">{stats.tags_count} 个</span>
                </div>
                <div className="stat-item">
                  <span className="stat-icon">💾</span>
                  <span className="stat-label">数据库大小</span>
                  <span className="stat-value">{formatBytes(stats.database_size_bytes)}</span>
                </div>
              </div>

              {/* 重要说明 */}
              <div className="info-box">
                <p className="info-title">📌 重要说明</p>
                <ul className="info-list">
                  <li>已加密的文件将永久无法解密</li>
                  <li>所有标签和文件记录将被清空</li>
                  <li>数据库将备份到 metadata.db.backup</li>
                  <li>您需要重新设置主密码</li>
                </ul>
              </div>
            </div>

            {/* 操作按钮 */}
            <div className="action-buttons">
              <button onClick={handleCancel} className="btn-cancel">
                取消
              </button>
              <button onClick={handleContinue} className="btn-continue">
                我了解风险，继续
              </button>
            </div>
          </>
        )}
      </div>

      <style>{`
        .reset-warning-view {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--bg-app);
          padding: var(--space-4);
        }

        .reset-warning-card {
          max-width: 560px;
          width: 100%;
          background: var(--bg-card);
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow-2);
          padding: var(--space-8);
        }

        .warning-header {
          text-align: center;
          margin-bottom: var(--space-6);
        }

        .warning-icon {
          font-size: 48px;
          margin-bottom: var(--space-3);
        }

        h1 {
          margin: 0;
          font-size: var(--text-2xl);
          font-weight: 700;
          color: var(--color-error);
        }

        .loading-state {
          text-align: center;
          padding: var(--space-6);
          color: var(--text-secondary);
        }

        .error-message {
          padding: var(--space-4);
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid var(--color-error);
          border-radius: var(--radius-md);
          color: var(--color-error);
          text-align: center;
        }

        .error-message p {
          margin: 0 0 var(--space-3) 0;
        }

        .warning-content {
          margin-bottom: var(--space-6);
        }

        .warning-text {
          margin: 0 0 var(--space-3) 0;
          font-size: var(--text-base);
          color: var(--color-error);
          text-align: center;
          line-height: 1.6;
        }

        .warning-subtext {
          margin: 0 0 var(--space-4) 0;
          font-size: var(--text-sm);
          color: var(--text-secondary);
          text-align: center;
        }

        .stats-list {
          margin-bottom: var(--space-6);
        }

        .stat-item {
          display: flex;
          align-items: center;
          padding: var(--space-3);
          margin-bottom: var(--space-2);
          background: var(--bg-surface);
          border-radius: var(--radius-md);
        }

        .stat-icon {
          font-size: var(--text-xl);
          margin-right: var(--space-3);
        }

        .stat-label {
          flex: 1;
          font-size: var(--text-sm);
          color: var(--text-secondary);
        }

        .stat-value {
          font-size: var(--text-base);
          font-weight: 600;
          color: var(--text-primary);
        }

        .info-box {
          padding: var(--space-4);
          background: rgba(59, 130, 246, 0.1);
          border: 1px solid rgba(59, 130, 246, 0.2);
          border-radius: var(--radius-md);
        }

        .info-title {
          margin: 0 0 var(--space-3) 0;
          font-size: var(--text-sm);
          font-weight: 600;
          color: var(--color-primary);
        }

        .info-list {
          margin: 0;
          padding-left: var(--space-5);
        }

        .info-list li {
          margin-bottom: var(--space-2);
          font-size: var(--text-sm);
          color: var(--text-secondary);
          line-height: 1.6;
        }

        .info-list li:last-child {
          margin-bottom: 0;
        }

        .action-buttons {
          display: flex;
          gap: var(--space-3);
        }

        .btn-cancel,
        .btn-continue,
        .btn-secondary {
          flex: 1;
          padding: var(--space-3) var(--space-4);
          border: none;
          border-radius: var(--radius-md);
          font-size: var(--text-sm);
          font-weight: 600;
          cursor: pointer;
          transition: all var(--duration-fast) var(--ease-out);
        }

        .btn-cancel {
          background: var(--bg-surface);
          color: var(--text-primary);
          border: 1px solid var(--color-border);
        }

        .btn-cancel:hover {
          background: var(--bg-card);
          border-color: var(--text-secondary);
        }

        .btn-continue {
          background: var(--color-error);
          color: white;
        }

        .btn-continue:hover {
          background: #dc2626;
          transform: translateY(-1px);
          box-shadow: var(--shadow-2);
        }

        .btn-secondary {
          background: var(--color-primary);
          color: white;
        }

        .btn-secondary:hover {
          background: var(--color-primary-hover);
        }

        .btn-cancel:focus-visible,
        .btn-continue:focus-visible,
        .btn-secondary:focus-visible {
          outline: 2px solid var(--color-primary);
          outline-offset: 2px;
        }

        .btn-cancel:active,
        .btn-continue:active,
        .btn-secondary:active {
          transform: translateY(0);
        }

        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {
          .btn-cancel,
          .btn-continue,
          .btn-secondary {
            transition: none;
          }

          .btn-continue:hover,
          .btn-cancel:active,
          .btn-continue:active {
            transform: none;
          }
        }
      `}</style>
    </div>
  );
}
