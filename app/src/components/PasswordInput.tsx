import React, { useState } from 'react';

interface PasswordInputProps {
  onSubmit: (password: string) => void;
  mode: 'set' | 'verify'; // 设置密码 or 验证密码
}

/**
 * 密码输入组件
 *
 * Features:
 * - 密码强度验证（长度 >= 8，包含大小写+数字）
 * - 确认密码输入（设置模式）
 * - 实时强度反馈
 * - 错误提示
 */
export function PasswordInput({ onSubmit, mode }: PasswordInputProps) {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // 密码强度检查
  const validatePasswordStrength = (pwd: string): { valid: boolean; message: string } => {
    if (pwd.length < 8) {
      return { valid: false, message: '密码长度至少 8 个字符' };
    }

    const hasLowerCase = /[a-z]/.test(pwd);
    const hasUpperCase = /[A-Z]/.test(pwd);
    const hasNumber = /[0-9]/.test(pwd);

    if (!hasLowerCase) {
      return { valid: false, message: '密码需要包含小写字母' };
    }

    if (!hasUpperCase) {
      return { valid: false, message: '密码需要包含大写字母' };
    }

    if (!hasNumber) {
      return { valid: false, message: '密码需要包含数字' };
    }

    return { valid: true, message: '密码强度：强' };
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // 验证模式：直接提交
    if (mode === 'verify') {
      if (!password) {
        setError('请输入密码');
        return;
      }
      onSubmit(password);
      return;
    }

    // 设置模式：检查密码强度和确认密码
    const validation = validatePasswordStrength(password);
    if (!validation.valid) {
      setError(validation.message);
      return;
    }

    if (password !== confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    onSubmit(password);
  };

  const strengthInfo = password ? validatePasswordStrength(password) : null;

  return (
    <div className="password-input-container">
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label htmlFor="password">
            {mode === 'set' ? '设置主密码' : '输入主密码'}
          </label>
          <div className="password-field">
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={mode === 'set' ? '至少8位，包含大小写字母和数字' : '请输入密码'}
              autoComplete={mode === 'set' ? 'new-password' : 'current-password'}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="toggle-visibility"
            >
              {showPassword ? '隐藏' : '显示'}
            </button>
          </div>

          {/* 密码强度提示（仅设置模式） */}
          {mode === 'set' && strengthInfo && (
            <div
              className={`strength-indicator ${
                strengthInfo.valid ? 'strong' : 'weak'
              }`}
            >
              {strengthInfo.message}
            </div>
          )}
        </div>

        {/* 确认密码（仅设置模式） */}
        {mode === 'set' && (
          <div className="input-group">
            <label htmlFor="confirm-password">确认密码</label>
            <input
              id="confirm-password"
              type={showPassword ? 'text' : 'password'}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="再次输入密码"
              autoComplete="new-password"
            />
          </div>
        )}

        {/* 错误提示 */}
        {error && <div className="error-message">{error}</div>}

        {/* 提交按钮 */}
        <button type="submit" className="submit-button">
          {mode === 'set' ? '设置密码' : '解锁'}
        </button>
      </form>

      <style>{`
        .password-input-container {
          max-width: 400px;
          margin: 0 auto;
          padding: var(--space-6);
        }

        .input-group {
          margin-bottom: var(--space-4);
        }

        label {
          display: block;
          margin-bottom: var(--space-2);
          font-weight: 600;
          color: var(--text-primary);
        }

        .password-field {
          position: relative;
        }

        input {
          width: 100%;
          padding: var(--space-3);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          font-size: var(--text-sm);
        }

        input:focus {
          outline: 2px solid var(--color-primary);
          outline-offset: 2px;
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
        }

        .strength-indicator {
          margin-top: var(--space-2);
          padding: var(--space-2);
          border-radius: var(--radius-sm);
          font-size: var(--text-xs);
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
          margin-top: var(--space-2);
          padding: var(--space-3);
          background: var(--bg-error);
          color: var(--color-error);
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
          transition: background var(--duration-fast) var(--ease-out);
        }

        .submit-button:hover {
          background: var(--color-primary-hover);
        }

        .submit-button:focus-visible {
          outline: 2px solid var(--color-primary);
          outline-offset: 2px;
        }
      `}</style>
    </div>
  );
}
