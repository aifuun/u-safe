/**
 * 拖拽区域组件
 * 支持多文件拖拽导入
 */

import { ReactNode } from 'react';
import { useFileDrop } from '@/modules/file';
import type { UseFileDropOptions } from '@/modules/file';
import './DragDropZone.css';

export interface DragDropZoneProps extends UseFileDropOptions {
  children?: ReactNode;
  className?: string;
}

/**
 * 拖拽区域组件
 *
 * @example
 * ```tsx
 * <DragDropZone
 *   onFilesAccepted={(files) => handleFiles(files)}
 *   onValidationError={(errors) => showErrors(errors)}
 * >
 *   <p>拖拽文件到这里</p>
 * </DragDropZone>
 * ```
 */
export function DragDropZone({
  children,
  className = '',
  ...dropOptions
}: DragDropZoneProps) {
  const { isDragActive, ...dragHandlers } = useFileDrop(dropOptions);

  return (
    <div
      {...dragHandlers}
      className={`drag-drop-zone ${isDragActive ? 'drag-drop-zone--active' : ''} ${className}`}
      role="button"
      tabIndex={0}
      aria-label="拖拽文件到这里导入"
    >
      <div className="drag-drop-zone__content">
        {isDragActive ? (
          <div className="drag-drop-zone__overlay">
            <div className="drag-drop-zone__icon">📁</div>
            <p className="drag-drop-zone__text">释放以导入文件</p>
          </div>
        ) : (
          children || (
            <div className="drag-drop-zone__placeholder">
              <div className="drag-drop-zone__icon">📂</div>
              <p className="drag-drop-zone__text">拖拽文件到这里</p>
              <p className="drag-drop-zone__hint">
                支持常见文档、图片、视频格式
              </p>
              <p className="drag-drop-zone__hint">
                单文件最大 5GB，一次最多 100 个文件
              </p>
            </div>
          )
        )}
      </div>
    </div>
  );
}
