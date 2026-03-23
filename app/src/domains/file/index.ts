/**
 * File Domain - Domains Layer (Layer 1)
 *
 * 纯业务逻辑层，不依赖 IO 或框架
 * 使用路径别名: @/domains/file
 */

// ========== 实体 ==========
export type {
  File,
  EncryptionMetadata,
  CreateFileParams,
} from './entities/File';

// ========== 类型 ==========
export {
  FileStatus,
  type FileStatusType,
  isValidFileStatus,
  getFileStatusLabel,
} from './types/FileStatus';

// ========== 业务规则 ==========
export {
  // 常量
  FILE_SIZE_LIMITS,
  ALLOWED_EXTENSIONS,

  // 类型
  type FileValidationError,
  type FileValidationWarning,
  type FileValidationResult,
  type BatchFileValidationResult,

  // 工具函数
  formatFileSize,
  getFileExtension,
  isFileTypeAllowed,

  // 验证函数
  validateFileSize,
  validateFileType,
  validateFile,
  validateFiles,
} from './rules/validation';
