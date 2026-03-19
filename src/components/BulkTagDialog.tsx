import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import './BulkTagDialog.css';

interface BulkOperationResult {
  total_files: number;
  total_tags: number;
  associations_added: number;
  failures: string[];
}

export interface BulkTagDialogProps {
  selectedFileIds: number[];
  availableTags: Array<{
    tag_id: string;
    tag_name: string;
    tag_color?: string | null;
    full_path: string;
  }>;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function BulkTagDialog({
  selectedFileIds,
  availableTags,
  isOpen,
  onClose,
  onSuccess,
}: BulkTagDialogProps) {
  const [selectedTagIds, setSelectedTagIds] = useState<Set<string>>(new Set());
  const [isApplying, setIsApplying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // 重置状态当对话框打开时
  useEffect(() => {
    if (isOpen) {
      setSelectedTagIds(new Set());
      setSearchQuery('');
      setError(null);
    }
  }, [isOpen]);

  // 过滤标签
  const filteredTags = availableTags.filter((tag) =>
    tag.tag_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    tag.full_path.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // 切换标签选择
  const toggleTag = (tagId: string) => {
    const newSelected = new Set(selectedTagIds);
    if (newSelected.has(tagId)) {
      newSelected.delete(tagId);
    } else {
      newSelected.add(tagId);
    }
    setSelectedTagIds(newSelected);
  };

  // 应用批量添加标签
  const handleApply = async () => {
    if (selectedTagIds.size === 0) {
      setError('请至少选择一个标签');
      return;
    }

    setIsApplying(true);
    setError(null);

    try {
      const result = await invoke<BulkOperationResult>('bulk_add_tags', {
        fileIds: selectedFileIds,
        tagIds: Array.from(selectedTagIds),
      });

      console.info('[bulk:add_tags:success]', {
        fileCount: result.total_files,
        tagCount: result.total_tags,
        associationsAdded: result.associations_added,
      });

      if (result.failures.length > 0) {
        setError(`部分操作失败：${result.failures.length} 个关联失败`);
      } else {
        onSuccess();
        onClose();
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setError(errorMessage);
      console.error('[bulk:add_tags:failed]', { error: errorMessage });
    } finally {
      setIsApplying(false);
    }
  };

  if (!isOpen) return null;

  const totalAssociations = selectedFileIds.length * selectedTagIds.size;

  return (
    <div className="bulk-tag-dialog-overlay" onClick={onClose}>
      <div className="bulk-tag-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="bulk-tag-dialog__header">
          <h2>批量添加标签</h2>
          <button
            className="bulk-tag-dialog__close-btn"
            onClick={onClose}
            disabled={isApplying}
            aria-label="关闭对话框"
          >
            ✕
          </button>
        </div>

        <div className="bulk-tag-dialog__body">
          <div className="bulk-tag-dialog__summary">
            <div className="bulk-tag-dialog__summary-item">
              <span className="bulk-tag-dialog__summary-label">已选文件:</span>
              <span className="bulk-tag-dialog__summary-value">{selectedFileIds.length}</span>
            </div>
            <div className="bulk-tag-dialog__summary-item">
              <span className="bulk-tag-dialog__summary-label">已选标签:</span>
              <span className="bulk-tag-dialog__summary-value">{selectedTagIds.size}</span>
            </div>
            <div className="bulk-tag-dialog__summary-item">
              <span className="bulk-tag-dialog__summary-label">将创建关联:</span>
              <span className="bulk-tag-dialog__summary-value bulk-tag-dialog__summary-value--primary">
                {totalAssociations}
              </span>
            </div>
          </div>

          <div className="bulk-tag-dialog__search">
            <input
              type="text"
              className="bulk-tag-dialog__search-input"
              placeholder="搜索标签..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              disabled={isApplying}
            />
          </div>

          <div className="bulk-tag-dialog__tag-list">
            {filteredTags.length === 0 ? (
              <div className="bulk-tag-dialog__empty">
                {searchQuery ? '没有找到匹配的标签' : '没有可用的标签'}
              </div>
            ) : (
              filteredTags.map((tag) => (
                <label
                  key={tag.tag_id}
                  className={`bulk-tag-dialog__tag-item ${
                    selectedTagIds.has(tag.tag_id) ? 'bulk-tag-dialog__tag-item--selected' : ''
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedTagIds.has(tag.tag_id)}
                    onChange={() => toggleTag(tag.tag_id)}
                    disabled={isApplying}
                  />
                  <div className="bulk-tag-dialog__tag-content">
                    {tag.tag_color && (
                      <span
                        className="bulk-tag-dialog__tag-color"
                        style={{ backgroundColor: tag.tag_color }}
                      />
                    )}
                    <div className="bulk-tag-dialog__tag-info">
                      <span className="bulk-tag-dialog__tag-name">{tag.tag_name}</span>
                      {tag.full_path !== tag.tag_name && (
                        <span className="bulk-tag-dialog__tag-path">{tag.full_path}</span>
                      )}
                    </div>
                  </div>
                </label>
              ))
            )}
          </div>

          {error && (
            <div className="bulk-tag-dialog__error" role="alert">
              {error}
            </div>
          )}
        </div>

        <div className="bulk-tag-dialog__footer">
          <button
            className="bulk-tag-dialog__btn bulk-tag-dialog__btn--cancel"
            onClick={onClose}
            disabled={isApplying}
          >
            取消
          </button>
          <button
            className="bulk-tag-dialog__btn bulk-tag-dialog__btn--primary"
            onClick={handleApply}
            disabled={isApplying || selectedTagIds.size === 0}
          >
            {isApplying ? '处理中...' : `添加标签 (${totalAssociations})`}
          </button>
        </div>
      </div>
    </div>
  );
}
