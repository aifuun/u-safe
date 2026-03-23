/**
 * 文件验证工具 - Adapter for Browser File API
 *
 * 这是 Modules 层的适配器，将浏览器的 File 对象适配到 Domains 层的验证规则
 * 业务规则在 @/domains/file/rules/validation
 */

import {
  FILE_SIZE_LIMITS,
  ALLOWED_EXTENSIONS,
  formatFileSize,
  validateFile as validateFileDomain,
} from '@/domains/file';

// 重新导出常量供外部使用
export { FILE_SIZE_LIMITS, ALLOWED_EXTENSIONS, formatFileSize };

// Adapter 层的类型定义（包含浏览器 File 对象）
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
 * 验证单个文件 - Adapter
 * 将浏览器 File 对象适配到 Domains 层验证
 */
export function validateFile(file: File): {
  valid: boolean;
  warning?: FileValidationWarning;
  error?: FileValidationError;
} {
  // 调用 Domains 层纯函数（传递文件名和大小）
  const domainResult = validateFileDomain(file.name, file.size);

  // 适配结果（添加 File 对象引用）
  if (!domainResult.valid && domainResult.error) {
    return {
      valid: false,
      error: {
        file,
        reason: domainResult.error.reason,
        message: domainResult.error.message,
      },
    };
  }

  if (domainResult.valid && domainResult.warning) {
    return {
      valid: true,
      warning: {
        file,
        reason: domainResult.warning.reason,
        message: domainResult.warning.message,
      },
    };
  }

  return { valid: true };
}

/**
 * 批量验证文件 - Adapter
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
