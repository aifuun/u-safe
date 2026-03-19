import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import './TagStatsPanel.css';

interface Tag {
  tag_id: string;
  tag_name: string;
  tag_color?: string | null;
  full_path: string;
  usage_count: number;
}

interface TagStatistics {
  total_tags: number;
  total_files: number;
  total_associations: number;
  most_used_tags: Array<[Tag, number]>;
  orphaned_tags: Tag[];
  max_depth_used: number;
  avg_files_per_tag: number;
}

export function TagStatsPanel() {
  const [stats, setStats] = useState<TagStatistics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 加载统计数据
  const loadStatistics = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await invoke<TagStatistics>('get_tag_statistics');
      setStats(result);
      console.info('[tag:statistics:loaded]', {
        totalTags: result.total_tags,
        totalFiles: result.total_files,
        totalAssociations: result.total_associations,
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setError(errorMessage);
      console.error('[tag:statistics:failed]', { error: errorMessage });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadStatistics();
  }, []);

  if (isLoading) {
    return (
      <div className="tag-stats-panel">
        <div className="tag-stats-panel__loading">
          <div className="tag-stats-panel__spinner" />
          <span>加载统计数据...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="tag-stats-panel">
        <div className="tag-stats-panel__error">
          <span>❌ 加载失败: {error}</span>
          <button onClick={loadStatistics} className="tag-stats-panel__retry-btn">
            重试
          </button>
        </div>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  return (
    <div className="tag-stats-panel">
      <div className="tag-stats-panel__header">
        <h2>标签系统统计</h2>
        <button onClick={loadStatistics} className="tag-stats-panel__refresh-btn" title="刷新统计">
          🔄
        </button>
      </div>

      {/* 总览卡片 */}
      <div className="tag-stats-panel__overview">
        <div className="tag-stats-card">
          <div className="tag-stats-card__icon">🏷️</div>
          <div className="tag-stats-card__content">
            <div className="tag-stats-card__value">{stats.total_tags}</div>
            <div className="tag-stats-card__label">总标签数</div>
          </div>
        </div>

        <div className="tag-stats-card">
          <div className="tag-stats-card__icon">📁</div>
          <div className="tag-stats-card__content">
            <div className="tag-stats-card__value">{stats.total_files}</div>
            <div className="tag-stats-card__label">总文件数</div>
          </div>
        </div>

        <div className="tag-stats-card">
          <div className="tag-stats-card__icon">🔗</div>
          <div className="tag-stats-card__content">
            <div className="tag-stats-card__value">{stats.total_associations}</div>
            <div className="tag-stats-card__label">关联数</div>
          </div>
        </div>

        <div className="tag-stats-card">
          <div className="tag-stats-card__icon">📊</div>
          <div className="tag-stats-card__content">
            <div className="tag-stats-card__value">{stats.avg_files_per_tag.toFixed(1)}</div>
            <div className="tag-stats-card__label">平均文件/标签</div>
          </div>
        </div>
      </div>

      {/* 层级深度 */}
      <div className="tag-stats-section">
        <h3>层级深度</h3>
        <div className="tag-stats-depth">
          <div className="tag-stats-depth__bar">
            <div
              className="tag-stats-depth__fill"
              style={{ width: `${(stats.max_depth_used / 5) * 100}%` }}
            />
          </div>
          <div className="tag-stats-depth__label">
            当前最大深度: <strong>{stats.max_depth_used}</strong> / 5
          </div>
        </div>
      </div>

      {/* 最常用标签 */}
      {stats.most_used_tags.length > 0 && (
        <div className="tag-stats-section">
          <h3>最常用标签 (Top {stats.most_used_tags.length})</h3>
          <div className="tag-stats-list">
            {stats.most_used_tags.map(([tag, count], index) => (
              <div key={tag.tag_id} className="tag-stats-list-item">
                <div className="tag-stats-list-item__rank">#{index + 1}</div>
                <div className="tag-stats-list-item__tag">
                  {tag.tag_color && (
                    <span
                      className="tag-stats-list-item__color"
                      style={{ backgroundColor: tag.tag_color }}
                    />
                  )}
                  <div className="tag-stats-list-item__info">
                    <span className="tag-stats-list-item__name">{tag.tag_name}</span>
                    <span className="tag-stats-list-item__path">{tag.full_path}</span>
                  </div>
                </div>
                <div className="tag-stats-list-item__count">{count} 个文件</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 孤立标签 */}
      {stats.orphaned_tags.length > 0 && (
        <div className="tag-stats-section">
          <h3>孤立标签 ({stats.orphaned_tags.length})</h3>
          <div className="tag-stats-warning">
            <span className="tag-stats-warning__icon">⚠️</span>
            <span>这些标签没有关联任何文件，可以考虑删除</span>
          </div>
          <div className="tag-stats-orphaned">
            {stats.orphaned_tags.slice(0, 10).map((tag) => (
              <div key={tag.tag_id} className="tag-stats-orphaned-item">
                {tag.tag_color && (
                  <span
                    className="tag-stats-orphaned-item__color"
                    style={{ backgroundColor: tag.tag_color }}
                  />
                )}
                <span className="tag-stats-orphaned-item__name">{tag.full_path}</span>
              </div>
            ))}
            {stats.orphaned_tags.length > 10 && (
              <div className="tag-stats-orphaned-more">
                还有 {stats.orphaned_tags.length - 10} 个孤立标签...
              </div>
            )}
          </div>
        </div>
      )}

      {/* 空状态 */}
      {stats.total_tags === 0 && (
        <div className="tag-stats-empty">
          <div className="tag-stats-empty__icon">📭</div>
          <div className="tag-stats-empty__title">还没有标签</div>
          <div className="tag-stats-empty__description">创建第一个标签来开始组织文件</div>
        </div>
      )}
    </div>
  );
}
