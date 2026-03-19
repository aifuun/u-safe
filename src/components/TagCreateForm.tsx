import { useState, FormEvent } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { Tag, CreateTagRequest } from '../types/tag';
import './TagCreateForm.css';

interface TagCreateFormProps {
  onSuccess?: (tag: Tag) => void;
  onError?: (error: string) => void;
  parentTag?: Tag | null;
}

/**
 * 标签创建表单组件
 *
 * 功能：
 * - 输入标签名称（必填，≤50字符）
 * - 选择颜色（可选）
 * - 选择父标签（可选）
 * - 客户端验证
 * - 调用 create_tag IPC 命令
 * - 错误处理和提示
 */
export function TagCreateForm({ onSuccess, onError, parentTag = null }: TagCreateFormProps) {
  const [name, setName] = useState('');
  const [color, setColor] = useState('#3B82F6'); // 默认蓝色
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationError, setValidationError] = useState('');

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

  // 处理表单提交
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // 客户端验证
    const error = validateName(name);
    if (error) {
      setValidationError(error);
      return;
    }

    setIsSubmitting(true);
    setValidationError('');

    try {
      console.log('[tag:create] 开始创建标签', { name, parentTag, color });

      const request: CreateTagRequest = {
        name: name.trim(),
        color,
      };

      // 如果有父标签，添加 parent_id
      if (parentTag) {
        request.parent_id = parentTag.tag_id;
      }

      // 调用 Rust IPC 命令
      const newTag = await invoke<Tag>('create_tag', { request });

      console.log('[tag:create:success]', newTag);

      // 重置表单
      setName('');
      setColor('#3B82F6');

      // 调用成功回调
      if (onSuccess) {
        onSuccess(newTag);
      }
    } catch (error) {
      console.error('[tag:create:failed]', error);

      // 解析错误信息
      const errorMessage = typeof error === 'string' ? error : '创建标签失败';

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
    <form className="tag-create-form" onSubmit={handleSubmit}>
      <div className="form-header">
        <h3 className="form-title">创建标签</h3>
        {parentTag && (
          <p className="parent-tag-info">
            父标签: <span className="parent-tag-name">{parentTag.full_path}</span>
          </p>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="tag-name" className="form-label">
          标签名称 <span className="required">*</span>
        </label>
        <input
          id="tag-name"
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
          aria-describedby={validationError ? 'tag-name-error' : undefined}
        />
        <div className="char-count">
          {name.length} / 50
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="tag-color" className="form-label">
          标签颜色
        </label>
        <div className="color-picker-container">
          <input
            id="tag-color"
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
          id="tag-name-error"
          className="error-message"
          role="alert"
        >
          ⚠️ {validationError}
        </div>
      )}

      <div className="form-actions">
        <button
          type="submit"
          className="btn btn-primary"
          disabled={isSubmitting || !name.trim()}
        >
          {isSubmitting ? '创建中...' : '创建标签'}
        </button>
      </div>
    </form>
  );
}
