/**
 * useToast Hook
 * 在组件中使用 Toast
 */

import { useContext } from 'react';
import { ToastContext, ToastContextValue } from './ToastProvider';

/**
 * 使用 Toast
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const toast = useToast();
 *
 *   const handleSave = async () => {
 *     try {
 *       await saveData();
 *       toast.success('保存成功！');
 *     } catch (error) {
 *       toast.error('保存失败，请重试');
 *     }
 *   };
 *
 *   return <button onClick={handleSave}>保存</button>;
 * }
 * ```
 */
export function useToast(): ToastContextValue {
  const context = useContext(ToastContext);

  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }

  return context;
}
