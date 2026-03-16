//! 文件读取
//!
//! 提供流式文件读取功能

use std::fs::File;
use std::io::{BufReader, Read};
use std::path::Path;
use super::super::crypto::error::CryptoError;

/// 文件读取器（带缓冲）
pub struct FileReader {
    reader: BufReader<File>,
    file_size: u64,
}

impl FileReader {
    /// 打开文件进行读取
    ///
    /// # Arguments
    /// * `path` - 文件路径
    ///
    /// # Returns
    /// * `Ok(FileReader)` - 文件读取器
    /// * `Err` - 打开失败
    pub fn open<P: AsRef<Path>>(path: P) -> Result<Self, CryptoError> {
        let file = File::open(&path)?;
        let metadata = file.metadata()?;
        let file_size = metadata.len();

        let reader = BufReader::new(file);

        log::info!("[file:reader] 打开文件: {:?}, 大小: {} 字节",
            path.as_ref(), file_size);

        Ok(FileReader { reader, file_size })
    }

    /// 获取文件大小
    pub fn size(&self) -> u64 {
        self.file_size
    }
}

impl Read for FileReader {
    fn read(&mut self, buf: &mut [u8]) -> std::io::Result<usize> {
        self.reader.read(buf)
    }
}
