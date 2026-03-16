//! Argon2id 密钥派生函数 (KDF)
//!
//! 使用 Argon2id 从用户密码派生 32 字节主密钥
//! 参数配置符合 ADR-004 和 OWASP 2023 推荐

use argon2::{
    password_hash::{PasswordHash, PasswordHasher, PasswordVerifier, SaltString},
    Argon2, Algorithm, Params, Version,
};
use rand::rngs::OsRng;

use super::error::CryptoError;

/// Argon2id 参数配置
/// - 内存: 64 MB (65536 KB)
/// - 迭代次数: 3
/// - 并行度: 1
const MEMORY_SIZE_KB: u32 = 64 * 1024; // 64 MB
const ITERATIONS: u32 = 3;
const PARALLELISM: u32 = 1;
const OUTPUT_LEN: usize = 32; // 256 bits

/// 从密码派生密钥
///
/// # Arguments
/// * `password` - 用户密码（明文）
///
/// # Returns
/// * `Ok((key, salt))` - 32 字节密钥和盐值的 PHC 字符串
/// * `Err` - 派生失败
///
/// # Example
/// ```rust
/// let (key, salt) = derive_key("my_secure_password")?;
/// ```
pub fn derive_key(password: &str) -> Result<([u8; OUTPUT_LEN], String), CryptoError> {
    // 生成随机盐 (16 字节)
    let salt = SaltString::generate(&mut OsRng);

    // 配置 Argon2id 参数
    let params = Params::new(
        MEMORY_SIZE_KB,
        ITERATIONS,
        PARALLELISM,
        Some(OUTPUT_LEN)
    ).map_err(|e| CryptoError::KdfError(format!("参数配置失败: {}", e)))?;

    let argon2 = Argon2::new(
        Algorithm::Argon2id,
        Version::V0x13,
        params,
    );

    // 派生密钥
    let password_hash = argon2
        .hash_password(password.as_bytes(), &salt)
        .map_err(|e| CryptoError::KdfError(format!("密钥派生失败: {}", e)))?;

    // 提取 32 字节密钥
    let hash_output = password_hash.hash
        .ok_or_else(|| CryptoError::KdfError("缺少哈希输出".to_string()))?;

    let mut key = [0u8; OUTPUT_LEN];
    key.copy_from_slice(&hash_output.as_bytes()[..OUTPUT_LEN]);

    // 返回密钥和 PHC 格式的盐值字符串（用于后续验证）
    Ok((key, password_hash.to_string()))
}

/// 验证密码是否正确
///
/// # Arguments
/// * `password` - 用户输入的密码
/// * `stored_hash` - 存储的 PHC 格式哈希字符串
///
/// # Returns
/// * `Ok(key)` - 验证成功，返回派生的 32 字节密钥
/// * `Err` - 验证失败（密码错误或格式错误）
///
/// # Example
/// ```rust
/// let key = verify_password("my_secure_password", &stored_hash)?;
/// ```
pub fn verify_password(password: &str, stored_hash: &str) -> Result<[u8; OUTPUT_LEN], CryptoError> {
    // 解析存储的哈希
    let parsed_hash = PasswordHash::new(stored_hash)
        .map_err(|e| CryptoError::InvalidPassword(format!("哈希格式错误: {}", e)))?;

    // 重新配置 Argon2id
    let params = Params::new(
        MEMORY_SIZE_KB,
        ITERATIONS,
        PARALLELISM,
        Some(OUTPUT_LEN)
    ).map_err(|e| CryptoError::KdfError(format!("参数配置失败: {}", e)))?;

    let argon2 = Argon2::new(
        Algorithm::Argon2id,
        Version::V0x13,
        params,
    );

    // 验证密码
    argon2
        .verify_password(password.as_bytes(), &parsed_hash)
        .map_err(|_| CryptoError::InvalidPassword("密码错误".to_string()))?;

    // 重新派生密钥
    let salt = parsed_hash.salt
        .ok_or_else(|| CryptoError::KdfError("缺少盐值".to_string()))?;

    let password_hash = argon2
        .hash_password(password.as_bytes(), salt)
        .map_err(|e| CryptoError::KdfError(format!("密钥派生失败: {}", e)))?;

    // 提取密钥
    let hash_output = password_hash.hash
        .ok_or_else(|| CryptoError::KdfError("缺少哈希输出".to_string()))?;

    let mut key = [0u8; OUTPUT_LEN];
    key.copy_from_slice(&hash_output.as_bytes()[..OUTPUT_LEN]);

    Ok(key)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_derive_key_generates_different_salts() {
        let password = "test_password";

        let (key1, salt1) = derive_key(password).unwrap();
        let (key2, salt2) = derive_key(password).unwrap();

        // 相同密码，不同盐值，应该生成不同密钥
        assert_ne!(salt1, salt2);
        assert_ne!(key1, key2);
    }

    #[test]
    fn test_verify_password_success() {
        let password = "my_secure_password";

        // 派生密钥
        let (original_key, stored_hash) = derive_key(password).unwrap();

        // 验证密码并重新派生密钥
        let verified_key = verify_password(password, &stored_hash).unwrap();

        // 验证密钥应该相同
        assert_eq!(original_key, verified_key);
    }

    #[test]
    fn test_verify_password_wrong_password() {
        let correct_password = "correct_password";
        let wrong_password = "wrong_password";

        // 派生密钥
        let (_, stored_hash) = derive_key(correct_password).unwrap();

        // 错误密码应该验证失败
        let result = verify_password(wrong_password, &stored_hash);
        assert!(result.is_err());
    }

    #[test]
    fn test_output_key_length() {
        let password = "test";
        let (key, _) = derive_key(password).unwrap();

        // 密钥长度应该是 32 字节
        assert_eq!(key.len(), OUTPUT_LEN);
    }
}
