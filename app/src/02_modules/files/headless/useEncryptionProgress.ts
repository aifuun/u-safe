/**
 * 加密/解密进度监听 Hook
 *
 * 监听 Rust 后端发送的加密/解密进度事件
 * 参考: .claude/rules/desktop/tauri-ipc.md
 */

import { useEffect, useState } from 'react';
import { listen, type UnlistenFn } from '@tauri-apps/api/event';
import { logger } from '@/modules/core';

/**
 * 加密进度数据（与 Rust EncryptionProgress 对应）
 */
export interface EncryptionProgress {
  /** 已处理字节数 */
  bytes_processed: number;
  /** 总字节数 */
  total_bytes: number;
  /** 进度百分比 (0-100) */
  percentage: number;
}

/**
 * 加密进度状态
 */
export interface EncryptionProgressState {
  /** 是否正在加密 */
  isEncrypting: boolean;
  /** 是否正在解密 */
  isDecrypting: boolean;
  /** 加密进度 */
  encryptionProgress: EncryptionProgress | null;
  /** 解密进度 */
  decryptionProgress: EncryptionProgress | null;
}

/**
 * 加密/解密进度监听 Hook
 *
 * @returns EncryptionProgressState
 *
 * @example
 * ```tsx
 * const { isEncrypting, encryptionProgress } = useEncryptionProgress();
 *
 * {isEncrypting && encryptionProgress && (
 *   <ProgressBar
 *     value={encryptionProgress.percentage}
 *     max={100}
 *     label={`加密中... ${encryptionProgress.percentage.toFixed(1)}%`}
 *   />
 * )}
 * ```
 */
export function useEncryptionProgress(): EncryptionProgressState {
  const [isEncrypting, setIsEncrypting] = useState(false);
  const [isDecrypting, setIsDecrypting] = useState(false);
  const [encryptionProgress, setEncryptionProgress] = useState<EncryptionProgress | null>(null);
  const [decryptionProgress, setDecryptionProgress] = useState<EncryptionProgress | null>(null);

  useEffect(() => {
    let unlistenEncryption: UnlistenFn | null = null;
    let unlistenDecryption: UnlistenFn | null = null;

    // 监听加密进度事件
    listen<EncryptionProgress>('encryption-progress', (event) => {
      logger.info('useEncryptionProgress:encryption', event.payload as unknown as Record<string, unknown>);
      setIsEncrypting(true);
      setEncryptionProgress(event.payload);

      // 加密完成时重置状态
      if (event.payload.percentage >= 100) {
        setTimeout(() => {
          setIsEncrypting(false);
          setEncryptionProgress(null);
        }, 500); // 延迟 500ms 让用户看到 100%
      }
    }).then((fn) => {
      unlistenEncryption = fn;
    });

    // 监听解密进度事件
    listen<EncryptionProgress>('decryption-progress', (event) => {
      logger.info('useEncryptionProgress:decryption', event.payload as unknown as Record<string, unknown>);
      setIsDecrypting(true);
      setDecryptionProgress(event.payload);

      // 解密完成时重置状态
      if (event.payload.percentage >= 100) {
        setTimeout(() => {
          setIsDecrypting(false);
          setDecryptionProgress(null);
        }, 500); // 延迟 500ms 让用户看到 100%
      }
    }).then((fn) => {
      unlistenDecryption = fn;
    });

    // 清理监听器
    return () => {
      if (unlistenEncryption) {
        unlistenEncryption();
      }
      if (unlistenDecryption) {
        unlistenDecryption();
      }
    };
  }, []);

  return {
    isEncrypting,
    isDecrypting,
    encryptionProgress,
    decryptionProgress,
  };
}
