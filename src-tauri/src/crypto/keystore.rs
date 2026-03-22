//! 主密钥存储
//!
//! 使用密码派生的密钥加密主密钥，存储到 .u-safe/keys/master.key

use std::fs;
use std::path::PathBuf;
use aes_gcm::{
    aead::{Aead, KeyInit, OsRng},
    Aes256Gcm, Nonce,
};
use rand::RngCore;
use super::key::SecretKey;
use super::error::CryptoError;

const NONCE_SIZE: usize = 12; // AES-GCM 标准 nonce 大小

/// 主密钥存储管理器
pub struct KeyStore;

impl KeyStore {
    /// 创建密钥存储管理器
    pub fn new() -> Self {
        KeyStore
    }

    /// 获取主密钥文件路径
    ///
    /// 使用统一的数据目录 (.u-safe/)
    fn get_master_key_path() -> PathBuf {
        let data_dir = crate::usb_detection::get_data_dir();
        let keys_dir = data_dir.join("keys");

        // 确保目录存在
        std::fs::create_dir_all(&keys_dir).ok();

        keys_dir.join("master.key")
    }

    /// 获取主密钥文件路径（实例方法，兼容现有接口）
    fn key_file_path(&self) -> PathBuf {
        Self::get_master_key_path()
    }

    /// 生成并存储新的主密钥
    ///
    /// # Arguments
    /// * `password_derived_key` - 从用户密码派生的密钥（32 字节）
    ///
    /// # Returns
    /// * `Ok(master_key)` - 生成的主密钥
    /// * `Err` - 生成或存储失败
    pub fn generate_and_store(&self, password_derived_key: &[u8; 32]) -> Result<SecretKey, CryptoError> {
        // 生成随机主密钥（32 字节）
        let mut master_key_bytes = [0u8; 32];
        OsRng.fill_bytes(&mut master_key_bytes);

        let master_key = SecretKey::new(master_key_bytes);

        // 存储加密后的主密钥
        self.store(&master_key, password_derived_key)?;

        log::info!("[keystore:generate] 主密钥已生成并存储");
        Ok(master_key)
    }

    /// 存储主密钥（加密）
    ///
    /// # Arguments
    /// * `master_key` - 要存储的主密钥
    /// * `password_derived_key` - 从用户密码派生的密钥（用于加密主密钥）
    pub fn store(&self, master_key: &SecretKey, password_derived_key: &[u8; 32]) -> Result<(), CryptoError> {
        // 使用 AES-256-GCM 加密主密钥
        let cipher = Aes256Gcm::new_from_slice(password_derived_key)
            .map_err(|e| CryptoError::KeystoreError(format!("创建 cipher 失败: {}", e)))?;

        // 生成随机 nonce
        let mut nonce_bytes = [0u8; NONCE_SIZE];
        OsRng.fill_bytes(&mut nonce_bytes);
        let nonce = Nonce::from_slice(&nonce_bytes);

        // 加密主密钥
        let ciphertext = cipher
            .encrypt(nonce, master_key.as_slice())
            .map_err(|e| CryptoError::EncryptionError(format!("加密主密钥失败: {}", e)))?;

        // 组合 nonce + ciphertext
        let mut data = Vec::with_capacity(NONCE_SIZE + ciphertext.len());
        data.extend_from_slice(&nonce_bytes);
        data.extend_from_slice(&ciphertext);

        // 确保目录存在
        let key_file = self.key_file_path();
        if let Some(parent) = key_file.parent() {
            fs::create_dir_all(parent)?;
        }

        // 写入文件
        fs::write(&key_file, data)?;

        log::info!("[keystore:store] 主密钥已加密存储: {:?}", key_file);
        Ok(())
    }

    /// 读取并解密主密钥
    ///
    /// # Arguments
    /// * `password_derived_key` - 从用户密码派生的密钥
    ///
    /// # Returns
    /// * `Ok(master_key)` - 解密后的主密钥
    /// * `Err` - 读取或解密失败
    pub fn load(&self, password_derived_key: &[u8; 32]) -> Result<SecretKey, CryptoError> {
        let key_file = self.key_file_path();

        // 读取文件
        let data = fs::read(&key_file)
            .map_err(|e| CryptoError::KeystoreError(format!("读取密钥文件失败: {}", e)))?;

        if data.len() < NONCE_SIZE {
            return Err(CryptoError::KeystoreError("密钥文件格式错误".to_string()));
        }

        // 分离 nonce 和 ciphertext
        let (nonce_bytes, ciphertext) = data.split_at(NONCE_SIZE);
        let nonce = Nonce::from_slice(nonce_bytes);

        // 创建 cipher
        let cipher = Aes256Gcm::new_from_slice(password_derived_key)
            .map_err(|e| CryptoError::KeystoreError(format!("创建 cipher 失败: {}", e)))?;

        // 解密主密钥
        let plaintext = cipher
            .decrypt(nonce, ciphertext)
            .map_err(|_| CryptoError::DecryptionError("解密主密钥失败（密码可能错误）".to_string()))?;

        if plaintext.len() != 32 {
            return Err(CryptoError::KeystoreError("主密钥长度错误".to_string()));
        }

        let mut key_bytes = [0u8; 32];
        key_bytes.copy_from_slice(&plaintext);

        log::info!("[keystore:load] 主密钥已解密加载");
        Ok(SecretKey::new(key_bytes))
    }

    /// 检查主密钥文件是否存在
    pub fn exists(&self) -> bool {
        self.key_file_path().exists()
    }

    /// 删除主密钥文件
    pub fn delete(&self) -> Result<(), CryptoError> {
        let key_file = self.key_file_path();
        if key_file.exists() {
            fs::remove_file(&key_file)?;
            log::info!("[keystore:delete] 主密钥文件已删除");
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn test_keystore() -> KeyStore {
        // 测试环境使用统一的数据目录
        KeyStore::new()
    }

    #[test]
    fn test_generate_and_load_master_key() {
        let keystore = test_keystore();
        let password_key = [42u8; 32];

        // 生成并存储主密钥
        let original_key = keystore.generate_and_store(&password_key).unwrap();

        // 加载主密钥
        let loaded_key = keystore.load(&password_key).unwrap();

        // 验证密钥相同
        assert_eq!(original_key.as_bytes(), loaded_key.as_bytes());

        // 清理
        keystore.delete().ok();
    }

    #[test]
    fn test_wrong_password_fails_to_decrypt() {
        let keystore = test_keystore();
        let correct_key = [42u8; 32];
        let wrong_key = [99u8; 32];

        // 使用正确密码生成
        keystore.generate_and_store(&correct_key).unwrap();

        // 使用错误密码加载应该失败
        let result = keystore.load(&wrong_key);
        assert!(result.is_err());

        // 清理
        keystore.delete().ok();
    }

    #[test]
    fn test_keystore_exists() {
        let keystore = test_keystore();
        let password_key = [42u8; 32];

        // 初始不存在
        assert!(!keystore.exists());

        // 生成后存在
        keystore.generate_and_store(&password_key).unwrap();
        assert!(keystore.exists());

        // 删除后不存在
        keystore.delete().unwrap();
        assert!(!keystore.exists());
    }
}
