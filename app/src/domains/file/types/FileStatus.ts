/**
 * 文件状态枚举
 * 表示文件在系统中的当前状态
 */
export const FileStatus = {
  /** 未加密 - 原始文件状态 */
  DECRYPTED: 'decrypted',
  /** 加密中 - 正在执行加密操作 */
  ENCRYPTING: 'encrypting',
  /** 已加密 - 加密完成，文件已被加密 */
  ENCRYPTED: 'encrypted',
  /** 解密中 - 正在执行解密操作 */
  DECRYPTING: 'decrypting',
  /** 错误 - 操作失败 */
  ERROR: 'error',
} as const;

export type FileStatusType = typeof FileStatus[keyof typeof FileStatus];

/**
 * 检查是否为有效的文件状态
 */
export function isValidFileStatus(status: string): status is FileStatusType {
  return Object.values(FileStatus).includes(status as FileStatusType);
}

/**
 * 获取文件状态的中文描述
 */
export function getFileStatusLabel(status: FileStatusType): string {
  const labels: Record<FileStatusType, string> = {
    [FileStatus.DECRYPTED]: '未加密',
    [FileStatus.ENCRYPTING]: '加密中',
    [FileStatus.ENCRYPTED]: '已加密',
    [FileStatus.DECRYPTING]: '解密中',
    [FileStatus.ERROR]: '错误',
  };

  return labels[status] || '未知状态';
}
