# Issue #46 实施计划：实现日志导出功能（ZIP + UI）

> **Issue**: #46
> **分支**: `feature/issue-46-log-export-ui`
> **创建时间**: 2026-03-23
> **预估工时**: 2 小时
> **状态**: 计划中

---

## 1. 目标

实现用户友好的日志导出功能，包括后端 ZIP 打包、前端 UI 组件和系统文件对话框集成。用户可以导出最近 7 天的日志文件用于问题诊断和反馈。

## 2. 依赖关系

### 阻塞依赖
- ✅ Issue #45（前端日志服务）- 已完成
- ✅ Issue #44（后端日志持久化）- 已完成

### 技术依赖
- ✅ Tauri 文件对话框 API (`@tauri-apps/api/dialog`)
- ✅ Rust `zip` crate（需添加到 Cargo.toml）
- ✅ 后端日志系统（`tracing-appender`）

## 3. 实施步骤

### Step 1: 添加 Rust 依赖和系统信息收集

**时长**: 30 分钟

**文件**:
- `src-tauri/Cargo.toml` (修改)
- `src-tauri/src/commands/logging.rs` (修改)

**任务**:
- [ ] 添加 `zip` crate 依赖
- [ ] 添加 `sysinfo` crate 依赖（收集系统信息）
- [ ] 实现 `collect_system_info` 函数

**实现细节**:
```toml
# src-tauri/Cargo.toml
[dependencies]
zip = "0.6"
sysinfo = "0.30"
```

```rust
// src-tauri/src/commands/logging.rs
use sysinfo::{System, SystemExt};
use std::fs;

/// 收集系统信息
///
/// 返回格式化的系统信息字符串，包含：
/// - 应用版本
/// - 操作系统信息
/// - 硬件信息
/// - 日志文件统计
fn collect_system_info() -> Result<String, String> {
    let mut sys = System::new_all();
    sys.refresh_all();

    let info = format!(
        r#"# U-Safe 系统信息
生成时间: {}

## 应用信息
版本: {}
平台: Tauri 2.0
构建日期: {}

## 系统信息
操作系统: {} {}
架构: {}
内核版本: {}
主机名: {}

## 硬件信息
CPU: {} 核心
总内存: {} GB
可用内存: {} GB

## 日志文件统计
日志目录: {}
文件数量: {}
总大小: {} MB
"#,
        chrono::Local::now().format("%Y-%m-%d %H:%M:%S"),
        env!("CARGO_PKG_VERSION"),
        env!("VERGEN_BUILD_DATE", "未知"),
        sys.name().unwrap_or_else(|| "未知".to_string()),
        sys.os_version().unwrap_or_else(|| "未知".to_string()),
        std::env::consts::ARCH,
        sys.kernel_version().unwrap_or_else(|| "未知".to_string()),
        sys.host_name().unwrap_or_else(|| "未知".to_string()),
        sys.cpus().len(),
        sys.total_memory() / 1024 / 1024 / 1024,
        sys.available_memory() / 1024 / 1024 / 1024,
        get_log_dir()?.display(),
        count_log_files()?,
        calculate_log_size_mb()?,
    );

    Ok(info)
}

/// 统计日志文件数量
fn count_log_files() -> Result<usize, String> {
    let log_dir = get_log_dir()?;
    let count = fs::read_dir(log_dir)
        .map_err(|e| e.to_string())?
        .filter(|entry| {
            entry.as_ref()
                .ok()
                .and_then(|e| e.path().extension())
                .and_then(|ext| ext.to_str())
                == Some("log")
        })
        .count();
    Ok(count)
}

/// 计算日志文件总大小（MB）
fn calculate_log_size_mb() -> Result<u64, String> {
    let log_dir = get_log_dir()?;
    let total_size: u64 = fs::read_dir(log_dir)
        .map_err(|e| e.to_string())?
        .filter_map(|entry| entry.ok())
        .filter_map(|entry| entry.metadata().ok())
        .map(|metadata| metadata.len())
        .sum();
    Ok(total_size / 1024 / 1024)
}
```

**验收标准**:
- [ ] 编译通过（`cargo build`）
- [ ] `collect_system_info` 返回正确格式的字符串
- [ ] 系统信息包含所有关键字段

---

### Step 2: 实现日志导出 IPC 命令

**时长**: 45 分钟

**文件**:
- `src-tauri/src/commands/logging.rs` (修改)

**任务**:
- [ ] 实现 `export_diagnostic_logs` IPC 命令
- [ ] 收集最近 7 天的日志文件
- [ ] 创建 ZIP 压缩包
- [ ] 包含系统信息文件

**实现细节**:
```rust
// src-tauri/src/commands/logging.rs
use zip::write::FileOptions;
use zip::ZipWriter;
use std::fs::File;
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use chrono::{Local, Duration};

/// 导出诊断日志
///
/// 功能：
/// 1. 收集最近 7 天的日志文件
/// 2. 生成系统信息文件
/// 3. 创建 ZIP 压缩包
/// 4. 返回 ZIP 文件路径
///
/// 返回值：ZIP 文件的绝对路径
#[tauri::command]
pub async fn export_diagnostic_logs() -> Result<String, String> {
    log::info!("[logging:export:start] 开始导出诊断日志");

    // 1. 创建临时目录
    let temp_dir = std::env::temp_dir().join(format!("u-safe-logs-export-{}", Local::now().timestamp()));
    fs::create_dir_all(&temp_dir).map_err(|e| format!("创建临时目录失败: {}", e))?;

    // 2. 收集日志文件（最近 7 天）
    let log_files = collect_recent_logs(7)?;
    log::info!("[logging:export:collect] 收集到 {} 个日志文件", log_files.len());

    // 3. 生成系统信息文件
    let system_info = collect_system_info()?;
    let system_info_path = temp_dir.join("system-info.txt");
    fs::write(&system_info_path, system_info).map_err(|e| format!("写入系统信息失败: {}", e))?;

    // 4. 创建 ZIP 文件
    let zip_filename = format!("u-safe-logs-{}.zip", Local::now().format("%Y-%m-%d"));
    let zip_path = temp_dir.join(&zip_filename);
    create_log_zip(&zip_path, &log_files, &system_info_path)?;

    log::info!("[logging:export:done] ZIP 文件已创建: {}", zip_path.display());

    Ok(zip_path.to_string_lossy().to_string())
}

/// 收集最近 N 天的日志文件
///
/// @param days - 收集的天数
/// @return 日志文件路径列表
fn collect_recent_logs(days: i64) -> Result<Vec<PathBuf>, String> {
    let log_dir = get_log_dir()?;
    let cutoff_date = Local::now() - Duration::days(days);

    let mut log_files = Vec::new();

    for entry in fs::read_dir(log_dir).map_err(|e| e.to_string())? {
        let entry = entry.map_err(|e| e.to_string())?;
        let path = entry.path();

        // 只收集 .log 文件
        if path.extension().and_then(|s| s.to_str()) != Some("log") {
            continue;
        }

        // 检查文件修改时间
        if let Ok(metadata) = path.metadata() {
            if let Ok(modified) = metadata.modified() {
                let modified_chrono: chrono::DateTime<Local> = modified.into();
                if modified_chrono > cutoff_date {
                    log_files.push(path);
                }
            }
        }
    }

    // 按文件名排序（确保时间顺序）
    log_files.sort();

    Ok(log_files)
}

/// 创建日志 ZIP 压缩包
///
/// @param zip_path - ZIP 文件输出路径
/// @param log_files - 要打包的日志文件列表
/// @param system_info_path - 系统信息文件路径
fn create_log_zip(
    zip_path: &Path,
    log_files: &[PathBuf],
    system_info_path: &Path,
) -> Result<(), String> {
    let file = File::create(zip_path).map_err(|e| format!("创建 ZIP 文件失败: {}", e))?;
    let mut zip = ZipWriter::new(file);

    let options = FileOptions::default()
        .compression_method(zip::CompressionMethod::Deflated)
        .unix_permissions(0o755);

    // 添加系统信息文件
    add_file_to_zip(&mut zip, system_info_path, "system-info.txt", options)?;

    // 添加所有日志文件
    for log_file in log_files {
        if let Some(filename) = log_file.file_name() {
            add_file_to_zip(&mut zip, log_file, filename.to_str().unwrap(), options)?;
        }
    }

    zip.finish().map_err(|e| format!("完成 ZIP 文件失败: {}", e))?;

    Ok(())
}

/// 添加单个文件到 ZIP
fn add_file_to_zip<W: Write + std::io::Seek>(
    zip: &mut ZipWriter<W>,
    file_path: &Path,
    zip_filename: &str,
    options: FileOptions,
) -> Result<(), String> {
    zip.start_file(zip_filename, options)
        .map_err(|e| format!("添加文件到 ZIP 失败: {}", e))?;

    let mut file = File::open(file_path)
        .map_err(|e| format!("打开文件失败: {}", e))?;
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)
        .map_err(|e| format!("读取文件失败: {}", e))?;

    zip.write_all(&buffer)
        .map_err(|e| format!("写入 ZIP 失败: {}", e))?;

    Ok(())
}
```

**验收标准**:
- [ ] 编译通过（`cargo build`）
- [ ] 可以成功创建 ZIP 文件
- [ ] ZIP 包含所有日志文件和系统信息
- [ ] 文件名格式正确：`u-safe-logs-YYYY-MM-DD.zip`

---

### Step 3: 创建设置页面 UI 组件

**时长**: 30 分钟

**文件**:
- `app/src/02_modules/settings/components/DiagnosticExport.tsx` (新建)
- `app/src/02_modules/settings/views/SettingsView.tsx` (修改)
- `app/src/02_modules/settings/components/DiagnosticExport.css` (新建)

**任务**:
- [ ] 创建 `DiagnosticExport` 组件
- [ ] 实现"导出诊断日志"按钮
- [ ] 添加说明文字
- [ ] 集成到设置页面

**实现细节**:
```typescript
// app/src/02_modules/settings/components/DiagnosticExport.tsx
import { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { save } from '@tauri-apps/api/dialog';
import { logger } from '@/00_kernel/services/logService';
import './DiagnosticExport.css';

/**
 * 诊断日志导出组件
 *
 * 功能：
 * 1. 导出最近 7 天的日志文件
 * 2. 打开系统文件保存对话框
 * 3. 显示导出状态（进行中/成功/失败）
 */
export function DiagnosticExport() {
  const [isExporting, setIsExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');

  /**
   * 导出诊断日志
   */
  const handleExport = async () => {
    setIsExporting(true);
    setExportStatus('idle');
    setErrorMessage('');

    try {
      logger.info('settings:export-logs:start');

      // 1. 调用后端生成 ZIP 文件
      const zipPath = await invoke<string>('export_diagnostic_logs');

      logger.info('settings:export-logs:zip-created', { zipPath });

      // 2. 打开系统保存对话框
      const savePath = await save({
        defaultPath: `u-safe-logs-${new Date().toISOString().split('T')[0]}.zip`,
        filters: [
          {
            name: 'ZIP 压缩包',
            extensions: ['zip'],
          },
        ],
      });

      if (!savePath) {
        // 用户取消保存
        logger.info('settings:export-logs:cancelled');
        setIsExporting(false);
        return;
      }

      // 3. 移动文件到用户选择的位置
      await invoke('move_file', {
        from: zipPath,
        to: savePath,
      });

      logger.info('settings:export-logs:success', { savePath });
      setExportStatus('success');

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('settings:export-logs:failed', { error: errorMsg });
      setExportStatus('error');
      setErrorMessage(errorMsg);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="diagnostic-export">
      <h3 className="diagnostic-export__title">📊 诊断与日志</h3>

      <div className="diagnostic-export__content">
        <button
          className="diagnostic-export__button"
          onClick={handleExport}
          disabled={isExporting}
        >
          {isExporting ? '⏳ 导出中...' : '📤 导出诊断日志'}
        </button>

        <p className="diagnostic-export__description">
          导出最近 7 天的日志文件，用于问题诊断和反馈。
          包含应用日志和系统信息。
        </p>

        {exportStatus === 'success' && (
          <div className="diagnostic-export__success">
            ✅ 日志导出成功！
          </div>
        )}

        {exportStatus === 'error' && (
          <div className="diagnostic-export__error">
            ❌ 导出失败：{errorMessage}
          </div>
        )}
      </div>
    </div>
  );
}
```

```css
/* app/src/02_modules/settings/components/DiagnosticExport.css */

.diagnostic-export {
  padding: var(--space-4);
  background: var(--bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-1);
}

.diagnostic-export__title {
  font-size: var(--text-lg);
  font-weight: 700;
  margin-bottom: var(--space-3);
  color: var(--text-primary);
}

.diagnostic-export__content {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.diagnostic-export__button {
  padding: var(--space-3) var(--space-4);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  transition: background-color var(--duration-fast) var(--ease-out);
  align-self: flex-start;
}

.diagnostic-export__button:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.diagnostic-export__button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.diagnostic-export__description {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
}

.diagnostic-export__success {
  padding: var(--space-3);
  background: var(--bg-success);
  color: var(--color-success);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
}

.diagnostic-export__error {
  padding: var(--space-3);
  background: var(--bg-error);
  color: var(--color-error);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .diagnostic-export__button {
    width: 100%;
  }
}
```

**验收标准**:
- [ ] 组件渲染正常
- [ ] 按钮点击触发导出流程
- [ ] 成功/失败状态显示正确
- [ ] CSS 符合设计系统规范

---

### Step 4: 实现文件移动 IPC 命令

**时长**: 15 分钟

**文件**:
- `src-tauri/src/commands/mod.rs` (修改)
- `src-tauri/src/lib.rs` (修改)

**任务**:
- [ ] 实现 `move_file` IPC 命令
- [ ] 注册命令到 Tauri builder

**实现细节**:
```rust
// src-tauri/src/commands/mod.rs
pub mod logging;

/// 移动文件
///
/// @param from - 源文件路径
/// @param to - 目标文件路径
#[tauri::command]
pub fn move_file(from: String, to: String) -> Result<(), String> {
    std::fs::rename(&from, &to)
        .map_err(|e| format!("移动文件失败: {}", e))?;
    Ok(())
}
```

```rust
// src-tauri/src/lib.rs
mod commands;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            commands::logging::write_frontend_log,
            commands::logging::export_diagnostic_logs,
            commands::move_file,
            // ... 其他命令
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

**验收标准**:
- [ ] 编译通过
- [ ] 可以成功移动文件
- [ ] 错误处理正确

---

## 4. 验收清单

### 功能验收
- [ ] 点击"导出诊断日志"成功生成 ZIP 文件
- [ ] ZIP 包含所有日志文件（最近 7 天）
- [ ] ZIP 包含系统信息文件
- [ ] 文件名格式：`u-safe-logs-YYYY-MM-DD.zip`
- [ ] 用户可选择保存位置
- [ ] 导出成功/失败有明确提示

### 技术验收
- [ ] TypeScript 编译无错误
- [ ] Rust 编译无警告
- [ ] UI 符合设计系统规范
- [ ] 日志记录完整（导出过程）

### 用户体验验收
- [ ] 导出流程流畅（无卡顿）
- [ ] 按钮状态反馈清晰（进行中/完成）
- [ ] 错误提示友好（中文描述）

---

## 5. 测试计划

### 手动测试

**场景 1: 正常导出流程**
```bash
# 1. 启动应用
npm run tauri dev

# 2. 打开设置页面
# 3. 点击"导出诊断日志"
# 4. 选择保存位置（例如：桌面）
# 5. 验证文件生成成功
# 6. 解压 ZIP 文件
unzip ~/Desktop/u-safe-logs-2026-03-23.zip -d ~/Desktop/logs-test

# 7. 验证文件内容
ls ~/Desktop/logs-test
# 预期：system-info.txt + app-*.log + error-*.log
```

**场景 2: 取消保存**
```
1. 点击"导出诊断日志"
2. 在文件对话框中点击"取消"
3. 验证应用不报错
4. 验证状态恢复正常
```

**场景 3: 无日志文件**
```bash
# 1. 删除所有日志文件
rm -rf ~/.u-safe/logs/*.log

# 2. 点击"导出诊断日志"
# 3. 验证 ZIP 仅包含 system-info.txt
# 4. 验证不报错
```

**场景 4: 磁盘空间不足**
```
1. 模拟磁盘空间不足（测试环境）
2. 点击"导出诊断日志"
3. 验证显示错误提示
4. 验证应用不崩溃
```

### 系统信息验证
```bash
# 解压 ZIP 后查看系统信息
cat system-info.txt

# 验证包含：
# - 应用版本
# - 操作系统信息
# - 硬件信息
# - 日志文件统计
```

---

## 6. 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| ZIP 创建失败（磁盘空间不足） | 高 | 低 | 错误提示 + 日志记录 |
| 文件移动失败（权限问题） | 中 | 低 | 使用 fs::copy + 删除源文件 |
| 日志文件过大（> 100MB） | 中 | 低 | 已有日志轮转机制（每天 10MB） |
| 系统信息收集失败 | 低 | 低 | 使用 unwrap_or_default 提供默认值 |

---

## 7. 后续优化（Post-MVP）

| 优化项 | 优先级 | 说明 |
|--------|--------|------|
| 菜单项快捷方式 | P2 | "帮助" → "导出诊断日志" |
| 日志级别选择器 | P2 | 用户可配置日志级别（INFO/DEBUG/ERROR） |
| 导出进度条 | P3 | 显示 ZIP 创建进度 |
| 自动上传（可选） | P3 | 未来支持联网后，可选匿名上传 |

---

## 8. 参考文档

| 文档 | 路径 |
|------|------|
| 日志系统设计 | `.claude/plans/active/logging-system-design.md` |
| 日志使用场景 | `.claude/plans/active/logging-usage-scenarios.md` |
| Tauri 文件对话框 | `https://tauri.app/develop/api-js/dialog/` |
| 设计系统规范 | `.claude/rules/frontend/design-system.md` |
| 设计 Token | `.claude/rules/frontend/design-tokens.md` |

---

## 9. 时间线

| 阶段 | 时长 | 累计 |
|------|------|------|
| Step 1: Rust 依赖和系统信息 | 30 分钟 | 30 分钟 |
| Step 2: 日志导出 IPC 命令 | 45 分钟 | 1 小时 15 分钟 |
| Step 3: 设置页面 UI 组件 | 30 分钟 | 1 小时 45 分钟 |
| Step 4: 文件移动命令 | 15 分钟 | 2 小时 |
| **总计** | **2 小时** | - |

---

## 10. 签名

**计划创建者**: Claude (Sonnet 4.5)
**计划审核者**: 待用户确认
**实施状态**: 待开始

---

**下一步**: 等待用户确认计划，然后开始实施 Step 1
