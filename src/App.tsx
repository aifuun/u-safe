import { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';

function App() {
  const [message, setMessage] = useState('');

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

  return (
    <div className="container">
      <h1>U-Safe - 万能保险箱</h1>
      <p>欢迎使用 U盘文件加密管理工具</p>

      <div className="card">
        <h2>项目骨架初始化完成</h2>
        <p>Phase 1 (M1) - Tauri 2.0 + React 18 + TypeScript</p>
        {message && <p className="message">{message}</p>}

        <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
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
      </div>
    </div>
  );
}

export default App;
