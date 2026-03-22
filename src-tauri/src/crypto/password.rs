//! 密码管理和验证
//!
//! 提供密码哈希存储、验证流程和错误次数限制

use std::sync::Mutex;
use std::time::{Duration, Instant};
use std::path::PathBuf;
use super::kdf::{derive_key, verify_password as verify_pwd};
use super::error::CryptoError;

/// 密码验证状态
struct PasswordState {
    /// 存储的密码哈希（PHC 格式）
    stored_hash: Option<String>,
    /// 错误尝试次数
    failed_attempts: u32,
    /// 锁定截止时间
    locked_until: Option<Instant>,
}

/// 密码管理器
///
/// 负责密码的设置、验证和错误次数限制
pub struct PasswordManager {
    state: Mutex<PasswordState>,
    max_attempts: u32,
    lockout_duration: Duration,
}

impl PasswordManager {
    /// 创建新的密码管理器
    ///
    /// # Arguments
    /// * `max_attempts` - 最大错误次数（默认 3）
    /// * `lockout_duration_secs` - 锁定时长（秒，默认 300 = 5 分钟）
    pub fn new(max_attempts: u32, lockout_duration_secs: u64) -> Self {
        PasswordManager {
            state: Mutex::new(PasswordState {
                stored_hash: None,
                failed_attempts: 0,
                locked_until: None,
            }),
            max_attempts,
            lockout_duration: Duration::from_secs(lockout_duration_secs),
        }
    }

    /// 使用默认配置创建
    pub fn default() -> Self {
        Self::new(3, 300) // 3 次错误，锁定 5 分钟
    }

    /// 从文件加载密码管理器
    ///
    /// 自动从 `.u-safe/keys/password.hash` 恢复密码哈希
    pub fn load() -> Result<Self, CryptoError> {
        let hash_file = Self::get_hash_file_path()?;
        let stored_hash = if hash_file.exists() {
            Some(std::fs::read_to_string(&hash_file)?)
        } else {
            None
        };

        log::info!("[password:load] 密码管理器已初始化, 密码已设置: {}", stored_hash.is_some());

        Ok(PasswordManager {
            state: Mutex::new(PasswordState {
                stored_hash,
                failed_attempts: 0,
                locked_until: None,
            }),
            max_attempts: 3,
            lockout_duration: Duration::from_secs(300),
        })
    }

    /// 获取密码哈希文件路径
    fn get_hash_file_path() -> Result<PathBuf, CryptoError> {
        // 使用统一的数据目录（.u-safe/）
        let data_dir = crate::usb_detection::get_data_dir();
        let keys_dir = data_dir.join("keys");

        std::fs::create_dir_all(&keys_dir)?;

        Ok(keys_dir.join("password.hash"))
    }

    /// 设置主密码
    ///
    /// # Arguments
    /// * `password` - 用户输入的密码
    ///
    /// # Returns
    /// * `Ok(())` - 设置成功
    /// * `Err` - 设置失败
    pub fn set_password(&self, password: &str) -> Result<(), CryptoError> {
        // 派生密钥并生成哈希
        let (_, hash) = derive_key(password)?;

        // 持久化到文件
        let hash_file = Self::get_hash_file_path()?;
        std::fs::write(&hash_file, &hash)?;

        // 存储哈希到内存
        let mut state = self.state.lock().unwrap();
        state.stored_hash = Some(hash);
        state.failed_attempts = 0;
        state.locked_until = None;

        log::info!("[password:set] 主密码已设置并持久化");
        Ok(())
    }

    /// 验证密码
    ///
    /// # Arguments
    /// * `password` - 用户输入的密码
    ///
    /// # Returns
    /// * `Ok(key)` - 验证成功，返回 32 字节密钥
    /// * `Err` - 验证失败（密码错误、账户锁定等）
    pub fn verify_password(&self, password: &str) -> Result<[u8; 32], CryptoError> {
        let mut state = self.state.lock().unwrap();

        // 检查是否被锁定
        if let Some(locked_until) = state.locked_until {
            if Instant::now() < locked_until {
                let remaining = locked_until.duration_since(Instant::now()).as_secs();
                return Err(CryptoError::InvalidPassword(
                    format!("账户已锁定，请 {} 秒后重试", remaining)
                ));
            } else {
                // 锁定时间已过，重置状态
                state.locked_until = None;
                state.failed_attempts = 0;
            }
        }

        // 检查是否已设置密码
        let stored_hash = state.stored_hash.as_ref()
            .ok_or_else(|| CryptoError::InvalidPassword("尚未设置主密码".to_string()))?;

        // 验证密码
        match verify_pwd(password, stored_hash) {
            Ok(key) => {
                // 验证成功，重置错误次数
                state.failed_attempts = 0;
                log::info!("[password:verify] 密码验证成功");
                Ok(key)
            }
            Err(_) => {
                // 验证失败，增加错误次数
                state.failed_attempts += 1;
                log::warn!("[password:verify] 密码验证失败 ({}/{})",
                    state.failed_attempts, self.max_attempts);

                // 检查是否需要锁定
                if state.failed_attempts >= self.max_attempts {
                    state.locked_until = Some(Instant::now() + self.lockout_duration);
                    let lockout_secs = self.lockout_duration.as_secs();
                    log::warn!("[password:verify] 账户已锁定 {} 秒", lockout_secs);
                    return Err(CryptoError::InvalidPassword(
                        format!("密码错误次数过多，账户已锁定 {} 秒", lockout_secs)
                    ));
                }

                Err(CryptoError::InvalidPassword(
                    format!("密码错误 ({}/{})", state.failed_attempts, self.max_attempts)
                ))
            }
        }
    }

    /// 检查是否已设置密码
    pub fn is_password_set(&self) -> bool {
        let state = self.state.lock().unwrap();
        state.stored_hash.is_some()
    }

    /// 获取剩余尝试次数
    pub fn remaining_attempts(&self) -> u32 {
        let state = self.state.lock().unwrap();
        if state.failed_attempts >= self.max_attempts {
            0
        } else {
            self.max_attempts - state.failed_attempts
        }
    }

    /// 检查是否被锁定
    pub fn is_locked(&self) -> bool {
        let state = self.state.lock().unwrap();
        if let Some(locked_until) = state.locked_until {
            Instant::now() < locked_until
        } else {
            false
        }
    }

    /// 重置错误次数（管理员功能）
    pub fn reset_attempts(&self) {
        let mut state = self.state.lock().unwrap();
        state.failed_attempts = 0;
        state.locked_until = None;
        log::info!("[password:reset] 错误次数已重置");
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_set_and_verify_password() {
        let manager = PasswordManager::default();

        // 设置密码
        manager.set_password("MySecurePass123").unwrap();
        assert!(manager.is_password_set());

        // 验证正确密码
        let key = manager.verify_password("MySecurePass123").unwrap();
        assert_eq!(key.len(), 32);
    }

    #[test]
    fn test_wrong_password() {
        let manager = PasswordManager::default();
        manager.set_password("correct").unwrap();

        // 错误密码应该验证失败
        let result = manager.verify_password("wrong");
        assert!(result.is_err());
    }

    #[test]
    fn test_lockout_after_max_attempts() {
        let manager = PasswordManager::new(3, 300);
        manager.set_password("correct").unwrap();

        // 尝试 3 次错误密码
        for i in 1..=3 {
            let result = manager.verify_password("wrong");
            assert!(result.is_err());
            if i < 3 {
                assert_eq!(manager.remaining_attempts(), 3 - i);
            }
        }

        // 第 3 次后应该被锁定
        assert!(manager.is_locked());
        assert_eq!(manager.remaining_attempts(), 0);

        // 即使输入正确密码也应该被拒绝
        let result = manager.verify_password("correct");
        assert!(result.is_err());
    }

    #[test]
    fn test_reset_attempts() {
        let manager = PasswordManager::default();
        manager.set_password("correct").unwrap();

        // 错误一次
        let _ = manager.verify_password("wrong");
        assert_eq!(manager.remaining_attempts(), 2);

        // 重置
        manager.reset_attempts();
        assert_eq!(manager.remaining_attempts(), 3);
        assert!(!manager.is_locked());
    }

    #[test]
    fn test_successful_login_resets_attempts() {
        let manager = PasswordManager::default();
        manager.set_password("correct").unwrap();

        // 错误一次
        let _ = manager.verify_password("wrong");
        assert_eq!(manager.remaining_attempts(), 2);

        // 正确登录应该重置错误次数
        let _ = manager.verify_password("correct").unwrap();
        assert_eq!(manager.remaining_attempts(), 3);
    }
}
