# U-Safe (万能保险箱)

> U 盘文件加密管理工具 — 军事级加密 + 虚拟标签整理

## 技术栈

Tauri 2.0 + Rust (后端) + React 18 + TailwindCSS (前端) + SQLite

## 核心文档

开发时按需读取，不要凭记忆猜测，先读文档再实现：

| 文档 | 路径 | 用途 |
|------|------|------|
| 产品需求 | `docs/product/PRD.md` | 完整产品定义 |
| 产品路线图 | `docs/product/roadmap.md` | 功能范围、优先级、里程碑 |
| 架构设计 | `docs/arch/ARCHITECTURE.md` | 系统架构、分层设计 |
| 数据库设计 | `docs/arch/Database_Schema.md` | 5 个核心表结构 |
| 设计系统 | `docs/design/DESIGN_SYSTEM.md` | 设计 token + 组件规范 |
| UI/UX 规范 | `docs/design/UI_UX_DESIGN.md` | 界面设计规范 |

## MVP 关键约束

- 单用户、离线、无提权、本地 SQLite
- 加密: AES-256-GCM + Argon2id + 64KB 分块
- 平台: Windows 10/11 + macOS (Intel/Apple Silicon)
- MVP 语言: 仅中文界面
- 不包含: 云同步、多语言、批量操作、自动更新

## 编码规范

- **Rules**: `.claude/rules/` — 按文件路径自动触发，无需手动查找
- **Pillars**: `.prot/pillars/` — 18 个深度编码标准 (200-300 行/个)，Rules 中有链接指向对应 Pillar

### Pillars 概览

| 象限 | Pillars | 与 U-Safe 关联 |
|------|---------|---------------|
| **Q1 数据完整性** | A 名义类型, B 校验, C Mock, D 状态机 | 类型安全、加密数据校验 |
| **Q2 流程并发** | E 编排, F 并发, Q 幂等 | 加密流程编排 |
| **Q3 结构边界** | G 追踪, H 策略, I 防火墙, J 局部性, K 测试, L 无头 | React/Rust 分层架构 |
| **Q4 韧性可观测** | M Saga, N 上下文, O 异步, P 熔断, R 可观测 | 错误恢复、日志 |

## ADRs

位置: `docs/adr/` (唯一位置，不要在别处创建)

| # | 标题 | 位置 |
|---|------|------|
| 001 | Design Token System (CSS Variables) | `docs/adr/` |
| 002 | Record Architecture Decisions | `docs/adr/` |
| 003 | Technical Stack | `docs/adr/` |
| 004 | Encryption Strategy | `docs/adr/` |
| 006 | Unified Data Directory | `docs/adr/` |
