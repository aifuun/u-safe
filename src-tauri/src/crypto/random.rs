//! 安全随机数生成
//!
//! 提供 Salt 和 Nonce 生成功能

use rand::{RngCore, rngs::OsRng};
use super::aes::NONCE_SIZE;

/// 生成 Salt（用于 Argon2id KDF）
///
/// # Returns
/// * 16 字节随机 salt
pub fn generate_salt() -> [u8; 16] {
    let mut salt = [0u8; 16];
    OsRng.fill_bytes(&mut salt);
    salt
}

/// 生成 Nonce（用于 AES-GCM）
///
/// # Returns
/// * 12 字节随机 nonce
///
/// # Note
/// 每个加密块必须使用不同的 nonce
pub fn generate_nonce() -> [u8; NONCE_SIZE] {
    let mut nonce = [0u8; NONCE_SIZE];
    OsRng.fill_bytes(&mut nonce);
    nonce
}

/// 生成带块索引的 Nonce（用于流式加密）
///
/// # Arguments
/// * `base_nonce` - 基础 nonce（随机生成）
/// * `chunk_index` - 块索引（从 0 开始）
///
/// # Returns
/// * 12 字节 nonce（base_nonce XOR chunk_index）
///
/// # Note
/// 这种方法确保每个块的 nonce 都不同，同时避免随机数重复
pub fn generate_nonce_for_chunk(base_nonce: &[u8; NONCE_SIZE], chunk_index: u64) -> [u8; NONCE_SIZE] {
    let mut nonce = *base_nonce;

    // 将 chunk_index 编码到 nonce 的最后 8 字节
    let index_bytes = chunk_index.to_le_bytes();
    for i in 0..8 {
        nonce[NONCE_SIZE - 8 + i] ^= index_bytes[i];
    }

    nonce
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_generate_salt() {
        let salt1 = generate_salt();
        let salt2 = generate_salt();

        // 长度正确
        assert_eq!(salt1.len(), 16);
        assert_eq!(salt2.len(), 16);

        // 两次生成的 salt 应该不同
        assert_ne!(salt1, salt2);
    }

    #[test]
    fn test_generate_nonce() {
        let nonce1 = generate_nonce();
        let nonce2 = generate_nonce();

        // 长度正确
        assert_eq!(nonce1.len(), NONCE_SIZE);
        assert_eq!(nonce2.len(), NONCE_SIZE);

        // 两次生成的 nonce 应该不同
        assert_ne!(nonce1, nonce2);
    }

    #[test]
    fn test_generate_nonce_for_chunk() {
        let base_nonce = generate_nonce();

        let nonce_0 = generate_nonce_for_chunk(&base_nonce, 0);
        let nonce_1 = generate_nonce_for_chunk(&base_nonce, 1);
        let nonce_2 = generate_nonce_for_chunk(&base_nonce, 2);

        // 不同块的 nonce 应该不同
        assert_ne!(nonce_0, nonce_1);
        assert_ne!(nonce_1, nonce_2);
        assert_ne!(nonce_0, nonce_2);
    }

    #[test]
    fn test_nonce_for_chunk_deterministic() {
        let base_nonce = generate_nonce();

        // 相同的 base_nonce 和 chunk_index 应该生成相同的 nonce
        let nonce_a = generate_nonce_for_chunk(&base_nonce, 42);
        let nonce_b = generate_nonce_for_chunk(&base_nonce, 42);

        assert_eq!(nonce_a, nonce_b);
    }

    #[test]
    fn test_salt_not_all_zeros() {
        let salt = generate_salt();

        // 随机 salt 不应该全是 0
        assert_ne!(salt, [0u8; 16]);
    }

    #[test]
    fn test_nonce_not_all_zeros() {
        let nonce = generate_nonce();

        // 随机 nonce 不应该全是 0
        assert_ne!(nonce, [0u8; NONCE_SIZE]);
    }
}
