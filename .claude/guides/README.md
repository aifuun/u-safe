# AI Guides System

> AI 开发指南和文档模板的统一系统

## 📂 目录结构

```
.claude/guides/
├── README.md         # 本文件 - 总导航
│
├── workflow/         # AI 工作流参考指南（5个）
│   ├── README.md
│   ├── ADR_GUIDE.md
│   ├── CLAUDE_MD_GUIDE.md
│   ├── ISSUE_LIFECYCLE_GUIDE.md
│   ├── PROJECT_PLANNING_GUIDE.md
│   └── SKILL_GUIDE.md
│
└── doc-templates/    # 项目文档模板系统（22个模板+6个guide）
    ├── README.md
    ├── STACK_TAGS.md
    ├── prd/
    ├── architecture/
    ├── design/
    ├── dev/
    ├── qa/
    └── ops/
```

## 🎯 两个子系统

### 1. workflow/ - AI 工作流指南

**定位:** 指导 AI 如何执行开发任务

**内容:** 5 个工作流参考指南
- `ADR_GUIDE.md` - 创建架构决策记录（ADR）
- `CLAUDE_MD_GUIDE.md` - 维护 CLAUDE.md 文件
- `ISSUE_LIFECYCLE_GUIDE.md` - Issue 生命周期管理
- `PROJECT_PLANNING_GUIDE.md` - 项目规划标准
- `SKILL_GUIDE.md` - Skill 开发指南

**使用者:** AI (在执行 skills 时读取)

**同步方式:** `/update-guides` skill 同步到目标项目

**详细文档:** [workflow/README.md](workflow/README.md)

---

### 2. doc-templates/ - 文档模板系统

**定位:** 项目文档的结构和模板

**内容:** 22 个文档模板 + 6 个模块指南 + 1 个主指南
- **MANAGE_DOCS_GUIDE.md** - AI 创建/更新文档的主指南
- **STACK_TAGS.md** - Stack tag 处理系统
- PRD（产品需求文档）
- Architecture（系统架构）
- Design（设计系统 - 14个子模板）
- Dev（开发环境）
- QA（测试计划）
- Ops（运维部署）

**使用者:** `init-project.py` 和 `/init-docs` skill

**同步方式:** 随 framework 同步（不通过 update-guides）

**详细文档:** [doc-templates/README.md](doc-templates/README.md)

---

## 🔄 迁移说明

**从旧结构迁移:**

| 旧位置 | 新位置 | 状态 |
|--------|--------|------|
| `.claude/guides/*.md` | `.claude/guides/workflow/` | ✅ 已迁移 |
| `framework/guides/` | `.claude/guides/doc-templates/` | ✅ 已迁移 |
| `.claude/pillars/docs-templates/` | `.claude/guides/doc-templates/` | ✅ 已删除（旧） |
| `.claude/guides/DOCS_GUIDE.md` | `.claude/guides/doc-templates/README.md` | ✅ 已替换 |

**详细迁移指南:** [../../docs/MIGRATION_GUIDES_UNIFICATION.md](../../docs/MIGRATION_GUIDES_UNIFICATION.md)

---

## 📋 Hardcoding Policy

**定义何时可以在 guides 中硬编码具体 skill 名称**

### 核心原则

Guides 是抽象的参考标准，不是具体实现的硬编码列表。

### 允许硬编码 ✅

1. **主题文档** - 专门介绍某个 skill 的文档（如 ADR_GUIDE.md）
2. **流程架构** - 展示 skill 调用链的文档（如 ISSUE_LIFECYCLE_GUIDE.md）
3. **配置文档** - 初始化和设置步骤（如 Quick Start）

### 禁止硬编码 ❌

1. **模板示例** - CLAUDE_MD_GUIDE.md 中的项目模板（改用 AI 生成指令）
2. **代码示例** - SKILL_GUIDE.md 中的代码模板（改用抽象占位符）
3. **废弃引用** - 已废弃的 skill（如 /adr, /maintain-project）

**详细规范:** [HARDCODING_POLICY.md](HARDCODING_POLICY.md)

---

## 📖 相关文档

- **Hardcoding Policy:** [HARDCODING_POLICY.md](HARDCODING_POLICY.md)
- **Workflow Guides:** [workflow/README.md](workflow/README.md)
- **Doc Templates:** [doc-templates/README.md](doc-templates/README.md)
- **Stack Tags:** [doc-templates/STACK_TAGS.md](doc-templates/STACK_TAGS.md)
- **Framework README:** [../../framework/README.md](../../framework/README.md)

---

**Last Updated:** 2026-04-01 (Issue #444)
**Maintained By:** AI Development Framework Team
