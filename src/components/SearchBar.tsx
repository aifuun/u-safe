import { useState, useEffect } from 'react';
import './SearchBar.css';

interface SearchBarProps {
  onSearch: (query: string) => void;
  debounceMs?: number;
  placeholder?: string;
}

/**
 * SearchBar 组件
 *
 * 搜索输入框，支持防抖和清除功能
 */
export function SearchBar({
  onSearch,
  debounceMs = 300,
  placeholder = '搜索文件名...'
}: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  // 防抖搜索
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsSearching(false);
      onSearch(query);
    }, debounceMs);

    if (query) {
      setIsSearching(true);
    }

    return () => {
      clearTimeout(timer);
    };
  }, [query, debounceMs, onSearch]);

  const handleClear = () => {
    setQuery('');
    setIsSearching(false);
    onSearch('');
  };

  return (
    <div className="search-bar">
      <div className="search-bar__input-wrapper">
        <span className="search-bar__icon" aria-hidden="true">🔍</span>
        <input
          type="text"
          className="search-bar__input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          aria-label="搜索文件名"
        />
        {query && (
          <button
            className="search-bar__clear"
            onClick={handleClear}
            aria-label="清除搜索"
            type="button"
          >
            ✕
          </button>
        )}
        {isSearching && (
          <span className="search-bar__loading" aria-label="搜索中" />
        )}
      </div>
    </div>
  );
}
