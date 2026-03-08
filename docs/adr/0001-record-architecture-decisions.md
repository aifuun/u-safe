# ADR 0001: 采用架构决策记录 (Architecture Decision Records)

## Status

**Accepted** - 2026-03-08

## Context

在软件项目开发过程中，我们会做出许多重要的架构和技术决策。这些决策往往基于当时的技术环境、团队能力、业务需求等多种因素。随着时间推移和团队成员变化，这些决策的**背景和原因**很容易被遗忘，导致：

1. **重复讨论** - 新成员不理解为什么做某个选择，提出已经讨论过的问题
2. **错误修改** - 不了解历史决策，做出与架构设计相冲突的改动
3. **知识流失** - 关键决策信息存在于某个人脑海中，离职后无法追溯
4. **AI 协同困难** - Claude Code 等 AI 助手无法理解项目的技术选型原因

我们需要一种**轻量级、版本化、易于维护**的方式来记录这些重要决策。

## Decision

我们将采用 **Architecture Decision Records (ADR)** 来记录所有重要的架构和技术决策。

### ADR 格式规范

每个 ADR 文件必须包含以下章节：

```markdown
# ADR XXXX: [简短的决策标题]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-YYYY]

## Context
描述做出此决策时的背景、面临的问题、约束条件等。

## Decision
明确说明我们决定做什么。使用主动语态，例如"我们将使用 Rust"。

## Consequences

### Positive (正面影响)
- 列出此决策带来的好处

### Negative (负面影响)
- 列出此决策的代价、风险或限制

### Neutral (中性影响)
- 列出需要注意的事项

## Alternatives Considered

### Alternative 1: [方案名称]
- **优点**: ...
- **缺点**: ...
- **为什么不选**: ...

### Alternative 2: [方案名称]
- **优点**: ...
- **缺点**: ...
- **为什么不选**: ...
```

### 文件命名规范

- **格式**: `NNNN-short-title-in-kebab-case.md`
- **示例**: `0001-record-architecture-decisions.md`
- **编号**: 四位数字，从 0001 开始递增，不跳号
- **标题**: 使用 kebab-case（短横线分隔），英文或拼音

### 状态定义

| Status | 含义 | 使用场景 |
|--------|------|----------|
| **Proposed** | 提议中 | ADR 草稿，等待讨论和批准 |
| **Accepted** | 已接受 | 决策已通过，正在或将要实施 |
| **Deprecated** | 已废弃 | 决策不再适用，但未被其他 ADR 替代 |
| **Superseded by ADR-XXXX** | 已被替代 | 有新的 ADR 替代了此决策，注明新 ADR 编号 |

### 存储位置

- 所有 ADR 存放在 `docs/adr/` 目录
- 按编号顺序排列
- 使用 Git 进行版本控制

### 使用流程

1. **创建 ADR**
   - 复制此文件作为模板
   - 分配下一个可用编号
   - 填写各个章节
   - 初始状态设为 `Proposed`

2. **讨论和修订**
   - 通过 Git commit 记录修改历史
   - 在需要时进行团队讨论（或与 Claude Code 讨论）

3. **接受决策**
   - 确认后将状态改为 `Accepted`
   - 提交到主分支

4. **废弃或替代**
   - 不要删除旧 ADR
   - 更新状态为 `Deprecated` 或 `Superseded by ADR-XXXX`
   - 在新 ADR 中说明为什么要替代旧决策

## Consequences

### Positive

- **知识沉淀** - 决策背景和原因被永久记录，不会因人员变动而丢失
- **快速上手** - 新成员（包括 AI）可以通过 ADR 快速理解项目架构
- **避免重复讨论** - 已经讨论过的问题有明确的记录和结论
- **版本化追溯** - 通过 Git 历史可以看到决策的演进过程
- **AI 友好** - Claude Code 可以读取 ADR 来理解项目的技术选型和架构原则

### Negative

- **维护成本** - 需要额外时间编写和维护文档
- **可能过时** - 如果不及时更新，ADR 可能与实际代码脱节

### Neutral

- **文档必须简洁** - 避免过度详细，重点记录"为什么"而非"怎么做"
- **不是所有决策都需要 ADR** - 只记录有长期影响的架构级决策

## Alternatives Considered

### Alternative 1: Wiki 或 Confluence

- **优点**: 界面友好，支持富文本，易于搜索
- **缺点**:
  - 不与代码版本同步
  - 需要额外的工具和权限管理
  - 无法通过 Git 进行版本控制
- **为什么不选**: U-Safe 追求轻量化和便携性，不希望依赖外部服务

### Alternative 2: 代码注释

- **优点**: 与代码紧密结合，不需要额外文件
- **缺点**:
  - 难以获得架构全局视角
  - 注释容易被删除或遗漏
  - 无法记录被否决的方案
- **为什么不选**: 架构决策的受众不仅是开发者，还包括 PM、新成员和 AI 助手

### Alternative 3: 不记录，口头传承

- **优点**: 零成本，完全灵活
- **缺点**:
  - 知识随人员流失
  - 无法追溯历史决策
  - AI 助手无法获取上下文
- **为什么不选**: 这正是我们要解决的问题

## References

- [Architecture Decision Records (ADR) - Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [ADR GitHub Organization](https://adr.github.io/)
