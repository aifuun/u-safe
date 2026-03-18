/**
 * Files Module - File Management with Encryption
 *
 * Phase 3 (M3): 文件管理
 */

// Types
export type { FileNode, FileType, FileTreeState, FileOperation } from './types';

// Components
export { FileTreeView } from './views/FileTreeView';
export { ContextMenu } from './views/ContextMenu';

// Hooks & Stores
export { useFileTreeStore } from './headless/useFileTreeStore';

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
