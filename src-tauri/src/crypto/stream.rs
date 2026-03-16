//! 64KB 分块流式加密
//!
//! 提供文件流式读取、分块加密和进度跟踪

use std::io::{Read, Write};
use super::aes::{encrypt_chunk, decrypt_chunk, CHUNK_SIZE, NONCE_SIZE};
use super::random::{generate_nonce, generate_nonce_for_chunk};
use super::error::CryptoError;

/// 加密进度回调
pub type ProgressCallback = dyn Fn(u64, u64) + Send + Sync;

/// 流式加密文件
///
/// # Arguments
/// * `reader` - 输入数据源（实现 Read trait）
/// * `writer` - 输出目标（实现 Write trait）
/// * `key` - 32 字节密钥
/// * `total_size` - 总文件大小（用于进度跟踪）
/// * `progress_callback` - 可选的进度回调函数
///
/// # Returns
/// * `Ok(())` - 加密成功
/// * `Err` - 加密失败
///
/// # 文件格式
/// ```
/// [base_nonce: 12 字节]
/// [chunk_0: 加密数据 + MAC]
/// [chunk_1: 加密数据 + MAC]
/// ...
/// ```
pub fn encrypt_stream<R: Read, W: Write>(
    mut reader: R,
    mut writer: W,
    key: &[u8; 32],
    total_size: u64,
    progress_callback: Option<&ProgressCallback>,
) -> Result<(), CryptoError> {
    // 生成基础 nonce
    let base_nonce = generate_nonce();

    // 写入 nonce 到输出（用于解密）
    writer.write_all(&base_nonce)?;

    let mut buffer = vec![0u8; CHUNK_SIZE];
    let mut bytes_processed: u64 = 0;
    let mut chunk_index: u64 = 0;

    loop {
        // 读取一块数据
        let bytes_read = reader.read(&mut buffer)?;

        if bytes_read == 0 {
            break; // EOF
        }

        // 生成当前块的 nonce
        let chunk_nonce = generate_nonce_for_chunk(&base_nonce, chunk_index);

        // 加密当前块
        let ciphertext = encrypt_chunk(key, &chunk_nonce, &buffer[..bytes_read])?;

        // 写入密文
        writer.write_all(&ciphertext)?;

        // 更新进度
        bytes_processed += bytes_read as u64;
        chunk_index += 1;

        // 调用进度回调
        if let Some(callback) = progress_callback {
            callback(bytes_processed, total_size);
        }
    }

    writer.flush()?;

    log::info!("[stream:encrypt] 流式加密完成: {} 字节, {} 块",
        bytes_processed, chunk_index);

    Ok(())
}

/// 流式解密文件
///
/// # Arguments
/// * `reader` - 输入数据源（加密文件）
/// * `writer` - 输出目标（明文文件）
/// * `key` - 32 字节密钥
/// * `total_size` - 加密文件总大小（用于进度跟踪）
/// * `progress_callback` - 可选的进度回调函数
///
/// # Returns
/// * `Ok(())` - 解密成功
/// * `Err` - 解密失败（MAC 验证失败或数据损坏）
pub fn decrypt_stream<R: Read, W: Write>(
    mut reader: R,
    mut writer: W,
    key: &[u8; 32],
    total_size: u64,
    progress_callback: Option<&ProgressCallback>,
) -> Result<(), CryptoError> {
    // 读取基础 nonce
    let mut base_nonce = [0u8; NONCE_SIZE];
    reader.read_exact(&mut base_nonce)?;

    // 每个加密块的大小（明文 CHUNK_SIZE + MAC 16 字节）
    let encrypted_chunk_size = CHUNK_SIZE + 16;
    let mut buffer = vec![0u8; encrypted_chunk_size];

    let mut bytes_processed: u64 = NONCE_SIZE as u64;
    let mut chunk_index: u64 = 0;

    loop {
        // 读取一块加密数据
        let bytes_read = match reader.read(&mut buffer) {
            Ok(0) => break, // EOF
            Ok(n) => n,
            Err(e) if e.kind() == std::io::ErrorKind::UnexpectedEof => break,
            Err(e) => return Err(CryptoError::IoError(e)),
        };

        // 生成当前块的 nonce
        let chunk_nonce = generate_nonce_for_chunk(&base_nonce, chunk_index);

        // 解密当前块
        let plaintext = decrypt_chunk(key, &chunk_nonce, &buffer[..bytes_read])?;

        // 写入明文
        writer.write_all(&plaintext)?;

        // 更新进度
        bytes_processed += bytes_read as u64;
        chunk_index += 1;

        // 调用进度回调
        if let Some(callback) = progress_callback {
            callback(bytes_processed, total_size);
        }
    }

    writer.flush()?;

    log::info!("[stream:decrypt] 流式解密完成: {} 块", chunk_index);

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Cursor;

    #[test]
    fn test_encrypt_decrypt_stream_small_file() {
        let key = [42u8; 32];
        let plaintext = b"Hello, streaming encryption!";

        // 加密
        let mut encrypted = Vec::new();
        let reader = Cursor::new(plaintext);
        encrypt_stream(reader, &mut encrypted, &key, plaintext.len() as u64, None).unwrap();

        // 解密
        let mut decrypted = Vec::new();
        let reader = Cursor::new(&encrypted);
        decrypt_stream(reader, &mut decrypted, &key, encrypted.len() as u64, None).unwrap();

        // 验证往返一致
        assert_eq!(decrypted, plaintext);
    }

    #[test]
    fn test_encrypt_decrypt_stream_large_file() {
        let key = [42u8; 32];
        // 200KB 数据（超过 3 个 chunk）
        let plaintext = vec![0xAB; 200 * 1024];

        // 加密
        let mut encrypted = Vec::new();
        let reader = Cursor::new(&plaintext);
        encrypt_stream(reader, &mut encrypted, &key, plaintext.len() as u64, None).unwrap();

        // 加密后大小应该略大于原始大小（nonce + MAC tags）
        assert!(encrypted.len() > plaintext.len());

        // 解密
        let mut decrypted = Vec::new();
        let reader = Cursor::new(&encrypted);
        decrypt_stream(reader, &mut decrypted, &key, encrypted.len() as u64, None).unwrap();

        // 验证往返一致
        assert_eq!(decrypted, plaintext);
    }

    #[test]
    fn test_stream_progress_callback() {
        use std::sync::{Arc, Mutex};

        let key = [42u8; 32];
        let plaintext = vec![0u8; 128 * 1024]; // 128KB (2 chunks)

        let progress_calls = Arc::new(Mutex::new(0));
        let progress_calls_clone = progress_calls.clone();

        let callback = move |_current: u64, _total: u64| {
            *progress_calls_clone.lock().unwrap() += 1;
        };

        let mut encrypted = Vec::new();
        let reader = Cursor::new(&plaintext);
        encrypt_stream(
            reader,
            &mut encrypted,
            &key,
            plaintext.len() as u64,
            Some(&callback)
        ).unwrap();

        // 应该至少调用了 2 次（2 个 chunk）
        let calls = *progress_calls.lock().unwrap();
        assert!(calls >= 2);
    }

    #[test]
    fn test_decrypt_with_wrong_key_fails() {
        let correct_key = [42u8; 32];
        let wrong_key = [99u8; 32];
        let plaintext = b"Secret data";

        // 使用正确密钥加密
        let mut encrypted = Vec::new();
        let reader = Cursor::new(plaintext);
        encrypt_stream(reader, &mut encrypted, &correct_key, plaintext.len() as u64, None).unwrap();

        // 使用错误密钥解密应该失败
        let mut decrypted = Vec::new();
        let reader = Cursor::new(&encrypted);
        let result = decrypt_stream(reader, &mut decrypted, &wrong_key, encrypted.len() as u64, None);

        assert!(result.is_err());
    }

    #[test]
    fn test_tampered_stream_fails_mac() {
        let key = [42u8; 32];
        let plaintext = b"Important data";

        // 加密
        let mut encrypted = Vec::new();
        let reader = Cursor::new(plaintext);
        encrypt_stream(reader, &mut encrypted, &key, plaintext.len() as u64, None).unwrap();

        // 篡改密文（跳过 nonce 前 12 字节）
        if encrypted.len() > 20 {
            encrypted[20] ^= 0xFF;
        }

        // 解密应该失败（MAC 验证失败）
        let mut decrypted = Vec::new();
        let reader = Cursor::new(&encrypted);
        let result = decrypt_stream(reader, &mut decrypted, &key, encrypted.len() as u64, None);

        assert!(matches!(result, Err(CryptoError::MacVerificationFailed)));
    }
}
