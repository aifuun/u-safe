/**
 * 文件操作服务
 *
 * 提供文件删除、重命名等操作的 IPC 封装
 * 参考: .claude/rules/desktop/tauri-ipc.md
 */

import { invoke } from '@tauri-apps/api/core';

/**
 * 文件删除响应
 */
export interface DeleteFileResponse {
  /** 是否成功 */
  success: boolean;
  /** 删除的文件 ID */
  file_id: number;
  /** 消息 */
  message: string;
}

/**
 * 文件重命名响应
 */
export interface RenameFileResponse {
  /** 是否成功 */
  success: boolean;
  /** 文件 ID */
  file_id: number;
  /** 新文件名 */
  new_name: string;
  /** 消息 */
  message: string;
}

/**
 * 删除文件
 *
 * @param fileId - 文件 ID
 * @returns Promise<DeleteFileResponse>
 * @throws {string} 错误信息
 */
export async function deleteFile(fileId: number): Promise<DeleteFileResponse> {
  console.info('[fileOperations:delete:start]', { fileId });

  try {
    const response = await invoke<DeleteFileResponse>('delete_file', {
      fileId,
    });

    console.info('[fileOperations:delete:done]', { fileId, response });
    return response;
  } catch (error) {
    console.error('[fileOperations:delete:failed]', { fileId, error });
    throw error;
  }
}

/**
 * 重命名文件
 *
 * @param fileId - 文件 ID
 * @param newName - 新文件名
 * @returns Promise<RenameFileResponse>
 * @throws {string} 错误信息
 */
export async function renameFile(
  fileId: number,
  newName: string
): Promise<RenameFileResponse> {
  console.info('[fileOperations:rename:start]', { fileId, newName });

  try {
    const response = await invoke<RenameFileResponse>('rename_file', {
      fileId,
      newName,
    });

    console.info('[fileOperations:rename:done]', { fileId, newName, response });
    return response;
  } catch (error) {
    console.error('[fileOperations:rename:failed]', { fileId, newName, error });
    throw error;
  }
}
