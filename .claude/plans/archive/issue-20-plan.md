# Issue #20: Phase 3 (M3): 文件管理 - File Management

**GitHub**: https://github.com/aifuun/u-safe/issues/20
**Branch**: feature/20-phase-3-m3-file-management
**Worktree**: /Users/woo/dev/u-safe-20-phase-3-m3-file-management
**Started**: 2026-03-16

---

## 🎯 目标

实现 P1 文件浏览和加密集成

**Duration**: 8 天 (乐观: 6 天，悲观: 10 天)
**Week**: Week 4
**Phase**: 3/6
**Milestone**: M3
**Priority**: P1
**Dependencies**: Phase 2 (M2) must be complete

---

## 📋 上下文

本 issue 基于已完成的 Phase 2 (M2) Encryption Engine，需要实现文件管理功能，包括：
- 文件树递归扫描和显示
- 文件加密/解密 IPC 集成
- 进度反馈和错误处理
- 性能优化（1000 个文件 < 1 秒加载）

---

## ✅ 实现任务

### Phase 1: File Tree Backend (3 天)

**Task 1: 实现文件树扫描 IPC 命令** (1 天)
- [ ] 创建 `scan_file_tree` IPC 命令 (`src-tauri/src/commands/file_scanner.rs`)
- [ ] 递归扫描目录结构
- [ ] 返回文件元数据：path, name, size, is_dir, children
- [ ] 添加错误处理（权限错误、符号链接循环）
- [ ] 单元测试：空目录、深层嵌套、大量文件
- **AC**: 能够扫描 1000 个文件在 < 500ms

**Task 2: 文件类型检测** (0.5 天)
- [ ] 使用 `mime_guess` crate 检测文件类型
- [ ] 返回 MIME type 和文件扩展名
- [ ] 支持常见文件类型：文档、图片、视频、压缩包
- [ ] 添加文件类型枚举映射
- **AC**: 正确识别 20+ 种常见文件类型

**Task 3: 文件监听（条件实现）** (1.5 天)
- **实现条件**（满足其一即实现）：
  1. 性能测试发现手动刷新延迟 > 1 秒，或
  2. 用户反馈明确需要实时监听功能
- **如不满足条件**：跳过此任务，使用手动刷新按钮
- [ ] 使用 `notify` crate 监听文件系统变化
- [ ] 发送事件到前端（新增、删除、修改）
- [ ] 添加防抖逻辑（避免频繁更新）
- [ ] 错误处理：监听失败回退到轮询
- **AC**: 文件变化在 500ms 内反映到 UI

### Phase 2: File Tree Frontend (2 天)

**Task 4: TreeView 组件** (1 天)
- [ ] 创建 `FileTreeView.tsx` (`app/src/02_modules/files/views/`)
- [ ] 使用递归组件渲染树结构
- [ ] 实现展开/折叠状态管理（Zustand store）
- [ ] 添加虚拟滚动（react-window）支持大量文件
- [ ] CSS: 缩进、连接线、hover 状态
- **AC**: 渲染 1000 个文件 < 1 秒，UI 流畅

**Task 5: 文件类型图标** (0.5 天)
- [ ] 创建图标映射 (`iconMap.ts`)
- [ ] 使用 Emoji 图标（MVP v1.0 标准）
- [ ] 文件夹：📁（折叠）📂（展开）
- [ ] 文件类型：📄（文档）🖼️（图片）🎬（视频）📦（压缩包）
- [ ] 加密文件：🔒 叠加显示
- **AC**: 所有支持的文件类型有对应图标

**Task 6: 右键菜单** (0.5 天)
- [ ] 创建 `ContextMenu.tsx`
- [ ] 菜单项：加密、解密、重命名、删除
- [ ] 根据文件状态显示可用操作
- [ ] 快捷键支持（可选）
- **AC**: 右键菜单正确显示，点击触发对应操作

### Phase 3: Encryption Integration (2 天)

**Task 7: 加密文件 IPC 集成** (1 天)
- [ ] 在 `FileTreeView` 中调用 `encrypt_file` IPC
- [ ] 显示进度条（分块加密进度）
- [ ] 成功后刷新文件树（显示 🔒 图标）
- [ ] 失败显示 Toast 错误提示
- [ ] 添加取消操作支持
- **AC**: 加密流程完整，进度实时更新

**Task 8: 解密文件 IPC 集成** (1 天)
- [ ] 在 `FileTreeView` 中调用 `decrypt_file` IPC
- [ ] 显示进度条（分块解密进度）
- [ ] 成功后刷新文件树（移除 🔒 图标）
- [ ] 失败显示 Toast 错误提示
- [ ] 添加取消操作支持
- **AC**: 解密流程完整，进度实时更新

**Task 9: 密码安全机制** (0.5 天)
- [ ] 在 Rust 后端实现密码尝试次数追踪（SQLite 表）
- [ ] 密码错误 3 次后锁定文件 5 分钟
- [ ] 前端显示剩余尝试次数和锁定倒计时
- [ ] 添加解锁时间到期自动重置机制
- [ ] 日志记录所有解密尝试（成功/失败）
- **AC**: 密码错误 3 次后无法继续尝试解密，5 分钟后自动解锁

### Phase 4: Testing & Polish (1 天)

**Task 10: 单元测试** (0.5 天)
- [ ] Rust: `file_scanner.rs` 测试（空目录、大量文件、错误情况）
- [ ] TypeScript: `FileTreeView.test.tsx` 渲染测试
- [ ] TypeScript: `iconMap.test.ts` 图标映射测试
- **AC**: 测试覆盖率 > 80%

**Task 11: 集成测试** (0.5 天)
- [ ] 完整加密/解密流程测试（E2E）
- [ ] 错误场景测试：权限错误、文件不存在、密码错误
- [ ] 性能测试：1000 个文件加载时间
- [ ] UI 测试：TreeView 交互正常
- **AC**: 所有测试通过，无回归

---

## 🎯 验收标准

- ✅ 文件树正常显示（展开/折叠、图标、右键菜单）
- ✅ 加密/解密集成正常（IPC 调用、进度反馈、错误处理）
- ✅ 进度反馈实时更新（分块进度条）
- ✅ 1000 个文件 < 1 秒加载
- ✅ 测试覆盖率 > 80%
- ✅ 无明显性能问题或 UI 卡顿

---

## 📚 参考文档

**核心文档**:
- `docs/roadmap/MVP_Definition.md` - MVP 功能范围
- `docs/spec/PRD_Core_Logic.md` - 加密/解密业务流程
- `docs/spec/UI_UX_Design_System.md` - 设计 token + 组件规范
- `docs/spec/Database_Schema.md` - 数据库表结构

**技术参考**:
- `.claude/rules/frontend/design-tokens.md` - CSS token 使用规范
- `.claude/rules/desktop/tauri-ipc.md` - IPC 调用模式
- `.prot/pillars/` - 18 个编码标准（按需读取）

**已完成依赖**:
- Phase 2 (M2): Encryption Engine (#19) - 已合并

---

## 📊 进度追踪

- [ ] Plan reviewed
- [ ] Phase 1: File Tree Backend (3 tasks)
- [ ] Phase 2: File Tree Frontend (3 tasks)
- [ ] Phase 3: Encryption Integration (3 tasks) - 新增密码安全机制
- [ ] Phase 4: Testing & Polish (2 tasks)
- [ ] Tests passing
- [ ] Ready for review

---

## 🚀 下一步

1. **Review this plan** - 确认任务分解合理
2. **Run `/eval-plan #20`** - 自动验证计划质量
3. **Get first task**: `/next` - 开始第一个任务
4. **Start implementation** - 使用 worktree 路径操作
5. **When done**: `/finish-issue #20` - 提交 PR 并关闭 issue

---

## ⚠️ CRITICAL: Worktree Context

**所有操作必须使用 worktree 路径**:
- Worktree: `/Users/woo/dev/u-safe-20-phase-3-m3-file-management`
- 主仓库: `/Users/woo/dev/u-safe` (保持在 master 分支)

**正确示例**:
```bash
# Read files
Read /Users/woo/dev/u-safe-20-phase-3-m3-file-management/src-tauri/src/commands/file_scanner.rs

# Edit files
Edit /Users/woo/dev/u-safe-20-phase-3-m3-file-management/app/src/02_modules/files/views/FileTreeView.tsx

# Git operations
git -C /Users/woo/dev/u-safe-20-phase-3-m3-file-management status
git -C /Users/woo/dev/u-safe-20-phase-3-m3-file-management add .
git -C /Users/woo/dev/u-safe-20-phase-3-m3-file-management commit -m "feat: implement file tree"
```

**错误示例 (DO NOT DO THIS)**:
```bash
❌ Read src-tauri/src/commands/file_scanner.rs  # 相对路径
❌ Edit /Users/woo/dev/u-safe/app/src/...        # 主仓库路径
❌ git status                                    # 缺少 -C flag
```
