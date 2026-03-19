import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { TagNode } from '../types/tag';
import './TagTreeWithSelection.css';

interface TagTreeWithSelectionProps {
  selectedTagIds: string[];
  onSelectionChange: (tagIds: string[]) => void;
}

/**
 * TagTreeWithSelection 组件 (Phase 3)
 *
 * 支持多选的标签树
 * - 显示层级标签结构
 * - 支持多选标签（复选框）
 * - 展开/折叠子标签
 */
export function TagTreeWithSelection({
  selectedTagIds,
  onSelectionChange
}: TagTreeWithSelectionProps) {
  const [tree, setTree] = useState<TagNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  // 加载标签树
  const loadTagTree = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('[tag-tree:load] 开始加载标签树');

      const result = await invoke<TagNode[]>('get_tag_tree');
      console.log('[tag-tree:load:success] 加载了', result.length, '个根标签');

      setTree(result);

      // 默认展开第一层
      const firstLevelIds = result.map(node => node.tag_id);
      setExpandedNodes(new Set(firstLevelIds));
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      console.error('[tag-tree:load:failed]', errorMsg);
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // 组件挂载时加载
  useEffect(() => {
    loadTagTree();
  }, []);

  // 切换展开/折叠
  const toggleExpand = (tagId: string) => {
    setExpandedNodes(prev => {
      const next = new Set(prev);
      if (next.has(tagId)) {
        next.delete(tagId);
      } else {
        next.add(tagId);
      }
      return next;
    });
  };

  // 切换标签选中状态
  const toggleTagSelection = (tagId: string) => {
    const newSelection = selectedTagIds.includes(tagId)
      ? selectedTagIds.filter(id => id !== tagId)
      : [...selectedTagIds, tagId];

    onSelectionChange(newSelection);
  };

  // 渲染单个标签节点
  const renderNode = (node: TagNode, depth: number = 0): JSX.Element => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = expandedNodes.has(node.tag_id);
    const isSelected = selectedTagIds.includes(node.tag_id);

    return (
      <div key={node.tag_id} className="tag-tree-sel-node">
        <div
          className={`tag-tree-sel-item ${isSelected ? 'tag-tree-sel-item--selected' : ''}`}
          style={{ paddingLeft: `${depth * 20}px` }}
        >
          {/* 展开/折叠按钮 */}
          {hasChildren && (
            <button
              className="tag-tree-sel-toggle"
              onClick={() => toggleExpand(node.tag_id)}
              aria-label={isExpanded ? '折叠' : '展开'}
            >
              {isExpanded ? '▼' : '▶'}
            </button>
          )}
          {!hasChildren && <span className="tag-tree-sel-spacer" />}

          {/* 复选框 */}
          <input
            type="checkbox"
            checked={isSelected}
            onChange={() => toggleTagSelection(node.tag_id)}
            className="tag-tree-sel-checkbox"
            aria-label={`选择标签: ${node.tag_name}`}
          />

          {/* 标签名称 */}
          <label
            className="tag-tree-sel-label"
            onClick={() => toggleTagSelection(node.tag_id)}
          >
            {/* 颜色指示器 */}
            {node.tag_color && (
              <span
                className="tag-tree-sel-color"
                style={{ backgroundColor: node.tag_color }}
                aria-hidden="true"
              />
            )}

            {/* 标签名称 */}
            <span className="tag-tree-sel-name">{node.tag_name}</span>

            {/* 使用计数 */}
            {node.usage_count > 0 && (
              <span className="tag-tree-sel-count">{node.usage_count}</span>
            )}
          </label>
        </div>

        {/* 子标签 */}
        {hasChildren && isExpanded && (
          <div className="tag-tree-sel-children">
            {node.children.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  // 加载中状态
  if (loading) {
    return (
      <div className="tag-tree-sel-loading" role="status">
        <div className="tag-tree-sel-spinner" />
        <p>加载标签树...</p>
      </div>
    );
  }

  // 错误状态
  if (error) {
    return (
      <div className="tag-tree-sel-error" role="alert">
        <p className="tag-tree-sel-error-message">❌ 加载失败：{error}</p>
        <button
          className="tag-tree-sel-retry-btn"
          onClick={loadTagTree}
        >
          重试
        </button>
      </div>
    );
  }

  // 空状态
  if (tree.length === 0) {
    return (
      <div className="tag-tree-sel-empty">
        <p>暂无标签</p>
        <p className="tag-tree-sel-empty-hint">创建第一个标签来开始整理文件</p>
      </div>
    );
  }

  // 渲染标签树
  return (
    <div className="tag-tree-sel">
      <div className="tag-tree-sel-header">
        <h3 className="tag-tree-sel-title">标签</h3>
        <button
          className="tag-tree-sel-refresh-btn"
          onClick={loadTagTree}
          aria-label="刷新标签树"
          title="刷新"
        >
          🔄
        </button>
      </div>
      <div className="tag-tree-sel-content">
        {tree.map(node => renderNode(node, 0))}
      </div>
    </div>
  );
}
