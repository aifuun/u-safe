import type { FileType } from '../types';

/**
 * 文件类型到图标的映射
 *
 * MVP v1.0 使用 Emoji 图标
 * 后续版本可迁移到 Lucide React
 */

/** 文件夹图标 */
export const FOLDER_ICONS = {
  /** 折叠状态 */
  collapsed: '📁',
  /** 展开状态 */
  expanded: '📂',
} as const;

/** 文件类型图标映射 */
export const FILE_TYPE_ICONS: Record<FileType, string> = {
  document: '📄',
  image: '🖼️',
  video: '🎬',
  audio: '🎵',
  archive: '📦',
  code: '💻',
  unknown: '📄',
} as const;

/** 加密文件叠加图标 */
export const ENCRYPTION_ICON = '🔒';

/**
 * 获取文件夹图标
 *
 * @param isExpanded - 是否展开
 * @returns 文件夹图标
 */
export function getFolderIcon(isExpanded: boolean): string {
  return isExpanded ? FOLDER_ICONS.expanded : FOLDER_ICONS.collapsed;
}

/**
 * 获取文件类型图标
 *
 * @param fileType - 文件类型
 * @returns 文件类型图标
 */
export function getFileTypeIcon(fileType?: FileType): string {
  if (!fileType) return FILE_TYPE_ICONS.unknown;
  return FILE_TYPE_ICONS[fileType] || FILE_TYPE_ICONS.unknown;
}

/**
 * 获取文件图标（包含加密标识）
 *
 * @param fileType - 文件类型
 * @param isEncrypted - 是否已加密
 * @returns 文件图标字符串
 */
export function getFileIcon(fileType?: FileType, isEncrypted = false): string {
  const baseIcon = getFileTypeIcon(fileType);
  return isEncrypted ? `${ENCRYPTION_ICON} ${baseIcon}` : baseIcon;
}

/**
 * 扩展名到文件类型的映射（辅助）
 *
 * 用于前端快速判断文件类型（不依赖后端）
 */
export const EXTENSION_TO_TYPE: Record<string, FileType> = {
  // 文档类
  pdf: 'document',
  doc: 'document',
  docx: 'document',
  xls: 'document',
  xlsx: 'document',
  ppt: 'document',
  pptx: 'document',
  txt: 'document',
  md: 'document',

  // 图片类
  jpg: 'image',
  jpeg: 'image',
  png: 'image',
  gif: 'image',
  webp: 'image',
  svg: 'image',
  bmp: 'image',
  ico: 'image',

  // 视频类
  mp4: 'video',
  avi: 'video',
  mkv: 'video',
  mov: 'video',
  wmv: 'video',
  flv: 'video',
  webm: 'video',

  // 音频类
  mp3: 'audio',
  wav: 'audio',
  flac: 'audio',
  ogg: 'audio',
  aac: 'audio',
  m4a: 'audio',

  // 压缩包类
  zip: 'archive',
  rar: 'archive',
  '7z': 'archive',
  tar: 'archive',
  gz: 'archive',
  bz2: 'archive',

  // 代码类
  js: 'code',
  ts: 'code',
  tsx: 'code',
  jsx: 'code',
  html: 'code',
  css: 'code',
  scss: 'code',
  json: 'code',
  xml: 'code',
  py: 'code',
  rb: 'code',
  rs: 'code',
  go: 'code',
  java: 'code',
  c: 'code',
  cpp: 'code',
  h: 'code',
  sh: 'code',
} as const;

/**
 * 根据文件扩展名猜测文件类型
 *
 * @param extension - 文件扩展名（不含点号）
 * @returns 文件类型
 */
export function guessFileTypeByExtension(extension?: string): FileType {
  if (!extension) return 'unknown';
  const normalized = extension.toLowerCase();
  return EXTENSION_TO_TYPE[normalized] || 'unknown';
}
