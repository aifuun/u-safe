/**
 * File Module Exports
 */

// Components
export { DragDropZone } from './components/DragDropZone';
export type { DragDropZoneProps } from './components/DragDropZone';

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
