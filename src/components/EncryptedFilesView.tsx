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

interface EncryptedFilesViewProps {
  onFileClick?: (fileId: number) => void;
}

/**
 * EncryptedFilesView 组件 - 仅加密文件视图
 *
 * 功能:
 * - 显示所有已加密的文件
 * - 网格布局（复用 AllFilesView 样式）
 * - 显示加密状态突出
 * - 排序选项
 */
export function EncryptedFilesView({ onFileClick }: EncryptedFilesViewProps) {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'size'>('date');

  // 加载已加密文件
  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      console.info('[view:encrypted:load]');
      setLoading(true);
      setError(null);

      const result = await invoke<FileInfo[]>('get_encrypted_files');
      console.info('[view:encrypted:loaded]', { count: result.length });
      setFiles(result);
    } catch (err) {
      console.error('[view:encrypted:load:failed]', err);
      setError(err instanceof Error ? err.message : '加载已加密文件失败');
    } finally {
      setLoading(false);
    }
  };

  // 排序文件
  const sortedFiles = [...files].sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.name.localeCompare(b.name, 'zh-CN');
      case 'date':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      case 'size':
        return b.size - a.size;
      default:
        return 0;
    }
  });

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
  };

  // 格式化日期
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // 加载中状态
  if (loading) {
    return (
      <div className="all-files-view">
        <div className="all-files-view__loading">
          <div className="loading-spinner" aria-label="加载中" />
          <p>加载已加密文件...</p>
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
          <span className="empty-icon">🔒</span>
          <p className="empty-title">暂无已加密文件</p>
          <p className="empty-description">
            开始加密文件以查看列表
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
            共 {files.length} 个已加密文件
          </span>
        </div>
        <div className="toolbar-right">
          <label htmlFor="sort-select" className="sort-label">
            排序:
          </label>
          <select
            id="sort-select"
            className="sort-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'name' | 'date' | 'size')}
          >
            <option value="date">日期</option>
            <option value="name">名称</option>
            <option value="size">大小</option>
          </select>
        </div>
      </div>

      {/* 文件网格 */}
      <div className="all-files-view__grid">
        {sortedFiles.map((file) => (
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
            aria-label={`已加密文件: ${file.name}`}
          >
            {/* 文件图标 */}
            <div className="file-card__icon">
              🔒
            </div>

            {/* 文件信息 */}
            <div className="file-card__info">
              <h3 className="file-card__name" title={file.name}>
                {file.name}
              </h3>
              <p className="file-card__meta">
                {formatFileSize(file.size)} • {formatDate(file.created_at)}
              </p>
              <p className="file-card__status">
                <span className="status-badge status-badge--encrypted">
                  ✅ 已加密
                </span>
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
