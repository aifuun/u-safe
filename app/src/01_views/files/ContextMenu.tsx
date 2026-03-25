import React, { useEffect, useRef, useCallback } from 'react';
import type { FileNode, FileOperation } from '@/modules/files/types';
import './ContextMenu.css';

interface ContextMenuProps {
  /** 目标文件节点 */
  node: FileNode | null;
  /** 菜单位置 */
  position: { x: number; y: number } | null;
  /** 关闭菜单回调 */
  onClose: () => void;
  /** 操作选择回调 */
  onAction: (operation: FileOperation, node: FileNode) => void;
}

/**
 * 文件右键菜单组件
 *
 * 根据文件状态显示可用操作：
 * - 未加密文件：加密、重命名、删除
 * - 已加密文件：解密、重命名、删除
 * - 文件夹：重命名、删除（加密/解密整个文件夹待后续支持）
 */
export const ContextMenu: React.FC<ContextMenuProps> = ({ node, position, onClose, onAction }) => {
  const menuRef = useRef<HTMLDivElement>(null);

  // 点击外部关闭菜单
  useEffect(() => {
    if (!position) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [position, onClose]);

  // ESC 键关闭菜单
  useEffect(() => {
    if (!position) return;

    const handleEsc = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, [position, onClose]);

  const handleAction = useCallback(
    (operation: FileOperation) => {
      if (node) {
        onAction(operation, node);
        onClose();
      }
    },
    [node, onAction, onClose]
  );

  if (!position || !node) return null;

  // 判断文件是否已加密（通过文件名或元数据）
  // MVP: 简化判断，通过扩展名 .enc 或特定标记
  const isEncrypted = node.name.endsWith('.enc') || node.name.includes('🔒');

  // 可用操作
  const showEncrypt = !node.is_dir && !isEncrypted;
  const showDecrypt = !node.is_dir && isEncrypted;
  const showRename = true; // 所有文件/文件夹都可重命名
  const showDelete = true; // 所有文件/文件夹都可删除

  return (
    <div
      ref={menuRef}
      className="context-menu"
      style={{
        top: `${position.y}px`,
        left: `${position.x}px`,
      }}
      role="menu"
      aria-label="文件操作菜单"
    >
      {showEncrypt && (
        <button
          className="context-menu__item"
          onClick={() => handleAction('encrypt')}
          role="menuitem"
        >
          <span className="context-menu__icon">🔒</span>
          <span className="context-menu__label">加密</span>
        </button>
      )}

      {showDecrypt && (
        <button
          className="context-menu__item"
          onClick={() => handleAction('decrypt')}
          role="menuitem"
        >
          <span className="context-menu__icon">🔓</span>
          <span className="context-menu__label">解密</span>
        </button>
      )}

      {showRename && (
        <button
          className="context-menu__item"
          onClick={() => handleAction('rename')}
          role="menuitem"
        >
          <span className="context-menu__icon">✏️</span>
          <span className="context-menu__label">重命名</span>
        </button>
      )}

      {showDelete && (
        <button
          className="context-menu__item context-menu__item--danger"
          onClick={() => handleAction('delete')}
          role="menuitem"
        >
          <span className="context-menu__icon">🗑️</span>
          <span className="context-menu__label">删除</span>
        </button>
      )}
    </div>
  );
};
