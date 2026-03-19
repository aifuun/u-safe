import { useEffect, useRef } from 'react';

export interface TagKeyboardHandlers {
  onRename?: () => void;
  onDelete?: () => void;
  onDuplicate?: () => void;
  onNewChild?: () => void;
  onEdit?: () => void;
  onFocusSearch?: () => void;
  onSelectAll?: () => void;
  onClearSelection?: () => void;
}

/**
 * 标签键盘快捷键 Hook
 *
 * 快捷键说明:
 * - F2: 重命名选中标签
 * - Delete: 删除选中标签
 * - Ctrl+D: 复制标签
 * - Ctrl+N: 新建子标签
 * - Ctrl+E: 编辑选中标签
 * - Ctrl+F: 聚焦搜索框
 * - Ctrl+A: 全选文件
 * - Escape: 清除选择
 */
export function useTagKeyboardShortcuts(handlers: TagKeyboardHandlers) {
  // 使用 ref 保持最新的 handlers 引用
  const handlersRef = useRef(handlers);

  useEffect(() => {
    handlersRef.current = handlers;
  }, [handlers]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // 如果焦点在输入框中，跳过某些快捷键
      const target = e.target as HTMLElement;
      const isInputFocused =
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable;

      // F2: 重命名
      if (e.key === 'F2' && !isInputFocused) {
        e.preventDefault();
        handlersRef.current.onRename?.();
        console.info('[shortcut:f2] 触发重命名');
        return;
      }

      // Delete: 删除
      if (e.key === 'Delete' && !isInputFocused) {
        e.preventDefault();
        handlersRef.current.onDelete?.();
        console.info('[shortcut:delete] 触发删除');
        return;
      }

      // Escape: 清除选择
      if (e.key === 'Escape') {
        e.preventDefault();
        handlersRef.current.onClearSelection?.();
        console.info('[shortcut:escape] 清除选择');
        return;
      }

      // Ctrl/Cmd + D: 复制
      if ((e.ctrlKey || e.metaKey) && e.key === 'd' && !isInputFocused) {
        e.preventDefault();
        handlersRef.current.onDuplicate?.();
        console.info('[shortcut:ctrl+d] 触发复制');
        return;
      }

      // Ctrl/Cmd + N: 新建子标签
      if ((e.ctrlKey || e.metaKey) && e.key === 'n' && !isInputFocused) {
        e.preventDefault();
        handlersRef.current.onNewChild?.();
        console.info('[shortcut:ctrl+n] 触发新建子标签');
        return;
      }

      // Ctrl/Cmd + E: 编辑
      if ((e.ctrlKey || e.metaKey) && e.key === 'e' && !isInputFocused) {
        e.preventDefault();
        handlersRef.current.onEdit?.();
        console.info('[shortcut:ctrl+e] 触发编辑');
        return;
      }

      // Ctrl/Cmd + F: 聚焦搜索
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        handlersRef.current.onFocusSearch?.();
        console.info('[shortcut:ctrl+f] 聚焦搜索');
        return;
      }

      // Ctrl/Cmd + A: 全选（仅当不在输入框中）
      if ((e.ctrlKey || e.metaKey) && e.key === 'a' && !isInputFocused) {
        e.preventDefault();
        handlersRef.current.onSelectAll?.();
        console.info('[shortcut:ctrl+a] 全选');
        return;
      }
    };

    // 添加键盘事件监听
    window.addEventListener('keydown', handleKeyDown);

    // 清理函数
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []); // 空依赖数组，因为使用 ref 保持最新的 handlers
}

/**
 * 获取快捷键显示文本
 * 根据操作系统返回对应的修饰键符号
 */
export function getShortcutDisplay(shortcut: string): string {
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
  const ctrl = isMac ? '⌘' : 'Ctrl';

  return shortcut
    .replace('Ctrl', ctrl)
    .replace('cmd', '⌘')
    .replace('alt', isMac ? '⌥' : 'Alt')
    .replace('shift', isMac ? '⇧' : 'Shift');
}

/**
 * 快捷键帮助信息
 */
export const TAG_SHORTCUTS = [
  { key: 'F2', description: '重命名标签' },
  { key: 'Delete', description: '删除标签' },
  { key: 'Ctrl+D', description: '复制标签' },
  { key: 'Ctrl+N', description: '新建子标签' },
  { key: 'Ctrl+E', description: '编辑标签' },
  { key: 'Ctrl+F', description: '搜索标签' },
  { key: 'Ctrl+A', description: '全选文件' },
  { key: 'Escape', description: '清除选择' },
] as const;
