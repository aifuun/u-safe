# AI Workflow Guides

> AI 执行开发任务的参考标准

## 📚 Guides 列表

| Guide | 用途 | 使用场景 |
|-------|------|----------|
| **ADR_GUIDE.md** | 创建架构决策记录 | `/adr` 或 `/manage-adrs` skill |
| **CLAUDE_MD_GUIDE.md** | 维护 CLAUDE.md | `/maintain-project` 或 `/manage-claude-md` skill |
| **ISSUE_LIFECYCLE_GUIDE.md** | Issue 生命周期流程 | `/solve-issues`, `/auto-solve-issue` skills |
| **PROJECT_PLANNING_GUIDE.md** | 项目规划标准 | 项目初始化和规划 |
| **SKILL_GUIDE.md** | Skill 开发规范 | `/skill-creator` skill |

## 🎯 用途

这些 guides 是 **AI 的参考标准**，在执行相关 skills 时会被读取。

**For AI:**
- AI skills 在运行时读取对应的 guide
- Guide 提供结构、标准、最佳实践
- 确保 AI 生成的内容符合规范

**For Humans:**
- 了解 AI 的决策依据
- 审查 AI 生成的内容
- 理解项目的文档标准

## 🔄 同步

这些 guides 通过 `/update-guides` skill 从 framework 同步到目标项目：

```bash
# 在目标项目中运行
/update-guides ~/path/to/framework

# 只同步 workflow/ 子目录（不包括 doc-templates/）
```

## 📖 详细说明

### ADR_GUIDE.md
- 定义 ADR（Architecture Decision Record）结构
- YAML frontmatter 标准
- 必需章节：TL;DR, Context, Decision, Consequences
- 长度限制：50-150 行

### CLAUDE_MD_GUIDE.md
- 定义 CLAUDE.md 文件结构
- 必需章节：What Is This Project, Skills System, How to Use
- 不应包含的内容：实现细节、完整 API 文档

### ISSUE_LIFECYCLE_GUIDE.md
- 定义 5 个阶段工作流
- Phase 1: start-issue, Phase 1.5: eval-plan
- Phase 2: execute-plan, Phase 2.5: review
- Phase 3: finish-issue

### PROJECT_PLANNING_GUIDE.md
- 项目规划标准
- 4 层规划：Strategy → Campaign → Tactics → Code

### SKILL_GUIDE.md
- Skill 开发规范
- YAML frontmatter 标准
- 文件结构和命名规则

---

**Parent:** [../README.md](../README.md)
**Last Updated:** 2026-03-26 (Issue #337)
