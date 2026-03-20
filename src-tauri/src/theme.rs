/**
 * 系统主题检测模块
 *
 * 提供系统主题自动检测和监听功能
 */

use serde::{Deserialize, Serialize};

/// 系统主题类型
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum SystemTheme {
    /// 亮色主题
    Light,
    /// 暗色主题
    Dark,
}

/// 获取当前系统主题
///
/// # Returns
/// * `Result<SystemTheme, String>` - 系统主题或错误信息
pub fn get_system_theme() -> Result<SystemTheme, String> {
    #[cfg(target_os = "macos")]
    {
        get_macos_theme()
    }

    #[cfg(target_os = "windows")]
    {
        get_windows_theme()
    }

    #[cfg(target_os = "linux")]
    {
        get_linux_theme()
    }

    #[cfg(not(any(target_os = "macos", target_os = "windows", target_os = "linux")))]
    {
        // 默认返回亮色主题
        Ok(SystemTheme::Light)
    }
}

#[cfg(target_os = "macos")]
fn get_macos_theme() -> Result<SystemTheme, String> {
    use std::process::Command;

    let output = Command::new("defaults")
        .args(&["read", "-g", "AppleInterfaceStyle"])
        .output()
        .map_err(|e| format!("读取系统主题失败: {}", e))?;

    if output.status.success() {
        let theme_str = String::from_utf8_lossy(&output.stdout);
        if theme_str.trim() == "Dark" {
            Ok(SystemTheme::Dark)
        } else {
            Ok(SystemTheme::Light)
        }
    } else {
        // 如果命令失败（未设置 AppleInterfaceStyle），默认为亮色
        Ok(SystemTheme::Light)
    }
}

#[cfg(target_os = "windows")]
fn get_windows_theme() -> Result<SystemTheme, String> {
    use winreg::RegKey;
    use winreg::enums::*;

    let hkcu = RegKey::predef(HKEY_CURRENT_USER);
    let personalize = hkcu
        .open_subkey("Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")
        .map_err(|e| format!("打开注册表失败: {}", e))?;

    let apps_use_light_theme: u32 = personalize
        .get_value("AppsUseLightTheme")
        .map_err(|e| format!("读取主题设置失败: {}", e))?;

    if apps_use_light_theme == 0 {
        Ok(SystemTheme::Dark)
    } else {
        Ok(SystemTheme::Light)
    }
}

#[cfg(target_os = "linux")]
fn get_linux_theme() -> Result<SystemTheme, String> {
    use std::process::Command;

    // 尝试使用 gsettings 读取 GNOME 主题
    let output = Command::new("gsettings")
        .args(&["get", "org.gnome.desktop.interface", "gtk-theme"])
        .output()
        .map_err(|e| format!("读取系统主题失败: {}", e))?;

    if output.status.success() {
        let theme_str = String::from_utf8_lossy(&output.stdout);
        let theme_lower = theme_str.to_lowercase();

        if theme_lower.contains("dark") {
            Ok(SystemTheme::Dark)
        } else {
            Ok(SystemTheme::Light)
        }
    } else {
        // 默认返回亮色主题
        Ok(SystemTheme::Light)
    }
}

/// 获取系统主题 IPC 命令
#[tauri::command]
pub async fn get_theme() -> Result<SystemTheme, String> {
    log::info!("[theme:get:start]");

    let theme = get_system_theme()?;

    log::info!("[theme:get:done] theme={:?}", theme);

    Ok(theme)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_system_theme() {
        // 测试系统主题检测（具体结果取决于运行环境）
        let result = get_system_theme();
        assert!(result.is_ok());

        let theme = result.unwrap();
        assert!(theme == SystemTheme::Light || theme == SystemTheme::Dark);
    }
}
