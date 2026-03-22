# Issue #37: 实现缺失的密码管理 IPC 命令（阻塞启动流程）

**GitHub**: https://github.com/aifuun/u-safe/issues/37
**Branch**: feature/37-password-ipc-commands
**Worktree**: /Users/woo/dev/u-safe-37-password-ipc-commands
**Started**: 2026-03-22

## Context

应用启动时直接跳转到登录页面要求输入主密码,但实际上缺少关键的 IPC 命令实现,导致:

1. **无法检测密码是否已设置** - 前端无法判断是首次设置还是日常登录
2. **无法设置密码** - Setup 页面无法将密码保存到后端
3. **无法验证密码** - Login 页面无法验证用户输入的密码

### 根因分析

后端 Rust 代码中 `PasswordManager` 已实现完整功能,但**未暴露为 Tauri IPC 命令**:

**已实现但未暴露的功能**:
```rust
// src-tauri/src/crypto/password.rs
impl PasswordManager {
  pub fn is_password_set(&self) -> bool { ... }              // ✅ 已实现
  pub fn set_password(&self, password: &str) -> Result<...>  // ✅ 已实现
  pub fn verify_password(&self, password: &str) -> Result<...> // ✅ 已实现
}
```

**前端实际调用的 IPC 命令（缺失）**:
```typescript
// app/src/00_kernel/stores/authStore.ts:112
const isSetup = await invoke<boolean>('is_master_key_set');  // ❌ 未注册

// app/src/01_views/setup/SetupPasswordView.tsx:86
await invoke('derive_master_key', { password });  // ❌ 未注册 (设置密码)

// app/src/01_views/login/LoginView.tsx:36
await invoke('verify_password', { password }); // ❌ 未注册 (验证密码)
```

**关键问题**:
1. **命令名称不匹配**: 前端调用 `derive_master_key`,后端应提供同名命令
2. **缺少持久化**: `PasswordManager` 仅在内存存储密码哈希,重启后丢失
3. **状态注入错误**: `PasswordManager::new()` 需要 2 个参数,不能直接调用
4. **返回类型问题**: `verify_password` 返回 `[u8; 32]` 需要序列化支持

## Tasks

### Phase 1: 创建密码存储持久化逻辑

**目标**: 将密码哈希持久化到 `.u-safe/keys/password.hash` 文件

- [x] 在 `PasswordManager` 中添加 `load_from_file()` 方法
  - 从 `.u-safe/keys/password.hash` 读取哈希
  - 如果文件不存在,返回 `None`
  - 错误处理: 文件损坏时返回错误
- [x] 在 `PasswordManager::set_password()` 中添加持久化逻辑
  - 成功设置密码后,写入 `.u-safe/keys/password.hash`
  - 确保目录存在 (创建 `.u-safe/keys/` 如果不存在)
  - 错误处理: 写入失败时返回错误
- [x] 修改 `PasswordManager::new()` 为 `PasswordManager::load()`
  - 自动从文件加载密码哈希
  - 如果文件不存在,初始化为空状态

### Phase 2: 创建 IPC 命令模块

- [x] 创建 `src-tauri/src/commands/auth.rs` 文件
- [x] 实现 `is_master_key_set()` IPC 命令
  ```rust
  #[tauri::command]
  pub fn is_master_key_set(
      password_manager: State<PasswordManager>
  ) -> Result<bool, String> {
      Ok(password_manager.is_password_set())
  }
  ```
- [x] 实现 `derive_master_key()` IPC 命令 (设置密码)
  ```rust
  #[tauri::command]
  pub fn derive_master_key(
      password: String,
      password_manager: State<PasswordManager>
  ) -> Result<Vec<u8>, String> {
      // 1. 检查是否已设置密码
      if password_manager.is_password_set() {
          return Err("密码已设置,无法重复设置".to_string());
      }

      // 2. 设置密码并持久化
      password_manager
          .set_password(&password)
          .map_err(|e| e.to_string())?;

      // 3. 验证并返回密钥
      let key = password_manager
          .verify_password(&password)
          .map_err(|e| e.to_string())?;

      // 4. 返回 Vec<u8> (可序列化)
      Ok(key.to_vec())
  }
  ```
- [x] 实现 `verify_password()` IPC 命令
  ```rust
  #[tauri::command]
  pub fn verify_password(
      password: String,
      password_manager: State<PasswordManager>
  ) -> Result<Vec<u8>, String> {
      password_manager
          .verify_password(&password)
          .map(|key| key.to_vec())  // [u8; 32] → Vec<u8>
          .map_err(|e| e.to_string())
  }
  ```
- [x] 创建 `src-tauri/src/commands/mod.rs` 导出 auth 模块
  ```rust
  pub mod auth;
  ```

### Phase 3: 注册命令到 Tauri

- [x] 在 `src-tauri/src/lib.rs` 中导入 auth 命令
  ```rust
  mod commands;
  use commands::auth::{is_master_key_set, derive_master_key, verify_password};
  ```
- [x] 在 `Builder` 中注入 `PasswordManager` 状态
  ```rust
  .manage(PasswordManager::default())  // 使用 ::default() 而非 ::new()
  ```
- [x] 在 `invoke_handler` 中注册 3 个新命令
  ```rust
  .invoke_handler(tauri::generate_handler![
      hello_world,
      test_db_connection,
      is_master_key_set,     // ✅ 新增
      derive_master_key,     // ✅ 新增 (设置密码)
      verify_password,       // ✅ 新增 (验证密码)
  ])
  ```

### Phase 4: 测试验证

- [ ] **首次启动测试**
  - 启动应用 → 确认跳转到 `/setup` 页面
  - `is_master_key_set` 返回 `false`
- [ ] **设置密码测试**
  - 在 `/setup` 页面输入密码
  - `derive_master_key` 成功返回 32 字节密钥
  - 确认密码保存到 `.u-safe/keys/password.hash`
- [ ] **重启应用测试**
  - 重启应用 → 确认跳转到 `/login` 页面
  - `is_master_key_set` 返回 `true`
- [ ] **验证密码测试**
  - 输入正确密码 → `verify_password` 成功,跳转到 `/files`
  - 输入错误密码 → `verify_password` 失败,显示错误提示
- [ ] **锁定机制测试**
  - 连续 3 次错误密码 → 确认锁定 5 分钟
  - 锁定期间输入正确密码 → 仍然被拒绝

## Implementation Details

### 文件结构
```
src-tauri/src/
├── commands/
│   ├── mod.rs          # 新建 - 导出 auth 模块
│   └── auth.rs         # 新建 - 3 个 IPC 命令实现
├── crypto/
│   └── password.rs     # 修改 - 添加持久化逻辑
└── lib.rs              # 修改 - 注册命令
```

### 密码哈希存储路径

```
.u-safe/
└── keys/
    └── password.hash   # PHC 格式哈希字符串
```

**格式示例**:
```
$argon2id$v=19$m=19456,t=2,p=1$<salt>$<hash>
```

### PasswordManager 持久化改造

**修改前 (内存存储)**:
```rust
impl PasswordManager {
    pub fn new(max_attempts: u32, lockout_duration_secs: u64) -> Self {
        PasswordManager {
            state: Mutex::new(PasswordState {
                stored_hash: None,  // ❌ 重启后丢失
                failed_attempts: 0,
                locked_until: None,
            }),
            max_attempts,
            lockout_duration: Duration::from_secs(lockout_duration_secs),
        }
    }
}
```

**修改后 (文件持久化)**:
```rust
impl PasswordManager {
    /// 从文件加载密码管理器
    pub fn load() -> Result<Self, CryptoError> {
        let hash_file = Self::get_hash_file_path()?;
        let stored_hash = if hash_file.exists() {
            Some(std::fs::read_to_string(&hash_file)?)
        } else {
            None
        };

        Ok(PasswordManager {
            state: Mutex::new(PasswordState {
                stored_hash,  // ✅ 从文件恢复
                failed_attempts: 0,
                locked_until: None,
            }),
            max_attempts: 3,
            lockout_duration: Duration::from_secs(300),
        })
    }

    /// 获取密码哈希文件路径
    fn get_hash_file_path() -> Result<PathBuf, CryptoError> {
        let data_dir = dirs::data_dir()
            .ok_or_else(|| CryptoError::Io("无法获取数据目录".to_string()))?;

        let u_safe_dir = data_dir.join(".u-safe").join("keys");
        std::fs::create_dir_all(&u_safe_dir)?;

        Ok(u_safe_dir.join("password.hash"))
    }

    /// 设置主密码 (添加持久化)
    pub fn set_password(&self, password: &str) -> Result<(), CryptoError> {
        // 派生密钥并生成哈希
        let (_, hash) = derive_key(password)?;

        // 持久化到文件
        let hash_file = Self::get_hash_file_path()?;
        std::fs::write(&hash_file, &hash)?;

        // 存储到内存
        let mut state = self.state.lock().unwrap();
        state.stored_hash = Some(hash);
        state.failed_attempts = 0;
        state.locked_until = None;

        log::info!("[password:set] 主密码已设置并持久化");
        Ok(())
    }
}
```

### 返回类型序列化

**问题**: `[u8; 32]` 固定大小数组不能直接序列化为 JSON

**解决方案**: 返回 `Vec<u8>` 替代

```rust
// ❌ 编译错误 - 固定大小数组不支持 serde
#[tauri::command]
pub fn verify_password(...) -> Result<[u8; 32], String> { ... }

// ✅ 正确 - Vec<u8> 可序列化
#[tauri::command]
pub fn verify_password(...) -> Result<Vec<u8>, String> {
    password_manager
        .verify_password(&password)
        .map(|key| key.to_vec())  // 转换为 Vec<u8>
        .map_err(|e| e.to_string())
}
```

### 状态注入

**问题**: `PasswordManager::new(u32, u64)` 需要 2 个参数

**解决方案**: 使用 `::default()` 或 `::load()`

```rust
// ❌ 错误 - new() 需要参数
.manage(PasswordManager::new())

// ✅ 方案 1: 使用 default()
.manage(PasswordManager::default())

// ✅ 方案 2: 使用 load() (推荐)
.manage(PasswordManager::load().expect("无法加载密码管理器"))
```

## Acceptance Criteria

### 1. IPC 命令实现
- ✅ `is_master_key_set` 返回 `boolean`
- ✅ `derive_master_key` 接受 `password` 参数,首次设置成功并返回 `Vec<u8>`
- ✅ `derive_master_key` 防止重复设置 (已设置则返回错误)
- ✅ `verify_password` 接受 `password` 参数,返回 `Vec<u8>` 或错误

### 2. 密码持久化
- ✅ 密码哈希存储到 `.u-safe/keys/password.hash`
- ✅ 重启应用后密码状态恢复
- ✅ 文件权限安全 (仅当前用户可读写)

### 3. Tauri 集成
- ✅ 命令在 `lib.rs` 中正确注册
- ✅ `PasswordManager` 状态正确注入 (使用 `::load()`)
- ✅ 前端可以成功调用 3 个命令

### 4. 端到端流程
- ✅ 首次启动自动跳转 Setup 页面
- ✅ 设置密码后持久化到文件系统
- ✅ 后续启动跳转 Login 页面
- ✅ 正确密码验证通过
- ✅ 错误密码显示提示并支持重试
- ✅ 3 次错误后锁定机制生效

### 5. 错误处理
- ✅ 文件读写错误有明确日志
- ✅ 密码验证失败有清晰错误消息
- ✅ 锁定状态显示剩余时间

## Progress

- [x] Plan reviewed
- [x] Implementation started
- [x] Implementation completed
- [ ] Tests added
- [ ] Ready for review

## Next Steps

1. 修改 `src-tauri/src/crypto/password.rs` 添加持久化逻辑
2. 创建 `commands/auth.rs` 和 `commands/mod.rs`
3. 实现 3 个 IPC 命令 (按照上面代码片段)
4. 修改 `lib.rs` 注册命令和状态
5. 启动应用测试完整流程
6. 验证所有 Acceptance Criteria
7. 完成后执行 `/finish-issue 37`

## Related Files

- Backend: `src-tauri/src/crypto/password.rs` (修改 - 添加持久化)
- Backend: `src-tauri/src/commands/auth.rs` (新建 - IPC 命令)
- Backend: `src-tauri/src/commands/mod.rs` (新建 - 模块导出)
- Backend: `src-tauri/src/lib.rs` (修改 - 注册命令)
- Frontend: `app/src/00_kernel/stores/authStore.ts` (调用 `is_master_key_set`)
- Frontend: `app/src/01_views/setup/SetupPasswordView.tsx` (调用 `derive_master_key`)
- Frontend: `app/src/01_views/login/LoginView.tsx` (调用 `verify_password`)

## Security Considerations

### 密码哈希安全
- ✅ 使用 Argon2id (内存硬函数,抗 GPU 破解)
- ✅ 随机 Salt (存储在 PHC 格式字符串中)
- ✅ 不存储明文密码
- ✅ 密钥派生后立即 zeroize 内存

### 文件权限
- ✅ `.u-safe/keys/` 目录权限: 0700 (仅当前用户)
- ✅ `password.hash` 文件权限: 0600 (仅当前用户读写)

### 日志安全
- ❌ **禁止**: 不要记录密码或密钥到日志
- ✅ **允许**: 记录操作事件 (`[password:set]`, `[password:verify]`)
- ✅ **允许**: 记录错误次数和锁定状态

## References

- **Pillar I**: Firewalls (IPC 边界保护)
- **Pillar H**: Policy (密码策略)
- **Rule**: `tauri-ipc.md` (IPC 命令规范)
- **Rule**: `secrets.md` (密钥管理)
- **Rule**: `diagnostic-export-logging.md` (结构化日志)
- **Tauri Docs**: https://tauri.app/develop/calling-rust/
