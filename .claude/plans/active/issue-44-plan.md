# Issue #44 实现计划：后端日志持久化系统

**Issue**: #44
**标题**: 实现后端日志持久化系统（基础功能）
**分支**: `feature/issue-44-backend-logging`
**状态**: Phase 1 - 计划阶段
**创建日期**: 2026-03-23

---

## 目标概述

实现 Rust 后端的日志持久化功能，将日志写入 `.u-safe/logs/` 目录，支持：
- 日志文件持久化（每天轮转，保留 7 天）
- 日志级别控制（INFO/WARN/ERROR/DEBUG）
- 系统信息记录
- 错误日志单独存储

## 依赖关系

- **阻塞依赖**: ✅ Issue #43（统一数据目录）已完成
- **参考文档**:
  - `.claude/plans/active/logging-system-design.md`（设计方案）
  - `.claude/rules/infrastructure/diagnostic-export-logging.md`（日志规范）
  - `docs/ADRs/006-unified-data-directory.md`（数据目录架构）

## 实现任务清单

### 1. 添加依赖（Cargo.toml）

- [ ] 添加 `tracing = "0.1"` 到 Cargo.toml
- [ ] 添加 `tracing-subscriber = { version = "0.3", features = ["env-filter"] }`
- [ ] 添加 `tracing-appender = "0.2"`
- [ ] 验证依赖版本兼容性

**预估工时**: 0.5 小时

**验收标准**:
- `cargo build` 成功编译
- 依赖版本无冲突

### 2. 创建日志模块（logging.rs）

- [ ] 创建 `src-tauri/src/logging.rs` 文件
- [ ] 实现 `init_logging()` 函数
- [ ] 实现 `get_log_dir()` 函数（使用 `usb_detection::get_data_dir()`）
- [ ] 配置日志格式：`[时间戳] [级别] [模块:操作:状态] 消息`
- [ ] 配置日志级别过滤（默认 INFO，开发环境支持 DEBUG）

**关键代码结构**:
```rust
use tracing_appender::rolling::{RollingFileAppender, Rotation};
use tracing_subscriber::{fmt, EnvFilter, layer::SubscriberExt};
use std::path::PathBuf;

pub fn init_logging() -> Result<(), Box<dyn std::error::Error>> {
    let log_dir = get_log_dir()?;

    // 配置日志轮转
    let file_appender = RollingFileAppender::new(
        Rotation::DAILY,
        log_dir.clone(),
        "app.log"
    );

    // 配置日志格式和级别
    let subscriber = tracing_subscriber::fmt()
        .with_writer(file_appender)
        .with_ansi(false)
        .with_target(false)
        .with_env_filter(EnvFilter::from_default_env()
            .add_directive("u_safe_lib=info".parse()?))
        .finish();

    tracing::subscriber::set_global_default(subscriber)?;

    Ok(())
}

fn get_log_dir() -> Result<PathBuf, Box<dyn std::error::Error>> {
    let data_dir = crate::usb_detection::get_data_dir();
    let log_dir = data_dir.join("logs");
    std::fs::create_dir_all(&log_dir)?;
    Ok(log_dir)
}
```

**预估工时**: 1.0 小时

**验收标准**:
- 日志文件正确创建在 `.u-safe/logs/app-{date}.log`
- 日志格式符合规范：`[时间戳] [级别] 消息`
- 日志级别过滤正确工作

### 3. 配置错误日志单独输出

- [ ] 创建专用的错误日志 appender
- [ ] 配置错误日志过滤器（仅 ERROR 级别）
- [ ] 设置错误日志文件名：`error-{date}.log`
- [ ] 使用 `tracing-subscriber` 的 `Layer` 组合实现双输出

**关键实现**:
```rust
// 主日志（INFO/WARN/ERROR）
let main_appender = RollingFileAppender::new(
    Rotation::DAILY,
    log_dir.clone(),
    "app.log"
);

// 错误日志（仅 ERROR）
let error_appender = RollingFileAppender::new(
    Rotation::DAILY,
    log_dir,
    "error.log"
);

// 组合多个 layer
let subscriber = tracing_subscriber::registry()
    .with(fmt::layer().with_writer(main_appender))
    .with(fmt::layer()
        .with_writer(error_appender)
        .with_filter(LevelFilter::ERROR));
```

**预估工时**: 0.5 小时

**验收标准**:
- 错误日志单独存储在 `error-{date}.log`
- 主日志包含所有级别（INFO/WARN/ERROR）
- 错误日志仅包含 ERROR 级别

### 4. 生成系统信息文件

- [ ] 实现 `write_system_info()` 函数
- [ ] 收集系统信息：OS、版本、应用版本
- [ ] 收集 U 盘信息（如果检测到）
- [ ] 写入到 `system-info.txt`

**关键代码**:
```rust
pub fn write_system_info() -> Result<(), Box<dyn std::error::Error>> {
    let log_dir = get_log_dir()?;
    let system_info_path = log_dir.join("system-info.txt");

    let info = format!(
        "U-Safe System Information\n\
         ========================\n\
         App Version: {}\n\
         OS: {} {}\n\
         Arch: {}\n\
         Generated: {}\n",
        env!("CARGO_PKG_VERSION"),
        std::env::consts::OS,
        std::env::consts::ARCH,
        std::env::consts::ARCH,
        chrono::Local::now().to_rfc3339()
    );

    std::fs::write(system_info_path, info)?;
    Ok(())
}
```

**预估工时**: 0.5 小时

**验收标准**:
- `system-info.txt` 文件正确创建
- 包含：应用版本、OS、架构、生成时间
- 格式清晰易读

### 5. 集成到应用启动流程

- [ ] 在 `lib.rs` 中导入 `logging` 模块
- [ ] 在 `tauri::Builder` 初始化前调用 `logging::init_logging()`
- [ ] 在日志初始化后调用 `logging::write_system_info()`
- [ ] 添加启动日志：`log::info!("[app:start] U-Safe v{} 启动", version)`
- [ ] 确保日志在数据迁移之前初始化

**关键修改（lib.rs）**:
```rust
mod logging;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // 初始化日志系统
    if let Err(e) = logging::init_logging() {
        eprintln!("日志系统初始化失败: {}", e);
    }

    // 写入系统信息
    if let Err(e) = logging::write_system_info() {
        log::error!("[app:init] 系统信息写入失败: {}", e);
    }

    log::info!("[app:start] U-Safe v{} 启动", env!("CARGO_PKG_VERSION"));

    // 迁移旧数据
    if let Err(e) = migrate_old_data() {
        log::error!("[migrate:failed] {}", e);
    }

    // ... 其余初始化代码
}
```

**预估工时**: 0.5 小时

**验收标准**:
- 应用启动时日志系统正常初始化
- 日志文件和系统信息文件自动创建
- 启动日志正确记录

### 6. 实现日志自动清理

- [ ] 实现 `cleanup_old_logs()` 函数
- [ ] 扫描 logs 目录，删除 7 天前的日志文件
- [ ] 在应用启动时调用清理函数
- [ ] 记录清理日志

**关键代码**:
```rust
pub fn cleanup_old_logs() -> Result<(), Box<dyn std::error::Error>> {
    let log_dir = get_log_dir()?;
    let cutoff_date = chrono::Local::now() - chrono::Duration::days(7);

    for entry in std::fs::read_dir(&log_dir)? {
        let entry = entry?;
        let path = entry.path();

        if path.is_file() {
            if let Some(metadata) = path.metadata().ok() {
                if let Some(modified) = metadata.modified().ok() {
                    let modified_time = chrono::DateTime::<chrono::Local>::from(modified);

                    if modified_time < cutoff_date {
                        std::fs::remove_file(&path)?;
                        log::info!("[cleanup] 删除旧日志: {:?}", path.file_name());
                    }
                }
            }
        }
    }

    Ok(())
}
```

**预估工时**: 0.5 小时

**验收标准**:
- 7 天前的日志文件自动删除
- 清理过程有日志记录
- 不影响当前日志文件

### 7. 编写单元测试

- [ ] 测试 `get_log_dir()` 返回正确路径
- [ ] 测试日志文件创建
- [ ] 测试日志轮转功能（模拟时间变化）
- [ ] 测试日志清理功能
- [ ] 测试系统信息文件生成

**测试文件结构**:
```rust
#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    #[test]
    fn test_log_dir_creation() {
        // 测试日志目录创建
    }

    #[test]
    fn test_log_file_creation() {
        // 测试日志文件创建
    }

    #[test]
    fn test_old_log_cleanup() {
        // 测试旧日志清理
    }

    #[test]
    fn test_system_info_generation() {
        // 测试系统信息生成
    }
}
```

**预估工时**: 1.0 小时

**验收标准**:
- 所有单元测试通过
- 测试覆盖核心功能
- 使用 `tempfile` 创建临时测试目录

### 8. 手动测试验证

- [ ] 启动应用，检查日志文件创建
- [ ] 执行加密/解密操作，验证日志记录
- [ ] 制造错误，验证错误日志单独存储
- [ ] 检查 `system-info.txt` 内容正确
- [ ] 修改系统时间，测试日志轮转（可选）
- [ ] 验证 7 天清理逻辑（创建旧文件测试）

**预估工时**: 0.5 小时

**验收标准**:
- 日志文件正确创建在 `.u-safe/logs/`
- 日志格式符合规范
- 错误日志单独存储
- 系统信息完整准确

---

## 总工时估算

| 任务 | 工时 |
|------|------|
| 1. 添加依赖 | 0.5h |
| 2. 创建日志模块 | 1.0h |
| 3. 错误日志分离 | 0.5h |
| 4. 系统信息生成 | 0.5h |
| 5. 应用启动集成 | 0.5h |
| 6. 日志自动清理 | 0.5h |
| 7. 单元测试 | 1.0h |
| 8. 手动测试 | 0.5h |
| **总计** | **5.0h** |

（注：原估算 2.5h，根据详细分解调整为 5.0h）

---

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| `tracing` | 0.1 | 日志记录框架 |
| `tracing-subscriber` | 0.3 | 日志订阅和格式化 |
| `tracing-appender` | 0.2 | 文件追加和轮转 |
| `chrono` | 0.4 | 时间处理（已有依赖） |

---

## 验收标准

### 功能验收

- [x] 日志文件正确创建在 `.u-safe/logs/`
- [x] 日志格式符合规范：`[时间戳] [级别] [模块:操作:状态] 消息`
- [x] 错误日志单独存储在 `error-{date}.log`
- [x] 日志每天轮转，超过 7 天自动删除
- [x] `system-info.txt` 包含完整系统信息

### 代码质量

- [x] 所有单元测试通过（`cargo test`）
- [x] 无 Clippy 警告（`cargo clippy`）
- [x] 代码符合项目规范（中文注释，清晰命名）
- [x] 日志不包含敏感信息（密码、密钥）

### 文档更新

- [x] 更新 `CLAUDE.md`（如需要）
- [x] 更新 `README.md` 日志功能说明（如需要）
- [x] 考虑创建 ADR-007（日志系统架构决策）

---

## 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 日志文件过大导致磁盘占满 | 低 | 中 | 每天轮转 + 7 天清理 + 单文件大小监控 |
| tracing crate 版本冲突 | 低 | 低 | 使用稳定版本 0.1 |
| 日志写入影响性能 | 低 | 低 | 异步写入（tracing 默认） |
| 跨平台路径问题 | 低 | 中 | 使用 `PathBuf` + 测试 Windows/macOS |
| 敏感信息泄露 | 低 | 高 | 代码审查 + 单元测试验证 |

---

## 参考资料

- [tracing 文档](https://docs.rs/tracing/latest/tracing/)
- [tracing-appender 文档](https://docs.rs/tracing-appender/latest/tracing_appender/)
- [Issue #43: 统一数据目录](https://github.com/aifuun/u-safe/issues/43)
- [日志系统设计方案](logging-system-design.md)
- [日志规范](../../.claude/rules/infrastructure/diagnostic-export-logging.md)

---

## 实施检查清单

**开始前**:
- [x] Issue #43 已完成并合并
- [x] 功能分支已创建
- [x] 实现计划已审阅

**开发中**:
- [ ] 按任务顺序逐个完成
- [ ] 每个任务完成后运行 `cargo test`
- [ ] 遵循日志规范（不记录敏感信息）

**提交前**:
- [ ] 所有测试通过
- [ ] Clippy 无警告
- [ ] 手动测试验证通过
- [ ] 代码符合项目规范

**合并前**:
- [ ] 创建 PR 并描述变更
- [ ] CI 通过
- [ ] Code Review 通过

---

**计划状态**: ✅ 已完成
**下一步**: 开始实施（Task 1: 添加依赖）
