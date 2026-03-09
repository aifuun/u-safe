# Issue #4: arch/Database_Schema.md: 定义数据库表结构

**GitHub**: https://github.com/aifuun/u-safe/issues/4
**Branch**: feature/4-database-schema
**Started**: 2026-03-09

## Context

定义 U-Safe 的 SQLite 数据库结构，这是所有业务逻辑的基础。需要基于 ADR 0002 (技术栈) 和 ADR 0003 (加密方案) 设计表结构。

## Tasks

- [ ] 设计文件元数据表 (files)
  - 文件 ID、路径、加密状态
  - 文件大小、MIME 类型
  - 创建/修改时间

- [ ] 设计标签表 (tags)
  - 标签 ID、名称、颜色
  - 父标签（支持层级）

- [ ] 设计文件-标签关联表 (file_tags)
  - 多对多关系
  - 关联时间戳

- [ ] 设计加密元数据表 (encryption_meta)
  - 文件 ID
  - 加密算法（AES-256-GCM）
  - Nonce/IV
  - 分块信息

- [ ] 设计配置表 (config)
  - Key-Value 存储
  - 用户偏好设置

- [ ] 创建完整的数据库 Schema 文档
  - 表定义（字段类型、约束）
  - 索引策略
  - 关系图
  - 迁移策略
  - 输出到 `docs/arch/Database_Schema.md`

## Acceptance Criteria

- [ ] 所有 5 个表都有完整定义（字段、类型、约束）
- [ ] 表之间关系清晰（外键、索引）
- [ ] 符合 SQLite 最佳实践
- [ ] 支持 ADR 0003 的加密方案（分块、Nonce、MAC）
- [ ] 文档格式清晰，包含示例 SQL
- [ ] 文档输出到正确位置：`docs/arch/Database_Schema.md`

## Dependencies

- ✅ Issue #1 (ADR 0002) - 技术栈已确定
- ✅ Issue #2 (ADR 0003) - 加密方案已确定

## Progress

- [x] Plan created
- [ ] Tables designed
- [ ] Schema documented
- [ ] Ready for review

## Next Steps

1. Review this plan
2. Get first task: `/next`
3. Start designing tables
4. When done: `/finish-issue #4`

## References

- ADR 0002 (Tech Stack): `docs/adr/0002-technical-stack.md`
- ADR 0003 (Encryption): `docs/adr/0003-encryption-strategy.md`
- PRD Storage Layout: `docs/prd/PRD.md#3.2`
- SQLite Best Practices: https://www.sqlite.org/bestpractice.html
