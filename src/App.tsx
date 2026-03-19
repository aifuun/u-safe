import { ViewSwitcher } from './components/ViewSwitcher';
import { AllFilesView } from './components/AllFilesView';
import { TagTreeWithSelection } from './components/TagTreeWithSelection';
import { TagFilter } from './components/TagFilter';
import { SearchBar } from './components/SearchBar';
import { TagFileList } from './components/TagFileList';
import { EncryptedFilesView } from './components/EncryptedFilesView';
import { RecentFilesView } from './components/RecentFilesView';
import { useViewStore } from './stores/viewStore';
import './App.css';

function App() {
  // Zustand store - 视图状态管理
  const {
    currentView,
    setView,
    selectedTagIds,
    setSelectedTagIds,
    filterMode,
    setFilterMode,
    recursive,
    setRecursive,
    searchQuery,
    setSearchQuery,
    resetTagView,
  } = useViewStore();

  const handleSelectionChange = (tagIds: string[]) => {
    console.log('[app] 标签选择变化:', tagIds);
    setSelectedTagIds(tagIds);
  };

  const handleClearFilters = () => {
    console.log('[app] 清除过滤器');
    resetTagView();
  };

  const handleFileClick = (fileId: number) => {
    console.log('[app] 文件点击:', fileId);
    // TODO: 实现文件详情/操作
  };

  const handleViewChange = (view: typeof currentView) => {
    console.info('[app:view:switch]', { from: currentView, to: view });
    setView(view);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-top">
          <h1>U-Safe 标签系统 Demo</h1>
          <p className="app-subtitle">Phase 4: View Switching（视图切换）</p>
        </div>
        <div className="header-nav">
          <ViewSwitcher currentView={currentView} onViewChange={handleViewChange} />
        </div>
      </header>

      <main className="app-main">
        {/* 标签视图: 侧边栏 + 主内容区 */}
        {currentView === 'tag-view' && (
          <>
            <aside className="app-sidebar">
              <TagTreeWithSelection
                selectedTagIds={selectedTagIds}
                onSelectionChange={handleSelectionChange}
              />
            </aside>

            <section className="app-content">
              <div className="content-toolbar">
                <TagFilter
                  filterMode={filterMode}
                  recursive={recursive}
                  selectedCount={selectedTagIds.length}
                  onFilterModeChange={setFilterMode}
                  onRecursiveChange={setRecursive}
                  onClear={handleClearFilters}
                />
                <SearchBar
                  onSearch={setSearchQuery}
                  placeholder="搜索文件名..."
                />
              </div>

              <div className="content-body">
                <TagFileList
                  selectedTagIds={selectedTagIds}
                  filterMode={filterMode}
                  recursive={recursive}
                  nameQuery={searchQuery}
                  onFileClick={handleFileClick}
                />
              </div>
            </section>
          </>
        )}

        {/* 其他视图: 全宽内容区 */}
        {currentView === 'all-files' && (
          <section className="app-content app-content--full">
            <AllFilesView onFileClick={handleFileClick} />
          </section>
        )}

        {currentView === 'encrypted-only' && (
          <section className="app-content app-content--full">
            <EncryptedFilesView onFileClick={handleFileClick} />
          </section>
        )}

        {currentView === 'recent' && (
          <section className="app-content app-content--full">
            <RecentFilesView onFileClick={handleFileClick} days={7} />
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
