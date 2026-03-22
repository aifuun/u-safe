# Issue #43: 统一数据目录：所有文件存储在 .u-safe/ 下（符合 PRD 设计）

**GitHub**: https://github.com/aifuun/u-safe/issues/43
**Branch**: feature/43-unified-data-directory
**Worktree**: /Users/woo/dev/u-safe-43-unified-data-directory
**Started**: 2026-03-22

## Context

当前代码中存在**数据目录不一致**的架构缺陷：不同模块使用不同的数据目录，导致应用数据分散存储，违背了 PRD 中"U 盘端存储布局"的设计意图。

### 当前问题

```rust
// ❌ password.rs - 使用系统数据目录
let data_dir = dirs::data_dir()              // macOS: ~/Library/Application Support/
    .join(".u-safe");

// ✅ db/mod.rs - 使用 USB 检测目录
let data_dir = usb_detection::get_data_dir(); // .u-safe/ (当前或 USB)
```

**实际后果**：
```
数据库     → 项目目录/.u-safe/u-safe.db
密码哈希   → ~/Library/Application Support/.u-safe/keys/password.hash
主密钥     → 未知位置（相对路径）

❌ 同一个应用的数据分裂在 3 个位置！
```

### PRD 设计意图

根据 `docs/product/PRD.md` 第 3.2 节"存储布局设计（U 盘端）"：

```
/.usafe/ (系统隐藏)：
  * config.json：用户偏好设置
  * index.db：SQLite 标签与文件元数据索引
  * data/：存放加密后的二进制分块数据
```

**原设计**：所有数据（数据库、密码、密钥、日志）都应该存储在 **U 盘根目录的 `.u-safe/` 下**。

## Tasks

### Phase 1: 修复密码管理模块 (30分钟)

- [ ] 阅读当前实现 `src-tauri/src/crypto/password.rs:78-85`
- [ ] 修改 `get_hash_file_path()` 函数
  - 将 `dirs::data_dir()` 改为 `crate::usb_detection::get_data_dir()`
  - 确保路径为 `{data_dir}/keys/password.hash`
- [ ] 测试密码设置功能
- [ ] 验证文件位置正确（应在 `./.u-safe/keys/password.hash`）

### Phase 2: 修复密钥存储模块 (30分钟)

- [ ] 阅读当前实现 `src-tauri/src/crypto/keystore.rs:15`
- [ ] 移除硬编码的 `MASTER_KEY_FILE` 常量
- [ ] 添加 `get_master_key_path()` 函数
  - 使用 `crate::usb_detection::get_data_dir()`
  - 返回 `{data_dir}/keys/master.key`
- [ ] 更新所有使用 `MASTER_KEY_FILE` 的代码
- [ ] 测试密钥生成和读取

### Phase 3: 添加数据迁移逻辑 (1小时)

- [ ] 在 `src-tauri/src/lib.rs` 添加 `migrate_old_data()` 函数
- [ ] 实现旧数据检测逻辑
  - 检查 `dirs::data_dir().join(".u-safe")` 是否存在
  - 与新路径 `usb_detection::get_data_dir()` 比较
- [ ] 实现迁移逻辑
  - 迁移 `keys/password.hash`
  - 迁移 `keys/master.key`
  - 创建目标目录结构
- [ ] 添加日志记录
  - 迁移开始
  - 迁移完成
  - 保留旧数据提示
- [ ] 在应用启动时调用 `migrate_old_data()`

### Phase 4: 测试验证 (1小时)

- [ ] **单元测试**
  - 测试 `get_hash_file_path()` 返回正确路径
  - 测试 `get_master_key_path()` 返回正确路径
- [ ] **集成测试**
  - 测试密码设置后文件在正确位置
  - 测试密钥创建后文件在正确位置
  - 测试数据迁移功能（模拟旧数据存在）
- [ ] **手动测试**
  - 开发环境数据在 `./.u-safe/`
  - 验证数据迁移流程
  - 验证所有功能正常工作

### Phase 5: 文档更新 (1小时)

- [ ] **创建 ADR-006: 数据目录架构决策**
  - 记录为什么选择纯 U 盘模式
  - 记录拒绝混合模式的原因
  - 记录安全性考虑（Argon2id 足以抵抗暴力破解）
  - 记录跨平台兼容性方案
- [ ] **更新 PRD**
  - 明确 `.u-safe/` 完整目录结构
  - 添加日志目录说明
- [ ] **更新 README**
  - 说明数据存储位置
  - 添加数据备份建议

## Acceptance Criteria

### 代码修改

- [ ] **所有模块使用统一路径**
  - [ ] `password.rs` 使用 `usb_detection::get_data_dir()`
  - [ ] `keystore.rs` 使用 `usb_detection::get_data_dir()`
  - [ ] 未来的 `logging.rs` 使用 `usb_detection::get_data_dir()`

- [ ] **数据目录结构正确**
  ```
  .u-safe/
  ├── u-safe.db
  ├── keys/
  │   ├── password.hash
  │   └── master.key
  └── logs/  # 未来
  ```

- [ ] **数据迁移（如果有旧数据）**
  - [ ] 检测系统目录下的旧数据
  - [ ] 自动迁移到新位置
  - [ ] 日志记录迁移过程
  - [ ] 保留旧数据（不自动删除）

### 测试验证

- [ ] **单元测试** - 路径函数返回正确
- [ ] **集成测试** - 文件存储位置正确
- [ ] **手动测试** - 所有功能正常工作

### 文档更新

- [ ] **ADR-006** - 架构决策记录完整
- [ ] **PRD** - 目录结构说明清晰
- [ ] **README** - 用户指南完善

## 影响范围

| 模块 | 当前路径 | 修复后路径 | 文件 |
|------|---------|-----------|------|
| 数据库 | ✅ 正确 | 保持不变 | `db/mod.rs` |
| 密码管理 | ❌ 系统目录 | `.u-safe/keys/` | `crypto/password.rs` |
| 密钥存储 | ❌ 相对路径 | `.u-safe/keys/` | `crypto/keystore.rs` |
| 日志系统 | ⚠️ 未实现 | `.u-safe/logs/` | 待实现 |

## 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 现有用户数据丢失 | 低 | 高 | 实现自动迁移脚本 + 保留旧数据 |
| 迁移逻辑错误 | 低 | 中 | 充分测试 + 日志记录 |
| 跨平台路径问题 | 低 | 中 | 使用 `PathBuf` + Win/Mac 测试 |

## Progress

- [x] Plan reviewed
- [x] Phase 1 完成（密码模块）
- [x] Phase 2 完成（密钥模块）
- [x] Phase 3 完成（数据迁移）
- [x] Phase 4 完成（测试验证）
- [x] Phase 5 完成（文档更新）
- [x] Ready for review

## Next Steps

1. 开始 Phase 1: 修复密码管理模块
2. 阅读 `src-tauri/src/crypto/password.rs`
3. 修改 `get_hash_file_path()` 函数
4. 测试验证

## 关联文档

- **PRD**: `docs/product/PRD.md` 第 3.2 节
- **问题分析**: `.claude/plans/active/directory-architecture-issue.md`
- **阻塞功能**: `.claude/plans/active/logging-system-design.md`

## 实施工时估算

- Phase 1: 修复密码管理模块 - 30 分钟
- Phase 2: 修复密钥存储模块 - 30 分钟
- Phase 3: 数据迁移逻辑 - 1 小时
- Phase 4: 测试验证 - 1 小时
- Phase 5: 文档更新（含 ADR-006） - 1 小时

**总计**: 4 小时

## 优先级说明

**P0 Critical**：此问题是架构级缺陷，影响：
1. ❌ 阻塞日志系统实现（不知道用哪个目录）
2. ❌ 违背 PRD 设计意图（数据应该在 U 盘）
3. ❌ 影响产品便携性（密码在系统目录）
4. ❌ 数据管理混乱（分散在多个位置）

必须**立即修复**后才能继续其他功能开发。
