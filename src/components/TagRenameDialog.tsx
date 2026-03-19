import { useState, useEffect } from 'react';
import './TagRenameDialog.css';

export interface TagRenameDialogProps {
  tag: {
    tag_id: string;
    tag_name: string;
    tag_color?: string | null;
    parent_tag_id?: string | null;
  };
  isOpen: boolean;
  onClose: () => void;
  onRename: (tagId: string, newName: string) => Promise<void>;
  descendantCount?: number; // 子标签数量
}

export function TagRenameDialog({
  tag,
  isOpen,
  onClose,
  onRename,
  descendantCount = 0,
}: TagRenameDialogProps) {
  const [newName, setNewName] = useState(tag.tag_name);
  const [isRenaming, setIsRenaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 重置状态当对话框打开或标签改变时
  useEffect(() => {
    if (isOpen) {
      setNewName(tag.tag_name);
      setError(null);
    }
  }, [isOpen, tag.tag_name]);

  // 处理键盘事件
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === 'Enter' && !e.shiftKey) {
        handleRename();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, newName]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleRename = async () => {
    const trimmedName = newName.trim();

    // 验证：名称不能为空
    if (!trimmedName) {
      setError('标签名称不能为空');
      return;
    }

    // 验证：长度不超过50
    if (trimmedName.length > 50) {
      setError('标签名称不能超过50个字符');
      return;
    }

    // 验证：名称没有改变
    if (trimmedName === tag.tag_name) {
      onClose();
      return;
    }

    setIsRenaming(true);
    setError(null);

    try {
      await onRename(tag.tag_id, trimmedName);
      onClose();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setError(errorMessage);
      console.error('[tag:rename:failed]', { tagId: tag.tag_id, error: errorMessage });
    } finally {
      setIsRenaming(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="tag-rename-dialog-overlay" onClick={onClose}>
      <div className="tag-rename-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="tag-rename-dialog__header">
          <h2>重命名标签</h2>
          <button
            className="tag-rename-dialog__close-btn"
            onClick={onClose}
            disabled={isRenaming}
            aria-label="关闭对话框"
          >
            ✕
          </button>
        </div>

        <div className="tag-rename-dialog__body">
          <div className="tag-rename-dialog__current-info">
            <label>当前名称:</label>
            <div className="tag-rename-dialog__current-tag">
              {tag.tag_color && (
                <span
                  className="tag-rename-dialog__color-badge"
                  style={{ backgroundColor: tag.tag_color }}
                />
              )}
              <span>{tag.tag_name}</span>
            </div>
          </div>

          <div className="tag-rename-dialog__input-group">
            <label htmlFor="new-tag-name">新名称:</label>
            <input
              id="new-tag-name"
              type="text"
              className="tag-rename-dialog__input"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              disabled={isRenaming}
              placeholder="输入新标签名称"
              maxLength={50}
              autoFocus
            />
            <div className="tag-rename-dialog__char-count">
              {newName.length}/50
            </div>
          </div>

          {descendantCount > 0 && (
            <div className="tag-rename-dialog__warning">
              <span className="tag-rename-dialog__warning-icon">⚠️</span>
              <span>
                此操作将同时更新 <strong>{descendantCount}</strong> 个子标签的路径
              </span>
            </div>
          )}

          {error && (
            <div className="tag-rename-dialog__error" role="alert">
              {error}
            </div>
          )}
        </div>

        <div className="tag-rename-dialog__footer">
          <button
            className="tag-rename-dialog__btn tag-rename-dialog__btn--cancel"
            onClick={onClose}
            disabled={isRenaming}
          >
            取消
          </button>
          <button
            className="tag-rename-dialog__btn tag-rename-dialog__btn--primary"
            onClick={handleRename}
            disabled={isRenaming || !newName.trim()}
          >
            {isRenaming ? '重命名中...' : '确认'}
          </button>
        </div>
      </div>
    </div>
  );
}
