# U-Safe 系统架构文档

> U-Safe (万能保险箱) - U 盘文件加密管理工具的系统架构设计

**版本**: v1.0
**状态**: Active
**最后更新**: 2026-03-20

---

## 目录

1. [系统概述](#1-系统概述)
2. [技术栈](#2-技术栈)
3. [架构分层](#3-架构分层)
4. [模块划分](#4-模块划分)
5. [数据流](#5-数据流)
6. [关键设计决策](#6-关键设计决策)
7. [部署架构](#7-部署架构)
8. [性能考虑](#8-性能考虑)
9. [安全策略](#9-安全策略)
10. [架构图](#10-架构图)

---

## 1. 系统概述

### 1.1 系统定位

U-Safe 是一款**离线优先**的桌面应用程序，专为 U 盘用户设计，提供：

- **军事级文件加密** - AES-256-GCM 认证加密
- **虚拟标签整理** - 不改变物理路径的逻辑分类
- **跨平台兼容** - Windows 10/11 + macOS (Intel/Apple Silicon)
- **零提权运行** - 完全用户态操作，无需管理员权限

### 1.2 核心价值

1. **安全性** - 在不信任的环境（办公电脑）上保护 U 盘文件隐私
2. **便捷性** - 不改变用户原有文件组织习惯
3. **性能** - 大文件快速加解密（>50 MB/s），低内存占用
4. **可靠性** - 异常关闭时自动销毁内存密钥，无残留

### 1.3 关键约束

**MVP 阶段约束**:
- ✅ 单用户、离线、本地 SQLite
- ✅ 仅中文界面
- ❌ 不包含：云同步、多语言、批量操作、自动更新

**技术约束**:
- 完全用户态（无提权）
- exFAT 文件系统兼容（跨平台）
- 冷启动时间 < 2 秒（SSD U 盘）
- 二进制大小 < 10 MB（单平台）

---

## 2. 技术栈

### 2.1 核心框架

| 层级 | 技术 | 版本 | 理由 |
|------|------|------|------|
| **应用框架** | Tauri | 2.0 | 小体积、高性能、原生 Rust 后端 (ADR-003) |
| **前端框架** | React | 18 | 组件化、生态成熟、Tauri 官方支持 |
| **类型系统** | TypeScript | 5.x | 类型安全、开发体验 (Pillar A) |
| **UI 框架** | TailwindCSS | 3.x | 快速开发、Design Token 集成 (ADR-001) |
| **后端语言** | Rust | 1.75+ | 内存安全、性能、跨平台 (ADR-003) |
| **数据库** | SQLite | 3.45+ | 嵌入式、跨平台、单用户场景 |

### 2.2 关键库

**前端依赖**:
- `@tauri-apps/api` - Tauri IPC 通信
- `zustand` - 轻量状态管理
- `react-router-dom` - 路由

**后端依赖** (Rust Crates):
- `rusqlite` - SQLite 驱动（同步）
- `aes-gcm` - AES-256-GCM 加密
- `argon2` - 密钥派生
- `serde` / `serde_json` - 序列化
- `tauri` - 应用框架

### 2.3 技术选型理由

详见：
- **ADR-001**: Design Token System (CSS Variables)
- **ADR-003**: Technical Stack Selection
- **ADR-004**: Encryption Strategy

---

## 3. 架构分层

U-Safe 采用**三层架构 + 跨层服务**模式：

```
┌─────────────────────────────────────────────────────┐
│                    前端 (React)                      │
├─────────────────────────────────────────────────────┤
│  UI Layer         │  React Components               │
│                   │  - Views (加密视图、标签视图)    │
│                   │  - Widgets (文件卡片、标签树)    │
├───────────────────┼─────────────────────────────────┤
│  Service Layer    │  Frontend Services              │
│                   │  - fileService (文件操作封装)    │
│                   │  - tagService (标签逻辑)         │
├───────────────────┼─────────────────────────────────┤
│  State Layer      │  Zustand Stores                 │
│                   │  - UI 状态 (主题、侧边栏)        │
│                   │  - 应用状态 (文件列表、标签树)   │
├─────────────────────────────────────────────────────┤
│                   IPC Boundary (Tauri Commands)     │
├─────────────────────────────────────────────────────┤
│                    后端 (Rust)                       │
├─────────────────────────────────────────────────────┤
│  Commands Layer   │  Tauri Commands                 │
│                   │  - file_commands (CRUD)         │
│                   │  - crypto_commands (加密/解密)   │
│                   │  - tag_commands (标签管理)       │
├───────────────────┼─────────────────────────────────┤
│  Service Layer    │  Business Logic                 │
│                   │  - FileService (文件管理)        │
│                   │  - CryptoService (加密引擎)      │
│                   │  - TagService (标签服务)         │
├───────────────────┼─────────────────────────────────┤
│  Core Layer       │  Domain Logic                   │
│                   │  - CryptoEngine (AES-GCM)       │
│                   │  - ChunkProcessor (分块处理)     │
│                   │  - KeyDerivation (Argon2id)     │
├───────────────────┼─────────────────────────────────┤
│  Data Layer       │  Data Access                    │
│                   │  - DatabaseService (SQLite)     │
│                   │  - FileSystem (文件 I/O)         │
└─────────────────────────────────────────────────────┘
```

### 3.1 前端分层 (React)

**UI Layer** - React 组件
- **职责**: 渲染界面、处理用户交互
- **原则**:
  - 只负责展示逻辑，不包含业务逻辑
  - 使用 Design Tokens (参考 `.claude/rules/frontend/design-system.md`)
  - 遵循无障碍规范 (WCAG 2.1 AA)

**Service Layer** - Frontend Services
- **职责**: 封装 Tauri IPC 调用、前端业务逻辑
- **原则**:
  - 将 IPC 调用封装为语义化 API
  - 处理错误转换 (Rust Error → User Message)
  - 缓存频繁访问的数据

**State Layer** - Zustand Stores
- **职责**: 管理应用状态
- **原则**:
  - UI 状态 (主题、侧边栏) 留在前端
  - 业务数据 (文件列表) 从后端同步
  - 遵循 Pillar J (局部性) - 最小化状态共享

### 3.2 后端分层 (Rust)

**Commands Layer** - Tauri Commands
- **职责**: IPC 入口，参数验证
- **原则**:
  - 使用 `Result<T, String>` 返回类型
  - 输入验证 (Pillar B - Airlock)
  - 结构化日志 (`[module:operation:status]`)

**Service Layer** - Business Logic
- **职责**: 业务流程编排
- **原则**:
  - 协调多个 Core 模块
  - 事务管理 (数据库 + 文件系统)
  - 错误恢复 (Pillar M - Saga)

**Core Layer** - Domain Logic
- **职责**: 核心算法实现
- **原则**:
  - 纯函数设计，易于测试
  - 无外部依赖（数据库、文件系统）
  - 内存安全（使用 `zeroize` 清零密钥）

**Data Layer** - Data Access
- **职责**: 数据持久化
- **原则**:
  - 原子性（事务）
  - 隔离性（单用户，无并发）
  - 持久性（立即刷盘）

---

## 4. 模块划分

### 4.1 加密引擎模块 (CryptoEngine)

**职责**:
- AES-256-GCM 加密/解密
- 密钥派生 (Argon2id)
- 分块处理 (64KB chunks)
- 元数据管理

**关键文件**:
```
src-tauri/src/
├── crypto/
│   ├── engine.rs       # 加密引擎核心
│   ├── key_derivation.rs  # Argon2id KDF
│   ├── chunk.rs        # 分块处理
│   └── metadata.rs     # 加密元数据
```

**依赖**:
- `aes-gcm` crate
- `argon2` crate
- `zeroize` crate (内存清零)

**设计决策**: ADR-004 (Encryption Strategy)

### 4.2 标签管理模块 (TagManager)

**职责**:
- 标签 CRUD
- 标签树结构维护
- 文件-标签关联
- 虚拟视图查询

**关键文件**:
```
src-tauri/src/
├── tag/
│   ├── service.rs      # 标签服务
│   ├── tree.rs         # 标签树操作
│   └── query.rs        # 虚拟视图查询
```

**数据库表**:
- `tags` - 标签信息
- `file_tags` - 文件-标签关联

详见: `docs/arch/SCHEMA.md`

### 4.3 文件管理模块 (FileManager)

**职责**:
- 文件元数据 CRUD
- 物理文件操作 (复制、移动、删除)
- 文件状态跟踪 (已加密、已解密、加密中)

**关键文件**:
```
src-tauri/src/
├── file/
│   ├── service.rs      # 文件服务
│   ├── metadata.rs     # 元数据管理
│   └── operations.rs   # 文件操作
```

**数据库表**:
- `files` - 文件元数据
- `encryption_meta` - 加密参数

### 4.4 用户界面模块 (UI)

**职责**:
- 文件列表视图
- 标签树视图
- 加密/解密进度显示
- 设置页面

**关键文件**:
```
app/src/
├── 02_modules/
│   ├── files/          # 文件模块
│   ├── tags/           # 标签模块
│   ├── settings/       # 设置模块
│   └── debug/          # 调试面板 (开发者)
```

---

## 5. 数据流

### 5.1 文件加密流程

```
用户点击"加密"
  ↓
[UI] FileCard.tsx
  ↓ invoke('encrypt_file', { file_id, password })
[IPC] Tauri Commands
  ↓
[Service] CryptoService::encrypt_file()
  ├─ 读取文件元数据 (DatabaseService)
  ├─ 派生密钥 (Argon2id)
  ├─ 分块加密 (AES-256-GCM)
  │   ├─ 每 64KB 一个 chunk
  │   ├─ 发送进度事件 (emit 'encryption-progress')
  │   └─ 写入加密数据
  ├─ 保存加密元数据
  └─ 删除原文件（可选）
  ↓
[Event] Frontend 监听进度事件
  ↓
[UI] ProgressBar 更新
```

详见: `docs/design/diagrams/1-2-file-encryption.mmd`

### 5.2 标签创建流程

```
用户输入标签名
  ↓
[UI] TagCreateForm.tsx
  ↓ invoke('create_tag', { name, parent_id, color })
[IPC] Tauri Commands
  ↓
[Service] TagService::create_tag()
  ├─ 验证标签名（非空、长度 ≤ 50）
  ├─ 检查重复
  ├─ 插入数据库
  └─ 更新标签树缓存
  ↓
[State] Frontend 同步标签列表
  ↓
[UI] TagTree 刷新
```

详见: `docs/design/diagrams/2-1-tag-creation.mmd`

---

## 6. 关键设计决策

### 6.1 架构决策记录 (ADRs)

U-Safe 的关键架构决策记录在 `docs/adr/` 目录：

| ADR | 标题 | 关联模块 |
|-----|------|---------|
| [ADR-001](../adr/001-design-token-system-css-variables.md) | Design Token System | UI 模块 |
| [ADR-002](../adr/002-record-architecture-decisions.md) | Record Architecture Decisions | - |
| [ADR-003](../adr/003-technical-stack.md) | Technical Stack Selection | 整体架构 |
| [ADR-004](../adr/004-encryption-strategy.md) | Encryption Strategy | 加密引擎 |

### 6.2 设计原则 (Pillars)

U-Safe 遵循 18 个架构 Pillars (`.prot/pillars/`)，其中与系统架构直接相关的有：

**Q1: 数据完整性**
- **Pillar A (名义类型)**: 使用品牌类型区分 `FileId` / `TagId` / `UserId`
- **Pillar B (Airlock)**: IPC 边界验证所有输入
- **Pillar D (状态机)**: 文件状态机 (原始 → 加密中 → 已加密 → 解密中 → 已解密)

**Q2: 流程并发**
- **Pillar E (编排)**: 加密流程编排 (密钥派生 → 分块加密 → 元数据保存)
- **Pillar Q (幂等)**: 重试安全 (加密操作可重入)

**Q3: 结构边界**
- **Pillar G (追踪)**: 结构化日志 `[module:operation:status]`
- **Pillar H (策略)**: 输入验证策略 (文件名、标签名)
- **Pillar I (防火墙)**: IPC 边界隔离前后端
- **Pillar J (局部性)**: 模块内聚，最小化耦合

**Q4: 韧性可观测**
- **Pillar M (Saga)**: 加密事务补偿 (失败时回滚)
- **Pillar R (可观测)**: 日志、进度事件、错误报告

---

## 7. 部署架构

### 7.1 平台支持

| 平台 | 架构 | 二进制 | 最低版本 |
|------|------|--------|---------|
| **Windows** | x86_64 | U-Safe.exe | Windows 10 (1903+) |
| **macOS** | x86_64, aarch64 | U-Safe.app | macOS 11+ |

### 7.2 目录结构 (U 盘)

```
U:/  (U 盘根目录)
├── U-Safe.exe              # Windows 启动程序
├── U-Safe.app/             # macOS 应用包
├── .u-safe/                # 隐藏数据目录
│   ├── index.db            # SQLite 数据库
│   ├── keys/               # 密钥存储 (Salt)
│   ├── encrypted/          # 加密文件存储
│   │   ├── {file_id}.enc   # 加密后的文件
│   │   └── {file_id}.meta  # 加密元数据
│   └── config.json         # 用户配置
└── [用户原始文件]          # 未加密的文件
```

### 7.3 启动流程

```
用户双击 U-Safe.exe/app
  ↓
1. Tauri 启动 Rust 后端
  ├─ 检测 U 盘路径
  ├─ 初始化 SQLite 数据库
  ├─ 加载用户配置
  └─ 创建 Tauri 窗口
  ↓
2. 加载 React 前端
  ├─ 渲染 UI
  ├─ 初始化 Zustand Stores
  └─ 连接 Tauri IPC
  ↓
3. 显示主界面
  ├─ 如果有密码 → 显示解锁界面
  └─ 如果无密码 → 显示文件列表
```

冷启动目标: < 2 秒 (SSD U 盘)

---

## 8. 性能考虑

### 8.1 性能目标

| 指标 | 目标 | 测量方法 |
|------|------|---------|
| **冷启动时间** | < 2 秒 | 双击到显示 UI |
| **加密速度** | > 50 MB/s | 100MB 文件加密 < 2 秒 |
| **解密速度** | > 50 MB/s | 100MB 文件解密 < 2 秒 |
| **内存占用** | < 100 MB | 空闲时 |
| **二进制大小** | < 10 MB | 单平台压缩后 |

### 8.2 性能优化策略

**加密性能**:
- ✅ 使用硬件加速 (AES-NI)
- ✅ 64KB 分块处理 (流式，低内存)
- ✅ Rust 编译优化 (`release` profile)

**数据库性能**:
- ✅ 索引关键字段 (file_id, tag_id)
- ✅ 同步 I/O (单用户，无并发)
- ✅ WAL 模式 (更快写入)

**UI 性能**:
- ✅ 虚拟列表 (大文件列表)
- ✅ React.memo (避免不必要的渲染)
- ✅ 代码分割 (Lazy Loading)

详见: `.claude/rules/desktop/tauri-performance.md`

---

## 9. 安全策略

### 9.1 加密安全

**算法选择**:
- **对称加密**: AES-256-GCM (认证加密)
- **密钥派生**: Argon2id (抗暴力破解)
- **随机数**: `rand` crate (CSPRNG)

**密钥管理**:
- ❌ **不存储** 明文密码或密钥
- ✅ 从用户密码派生加密密钥 (Argon2id)
- ✅ Salt 随机生成并存储在 `.u-safe/keys/`
- ✅ 内存密钥使用 `zeroize` 清零

详见: ADR-004, `.claude/rules/infrastructure/secrets.md`

### 9.2 应用安全

**Tauri 安全配置**:
```json
{
  "tauri": {
    "allowlist": {
      "all": false,
      "fs": {
        "scope": ["$APPDATA/.u-safe/*", "$RESOURCE/*"]
      },
      "dialog": { "all": true },
      "shell": { "open": true }
    },
    "security": {
      "csp": "default-src 'self'; script-src 'self'"
    }
  }
}
```

详见: `.claude/rules/desktop/tauri-security.md`

### 9.3 数据安全

**零残留原则**:
- ❌ **禁止** 在宿主电脑硬盘缓存明文文件
- ✅ 解密后的临时文件仅存在于内存或 U 盘
- ✅ 应用关闭时自动销毁内存密钥
- ✅ U 盘拔出时自动锁定应用

---

## 10. 架构图

### 10.1 系统架构图

详见: [`docs/design/diagrams/system-architecture.mmd`](../design/diagrams/system-architecture.mmd)

```
[用户界面 (React)]
       ↕ (IPC)
[Tauri Commands (Rust)]
       ↕
[业务服务层 (Rust)]
  ├─ CryptoService
  ├─ FileService
  └─ TagService
       ↕
[数据访问层]
  ├─ SQLite (元数据)
  └─ FileSystem (加密文件)
```

### 10.2 数据流图

详见: [`docs/design/diagrams/data-flow.mmd`](../design/diagrams/data-flow.mmd)

加密/解密/标签的完整数据流转路径。

### 10.3 已有图表

项目已包含以下 Mermaid 图表 (位于 `docs/design/diagrams/`):

1. **1-1-password-setup.mmd** - 密码设置流程
2. **1-2-file-encryption.mmd** - 文件加密流程
3. **1-3-file-decryption.mmd** - 文件解密流程
4. **1-4-password-verification.mmd** - 密码验证流程
5. **2-1-tag-creation.mmd** - 标签创建流程
6. **3-1-view-switching.mmd** - 视图切换流程
7. **4-1-file-addition.mmd** - 文件添加流程

详见: [`docs/design/diagrams/README.md`](../design/diagrams/README.md)

---

## 相关文档

### 产品与需求
- [PRD.md](../product/PRD.md) - 产品需求文档
- [roadmap.md](../product/roadmap.md) - 产品路线图和 MVP 计划

### 架构与设计
- [SCHEMA.md](./SCHEMA.md) - 数据库设计
- [API.md](./API.md) - IPC 接口文档
- [UI_UX_DESIGN.md](../design/UI_UX_DESIGN.md) - UI/UX 设计系统
- [DESIGN_SYSTEM.md](../design/DESIGN_SYSTEM.md) - 设计系统实施

### 开发与测试
- [SETUP.md](../dev/SETUP.md) - 开发环境搭建
- [CONTRIBUTING.md](../dev/CONTRIBUTING.md) - 贡献指南
- [TEST_PLAN.md](../qa/TEST_PLAN.md) - 测试策略

### 架构决策
- [adr/](../adr/) - 所有架构决策记录

### 编码规范
- `.claude/rules/` - 编码规则
- `.prot/pillars/` - 架构 Pillars

---

**文档版本**: v1.0
**最后更新**: 2026-03-20
**维护者**: U-Safe 开发团队
**状态**: ✅ 架构文档完整
