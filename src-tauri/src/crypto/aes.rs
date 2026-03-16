//! AES-256-GCM 加密/解密
//!
//! 提供单块加密、解密和 MAC 验证功能

use aes_gcm::{
    aead::{Aead, KeyInit},
    Aes256Gcm, Nonce,
};
use super::error::CryptoError;

/// 块大小：64KB
pub const CHUNK_SIZE: usize = 64 * 1024;

/// Nonce 大小：12 字节（AES-GCM 标准）
pub const NONCE_SIZE: usize = 12;

/// 加密单个数据块
///
/// # Arguments
/// * `key` - 32 字节密钥
/// * `nonce` - 12 字节 nonce（每块必须唯一）
/// * `plaintext` - 明文数据
///
/// # Returns
/// * `Ok(ciphertext)` - 加密后的数据（包含 MAC tag）
/// * `Err` - 加密失败
///
/// # Note
/// 返回的 ciphertext 长度 = plaintext.len() + 16 (MAC tag)
pub fn encrypt_chunk(
    key: &[u8; 32],
    nonce: &[u8; NONCE_SIZE],
    plaintext: &[u8],
) -> Result<Vec<u8>, CryptoError> {
    // 创建 cipher
    let cipher = Aes256Gcm::new_from_slice(key)
        .map_err(|e| CryptoError::EncryptionError(format!("创建 cipher 失败: {}", e)))?;

    let nonce = Nonce::from_slice(nonce);

    // 加密数据
    cipher
        .encrypt(nonce, plaintext)
        .map_err(|e| CryptoError::EncryptionError(format!("加密失败: {}", e)))
}

/// 解密单个数据块
///
/// # Arguments
/// * `key` - 32 字节密钥
/// * `nonce` - 12 字节 nonce（必须与加密时相同）
/// * `ciphertext` - 密文数据（包含 MAC tag）
///
/// # Returns
/// * `Ok(plaintext)` - 解密后的明文
/// * `Err` - 解密失败（MAC 验证失败或数据损坏）
///
/// # Note
/// 如果 MAC 验证失败，说明数据被篡改或密钥错误
pub fn decrypt_chunk(
    key: &[u8; 32],
    nonce: &[u8; NONCE_SIZE],
    ciphertext: &[u8],
) -> Result<Vec<u8>, CryptoError> {
    // 创建 cipher
    let cipher = Aes256Gcm::new_from_slice(key)
        .map_err(|e| CryptoError::DecryptionError(format!("创建 cipher 失败: {}", e)))?;

    let nonce = Nonce::from_slice(nonce);

    // 解密并验证 MAC
    cipher
        .decrypt(nonce, ciphertext)
        .map_err(|_| CryptoError::MacVerificationFailed) // MAC 验证失败
}

/// 验证 MAC（通过尝试解密）
///
/// # Arguments
/// * `key` - 32 字节密钥
/// * `nonce` - 12 字节 nonce
/// * `ciphertext` - 密文数据（包含 MAC tag）
///
/// # Returns
/// * `Ok(())` - MAC 有效
/// * `Err` - MAC 无效（数据被篡改）
pub fn verify_mac(
    key: &[u8; 32],
    nonce: &[u8; NONCE_SIZE],
    ciphertext: &[u8],
) -> Result<(), CryptoError> {
    // AES-GCM 的 MAC 验证通过解密完成
    // 如果解密成功，MAC 就是有效的
    decrypt_chunk(key, nonce, ciphertext)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_encrypt_decrypt_roundtrip() {
        let key = [42u8; 32];
        let nonce = [1u8; NONCE_SIZE];
        let plaintext = b"Hello, AES-256-GCM!";

        // 加密
        let ciphertext = encrypt_chunk(&key, &nonce, plaintext).unwrap();

        // 密文长度应该是明文 + 16 (MAC tag)
        assert_eq!(ciphertext.len(), plaintext.len() + 16);

        // 解密
        let decrypted = decrypt_chunk(&key, &nonce, &ciphertext).unwrap();

        // 验证往返一致
        assert_eq!(decrypted, plaintext);
    }

    #[test]
    fn test_wrong_key_fails_to_decrypt() {
        let correct_key = [42u8; 32];
        let wrong_key = [99u8; 32];
        let nonce = [1u8; NONCE_SIZE];
        let plaintext = b"Secret message";

        // 使用正确密钥加密
        let ciphertext = encrypt_chunk(&correct_key, &nonce, plaintext).unwrap();

        // 使用错误密钥解密应该失败（MAC 验证失败）
        let result = decrypt_chunk(&wrong_key, &nonce, &ciphertext);
        assert!(matches!(result, Err(CryptoError::MacVerificationFailed)));
    }

    #[test]
    fn test_wrong_nonce_fails_to_decrypt() {
        let key = [42u8; 32];
        let correct_nonce = [1u8; NONCE_SIZE];
        let wrong_nonce = [2u8; NONCE_SIZE];
        let plaintext = b"Test data";

        // 使用 nonce1 加密
        let ciphertext = encrypt_chunk(&key, &correct_nonce, plaintext).unwrap();

        // 使用 nonce2 解密应该失败
        let result = decrypt_chunk(&key, &wrong_nonce, &ciphertext);
        assert!(matches!(result, Err(CryptoError::MacVerificationFailed)));
    }

    #[test]
    fn test_tampered_ciphertext_fails_mac() {
        let key = [42u8; 32];
        let nonce = [1u8; NONCE_SIZE];
        let plaintext = b"Important data";

        // 加密
        let mut ciphertext = encrypt_chunk(&key, &nonce, plaintext).unwrap();

        // 篡改密文
        ciphertext[0] ^= 0xFF;

        // 解密应该失败（MAC 验证失败）
        let result = decrypt_chunk(&key, &nonce, &ciphertext);
        assert!(matches!(result, Err(CryptoError::MacVerificationFailed)));
    }

    #[test]
    fn test_verify_mac_success() {
        let key = [42u8; 32];
        let nonce = [1u8; NONCE_SIZE];
        let plaintext = b"Data with valid MAC";

        let ciphertext = encrypt_chunk(&key, &nonce, plaintext).unwrap();

        // MAC 验证应该成功
        assert!(verify_mac(&key, &nonce, &ciphertext).is_ok());
    }

    #[test]
    fn test_verify_mac_failure() {
        let key = [42u8; 32];
        let nonce = [1u8; NONCE_SIZE];
        let plaintext = b"Data";

        let mut ciphertext = encrypt_chunk(&key, &nonce, plaintext).unwrap();

        // 篡改数据
        ciphertext[5] ^= 0xFF;

        // MAC 验证应该失败
        assert!(verify_mac(&key, &nonce, &ciphertext).is_err());
    }

    #[test]
    fn test_encrypt_large_chunk() {
        let key = [42u8; 32];
        let nonce = [1u8; NONCE_SIZE];
        let plaintext = vec![0xAB; CHUNK_SIZE]; // 64KB 数据

        // 加密 64KB 数据
        let ciphertext = encrypt_chunk(&key, &nonce, &plaintext).unwrap();
        assert_eq!(ciphertext.len(), CHUNK_SIZE + 16);

        // 解密
        let decrypted = decrypt_chunk(&key, &nonce, &ciphertext).unwrap();
        assert_eq!(decrypted, plaintext);
    }
}
