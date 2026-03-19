import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import './TagFileList.css';

interface FileInfo {
  id: number;
  file_path: string;
  original_name: string;
  file_size: number;
  is_encrypted: boolean;
  created_at: string;
}

interface TagFileListProps {
  selectedTagIds: string[];
  filterMode: 'AND' | 'OR';
  recursive: boolean;
  nameQuery?: string;
  onFileClick?: (fileId: number) => void;
}

/**
 * TagFileList 组件
 *
 * 显示根据标签筛选的文件列表
 */
export function TagFileList({
  selectedTagIds,
  filterMode,
  recursive,
  nameQuery = '',
  onFileClick
}: TagFileListProps) {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const searchFiles = async () => {
      // 没有选中标签时，不查询
      if (selectedTagIds.length === 0) {
        setFiles([]);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        console.info('[tag-view:search]', {
          tagIds: selectedTagIds,
          filterMode,
          recursive,
          nameQuery
        });

        const result = await invoke<FileInfo[]>('search_files', {
          tagIds: selectedTagIds,
          filterMode,
          recursive: recursive || false,
          nameQuery: nameQuery || null
        });

        setFiles(result);
        console.info('[tag-view:search:success]', { count: result.length });
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : String(err);
        console.error('[tag-view:search:failed]', { error: errorMsg });
        setError(errorMsg);
        setFiles([]);
      } finally {
        setLoading(false);
      }
    };

    searchFiles();
  }, [selectedTagIds, filterMode, recursive, nameQuery]);

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  };

  // 格式化日期
  const formatDate = (isoString: string): string => {
    const date = new Date(isoString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Loading 状态
  if (loading) {
    return (
      <div className="tag-file-list">
        <div className="tag-file-list__loading" role="status">
          <div className="tag-file-list__spinner" />
          <p>正在加载文件...</p>
        </div>
      </div>
    );
  }

  // Error 状态
  if (error) {
    return (
      <div className="tag-file-list">
        <div className="tag-file-list__error" role="alert">
          <span className="tag-file-list__error-icon">⚠️</span>
          <div>
            <h3>加载失败</h3>
            <p>{error}</p>
          </div>
        </div>
      </div>
    );
  }

  // Empty 状态：没有选中标签
  if (selectedTagIds.length === 0) {
    return (
      <div className="tag-file-list">
        <div className="tag-file-list__empty">
          <span className="tag-file-list__empty-icon">📁</span>
          <h3>未选择标签</h3>
          <p>从左侧选择一个或多个标签查看关联的文件</p>
        </div>
      </div>
    );
  }

  // Empty 状态：没有匹配的文件
  if (files.length === 0) {
    return (
      <div className="tag-file-list">
        <div className="tag-file-list__empty">
          <span className="tag-file-list__empty-icon">🔍</span>
          <h3>没有找到文件</h3>
          <p>所选标签没有关联任何文件</p>
        </div>
      </div>
    );
  }

  // 文件列表
  return (
    <div className="tag-file-list">
      <div className="tag-file-list__header">
        <h3>文件列表</h3>
        <span className="tag-file-list__count">{files.length} 个文件</span>
      </div>

      <div className="tag-file-list__grid">
        {files.map((file) => (
          <div
            key={file.id}
            className="tag-file-card"
            onClick={() => onFileClick?.(file.id)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onFileClick?.(file.id);
              }
            }}
            aria-label={`文件: ${file.original_name}`}
          >
            <div className="tag-file-card__header">
              <span className="tag-file-card__icon">
                {file.is_encrypted ? '🔒' : '📄'}
              </span>
              <span
                className={`tag-file-card__status ${
                  file.is_encrypted ? 'tag-file-card__status--encrypted' : ''
                }`}
              >
                {file.is_encrypted ? '已加密' : '明文'}
              </span>
            </div>

            <div className="tag-file-card__body">
              <h4 className="tag-file-card__name" title={file.original_name}>
                {file.original_name}
              </h4>
              <p className="tag-file-card__meta">
                <span>{formatFileSize(file.file_size)}</span>
                <span>•</span>
                <span>{formatDate(file.created_at)}</span>
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
