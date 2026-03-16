//! 加密错误类型定义

use std::fmt;

#[derive(Debug)]
pub enum CryptoError {
    /// KDF (密钥派生) 错误
    KdfError(String),

    /// 密码无效
    InvalidPassword(String),

    /// 加密失败
    EncryptionError(String),

    /// 解密失败
    DecryptionError(String),

    /// MAC 验证失败
    MacVerificationFailed,

    /// 密钥存储错误
    KeystoreError(String),

    /// 文件 I/O 错误
    IoError(std::io::Error),

    /// 其他错误
    Other(String),
}

impl fmt::Display for CryptoError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            CryptoError::KdfError(msg) => write!(f, "KDF 错误: {}", msg),
            CryptoError::InvalidPassword(msg) => write!(f, "密码无效: {}", msg),
            CryptoError::EncryptionError(msg) => write!(f, "加密失败: {}", msg),
            CryptoError::DecryptionError(msg) => write!(f, "解密失败: {}", msg),
            CryptoError::MacVerificationFailed => write!(f, "MAC 验证失败"),
            CryptoError::KeystoreError(msg) => write!(f, "密钥存储错误: {}", msg),
            CryptoError::IoError(err) => write!(f, "I/O 错误: {}", err),
            CryptoError::Other(msg) => write!(f, "错误: {}", msg),
        }
    }
}

impl std::error::Error for CryptoError {}

impl From<std::io::Error> for CryptoError {
    fn from(err: std::io::Error) -> Self {
        CryptoError::IoError(err)
    }
}
