/**
 * Toast 提示组件
 * 基于 docs/design/FEEDBACK.md 规范
 */

import { useEffect } from 'react';
import './Toast.css';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: number;
  type: ToastType;
  message: string;
  duration?: number; // 持续时间 (ms)
}

export interface ToastItemProps extends Toast {
  onClose: (id: number) => void;
}

/**
 * Toast 图标映射
 */
const TOAST_ICONS: Record<ToastType, string> = {
  success: '✅',
  error: '❌',
  warning: '⚠️',
  info: 'ℹ️',
};

/**
 * Toast 默认持续时间 (ms)
 */
const DEFAULT_DURATIONS: Record<ToastType, number> = {
  success: 3000,
  error: 5000,
  warning: 4000,
  info: 3000,
};

/**
 * 单个 Toast 项组件
 */
export function ToastItem({ id, type, message, duration, onClose }: ToastItemProps) {
  useEffect(() => {
    const timer = setTimeout(
      () => onClose(id),
      duration || DEFAULT_DURATIONS[type]
    );

    return () => clearTimeout(timer);
  }, [id, type, duration, onClose]);

  return (
    <div
      className={`toast toast--${type}`}
      role="alert"
      aria-live="polite"
    >
      <div className="toast__icon">{TOAST_ICONS[type]}</div>
      <div className="toast__message">{message}</div>
      <button
        className="toast__close"
        onClick={() => onClose(id)}
        aria-label="关闭提示"
      >
        ×
      </button>
    </div>
  );
}
