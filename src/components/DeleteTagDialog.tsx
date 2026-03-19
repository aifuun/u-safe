import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { TagNode } from '../types/tag';
import './DeleteTagDialog.css';

interface DeleteTagDialogProps {
  tagNode: TagNode | null;
  onConfirm: (tagId: string, force: boolean) => Promise<void>;
  onCancel: () => void;
}

/**
 * 删除标签确认对话框
 *
 * 功能：
 * - 显示标签删除前的影响评估（子标签数、关联文件数）
 * - 提供三种操作选项：
 *   1. 取消删除
 *   2. 仅删除标签（需要无子标签和文件）
 *   3. 强制删除（删除所有子标签并解除文件关联）
 */
export function DeleteTagDialog({ tagNode, onConfirm, onCancel }: DeleteTagDialogProps) {
  const [childrenCount, setChildrenCount] = useState<number>(0);
  const [filesCount, setFilesCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  // 加载标签信息
  useEffect(() => {
    if (!tagNode) return;

    const loadTagInfo = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log('[tag:delete:info:load] tag_id=', tagNode.tag_id);

        const [children, files] = await invoke<[number, number]>('get_tag_info', {
          tagId: tagNode.tag_id,
        });

        console.log('[tag:delete:info:success] children=', children, ', files=', files);
        setChildrenCount(children);
        setFilesCount(files);
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : String(err);
        console.error('[tag:delete:info:failed]', errorMsg);
        setError(errorMsg);
      } finally {
        setLoading(false);
      }
    };

    loadTagInfo();
  }, [tagNode]);

  // 处理删除
  const handleDelete = async (force: boolean) => {
    if (!tagNode) return;

    try {
      setDeleting(true);
      console.log('[tag:delete:confirm] tag_id=', tagNode.tag_id, ', force=', force);
      await onConfirm(tagNode.tag_id, force);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      console.error('[tag:delete:failed]', errorMsg);
      setError(errorMsg);
      setDeleting(false);
    }
  };

  // 未打开对话框
  if (!tagNode) return null;

  return (
    <div className="delete-tag-dialog-overlay">
      <div className="delete-tag-dialog">
        <div className="delete-tag-dialog-header">
          <h2 className="delete-tag-dialog-title">删除标签</h2>
          <button
            className="delete-tag-dialog-close"
            onClick={onCancel}
            aria-label="关闭"
            disabled={deleting}
          >
            ✕
          </button>
        </div>

        <div className="delete-tag-dialog-body">
          {/* 标签信息 */}
          <div className="delete-tag-info">
            <div className="delete-tag-info-item">
              <span className="delete-tag-info-label">标签名称：</span>
              <span className="delete-tag-info-value">
                {tagNode.tag_color && (
                  <span
                    className="delete-tag-color"
                    style={{ backgroundColor: tagNode.tag_color }}
                  />
                )}
                {tagNode.tag_name}
              </span>
            </div>
            <div className="delete-tag-info-item">
              <span className="delete-tag-info-label">完整路径：</span>
              <span className="delete-tag-info-value">{tagNode.full_path}</span>
            </div>
          </div>

          {/* 加载中 */}
          {loading && (
            <div className="delete-tag-loading">
              <div className="delete-tag-spinner" />
              <p>加载标签信息...</p>
            </div>
          )}

          {/* 错误提示 */}
          {error && (
            <div className="delete-tag-error">
              <p className="delete-tag-error-message">❌ {error}</p>
            </div>
          )}

          {/* 影响评估 */}
          {!loading && !error && (
            <div className="delete-tag-impact">
              <h3 className="delete-tag-impact-title">删除影响：</h3>

              {childrenCount > 0 && (
                <div className="delete-tag-impact-item delete-tag-impact-item--warning">
                  <span className="delete-tag-impact-icon">⚠️</span>
                  <span className="delete-tag-impact-text">
                    包含 <strong>{childrenCount}</strong> 个子标签（递归统计）
                  </span>
                </div>
              )}

              {filesCount > 0 && (
                <div className="delete-tag-impact-item delete-tag-impact-item--warning">
                  <span className="delete-tag-impact-icon">📁</span>
                  <span className="delete-tag-impact-text">
                    关联 <strong>{filesCount}</strong> 个文件
                  </span>
                </div>
              )}

              {childrenCount === 0 && filesCount === 0 && (
                <div className="delete-tag-impact-item delete-tag-impact-item--safe">
                  <span className="delete-tag-impact-icon">✅</span>
                  <span className="delete-tag-impact-text">
                    该标签没有子标签和关联文件，可以安全删除
                  </span>
                </div>
              )}
            </div>
          )}

          {/* 操作说明 */}
          {!loading && !error && (childrenCount > 0 || filesCount > 0) && (
            <div className="delete-tag-warning">
              <p className="delete-tag-warning-title">⚠️ 警告</p>
              <p className="delete-tag-warning-text">
                普通删除会因为存在子标签或关联文件而失败。
              </p>
              <p className="delete-tag-warning-text">
                <strong>强制删除</strong>将：
              </p>
              <ul className="delete-tag-warning-list">
                {childrenCount > 0 && <li>递归删除所有子标签</li>}
                {filesCount > 0 && <li>解除所有文件的标签关联</li>}
              </ul>
            </div>
          )}
        </div>

        {/* 操作按钮 */}
        <div className="delete-tag-dialog-footer">
          <button
            className="delete-tag-btn delete-tag-btn--cancel"
            onClick={onCancel}
            disabled={deleting}
          >
            取消
          </button>

          {!loading && !error && (
            <>
              {childrenCount === 0 && filesCount === 0 && (
                <button
                  className="delete-tag-btn delete-tag-btn--danger"
                  onClick={() => handleDelete(false)}
                  disabled={deleting}
                >
                  {deleting ? '删除中...' : '删除标签'}
                </button>
              )}

              {(childrenCount > 0 || filesCount > 0) && (
                <>
                  <button
                    className="delete-tag-btn delete-tag-btn--secondary"
                    onClick={() => handleDelete(false)}
                    disabled={deleting}
                    title="仅在无子标签和文件时成功"
                  >
                    {deleting ? '删除中...' : '尝试删除'}
                  </button>
                  <button
                    className="delete-tag-btn delete-tag-btn--danger"
                    onClick={() => handleDelete(true)}
                    disabled={deleting}
                  >
                    {deleting ? '强制删除中...' : '强制删除'}
                  </button>
                </>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
