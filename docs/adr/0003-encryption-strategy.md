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

U-Safe 需要在 U 盘上加密存储财务数据，面临特殊挑战：
- **意外断电/拔出**: U 盘可能在写入时被拔出，需保证数据不损坏
- **大量历史记录**: 用户可能有数千条交易记录，需快速加密/解密
- **低配置设备**: 需要在 8GB RAM 的设备上流畅运行
- **篡改检测**: 必须能检测数据是否被恶意修改（完整性）

传统加密方案的问题：
- **AES-CBC**: 无认证，无法检测篡改，需额外 HMAC（复杂且易错）
- **全文件加密**: 大文件会占用大量内存（1GB 文件需 1GB+ RAM）
- **简单 KDF**: 如 PBKDF2 易受 GPU 暴力破解

## Decision Details

### 1. 为什么选择 AES-256-GCM（而非 AES-CBC 或 ChaCha20）

**AES-GCM 优势**:
- **AEAD**: Authenticated Encryption with Associated Data，一次操作完成加密+认证
- **硬件加速**: Intel/AMD CPU 自 2010 年起支持 AES-NI 指令集（~10x 性能提升）
- **并行化**: GCM 模式可并行加密，CBC 必须串行

**vs AES-CBC**:
- CBC 需额外 HMAC 保证完整性（Encrypt-then-MAC 模式，易出错）
- CBC 填充攻击风险（Padding Oracle Attack）

**vs ChaCha20-Poly1305**:
- ChaCha20 无硬件加速（ARM 平台优势，x86 劣势）
- U-Safe 目标平台（Windows/Mac/Linux x86）均有 AES-NI

**性能对比**（Intel Core i5, 100MB 文件）:
- AES-256-GCM (AES-NI): ~50 ms
- AES-256-CBC + HMAC: ~120 ms
- ChaCha20-Poly1305: ~80 ms

### 2. 为什么采用 64KB 分块流式加密

**分块策略**:
- 每个文件分割为 64KB 块，独立加密
- 每块有独立 nonce（12 bytes），防重放攻击
- 每块有独立 MAC（16 bytes），可单独验证完整性

**64KB 的理由**:
- **内存友好**: 加密/解密单块仅需 ~64KB 内存（vs 全文件加密需文件大小内存）
- **性能平衡**: 太小（如 4KB）则 MAC 开销大，太大（如 1MB）则内存占用高
- **断点续传**: 未来可实现按块解密（只解密需要的块）

**原子写入**:
- 先写临时文件（.tmp）
- 完成后原子重命名（atomic rename）
- U 盘拔出时，要么有完整文件，要么无新文件（不会有半成品）

### 3. 密钥管理策略

**Argon2id 选择**:
- **内存硬度**: 需要大量内存计算，抵抗 GPU/ASIC 暴力破解
- **侧信道防护**: Argon2id 混合 Argon2i（防时间侧信道）和 Argon2d（防 trade-off 攻击）
- **OWASP 推荐**: 2023 年密码哈希竞赛冠军，行业标准

**参数选择**:
- Memory: 64 MB（在低配设备可接受）
- Iterations: 3（平衡安全性和用户体验，~0.5s 解密延迟）
- Parallelism: 1（单线程，避免复杂度）

**密码强度要求**:
- 最短 12 字符（强制）
- 包含大小写、数字、符号（建议）
- 使用 zxcvbn 库评估强度

**内存保护**:
- 使用 Rust `zeroize` crate，密钥使用后立即清零
- 避免密钥被 swap 到磁盘（mlock）

### 4. U 盘意外拔出的数据完整性

**写入流程**:
1. 生成临时文件名（原文件名 + `.tmp.{timestamp}`）
2. 加密并写入临时文件（分块写入，每块 fsync）
3. 关闭文件句柄
4. 原子重命名：`rename(temp, target)`（操作系统保证原子性）

**完整性验证**:
- 每块有 GCM MAC（16 bytes），读取时验证
- 整个文件有元数据（文件大小、块数、版本），存储在文件头
- 启动时扫描，发现损坏文件标记为 corrupted

**最坏情况**:
- U 盘在步骤 2 拔出：临时文件不完整，原文件未受影响
- U 盘在步骤 4 拔出：操作系统保证 rename 原子性，要么成功要么失败

## Consequences

### Positive (TL;DR 中未详述的优势)
- **Rust 生态成熟**: `aes-gcm` crate 经过审计，`ring` 库基于 BoringSSL
- **未来扩展**: 分块设计支持增量备份、差异同步
- **跨平台一致**: AES-GCM 在所有平台行为一致（vs 文件系统差异）

### Negative (TL;DR 中未详述的挑战)
- **Nonce 管理**: 必须确保每块 nonce 唯一（使用随机数 + 块索引）
- **文件膨胀**: 每 64KB 块增加 28 bytes（12 nonce + 16 MAC），约 0.04% 开销
- **老旧设备**: 2010 年前 CPU 无 AES-NI，性能降至软件实现（~10x 慢）

## Alternatives Considered

### Alternative 1: AES-256-CBC + HMAC-SHA256
**不选原因**: 实现复杂（需正确实现 Encrypt-then-MAC），性能不如 GCM（需两次遍历），无硬件加速 HMAC

### Alternative 2: ChaCha20-Poly1305
**不选原因**: 无硬件加速（x86 平台），性能劣于 AES-GCM，Rust 生态不如 AES 成熟

### Alternative 3: 全文件加密（无分块）
**不选原因**: 大文件（1GB+）占用大量内存，无法实现断点续传，意外中断时整个文件损坏

## References

- [AES-GCM Spec (NIST SP 800-38D)](https://csrc.nist.gov/publications/detail/sp/800-38d/final)
- [Argon2 RFC 9106](https://www.rfc-editor.org/rfc/rfc9106.html)
- [Rust aes-gcm crate](https://docs.rs/aes-gcm/)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
