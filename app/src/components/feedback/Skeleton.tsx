/**
 * Skeleton 占位符组件
 * 用于加载状态
 */

import './Skeleton.css';

export interface SkeletonProps {
  /** 变体类型 */
  variant?: 'text' | 'circle' | 'rect';
  /** 宽度 */
  width?: string | number;
  /** 高度 */
  height?: string | number;
  /** 自定义类名 */
  className?: string;
}

/**
 * Skeleton 占位符组件
 *
 * @example
 * ```tsx
 * // 文本骨架
 * <Skeleton variant="text" width="80%" />
 *
 * // 圆形骨架 (头像)
 * <Skeleton variant="circle" width={40} height={40} />
 *
 * // 矩形骨架 (卡片)
 * <Skeleton variant="rect" width="100%" height={120} />
 * ```
 */
export function Skeleton({
  variant = 'text',
  width,
  height,
  className = '',
}: SkeletonProps) {
  const style: React.CSSProperties = {};

  if (width !== undefined) {
    style.width = typeof width === 'number' ? `${width}px` : width;
  }

  if (height !== undefined) {
    style.height = typeof height === 'number' ? `${height}px` : height;
  }

  return (
    <div
      className={`skeleton skeleton--${variant} ${className}`}
      style={style}
      aria-busy="true"
      aria-label="加载中"
    />
  );
}

/**
 * 文件列表骨架组件
 *
 * @example
 * ```tsx
 * {isLoading ? <FileListSkeleton count={5} /> : <FileList files={files} />}
 * ```
 */
export interface FileListSkeletonProps {
  /** 显示数量 */
  count?: number;
}

export function FileListSkeleton({ count = 3 }: FileListSkeletonProps) {
  return (
    <div className="file-list-skeleton">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="file-list-skeleton__item">
          <Skeleton variant="circle" width={40} height={40} />
          <div className="file-list-skeleton__content">
            <Skeleton variant="text" width="60%" height={16} />
            <Skeleton variant="text" width="40%" height={14} />
          </div>
        </div>
      ))}
    </div>
  );
}
