import { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { TagTree } from './components/TagTree';
import { TagCreateForm } from './components/TagCreateForm';
import { TagEditForm } from './components/TagEditForm';
import { DeleteTagDialog } from './components/DeleteTagDialog';
import { TagNode, Tag } from './types/tag';
import './App.css';

function App() {
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTag, setEditingTag] = useState<Tag | null>(null);
  const [parentForNew, setParentForNew] = useState<TagNode | null>(null);
  const [deletingTag, setDeletingTag] = useState<TagNode | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleTagSelect = (tagId: string) => {
    console.log('[app] 选中标签:', tagId);
    setSelectedTag(tagId);
  };

  const handleTagEdit = (node: TagNode) => {
    console.log('[app] 编辑标签:', node);
    // Convert TagNode to Tag (remove children)
    const tag: Tag = {
      tag_id: node.tag_id,
      tag_name: node.tag_name,
      tag_color: node.tag_color,
      parent_tag_id: node.parent_tag_id,
      tag_level: node.tag_level,
      full_path: node.full_path,
      created_at: node.created_at,
      updated_at: node.updated_at,
      usage_count: node.usage_count,
    };
    setEditingTag(tag);
  };

  const handleTagDelete = (node: TagNode) => {
    console.log('[app] 删除标签:', node);
    setDeletingTag(node);
  };

  const handleDeleteConfirm = async (tagId: string, force: boolean) => {
    try {
      console.log('[app] 确认删除标签:', tagId, 'force=', force);
      await invoke('delete_tag', { tagId, force });
      console.log('[app] 删除成功');
      setDeletingTag(null);
      // 刷新标签树
      setRefreshKey(prev => prev + 1);
    } catch (err) {
      console.error('[app] 删除失败:', err);
      throw err; // Re-throw to let dialog handle error display
    }
  };

  const handleDeleteCancel = () => {
    console.log('[app] 取消删除');
    setDeletingTag(null);
  };

  const handleAddChild = (parent: TagNode) => {
    console.log('[app] 添加子标签:', parent);
    setParentForNew(parent);
    setShowCreateForm(true);
  };

  const handleCreateSuccess = (tag: Tag) => {
    console.log('[app] 创建成功:', tag);
    setShowCreateForm(false);
    setParentForNew(null);
    // 刷新标签树
    setRefreshKey(prev => prev + 1);
  };

  const handleUpdateSuccess = (tag: Tag) => {
    console.log('[app] 更新成功:', tag);
    setEditingTag(null);
    // 刷新标签树
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>U-Safe 标签系统 Demo</h1>
        <p className="app-subtitle">Phase 1.5: 标签删除 + 级联检查</p>
      </header>

      <main className="app-main">
        <aside className="app-sidebar">
          <div className="sidebar-header">
            <button
              className="btn-create-tag"
              onClick={() => {
                setParentForNew(null);
                setShowCreateForm(true);
              }}
            >
              ➕ 创建标签
            </button>
          </div>

          <TagTree
            key={refreshKey}
            onTagSelect={handleTagSelect}
            onTagEdit={handleTagEdit}
            onTagDelete={handleTagDelete}
            onAddChild={handleAddChild}
          />
        </aside>

        <section className="app-content">
          {showCreateForm && (
            <div className="form-container">
              <h2>创建标签</h2>
              {parentForNew && (
                <p className="form-hint">
                  父标签: <strong>{parentForNew.full_path}</strong>
                </p>
              )}
              <TagCreateForm
                parentTag={parentForNew as any}
                onSuccess={handleCreateSuccess}
                onError={(err) => alert(`创建失败: ${err}`)}
              />
              <button
                className="btn-cancel"
                onClick={() => {
                  setShowCreateForm(false);
                  setParentForNew(null);
                }}
              >
                取消
              </button>
            </div>
          )}

          {editingTag && (
            <div className="form-container">
              <h2>编辑标签</h2>
              <p className="form-hint">
                路径: <strong>{editingTag.full_path}</strong>
              </p>
              <TagEditForm
                tag={editingTag}
                onSuccess={handleUpdateSuccess}
                onError={(err) => alert(`更新失败: ${err}`)}
                onCancel={() => setEditingTag(null)}
              />
            </div>
          )}

          {!showCreateForm && !editingTag && (
            <div className="content-placeholder">
              <h2>标签详情</h2>
              {selectedTag ? (
                <p>选中的标签 ID: <code>{selectedTag}</code></p>
              ) : (
                <p className="hint">从左侧选择一个标签</p>
              )}
            </div>
          )}
        </section>
      </main>

      {/* 删除标签对话框 */}
      <DeleteTagDialog
        tagNode={deletingTag}
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />
    </div>
  );
}

export default App;
