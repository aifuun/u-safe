/**
 * 文件拖拽 Hook
 * 处理拖拽文件导入逻辑
 */

import { useState, useCallback, DragEvent } from 'react';
import { validateFiles, FileValidationResult } from './fileValidator';

export interface UseFileDropOptions {
  onFilesAccepted?: (files: File[]) => void;
  onValidationError?: (errors: FileValidationResult['errors']) => void;
  onValidationWarning?: (warnings: FileValidationResult['warnings']) => void;
  maxFiles?: number; // 最大文件数量，默认 100
}

export interface UseFileDropReturn {
  isDragActive: boolean;
  onDragEnter: (e: DragEvent<HTMLElement>) => void;
  onDragOver: (e: DragEvent<HTMLElement>) => void;
  onDragLeave: (e: DragEvent<HTMLElement>) => void;
  onDrop: (e: DragEvent<HTMLElement>) => void;
}

/**
 * 文件拖拽 Hook
 *
 * @example
 * ```tsx
 * const { isDragActive, ...dragHandlers } = useFileDrop({
 *   onFilesAccepted: (files) => console.log('Accepted:', files),
 *   onValidationError: (errors) => console.error('Errors:', errors),
 * });
 *
 * return (
 *   <div {...dragHandlers} className={isDragActive ? 'drag-active' : ''}>
 *     拖拽文件到这里
 *   </div>
 * );
 * ```
 */
export function useFileDrop(options: UseFileDropOptions = {}): UseFileDropReturn {
  const {
    onFilesAccepted,
    onValidationError,
    onValidationWarning,
    maxFiles = 100,
  } = options;

  const [isDragActive, setIsDragActive] = useState(false);

  // 处理拖拽进入
  const onDragEnter = useCallback((e: DragEvent<HTMLElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(true);
  }, []);

  // 处理拖拽悬停
  const onDragOver = useCallback((e: DragEvent<HTMLElement>) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  // 处理拖拽离开
  const onDragLeave = useCallback((e: DragEvent<HTMLElement>) => {
    e.preventDefault();
    e.stopPropagation();

    // 只有当拖拽离开容器本身时才取消激活状态
    // （防止拖拽到子元素时触发）
    if (e.currentTarget === e.target) {
      setIsDragActive(false);
    }
  }, []);

  // 处理文件放下
  const onDrop = useCallback(
    (e: DragEvent<HTMLElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragActive(false);

      // 获取拖拽的文件
      const droppedFiles = Array.from(e.dataTransfer.files);

      // 检查文件数量限制
      if (droppedFiles.length > maxFiles) {
        onValidationError?.([
          {
            file: droppedFiles[0], // 使用第一个文件作为占位
            reason: 'unknown',
            message: `一次最多只能导入 ${maxFiles} 个文件，您拖拽了 ${droppedFiles.length} 个文件`,
          },
        ]);
        return;
      }

      // 验证文件
      const validationResult = validateFiles(droppedFiles);

      // 处理验证结果
      if (validationResult.errors.length > 0) {
        onValidationError?.(validationResult.errors);
      }

      if (validationResult.warnings.length > 0) {
        onValidationWarning?.(validationResult.warnings);
      }

      // 如果有有效文件，调用回调
      if (validationResult.valid.length > 0) {
        onFilesAccepted?.(validationResult.valid);
      }
    },
    [maxFiles, onFilesAccepted, onValidationError, onValidationWarning]
  );

  return {
    isDragActive,
    onDragEnter,
    onDragOver,
    onDragLeave,
    onDrop,
  };
}
