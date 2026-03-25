/**
 * File Module Exports
 */

// Components moved to 01_views/files/

// Headless Hooks
export { useFileDrop } from './headless/useFileDrop';
export type { UseFileDropOptions, UseFileDropReturn } from './headless/useFileDrop';

// Utilities
export {
  validateFile,
  validateFiles,
  formatFileSize,
  FILE_SIZE_LIMITS,
  ALLOWED_EXTENSIONS,
} from './headless/fileValidator';
export type {
  FileValidationError,
  FileValidationWarning,
  FileValidationResult,
} from './headless/fileValidator';
