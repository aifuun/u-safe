/**
 * Spinner 加载组件
 * CSS 动画实现
 */

import './Spinner.css';

export interface SpinnerProps {
  /** 大小 */
  size?: 'sm' | 'md' | 'lg';
  /** 自定义类名 */
  className?: string;
  /** 文字说明 */
  label?: string;
}

/**
 * Spinner 加载组件
 *
 * @example
 * ```tsx
 * <Spinner size="md" label="加载中..." />
 * ```
 */
export function Spinner({ size = 'md', className = '', label }: SpinnerProps) {
  return (
    <div className={`spinner spinner--${size} ${className}`} role="status">
      <div className="spinner__circle" aria-hidden="true" />
      {label && <span className="spinner__label">{label}</span>}
      <span className="sr-only">{label || '加载中...'}</span>
    </div>
  );
}
