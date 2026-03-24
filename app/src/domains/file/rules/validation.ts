/**
 * 文件验证业务规则
 * 纯函数，无 IO 依赖
 */

// ========== 常量 ==========

/** 文件大小限制（字节） */
export const FILE_SIZE_LIMITS = {
  /** 2GB - 显示警告 */
  WARNING: 2 * 1024 * 1024 * 1024,
  /** 5GB - 阻止上传 */
  MAX: 5 * 1024 * 1024 * 1024,
} as const;

/** 支持的文件扩展名白名单 */
export const ALLOWED_EXTENSIONS = [
  // 图片
  '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
  // 文档
  '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
  '.txt', '.md', '.rtf', '.odt', '.ods', '.odp',
  // 视频
  '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm',
  // 音频
  '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a',
  // 压缩包
  '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
  // 其他
  '.json', '.xml', '.csv', '.log',
] as const;

// ========== 类型定义 ==========

export interface FileValidationError {
  fileName: string;
  fileSize: number;
  reason: 'type' | 'size' | 'unknown';
  message: string;
}

export interface FileValidationWarning {
  fileName: string;
  fileSize: number;
  reason: 'large';
  message: string;
}

export interface FileValidationResult {
  valid: boolean;
  warning?: FileValidationWarning;
  error?: FileValidationError;
}

export interface BatchFileValidationResult {
  validFiles: string[];
  warnings: FileValidationWarning[];
  errors: FileValidationError[];
}

// ========== 工具函数 ==========

/**
 * 格式化文件大小为人类可读格式
 * @example formatFileSize(1024) => "1.00 KB"
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
}

/**
 * 提取文件扩展名
 * @example getFileExtension("document.pdf") => ".pdf"
 */
export function getFileExtension(fileName: string): string {
  const lastDotIndex = fileName.lastIndexOf('.');
  if (lastDotIndex === -1) return '';
  return fileName.substring(lastDotIndex).toLowerCase();
}

/**
 * 检查文件扩展名是否在白名单中
 */
export function isFileTypeAllowed(fileName: string): boolean {
  const ext = getFileExtension(fileName);
  return ALLOWED_EXTENSIONS.includes(ext as any);
}

// ========== 验证规则 ==========

/**
 * 验证文件大小
 * 返回 null 表示通过，否则返回错误信息
 */
export function validateFileSize(
  fileName: string,
  fileSize: number
): FileValidationError | FileValidationWarning | null {
  // 超过 5GB - 阻止
  if (fileSize > FILE_SIZE_LIMITS.MAX) {
    return {
      fileName,
      fileSize,
      reason: 'size',
      message: `文件过大（${formatFileSize(fileSize)}），超过 5GB 限制`,
    };
  }

  // 超过 2GB - 警告
  if (fileSize > FILE_SIZE_LIMITS.WARNING) {
    return {
      fileName,
      fileSize,
      reason: 'large',
      message: `文件较大（${formatFileSize(fileSize)}），加密可能耗时较长`,
    };
  }

  return null;
}

/**
 * 验证文件类型
 * 返回 null 表示通过，否则返回错误信息
 */
export function validateFileType(
  fileName: string,
  fileSize: number
): FileValidationError | null {
  if (!isFileTypeAllowed(fileName)) {
    const ext = getFileExtension(fileName);
    return {
      fileName,
      fileSize,
      reason: 'type',
      message: `不支持的文件类型: ${ext || '(无扩展名)'}`,
    };
  }

  return null;
}

/**
 * 验证单个文件
 * @param fileName 文件名
 * @param fileSize 文件大小（字节）
 */
export function validateFile(
  fileName: string,
  fileSize: number
): FileValidationResult {
  // 1. 检查文件大小（可能返回错误或警告）
  const sizeValidation = validateFileSize(fileName, fileSize);
  if (sizeValidation && 'reason' in sizeValidation && sizeValidation.reason === 'size') {
    return {
      valid: false,
      error: sizeValidation,
    };
  }

  // 2. 检查文件类型
  const typeValidation = validateFileType(fileName, fileSize);
  if (typeValidation) {
    return {
      valid: false,
      error: typeValidation,
    };
  }

  // 3. 返回结果（可能包含警告）
  if (sizeValidation && sizeValidation.reason === 'large') {
    return {
      valid: true,
      warning: sizeValidation,
    };
  }

  return { valid: true };
}

/**
 * 批量验证文件
 * @param files 文件信息数组 [{ name, size }, ...]
 */
export function validateFiles(
  files: Array<{ name: string; size: number }>
): BatchFileValidationResult {
  const result: BatchFileValidationResult = {
    validFiles: [],
    warnings: [],
    errors: [],
  };

  for (const file of files) {
    const validation = validateFile(file.name, file.size);

    if (validation.valid) {
      result.validFiles.push(file.name);
      if (validation.warning) {
        result.warnings.push(validation.warning);
      }
    } else if (validation.error) {
      result.errors.push(validation.error);
    }
  }

  return result;
}
