// 02_modules/index.ts - Modules Layer Public API

// File module
export * from './file';

// Files module
export { FileTreeView } from './files';
export type { FileNode, FileOperation, FileType, FileTreeState } from './files/types';

// Settings module
export { DiagnosticExport } from './settings/components/DiagnosticExport';
