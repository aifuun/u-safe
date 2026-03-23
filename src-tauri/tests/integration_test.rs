use u_safe_lib::db::{Database, get_default_db_path};
use u_safe_lib::crypto::password::PasswordManager;
use u_safe_lib::crypto::keystore::KeyStore;
use std::fs;

#[test]
fn test_database_integration() {
    // Test database creation and initialization
    let db_path = get_default_db_path();
    
    // Clean up any existing test database
    if db_path.exists() {
        std::fs::remove_file(&db_path).ok();
    }
    if let Some(parent) = db_path.parent() {
        if parent.exists() {
            std::fs::remove_dir_all(parent).ok();
        }
    }

    // Create new database
    let db = Database::new(db_path.clone()).unwrap();

    // Verify schema is initialized
    let version: String = db.connection()
        .query_row(
            "SELECT value FROM config WHERE key = 'schema_version'",
            [],
            |row| row.get(0)
        )
        .unwrap();
    
    assert_eq!(version, "1");

    // Verify all tables exist
    let table_count: i32 = db.connection()
        .query_row(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table'",
            [],
            |row| row.get(0)
        )
        .unwrap();
    
    assert!(table_count >= 5, "Expected at least 5 tables, got {}", table_count);

    // Clean up
    std::fs::remove_file(db_path).ok();
}

#[test]
fn test_master_key_wrapping_flow() {
    // 测试 Master Key Wrapping 完整流程：
    // 1. 设置密码 → 生成主密钥 → 加密存储
    // 2. 验证密码 → 解密主密钥
    // 3. 使用主密钥加密/解密文件（这里模拟密钥使用）

    // 清理旧数据
    let data_dir = std::path::PathBuf::from(".u-safe");
    if data_dir.exists() {
        fs::remove_dir_all(&data_dir).ok();
    }

    let password = "TestSecurePassword123!";

    // 步骤 1: 创建密码管理器和密钥库
    let password_manager = PasswordManager::default();
    let keystore = KeyStore::new();

    // 验证初始状态
    assert!(!password_manager.is_password_set(), "初始状态不应该有密码");
    assert!(!keystore.exists(), "初始状态不应该有主密钥文件");

    // 步骤 2: 设置密码
    password_manager
        .set_password(password)
        .expect("设置密码应该成功");

    assert!(password_manager.is_password_set(), "设置后应该有密码");

    // 步骤 3: 派生密钥（从密码）
    let password_key = password_manager
        .verify_password(password)
        .expect("验证密码应该成功");

    // 步骤 4: 生成并存储主密钥（用密码密钥加密）
    let master_key = keystore
        .generate_and_store(&password_key)
        .expect("生成主密钥应该成功");

    assert!(keystore.exists(), "主密钥文件应该存在");

    // 步骤 5: 重新加载主密钥（使用相同的密码密钥）
    let keystore_reload = KeyStore::new();
    let master_key_loaded = keystore_reload
        .load(&password_key)
        .expect("重新加载主密钥应该成功");

    // 验证主密钥相同
    assert_eq!(
        master_key.as_bytes(),
        master_key_loaded.as_bytes(),
        "重新加载的主密钥应该与原始主密钥相同"
    );

    // 步骤 6: 测试错误密码
    let wrong_password = "WrongPassword";
    let wrong_result = password_manager.verify_password(wrong_password);
    assert!(wrong_result.is_err(), "错误密码应该验证失败");

    // 步骤 7: 测试主密钥无法用错误密码解密
    // 先重置错误次数（因为上一步增加了错误次数）
    password_manager.reset_attempts();

    // 再次获取正确的密码密钥
    let correct_key = password_manager
        .verify_password(password)
        .expect("正确密码应该验证成功");

    // 尝试用错误密钥解密（这会失败）
    let mut wrong_key = correct_key.clone();
    wrong_key[0] = wrong_key[0].wrapping_add(1); // 修改一个字节

    let load_with_wrong_key = keystore.load(&wrong_key);
    assert!(
        load_with_wrong_key.is_err(),
        "用错误密钥解密主密钥应该失败"
    );

    // 清理测试数据
    fs::remove_dir_all(&data_dir).ok();

    println!("✅ Master Key Wrapping 完整流程测试通过");
}

#[test]
fn test_master_key_persistence() {
    // 测试主密钥持久化：确保文件正确保存和读取
    // 注意：这个测试使用实际的数据目录 (.u-safe/)

    let password = "PersistenceTest123!";

    // 清理旧数据（如果存在）
    let data_dir = std::path::PathBuf::from(".u-safe");
    if data_dir.exists() {
        fs::remove_dir_all(&data_dir).ok();
    }

    let password_manager = PasswordManager::default();
    let keystore = KeyStore::new();

    // 设置密码并生成主密钥
    password_manager.set_password(password).unwrap();
    let password_key = password_manager.verify_password(password).unwrap();
    let original_master_key = keystore.generate_and_store(&password_key).unwrap();

    // 验证文件存在
    let key_file_path = data_dir.join("keys").join("master.key");
    assert!(key_file_path.exists(), "主密钥文件应该存在: {:?}", key_file_path);

    // 读取文件内容（加密后的）
    let encrypted_content = fs::read(&key_file_path).unwrap();
    assert!(encrypted_content.len() > 12, "加密文件应该包含 nonce + ciphertext");

    // 重新加载主密钥
    let loaded_key = keystore.load(&password_key).unwrap();
    assert_eq!(
        original_master_key.as_bytes(),
        loaded_key.as_bytes(),
        "重新加载的主密钥应该相同"
    );

    // 清理
    fs::remove_dir_all(&data_dir).ok();

    println!("✅ 主密钥持久化测试通过");
}

#[test]
fn test_edge_case_wrong_password() {
    // 边界测试：错误密码应该返回明确错误

    let data_dir = std::path::PathBuf::from(".u-safe");
    if data_dir.exists() {
        fs::remove_dir_all(&data_dir).ok();
    }

    let password = "CorrectPassword123!";
    let wrong_password = "WrongPassword123!";

    let password_manager = PasswordManager::default();
    let keystore = KeyStore::new();

    // 设置密码并生成主密钥
    password_manager.set_password(password).unwrap();
    let password_key = password_manager.verify_password(password).unwrap();
    keystore.generate_and_store(&password_key).unwrap();

    // 测试错误密码验证失败
    password_manager.reset_attempts(); // 重置以避免锁定
    let wrong_result = password_manager.verify_password(wrong_password);
    assert!(wrong_result.is_err(), "错误密码应该验证失败");

    match wrong_result {
        Err(e) => {
            let err_msg = format!("{}", e);
            assert!(err_msg.contains("密码错误"), "错误信息应该明确提示密码错误: {}", err_msg);
        }
        Ok(_) => panic!("不应该验证成功"),
    }

    // 清理
    fs::remove_dir_all(&data_dir).ok();

    println!("✅ 边界测试（错误密码）通过");
}

#[test]
fn test_edge_case_missing_master_key_file() {
    // 边界测试：删除主密钥文件后应该提示损坏

    let data_dir = std::path::PathBuf::from(".u-safe");
    if data_dir.exists() {
        fs::remove_dir_all(&data_dir).ok();
    }

    let password = "TestPassword123!";

    let password_manager = PasswordManager::default();
    let keystore = KeyStore::new();

    // 设置密码并生成主密钥
    password_manager.set_password(password).unwrap();
    let password_key = password_manager.verify_password(password).unwrap();
    keystore.generate_and_store(&password_key).unwrap();

    // 删除主密钥文件（模拟文件损坏）
    let key_file = data_dir.join("keys").join("master.key");
    fs::remove_file(&key_file).expect("删除主密钥文件应该成功");

    // 尝试加载主密钥应该失败
    let load_result = keystore.load(&password_key);
    assert!(load_result.is_err(), "缺失主密钥文件应该加载失败");

    match load_result {
        Err(e) => {
            let err_msg = format!("{}", e);
            assert!(
                err_msg.contains("读取密钥文件失败") || err_msg.contains("KeystoreError"),
                "错误信息应该提示文件问题: {}",
                err_msg
            );
        }
        Ok(_) => panic!("不应该加载成功"),
    }

    // 清理
    fs::remove_dir_all(&data_dir).ok();

    println!("✅ 边界测试（主密钥文件缺失）通过");
}

#[test]
fn test_edge_case_password_hash_without_master_key() {
    // 边界测试：密码哈希存在但主密钥文件不存在（数据不一致）

    let data_dir = std::path::PathBuf::from(".u-safe");
    if data_dir.exists() {
        fs::remove_dir_all(&data_dir).ok();
    }

    let password = "TestPassword123!";

    let password_manager = PasswordManager::default();

    // 只设置密码，不生成主密钥
    password_manager.set_password(password).unwrap();

    // 验证密码应该成功
    let password_key = password_manager.verify_password(password).unwrap();

    // 但加载主密钥应该失败（因为主密钥文件不存在）
    let keystore = KeyStore::new();
    assert!(!keystore.exists(), "主密钥文件不应该存在");

    let load_result = keystore.load(&password_key);
    assert!(
        load_result.is_err(),
        "缺失主密钥文件时加载应该失败"
    );

    // 清理
    fs::remove_dir_all(&data_dir).ok();

    println!("✅ 边界测试（密码哈希存在但主密钥缺失）通过");
}

#[test]
fn test_edge_case_corrupted_master_key_file() {
    // 边界测试：主密钥文件损坏（内容被篡改）

    let data_dir = std::path::PathBuf::from(".u-safe");
    if data_dir.exists() {
        fs::remove_dir_all(&data_dir).ok();
    }

    let password = "TestPassword123!";

    let password_manager = PasswordManager::default();
    let keystore = KeyStore::new();

    // 设置密码并生成主密钥
    password_manager.set_password(password).unwrap();
    let password_key = password_manager.verify_password(password).unwrap();
    keystore.generate_and_store(&password_key).unwrap();

    // 篡改主密钥文件（写入垃圾数据）
    let key_file = data_dir.join("keys").join("master.key");
    fs::write(&key_file, b"corrupted data that is not valid AES-GCM ciphertext").unwrap();

    // 尝试加载主密钥应该失败
    let load_result = keystore.load(&password_key);
    assert!(load_result.is_err(), "损坏的主密钥文件应该加载失败");

    match load_result {
        Err(e) => {
            let err_msg = format!("{}", e);
            assert!(
                err_msg.contains("解密") || err_msg.contains("DecryptionError"),
                "错误信息应该提示解密失败: {}",
                err_msg
            );
        }
        Ok(_) => panic!("不应该加载成功"),
    }

    // 清理
    fs::remove_dir_all(&data_dir).ok();

    println!("✅ 边界测试（主密钥文件损坏）通过");
}
