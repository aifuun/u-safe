# Issue #18: Phase 1 (M1): 项目骨架 - Project Skeleton

**GitHub**: https://github.com/aifuun/u-safe/issues/18
**Branch**: feature/18-project-skeleton
**Worktree**: /Users/woo/dev/u-safe-18-project-skeleton
**Started**: 2026-03-15
**Duration**: 7 天 (乐观: 5 天，悲观: 9 天)
**Week**: Week 1
**Phase**: 1/6
**Milestone**: M1
**Priority**: P0

---

## 📋 Context

建立可运行的最小框架，验证技术栈可行性。这是 MVP v1.0 的第一个阶段，为后续开发奠定基础。

**核心目标**:
- 验证 Tauri 2.0 + Rust + React 18 技术栈可行性
- 建立基础项目结构和开发环境
- 实现最小 IPC 通信验证
- 建立 SQLite 数据库连接和 schema

---

## ✅ Tasks

### Setup (2 天) - 项目初始化

#### Task 1: 初始化 Tauri 2.0 项目
- [ ] 使用 `npm create tauri-app@latest` 初始化项目
- [ ] 选择 React + TypeScript 模板
- [ ] 验证项目结构正确 (src-tauri/, src/)
- [ ] 运行 `npm run tauri dev` 验证基础启动

**Acceptance Criteria**:
- 项目目录结构符合 Tauri 2.0 标准
- 开发服务器可以正常启动

#### Task 2: 配置 Rust + React 开发环境
- [ ] 配置 Rust toolchain (确保 Rust 1.70+)
- [ ] 安装 Tauri CLI: `npm install --save-dev @tauri-apps/cli@next`
- [ ] 配置 React 开发依赖
- [ ] 设置 tsconfig.json 严格模式
- [ ] 配置 Vite (如果使用)

**Acceptance Criteria**:
- `rustc --version` 显示正确版本
- TypeScript 严格模式启用
- 开发环境无警告

#### Task 3: 设置 SQLite 数据库连接
- [ ] 添加 Rust 依赖: `rusqlite = "0.30"`
- [ ] 创建数据库连接模块 `src-tauri/src/db/mod.rs`
- [ ] 实现数据库初始化函数
- [ ] 配置数据库文件路径 (.u-safe/u-safe.db)

**Acceptance Criteria**:
- 数据库连接成功创建
- 数据库文件正确保存

#### Task 4: 创建 5 张核心表 Schema
- [ ] 创建 migrations 目录
- [ ] 定义 files 表结构
- [ ] 定义 tags 表结构
- [ ] 定义 file_tags 表结构 (多对多关联)
- [ ] 定义 encryption_meta 表结构
- [ ] 定义 config 表结构
- [ ] 实现 migration 脚本

**参考**: docs/spec/Database_Schema.md

**Acceptance Criteria**:
- 所有 5 张表成功创建
- Schema 符合设计文档

#### Task 5: 配置 TailwindCSS
- [ ] 安装依赖: `npm install -D tailwindcss postcss autoprefixer`
- [ ] 初始化配置: `npx tailwindcss init -p`
- [ ] 配置 tailwind.config.js
- [ ] 添加 CSS 入口文件
- [ ] 验证样式正常工作

**Acceptance Criteria**:
- TailwindCSS 样式可用
- 开发模式下样式热更新

#### Task 6: 设置 TypeScript 严格模式
- [ ] 更新 tsconfig.json: `"strict": true`
- [ ] 启用 `"noImplicitAny": true`
- [ ] 启用 `"strictNullChecks": true`
- [ ] 修复所有类型错误

**Acceptance Criteria**:
- `npm run type-check` 无错误
- 所有文件类型安全

#### Task 7: 跨平台字体配置
- [ ] 配置系统字体回退 (Windows/macOS)
- [ ] 设置中文字体支持
- [ ] 验证字体渲染正常

**Acceptance Criteria**:
- Windows 使用 Segoe UI/Microsoft YaHei
- macOS 使用 SF Pro/PingFang SC

#### Task 8: Tauri 窗口配置
- [ ] 配置窗口尺寸 (默认 1200x800)
- [ ] 设置窗口标题
- [ ] 配置窗口图标
- [ ] 设置最小尺寸限制

**参考**: tauri.conf.json

**Acceptance Criteria**:
- 窗口尺寸符合设计
- 标题和图标正确显示

---

### Infrastructure (2 天) - 基础设施

#### Task 9: 实现 Tauri IPC 基础通信
- [ ] 创建第一个 IPC 命令: `hello_world`
- [ ] 在 Rust 实现命令处理函数
- [ ] 在 React 调用 IPC 命令
- [ ] 验证双向通信正常

**Acceptance Criteria**:
- React 调用 `invoke('hello_world')` 成功
- 返回 "Hello World"

#### Task 10: 创建数据库迁移脚本
- [ ] 实现 migration runner
- [ ] 支持 version tracking
- [ ] 实现 rollback 功能 (可选)
- [ ] 测试 migration 流程

**Acceptance Criteria**:
- Migration 自动执行
- 数据库 version 正确记录

#### Task 11: 实现 U 盘根目录检测逻辑
- [ ] 实现跨平台路径检测
- [ ] Windows: 检测可移动驱动器
- [ ] macOS: 检测 /Volumes/
- [ ] 返回 U 盘根目录路径

**Acceptance Criteria**:
- 正确检测 U 盘路径
- 跨平台兼容

#### Task 12: 创建 .u-safe/ 隐藏目录
- [ ] 实现目录创建逻辑
- [ ] Windows: 设置隐藏属性
- [ ] macOS: 使用 . 前缀
- [ ] 创建子目录结构 (data/, logs/)

**Acceptance Criteria**:
- 目录自动创建
- 目录隐藏属性正确

#### Task 13: 设置日志系统
- [ ] Rust: 配置 `log` + `env_logger`
- [ ] React: 配置 console logging
- [ ] 实现日志文件输出
- [ ] 设置日志级别

**Acceptance Criteria**:
- 日志输出到文件和控制台
- 日志级别可配置

---

### Testing (1 天) - 测试验证

#### Task 14: Windows 编译测试
- [ ] 在 Windows 环境编译
- [ ] 验证应用启动
- [ ] 测试 IPC 通信
- [ ] 检查数据库连接

**Acceptance Criteria**:
- Windows 编译无错误
- 应用正常运行

#### Task 15: macOS 编译测试
- [ ] 在 macOS 环境编译 (Intel + Apple Silicon)
- [ ] 验证应用启动
- [ ] 测试 IPC 通信
- [ ] 检查数据库连接

**Acceptance Criteria**:
- macOS 编译无错误
- 应用正常运行

#### Task 16: 验证 IPC 双向通信
- [ ] 测试 React → Rust 调用
- [ ] 测试 Rust → React 事件发送
- [ ] 测试复杂数据类型传递
- [ ] 性能测试 (IPC 延迟)

**Acceptance Criteria**:
- 双向通信正常
- 延迟 < 50ms

#### Task 17: 验证数据库读写
- [ ] 测试表创建
- [ ] 测试数据插入
- [ ] 测试数据查询
- [ ] 测试数据更新和删除

**Acceptance Criteria**:
- CRUD 操作正常
- 数据持久化正确

#### Task 18: WebView2 环境检测 (Windows)
- [ ] 检测 WebView2 runtime
- [ ] 提供安装提示 (如果未安装)
- [ ] 测试 WebView2 功能

**Acceptance Criteria**:
- 正确检测 WebView2
- 缺失时提示友好

#### Task 19: 系统环境自检
- [ ] 检查文件系统权限
- [ ] 检查路径访问权限
- [ ] 验证 U 盘读写权限
- [ ] 生成环境检测报告

**Acceptance Criteria**:
- 自检功能正常
- 问题提示清晰

---

## 🎯 Acceptance Criteria

验收标准 (必须全部通过):

### 功能验收
- [ ] 应用可在 Windows 10/11 正常启动
- [ ] 应用可在 macOS (Intel + Apple Silicon) 正常启动
- [ ] IPC 调用成功返回 "Hello World"
- [ ] SQLite 数据库可读写 (CRUD 操作正常)
- [ ] .u-safe/ 目录自动创建并正确隐藏

### 技术验收
- [ ] TypeScript 严格模式无错误
- [ ] Rust 编译无警告
- [ ] TailwindCSS 样式正常工作
- [ ] 跨平台字体渲染正常
- [ ] 日志系统输出正常

### 性能验收
- [ ] 应用冷启动 < 2 秒
- [ ] IPC 调用延迟 < 50ms
- [ ] 数据库操作响应 < 100ms

---

## 📈 Progress

- [ ] Setup (2 天) - 8 tasks
- [ ] Infrastructure (2 天) - 5 tasks
- [ ] Testing (1 天) - 6 tasks

**Total**: 19 tasks

---

## 📝 Next Steps

1. Review this plan
2. Start with Task 1: 初始化 Tauri 2.0 项目
3. Use `/next` to get each task
4. Update progress as tasks complete
5. When done: `/finish-issue 18`

---

## 📚 References

- **MVP 实施计划**: docs/roadmap/MVP_v1.0_Implementation_Plan.md
- **数据库设计**: docs/spec/Database_Schema.md
- **产品需求**: docs/prd/PRD.md
- **UI/UX 设计**: docs/spec/UI_UX_Design_System.md
- **MVP 总计划**: .claude/plans/active/mvp-v1.0-plan.md

---

**Created**: 2026-03-15
**Estimated Completion**: 2026-03-22 (7 天)
**Dependencies**: None (第一阶段)
