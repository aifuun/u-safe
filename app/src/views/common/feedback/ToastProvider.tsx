/**
 * Toast Provider
 * 管理全局 Toast 状态
 */

import { createContext, useState, useCallback, ReactNode } from 'react';
import { Toast, ToastItem, ToastType } from './Toast';
import './Toast.css';

const MAX_TOASTS = 3; // 最大同时显示数量

export interface ToastContextValue {
  addToast: (type: ToastType, message: string, duration?: number) => void;
  success: (message: string, duration?: number) => void;
  error: (message: string, duration?: number) => void;
  warning: (message: string, duration?: number) => void;
  info: (message: string, duration?: number) => void;
}

export const ToastContext = createContext<ToastContextValue | null>(null);

export interface ToastProviderProps {
  children: ReactNode;
}

/**
 * Toast Provider 组件
 *
 * @example
 * ```tsx
 * // 在 App 根组件中包裹
 * <ToastProvider>
 *   <App />
 * </ToastProvider>
 *
 * // 在子组件中使用
 * const toast = useToast();
 * toast.success('操作成功！');
 * toast.error('操作失败！');
 * ```
 */
export function ToastProvider({ children }: ToastProviderProps) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  // 添加 Toast
  const addToast = useCallback((type: ToastType, message: string, duration?: number) => {
    const id = Date.now();
    const newToast: Toast = { id, type, message, duration };

    setToasts((prev) => {
      // 如果超过最大数量，移除最旧的
      const updated = prev.length >= MAX_TOASTS ? prev.slice(1) : prev;
      return [...updated, newToast];
    });
  }, []);

  // 移除 Toast
  const removeToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  // 便捷方法
  const success = useCallback(
    (message: string, duration?: number) => addToast('success', message, duration),
    [addToast]
  );

  const error = useCallback(
    (message: string, duration?: number) => addToast('error', message, duration),
    [addToast]
  );

  const warning = useCallback(
    (message: string, duration?: number) => addToast('warning', message, duration),
    [addToast]
  );

  const info = useCallback(
    (message: string, duration?: number) => addToast('info', message, duration),
    [addToast]
  );

  const value: ToastContextValue = {
    addToast,
    success,
    error,
    warning,
    info,
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="toast-container">
        {toasts.map((toast) => (
          <ToastItem key={toast.id} {...toast} onClose={removeToast} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}
