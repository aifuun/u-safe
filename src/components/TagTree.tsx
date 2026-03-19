import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { TagNode } from '../types/tag';
import { ContextMenu, MenuItem, MenuSeparator } from './ContextMenu';
import './TagTree.css';

interface TagTreeProps {
  onTagSelect?: (tagId: string) => void;
  onTagEdit?: (tagNode: TagNode) => void;
  onTagDelete?: (tagNode: TagNode) => void;
  onAddChild?: (parentNode: TagNode) => void;
  onRename?: (tagNode: TagNode) => void;
  onDuplicate?: (tagNode: TagNode) => void;
  onExport?: (tagNode: TagNode) => void;
}

/**
 * 标签树组件
 *
 * 功能：
 * - 显示层级标签结构（最多5层）
 * - 展开/折叠子标签
 * - 点击标签触发选中事件
 * - 右键菜单（编辑、删除、添加子标签）
 * - 自动加载标签树数据
 */
export function TagTree({
  onTagSelect,
  onTagEdit,
  onTagDelete,
  onAddChild,
  onRename,
  onDuplicate,
  onExport
}: TagTreeProps) {
  const [tree, setTree] = useState<TagNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  // 拖拽状态
  const [draggingTagId, setDraggingTagId] = useState<string | null>(null);
  const [dropTargetId, setDropTargetId] = useState<string | null>(null);

  // 上下文菜单状态
  const [contextMenu, setContextMenu] = useState<{
    tag: TagNode;
    x: number;
    y: number;
  } | null>(null);

  // 加载标签树
  const loadTagTree = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('[tag:tree:load] 开始加载标签树');

      const result = await invoke<TagNode[]>('get_tag_tree');
      console.log('[tag:tree:load:success] 加载了', result.length, '个根标签');

      setTree(result);

      // 默认展开第一层
      const firstLevelIds = result.map(node => node.tag_id);
      setExpandedNodes(new Set(firstLevelIds));
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      console.error('[tag:tree:load:failed]', errorMsg);
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

  // 处理标签点击
  const handleTagClick = (tagId: string) => {
    if (onTagSelect) {
      onTagSelect(tagId);
    }
  };

  // 获取标签深度
  const getTagDepth = (tagId: string, currentTree: TagNode[] = tree, depth = 0): number => {
    for (const node of currentTree) {
      if (node.tag_id === tagId) {
        return depth;
      }
      if (node.children && node.children.length > 0) {
        const childDepth = getTagDepth(tagId, node.children, depth + 1);
        if (childDepth > -1) return childDepth;
      }
    }
    return -1;
  };

  // 获取子树深度
  const getSubtreeDepth = (tagId: string, currentTree: TagNode[] = tree): number => {
    for (const node of currentTree) {
      if (node.tag_id === tagId) {
        if (!node.children || node.children.length === 0) return 0;
        return 1 + Math.max(...node.children.map(child => getSubtreeDepth(child.tag_id, node.children)));
      }
      if (node.children && node.children.length > 0) {
        const depth = getSubtreeDepth(tagId, node.children);
        if (depth > -1) return depth;
      }
    }
    return -1;
  };

  // 检查是否是后代节点
  const isDescendant = (childId: string, ancestorId: string, currentTree: TagNode[] = tree): boolean => {
    for (const node of currentTree) {
      if (node.tag_id === ancestorId) {
        // 找到祖先节点，检查其子树
        return checkInSubtree(childId, node.children || []);
      }
      if (node.children && node.children.length > 0) {
        if (isDescendant(childId, ancestorId, node.children)) {
          return true;
        }
      }
    }
    return false;
  };

  const checkInSubtree = (tagId: string, subtree: TagNode[]): boolean => {
    for (const node of subtree) {
      if (node.tag_id === tagId) return true;
      if (node.children && checkInSubtree(tagId, node.children)) return true;
    }
    return false;
  };

  // 验证拖放目标
  const canDropOn = (draggedId: string, targetId: string): boolean => {
    // 不能拖到自己身上
    if (draggedId === targetId) return false;

    // 不能拖到自己的后代节点上（避免循环）
    if (isDescendant(targetId, draggedId)) return false;

    // 检查深度限制（最多5层）
    const targetDepth = getTagDepth(targetId);
    const draggedTreeDepth = getSubtreeDepth(draggedId);
    if (targetDepth + draggedTreeDepth >= 4) return false; // 0-based, so 4 = 5 levels

    return true;
  };

  // 拖拽开始
  const handleDragStart = (e: React.DragEvent, tag: TagNode) => {
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('tagId', tag.tag_id);
    setDraggingTagId(tag.tag_id);
    console.log('[tag:drag:start]', { tagId: tag.tag_id, tagName: tag.tag_name });
  };

  // 拖拽结束
  const handleDragEnd = () => {
    setDraggingTagId(null);
    setDropTargetId(null);
    console.log('[tag:drag:end]');
  };

  // 拖拽经过
  const handleDragOver = (e: React.DragEvent, tag: TagNode) => {
    e.preventDefault();

    if (!draggingTagId) return;

    if (canDropOn(draggingTagId, tag.tag_id)) {
      e.dataTransfer.dropEffect = 'move';
      setDropTargetId(tag.tag_id);
    } else {
      e.dataTransfer.dropEffect = 'none';
      setDropTargetId(null);
    }
  };

  // 拖拽离开
  const handleDragLeave = () => {
    setDropTargetId(null);
  };

  // 放置
  const handleDrop = async (e: React.DragEvent, targetTag: TagNode) => {
    e.preventDefault();
    e.stopPropagation();

    const draggedId = draggingTagId;

    if (!draggedId || !canDropOn(draggedId, targetTag.tag_id)) {
      console.warn('[tag:drop:invalid]', { draggedId, targetId: targetTag.tag_id });
      setDraggingTagId(null);
      setDropTargetId(null);
      return;
    }

    try {
      console.log('[tag:drop:start]', { draggedId, targetId: targetTag.tag_id, targetName: targetTag.tag_name });

      // 调用后端更新父标签
      await invoke('update_tag', {
        request: {
          id: draggedId,
          parent_id: targetTag.tag_id
        }
      });

      console.log('[tag:drop:success]');

      // 刷新标签树
      await loadTagTree();
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      console.error('[tag:drop:failed]', errorMsg);
      setError(`移动标签失败: ${errorMsg}`);
    } finally {
      setDraggingTagId(null);
      setDropTargetId(null);
    }
  };

  // 右键菜单
  const handleContextMenu = (e: React.MouseEvent, tag: TagNode) => {
    e.preventDefault();
    e.stopPropagation();
    setContextMenu({
      tag,
      x: e.clientX,
      y: e.clientY
    });
    console.log('[tag:contextmenu:open]', { tagId: tag.tag_id, tagName: tag.tag_name });
  };

  const handleContextMenuClose = () => {
    setContextMenu(null);
    console.log('[tag:contextmenu:close]');
  };

  // 渲染单个标签节点
  const renderNode = (node: TagNode, depth: number = 0): JSX.Element => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = expandedNodes.has(node.tag_id);
    const isDragging = draggingTagId === node.tag_id;
    const isDropTarget = dropTargetId === node.tag_id;
    const isDropInvalid = draggingTagId && !canDropOn(draggingTagId, node.tag_id);

    return (
      <div key={node.tag_id} className="tag-tree-node">
        <div
          className={`tag-tree-item ${isDragging ? 'tag-tree-item--dragging' : ''} ${
            isDropTarget ? 'tag-tree-item--drop-target' : ''
          } ${isDropInvalid ? 'tag-tree-item--drop-invalid' : ''}`}
          style={{ paddingLeft: `${depth * 20}px` }}
          draggable
          onDragStart={(e) => handleDragStart(e, node)}
          onDragEnd={handleDragEnd}
          onDragOver={(e) => handleDragOver(e, node)}
          onDragLeave={handleDragLeave}
          onDrop={(e) => handleDrop(e, node)}
          onContextMenu={(e) => handleContextMenu(e, node)}
        >
          {/* 展开/折叠按钮 */}
          {hasChildren && (
            <button
              className="tag-tree-toggle"
              onClick={() => toggleExpand(node.tag_id)}
              aria-label={isExpanded ? '折叠' : '展开'}
            >
              {isExpanded ? '▼' : '▶'}
            </button>
          )}
          {!hasChildren && <span className="tag-tree-spacer" />}

          {/* 标签名称 */}
          <div
            className="tag-tree-label"
            onClick={() => handleTagClick(node.tag_id)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                handleTagClick(node.tag_id);
              }
            }}
          >
            {/* 颜色指示器 */}
            {node.tag_color && (
              <span
                className="tag-tree-color"
                style={{ backgroundColor: node.tag_color }}
                aria-hidden="true"
              />
            )}

            {/* 标签名称 */}
            <span className="tag-tree-name">{node.tag_name}</span>

            {/* 使用计数 */}
            {node.usage_count > 0 && (
              <span className="tag-tree-count">({node.usage_count})</span>
            )}
          </div>

          {/* 操作按钮 */}
          <div className="tag-tree-actions">
            {onAddChild && (
              <button
                className="tag-tree-action-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  onAddChild(node);
                }}
                aria-label="添加子标签"
                title="添加子标签"
              >
                ➕
              </button>
            )}
            {onTagEdit && (
              <button
                className="tag-tree-action-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  onTagEdit(node);
                }}
                aria-label="编辑标签"
                title="编辑"
              >
                ✏️
              </button>
            )}
            {onTagDelete && (
              <button
                className="tag-tree-action-btn tag-tree-action-btn--danger"
                onClick={(e) => {
                  e.stopPropagation();
                  onTagDelete(node);
                }}
                aria-label="删除标签"
                title="删除"
              >
                🗑️
              </button>
            )}
          </div>
        </div>

        {/* 子标签 */}
        {hasChildren && isExpanded && (
          <div className="tag-tree-children">
            {node.children.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  // 加载中状态
  if (loading) {
    return (
      <div className="tag-tree-loading">
        <div className="tag-tree-spinner" aria-label="加载中" />
        <p>加载标签树...</p>
      </div>
    );
  }

  // 错误状态
  if (error) {
    return (
      <div className="tag-tree-error">
        <p className="tag-tree-error-message">❌ 加载失败：{error}</p>
        <button
          className="tag-tree-retry-btn"
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
      <div className="tag-tree-empty">
        <p>暂无标签</p>
        <p className="tag-tree-empty-hint">创建第一个标签来开始整理文件</p>
      </div>
    );
  }

  // 渲染标签树
  return (
    <>
      <div className="tag-tree">
        <div className="tag-tree-header">
          <h3 className="tag-tree-title">标签</h3>
          <button
            className="tag-tree-refresh-btn"
            onClick={loadTagTree}
            aria-label="刷新"
            title="刷新标签树"
          >
            🔄
          </button>
        </div>
        <div className="tag-tree-content">
          {tree.map(node => renderNode(node, 0))}
        </div>
      </div>

      {/* 上下文菜单 */}
      {contextMenu && (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          isOpen={!!contextMenu}
          onClose={handleContextMenuClose}
        >
          {onRename && (
            <MenuItem
              icon="✏️"
              label="重命名"
              shortcut="F2"
              onClick={() => {
                onRename(contextMenu.tag);
                handleContextMenuClose();
              }}
            />
          )}
          {onTagEdit && (
            <MenuItem
              icon="⚙️"
              label="编辑颜色"
              onClick={() => {
                onTagEdit(contextMenu.tag);
                handleContextMenuClose();
              }}
            />
          )}
          {onAddChild && (
            <MenuItem
              icon="➕"
              label="添加子标签"
              shortcut="Ctrl+N"
              onClick={() => {
                onAddChild(contextMenu.tag);
                handleContextMenuClose();
              }}
            />
          )}
          {onDuplicate && (
            <MenuItem
              icon="📋"
              label="复制"
              shortcut="Ctrl+D"
              onClick={() => {
                onDuplicate(contextMenu.tag);
                handleContextMenuClose();
              }}
            />
          )}
          <MenuSeparator />
          {onExport && (
            <MenuItem
              icon="💾"
              label="导出"
              onClick={() => {
                onExport(contextMenu.tag);
                handleContextMenuClose();
              }}
            />
          )}
          <MenuSeparator />
          {onTagDelete && (
            <MenuItem
              icon="🗑️"
              label="删除"
              shortcut="Del"
              danger
              onClick={() => {
                onTagDelete(contextMenu.tag);
                handleContextMenuClose();
              }}
            />
          )}
        </ContextMenu>
      )}
    </>
  );
}
