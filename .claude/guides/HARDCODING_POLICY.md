# Hardcoding Policy - When to Hardcode Skill Names

> 定义 guides 中何时可以硬编码具体 skill 名称，何时不可以

## 🎯 核心原则

**Guides 是抽象的参考标准，不是具体实现的硬编码列表。**

- ✅ **允许硬编码**：主题文档、流程架构、配置文档
- ❌ **禁止硬编码**：模板示例、代码示例、废弃引用

---

## ✅ 允许硬编码的 3 种场景

### 1. 主题文档（Theme Documents）

**定义**：专门介绍某个 skill 或某类 skills 的文档。

**判断标准**：文档标题包含具体 skill 名称。

**示例**：
```markdown
# ADR_GUIDE.md - ADR 创建指南
本文档专门讲解 `/manage-adrs` skill 的使用。

## 何时使用 `/manage-adrs`
当你需要记录架构决策时...
```

**为什么允许**：文档本身就是围绕这个 skill 编写的，硬编码是必要的。

---

### 2. 流程架构文档（Flow Architecture）

**定义**：描述多个 skills 之间的调用关系和工作流。

**判断标准**：文档展示 skill 之间的依赖链或调用序列。

**示例**：
```markdown
# ISSUE_LIFECYCLE_GUIDE.md
## 5-Phase Workflow
Phase 1: /start-issue → Phase 1.5: /eval-plan → Phase 2: /execute-plan → Phase 2.5: /review → Phase 3: /finish-issue
```

**为什么允许**：需要明确展示具体的 skill 调用顺序。

---

### 3. 配置文档（Configuration Documents）

**定义**：说明如何配置项目，包含具体的 skill 引用。

**判断标准**：文档是配置指南或初始化流程。

**示例**：
```markdown
# Quick Start Guide
## Setup
1. Run `/update-framework ~/dev/ai-dev`
2. Run `/manage-project --select-profile`
3. Run `/init-docs`
```

**为什么允许**：配置步骤需要具体的 skill 名称。

---

## ❌ 禁止硬编码的 3 种场景

### 1. 模板示例（Template Examples）

**定义**：CLAUDE_MD_GUIDE.md 中的项目模板。

**问题**：模板应该是通用的，不应绑定具体 skill。

**错误示例**：
```markdown
## ⚡ Skills System
- /start-issue
- /execute-plan
- /finish-issue
```

**正确示例**：
```markdown
## ⚡ Skills System

**AI生成指令**：
1. 扫描 `.claude/skills/` 目录获取所有 skills
2. 从 YAML frontmatter 提取 name 和 description
3. 按功能分类生成列表
```

**为什么禁止**：不同项目有不同的 skills，模板应该教 AI 如何生成，而不是硬编码。

---

### 2. 代码示例（Code Examples）

**定义**：SKILL_GUIDE.md 中的代码模板。

**问题**：代码示例应该使用抽象占位符。

**错误示例**：
```python
Skill("update-pillars", args="~/framework")
Skill("update-skills", args="~/framework")
```

**正确示例**：
```python
Skill("{{sync-skill-1}}", args="{{args-1}}")
Skill("{{sync-skill-2}}", args="{{args-2}}")
```

**为什么禁止**：代码示例是教学用的，应该是通用模式，不是具体实现。

---

### 3. 废弃引用（Deprecated References）

**定义**：引用已废弃的 skill（如 `/adr`, `/maintain-project`）。

**问题**：废弃 skill 应该从文档中完全移除。

**错误示例**：
```markdown
| ADR_GUIDE.md | 创建 ADR | `/adr` 或 `/manage-adrs` |
```

**正确示例**：
```markdown
| ADR_GUIDE.md | 创建 ADR | `/manage-adrs` |
```

**为什么禁止**：废弃的 skill 会导致用户困惑和错误调用。

---

## 🔍 判断流程

**遇到需要引用 skill 时，按以下流程判断**：

```
1. 是否是主题文档（文档标题包含 skill 名称）？
   ├─ 是 → ✅ 允许硬编码
   └─ 否 → 继续

2. 是否是流程架构（展示 skill 调用链）？
   ├─ 是 → ✅ 允许硬编码
   └─ 否 → 继续

3. 是否是配置文档（初始化/设置步骤）？
   ├─ 是 → ✅ 允许硬编码
   └─ 否 → 继续

4. 是否是模板示例？
   ├─ 是 → ❌ 禁止硬编码，改用 AI 生成指令
   └─ 否 → 继续

5. 是否是代码示例？
   ├─ 是 → ❌ 禁止硬编码，改用抽象占位符
   └─ 否 → 继续

6. 是否引用废弃 skill？
   ├─ 是 → ❌ 禁止硬编码，删除引用
   └─ 否 → ✅ 允许硬编码（默认）
```

---

## 📚 实际应用

### 示例 1：workflow/README.md

**场景**：列出 guides 和对应 skills。

**判断**：
- 不是主题文档（README 是索引）
- 不是流程架构（只是列表）
- 是配置文档（告诉用户何时使用）

**结论**：✅ 允许硬编码，但必须删除废弃引用。

**修复**：
```diff
- | ADR_GUIDE.md | 创建 ADR | `/adr` 或 `/manage-adrs` |
+ | ADR_GUIDE.md | 创建 ADR | `/manage-adrs` |
```

---

### 示例 2：CLAUDE_MD_GUIDE.md 模板

**场景**：项目模板中的 Skills System 章节。

**判断**：
- 不是主题文档（模板是通用的）
- 不是流程架构（只是列表）
- 不是配置文档（是模板）
- 是模板示例

**结论**：❌ 禁止硬编码，改用 AI 生成指令。

**修复**：
```diff
- ## ⚡ Skills System
- - /start-issue
- - /execute-plan
+ ## ⚡ Skills System
+ **AI生成指令**：
+ 1. 扫描 .claude/skills/ 目录
+ 2. 提取 YAML frontmatter
+ 3. 生成分类列表
```

---

### 示例 3：SKILL_GUIDE.md 代码示例

**场景**：组合技能的代码模板。

**判断**：
- 不是主题文档（是通用指南）
- 不是流程架构（是代码片段）
- 不是配置文档（是教学）
- 是代码示例

**结论**：❌ 禁止硬编码，改用抽象占位符。

**修复**：
```diff
- Skill("update-pillars", args="~/framework")
- Skill("update-skills", args="~/framework")
+ Skill("{{sync-skill-1}}", args="{{target-path}}")
+ Skill("{{sync-skill-2}}", args="{{target-path}}")
```

---

## 🛠️ 维护规范

### AI 执行检查

**当 AI 维护 guides 时，必须遵循此 policy**：

1. **读取此文档** - 在修改任何 guide 前先读取 HARDCODING_POLICY.md
2. **应用判断流程** - 按照判断流程决定是否可以硬编码
3. **修复违规** - 将禁止的硬编码改为 AI 生成指令或抽象占位符
4. **删除废弃引用** - 完全移除已废弃的 skill

### 人工审查

**Code Review 时检查**：

```bash
# 查找所有 guide 文件
find .claude/guides -name "*.md"

# 检查是否有废弃 skill 引用
git grep "/adr\|/maintain-project\|/update-rules\|/dev-issue" .claude/guides/

# 检查模板是否硬编码（应该包含 "AI生成指令"）
git grep "## ⚡ Skills System" .claude/guides/workflow/CLAUDE_MD_GUIDE.md
```

---

## 📋 检查清单

**维护 guides 时的自检清单**：

```
- [ ] 读取 HARDCODING_POLICY.md
- [ ] 识别文档类型（主题/流程/配置/模板/代码）
- [ ] 应用判断流程
- [ ] 删除所有废弃 skill 引用
- [ ] 模板改用 AI 生成指令
- [ ] 代码改用抽象占位符
- [ ] 运行 git grep 验证无遗留
```

---

## 🔗 相关文档

- [.claude/guides/README.md](.claude/guides/README.md) - Guides 系统概览
- [.claude/guides/workflow/README.md](.claude/guides/workflow/README.md) - Workflow Guides 索引
- [ADR-013](../../docs/ADRs/013-rules-generation-workflow.md) - Rules 生成工作流（类似原则）

---

**Version**: 1.0.0
**Created**: 2026-04-01 (Issue #444)
**Last Updated**: 2026-04-01
**Purpose**: 明确 guides 中硬编码的边界，防止过度耦合
