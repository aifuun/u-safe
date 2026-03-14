# Debugging Rules

> 不要猜测，让日志说话。

## 排查顺序

```
1. 控制台日志 → 2. Tauri DevTools → 3. 模拟代码流程 → 4. 最小复现
```

### 1. 控制台日志

**前端 (React)**:
```typescript
console.log('[encrypt:start]', { fileId, fileSize });
console.error('[encrypt:failed]', { fileId, error });
```

**后端 (Rust)**:
```rust
log::info!("[encrypt:start] file_id={}, size={}", file_id, size);
log::error!("[encrypt:failed] file_id={}, err={}", file_id, err);
```

### 2. Tauri DevTools

- 前端: 浏览器开发者工具 (F12)
- 后端: Rust `RUST_LOG=debug` 环境变量
- IPC: 检查 invoke 调用和事件传递

### 3. 模拟代码流程

- 用 LSP `goToDefinition` / `incomingCalls` 追踪调用链
- 检查状态机转换日志
- 添加临时 `log::debug!()` 或 `console.log()` 缩小范围

### 4. 最小复现

写测试固定 bug，隔离变量逐个排除。

## 黄金法则

1. **先看日志** - 日志比直觉可靠
2. **前后端分层排查** - 先确认问题在 React 还是 Rust
3. **检查 IPC 边界** - 很多 bug 是前后端数据传递问题
