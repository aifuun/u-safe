import type { FileStatusType } from '../types/FileStatus';

/**
 * 文件实体
 * 表示系统中的文件及其元数据
 *
 * 这是纯数据类型，不包含 IO 操作或副作用
 */
export interface File {
  /** 文件唯一标识符 */
  id: string;

  /** 文件名（包含扩展名） */
  name: string;

  /** 文件大小（字节） */
  size: number;

  /** 文件类型（MIME type） */
  type: string;

  /** 文件状态 */
  status: FileStatusType;

  /** 文件路径（在 U 盘中的相对路径） */
  path: string;

  /** 创建时间（ISO 8601 字符串） */
  createdAt: string;

  /** 最后修改时间（ISO 8601 字符串） */
  updatedAt: string;

  /** 关联的标签 ID 列表 */
  tagIds?: string[];

  /** 加密元数据（可选，仅加密文件有） */
  encryptionMeta?: EncryptionMetadata;
}

/**
 * 加密元数据
 * 存储加密相关的信息
 */
export interface EncryptionMetadata {
  /** 加密算法 */
  algorithm: 'AES-256-GCM';

  /** 加密块大小（字节） */
  chunkSize: number;

  /** 加密时间 */
  encryptedAt: string;

  /** 原始文件哈希（用于完整性校验） */
  originalHash?: string;
}

/**
 * 文件创建参数
 * 用于创建新文件实体的最小必需字段
 */
export interface CreateFileParams {
  name: string;
  size: number;
  type: string;
  path: string;
}
