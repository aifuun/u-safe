import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import './AllFilesView.css'; // 复用样式

interface FileInfo {
  id: number;
  name: string;
  original_path: string;
  encrypted_path: string;
  size: number;
  is_encrypted: boolean;
  created_at: string;
}

interface RecentFilesViewProps {
  onFileClick?: (fileId: number) => void;
  days?: number; // 最近 N 天，默认 7 天
}

/**
 * RecentFilesView 组件 - 最近添加文件视图
 *
 * 功能:
 * - 显示最近 N 天添加的文件（默认 7 天）
 * - 显示相对时间（"2 天前"）
 * - 网格布局（复用 AllFilesView 样式）
 * - 按日期降序排列
 */
export function RecentFilesView({ onFileClick, days = 7 }: RecentFilesViewProps) {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 加载最近文件
  useEffect(() => {
    loadFiles();
  }, [days]);

  const loadFiles = async () => {
    try {
      console.info('[view:recent:load]', { days });
      setLoading(true);
      setError(null);

      const result = await invoke<FileInfo[]>('get_recent_files', { days });
      console.info('[view:recent:loaded]', { count: result.length });
      setFiles(result);
    } catch (err) {
      console.error('[view:recent:load:failed]', err);
      setError(err instanceof Error ? err.message : '加载最近文件失败');
    } finally {
      setLoading(false);
    }
  };

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
  };

  // 格式化相对时间
  const formatRelativeTime = (dateString: string): string => {
    const now = new Date();
    const date = new Date(dateString);
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) {
      return `${diffMins} 分钟前`;
    } else if (diffHours < 24) {
      return `${diffHours} 小时前`;
    } else if (diffDays === 1) {
      return '昨天';
    } else {
      return `${diffDays} 天前`;
    }
  };

  // 加载中状态
  if (loading) {
    return (
      <div className="all-files-view">
        <div className="all-files-view__loading">
          <div className="loading-spinner" aria-label="加载中" />
          <p>加载最近文件...</p>
        </div>
      </div>
    );
  }

  // 错误状态
  if (error) {
    return (
      <div className="all-files-view">
        <div className="all-files-view__error" role="alert">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
          <button
            type="button"
            className="btn-retry"
            onClick={loadFiles}
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  // 空状态
  if (files.length === 0) {
    return (
      <div className="all-files-view">
        <div className="all-files-view__empty">
          <span className="empty-icon">🕒</span>
          <p className="empty-title">最近 {days} 天无新文件</p>
          <p className="empty-description">
            最近添加的文件将显示在这里
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="all-files-view">
      {/* 工具栏 */}
      <div className="all-files-view__toolbar">
        <div className="toolbar-left">
          <span className="file-count">
            最近 {days} 天添加了 {files.length} 个文件
          </span>
        </div>
      </div>

      {/* 文件网格 */}
      <div className="all-files-view__grid">
        {files.map((file) => (
          <div
            key={file.id}
            className="file-card"
            onClick={() => onFileClick?.(file.id)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onFileClick?.(file.id);
              }
            }}
            role="button"
            tabIndex={0}
            aria-label={`文件: ${file.name}`}
          >
            {/* 文件图标 */}
            <div className="file-card__icon">
              {file.is_encrypted ? '🔒' : '📄'}
            </div>

            {/* 文件信息 */}
            <div className="file-card__info">
              <h3 className="file-card__name" title={file.name}>
                {file.name}
              </h3>
              <p className="file-card__meta">
                {formatFileSize(file.size)} • {formatRelativeTime(file.created_at)}
              </p>
              <p className="file-card__status">
                {file.is_encrypted ? (
                  <span className="status-badge status-badge--encrypted">
                    已加密
                  </span>
                ) : (
                  <span className="status-badge status-badge--decrypted">
                    未加密
                  </span>
                )}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
