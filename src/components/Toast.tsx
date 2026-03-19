import { useEffect } from 'react';
import './Toast.css';

export interface ToastProps {
  message: string;
  type: 'success' | 'error' | 'info';
  onClose: () => void;
  duration?: number; // 持续时间（毫秒），默认3000
}

/**
 * Toast 通知组件
 * 用于显示操作反馈（成功、错误、信息）
 */
export function Toast({ message, type, onClose, duration = 3000 }: ToastProps) {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [onClose, duration]);

  const icons = {
    success: '✅',
    error: '❌',
    info: 'ℹ️',
  };

  return (
    <div
      className={`toast toast--${type}`}
      role="alert"
      aria-live="polite"
    >
      <span className="toast__icon">{icons[type]}</span>
      <span className="toast__message">{message}</span>
      <button
        className="toast__close"
        onClick={onClose}
        aria-label="关闭通知"
      >
        ✕
      </button>
    </div>
  );
}

/**
 * Toast 容器组件
 * 用于在页面右上角显示多个 Toast
 */
export interface ToastContainerProps {
  toasts: Array<{
    id: string;
    message: string;
    type: 'success' | 'error' | 'info';
  }>;
  onRemove: (id: string) => void;
}

export function ToastContainer({ toasts, onRemove }: ToastContainerProps) {
  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          onClose={() => onRemove(toast.id)}
        />
      ))}
    </div>
  );
}
