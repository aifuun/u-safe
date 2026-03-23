import { invoke } from '@tauri-apps/api/core';

type LogLevel = 'info' | 'warn' | 'error' | 'debug';

/**
 * 前端日志服务
 *
 * 功能：
 * 1. 开发环境：输出到浏览器控制台（便于调试）
 * 2. 生产环境：通过 IPC 写入后端日志文件
 * 3. 统一日志格式：[event] {context}
 *
 * 使用示例：
 * ```typescript
 * import { logger } from '@/kernel/services/logService';
 *
 * logger.info('file:encrypt:start', { fileId: 123, size: '1.2MB' });
 * logger.error('file:encrypt:failed', { fileId: 123, error: 'MAC验证失败' });
 * ```
 */
class LogService {
  /**
   * 内部日志方法
   *
   * @param level - 日志级别
   * @param event - 事件标识（例如："file:encrypt:start"）
   * @param context - 可选的上下文数据
   */
  private async log(
    level: LogLevel,
    event: string,
    context?: Record<string, unknown>
  ): Promise<void> {
    // 1. 立即输出到浏览器控制台（开发调试）
    const consoleContext = context ? context : '';
    console[level](`[${event}]`, consoleContext);

    // 2. 异步写入后端日志文件（不阻塞 UI）
    try {
      await invoke('write_frontend_log', {
        level,
        event,
        context: context ? JSON.stringify(context) : null,
      });
    } catch (err) {
      // 静默失败（避免日志系统故障影响主功能）
      // 仅在控制台输出警告
      console.warn('[logService] 写入后端日志失败:', err);
    }
  }

  /**
   * 记录信息级别日志
   *
   * 用途：关键业务事件（加密开始、文件删除等）
   *
   * @param event - 事件标识
   * @param context - 可选的上下文数据
   */
  info(event: string, context?: Record<string, unknown>): Promise<void> {
    return this.log('info', event, context);
  }

  /**
   * 记录警告级别日志
   *
   * 用途：异常但可恢复（密码错误、文件跳过等）
   *
   * @param event - 事件标识
   * @param context - 可选的上下文数据
   */
  warn(event: string, context?: Record<string, unknown>): Promise<void> {
    return this.log('warn', event, context);
  }

  /**
   * 记录错误级别日志
   *
   * 用途：操作失败、异常崩溃
   *
   * @param event - 事件标识
   * @param context - 可选的上下文数据
   */
  error(event: string, context?: Record<string, unknown>): Promise<void> {
    return this.log('error', event, context);
  }

  /**
   * 记录调试级别日志
   *
   * 用途：开发调试信息（仅开发环境）
   *
   * @param event - 事件标识
   * @param context - 可选的上下文数据
   */
  debug(event: string, context?: Record<string, unknown>): Promise<void> {
    return this.log('debug', event, context);
  }
}

/**
 * 全局日志服务实例
 *
 * 使用方式：
 * ```typescript
 * import { logger } from '@/kernel/services/logService';
 *
 * logger.info('app:init', { version: '0.1.0' });
 * ```
 */
export const logger = new LogService();
