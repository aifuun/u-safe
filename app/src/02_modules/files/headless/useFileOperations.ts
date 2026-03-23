/**
 * 文件操作 Hook
 *
 * 提供文件删除、重命名操作，并集成 Toast 反馈
 */

import { useState } from 'react';
import { deleteFile, renameFile } from './fileOperations';
import { logger } from '@/kernel/services/logService';

export interface UseFileOperationsReturn {
  /** 是否正在执行操作 */
  isLoading: boolean;
  /** 错误信息 */
  error: string | null;
  /** 删除文件 */
  handleDelete: (fileId: number) => Promise<boolean>;
  /** 重命名文件 */
  handleRename: (fileId: number, newName: string) => Promise<boolean>;
  /** 清除错误 */
  clearError: () => void;
}

/**
 * 文件操作 Hook
 *
 * @returns UseFileOperationsReturn
 *
 * @example
 * ```tsx
 * const { isLoading, error, handleDelete, handleRename } = useFileOperations();
 *
 * // 删除文件
 * const success = await handleDelete(fileId);
 * if (success) {
 *   // 刷新文件列表
 * }
 *
 * // 重命名文件
 * const success = await handleRename(fileId, "new-name.txt");
 * if (success) {
 *   // 刷新文件列表
 * }
 * ```
 */
export function useFileOperations(): UseFileOperationsReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * 删除文件
   */
  const handleDelete = async (fileId: number): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await deleteFile(fileId);

      if (response.success) {
        logger.info('useFileOperations:delete:success', { fileId });
        return true;
      } else {
        const errorMsg = response.message || '删除失败';
        setError(errorMsg);
        logger.error('useFileOperations:delete:failed', { fileId, error: errorMsg });
        return false;
      }
    } catch (err) {
      const errorMsg = typeof err === 'string' ? err : '删除文件失败';
      setError(errorMsg);
      logger.error('useFileOperations:delete:error', { fileId, error: err });
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * 重命名文件
   */
  const handleRename = async (fileId: number, newName: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await renameFile(fileId, newName);

      if (response.success) {
        logger.info('useFileOperations:rename:success', { fileId, newName });
        return true;
      } else {
        const errorMsg = response.message || '重命名失败';
        setError(errorMsg);
        logger.error('useFileOperations:rename:failed', { fileId, newName, error: errorMsg });
        return false;
      }
    } catch (err) {
      const errorMsg = typeof err === 'string' ? err : '重命名文件失败';
      setError(errorMsg);
      logger.error('useFileOperations:rename:error', { fileId, newName, error: err });
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * 清除错误
   */
  const clearError = () => {
    setError(null);
  };

  return {
    isLoading,
    error,
    handleDelete,
    handleRename,
    clearError,
  };
}
