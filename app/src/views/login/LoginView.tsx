import React, { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useNavigate } from 'react-router-dom';

/**
 * 登录/解锁界面
 *
 * Features:
 * - 密码输入框（简洁版）
 * - IPC verify_password(password) 验证主密码
 * - 错误提示（密码错误、锁定状态）
 * - 成功后跳转到文件管理界面
 */
export function LoginView() {
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [failedAttempts, setFailedAttempts] = useState(0);

  /**
   * 提交密码验证
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!password) {
      setError('请输入密码');
      return;
    }

    setIsSubmitting(true);
    try {
      await invoke('verify_password', { password });
      // 验证成功：跳转到文件管理界面
      navigate('/files');
    } catch (err) {
      // 验证失败：记录失败次数，显示错误
      const newFailedAttempts = failedAttempts + 1;
      setFailedAttempts(newFailedAttempts);

      // 3 次失败后锁定 30 秒（可选，暂时只提示）
      if (newFailedAttempts >= 3) {
        setError(
          `密码错误。已失败 ${newFailedAttempts} 次，请仔细检查密码是否正确。`
        );
      } else {
        setError(err as string || '密码错误，请重试');
      }

      // 清空密码输入
      setPassword('');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="login-view">
      <div className="login-card">
        <h1>🔓 解锁 U-Safe</h1>
        <p className="subtitle">
          输入主密码以访问您的加密文件
        </p>

        <form onSubmit={handleSubmit}>
          {/* 密码输入 */}
          <div className="input-group">
            <label htmlFor="password">主密码</label>
            <div className="password-field">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="请输入主密码"
                autoComplete="current-password"
                autoFocus
                disabled={isSubmitting}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="toggle-visibility"
                disabled={isSubmitting}
                aria-label={showPassword ? '隐藏密码' : '显示密码'}
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="error-message" role="alert">
              {error}
            </div>
          )}

          {/* 提交按钮 */}
          <button
            type="submit"
            className="submit-button"
            disabled={isSubmitting || !password}
          >
            {isSubmitting ? '验证中...' : '解锁'}
          </button>
        </form>

        {/* 忘记密码提示 */}
        <div className="forgot-password-hint">
          <p>⚠️ 忘记密码？</p>
          <p>主密码无法恢复。如忘记，您需要重新设置（将丢失所有已加密文件的访问权限）。</p>
          <button
            type="button"
            onClick={() => navigate('/reset-warning')}
            className="forgot-password-link"
          >
            重置密码并清空数据
          </button>
        </div>
      </div>

      <style>{`
        .login-view {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--bg-app);
          padding: var(--space-4);
        }

        .login-card {
          max-width: 420px;
          width: 100%;
          background: var(--bg-card);
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow-2);
          padding: var(--space-8);
        }

        h1 {
          margin: 0 0 var(--space-2) 0;
          font-size: var(--text-2xl);
          font-weight: 700;
          color: var(--text-primary);
          text-align: center;
        }

        .subtitle {
          margin: 0 0 var(--space-6) 0;
          font-size: var(--text-sm);
          color: var(--text-secondary);
          text-align: center;
          line-height: 1.6;
        }

        .input-group {
          margin-bottom: var(--space-4);
        }

        label {
          display: block;
          margin-bottom: var(--space-2);
          font-weight: 600;
          font-size: var(--text-sm);
          color: var(--text-primary);
        }

        .password-field {
          position: relative;
        }

        input {
          width: 100%;
          padding: var(--space-3);
          padding-right: var(--space-10);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          font-size: var(--text-sm);
          color: var(--text-primary);
          background: var(--bg-surface);
          transition: border-color var(--duration-fast) var(--ease-out);
        }

        input:focus {
          outline: none;
          border-color: var(--color-primary);
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        input:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .toggle-visibility {
          position: absolute;
          right: var(--space-2);
          top: 50%;
          transform: translateY(-50%);
          padding: var(--space-2);
          background: none;
          border: none;
          color: var(--text-secondary);
          cursor: pointer;
          font-size: var(--text-lg);
          line-height: 1;
        }

        .toggle-visibility:hover {
          color: var(--text-primary);
        }

        .toggle-visibility:disabled {
          cursor: not-allowed;
          opacity: 0.5;
        }

        .error-message {
          margin-bottom: var(--space-4);
          padding: var(--space-3);
          background: rgba(239, 68, 68, 0.1);
          color: var(--color-error);
          border: 1px solid rgba(239, 68, 68, 0.2);
          border-radius: var(--radius-md);
          font-size: var(--text-sm);
          line-height: 1.5;
        }

        .submit-button {
          width: 100%;
          padding: var(--space-3) var(--space-4);
          background: var(--color-primary);
          color: white;
          border: none;
          border-radius: var(--radius-md);
          font-size: var(--text-sm);
          font-weight: 600;
          cursor: pointer;
          transition: all var(--duration-fast) var(--ease-out);
        }

        .submit-button:hover:not(:disabled) {
          background: var(--color-primary-hover);
          transform: translateY(-1px);
          box-shadow: var(--shadow-2);
        }

        .submit-button:active:not(:disabled) {
          transform: translateY(0);
        }

        .submit-button:focus-visible {
          outline: 2px solid var(--color-primary);
          outline-offset: 2px;
        }

        .submit-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .forgot-password-hint {
          margin-top: var(--space-6);
          padding-top: var(--space-4);
          border-top: 1px solid var(--color-border);
        }

        .forgot-password-hint p {
          margin: var(--space-2) 0;
          font-size: var(--text-xs);
          color: var(--text-secondary);
          line-height: 1.6;
        }

        .forgot-password-hint p:first-child {
          font-weight: 600;
          color: var(--color-warning);
        }

        .forgot-password-link {
          display: inline-block;
          margin-top: var(--space-3);
          padding: var(--space-2) var(--space-3);
          background: none;
          border: 1px solid var(--color-error);
          border-radius: var(--radius-sm);
          color: var(--color-error);
          font-size: var(--text-xs);
          font-weight: 600;
          cursor: pointer;
          transition: all var(--duration-fast) var(--ease-out);
        }

        .forgot-password-link:hover {
          background: rgba(239, 68, 68, 0.1);
          border-color: #dc2626;
          color: #dc2626;
        }

        .forgot-password-link:focus-visible {
          outline: 2px solid var(--color-error);
          outline-offset: 2px;
        }

        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {
          .submit-button,
          input,
          .forgot-password-link {
            transition: none;
          }

          .submit-button:hover:not(:disabled) {
            transform: none;
          }
        }
      `}</style>
    </div>
  );
}
