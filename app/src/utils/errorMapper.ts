/**
 * 错误信息友好化映射
 * 将技术错误转换为用户可读的友好消息
 */

/**
 * 错误代码到友好消息的映射表
 */
const ERROR_MESSAGES: Record<string, string> = {
  // 文件系统错误
  ENOSPC: '磁盘空间不足，请清理空间后重试',
  EACCES: '无权限访问该文件，请检查文件权限',
  ENOENT: '文件不存在或已被删除',
  EISDIR: '目标路径是目录而非文件',
  ENOTDIR: '目标路径是文件而非目录',
  EEXIST: '文件已存在',
  EMFILE: '打开的文件过多，请关闭一些文件后重试',
  ENAMETOOLONG: '文件名过长',
  EROFS: '文件系统为只读，无法写入',

  // 加密相关错误
  InvalidPassword: '密码错误，请重新输入',
  PasswordTooShort: '密码长度不足，至少需要 8 个字符',
  PasswordTooWeak: '密码强度不足，请使用更复杂的密码',
  DecryptionFailed: '解密失败，文件可能已损坏或密码错误',
  EncryptionFailed: '加密失败，请重试',
  KeyDerivationFailed: '密钥派生失败',
  FileCorrupted: '文件已损坏，无法解密',

  // 文件验证错误
  FileTooLarge: '文件过大（超过 5GB），暂不支持',
  UnsupportedFileType: '不支持的文件类型',
  InvalidFileName: '文件名包含非法字符',
  TooManyFiles: '文件数量过多，一次最多导入 100 个文件',

  // 数据库错误
  DatabaseError: '数据库操作失败',
  DatabaseLocked: '数据库被锁定，请稍后重试',
  ConstraintViolation: '数据约束冲突',
  ForeignKeyViolation: '关联数据不存在',

  // 网络错误 (虽然 MVP 是离线应用，但预留)
  NetworkError: '网络连接失败',
  Timeout: '操作超时，请重试',

  // 通用错误
  UnknownError: '未知错误，请联系技术支持',
  OperationCancelled: '操作已取消',
  PermissionDenied: '权限不足',
  InvalidInput: '输入无效',
};

/**
 * 带解决建议的错误消息
 */
const ERROR_SUGGESTIONS: Record<string, string> = {
  ENOSPC: '请删除一些文件释放空间，或选择其他磁盘',
  EACCES: '请确保您有读写该文件的权限',
  InvalidPassword: '请仔细核对密码，注意大小写',
  FileTooLarge: '请将大文件分割后再导入，或使用外部加密工具',
  DatabaseLocked: '请关闭其他正在访问数据库的程序',
};

/**
 * 将技术错误转换为用户友好的消息
 *
 * @param technicalError - 技术错误代码或消息
 * @param includesSuggestion - 是否包含解决建议
 * @returns 用户友好的错误消息
 *
 * @example
 * ```ts
 * friendlyError('ENOSPC') // "磁盘空间不足，请清理空间后重试"
 * friendlyError('ENOSPC', true) // "磁盘空间不足，请清理空间后重试。请删除一些文件释放空间，或选择其他磁盘"
 * friendlyError('some_unknown_error') // "操作失败: some_unknown_error"
 * ```
 */
export function friendlyError(
  technicalError: string,
  includeSuggestion: boolean = false
): string {
  // 查找匹配的错误消息
  const message = ERROR_MESSAGES[technicalError];

  if (!message) {
    // 如果没有匹配的映射，返回通用错误
    return `操作失败: ${technicalError}`;
  }

  // 如果需要包含建议
  if (includeSuggestion) {
    const suggestion = ERROR_SUGGESTIONS[technicalError];
    if (suggestion) {
      return `${message}。${suggestion}`;
    }
  }

  return message;
}

/**
 * 从 Error 对象提取友好消息
 *
 * @param error - Error 对象
 * @param includeSuggestion - 是否包含解决建议
 * @returns 用户友好的错误消息
 *
 * @example
 * ```ts
 * try {
 *   // some operation
 * } catch (error) {
 *   const message = friendlyErrorFromException(error, true);
 *   toast.error(message);
 * }
 * ```
 */
export function friendlyErrorFromException(
  error: unknown,
  includeSuggestion: boolean = false
): string {
  if (error instanceof Error) {
    return friendlyError(error.message, includeSuggestion);
  }

  if (typeof error === 'string') {
    return friendlyError(error, includeSuggestion);
  }

  return friendlyError('UnknownError', includeSuggestion);
}
