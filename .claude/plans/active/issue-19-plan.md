# Issue #19: Phase 2 (M2): 加密引擎 - Encryption Engine

**GitHub**: https://github.com/aifuun/u-safe/issues/19
**Branch**: feature/19-encryption-engine
**Started**: 2026-03-16
**Duration**: 13 days (Optimistic: 10 days, Pessimistic: 16 days)
**Phase**: 2/6 (M2)
**Priority**: P0

---

## 🎯 目标

实现核心加密/解密功能，确保安全性和性能：
- AES-256-GCM 加密算法
- Argon2id 密钥派生
- 64KB 分块流式处理
- 内存安全和临时文件清理

---

## 📋 任务清单

### Task Group 1: Password Management (3 days)

**Task 1.1: Implement Argon2id KDF**
- 使用 `argon2` crate
- 配置参数: mem=64MB, time=3, parallelism=1
- 生成 32 字节主密钥
- 随机 16 字节 salt
- 文件: `src-tauri/src/crypto/kdf.rs`

**Task 1.2: Master Password UI**
- 密码输入组件（前端 React）
- 强度验证（长度 >= 8，包含大小写+数字）
- 确认密码输入
- 错误提示
- 文件: `app/src/components/PasswordInput.tsx`

**Task 1.3: Password Verification Logic**
- 主密码哈希存储（Argon2id）
- 验证流程（Rust 后端）
- 错误次数限制（3 次锁定 5 分钟）
- 文件: `src-tauri/src/crypto/password.rs`

**Task 1.4: Master Key Storage**
- 主密钥加密存储（使用密码派生的密钥）
- 存储位置: `.u-safe/keys/master.key`
- 读取和解密逻辑
- 文件: `src-tauri/src/crypto/keystore.rs`

**Task 1.5: Password Error Handling**
- 错误密码提示
- 重试逻辑
- 锁定机制
- 文件: `src-tauri/src/crypto/password.rs`

**Task 1.6: Memory Zeroing**
- 使用 `zeroize` crate
- 密钥用完后清零
- Drop trait 实现
- 文件: `src-tauri/src/crypto/key.rs`

---

### Task Group 2: AES-256-GCM Encryption (5 days)

**Task 2.1: Implement AES-256-GCM Encryption**
- 使用 `aes-gcm` crate
- 加密单个 64KB 块
- 随机 12 字节 nonce
- MAC 生成
- 文件: `src-tauri/src/crypto/aes.rs`

**Task 2.2: Implement AES-256-GCM Decryption**
- 解密单个块
- MAC 验证
- 错误处理（MAC 失败）
- 文件: `src-tauri/src/crypto/aes.rs`

**Task 2.3: 64KB Chunked Streaming**
- 文件流式读取（64KB 块）
- 分块加密逻辑
- 进度跟踪（百分比）
- 内存优化（不加载整个文件）
- 文件: `src-tauri/src/crypto/stream.rs`

**Task 2.4: Random Salt/Nonce Generation**
- 使用 `rand` crate
- 安全随机数生成
- Salt: 16 字节（Argon2id）
- Nonce: 12 字节（AES-GCM，每块不同）
- 文件: `src-tauri/src/crypto/random.rs`

**Task 2.5: MAC Authentication**
- MAC 验证逻辑
- 认证失败处理
- 完整性检查
- 文件: `src-tauri/src/crypto/aes.rs`

**Task 2.6: Error Handling and Recovery**
- 加密失败回滚
- 部分加密文件清理
- 错误传播到前端
- 文件: `src-tauri/src/crypto/error.rs`

---

### Task Group 3: File I/O (3 days)

**Task 3.1: Source File Reading**
- 打开原文件
- 流式读取（BufReader）
- 文件大小获取
- 文件: `src-tauri/src/file/reader.rs`

**Task 3.2: Encrypted File Writing**
- 写入到 `.u-safe/data/{id}.enc`
- 加密元数据头（文件名、大小、salt、nonce）
- 加密块写入
- 文件: `src-tauri/src/file/writer.rs`

**Task 3.3: Decrypt to Temp File**
- 临时文件路径（系统 temp 目录）
- 解密并写入
- 临时文件权限（仅当前用户可读）
- 文件: `src-tauri/src/file/temp.rs`

**Task 3.4: Temp File Cleanup**
- 关闭时自动删除
- Drop trait 实现
- 异常情况清理
- 文件: `src-tauri/src/file/temp.rs`

**Task 3.5: Atomic Write (Temp + Rename)**
- 写入到 `.enc.tmp`
- 完成后重命名到 `.enc`
- 断电保护
- 文件: `src-tauri/src/file/writer.rs`

**Task 3.6: Power Failure Testing**
- 模拟断电场景
- 验证文件完整性
- 恢复机制
- 文件: `src-tauri/tests/power_failure.rs`

---

### Task Group 4: Testing (2 days)

**Task 4.1: Unit Test - KDF Consistency**
- 相同密码生成相同密钥
- 不同 salt 生成不同密钥
- 文件: `src-tauri/tests/kdf_test.rs`

**Task 4.2: Unit Test - Encrypt/Decrypt Roundtrip**
- 加密后解密，内容一致
- 不同文件大小测试（1KB, 1MB, 100MB）
- 文件: `src-tauri/tests/crypto_test.rs`

**Task 4.3: Performance Test - Encryption Speed > 50 MB/s**
- 测量加密速度
- 验证 > 50 MB/s
- 文件: `src-tauri/tests/perf_test.rs`

**Task 4.4: Performance Test - 100MB File < 2s**
- 100MB 测试文件
- 加密 + 解密总时间 < 2 秒
- 文件: `src-tauri/tests/perf_test.rs`

**Task 4.5: Security Test - Wrong Password**
- 错误密码无法解密
- MAC 验证失败
- 文件: `src-tauri/tests/security_test.rs`

**Task 4.6: Security Test - Memory Leak Detection**
- 使用 Valgrind 或 Rust sanitizer
- 验证无内存泄漏
- 文件: `src-tauri/tests/memory_test.rs`

---

## 🎯 成功标准

- ✅ **性能**: 100MB 文件加密 < 2 秒
- ✅ **性能**: 加密速度 > 50 MB/s
- ✅ **安全**: 错误密码无法解密
- ✅ **安全**: 临时文件自动清理
- ✅ **安全**: 内存清零（zeroize）
- ✅ **可靠**: 断电保护（原子写入）

---

## 📂 文件结构

```
src-tauri/src/crypto/
├── mod.rs           # 模块导出
├── kdf.rs           # Argon2id 密钥派生
├── password.rs      # 密码管理和验证
├── keystore.rs      # 主密钥存储
├── aes.rs           # AES-256-GCM 加密/解密
├── stream.rs        # 64KB 分块流式处理
├── random.rs        # 安全随机数生成
├── key.rs           # 密钥类型和内存清零
└── error.rs         # 加密错误类型

src-tauri/src/file/
├── mod.rs           # 模块导出
├── reader.rs        # 文件读取
├── writer.rs        # 文件写入（原子写入）
└── temp.rs          # 临时文件管理

app/src/components/
└── PasswordInput.tsx  # 密码输入 UI

src-tauri/tests/
├── kdf_test.rs
├── crypto_test.rs
├── perf_test.rs
├── security_test.rs
├── memory_test.rs
└── power_failure.rs

.u-safe/
├── keys/
│   └── master.key   # 加密后的主密钥
└── data/
    └── {id}.enc     # 加密文件
```

---

## 📚 参考文档

- **PRD Core Logic**: `docs/spec/PRD_Core_Logic.md`
- **Encryption Strategy (ADR-004)**: `docs/ADRs/004-encryption-strategy.md`
- **MVP Implementation Plan**: `docs/roadmap/MVP_v1.0_Implementation_Plan.md`
- **Database Schema**: `docs/spec/Database_Schema.md`

---

## 🔄 进度跟踪

- [ ] Plan reviewed
- [ ] Implementation started
- [ ] Password management complete
- [ ] AES-256-GCM encryption complete
- [ ] File I/O complete
- [ ] All tests passing
- [ ] Performance benchmarks met
- [ ] Security validation complete
- [ ] Ready for review

---

## 🚀 下一步

1. **Review this plan** - 确认任务清单完整
2. **Run /eval-plan #19** - 验证计划质量（推荐）
3. **Get first task**: `/next` - 开始第一个任务
4. **Start implementation** - 按任务顺序实现
5. **When done**: `/finish-issue #19` - 完成并关闭 Issue

---

**Dependencies**: Phase 1 (M1) ✅ Complete
**Blocks**: Phase 3 (M3) - File Management
**Estimated Completion**: Week 3 (Day 17-18)
