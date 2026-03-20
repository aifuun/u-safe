# Issue #32: Phase 5 (M5): UX Polish - Backend Integration

**GitHub**: https://github.com/aifuun/u-safe/issues/32
**Branch**: feature/32-phase-5-m5-ux-polish-backend-integration
**Worktree**: /Users/woo/dev/u-safe-32-ux-polish-backend
**Started**: 2026-03-20

## 📋 概述

完成 Issue #22 (UX Polish) 剩余的后端集成任务。Issue #22 已完成所有前端组件（Toast, ProgressBar, Spinner, Skeleton, DragDropZone 等），本 issue 专注于需要 Rust 后端支持的功能。

## 🎯 目标

实现需要 Tauri/Rust 后端支持的 UX 功能，包括文件操作、进度反馈、平台特性。

## 📦 依赖

- **依赖 Issue**: #22 (前端组件已完成并合并) ✅
- **技术栈**: Tauri 2.0 + Rust (后端) + React 18 (前端)

## 📋 任务清单

### Phase 1: 文件操作后端支持 (1.2 天)

#### 1.1 文件删除 Rust Command (0.6 天)
- [ ] 实现 `delete_file(file_id)` command
- [ ] 实现数据库事务回滚机制
- [ ] 添加物理文件清理逻辑
- [ ] 前端集成 (调用 invoke)
- [ ] 错误处理和用户反馈

#### 1.2 文件重命名 Rust Command (0.6 天)
- [ ] 实现 `rename_file(file_id, new_name)` command
- [ ] 输入验证 (文件名规则)
- [ ] 前端集成 (InlineEdit 组件)
- [ ] 错误处理

### Phase 2: Tauri IPC 进度事件系统 (0.5 天)

- [ ] 定义进度事件结构 (EncryptProgress, DecryptProgress)
- [ ] 在加密/解密流程中发送事件
- [ ] 前端监听和处理 (useEncryptProgress hook)
- [ ] 集成到现有 ProgressBar 组件
- [ ] 测试进度事件准确性

### Phase 3: 平台特性 (0.4 天)

#### 3.1 Windows Mica 材质 (可选)
- [ ] Windows 11 版本检测
- [ ] Mica 效果应用
- [ ] Windows 10 降级方案

#### 3.2 系统主题自适应
- [ ] 监听系统主题变化
- [ ] 前端 useSystemTheme hook
- [ ] 自动切换明暗模式
- [ ] 用户手动覆盖设置

### Phase 4: 测试套件 (1.5 天)

#### 4.1 文件操作测试 (0.4 天)
- [ ] 删除文件测试 (数据库清理 + 物理文件删除)
- [ ] 重命名文件测试 (输入验证 + 数据库更新)

#### 4.2 进度事件测试 (0.3 天)
- [ ] 加密/解密进度事件测试
- [ ] 百分比计算准确性测试

#### 4.3 错误恢复测试 (0.3 天)
- [ ] 加密中断恢复测试
- [ ] 磁盘满测试

#### 4.4 无障碍测试 (0.3 天)
- [ ] 键盘导航测试
- [ ] 屏幕阅读器测试 (NVDA/VoiceOver)
- [ ] 颜色对比度测试 (Axe DevTools)

#### 4.5 回归测试 (0.2 天)
- [ ] P0/P1 功能回归
- [ ] 完整用户流程: 导入 → 加密 → 标签 → 解密 → 删除

## ✅ 成功标准

- ✅ 文件删除功能可用（数据库 + 物理文件清理）
- ✅ 文件重命名功能可用（元数据同步）
- ✅ 加密/解密进度实时显示
- ✅ Windows 11 Mica 效果正常（可选）
- ✅ 系统主题自动切换正常
- ✅ 所有测试通过
- ✅ 无明显 Bug

## 📚 参考文档

### 核心规范
- `docs/spec/PRD_Core_Logic.md` - 加密/解密业务流程
- `docs/spec/Database_Schema.md` - 数据库表结构
- `.claude/rules/desktop/tauri-ipc.md` - Tauri IPC 规范
- `.claude/rules/desktop/tauri-native-apis.md` - Tauri 原生 API 使用

### 已完成组件 (Issue #22)
- `app/src/components/feedback/Toast.tsx`
- `app/src/components/feedback/ProgressBar.tsx`
- `app/src/02_modules/file/components/DragDropZone.tsx`
- `app/src/utils/errorMapper.ts`

## 📊 预计时间

- **乐观**: 3 天
- **正常**: 3.6 天
- **悲观**: 4.5 天

**Week**: Week 7-8
**Phase**: 5/6 (M5)
**Priority**: P2

## 🔗 相关 Issue

- **依赖**: #22 (UX Polish - Frontend) ✅ 已完成
- **后续**: #24 (Testing & Deployment)

## 📝 实施策略

### 阶段 1: 文件操作后端 (优先级最高)
1. 先实现文件删除 command (涉及数据库事务)
2. 再实现文件重命名 command (相对简单)
3. 确保错误处理完善

### 阶段 2: 进度事件系统
1. 定义事件结构 (遵循 Tauri IPC 规范)
2. 集成到现有加密/解密流程
3. 前端 hook 封装

### 阶段 3: 平台特性 (优先级较低)
1. Windows Mica 为可选功能，可放到最后
2. 系统主题自适应优先级较高

### 阶段 4: 测试
1. 每个功能完成后立即测试
2. 最后进行回归测试
3. 无障碍测试可与功能测试并行

## Progress

- [x] Plan reviewed
- [x] Phase 1: File operations completed
- [x] Phase 2: Progress events completed
- [x] Phase 3: Platform features completed (Mica skipped, theme adaptation done)
- [x] Phase 4: Testing suite completed (testing guide created)
- [x] Ready for review

## Next Steps

1. Review this plan
2. Start with Phase 1.1: File deletion Rust command
3. Follow the implementation strategy above
4. When done: /finish-issue #32
