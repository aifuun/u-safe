# Issue #34: 文档完善 - 补充架构文档和清理迁移变更

**GitHub**: https://github.com/aifuun/u-safe/issues/34
**Branch**: feature/34-docs-improvements-architecture-and-migration-cleanup
**Worktree**: /Users/woo/dev/u-safe-34-docs-improvements
**Started**: 2026-03-20

## 概述

完善项目文档结构，补充缺失内容，确保文档符合 ai-dev 标准。

## 目标

1. 保留文档迁移的成果（已完成的 docs 结构调整）
2. 补充关键文档的缺失内容
3. 清理和归档旧文档
4. 确保所有文档符合 DOCUMENTATION_MANUAL.md 标准

## 当前状态

**已完成的迁移**:
- ✅ 文档目录结构已调整为 ai-dev 标准
- ✅ docs.old/ 备份已创建
- ✅ 新的 adr/, arch/, design/, dev/, product/, qa/ 目录已建立
- ✅ DOCUMENTATION_MANUAL.md 已添加

**需要完善**:
- ⚠️ arch/ARCHITECTURE.md 内容过于简单（仅框架）
- ⚠️ 未提交的文档变更需要整理
- ⚠️ 计划文件需要归档
- ⚠️ 新技能文件需要提交

## 任务清单

### Phase 1: 整理当前变更 (0.2 天)

- [ ] **Task 1.1**: 添加新文档文件
  - 添加 docs/DOCUMENTATION_MANUAL.md
  - 添加 docs/adr/* (新目录结构)
  - 添加 docs/arch/API.md, ARCHITECTURE.md, SCHEMA.md
  - 添加 docs/design/* (新目录结构)
  - 添加 docs/dev/*, docs/product/*, docs/qa/*

- [ ] **Task 1.2**: 归档 issue #32 的计划文件
  - 移动 .claude/plans/active/issue-32-*.md 到 .claude/plans/archive/
  - 确认 3 个文件已归档

- [ ] **Task 1.3**: 添加新的技能文件
  - 添加 .claude/skills/common/
  - 添加 .claude/skills/eval-plan/checklists.yaml
  - 添加 .claude/skills/review/goal-coverage.ts

- [ ] **Task 1.4**: 更新 README.md
  - 检查并提交 README.md 的变更

- [ ] **Task 1.5**: 删除旧文档结构
  - 删除 docs/ADRs/* (旧大写目录)
  - 删除 docs/spec/* (已迁移到 design/)
  - 删除 docs/prd/* (已迁移到 product/)
  - 删除 docs/roadmap/* (已迁移到 product/)
  - 删除 docs/README.html
  - 删除 docs/arch/Database_Schema.md (已重命名为 SCHEMA.md)

### Phase 2: 补充 ARCHITECTURE.md (0.5 天)

- [ ] **Task 2.1**: 添加系统架构概述
  - 系统定位和核心价值
  - 主要功能模块概览
  - 关键约束和限制

- [ ] **Task 2.2**: 详细描述技术栈
  - Frontend: Tauri 2.0 + React 18 + TypeScript
  - Backend: Rust (加密引擎)
  - Database: SQLite
  - 每项技术的选择理由 (引用 ADR-003)

- [ ] **Task 2.3**: 添加架构分层说明
  - 前端: UI 层 (React) → Service 层 → IPC 层
  - 后端: Commands 层 → Service 层 → Core 层
  - 数据: SQLite + 加密文件存储
  - 引用 Pillars 和架构模式

- [ ] **Task 2.4**: 添加模块划分和职责
  - 加密引擎模块
  - 标签管理模块
  - 文件管理模块
  - 用户界面模块
  - 每个模块的职责和边界

- [ ] **Task 2.5**: 添加关键设计决策引用
  - 链接到 ADR-001 (Design Token System)
  - 链接到 ADR-003 (Technical Stack)
  - 链接到 ADR-004 (Encryption Strategy)

- [ ] **Task 2.6**: 添加架构图引用
  - 引用 system-architecture.mmd
  - 引用 data-flow.mmd
  - 说明图表位置和用途

### Phase 3: 补充架构图表 (0.3 天)

- [ ] **Task 3.1**: 创建系统架构图
  - 文件: docs/design/diagrams/system-architecture.mmd
  - 内容: 前端/后端/数据层的组件关系
  - Mermaid 语法验证

- [ ] **Task 3.2**: 创建数据流图
  - 文件: docs/design/diagrams/data-flow.mmd
  - 内容: 加密/解密/标签的数据流转
  - Mermaid 语法验证

- [ ] **Task 3.3**: (可选) 创建部署架构图
  - 文件: docs/design/diagrams/deployment.mmd
  - 内容: Windows/macOS 平台部署方式
  - Mermaid 语法验证

- [ ] **Task 3.4**: 更新 diagrams/README.md 索引
  - 添加新图表到索引
  - 更新图表计数
  - 添加图表用途说明

### Phase 4: 验证文档完整性 (0.2 天)

- [ ] **Task 4.1**: 检查必需文件存在
  - docs/README.md ✅
  - docs/DOCUMENTATION_MANUAL.md ✅
  - docs/product/PRD.md ✅
  - docs/arch/ARCHITECTURE.md ✅
  - docs/design/UI_UX_DESIGN.md ✅
  - docs/adr/README.md ✅

- [ ] **Task 4.2**: 验证文档内链接
  - 检查 docs/README.md 中的所有链接
  - 检查 ADR 之间的引用
  - 检查架构文档的图表引用

- [ ] **Task 4.3**: 验证 ADR 索引
  - 确认 docs/adr/README.md 包含所有 ADR
  - 确认编号连续 (001-004)
  - 确认状态正确

- [ ] **Task 4.4**: 验证 Mermaid 图表语法
  - 使用 docs/design/diagrams/VERIFICATION.md 中的方法
  - 确认所有 .mmd 文件语法正确
  - 测试图表渲染

### Phase 5: 清理和提交 (0.3 天)

- [ ] **Task 5.1**: 删除 docs.old/ 备份
  - 确认迁移完成且验证通过
  - 删除整个 docs.old/ 目录
  - Git 记录删除操作

- [ ] **Task 5.2**: 删除临时文件
  - 删除 MIGRATION_REPORT.md (如果存在)
  - 删除其他临时生成的文件

- [ ] **Task 5.3**: 提交所有文档变更
  - 暂存所有新增文件
  - 暂存所有删除的旧文件
  - 暂存修改的文件
  - 创建清晰的提交信息

- [ ] **Task 5.4**: 检查 CLAUDE.md 引用
  - 验证 .claude/rules/core/docs.md 路径是否需要更新
  - 如需更新则修改并提交

## 成功标准

- ✅ arch/ARCHITECTURE.md 包含完整的架构描述（至少 200 行）
- ✅ 至少 2 个架构图表（system-architecture, data-flow）
- ✅ 所有文档符合 DOCUMENTATION_MANUAL.md 标准
- ✅ 所有变更已提交到 git
- ✅ docs.old/ 已清理
- ✅ 文档内链接全部有效

## 参考文档

- `docs/DOCUMENTATION_MANUAL.md` - ai-dev 文档标准
- `docs/README.md` - 文档导航和迁移记录
- `.claude/rules/core/docs.md` - 文档规范
- `docs/adr/` - 架构决策记录
- `docs/product/PRD.md` - 产品需求（了解系统功能）
- `docs/arch/SCHEMA.md` - 数据模型（了解数据结构）

## 时间估算

- **Phase 1**: 0.2 天 (整理变更)
- **Phase 2**: 0.5 天 (补充 ARCHITECTURE.md)
- **Phase 3**: 0.3 天 (补充架构图表)
- **Phase 4**: 0.2 天 (验证完整性)
- **Phase 5**: 0.3 天 (清理和提交)

**总计**: 1.5 天 (正常估算)

## 进度跟踪

- [ ] Phase 1: 整理当前变更
- [ ] Phase 2: 补充 ARCHITECTURE.md
- [ ] Phase 3: 补充架构图表
- [ ] Phase 4: 验证文档完整性
- [ ] Phase 5: 清理和提交

## 下一步

1. 查看当前工作目录的文档变更状态
2. 开始 Phase 1: 整理当前变更
3. 按顺序完成每个 Phase
4. 完成后使用 `/finish-issue 34` 创建 PR 并合并
