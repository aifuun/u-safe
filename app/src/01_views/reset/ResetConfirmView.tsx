import { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useNavigate } from 'react-router-dom';

/**
 * 密码重置确认页面
 *
 * 最终确认页面，包含：
 * - 两个确认复选框
 * - 输入 "DELETE" 文本确认
 * - 执行重置操作
 * - 成功后清除 localStorage 并跳转到 /setup
 */
export function ResetConfirmView() {
  const navigate = useNavigate();

  // 表单状态
  const [checkbox1, setCheckbox1] = useState(false);
  const [checkbox2, setCheckbox2] = useState(false);
  const [deleteText, setDeleteText] = useState('');

  // UI 状态
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  /**
   * 检查是否可以提交
   */
  const canSubmit = checkbox1 && checkbox2 && deleteText === 'DELETE' && !isSubmitting;

  /**
   * 取消重置，返回登录页面
   */
  const handleCancel = () => {
    navigate('/login');
  };

  /**
   * 执行重置操作
   */
  const handleConfirm = async () => {
    if (!canSubmit) return;

    setIsSubmitting(true);
    setError('');

    try {
      // 1. 调用 Rust 后端执行重置
      await invoke('reset_app');

      // 2. 清除前端 localStorage
      localStorage.clear();

      // 3. 跳转到密码设置页面
      navigate('/setup', { replace: true });
    } catch (err) {
      console.error('[reset:confirm] 重置失败:', err);
      setError(err as string || '重置失败，请重试');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="reset-confirm-view">
      <div className="reset-confirm-card">
        {/* 标题 */}
        <div className="confirm-header">
          <div className="confirm-icon">🚨</div>
          <h1>最终确认</h1>
          <p className="subtitle">
            这是最后的机会。请仔细阅读并确认以下内容。
          </p>
        </div>

        {/* 确认项 */}
        <div className="confirm-content">
          {/* 确认复选框 1 */}
          <label className="checkbox-item">
            <input
              type="checkbox"
              checked={checkbox1}
              onChange={(e) => setCheckbox1(e.target.checked)}
              disabled={isSubmitting}
            />
            <span className="checkbox-label">
              我理解并接受所有加密文件将<strong>永久丢失</strong>，无法恢复
            </span>
          </label>

          {/* 确认复选框 2 */}
          <label className="checkbox-item">
            <input
              type="checkbox"
              checked={checkbox2}
              onChange={(e) => setCheckbox2(e.target.checked)}
              disabled={isSubmitting}
            />
            <span className="checkbox-label">
              我已尝试所有可能的密码，确认<strong>无法找回</strong>
            </span>
          </label>

          {/* 文本输入确认 */}
          <div className="text-confirm">
            <label htmlFor="delete-confirm">
              请输入 <code>DELETE</code> 以确认重置：
            </label>
            <input
              id="delete-confirm"
              type="text"
              value={deleteText}
              onChange={(e) => setDeleteText(e.target.value)}
              placeholder="输入 DELETE"
              disabled={isSubmitting}
              autoComplete="off"
              className={deleteText && deleteText !== 'DELETE' ? 'invalid' : ''}
            />
            {deleteText && deleteText !== 'DELETE' && (
              <p className="validation-hint">
                请输入大写的 "DELETE"（不含引号）
              </p>
            )}
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="error-message" role="alert">
              {error}
            </div>
          )}

          {/* 提示信息 */}
          <div className="info-box">
            <p className="info-title">💡 重置后将发生什么？</p>
            <ul className="info-list">
              <li>密码哈希文件被删除</li>
              <li>数据库备份到 metadata.db.backup</li>
              <li>所有表数据被清空</li>
              <li>应用跳转到密码设置页面</li>
            </ul>
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="action-buttons">
          <button
            onClick={handleCancel}
            className="btn-cancel"
            disabled={isSubmitting}
          >
            取消
          </button>
          <button
            onClick={handleConfirm}
            className="btn-confirm"
            disabled={!canSubmit}
          >
            {isSubmitting ? '正在重置...' : '确认重置并清空数据'}
          </button>
        </div>
      </div>

      <style>{`
        .reset-confirm-view {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--bg-app);
          padding: var(--space-4);
        }

        .reset-confirm-card {
          max-width: 560px;
          width: 100%;
          background: var(--bg-card);
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow-2);
          padding: var(--space-8);
        }

        .confirm-header {
          text-align: center;
          margin-bottom: var(--space-6);
        }

        .confirm-icon {
          font-size: 48px;
          margin-bottom: var(--space-3);
        }

        h1 {
          margin: 0 0 var(--space-2) 0;
          font-size: var(--text-2xl);
          font-weight: 700;
          color: var(--color-error);
        }

        .subtitle {
          margin: 0;
          font-size: var(--text-sm);
          color: var(--text-secondary);
          line-height: 1.6;
        }

        .confirm-content {
          margin-bottom: var(--space-6);
        }

        .checkbox-item {
          display: flex;
          align-items: flex-start;
          gap: var(--space-3);
          padding: var(--space-4);
          margin-bottom: var(--space-3);
          background: var(--bg-surface);
          border-radius: var(--radius-md);
          cursor: pointer;
          transition: background var(--duration-fast) var(--ease-out);
        }

        .checkbox-item:hover {
          background: var(--bg-card);
        }

        .checkbox-item input[type="checkbox"] {
          margin-top: 2px;
          width: 18px;
          height: 18px;
          cursor: pointer;
          flex-shrink: 0;
        }

        .checkbox-item input[type="checkbox"]:disabled {
          cursor: not-allowed;
          opacity: 0.5;
        }

        .checkbox-label {
          font-size: var(--text-sm);
          color: var(--text-primary);
          line-height: 1.6;
        }

        .checkbox-label strong {
          color: var(--color-error);
        }

        .text-confirm {
          margin-bottom: var(--space-4);
        }

        .text-confirm label {
          display: block;
          margin-bottom: var(--space-2);
          font-size: var(--text-sm);
          font-weight: 600;
          color: var(--text-primary);
        }

        .text-confirm code {
          padding: 2px var(--space-2);
          background: var(--bg-surface);
          border-radius: var(--radius-xs);
          font-family: var(--font-family-mono);
          color: var(--color-error);
        }

        .text-confirm input[type="text"] {
          width: 100%;
          padding: var(--space-3);
          border: 2px solid var(--color-border);
          border-radius: var(--radius-md);
          font-size: var(--text-sm);
          font-family: var(--font-family-mono);
          color: var(--text-primary);
          background: var(--bg-surface);
          transition: border-color var(--duration-fast) var(--ease-out);
        }

        .text-confirm input[type="text"]:focus {
          outline: none;
          border-color: var(--color-primary);
        }

        .text-confirm input[type="text"].invalid {
          border-color: var(--color-error);
        }

        .text-confirm input[type="text"]:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .validation-hint {
          margin: var(--space-2) 0 0 0;
          font-size: var(--text-xs);
          color: var(--color-error);
        }

        .error-message {
          padding: var(--space-3);
          margin-bottom: var(--space-4);
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid var(--color-error);
          border-radius: var(--radius-md);
          color: var(--color-error);
          font-size: var(--text-sm);
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
        .btn-confirm {
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

        .btn-cancel:hover:not(:disabled) {
          background: var(--bg-card);
          border-color: var(--text-secondary);
        }

        .btn-confirm {
          background: var(--color-error);
          color: white;
        }

        .btn-confirm:hover:not(:disabled) {
          background: #dc2626;
          transform: translateY(-1px);
          box-shadow: var(--shadow-2);
        }

        .btn-cancel:disabled,
        .btn-confirm:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .btn-cancel:focus-visible,
        .btn-confirm:focus-visible {
          outline: 2px solid var(--color-primary);
          outline-offset: 2px;
        }

        .btn-cancel:active:not(:disabled),
        .btn-confirm:active:not(:disabled) {
          transform: translateY(0);
        }

        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {
          .checkbox-item,
          .text-confirm input,
          .btn-cancel,
          .btn-confirm {
            transition: none;
          }

          .btn-confirm:hover:not(:disabled),
          .btn-cancel:active:not(:disabled),
          .btn-confirm:active:not(:disabled) {
            transform: none;
          }
        }
      `}</style>
    </div>
  );
}
