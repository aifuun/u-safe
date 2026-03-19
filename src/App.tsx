import { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { TagCreateForm } from './components/TagCreateForm';

interface Tag {
  tag_id: string;
  tag_name: string;
  tag_color?: string;
  parent_tag_id?: string;
  tag_level: number;
  full_path: string;
  created_at: string;
  updated_at: string;
  usage_count: number;
}

function App() {
  const [message, setMessage] = useState('');
  const [createdTags, setCreatedTags] = useState<Tag[]>([]);

  const testIPC = async () => {
    try {
      const response = await invoke<string>('hello_world');
      setMessage(response);
    } catch (error) {
      setMessage(`Error: ${error}`);
    }
  };

  const testDatabase = async () => {
    try {
      const response = await invoke<string>('test_db_connection');
      setMessage(response);
    } catch (error) {
      setMessage(`Error: ${error}`);
    }
  };

  const handleTagCreated = (tag: Tag) => {
    setCreatedTags((prev) => [...prev, tag]);
    setMessage(`✅ 成功创建标签: ${tag.tag_name} (${tag.full_path})`);
  };

  const handleTagError = (error: string) => {
    setMessage(`❌ 创建失败: ${error}`);
  };

  return (
    <div className="container">
      <h1>U-Safe - 万能保险箱</h1>
      <p>欢迎使用 U盘文件加密管理工具</p>

      <div className="card">
        <h2>Phase 1.1: 标签创建功能测试</h2>
        <p>Issue #21 - Tag System Implementation</p>
        {message && <p className="message">{message}</p>}

        <div style={{ display: 'flex', gap: '10px', marginTop: '10px', marginBottom: '20px' }}>
          <button onClick={() => setMessage('Hello from U-Safe!')}>
            测试 React
          </button>
          <button onClick={testIPC}>
            测试 IPC (Rust)
          </button>
          <button onClick={testDatabase}>
            测试数据库连接
          </button>
        </div>

        <hr style={{ margin: '20px 0', border: 'none', borderTop: '1px solid #e5e7eb' }} />

        <TagCreateForm
          onSuccess={handleTagCreated}
          onError={handleTagError}
        />

        {createdTags.length > 0 && (
          <div style={{ marginTop: '20px' }}>
            <h3>已创建的标签</h3>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {createdTags.map((tag) => (
                <li
                  key={tag.tag_id}
                  style={{
                    padding: '8px',
                    margin: '4px 0',
                    background: '#f3f4f6',
                    borderRadius: '4px',
                    borderLeft: `4px solid ${tag.tag_color || '#3b82f6'}`,
                  }}
                >
                  <strong>{tag.tag_name}</strong> - {tag.full_path}
                  <br />
                  <small style={{ color: '#6b7280' }}>
                    Level: {tag.tag_level} | ID: {tag.tag_id.slice(0, 8)}...
                  </small>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
