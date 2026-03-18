/**
 * 文件类型枚举
 */
export type FileType = 'document' | 'image' | 'video' | 'audio' | 'archive' | 'code' | 'unknown';

/**
 * 文件节点接口（与 Rust FileNode 对应）
 */
export interface FileNode {
  /** 文件路径 */
  path: string;
  /** 文件名 */
  name: string;
  /** 文件大小（字节） */
  size: number;
  /** 是否为目录 */
  is_dir: boolean;
  /** 文件类型（仅文件有） */
  file_type?: FileType;
  /** MIME 类型（仅文件有） */
  mime_type?: string;
  /** 文件扩展名（仅文件有） */
  extension?: string;
  /** 子节点（仅目录有） */
  children?: FileNode[];
}

/**
 * 文件树状态接口
 */
export interface FileTreeState {
  /** 根节点 */
  root: FileNode | null;
  /** 展开的节点路径集合 */
  expandedPaths: Set<string>;
  /** 选中的节点路径 */
  selectedPath: string | null;
  /** 加载状态 */
  loading: boolean;
  /** 错误信息 */
  error: string | null;
}

/**
 * 文件操作类型
 */
export type FileOperation = 'encrypt' | 'decrypt' | 'rename' | 'delete';
