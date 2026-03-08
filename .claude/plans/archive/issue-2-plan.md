# Issue #2: ADR 0003: 加密方案选型

**GitHub**: https://github.com/aifuun/u-safe/issues/2
**Branch**: feature/2-adr-0003-encryption-strategy
**Started**: 2026-03-08

## Context

记录 U-Safe 的加密方案选型决策，明确为什么选择 AES-256-GCM 以及如何实现流式加密。

## Tasks

- [ ] 分析并记录为什么选择 AES-256-GCM
  - 对比 AES-CBC、ChaCha20-Poly1305
  - 认证加密（AEAD）的重要性
  - 硬件加速支持（AES-NI）

- [ ] 说明为什么采用流式加密（Chunked Streaming）
  - 大文件处理能力
  - 内存占用控制
  - 断点续传可能性

- [ ] 设计密钥管理策略
  - 密钥派生（KDF）方案选择
  - 密码强度要求
  - 内存中密钥保护机制

- [ ] 设计 U 盘意外拔出的数据完整性保护
  - 原子写入策略
  - 分块验证机制

- [ ] 创建完整的 ADR 文档
  - 按照 ADR 0001 格式规范
  - TL;DR ≤30 行，总文档 ≤100 行
  - 输出到 `docs/adr/0003-encryption-strategy.md`

## Acceptance Criteria

- [ ] ADR 文档完整回答4个核心问题
- [ ] 文档格式符合 ADR 0001 标准（≤100 行，TL;DR ≤30 行）
- [ ] TL;DR 包含关键执行参考（加密算法、分块大小、KDF 参数）
- [ ] 详细部分补充背景分析（不与 TL;DR 重复）
- [ ] 文档输出到正确位置：`docs/adr/0003-encryption-strategy.md`

## Progress

- [x] Plan reviewed
- [ ] Implementation started
- [ ] ADR document drafted
- [ ] Ready for review

## Next Steps

1. Review this plan
2. Get first task: `/next`
3. Start drafting ADR 0003
4. When done: `/finish-issue #2`

## References

- ADR 0001 template: `docs/adr/0001-record-architecture-decisions.md`
- ADR 0002 (Tech Stack): `docs/adr/0002-technical-stack.md`
- PRD Security Requirements: `docs/prd/PRD.md#4.2`
- Rust Crypto Libraries: ring, aes-gcm, argon2
