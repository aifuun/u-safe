/**
 * Files Module - File Management with Encryption
 *
 * Phase 3 (M3): 文件管理
 */

// Types
export type { FileNode, FileType, FileTreeState, FileOperation } from './types';
export type { DeleteFileResponse, RenameFileResponse } from './headless/fileOperations';

// Components
export { FileTreeView } from './views/FileTreeView';
export { ContextMenu } from './views/ContextMenu';

// Hooks & Stores
export { useFileTreeStore } from './headless/useFileTreeStore';
export { useFileOperations } from './headless/useFileOperations';
export type { UseFileOperationsReturn } from './headless/useFileOperations';
export { useEncryptionProgress } from './headless/useEncryptionProgress';
export type { EncryptionProgress, EncryptionProgressState } from './headless/useEncryptionProgress';

// Services
export { deleteFile, renameFile } from './headless/fileOperations';

// Adapters
export {
  getFolderIcon,
  getFileTypeIcon,
  getFileIcon,
  guessFileTypeByExtension,
  FOLDER_ICONS,
  FILE_TYPE_ICONS,
  EXTENSION_TO_TYPE,
} from './adapters/iconMap';
