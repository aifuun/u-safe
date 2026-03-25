import { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
// @ts-expect-error - Tauri dialog API may not have type definitions in all versions
import { save } from '@tauri-apps/api/dialog';
import { logger } from '@/modules/core';
import './DiagnosticExport.css';

/**
 * 诊断日志导出组件
 *
 * 功能：
 * 1. 导出最近 7 天的日志文件
 * 2. 打开系统文件保存对话框
 * 3. 显示导出状态（进行中/成功/失败）
 */
export function DiagnosticExport() {
  const [isExporting, setIsExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');

  /**
   * 导出诊断日志
   */
  const handleExport = async () => {
    setIsExporting(true);
    setExportStatus('idle');
    setErrorMessage('');

    try {
      logger.info('settings:export-logs:start');

      // 1. 调用后端生成 ZIP 文件
      const zipPath = await invoke<string>('export_diagnostic_logs');

      logger.info('settings:export-logs:zip-created', { zipPath });

      // 2. 打开系统保存对话框
      const savePath = await save({
        defaultPath: `u-safe-logs-${new Date().toISOString().split('T')[0]}.zip`,
        filters: [
          {
            name: 'ZIP 压缩包',
            extensions: ['zip'],
          },
        ],
      });

      if (!savePath) {
        // 用户取消保存
        logger.info('settings:export-logs:cancelled');
        setIsExporting(false);
        return;
      }

      // 3. 移动文件到用户选择的位置
      await invoke('move_file', {
        from: zipPath,
        to: savePath,
      });

      logger.info('settings:export-logs:success', { savePath });
      setExportStatus('success');

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('settings:export-logs:failed', { error: errorMsg });
      setExportStatus('error');
      setErrorMessage(errorMsg);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="diagnostic-export">
      <h3 className="diagnostic-export__title">📊 诊断与日志</h3>

      <div className="diagnostic-export__content">
        <button
          className="diagnostic-export__button"
          onClick={handleExport}
          disabled={isExporting}
          aria-label="导出诊断日志"
        >
          {isExporting ? '⏳ 导出中...' : '📤 导出诊断日志'}
        </button>

        <p className="diagnostic-export__description">
          导出最近 7 天的日志文件，用于问题诊断和反馈。
          包含应用日志和系统信息。
        </p>

        {exportStatus === 'success' && (
          <div className="diagnostic-export__success">
            ✅ 日志导出成功！
          </div>
        )}

        {exportStatus === 'error' && (
          <div className="diagnostic-export__error">
            ❌ 导出失败：{errorMessage}
          </div>
        )}
      </div>
    </div>
  );
}
