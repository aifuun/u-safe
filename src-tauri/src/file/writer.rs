//! 加密文件写入
//!
//! 提供原子写入和加密元数据头

use std::fs::{self, File};
use std::io::{BufWriter, Write};
use std::path::{Path, PathBuf};
use super::super::crypto::error::CryptoError;

/// 加密文件写入器（原子写入）
pub struct EncryptedFileWriter {
    writer: BufWriter<File>,
    temp_path: PathBuf,
    final_path: PathBuf,
}

impl EncryptedFileWriter {
    /// 创建加密文件写入器
    ///
    /// # Arguments
    /// * `path` - 最终文件路径
    ///
    /// # Note
    /// 使用原子写入：先写入临时文件 (.enc.tmp)，完成后重命名
    pub fn create<P: AsRef<Path>>(path: P) -> Result<Self, CryptoError> {
        let final_path = path.as_ref().to_path_buf();

        // 临时文件路径
        let mut temp_path = final_path.clone();
        temp_path.set_extension("enc.tmp");

        // 确保目录存在
        if let Some(parent) = final_path.parent() {
            fs::create_dir_all(parent)?;
        }

        // 创建临时文件
        let file = File::create(&temp_path)?;
        let writer = BufWriter::new(file);

        log::info!("[file:writer] 创建加密文件写入器: {:?} -> {:?}",
            temp_path, final_path);

        Ok(EncryptedFileWriter {
            writer,
            temp_path,
            final_path,
        })
    }

    /// 完成写入（原子性重命名）
    pub fn finish(mut self) -> Result<(), CryptoError> {
        // 刷新缓冲区
        self.writer.flush()?;

        // 重命名（原子性操作）
        fs::rename(&self.temp_path, &self.final_path)?;

        log::info!("[file:writer] 原子写入完成: {:?}", self.final_path);

        Ok(())
    }
}

impl Write for EncryptedFileWriter {
    fn write(&mut self, buf: &[u8]) -> std::io::Result<usize> {
        self.writer.write(buf)
    }

    fn flush(&mut self) -> std::io::Result<()> {
        self.writer.flush()
    }
}

impl Drop for EncryptedFileWriter {
    fn drop(&mut self) {
        // 如果临时文件仍存在，删除（异常情况清理）
        if self.temp_path.exists() {
            let _ = fs::remove_file(&self.temp_path);
            log::warn!("[file:writer] 清理未完成的临时文件: {:?}", self.temp_path);
        }
    }
}
