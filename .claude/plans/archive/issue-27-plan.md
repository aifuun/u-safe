# Issue #27: Phase 3.5: UI Integration & Main Workflow

**GitHub**: https://github.com/aifuun/u-safe/issues/27
**Branch**: feature/27-phase-35-ui-integration-main-workflow
**Worktree**: /Users/woo/dev/u-safe-27-phase-35-ui-integration-main-workflow
**Started**: 2026-03-18

## 🎯 Context

Phase 2 (加密引擎) 和 Phase 3 (文件管理) 的后端功能已完成：
- ✅ 文件扫描、加密/解密 IPC 命令
- ✅ FileTreeView、ContextMenu 组件
- ✅ 51 个后端测试通过

**缺失部分**：
- ❌ 前端组件未集成到主应用 (src/App.tsx 仍是 Phase 1 骨架)
- ❌ 无主密码设置/验证流程
- ❌ 无路由配置
- ❌ 无法进行 E2E 测试

**Duration**: 5 天 (乐观: 4 天，悲观: 6 天)
**Week**: Week 4
**Phase**: 3.5/6
**Milestone**: M3.5
**Priority**: P0

---

## ✅ Tasks

### Phase 1: 主密码流程 (2 天)

#### Task 1: 首次设置密码界面
**File**: `app/src/01_views/setup/SetupPasswordView.tsx`
**Description**: 创建首次密码设置界面
- 密码输入组件（复用 components/PasswordInput.tsx）
- 密码强度验证 (≥12 字符, 大小写+数字+特殊字符)
- 确认密码匹配验证
- IPC 调用：derive_master_key(password) → 保存到 config 表
**AC**: 首次启动显示设置界面，密码保存成功

#### Task 2: 登录/解锁界面
**File**: `app/src/01_views/login/LoginView.tsx`
**Description**: 创建密码验证界面
- 密码输入框
- 验证 IPC：verify_password(password) → 解密主密钥
- 错误提示（密码错误、锁定状态）
- 成功后跳转到文件管理界面
**AC**: 密码验证成功进入主界面，失败显示错误

#### Task 3: 首次启动检测逻辑
**File**: `app/src/00_kernel/hooks/useAppInit.ts`
**Description**: 应用初始化状态检测
- 检测是否已设置密码 (config 表中有 master_key_hash)
- 未设置 → 跳转 /setup
- 已设置但未登录 → 跳转 /login
- 已登录 → 跳转 /files
**AC**: 根据状态自动跳转到正确页面

### Phase 2: 路由配置 (1 天)

#### Task 4: 安装和配置路由
**Files**:
- `app/src/router.tsx` (new)
- `app/src/main.tsx` (update)
**Description**: React Router 集成
- 安装 react-router-dom
- 创建路由配置
- 路由表：/setup, /login, /files, /
- 集成到 main.tsx
**AC**: 所有路由可访问，URL 正确

#### Task 5: 认证守卫
**File**: `app/src/01_views/ProtectedRoute.tsx`
**Description**: 路由访问控制
- 未登录访问 /files → 重定向 /login
- 已登录访问 /setup → 重定向 /files
**AC**: 路由保护生效，未授权访问被拦截

### Phase 3: 主界面集成 (1.5 天)

#### Task 6: 文件管理主界面
**File**: `app/src/01_views/files/FileManagementView.tsx`
**Description**: 集成文件管理组件
- 集成 FileTreeView 组件（从 app/src/02_modules/files/）
- 顶部工具栏：刷新、新增文件、搜索框（占位）
- 侧边栏：U 盘选择（占位）、视图切换（占位）
- 主内容区：FileTreeView
**AC**: 文件树正常显示，加密/解密功能可用

#### Task 7: 导航菜单
**File**: `app/src/01_views/layout/Layout.tsx`
**Description**: 全局布局和导航
- 顶部导航栏：Logo、菜单项、退出按钮
- 菜单项：文件管理 (当前)、标签视图 (禁用)、设置 (占位)
- 退出按钮：清除登录状态 → 跳转 /login
**AC**: 导航菜单显示，退出功能正常

#### Task 8: 状态管理（全局）
**File**: `app/src/00_kernel/stores/authStore.ts`
**Description**: 认证状态管理
- 使用 Zustand vanilla store
- 状态：isAuthenticated, isSetupComplete
- 操作：login(), logout(), checkSetupStatus()
- 持久化到 localStorage
**AC**: 登录状态在页面刷新后保持

### Phase 4: 样式和交互 (0.5 天)

#### Task 9: 全局样式
**File**: `app/src/styles.css`
**Description**: 更新全局样式
- 移除 Phase 1 测试样式
- 添加布局样式 (flex, grid)
- 使用 Design Tokens
**AC**: 界面美观，符合设计规范

#### Task 10: 交互优化
**Files**:
- `app/src/01_views/common/LoadingSpinner.tsx` (new)
- `app/src/01_views/common/Toast.tsx` (new)
**Description**: 用户反馈组件
- Loading 状态（密码验证、文件扫描）
- Toast 通知（成功/失败提示）
- 错误边界（React Error Boundary）
**AC**: 用户操作有明确反馈

---

## 🎯 Acceptance Criteria

- ✅ 首次启动可以设置主密码
- ✅ 主密码验证成功可进入主界面
- ✅ 文件树正常显示（可展开/折叠、右键菜单）
- ✅ 加密/解密功能正常（有进度反馈）
- ✅ 退出登录功能正常
- ✅ **可以进行完整的 E2E 测试**

---

## 📚 References

- docs/roadmap/MVP_Definition.md (F1, F2, F9)
- docs/spec/UI_UX_Design_System.md
- docs/spec/PRD_Core_Logic.md
- app/src/02_modules/files/ (已完成组件)
- .claude/rules/frontend/ (前端规范)

---

## Progress

- [ ] Plan reviewed
- [ ] Implementation started
- [ ] Tests added
- [ ] Ready for review

## Next Steps

1. Review this plan
2. Get first task: /next
3. Start implementation
4. When done: /finish-issue #27
