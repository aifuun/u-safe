import React, { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useNavigate } from 'react-router-dom';

interface PasswordStrengthResult {
  valid: boolean;
  message: string;
  strength: 'weak' | 'medium' | 'strong';
}

/**
 * 首次设置主密码界面
 *
 * Features:
 * - 密码强度验证（≥12 字符，大小写+数字+特殊字符）
 * - 确认密码匹配验证
 * - IPC 调用 derive_master_key(password) 保存到 config 表
 * - 成功后跳转到文件管理界面
 */
export function SetupPasswordView() {
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  /**
   * 密码强度检查（MVP 要求：≥12 字符，大小写+数字+特殊字符）
   */
  const validatePasswordStrength = (pwd: string): PasswordStrengthResult => {
    if (pwd.length < 12) {
      return { valid: false, message: '密码长度至少 12 个字符', strength: 'weak' };
    }

    const hasLowerCase = /[a-z]/.test(pwd);
    const hasUpperCase = /[A-Z]/.test(pwd);
    const hasNumber = /[0-9]/.test(pwd);
    const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pwd);

    const missingRequirements: string[] = [];
    if (!hasLowerCase) missingRequirements.push('小写字母');
    if (!hasUpperCase) missingRequirements.push('大写字母');
    if (!hasNumber) missingRequirements.push('数字');
    if (!hasSpecialChar) missingRequirements.push('特殊字符');

    if (missingRequirements.length > 0) {
      return {
        valid: false,
        message: `密码需要包含：${missingRequirements.join('、')}`,
        strength: 'weak',
      };
    }

    // 所有要求都满足
    const strength = pwd.length >= 16 ? 'strong' : 'medium';
    return {
      valid: true,
      message: strength === 'strong' ? '密码强度：强' : '密码强度：中等',
      strength,
    };
  };

  /**
   * 提交密码设置
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // 前端验证
    const validation = validatePasswordStrength(password);
    if (!validation.valid) {
      setError(validation.message);
      return;
    }

    if (password !== confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    // 调用 IPC 保存密码
    setIsSubmitting(true);
    try {
      await invoke('derive_master_key', { password });
      // 成功：跳转到文件管理界面
      navigate('/files');
    } catch (err) {
      setError(err as string || '密码设置失败，请重试');
    } finally {
      setIsSubmitting(false);
    }
  };

  const strengthInfo = password ? validatePasswordStrength(password) : null;

  return (
    <div className="setup-password-view">
      <div className="setup-card">
        <h1>🔐 设置主密码</h1>
        <p className="subtitle">
          主密码用于保护您的文件加密密钥，请妥善保管。一旦忘记将无法恢复。
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
                placeholder="至少12位，包含大小写、数字、特殊字符"
                autoComplete="new-password"
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

            {/* 密码强度提示 */}
            {strengthInfo && (
              <div
                className={`strength-indicator strength-${strengthInfo.strength}`}
                role="status"
                aria-live="polite"
              >
                {strengthInfo.message}
              </div>
            )}
          </div>

          {/* 确认密码 */}
          <div className="input-group">
            <label htmlFor="confirm-password">确认密码</label>
            <input
              id="confirm-password"
              type={showPassword ? 'text' : 'password'}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="再次输入密码"
              autoComplete="new-password"
              disabled={isSubmitting}
            />
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
            disabled={isSubmitting || !password || !confirmPassword}
          >
            {isSubmitting ? '设置中...' : '设置密码并开始使用'}
          </button>
        </form>

        {/* 密码要求说明 */}
        <div className="password-requirements">
          <h3>密码要求：</h3>
          <ul>
            <li>至少 12 个字符</li>
            <li>包含大写字母（A-Z）</li>
            <li>包含小写字母（a-z）</li>
            <li>包含数字（0-9）</li>
            <li>包含特殊字符（!@#$%^&*等）</li>
          </ul>
        </div>
      </div>

      <style>{`
        .setup-password-view {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--bg-app);
          padding: var(--space-4);
        }

        .setup-card {
          max-width: 480px;
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

        .strength-indicator {
          margin-top: var(--space-2);
          padding: var(--space-2) var(--space-3);
          border-radius: var(--radius-sm);
          font-size: var(--text-xs);
          font-weight: 500;
        }

        .strength-indicator.strength-weak {
          background: rgba(239, 68, 68, 0.1);
          color: var(--color-error);
          border: 1px solid rgba(239, 68, 68, 0.2);
        }

        .strength-indicator.strength-medium {
          background: rgba(251, 191, 36, 0.1);
          color: var(--color-warning);
          border: 1px solid rgba(251, 191, 36, 0.2);
        }

        .strength-indicator.strength-strong {
          background: rgba(16, 185, 129, 0.1);
          color: var(--color-success);
          border: 1px solid rgba(16, 185, 129, 0.2);
        }

        .error-message {
          margin-bottom: var(--space-4);
          padding: var(--space-3);
          background: rgba(239, 68, 68, 0.1);
          color: var(--color-error);
          border: 1px solid rgba(239, 68, 68, 0.2);
          border-radius: var(--radius-md);
          font-size: var(--text-sm);
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

        .password-requirements {
          margin-top: var(--space-6);
          padding-top: var(--space-4);
          border-top: 1px solid var(--color-border);
        }

        .password-requirements h3 {
          margin: 0 0 var(--space-2) 0;
          font-size: var(--text-sm);
          font-weight: 600;
          color: var(--text-secondary);
        }

        .password-requirements ul {
          margin: 0;
          padding-left: var(--space-5);
          font-size: var(--text-xs);
          color: var(--text-secondary);
          line-height: 1.8;
        }

        .password-requirements li {
          margin: var(--space-1) 0;
        }

        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {
          .submit-button,
          input {
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
