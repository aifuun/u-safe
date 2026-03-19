import { useState, FormEvent, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import './TagEditForm.css';

interface Tag {
  tag_id: string;
  tag_name: string;
  tag_color?: string;
  parent_tag_id?: string;
  tag_level: number;
  full_path: string;
  created_at: string;
  updated_at: string;
  usage_count: number;
}

interface UpdateTagRequest {
  id: string;
  name?: string;
  color?: string;
}

interface TagEditFormProps {
  tag: Tag;
  onSuccess?: (tag: Tag) => void;
  onError?: (error: string) => void;
  onCancel?: () => void;
}

/**
 * 标签编辑表单组件
 *
 * 功能：
 * - 预填充当前标签信息
 * - 编辑标签名称（可选）
 * - 编辑标签颜色（可选）
 * - 客户端验证
 * - 调用 update_tag IPC 命令
 * - 错误处理和提示
 */
export function TagEditForm({ tag, onSuccess, onError, onCancel }: TagEditFormProps) {
  const [name, setName] = useState(tag.tag_name);
  const [color, setColor] = useState(tag.tag_color || '#3B82F6');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationError, setValidationError] = useState('');

  // 标签变化时更新表单
  useEffect(() => {
    setName(tag.tag_name);
    setColor(tag.tag_color || '#3B82F6');
    setValidationError('');
  }, [tag]);

  // 客户端验证
  const validateName = (value: string): string | null => {
    if (!value.trim()) {
      return '标签名称不能为空';
    }
    if (value.length > 50) {
      return '标签名称不能超过50个字符';
    }
    return null;
  };

  // 检查表单是否有变化
  const hasChanges = (): boolean => {
    return (
      name.trim() !== tag.tag_name ||
      color !== (tag.tag_color || '#3B82F6')
    );
  };

  // 处理表单提交
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // 检查是否有变化
    if (!hasChanges()) {
      setValidationError('没有修改内容');
      return;
    }

    // 客户端验证
    const error = validateName(name);
    if (error) {
      setValidationError(error);
      return;
    }

    setIsSubmitting(true);
    setValidationError('');

    try {
      console.log('[tag:update] 开始更新标签', { id: tag.tag_id, name, color });

      const request: UpdateTagRequest = {
        id: tag.tag_id,
      };

      // 只发送有变化的字段
      if (name.trim() !== tag.tag_name) {
        request.name = name.trim();
      }

      if (color !== (tag.tag_color || '#3B82F6')) {
        request.color = color;
      }

      // 调用 Rust IPC 命令
      const updatedTag = await invoke<Tag>('update_tag', { request });

      console.log('[tag:update:success]', updatedTag);

      // 调用成功回调
      if (onSuccess) {
        onSuccess(updatedTag);
      }
    } catch (error) {
      console.error('[tag:update:failed]', error);

      // 解析错误信息
      const errorMessage = typeof error === 'string' ? error : '更新标签失败';

      setValidationError(errorMessage);

      // 调用错误回调
      if (onError) {
        onError(errorMessage);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="tag-edit-form" onSubmit={handleSubmit}>
      <div className="form-header">
        <h3 className="form-title">编辑标签</h3>
        <p className="tag-path-info">
          路径: <span className="tag-path">{tag.full_path}</span>
        </p>
      </div>

      <div className="form-group">
        <label htmlFor="tag-name-edit" className="form-label">
          标签名称 <span className="required">*</span>
        </label>
        <input
          id="tag-name-edit"
          type="text"
          className="form-input"
          value={name}
          onChange={(e) => {
            setName(e.target.value);
            setValidationError('');
          }}
          placeholder="例如: 工作、项目A、文档"
          maxLength={50}
          disabled={isSubmitting}
          aria-required="true"
          aria-invalid={!!validationError}
          aria-describedby={validationError ? 'tag-name-edit-error' : undefined}
        />
        <div className="char-count">
          {name.length} / 50
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="tag-color-edit" className="form-label">
          标签颜色
        </label>
        <div className="color-picker-container">
          <input
            id="tag-color-edit"
            type="color"
            className="color-picker"
            value={color}
            onChange={(e) => setColor(e.target.value)}
            disabled={isSubmitting}
          />
          <span className="color-value">{color}</span>
        </div>
      </div>

      {validationError && (
        <div
          id="tag-name-edit-error"
          className="error-message"
          role="alert"
        >
          ⚠️ {validationError}
        </div>
      )}

      <div className="form-actions">
        <button
          type="button"
          className="btn btn-secondary"
          onClick={onCancel}
          disabled={isSubmitting}
        >
          取消
        </button>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={isSubmitting || !hasChanges()}
        >
          {isSubmitting ? '保存中...' : '保存更改'}
        </button>
      </div>
    </form>
  );
}
