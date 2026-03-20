/**
 * 进度条组件
 * 基于 docs/design/FEEDBACK.md 规范
 */

import './ProgressBar.css';

export interface ProgressBarProps {
  /** 进度百分比 (0-100) */
  percent: number;
  /** 状态文字 */
  status?: string;
  /** 是否显示百分比 */
  showPercent?: boolean;
  /** 自定义类名 */
  className?: string;
}

/**
 * 进度条组件
 *
 * @example
 * ```tsx
 * <ProgressBar
 *   percent={45}
 *   status="正在加密..."
 *   showPercent
 * />
 * ```
 */
export function ProgressBar({
  percent,
  status,
  showPercent = true,
  className = '',
}: ProgressBarProps) {
  // 确保百分比在 0-100 范围内
  const clampedPercent = Math.min(100, Math.max(0, percent));

  return (
    <div className={`progress-bar ${className}`}>
      {/* 状态文字和百分比 */}
      <div className="progress-bar__header">
        {status && <span className="progress-bar__status">{status}</span>}
        {showPercent && (
          <span className="progress-bar__percent">{clampedPercent.toFixed(1)}%</span>
        )}
      </div>

      {/* 进度条轨道 */}
      <div
        className="progress-bar__track"
        role="progressbar"
        aria-valuenow={clampedPercent}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={status || `进度 ${clampedPercent}%`}
      >
        {/* 进度条填充 */}
        <div
          className="progress-bar__fill"
          style={{ width: `${clampedPercent}%` }}
        />
      </div>
    </div>
  );
}
