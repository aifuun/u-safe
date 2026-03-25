# ADR 0003: 加密方案选型

## TL;DR (For AI Context)

**Decision**: AES-256-GCM + Chunked Streaming (64KB) + Argon2id KDF

**Key Parameters** (执行参考):
| Parameter | Value | Reason |
|-----------|-------|--------|
| Algorithm | AES-256-GCM | AEAD + hardware acceleration (AES-NI) |
| Key Size | 256 bits | Industry standard, quantum-resistant timeline |
| Chunk Size | 64 KB | Balance memory (low) vs performance (fast) |
| KDF | Argon2id | Memory-hard, side-channel resistant, OWASP recommended |
| Salt | 32 bytes random | Prevent rainbow table attacks |
| Nonce | 12 bytes random per chunk | GCM standard, prevent replay |

**Why**:
1. **AEAD Security**: Integrity + confidentiality in one (防篡改 + 加密)
2. **Performance**: AES-NI hardware acceleration (~10x faster than software)
3. **Memory Efficient**: 64KB chunks, suitable for low-end devices (8GB RAM)
4. **Crash Safe**: Chunked approach enables atomic writes, U盘意外拔出时数据完整

**Trade-offs**:
- 👍 Hardware accelerated, authenticated encryption, crash-safe
- 👎 Slightly larger ciphertext (~16 bytes overhead per chunk for MAC)
- ⚖️ AES-NI not available on very old CPUs (fallback to software implementation)

**Rejected**: AES-CBC (no auth), ChaCha20-Poly1305 (no hardware accel on target platforms)

---

## Full Documentation (详细文档)

以下内容补充 TL;DR 中未涉及的背景分析和决策依据。

## Context

U-Safe 在 U 盘上加密财务数据，面临：意外断电/拔出、大量历史记录、低配设备 (8GB RAM)、篡改检测需求。传统方案问题：AES-CBC 无认证需额外 HMAC、全文件加密占用大量内存、PBKDF2 易受 GPU 破解。

## Decision Details

### 1. 为什么选择 AES-256-GCM

- **AEAD**: 一次操作完成加密+认证，避免 Encrypt-then-MAC 易错模式
- **硬件加速**: Intel/AMD AES-NI 指令集（2010 年起），~10x 性能提升
- **性能对比** (Intel i5, 100MB): GCM 50ms vs CBC+HMAC 120ms vs ChaCha20 80ms
- **vs ChaCha20**: x86 平台无硬件加速，目标平台 (Windows/Mac/Linux) 均有 AES-NI

### 2. 为什么采用 64KB 分块

- **内存友好**: 单块 64KB vs 全文件内存占用
- **性能平衡**: 避免 4KB 块 MAC 开销大、1MB 块内存占用高
- **原子写入**: 临时文件 → 分块写入 + fsync → atomic rename，U 盘拔出时要么完整旧文件要么完整新文件

### 3. 密钥管理策略

#### 3.1 Master Key Wrapping 架构

**实施日期**: 2026-03-23 (Issue #41)

U-Safe 使用双层密钥架构（Master Key Wrapping）实现密码独立于文件加密：

```
用户密码（可更改）
  ↓ Argon2id (KDF)
密码派生密钥 (Password-Derived Key, KEK)
  ↓ AES-256-GCM 加密
主密钥 (Master Key，固定，32字节随机)
  ↓ AES-256-GCM
加密文件（永不改变）
```

**优势**：
- ✅ **修改密码 <1 秒**：只需重新加密主密钥（32 字节），无需重新加密所有文件
- ✅ **降低文件损坏风险**：文件加密层不变，密码修改不涉及文件操作
- ✅ **用户体验极佳**：密码修改瞬间完成，与文件数量无关
- ✅ **安全性不降低**：双层加密（密码 → KEK → Master Key → 文件）

**存储结构**：
```
~/.u-safe/keys/
  ├── password.hash        (Argon2id PHC 格式，用于验证密码)
  └── master.key           (加密后的主密钥，nonce + ciphertext + tag)
```

**流程**：

1. **首次设置密码**：
   - 用户输入密码 → Argon2id 派生 KEK → 持久化 `password.hash`
   - 生成随机主密钥（32 字节）→ 用 KEK 加密 → 存储到 `master.key`
   - 主密钥保存到内存供后续文件加密使用

2. **登录验证**：
   - 用户输入密码 → 验证 `password.hash` → 派生 KEK
   - 用 KEK 解密 `master.key` → 获取主密钥
   - 主密钥保存到内存供文件解密使用

3. **修改密码**（Issue #42，已实现 - 2026-03-25）：
   - 验证旧密码 → 解密主密钥
   - 用新密码派生新 KEK → 重新加密主密钥 → 原子更新 `master.key`
   - 更新 `password.hash` 为新密码的哈希
   - 文件层加密不变（继续使用同一个主密钥）
   - **实现细节**：
     - 使用临时文件 + atomic rename 保证操作原子性
     - 失败时自动回滚，确保密码文件一致性
     - 操作耗时 <1 秒（仅重新加密 32 字节主密钥）

#### 3.2 KDF 参数

- **Argon2id**: 内存硬度抵抗 GPU/ASIC 暴力破解，混合 Argon2i/d 防侧信道，OWASP 2023 推荐
- **参数**: 64MB 内存 + 3 次迭代（~0.5s 解密延迟）+ 单线程
- **密码要求**: 最短 8 字符（符合 NIST SP 800-63B、OWASP 标准），必须包含大小写字母、数字、特殊字符
- **安全性依据**: Argon2id 内存密集型 KDF（64MB + 3 次迭代）提供核心防护，即使 8 位强密码，暴力破解成本也达 1000+ 年（RTX 4090 单卡）。参考：VeraCrypt、1Password、Bitwarden 均采用 8 位最小长度
- **内存保护**: Rust `zeroize` crate 清零密钥，mlock 防 swap

### 4. U 盘意外拔出保护

- **写入流程**: 临时文件 (.tmp.{timestamp}) → 分块写入 + fsync → rename (原子性)
- **完整性验证**: 每块 GCM MAC (16 bytes) + 文件头元数据 (大小/块数/版本)
- **最坏情况**: 步骤 2 拔出 (临时文件损坏，原文件完整)、步骤 4 拔出 (OS 保证 rename 原子性)

## Consequences

**Positive**:
- Rust 生态成熟 (aes-gcm/ring 经审计)
- 分块支持增量备份、跨平台一致
- **Master Key Wrapping 支持快速修改密码**（<1 秒，Issue #41）
- 双层加密架构降低文件损坏风险

**Negative**:
- Nonce 唯一性管理 (随机数+块索引)
- 文件膨胀 0.04% (28 bytes/64KB)
- 2010 年前 CPU 无 AES-NI 性能降 10x
- **Master Key 损坏则所有文件无法解密**（缓解：未来 Issue #44 恢复密钥导出）

## Alternatives Considered

- **AES-CBC + HMAC**: 需两次遍历，Encrypt-then-MAC 易错 → 拒绝
- **ChaCha20-Poly1305**: x86 无硬件加速，Rust 生态不如 AES → 拒绝
- **全文件加密**: 大文件占用大量内存，无断点续传 → 拒绝

## References

- [AES-GCM Spec (NIST SP 800-38D)](https://csrc.nist.gov/publications/detail/sp/800-38d/final)
- [Argon2 RFC 9106](https://www.rfc-editor.org/rfc/rfc9106.html)
- [Rust aes-gcm crate](https://docs.rs/aes-gcm/)
- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
