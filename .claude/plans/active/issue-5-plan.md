# Issue #5: spec/PRD_Core_Logic.md: 细化产品核心逻辑

**GitHub**: https://github.com/aifuun/u-safe/issues/5
**Branch**: feature/5-prd-core-logic
**Started**: 2026-03-09

## Context

详细阐述 U-Safe 的核心业务逻辑，包括加密流程、标签管理、虚拟视图等。基于已完成的 ADR 0003 (加密方案) 和 Database Schema 设计。

## Tasks

- [ ] 设计加密/解密流程
  - 用户首次设置密码流程
  - 文件加密流程图（基于 AES-256-GCM + 64KB 分块）
  - 文件解密流程图
  - 密码验证机制（Argon2id）

- [ ] 设计标签管理逻辑
  - 标签创建/编辑/删除
  - 标签层级关系（基于 tags 表的 parent_tag_id）
  - 标签批量操作

- [ ] 设计虚拟视图（影子视图）
  - 物理视图 vs 标签视图切换
  - 文件在标签视图中的显示逻辑
  - 标签视图中的文件操作

- [ ] 设计文件操作流程
  - 新增文件（自动加密）
  - 删除文件（标签移除 vs 物理删除）
  - 移动文件（仅限物理视图）
  - 重命名文件

- [ ] 创建完整的核心逻辑文档
  - 流程图（Mermaid 格式）
  - 状态转换图
  - 错误处理策略
  - 输出到 `docs/spec/PRD_Core_Logic.md`

## Acceptance Criteria

- [ ] 所有 4 个核心模块都有详细流程说明
- [ ] 包含流程图（Mermaid 格式）
- [ ] 基于 ADR 0003 的加密方案（AES-256-GCM + Argon2id）
- [ ] 基于 Database Schema 的数据操作流程
- [ ] 错误处理和边界情况覆盖
- [ ] 文档输出到正确位置：`docs/spec/PRD_Core_Logic.md`

## Dependencies

- ✅ Issue #2 (ADR 0003) - 加密策略已确定
- ✅ Issue #4 (Database Schema) - 数据库设计已完成

## Progress

- [x] Plan created
- [ ] Core logic designed
- [ ] Documentation complete
- [ ] Ready for review

## Next Steps

1. Review this plan
2. Get first task: `/next`
3. Start designing core logic
4. When done: `/finish-issue #5`

## References

- ADR 0003 (Encryption): `docs/adr/0003-encryption-strategy.md`
- Database Schema: `docs/arch/Database_Schema.md`
- PRD: `docs/prd/PRD.md`
