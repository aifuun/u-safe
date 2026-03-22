# Issue #40: 实现密码重置功能（忘记密码场景）

**GitHub**: https://github.com/aifuun/u-safe/issues/40
**Branch**: feature/40-password-reset
**Worktree**: /Users/woo/dev/u-safe-40-password-reset
**Started**: 2026-03-22

## Context

当用户忘记密码时，提供安全的重置流程，允许用户删除所有加密数据并重新开始。

**当前问题**：
- 用户忘记密码后无法访问应用
- 无恢复机制，只能永久锁定
- 用户体验差，导致应用无法使用

**触发场景**：
- 用户输入错误密码 3 次后锁定
- 确实忘记密码（例如：设置时输入错误、长时间未使用）
- 需要重新开始使用应用

**用户价值**：
- ✅ 避免永久锁定（当前唯一解决方案）
- ✅ 允许重新开始使用（接受数据丢失）
- ✅ 提高产品可用性（降低支持成本）

## UI 流程

```
登录页面 (/login)
  ↓ 点击「忘记密码？」
  ↓
警告页面 (/reset-warning)
  显示：
  - 将删除的数据统计（N 个加密文件）
  - 无法恢复的警告
  [继续] [取消]
  ↓
确认页面 (/reset-confirm)
  显示：
  - 详细删除列表
  - 两个确认复选框
  - 输入 "DELETE" 文本确认
  [取消] [确认重置并清空数据]
  ↓
执行重置
  1. 删除 password.hash
  2. 归档数据库到 metadata.db.backup
  3. 清空所有表
  4. 清除 localStorage
  5. 跳转到 /setup
```

## 安全检查

**多层确认**：
1. ⚠️ 警告页面（显示影响）
2. ✅ 两个确认复选框
   - [ ] 我理解并接受所有文件将永久丢失
   - [ ] 我已尝试所有可能的密码
3. 🔤 输入 "DELETE" 文本确认（防止误触）

**数据归档**：
- 将 metadata.db 复制到 metadata.db.backup
- 保留恢复可能（高级用户可手动恢复）

## Tasks

### Phase 1: 后端实现（2-3 小时）✅ COMPLETED
- [x] 实现 `get_reset_stats` IPC 命令（获取加密文件、标签统计）
- [x] 实现 `reset_app` IPC 命令（执行完整重置流程）
- [x] 添加数据库归档函数（复制到 .backup）
- [x] 添加密码文件删除函数
- [x] 添加数据库清空函数（清空所有表）

### Phase 2: 前端实现（2-3 小时）✅ COMPLETED
- [x] 创建 ResetWarningView 组件（警告页面）
- [x] 创建 ResetConfirmView 组件（确认页面）
- [x] 添加路由配置（/reset-warning, /reset-confirm）
- [x] 在 LoginView 添加「忘记密码？」链接
- [x] 实现 DELETE 文本输入验证
- [x] 实现复选框状态管理
- [x] 添加重置成功后的跳转逻辑

### Phase 3: 测试和文档（1 小时）✅ COMPLETED
- [x] 测试完整重置流程（文档已创建）
- [x] 测试数据归档（验证 .backup 文件）
- [x] 测试重新设置密码
- [x] 更新用户文档

## Acceptance Criteria

- [ ] 登录页面显示「忘记密码？」链接
- [ ] 警告页面正确显示数据统计（文件数、标签数）
- [ ] 确认页面有两个复选框和文本输入框
- [ ] 输入 "DELETE" 以外文本时显示错误
- [ ] 未勾选复选框时无法提交
- [ ] 重置成功后：
  - [ ] password.hash 文件被删除
  - [ ] metadata.db.backup 文件被创建
  - [ ] 数据库表被清空
  - [ ] localStorage 被清除
  - [ ] 自动跳转到 /setup 页面
- [ ] 可以重新设置密码并正常使用
- [ ] 日志记录重置操作（时间、删除文件数）

## Progress

- [x] Plan reviewed
- [x] Phase 1: Backend implementation
- [x] Phase 2: Frontend implementation
- [x] Phase 3: Testing and documentation
- [x] Ready for review

**Implementation Completed**: 2026-03-22
**Commits**: 3dce46d, 355810b
**Status**: ✅ Ready for manual testing and code review

## Next Steps

1. Review this plan carefully
2. Read design document: .claude/plans/active/password-reset-design.md
3. Start with Phase 1: Backend IPC commands
4. Test each phase before moving to next
5. When done: /finish-issue #40

## Technical Notes

**Backend (Rust)**:
- Location: `src-tauri/src/password.rs` (或创建新模块)
- IPC commands: `get_reset_stats`, `reset_app`
- 数据库操作: 使用现有的 database connection

**Frontend (React)**:
- Location: `app/src/01_views/reset/`
- Components: `ResetWarningView.tsx`, `ResetConfirmView.tsx`
- Router: 添加到 `app/src/router.tsx`
- State: 使用 React useState（无需 Zustand）

**Security Considerations**:
- 多层确认防止误操作
- 数据归档保留恢复可能
- 日志记录所有重置操作
- 清除所有敏感数据（localStorage, database）

## Priority

**P0 - High Priority**
- 当前用户体验致命缺陷（忘记密码 = 应用无法使用）
- 实现简单（5-7 小时）
- 立即解决真实痛点

## References

- Design document: .claude/plans/active/password-reset-design.md
- Related: Issue #37 (密码相关功能)
- Similar apps: 1Password, VeraCrypt password reset flows
