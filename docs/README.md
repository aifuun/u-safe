# 📂 U-Safe 项目知识库 (Project Knowledge Base)

> **项目愿景**：打造一款跨平台、免安装、原生感的 U 盘隐私管理与智能整理中心。
> **核心原则**：物理目录不动、无需管理员权限、军事级流式加密、双系统原生体验。

---

## 🏗️ 1. 文档架构全景图 (File Map)

我们采用"解耦合、分职责"的目录结构，确保每一个技术细节都有据可查，方便 Claude Code 快速检索上下文。

| 文件夹 | 职责 | 核心包含文件 |
| --- | --- | --- |
| **[`adr/`](./adr)** | **架构决策记录** | `0001-record-adr.md`, `0002-tech-stack.md`, `0003-aes-gcm-logic.md` |
| **[`spec/`](./spec)** | **产品逻辑与交互** | `PRD_Core_Logic.md`, `UI_UX_Design_System.md`, `User_Persona.md` |
| **[`arch/`](./arch)** | **技术方案深挖** | `Security_Whitepaper.md`, `Database_Schema.md`, `Tauri_IPC_Protocol.md` |
| **[`roadmap/`](./roadmap)** | **执行蓝图** | `MVP_Definition.md`, `Development_Phases.md`, `Backlog.md` |
| **[`qa/`](./qa)** | **质量与安全** | `Security_Audit_Cases.md`, `Hardware_Compatibility.md`, `Test_Plan.md` |
| **[`dev/`](./dev)** | **工程化支持** | `Environment_Setup.md`, `Build_Release_Guide.md`, `CI_CD_Workflow.md` |

---

## 🚀 2. 文档开发建议顺序 (Sequence)

为了保证项目的技术底座稳固，请按照以下顺序推动文档与代码开发：

1. **阶段一：确立契约 (The Foundation)**
   - 编写 `adr/0002` (技术栈) 和 `adr/0003` (加密选型)。
   - 编写 `arch/Database_Schema.md` (定义数据表，这是所有逻辑的基础)。

2. **阶段二：定义体验 (The Experience)**
   - 细化 `spec/PRD_Core_Logic.md` 和 `spec/UI_UX_Design_System.md`。
   - 明确 Win11/macOS 的差异化表现。

3. **阶段三：规划路径 (The Roadmap)**
   - 编写 `roadmap/MVP_Definition.md`，明确第一版只做哪些功能。

4. **阶段四：质量保障 (The Quality)**
   - 编写 `qa/Security_Audit_Cases.md`，在代码动工前定义好"什么样才算安全"。

5. **阶段五：同步开发 (Implementation)**
   - 根据文档实现 Rust 后端逻辑与 React 前端界面。

---

## 🔐 3. 核心架构准则 (Architectural Principles)

在利用 Claude Code 编写代码时，必须严格遵守以下 ADR 沉淀的准则：

- **数据隔离**：所有用户数据、标签信息、配置文件必须存储在 U 盘根目录的隐藏文件夹 `.usafe/` 中。
- **零足迹**：程序退出后，不得在宿主计算机（C盘）留下任何临时文件或注册表项。
- **流式加解密**：针对大文件，必须使用分块流式加密 (Chunked Streaming)，防止内存溢出。
- **路径中性**：代码中严禁使用硬编码路径，必须通过 Rust 动态获取 U 盘根目录（Relative Pathing）。

---

## 🤖 4. 如何使用 Claude Code 协同开发

为了让 Claude 成为你的高效助手，请遵循以下指令模式：

### A. 需求分析阶段

> *"Claude，请阅读 `docs/spec/PRD_Core_Logic.md`。我现在要设计'影子存储'的隐藏逻辑，请结合 `docs/ADRs/` 中的安全原则，给出 Rust 层的实现思路。"*

### B. 代码生成阶段

> *"参考 `docs/arch/Database_Schema.md` 中的 SQLite 表结构，请为我生成 `src-tauri/src/db.rs` 中的实体类和基础 CRUD 函数。"*

### C. 质量核查阶段

> *"我刚刚完成了文件加密模块，请对照 `docs/qa/Security_Audit_Cases.md` 中的测试用例，检查我的代码是否能够防御'意外拔出 U 盘导致的数据损坏'风险。"*

---

## 📝 5. 决策记录 (ADR) 规范

所有的重大技术决策必须记录在 `docs/ADRs/NNN-title.md` 中。

- **状态流**：`Proposed` (提议中) → `Accepted` (已接受) → `Superseded` (已废弃/替代)。
- **Claude 提示**：若发现代码实现与 ADR 冲突，请优先遵循 ADR 或向开发者发起询问。

---

## 🛠️ 6. 文档维护说明

- **ADR 状态变更**：当决策发生变化时，禁止直接修改旧 ADR，应新建 ADR 并将旧文件标记为 `Superseded`。
- **同步更新**：每当代码中的核心 API（Tauri Commands）发生变动，必须同步更新 `arch/Tauri_IPC_Protocol.md`。
- **Markdown 标准**：所有文档必须使用标准 Markdown，且数学公式需符合 LaTeX 规范（用于描述加密算法）。

---

## 🚀 7. 快速导航

- **想要了解产品逻辑？** 查看 [`/docs/spec/PRD_Core_Logic.md`](./spec/PRD_Core_Logic.md)
- **想要了解加密实现细节？** 查看 [`/docs/arch/Security_Whitepaper.md`](./arch/Security_Whitepaper.md)
- **想要了解当前开发进度？** 查看 [`/docs/roadmap/Development_Phases.md`](./roadmap/Development_Phases.md)
- **想要查找数据库表结构？** 查看 [`/docs/arch/Database_Schema.md`](./arch/Database_Schema.md)

---

**最后更新时间**：2026-03-08
**版本**：v1.0.0 (Initial Architect Baseline)
**责任人**：U-Safe 架构小组

---

### 💡 架构师寄语

这份文档体系是 **U-Safe** 的数字孪生。通过 **ADR** 记录思考过程，通过 **QA** 守护安全边界。现在，你可以先让 Claude 为你创建所有的文件夹及这个 `README.md`，然后从 `adr/0002` 技术栈选型开始你的开发旅程。

**需要我为你提供 `arch/Database_Schema.md` 的详细初稿，来定义核心的标签与加密映射关系吗？**
