/**
 * 文件验证工具
 * 验证文件类型、大小等
 */

// 文件大小限制 (字节)
export const FILE_SIZE_LIMITS = {
  WARNING: 2 * 1024 * 1024 * 1024, // 2GB - 显示警告
  MAX: 5 * 1024 * 1024 * 1024,     // 5GB - 阻止上传
} as const;

// 支持的文件类型白名单
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

export interface FileValidationError {
  file: File;
  reason: 'type' | 'size' | 'unknown';
  message: string;
}

export interface FileValidationWarning {
  file: File;
  reason: 'large';
  message: string;
}

export interface FileValidationResult {
  valid: File[];
  warnings: FileValidationWarning[];
  errors: FileValidationError[];
}

/**
 * 检查文件扩展名是否在白名单中
 */
function isFileTypeAllowed(filename: string): boolean {
  const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'));
  return ALLOWED_EXTENSIONS.includes(ext as any);
}

/**
 * 格式化文件大小为人类可读格式
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
}

/**
 * 验证单个文件
 */
export function validateFile(file: File): {
  valid: boolean;
  warning?: FileValidationWarning;
  error?: FileValidationError;
} {
  // 检查文件大小 - 超过 5GB 阻止
  if (file.size > FILE_SIZE_LIMITS.MAX) {
    return {
      valid: false,
      error: {
        file,
        reason: 'size',
        message: `文件过大（${formatFileSize(file.size)}），超过 5GB 限制`,
      },
    };
  }

  // 检查文件类型
  if (!isFileTypeAllowed(file.name)) {
    return {
      valid: false,
      error: {
        file,
        reason: 'type',
        message: `不支持的文件类型: ${file.name.substring(file.name.lastIndexOf('.'))}`,
      },
    };
  }

  // 检查文件大小 - 超过 2GB 警告
  if (file.size > FILE_SIZE_LIMITS.WARNING) {
    return {
      valid: true,
      warning: {
        file,
        reason: 'large',
        message: `文件较大（${formatFileSize(file.size)}），加密可能耗时较长`,
      },
    };
  }

  return { valid: true };
}

/**
 * 批量验证文件
 */
export function validateFiles(files: File[]): FileValidationResult {
  const result: FileValidationResult = {
    valid: [],
    warnings: [],
    errors: [],
  };

  for (const file of files) {
    const validation = validateFile(file);

    if (validation.valid) {
      result.valid.push(file);
      if (validation.warning) {
        result.warnings.push(validation.warning);
      }
    } else if (validation.error) {
      result.errors.push(validation.error);
    }
  }

  return result;
}
