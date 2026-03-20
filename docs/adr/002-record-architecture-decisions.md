# ADR 0001: 采用架构决策记录 (Architecture Decision Records)

## TL;DR (For AI Context)

**Decision**: 采用 ADR 记录所有重要架构和技术决策

**Why**:
1. 知识沉淀：决策背景永久记录，不因人员变动丢失
2. AI 友好：Claude Code 快速理解项目技术选型（TL;DR ≤30 行）
3. 避免重复讨论：已决策问题有明确记录
4. 版本化追溯：Git 历史可追踪决策演进

**Format 规范**:
- **长度限制**: TL;DR ≤30 行，整个 ADR ≤100 行
- **不重复原则**: TL;DR 和详细部分内容不重复，避免冗余
- **关键内容优先**: 执行参考、核心数据、决策结果放在 TL;DR
- **详细部分**: 补充背景、深入分析、备选方案对比（TL;DR 中未覆盖的内容）
- **无 Status**: 所有保留的 ADR 都是有效的，无效的直接删除文件

**File naming**: `NNNN-kebab-case.md` (如 `0002-technical-stack.md`)

**Trade-offs**:
- 👍 简洁高效、AI 友好、强制精炼
- 👎 需要精心组织内容、初次编写耗时
- ⚖️ 100 行限制需平衡完整性与简洁性

---

## Full Documentation (详细文档)

以下内容补充 TL;DR 中未涉及的背景信息和深入分析。

## Context

软件项目中的架构决策容易因时间和人员变化被遗忘，导致：
- 重复讨论已解决的问题
- 不了解历史背景而做出冲突改动
- 关键决策信息存在某人脑海中，离职后无法追溯
- AI 助手（Claude Code）无法理解项目的技术选型原因

传统方案（Wiki、代码注释、口头传承）都有明显缺陷：不与代码同步、难以全局视角、知识流失。

## Decision Details

ADR 是轻量级 Markdown 文件，与代码一起版本控制，包含：
- **TL;DR**: 为 AI 提供快速上下文，包含决策结果、关键数据、执行参考
- **Full Documentation**: 补充背景、深入分析、未在 TL;DR 中说明的细节

### 内容组织原则

**TL;DR 部分** (≤30 行，AI 主要阅读):
- Decision: 我们决定做什么
- Why: 3-5 条核心理由
- Format/Key Metrics: 关键数据、执行规范
- Trade-offs: 优缺点快速总览

**Full Documentation 部分** (≤70 行，人类深入阅读):
- Context: TL;DR 中未详述的背景（如历史问题、约束条件）
- Decision Details: TL;DR 中未展开的实施细节
- Consequences: 更详细的影响分析（正面/负面/中性）
- Alternatives Considered: 备选方案的深入对比

**不重复原则**: 同一信息不在两个部分重复出现，TL;DR 优先级高于详细部分。

## Consequences

### Positive
- **快速上手**: Claude Code 读 TL;DR（~300 tokens）即可理解 90% 决策
- **强制简洁**: 100 行限制避免过度冗长，信息密度高
- **版本化**: Git 历史记录决策演进过程
- **不重复**: 内容不冗余，行数利用率高

### Negative
- **编写挑战**: 在 100 行内说清楚需要精心组织
- **初次成本**: 首次编写需要反复精简
- **可能不足**: 极复杂决策可能需要拆分多个 ADR

## Alternatives Considered

### Alternative 1: 传统长文档
- 不选: Claude Code 读取成本高，容易冗长失焦

### Alternative 2: 仅 TL;DR
- 不选: 人类需要深入背景，30 行不足

### Alternative 3: Wiki/Confluence
- 不选: 不与代码同步，需额外工具

## References

- [ADR - Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [ADR GitHub](https://adr.github.io/)
