import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
}

/**
 * Loading 加载指示器
 *
 * 使用场景：
 * - 密码验证中
 * - 文件扫描中
 * - IPC 调用等待
 */
export function LoadingSpinner({ size = 'md', message }: LoadingSpinnerProps) {
  const sizeClass = `spinner--${size}`;

  return (
    <div className="loading-spinner" role="status" aria-live="polite">
      <div className={`spinner ${sizeClass}`}></div>
      {message && <p className="spinner-message">{message}</p>}

      <style>{`
        .loading-spinner {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: var(--space-2);
        }

        .spinner {
          border: 3px solid var(--color-border);
          border-top-color: var(--color-primary);
          border-radius: var(--radius-full);
          animation: spin 1s linear infinite;
        }

        .spinner--sm {
          width: 16px;
          height: 16px;
          border-width: 2px;
        }

        .spinner--md {
          width: 32px;
          height: 32px;
        }

        .spinner--lg {
          width: 48px;
          height: 48px;
          border-width: 4px;
        }

        .spinner-message {
          margin: 0;
          font-size: var(--text-sm);
          color: var(--text-secondary);
        }

        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .spinner {
            animation: none;
            border-top-color: var(--color-border);
            opacity: 0.6;
          }
        }
      `}</style>
    </div>
  );
}
