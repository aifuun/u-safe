# 📂 /docs 目录 README：U-Safe 项目知识库

> **身份申明**：本目录是 **U-Safe (万能保险箱)** 的核心大脑，包含了从商业逻辑到代码实现的所有权衡与标准。

## 🎯 核心设计哲学

1. **免安装 (Portable)**：所有数据必须跟随 U 盘，不依赖宿主系统路径。
2. **原生感 (Native Feel)**：UI 必须像素级还原 Win11/macOS，不产生异物感。
3. **安全至上 (Security First)**：采用 AES-256-GCM 流式加密，确保即使 U 盘意外拔出，数据依然完整受损极小。
4. **逻辑整理 (Logic Over Physical)**：物理目录不动，通过 SQLite 标签系统实现灵活整理。

---

## 🏗️ 目录结构规范

| 文件夹 | 职责描述 | 主要包含文件 | Claude 读取建议 |
| --- | --- | --- | --- |
| **[`spec/`](./spec)** | **业务规格**：定义"是什么"。 | PRD、UI/UX 交互规范、功能需求列表。 | 涉及功能边界和 UI 样式时必读。 |
| **[`arch/`](./arch)** | **系统架构**：定义"怎么做"。 | 安全架构白皮书、数据库 Schema、API 通信协议。 | 涉及 Rust 后端和数据库操作时必读。 |
| **[`adr/`](./adr)** | **决策记录**：记录"为什么"。 | 0001-技术栈选型、0002-加密方案、0003-跨平台策略。 | **核心优先级**：在重构代码前必须参考决策历史。 |
| **[`roadmap/`](./roadmap)** | **执行蓝图**：定义"何时做"。 | MVP 定义、开发里程碑 (Phase 1-3)、积压任务 (Backlog)。 | 确定当前迭代目标时使用。 |
| **[`dev/`](./dev)** | **工程指引**：定义"怎么跑"。 | 环境配置、代码签名指南、发布流程。 | 解决构建和打包问题时使用。 |

---

## 📝 决策记录 (ADR) 规范

所有的重大技术决策必须记录在 `docs/adr/NNNN-title.md` 中。

* **状态流**：`Proposed` (提议中) → `Accepted` (已接受) → `Superseded` (已废弃/替代)。
* **Claude 提示**：若发现代码实现与 ADR 冲突，请优先遵循 ADR 或向开发者发起询问。

---

## 🤖 与 Claude Code 协同开发指引

为了获得最高效的 AI 辅助，请在启动时或涉及核心模块开发时，向 Claude 发送以下指令：

> *"Claude, 请先阅读 `docs/adr` 了解我们的加密选型和架构原则，并参考 `docs/spec` 中的 UI 规范。现在我们要开始实现 [具体功能名]，请基于这些文档给出代码建议。"*

---

## 🚀 快速导航

* **想要了解产品逻辑？** 查看 [`/docs/spec/PRD_Core_Logic.md`](./spec/PRD_Core_Logic.md)
* **想要了解加密实现细节？** 查看 [`/docs/arch/Security_Whitepaper.md`](./arch/Security_Whitepaper.md)
* **想要了解当前开发进度？** 查看 [`/docs/roadmap/Development_Phases.md`](./roadmap/Development_Phases.md)
* **想要查找数据库表结构？** 查看 [`/docs/arch/Database_Schema.md`](./arch/Database_Schema.md)

---

**Last Updated**: 2026-03-08
**Owner**: U-Safe Senior Architect & PM

---

### 💡 架构师的补充提醒

在你的 `docs/` 文件夹下，建议第一个创建的文件就是这个 `README.md`。接下来，你可以按照我们之前讨论的列表，依次让 Claude 帮你生成：

1. `adr/0001-record-architecture-decisions.md`
2. `adr/0002-technical-stack.md`
3. `arch/Database_Schema.md`

**你准备好让 Claude 生成第一个 ADR（技术栈决策记录）了吗？**
