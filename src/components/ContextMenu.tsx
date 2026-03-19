import { useEffect, useRef, ReactNode } from 'react';
import './ContextMenu.css';

export interface ContextMenuProps {
  x: number;
  y: number;
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
}

export interface MenuItemProps {
  onClick: () => void;
  icon?: string;
  label: string;
  shortcut?: string;
  danger?: boolean;
  disabled?: boolean;
}

export interface MenuSeparatorProps {
  // 分隔线无需属性
}

/**
 * 上下文菜单组件
 * 提供右键菜单功能，自动处理位置和边界检测
 */
export function ContextMenu({ x, y, isOpen, onClose, children }: ContextMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null);

  // 处理点击外部关闭
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    // 延迟添加监听器，避免立即触发
    setTimeout(() => {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
    }, 0);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  // 调整菜单位置，防止超出屏幕
  useEffect(() => {
    if (!isOpen || !menuRef.current) return;

    const menu = menuRef.current;
    const rect = menu.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let adjustedX = x;
    let adjustedY = y;

    // 右边界检测
    if (x + rect.width > viewportWidth) {
      adjustedX = viewportWidth - rect.width - 10;
    }

    // 左边界检测
    if (adjustedX < 10) {
      adjustedX = 10;
    }

    // 下边界检测
    if (y + rect.height > viewportHeight) {
      adjustedY = viewportHeight - rect.height - 10;
    }

    // 上边界检测
    if (adjustedY < 10) {
      adjustedY = 10;
    }

    menu.style.left = `${adjustedX}px`;
    menu.style.top = `${adjustedY}px`;
  }, [isOpen, x, y]);

  if (!isOpen) return null;

  return (
    <div ref={menuRef} className="context-menu" role="menu">
      {children}
    </div>
  );
}

/**
 * 菜单项组件
 */
export function MenuItem({
  onClick,
  icon,
  label,
  shortcut,
  danger = false,
  disabled = false,
}: MenuItemProps) {
  const handleClick = () => {
    if (!disabled) {
      onClick();
    }
  };

  return (
    <button
      className={`context-menu-item ${danger ? 'context-menu-item--danger' : ''} ${
        disabled ? 'context-menu-item--disabled' : ''
      }`}
      onClick={handleClick}
      disabled={disabled}
      role="menuitem"
    >
      {icon && <span className="context-menu-item__icon">{icon}</span>}
      <span className="context-menu-item__label">{label}</span>
      {shortcut && <span className="context-menu-item__shortcut">{shortcut}</span>}
    </button>
  );
}

/**
 * 菜单分隔线组件
 */
export function MenuSeparator() {
  return <div className="context-menu-separator" role="separator" />;
}
