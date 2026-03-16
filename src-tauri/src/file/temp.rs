//! 临时文件管理
//!
//! 提供自动清理的临时文件

use std::fs::{self, File};
use std::io::{Read, Write};
use std::path::PathBuf;
use super::super::crypto::error::CryptoError;

/// 自动清理的临时文件
pub struct TempFile {
    file: File,
    path: PathBuf,
}

impl TempFile {
    /// 创建临时文件
    ///
    /// # Note
    /// 临时文件在 Drop 时自动删除
    pub fn create() -> Result<Self, CryptoError> {
        // 使用系统临时目录
        let mut path = std::env::temp_dir();
        path.push(format!("u-safe-temp-{}", uuid::Uuid::new_v4()));

        let file = File::create(&path)?;

        log::info!("[file:temp] 创建临时文件: {:?}", path);

        Ok(TempFile { file, path })
    }

    /// 获取文件路径
    pub fn path(&self) -> &PathBuf {
        &self.path
    }
}

impl Read for TempFile {
    fn read(&mut self, buf: &mut [u8]) -> std::io::Result<usize> {
        self.file.read(buf)
    }
}

impl Write for TempFile {
    fn write(&mut self, buf: &[u8]) -> std::io::Result<usize> {
        self.file.write(buf)
    }

    fn flush(&mut self) -> std::io::Result<()> {
        self.file.flush()
    }
}

impl Drop for TempFile {
    fn drop(&mut self) {
        // 自动删除临时文件
        if self.path.exists() {
            let _ = fs::remove_file(&self.path);
            log::info!("[file:temp] 自动清理临时文件: {:?}", self.path);
        }
    }
}
