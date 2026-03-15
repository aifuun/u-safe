# 📂 U-Safe 文档中心

> U 盘文件加密管理工具 — 军事级加密 + 虚拟标签整理

**技术栈**: Tauri 2.0 + Rust + React 18 + TailwindCSS + SQLite

---

## 🎯 核心文档（必读）

开发前请先阅读相关文档，不要凭记忆猜测：

| 文档 | 路径 | 用途 | 状态 |
|------|------|------|------|
| **产品路线图** | [`roadmap/ROADMAP.md`](./roadmap/ROADMAP.md) | 特性与版本对应规划（MVP - v2.0） | ✅ |
| **MVP 定义** | [`roadmap/MVP_Definition.md`](./roadmap/MVP_Definition.md) | 功能范围、优先级、里程碑 | ✅ |
| **产品需求** | [`prd/PRD.md`](./prd/PRD.md) | 完整产品定义 | ✅ |
| **核心逻辑** | [`spec/PRD_Core_Logic.md`](./spec/PRD_Core_Logic.md) | 加密/解密/标签业务流程 | ✅ |
| **数据库设计** | [`spec/Database_Schema.md`](./spec/Database_Schema.md) | 5 个核心表结构 | ✅ |
| **UI/UX 设计** | [`spec/UI_UX_Design_System.md`](./spec/UI_UX_Design_System.md) | 设计 token + 组件规范 | ✅ |

---

## 📁 文档架构

```
docs/
├── README.md                          # 📍 本文件 - 文档导航中心
│
├── roadmap/                           # 📊 产品规划
│   ├── ROADMAP.md                     # 特性与版本对应（MVP - v2.0）
│   └── MVP_Definition.md              # MVP 详细定义
│
├── prd/                               # 📋 产品需求
│   └── PRD.md                         # 完整产品需求文档
│
├── spec/                              # 📐 技术规格
│   ├── PRD_Core_Logic.md              # 核心业务流程
│   ├── Database_Schema.md             # 数据库设计
│   └── UI_UX_Design_System.md         # UI/UX 设计规范
│
└── ADRs/                              # 🏛️ 架构决策记录
    ├── README.md                      # ADR 索引
    ├── 001-*.md                       # Design Token System
    ├── 002-*.md                       # Record Architecture Decisions
    ├── 003-*.md                       # Technical Stack
    └── 004-*.md                       # Encryption Strategy
```

---

## 🚀 快速导航

### 按角色查找

#### 👨‍💼 产品经理/项目负责人
- **了解产品全貌** → [`prd/PRD.md`](./prd/PRD.md)
- **查看版本规划** → [`roadmap/ROADMAP.md`](./roadmap/ROADMAP.md)
- **确认 MVP 范围** → [`roadmap/MVP_Definition.md`](./roadmap/MVP_Definition.md)

#### 👨‍💻 开发者
- **开始新特性前** → 先查 [`roadmap/ROADMAP.md`](./roadmap/ROADMAP.md#特性矩阵) 确认版本
- **实现业务逻辑** → 参考 [`spec/PRD_Core_Logic.md`](./spec/PRD_Core_Logic.md)
- **操作数据库** → 参考 [`spec/Database_Schema.md`](./spec/Database_Schema.md)
- **设计 UI 组件** → 参考 [`spec/UI_UX_Design_System.md`](./spec/UI_UX_Design_System.md)
- **技术决策依据** → 查阅 [`ADRs/`](./ADRs/)

#### 🎨 设计师
- **设计系统规范** → [`spec/UI_UX_Design_System.md`](./spec/UI_UX_Design_System.md)
- **用户体验流程** → [`spec/PRD_Core_Logic.md`](./spec/PRD_Core_Logic.md)

#### 🧪 测试人员
- **编写测试计划** → 参考 [`roadmap/ROADMAP.md`](./roadmap/ROADMAP.md) 各版本的"成功标准"
- **验收标准** → [`roadmap/MVP_Definition.md`](./roadmap/MVP_Definition.md#成功标准)

---

## 🎯 按任务查找

### 场景 1: 开始新功能开发

```
1. 打开 roadmap/ROADMAP.md
2. 搜索功能名称（如"多语言支持"）
3. 找到对应版本（如 v1.1）
4. 查看:
   - 优先级（P0/P1/P2）
   - 工作量估算
   - 成功标准
   - 对应 Issue 编号
5. 阅读相关技术规格:
   - spec/PRD_Core_Logic.md (业务逻辑)
   - spec/Database_Schema.md (数据结构)
   - spec/UI_UX_Design_System.md (UI 规范)
6. 开始实现
```

### 场景 2: 评估新需求

```
1. 打开 roadmap/ROADMAP.md
2. 滚动到"特性矩阵"
3. 查找该功能是否已规划
4. 如果未规划:
   - 决定加入哪个版本
   - 更新对应版本的"新增特性"表格
   - 更新"特性矩阵"
   - 在"决策记录"说明原因
5. 创建 GitHub Issue 并链接
```

### 场景 3: Sprint 规划

```
1. 打开 roadmap/ROADMAP.md
2. 定位到当前版本（如 MVP v1.0）
3. 查看"核心特性"表格
4. 按优先级选择任务:
   - P0 优先
   - P1 其次
   - P2 有余力再做
5. 检查"对应 Issue"列
6. 拖入 Sprint Board
```

### 场景 4: 技术决策

```
1. 打开 ADRs/ 目录
2. 查找相关决策记录:
   - 技术选型 → ADR-003
   - 加密方案 → ADR-004
   - 设计系统 → ADR-001
3. 如果没有现成决策:
   - 讨论并达成共识
   - 创建新的 ADR
   - 更新 ADRs/README.md 索引
```

---

## 📊 文档间关系

```
ROADMAP.md (跨版本规划)
    │
    ├─→ MVP_Definition.md (MVP 详细定义)
    │       │
    │       ├─→ PRD.md (产品需求)
    │       │
    │       ├─→ PRD_Core_Logic.md (业务流程)
    │       │
    │       ├─→ Database_Schema.md (数据库)
    │       │
    │       └─→ UI_UX_Design_System.md (设计规范)
    │
    ├─→ v1.1 (概要)
    ├─→ v1.2 (概要)
    └─→ v2.0 (概要)

ADRs/ (技术决策依据)
    ├─→ ADR-001: Design Token System
    ├─→ ADR-002: Record Architecture Decisions
    ├─→ ADR-003: Technical Stack
    └─→ ADR-004: Encryption Strategy
```

**使用建议**:
- **跨版本规划** → 查 `ROADMAP.md`
- **当前版本详细** → 查 `MVP_Definition.md`
- **具体功能实现** → 查 `spec/` 目录
- **技术决策依据** → 查 `ADRs/` 目录

---

## 🔐 核心架构准则

在开发时，必须遵守以下原则（详见 ADRs）：

### 安全性
- ✅ 加密算法: AES-256-GCM (AEAD)
- ✅ 密钥派生: Argon2id (mem=64MB, time=3, lanes=1)
- ✅ 分块大小: 64 KB (流式加密)
- ✅ 内存清零: 使用 `zeroize` crate
- ❌ 密码不写入日志
- ❌ 不在宿主硬盘缓存明文

### 数据存储
- ✅ 所有数据存储在 U 盘 `.u-safe/` 目录
- ✅ SQLite WAL 模式
- ✅ 原子写入 (临时文件 + rename)
- ❌ 不在宿主系统留下痕迹

### 跨平台
- ✅ Windows 10/11 原生支持
- ✅ macOS (Intel + Apple Silicon)
- ✅ 无管理员权限要求
- ❌ MVP 不支持 Linux (延后到 v2.0)

---

## 🛠️ 文档维护规范

### 何时更新文档？

| 情况 | 操作 |
|------|------|
| **新增功能** | 更新 `ROADMAP.md` 对应版本 + 创建 Issue |
| **功能延期** | 在 `ROADMAP.md` 移动特性 + 记录到"决策记录" |
| **技术决策** | 创建新 ADR 并更新 `ADRs/README.md` |
| **设计变更** | 更新 `UI_UX_Design_System.md` |
| **数据库变更** | 更新 `Database_Schema.md` |
| **业务流程变更** | 更新 `PRD_Core_Logic.md` |

### 修改规则

1. **重大变更**: 必须创建 ADR 记录决策过程
2. **文档同步**: 代码实现后及时更新对应文档
3. **版本标记**: 每次重大更新后修改文档底部的"最后更新时间"
4. **不删除旧决策**: ADR 只标记为 `Superseded`，不删除

---

## 🤖 与 Claude Code 协同开发

### 提示词模板

#### 需求分析阶段
```
Claude，请阅读 docs/spec/PRD_Core_Logic.md。
我要实现【功能名】，请结合 docs/ADRs/ 中的技术决策，
给出 Rust 后端和 React 前端的实现思路。
```

#### 代码生成阶段
```
参考 docs/spec/Database_Schema.md 中的表结构，
请为我生成 src-tauri/src/db/{table_name}.rs 的 CRUD 函数。
```

#### 质量检查阶段
```
我刚完成了【模块名】，请对照 docs/roadmap/MVP_Definition.md
中的成功标准，检查我的实现是否符合要求。
```

#### 规划任务阶段
```
查看 docs/roadmap/ROADMAP.md，
列出当前 Sprint 应该做的 P0 任务（按优先级排序）。
```

---

## 📚 参考资料

### 内部文档
- [项目根目录 CLAUDE.md](../CLAUDE.md) - AI 开发框架说明
- [.claude/rules/](../.claude/rules/) - 开发规范和最佳实践

### 外部资源
- [Tauri 2.0 官方文档](https://v2.tauri.app/)
- [Rust 加密库 ring](https://github.com/briansmith/ring)
- [React 18 文档](https://react.dev/)
- [SQLite 文档](https://www.sqlite.org/docs.html)

---

## 🎯 MVP 关键约束（速查）

| 维度 | 约束 |
|------|------|
| **语言** | 仅中文界面 |
| **平台** | Windows 10/11 + macOS (Intel/Apple Silicon) |
| **用户** | 单用户、离线、无云同步 |
| **存储** | 本地 SQLite，数据在 U 盘 |
| **权限** | 无需管理员权限 |
| **性能** | 冷启动 < 2s，加密 > 50 MB/s |
| **体积** | 应用 < 10 MB |
| **不包含** | 多语言、批量操作、云同步、自动更新 |

---

## 📍 当前状态

| 项目 | 状态 |
|------|------|
| **当前阶段** | 🟡 MVP v1.0 开发中 (M1 项目骨架) |
| **下一里程碑** | M2: 加密引擎 (P0 功能可用) |
| **目标日期** | 2026-03-31 |
| **文档完成度** | 核心文档 100%，实施文档进行中 |

详见: [`roadmap/ROADMAP.md`](./roadmap/ROADMAP.md)

---

## 💡 快速开始

**第一次接触项目？**

1. 阅读 [`roadmap/MVP_Definition.md`](./roadmap/MVP_Definition.md) - 了解 MVP 目标和范围
2. 阅读 [`spec/PRD_Core_Logic.md`](./spec/PRD_Core_Logic.md) - 理解核心业务流程
3. 查看 [`roadmap/ROADMAP.md`](./roadmap/ROADMAP.md) - 了解完整产品规划
4. 根据当前 Sprint 任务，查阅对应的技术规格文档
5. 开始编码前，检查 [`ADRs/`](./ADRs/) 确认技术方案

**开始新 Sprint？**

1. 打开 [`roadmap/ROADMAP.md`](./roadmap/ROADMAP.md)
2. 定位到当前版本（MVP v1.0）
3. 按 P0 → P1 → P2 优先级选择任务
4. 创建/关联 GitHub Issues
5. 开始开发

---

**最后更新时间**: 2026-03-14
**文档版本**: v2.0 (新增 ROADMAP.md)
**维护者**: U-Safe 开发团队

---

## 📮 反馈与贡献

发现文档问题或有改进建议？

- 提交 GitHub Issue (标签: `documentation`)
- 直接提交 PR 修改文档
- 联系项目负责人

**文档改进指南**: 清晰 > 完整 > 美观
