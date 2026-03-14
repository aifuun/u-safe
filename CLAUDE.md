# U-Safe (万能保险箱)

> U 盘文件加密管理工具 — 军事级加密 + 虚拟标签整理

## 技术栈

Tauri 2.0 + Rust (后端) + React 18 + TailwindCSS (前端) + SQLite

## 核心文档

开发时按需读取，不要凭记忆猜测，先读文档再实现：

| 文档 | 路径 | 用途 |
|------|------|------|
| MVP 定义 | `docs/roadmap/MVP_Definition.md` | 功能范围、优先级、里程碑 |
| 产品需求 | `docs/prd/PRD.md` | 完整产品定义 |
| 核心逻辑 | `docs/spec/PRD_Core_Logic.md` | 加密/解密/标签业务流程 |
| 数据库设计 | `docs/spec/Database_Schema.md` | 5 个核心表结构 |
| UI/UX 设计 | `docs/spec/UI_UX_Design_System.md` | 设计 token + 组件规范 |

## MVP 关键约束

- 单用户、离线、无提权、本地 SQLite
- 加密: AES-256-GCM + Argon2id + 64KB 分块
- 平台: Windows 10/11 + macOS (Intel/Apple Silicon)
- MVP 语言: 仅中文界面
- 不包含: 云同步、多语言、批量操作、自动更新

## 编码规范

- **Rules**: `.claude/rules/` — 按文件路径自动触发，无需手动查找
- **Pillars**: 18 个深度编码标准，Rules 中有链接指向对应 Pillar

## ADRs

位置: `docs/ADRs/` (唯一位置，不要在别处创建)

| # | 标题 | 内容 |
|---|------|------|
| 001 | Official Skill Patterns | Skill 结构标准 |
| 002 | Skill Creation Workflow | `/skill-creator` + 简化测试 |
