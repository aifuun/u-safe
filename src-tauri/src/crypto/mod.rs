//! 加密模块
//!
//! 提供以下功能：
//! - KDF (密钥派生): Argon2id
//! - 加密/解密: AES-256-GCM
//! - 密钥管理: 主密钥存储和验证
//! - 内存安全: zeroize 清零

pub mod kdf;
pub mod key;
pub mod password;
pub mod keystore;
pub mod aes;
pub mod stream;
pub mod random;
pub mod error;

pub use kdf::{derive_key, verify_password};
pub use key::SecretKey;
pub use error::CryptoError;
