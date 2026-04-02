# Structured Logging Rules

> 结构化日志，便于调试。

## Quick Check

- [ ] Rust 后端使用 `log` crate（info/warn/error）
- [ ] 日志包含语义事件名：`[模块:操作:状态]`
- [ ] 敏感信息（密码、密钥）不写入日志
- [ ] 错误日志包含上下文（文件名、大小、操作类型）

## Core Pattern

**Rust:**
```rust
log::info!("[crypto:encrypt:start] file={}, size={}", path, size);
log::info!("[crypto:encrypt:done] file={}, chunks={}", path, chunks);
log::error!("[crypto:encrypt:failed] file={}, err={}", path, err);
```

**TypeScript (前端):**
```typescript
console.info('[tag:create]', { name, parentId });
console.error('[file:open:failed]', { fileId, error: err.message });
```

## 日志级别

| 级别 | 用途 |
|------|------|
| `error` | 操作失败，需要关注 |
| `warn` | 异常但可恢复 |
| `info` | 关键业务事件 |
| `debug` | 开发调试，release 不输出 |
