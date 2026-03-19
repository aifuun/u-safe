import { ViewType } from '../stores/viewStore';
import './ViewSwitcher.css';

interface ViewSwitcherProps {
  currentView: ViewType;
  onViewChange: (view: ViewType) => void;
}

// 视图配置
const VIEW_CONFIGS: Array<{
  id: ViewType;
  label: string;
  icon: string;
  ariaLabel: string;
}> = [
  {
    id: 'all-files',
    label: '全部文件',
    icon: '📁',
    ariaLabel: '切换到全部文件视图',
  },
  {
    id: 'tag-view',
    label: '标签视图',
    icon: '🏷️',
    ariaLabel: '切换到标签视图',
  },
  {
    id: 'encrypted-only',
    label: '仅加密',
    icon: '🔒',
    ariaLabel: '切换到仅加密文件视图',
  },
  {
    id: 'recent',
    label: '最近添加',
    icon: '🕒',
    ariaLabel: '切换到最近添加文件视图',
  },
];

/**
 * ViewSwitcher 组件 - 视图切换器
 *
 * 功能:
 * - Tab 导航切换视图（全部文件、标签视图、仅加密、最近）
 * - 当前视图高亮显示
 * - 支持键盘导航（箭头键）
 * - 设计 token 驱动的样式
 * - 响应式设计（移动端堆叠）
 * - WCAG AAA 可访问性
 *
 * 键盘导航:
 * - Tab: 聚焦到切换器
 * - 左/右箭头: 切换视图
 * - Home: 跳到第一个视图
 * - End: 跳到最后一个视图
 * - Enter/Space: 激活当前视图
 */
export function ViewSwitcher({ currentView, onViewChange }: ViewSwitcherProps) {
  const handleKeyDown = (e: React.KeyboardEvent, viewId: ViewType) => {
    const currentIndex = VIEW_CONFIGS.findIndex((v) => v.id === currentView);
    let newIndex = currentIndex;

    switch (e.key) {
      case 'ArrowLeft':
        e.preventDefault();
        newIndex = currentIndex > 0 ? currentIndex - 1 : VIEW_CONFIGS.length - 1;
        break;
      case 'ArrowRight':
        e.preventDefault();
        newIndex = currentIndex < VIEW_CONFIGS.length - 1 ? currentIndex + 1 : 0;
        break;
      case 'Home':
        e.preventDefault();
        newIndex = 0;
        break;
      case 'End':
        e.preventDefault();
        newIndex = VIEW_CONFIGS.length - 1;
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        onViewChange(viewId);
        return;
      default:
        return;
    }

    onViewChange(VIEW_CONFIGS[newIndex].id);
  };

  return (
    <div className="view-switcher" role="tablist" aria-label="视图切换">
      {VIEW_CONFIGS.map((view) => {
        const isActive = currentView === view.id;

        return (
          <button
            key={view.id}
            type="button"
            role="tab"
            aria-selected={isActive}
            aria-controls={`${view.id}-panel`}
            aria-label={view.ariaLabel}
            className={`view-switcher__tab ${isActive ? 'view-switcher__tab--active' : ''}`}
            onClick={() => onViewChange(view.id)}
            onKeyDown={(e) => handleKeyDown(e, view.id)}
            tabIndex={isActive ? 0 : -1}
          >
            <span className="view-switcher__icon" aria-hidden="true">
              {view.icon}
            </span>
            <span className="view-switcher__label">{view.label}</span>
          </button>
        );
      })}
    </div>
  );
}
