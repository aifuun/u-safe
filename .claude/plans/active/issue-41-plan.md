# Issue #41: 实现 Master Key Wrapping 加密架构重构

**GitHub**: https://github.com/aifuun/u-safe/issues/41
**Branch**: feature/issue-41-master-key-wrapping
**Worktree**: /Users/woo/dev/u-safe-41-master-key-wrapping
**Started**: 2026-03-23

## Context

重构加密架构，实现 Master Key Wrapping 模式，为修改密码功能打基础。

**当前架构问题**：
- 密码 → Argon2id → 派生密钥 → 直接加密文件
- 修改密码 = 新密钥 ≠ 旧密钥 → 必须重新加密所有文件（耗时数小时）

**Master Key Wrapping 架构**：
```
用户密码（可更改）
  ↓ Argon2id
密码派生密钥 (KEK)
  ↓ AES-256-GCM 加密
主密钥 Master Key（固定，32字节随机）
  ↓ AES-256-GCM
加密文件（永不改变）
```

**优势**：
- ✅ 修改密码只需重新加密 Master Key（<1秒，与文件数量无关）
- ✅ 文件保持不变，无需重新加密
- ✅ 降低文件损坏风险
- ✅ 用户体验极佳（瞬间完成）

## Tasks

### Phase 1: 核心模块实现（2天）

- [ ] **Task 1: 创建 MasterKeyManager 模块**
  - 实现 `initialize()` - 生成随机主密钥并加密
  - 实现 `unwrap()` - 用密码密钥解密主密钥
  - 实现 `rewrap()` - 用新密码重新包装主密钥
  - 实现 `get_wrapped_key_path()` - 返回存储路径
  - 添加单元测试

- [ ] **Task 2: 修改 derive_master_key IPC 命令**
  - 检测是否首次设置（password.hash 和 wrapped_master_key 不存在）
  - 首次设置：生成主密钥，调用 `MasterKeyManager::initialize()`
  - 登录验证：调用 `MasterKeyManager::unwrap()` 解密主密钥
  - 将解密后的主密钥保存到内存（用于后续加密/解密）

- [ ] **Task 3: 修改加密/解密逻辑**
  - 修改 `encrypt_file()` 使用 Master Key（不再用密码派生密钥）
  - 修改 `decrypt_file()` 使用 Master Key
  - 确保所有加密操作使用同一个 Master Key

### Phase 2: 集成测试（1天）

- [ ] **Task 4: 测试完整流程**
  - 测试首次设置密码 → 生成 Master Key → 加密文件
  - 测试登录验证 → 解密 Master Key → 解密文件
  - 测试多个文件加密/解密
  - 验证 `wrapped_master_key` 文件正确保存

- [ ] **Task 5: 测试边界情况**
  - 错误密码 → unwrap 失败，返回明确错误
  - 删除 `wrapped_master_key` → 提示文件损坏
  - 删除 `password.hash` 但保留 `wrapped_master_key` → 提示不一致

### Phase 3: 文档和清理（0.5天）

- [ ] **Task 6: 更新文档**
  - 更新 ADR-004（加密策略）
  - 添加 Master Key Wrapping 架构图
  - 更新用户手册（密码设置流程）

- [ ] **Task 7: 代码审查和优化**
  - 检查内存安全（使用 `zeroize` 清零敏感数据）
  - 检查错误处理
  - 添加日志记录

## Acceptance Criteria

- [ ] `MasterKeyManager` 模块实现完整（initialize, unwrap, rewrap）
- [ ] 首次设置密码时自动生成 Master Key
- [ ] `wrapped_master_key` 文件正确保存到 `~/.u-safe/keys/`
- [ ] 登录时正确解密 Master Key
- [ ] 所有文件加密使用 Master Key（不再直接用密码派生密钥）
- [ ] 所有文件解密使用 Master Key
- [ ] 错误密码时返回明确错误信息
- [ ] 单元测试覆盖核心功能（initialize, unwrap, rewrap）
- [ ] 集成测试通过（完整加密/解密流程）
- [ ] 文档更新完成

## Technical Details

### 1. MasterKeyManager 模块

```rust
// src-tauri/src/crypto/master_key.rs

pub struct MasterKeyManager {
    wrapped_key: Vec<u8>,  // 加密后的主密钥
}

impl MasterKeyManager {
    /// 初始化：生成主密钥并用密码加密
    pub fn initialize(password_key: &[u8; 32]) -> Result<Self>;

    /// 解密主密钥
    pub fn unwrap(&self, password_key: &[u8; 32]) -> Result<[u8; 32]>;

    /// 修改密码：重新包装主密钥
    pub fn rewrap(
        &mut self,
        old_password_key: &[u8; 32],
        new_password_key: &[u8; 32]
    ) -> Result<()>;
}
```

### 2. 文件存储

```
~/.u-safe/keys/
  ├── password.hash        (密码哈希，PHC 格式)
  └── wrapped_master_key   (加密后的主密钥，32字节密文)
```

### 3. 安全考虑

**优点**：
- ✅ 双层加密（密码 → KEK → Master Key → 文件）
- ✅ Master Key 随机生成（32 字节熵）
- ✅ 使用 AES-256-GCM 加密 Master Key
- ✅ 内存安全（zeroize 清零）

**风险**：
- ⚠️ 如果 `wrapped_master_key` 损坏，所有文件无法解密
- **缓解**：未来实现恢复密钥导出功能（Issue #44）

## Progress

- [ ] Plan reviewed
- [ ] Implementation started
- [ ] Tests added
- [ ] Ready for review

## Next Steps

1. Review this plan
2. Get first task: /next
3. Start implementation
4. When done: /finish-issue #41

## Time Estimate

**总计**: 3-4 天
- Phase 1: 2 天（核心实现）
- Phase 2: 1 天（测试）
- Phase 3: 0.5 天（文档）
- 缓冲: 0.5 天

## Dependencies

无依赖，可独立实现。

## Related Issues

- Issue #43: 实现修改密码功能（依赖本 issue）
- Issue #44: 恢复密钥导出/导入（增强安全性）

## References

- 设计文档：.claude/plans/active/password-reset-design.md
- ADR-004：加密策略
- NIST SP 800-38D：GCM 模式规范
