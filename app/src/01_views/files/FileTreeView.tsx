import React, { useEffect, useCallback, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useFileTreeStore, getFolderIcon, getFileTypeIcon } from '@/modules/files';
import type { FileNode, FileOperation } from '@/modules/files/types';
import { ContextMenu } from './ContextMenu';
import './FileTreeView.css';

/**
 * 文件树节点组件（递归）
 */
const TreeNode: React.FC<{
  node: FileNode;
  level: number;
  onContextMenu: (event: React.MouseEvent, node: FileNode) => void;
}> = ({ node, level, onContextMenu }) => {
  const { expandedPaths, selectedPath, toggleExpanded, select } = useFileTreeStore();

  const isExpanded = expandedPaths.has(node.path);
  const isSelected = selectedPath === node.path;

  const handleToggle = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      if (node.is_dir) {
        toggleExpanded(node.path);
      }
    },
    [node.is_dir, node.path, toggleExpanded]
  );

  const handleSelect = useCallback(() => {
    select(node.path);
  }, [node.path, select]);

  const handleContextMenu = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      onContextMenu(e, node);
    },
    [node, onContextMenu]
  );

  // 文件夹图标
  const folderIcon = node.is_dir ? getFolderIcon(isExpanded) : '';

  // 文件类型图标
  const fileIcon = !node.is_dir ? getFileTypeIcon(node.file_type) : '';

  return (
    <div className="tree-node">
      <div
        className={`tree-node__content ${isSelected ? 'tree-node__content--selected' : ''}`}
        style={{ paddingLeft: `${level * 20}px` }}
        onClick={handleSelect}
        onContextMenu={handleContextMenu}
      >
        {/* 展开/折叠按钮 */}
        {node.is_dir && (
          <button
            className="tree-node__toggle"
            onClick={handleToggle}
            aria-label={isExpanded ? '折叠' : '展开'}
          >
            {isExpanded ? '▼' : '▶'}
          </button>
        )}

        {/* 文件/文件夹图标 */}
        <span className="tree-node__icon" role="img" aria-label={node.is_dir ? '文件夹' : '文件'}>
          {folderIcon || fileIcon}
        </span>

        {/* 文件名 */}
        <span className="tree-node__name">{node.name}</span>

        {/* 文件大小（仅文件显示） */}
        {!node.is_dir && node.size > 0 && (
          <span className="tree-node__size">{formatFileSize(node.size)}</span>
        )}
      </div>

      {/* 子节点（递归渲染） */}
      {node.is_dir && isExpanded && node.children && (
        <div className="tree-node__children">
          {node.children.map((child) => (
            <TreeNode key={child.path} node={child} level={level + 1} onContextMenu={onContextMenu} />
          ))}
        </div>
      )}
    </div>
  );
};

/**
 * 文件树视图组件
 */
export const FileTreeView: React.FC<{
  rootPath?: string;
}> = ({ rootPath }) => {
  const { root, loading, error, setRoot, setLoading, setError } = useFileTreeStore();
  const [contextMenu, setContextMenu] = useState<{
    node: FileNode;
    position: { x: number; y: number };
  } | null>(null);

  // 加载文件树
  const loadFileTree = useCallback(
    async (path: string) => {
      setLoading(true);
      setError(null);

      try {
        console.info('[file_tree:load:start]', { path });

        const fileTree = await invoke<FileNode>('scan_file_tree', { rootPath: path });

        console.info('[file_tree:load:done]', { path, nodes: countNodes(fileTree) });

        setRoot(fileTree);
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : String(err);
        console.error('[file_tree:load:failed]', { path, error: errorMsg });
        setError(errorMsg);
      } finally {
        setLoading(false);
      }
    },
    [setRoot, setLoading, setError]
  );

  // 初始加载
  useEffect(() => {
    if (rootPath) {
      loadFileTree(rootPath);
    }
  }, [rootPath, loadFileTree]);

  // 处理右键菜单
  const handleContextMenu = useCallback((event: React.MouseEvent, node: FileNode) => {
    setContextMenu({
      node,
      position: { x: event.clientX, y: event.clientY },
    });
  }, []);

  const handleCloseContextMenu = useCallback(() => {
    setContextMenu(null);
  }, []);

  const handleFileOperation = useCallback(
    async (operation: FileOperation, node: FileNode) => {
      console.info('[file_operation:start]', { operation, node: node.path });

      try {
        switch (operation) {
          case 'encrypt': {
            // 提示用户输入密码
            const password = prompt('请输入加密密码:');
            if (!password) {
              console.warn('[file_operation:cancelled] 用户取消加密');
              return;
            }

            console.info('[file_operation:encrypt:start]', { path: node.path });

            const encryptedPath = await invoke<string>('encrypt_file', {
              sourcePath: node.path,
              password,
            });

            console.info('[file_operation:encrypt:done]', { encryptedPath });
            alert(`文件已加密: ${encryptedPath}`);

            // 刷新文件树
            if (rootPath) {
              await loadFileTree(rootPath);
            }
            break;
          }

          case 'decrypt': {
            // 提示用户输入密码
            const password = prompt('请输入解密密码:');
            if (!password) {
              console.warn('[file_operation:cancelled] 用户取消解密');
              return;
            }

            console.info('[file_operation:decrypt:start]', { path: node.path });

            const decryptedPath = await invoke<string>('decrypt_file', {
              encryptedPath: node.path,
              password,
            });

            console.info('[file_operation:decrypt:done]', { decryptedPath });
            alert(`文件已解密: ${decryptedPath}`);

            // 刷新文件树
            if (rootPath) {
              await loadFileTree(rootPath);
            }
            break;
          }

          case 'rename':
            console.log('重命名:', node.path);
            alert('重命名功能待实现');
            break;

          case 'delete':
            const confirmDelete = confirm(`确认删除文件: ${node.name}?`);
            if (confirmDelete) {
              console.log('删除:', node.path);
              alert('删除功能待实现');
            }
            break;
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : String(err);
        console.error('[file_operation:failed]', { operation, error: errorMsg });
        alert(`操作失败: ${errorMsg}`);
      }
    },
    [rootPath, loadFileTree]
  );

  if (loading) {
    return (
      <div className="file-tree-view file-tree-view--loading">
        <div className="file-tree-view__spinner">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="file-tree-view file-tree-view--error">
        <div className="file-tree-view__error">
          <span role="img" aria-label="错误">
            ❌
          </span>{' '}
          {error}
        </div>
        <button className="file-tree-view__retry" onClick={() => rootPath && loadFileTree(rootPath)}>
          重试
        </button>
      </div>
    );
  }

  if (!root) {
    return (
      <div className="file-tree-view file-tree-view--empty">
        <p className="file-tree-view__empty-message">请选择要浏览的文件夹</p>
      </div>
    );
  }

  return (
    <div className="file-tree-view">
      <TreeNode node={root} level={0} onContextMenu={handleContextMenu} />

      {/* 右键菜单 */}
      <ContextMenu
        node={contextMenu?.node || null}
        position={contextMenu?.position || null}
        onClose={handleCloseContextMenu}
        onAction={handleFileOperation}
      />
    </div>
  );
};

/**
 * 格式化文件大小
 */
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
}

/**
 * 统计节点数量（用于日志）
 */
function countNodes(node: FileNode): number {
  let count = 1;
  if (node.children) {
    for (const child of node.children) {
      count += countNodes(child);
    }
  }
  return count;
}

// Icon mapping moved to adapters/iconMap.ts
