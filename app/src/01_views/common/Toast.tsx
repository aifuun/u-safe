import React, { useEffect } from 'react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastProps {
  type: ToastType;
  message: string;
  onClose: () => void;
  duration?: number; // ms, 0 = 不自动关闭
}

/**
 * Toast 通知组件
 *
 * 使用场景：
 * - 操作成功提示
 * - 错误提示
 * - 警告提示
 */
export function Toast({ type, message, onClose, duration = 3000 }: ToastProps) {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
    return undefined;
  }, [duration, onClose]);

  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️',
  };

  return (
    <div className={`toast toast--${type}`} role="alert">
      <span className="toast-icon">{icons[type]}</span>
      <span className="toast-message">{message}</span>
      <button className="toast-close" onClick={onClose} aria-label="关闭">
        ✕
      </button>

      <style>{`
        .toast {
          display: flex;
          align-items: center;
          gap: var(--space-2);
          padding: var(--space-3) var(--space-4);
          background: var(--bg-card);
          border-radius: var(--radius-md);
          box-shadow: var(--shadow-2);
          border-left: 4px solid;
          animation: slideIn 0.3s var(--ease-out);
        }

        .toast--success {
          border-left-color: var(--color-success);
        }

        .toast--error {
          border-left-color: var(--color-error);
        }

        .toast--warning {
          border-left-color: var(--color-warning);
        }

        .toast--info {
          border-left-color: var(--color-primary);
        }

        .toast-icon {
          font-size: var(--text-lg);
          flex-shrink: 0;
        }

        .toast-message {
          flex: 1;
          font-size: var(--text-sm);
          color: var(--text-primary);
        }

        .toast-close {
          padding: var(--space-1);
          background: none;
          border: none;
          color: var(--text-secondary);
          cursor: pointer;
          font-size: var(--text-lg);
          line-height: 1;
          flex-shrink: 0;
        }

        .toast-close:hover {
          color: var(--text-primary);
        }

        @keyframes slideIn {
          from {
            transform: translateY(-20px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .toast {
            animation: none;
          }
        }
      `}</style>
    </div>
  );
}

/**
 * Toast 容器组件（固定在右上角）
 */
export function ToastContainer({ children }: { children: React.ReactNode }) {
  return (
    <div className="toast-container">
      {children}

      <style>{`
        .toast-container {
          position: fixed;
          top: var(--space-4);
          right: var(--space-4);
          z-index: 9999;
          display: flex;
          flex-direction: column;
          gap: var(--space-2);
          max-width: 400px;
        }

        @media (max-width: 768px) {
          .toast-container {
            left: var(--space-4);
            right: var(--space-4);
            max-width: none;
          }
        }
      `}</style>
    </div>
  );
}
