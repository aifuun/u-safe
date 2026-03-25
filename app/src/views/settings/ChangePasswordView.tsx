import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { invoke } from '@tauri-apps/api/core';

/**
 * 修改密码视图
 *
 * Features:
 * - 三个密码输入框（当前密码、新密码、确认新密码）
 * - 前端验证（密码强度、一致性检查）
 * - 错误处理和显示
 * - 加载状态
 */
export function ChangePasswordView() {
  const navigate = useNavigate();

  // 表单状态
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // UI 状态
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPasswords, setShowPasswords] = useState({
    old: false,
    new: false,
    confirm: false
  });

  // 密码强度检查
  const validatePasswordStrength = (pwd: string): { valid: boolean; message: string } => {
    if (pwd.length < 8) {
      return { valid: false, message: '密码长度至少 8 个字符' };
    }

    const hasLowerCase = /[a-z]/.test(pwd);
    const hasUpperCase = /[A-Z]/.test(pwd);
    const hasNumber = /[0-9]/.test(pwd);

    if (!hasLowerCase || !hasUpperCase || !hasNumber) {
      return { valid: false, message: '密码需要包含大小写字母和数字' };
    }

    return { valid: true, message: '密码强度：强' };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // 前端验证
    if (!oldPassword || !newPassword || !confirmPassword) {
      setError('请填写所有密码字段');
      return;
    }

    if (oldPassword === newPassword) {
      setError('新密码不能与旧密码相同');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('两次输入的新密码不一致');
      return;
    }

    const validation = validatePasswordStrength(newPassword);
    if (!validation.valid) {
      setError(validation.message);
      return;
    }

    // 调用 IPC 修改密码
    setIsSubmitting(true);
    try {
      await invoke('change_password', {
        oldPassword,
        newPassword,
      });

      // 修改成功 - 清空表单并提示用户
      alert('密码修改成功！请使用新密码重新登录。');

      // 清空表单
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');

      // 跳转回设置页面
      navigate('/settings');
    } catch (err) {
      const errorMessage = err instanceof Error
        ? err.message
        : typeof err === 'string'
          ? err
          : '密码修改失败，请重试';
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const togglePasswordVisibility = (field: 'old' | 'new' | 'confirm') => {
    setShowPasswords(prev => ({ ...prev, [field]: !prev[field] }));
  };

  const strengthInfo = newPassword ? validatePasswordStrength(newPassword) : null;

  return (
    <div className="change-password-view">
      <div className="header">
        <button
          className="back-button"
          onClick={() => navigate('/settings')}
          aria-label="返回设置"
        >
          ← 返回
        </button>
        <h1>🔑 修改主密码</h1>
      </div>

      <div className="security-notice">
        <strong>⚠️ 重要提示：</strong>
        <p>修改密码后，请务必记住新密码。忘记密码将无法恢复加密文件。</p>
        <p>建议使用密码管理器保存密码。</p>
      </div>

      <form onSubmit={handleSubmit} className="password-form">
        {/* 当前密码 */}
        <div className="input-group">
          <label htmlFor="old-password">当前密码</label>
          <div className="password-field">
            <input
              id="old-password"
              type={showPasswords.old ? 'text' : 'password'}
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              disabled={isSubmitting}
              required
              autoComplete="current-password"
              aria-label="当前密码"
            />
            <button
              type="button"
              onClick={() => togglePasswordVisibility('old')}
              className="toggle-visibility"
              aria-label={showPasswords.old ? '隐藏密码' : '显示密码'}
            >
              {showPasswords.old ? '👁️' : '👁️‍🗨️'}
            </button>
          </div>
        </div>

        {/* 新密码 */}
        <div className="input-group">
          <label htmlFor="new-password">新密码</label>
          <div className="password-field">
            <input
              id="new-password"
              type={showPasswords.new ? 'text' : 'password'}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="至少8位，包含大小写、数字"
              disabled={isSubmitting}
              required
              autoComplete="new-password"
              aria-label="新密码"
              aria-describedby="password-strength"
            />
            <button
              type="button"
              onClick={() => togglePasswordVisibility('new')}
              className="toggle-visibility"
              aria-label={showPasswords.new ? '隐藏密码' : '显示密码'}
            >
              {showPasswords.new ? '👁️' : '👁️‍🗨️'}
            </button>
          </div>

          {/* 密码强度提示 */}
          {strengthInfo && (
            <div
              id="password-strength"
              className={`strength-indicator ${strengthInfo.valid ? 'strong' : 'weak'}`}
              role="status"
              aria-live="polite"
            >
              {strengthInfo.message}
            </div>
          )}
        </div>

        {/* 确认新密码 */}
        <div className="input-group">
          <label htmlFor="confirm-password">确认新密码</label>
          <div className="password-field">
            <input
              id="confirm-password"
              type={showPasswords.confirm ? 'text' : 'password'}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={isSubmitting}
              required
              autoComplete="new-password"
              aria-label="确认新密码"
            />
            <button
              type="button"
              onClick={() => togglePasswordVisibility('confirm')}
              className="toggle-visibility"
              aria-label={showPasswords.confirm ? '隐藏密码' : '显示密码'}
            >
              {showPasswords.confirm ? '👁️' : '👁️‍🗨️'}
            </button>
          </div>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="error-message" role="alert">
            {error}
          </div>
        )}

        {/* 按钮组 */}
        <div className="button-group">
          <button
            type="submit"
            className="submit-button"
            disabled={isSubmitting || !oldPassword || !newPassword || !confirmPassword}
          >
            {isSubmitting ? '修改中...' : '确认修改'}
          </button>

          <button
            type="button"
            className="cancel-button"
            onClick={() => navigate('/settings')}
            disabled={isSubmitting}
          >
            取消
          </button>
        </div>
      </form>

      <style>{`
        .change-password-view {
          max-width: 500px;
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

        .security-notice {
          padding: var(--space-4);
          background: var(--bg-warning);
          border-left: 4px solid var(--color-warning);
          border-radius: var(--radius-md);
          margin-bottom: var(--space-6);
        }

        .security-notice strong {
          display: block;
          margin-bottom: var(--space-2);
          color: var(--color-warning);
        }

        .security-notice p {
          margin: var(--space-1) 0;
          font-size: var(--text-sm);
          color: var(--text-secondary);
        }

        .password-form {
          display: flex;
          flex-direction: column;
          gap: var(--space-5);
        }

        .input-group {
          display: flex;
          flex-direction: column;
          gap: var(--space-2);
        }

        label {
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
          transition: border-color var(--duration-fast) var(--ease-out);
        }

        input:focus {
          outline: 2px solid var(--color-primary);
          outline-offset: 2px;
          border-color: var(--color-primary);
        }

        input:disabled {
          background: var(--bg-disabled);
          cursor: not-allowed;
          opacity: 0.6;
        }

        .toggle-visibility {
          position: absolute;
          right: var(--space-2);
          top: 50%;
          transform: translateY(-50%);
          padding: var(--space-2);
          background: none;
          border: none;
          font-size: var(--text-lg);
          cursor: pointer;
          transition: opacity var(--duration-fast) var(--ease-out);
        }

        .toggle-visibility:hover {
          opacity: 0.7;
        }

        .toggle-visibility:focus-visible {
          outline: 2px solid var(--color-primary);
          outline-offset: 2px;
          border-radius: var(--radius-sm);
        }

        .strength-indicator {
          padding: var(--space-2);
          border-radius: var(--radius-sm);
          font-size: var(--text-xs);
          font-weight: 500;
        }

        .strength-indicator.weak {
          background: var(--bg-error);
          color: var(--color-error);
        }

        .strength-indicator.strong {
          background: var(--bg-success);
          color: var(--color-success);
        }

        .error-message {
          padding: var(--space-3);
          background: var(--bg-error);
          color: var(--color-error);
          border-radius: var(--radius-md);
          font-size: var(--text-sm);
          border-left: 4px solid var(--color-error);
        }

        .button-group {
          display: flex;
          gap: var(--space-3);
          margin-top: var(--space-2);
        }

        .submit-button,
        .cancel-button {
          flex: 1;
          padding: var(--space-3) var(--space-4);
          border: none;
          border-radius: var(--radius-md);
          font-size: var(--text-sm);
          font-weight: 600;
          cursor: pointer;
          transition: background var(--duration-fast) var(--ease-out);
        }

        .submit-button {
          background: var(--color-primary);
          color: white;
        }

        .submit-button:hover:not(:disabled) {
          background: var(--color-primary-hover);
        }

        .submit-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .submit-button:focus-visible,
        .cancel-button:focus-visible {
          outline: 2px solid var(--color-primary);
          outline-offset: 2px;
        }

        .cancel-button {
          background: var(--bg-card);
          color: var(--text-primary);
          border: 1px solid var(--color-border);
        }

        .cancel-button:hover:not(:disabled) {
          background: var(--bg-hover);
        }

        /* 响应式设计 */
        @media (max-width: 768px) {
          .change-password-view {
            padding: var(--space-4);
          }

          .button-group {
            flex-direction: column-reverse;
          }
        }

        /* 减少动画（可访问性） */
        @media (prefers-reduced-motion: reduce) {
          input,
          .submit-button,
          .cancel-button,
          .toggle-visibility,
          .back-button {
            transition: none;
          }
        }
      `}</style>
    </div>
  );
}
