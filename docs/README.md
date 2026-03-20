# u-safe 项目文档

> 本文档结构遵循 [ai-dev 文档标准](../ai-dev/docs/DOCUMENTATION_MANUAL.md)

## 📁 文档结构

### 产品文档
- [PRD.md](product/PRD.md) - 产品需求文档
- [roadmap.md](product/roadmap.md) - 产品路线图

### 架构文档
- [ARCHITECTURE.md](arch/ARCHITECTURE.md) - 系统架构概述
- [SCHEMA.md](arch/SCHEMA.md) - 数据模型设计
- [API.md](arch/API.md) - API 接口文档

### 设计文档
- [UI_UX_DESIGN.md](design/UI_UX_DESIGN.md) - UI/UX 设计规范
- [DESIGN_SYSTEM.md](design/DESIGN_SYSTEM.md) - 设计系统实施
- [diagrams/](design/diagrams/) - 设计图表
  - [README.md](design/diagrams/README.md) - 图表管理
  - [VERIFICATION.md](design/diagrams/VERIFICATION.md) - Mermaid 验证

### 开发文档
- [SETUP.md](dev/SETUP.md) - 开发环境搭建
- [CONTRIBUTING.md](dev/CONTRIBUTING.md) - 贡献指南

### 质量保证
- [TEST_PLAN.md](qa/TEST_PLAN.md) - 测试策略

### 架构决策记录
- [adr/](adr/) - 技术决策记录
  - [001-design-token-system-css-variables.md](adr/001-design-token-system-css-variables.md)
  - [002-record-architecture-decisions.md](adr/002-record-architecture-decisions.md)
  - [003-technical-stack.md](adr/003-technical-stack.md)
  - [004-encryption-strategy.md](adr/004-encryption-strategy.md)

## 🔍 快速参考

| 我想... | 查看文档 |
|--------|---------|
| 了解产品功能 | [PRD.md](product/PRD.md) |
| 搭建开发环境 | [SETUP.md](dev/SETUP.md) |
| 理解系统架构 | [ARCHITECTURE.md](arch/ARCHITECTURE.md) |
| 查看数据模型 | [SCHEMA.md](arch/SCHEMA.md) |
| 了解 UI/UX 设计 | [UI_UX_DESIGN.md](design/UI_UX_DESIGN.md) |
| 查看设计系统 | [DESIGN_SYSTEM.md](design/DESIGN_SYSTEM.md) |
| 了解测试策略 | [TEST_PLAN.md](qa/TEST_PLAN.md) |
| 查看技术决策 | [adr/](adr/) |

## 📏 文档标准

- 📘 [完整标准](DOCUMENTATION_MANUAL.md) - 项目本地副本
- 📋 [迁移指南](../ai-dev/docs/DOCUMENTATION_MIGRATION_GUIDE.md) - 框架参考
- ✅ [验证工具](/check-docs)

## 📊 文档迁移记录

本文档结构已于 2026-03-20 从旧结构迁移至 ai-dev 标准结构。

**迁移映射**:
- `ADRs/` → `adr/` (目录名改为小写)
- `arch/Database_Schema.md` → `arch/SCHEMA.md` (重命名)
- `prd/PRD.md` + `spec/PRD_Core_Logic.md` → `product/PRD.md` (合并)
- `roadmap/*.md` → `product/roadmap.md` (合并)
- `spec/UI_UX_Design_System.md` → `design/UI_UX_DESIGN.md` (移动)
- `spec/DESIGN_SYSTEM_ENFORCEMENT.md` → `design/DESIGN_SYSTEM.md` (移动)
- `spec/diagrams/` → `design/diagrams/` (移动)
- `spec/DIAGRAM_MANAGEMENT.md` → `design/diagrams/README.md` (移动)
- `spec/MERMAID_VERIFICATION.md` → `design/diagrams/VERIFICATION.md` (移动)

**备份**: 原始文档结构已备份至 `docs.old/` 目录

---

**最后更新**: 2026-03-20 | **文档评分**: 运行 `/check-docs` 查看当前评分
