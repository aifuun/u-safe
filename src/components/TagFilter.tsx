import './TagFilter.css';

interface TagFilterProps {
  filterMode: 'AND' | 'OR';
  recursive: boolean;
  selectedCount: number;
  onFilterModeChange: (mode: 'AND' | 'OR') => void;
  onRecursiveChange: (recursive: boolean) => void;
  onClear: () => void;
}

/**
 * TagFilter 组件
 *
 * 标签过滤模式切换器
 * - AND/OR 模式切换
 * - 递归选项
 * - 清除过滤器
 */
export function TagFilter({
  filterMode,
  recursive,
  selectedCount,
  onFilterModeChange,
  onRecursiveChange,
  onClear
}: TagFilterProps) {
  return (
    <div className="tag-filter">
      <div className="tag-filter__section">
        <label className="tag-filter__label">过滤模式:</label>
        <div className="tag-filter__mode-group" role="group" aria-label="过滤模式选择">
          <button
            className={`tag-filter__mode-btn ${filterMode === 'OR' ? 'tag-filter__mode-btn--active' : ''}`}
            onClick={() => onFilterModeChange('OR')}
            aria-pressed={filterMode === 'OR'}
            title="文件包含任一标签即可"
          >
            OR（或）
          </button>
          <button
            className={`tag-filter__mode-btn ${filterMode === 'AND' ? 'tag-filter__mode-btn--active' : ''}`}
            onClick={() => onFilterModeChange('AND')}
            aria-pressed={filterMode === 'AND'}
            title="文件必须包含所有标签"
          >
            AND（与）
          </button>
        </div>
      </div>

      <div className="tag-filter__section">
        <label className="tag-filter__checkbox-label">
          <input
            type="checkbox"
            checked={recursive}
            onChange={(e) => onRecursiveChange(e.target.checked)}
            aria-label="包含子标签"
          />
          <span>包含子标签</span>
        </label>
      </div>

      <div className="tag-filter__section">
        <span className="tag-filter__count" aria-live="polite">
          已选 <strong>{selectedCount}</strong> 个标签
        </span>
        {selectedCount > 0 && (
          <button
            className="tag-filter__clear-btn"
            onClick={onClear}
            aria-label="清除所有选中的标签"
          >
            清除
          </button>
        )}
      </div>
    </div>
  );
}
