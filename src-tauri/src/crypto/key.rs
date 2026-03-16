//! 密钥类型和内存安全
//!
//! 使用 zeroize 确保密钥在不再使用时清零内存

use zeroize::{Zeroize, ZeroizeOnDrop};

/// 256-bit (32 字节) 主密钥
///
/// 自动在 Drop 时清零内存，防止密钥泄漏
#[derive(Zeroize, ZeroizeOnDrop)]
pub struct SecretKey {
    bytes: [u8; 32],
}

impl SecretKey {
    /// 从字节数组创建密钥
    pub fn new(bytes: [u8; 32]) -> Self {
        SecretKey { bytes }
    }

    /// 获取密钥字节（不可变引用）
    pub fn as_bytes(&self) -> &[u8; 32] {
        &self.bytes
    }

    /// 获取密钥字节切片
    pub fn as_slice(&self) -> &[u8] {
        &self.bytes
    }

    /// 从切片复制创建密钥
    pub fn from_slice(slice: &[u8]) -> Result<Self, &'static str> {
        if slice.len() != 32 {
            return Err("密钥长度必须是 32 字节");
        }

        let mut bytes = [0u8; 32];
        bytes.copy_from_slice(slice);
        Ok(SecretKey { bytes })
    }
}

// Drop trait 由 ZeroizeOnDrop 自动实现
// 密钥在离开作用域时会自动清零内存

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_secret_key_creation() {
        let bytes = [0u8; 32];
        let key = SecretKey::new(bytes);
        assert_eq!(key.as_bytes(), &bytes);
    }

    #[test]
    fn test_secret_key_from_slice() {
        let slice = &[1u8; 32];
        let key = SecretKey::from_slice(slice).unwrap();
        assert_eq!(key.as_bytes(), slice);
    }

    #[test]
    fn test_secret_key_wrong_length() {
        let slice = &[1u8; 16]; // 错误长度
        let result = SecretKey::from_slice(slice);
        assert!(result.is_err());
    }

    #[test]
    fn test_secret_key_zeroize_on_drop() {
        // 这个测试验证密钥可以被正常 drop
        // 实际的内存清零由 ZeroizeOnDrop derive 自动保证
        {
            let key = SecretKey::new([42u8; 32]);
            // key 离开作用域时会自动清零
        }
        // 密钥已被清零（由 ZeroizeOnDrop 保证）
    }
}
