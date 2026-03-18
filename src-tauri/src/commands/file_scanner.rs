use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

/// 文件类型枚举
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum FileType {
    /// 文档类
    Document,
    /// 图片类
    Image,
    /// 视频类
    Video,
    /// 音频类
    Audio,
    /// 压缩包类
    Archive,
    /// 代码类
    Code,
    /// 未知类型
    Unknown,
}

/// 文件节点结构
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileNode {
    /// 文件路径
    pub path: String,
    /// 文件名
    pub name: String,
    /// 文件大小（字节）
    pub size: u64,
    /// 是否为目录
    pub is_dir: bool,
    /// 文件类型（仅文件有）
    #[serde(skip_serializing_if = "Option::is_none")]
    pub file_type: Option<FileType>,
    /// MIME 类型（仅文件有）
    #[serde(skip_serializing_if = "Option::is_none")]
    pub mime_type: Option<String>,
    /// 文件扩展名（仅文件有）
    #[serde(skip_serializing_if = "Option::is_none")]
    pub extension: Option<String>,
    /// 子节点（仅目录有）
    #[serde(skip_serializing_if = "Option::is_none")]
    pub children: Option<Vec<FileNode>>,
}

/// 扫描文件树 IPC 命令
///
/// # Arguments
/// * `root_path` - 根目录路径
///
/// # Returns
/// * `Result<FileNode, String>` - 文件树根节点或错误信息
#[tauri::command]
pub async fn scan_file_tree(root_path: String) -> Result<FileNode, String> {
    log::info!("[file_scanner:scan:start] path={}", root_path);

    let path = Path::new(&root_path);

    // 验证路径存在
    if !path.exists() {
        let err = format!("路径不存在: {}", root_path);
        log::error!("[file_scanner:scan:failed] {}", err);
        return Err(err);
    }

    // 递归扫描
    match scan_directory(path) {
        Ok(node) => {
            log::info!("[file_scanner:scan:done] path={}, files={}", root_path, count_files(&node));
            Ok(node)
        }
        Err(e) => {
            let err = format!("扫描失败: {}", e);
            log::error!("[file_scanner:scan:failed] {}", err);
            Err(err)
        }
    }
}

/// 递归扫描目录
fn scan_directory(path: &Path) -> Result<FileNode, std::io::Error> {
    let metadata = fs::metadata(path)?;
    let name = path
        .file_name()
        .and_then(|n| n.to_str())
        .unwrap_or("")
        .to_string();

    let path_str = path.to_string_lossy().to_string();

    if metadata.is_dir() {
        // 读取目录内容
        let entries = fs::read_dir(path)?;
        let mut children = Vec::new();

        for entry in entries {
            match entry {
                Ok(entry) => {
                    let entry_path = entry.path();

                    // 跳过符号链接（避免循环）
                    if entry_path.is_symlink() {
                        log::warn!("[file_scanner:skip_symlink] path={}", entry_path.display());
                        continue;
                    }

                    // 递归扫描子目录/文件
                    match scan_directory(&entry_path) {
                        Ok(child) => children.push(child),
                        Err(e) => {
                            // 权限错误等：记录日志但继续
                            log::warn!("[file_scanner:skip_entry] path={}, err={}", entry_path.display(), e);
                        }
                    }
                }
                Err(e) => {
                    log::warn!("[file_scanner:read_entry_failed] err={}", e);
                }
            }
        }

        // 按名称排序（文件夹优先）
        children.sort_by(|a, b| {
            match (a.is_dir, b.is_dir) {
                (true, false) => std::cmp::Ordering::Less,
                (false, true) => std::cmp::Ordering::Greater,
                _ => a.name.cmp(&b.name),
            }
        });

        Ok(FileNode {
            path: path_str,
            name,
            size: 0, // 目录大小不计算
            is_dir: true,
            file_type: None,
            mime_type: None,
            extension: None,
            children: Some(children),
        })
    } else {
        // 文件节点 - 检测类型
        let (file_type, mime_type, extension) = detect_file_type(path);

        Ok(FileNode {
            path: path_str,
            name,
            size: metadata.len(),
            is_dir: false,
            file_type: Some(file_type),
            mime_type,
            extension,
            children: None,
        })
    }
}

/// 检测文件类型
///
/// # Arguments
/// * `path` - 文件路径
///
/// # Returns
/// * `(FileType, Option<String>, Option<String>)` - (文件类型, MIME类型, 扩展名)
fn detect_file_type(path: &Path) -> (FileType, Option<String>, Option<String>) {
    // 获取扩展名
    let extension = path
        .extension()
        .and_then(|ext| ext.to_str())
        .map(|s| s.to_lowercase());

    // 使用 mime_guess 检测 MIME 类型
    let mime = mime_guess::from_path(path).first();

    let mime_str = mime.as_ref().map(|m| m.to_string());

    // 根据 MIME 类型分类（优先检查扩展名以避免误判）
    let file_type = match mime {
        Some(mime) => {
            // 先通过扩展名检查是否为代码文件（避免 .ts 被误判为 video/mp2t）
            if let Some(ext) = extension.as_deref() {
                match ext {
                    "rs" | "ts" | "tsx" | "jsx" | "js" | "py" | "rb" | "sh" | "go" |
                    "c" | "cpp" | "h" | "java" | "kt" | "swift" | "yaml" | "yml" |
                    "toml" | "json" | "xml" | "html" | "css" | "scss" | "vue" => {
                        return (FileType::Code, mime_str, extension);
                    }
                    _ => {}
                }
            }

            let type_str = mime.type_().as_str();
            let subtype_str = mime.subtype().as_str();

            match type_str {
                "image" => FileType::Image,
                "video" => FileType::Video,
                "audio" => FileType::Audio,
                "text" | "application" => {
                    // 进一步细分
                    match subtype_str {
                        // 文档类
                        "pdf" | "msword" | "vnd.openxmlformats-officedocument.wordprocessingml.document" |
                        "vnd.ms-excel" | "vnd.openxmlformats-officedocument.spreadsheetml.sheet" |
                        "vnd.ms-powerpoint" | "vnd.openxmlformats-officedocument.presentationml.presentation" => {
                            FileType::Document
                        }
                        // 压缩包类
                        "zip" | "x-7z-compressed" | "x-rar-compressed" | "gzip" | "x-tar" => {
                            FileType::Archive
                        }
                        // 代码类
                        "javascript" | "typescript" | "x-python" | "x-ruby" | "x-sh" |
                        "json" | "xml" | "html" | "css" => {
                            FileType::Code
                        }
                        _ => {
                            // 通过扩展名补充判断
                            match extension.as_deref() {
                                Some("rs") | Some("ts") | Some("tsx") | Some("jsx") |
                                Some("py") | Some("rb") | Some("sh") | Some("go") => FileType::Code,
                                Some("txt") | Some("md") | Some("doc") | Some("docx") => FileType::Document,
                                _ => FileType::Unknown,
                            }
                        }
                    }
                }
                _ => FileType::Unknown,
            }
        }
        None => {
            // MIME 检测失败，尝试通过扩展名判断
            match extension.as_deref() {
                Some("jpg") | Some("jpeg") | Some("png") | Some("gif") | Some("webp") | Some("svg") => FileType::Image,
                Some("mp4") | Some("avi") | Some("mkv") | Some("mov") => FileType::Video,
                Some("mp3") | Some("wav") | Some("flac") | Some("ogg") => FileType::Audio,
                Some("zip") | Some("rar") | Some("7z") | Some("tar") | Some("gz") => FileType::Archive,
                Some("txt") | Some("md") | Some("pdf") | Some("doc") | Some("docx") => FileType::Document,
                Some("rs") | Some("ts") | Some("tsx") | Some("js") | Some("jsx") |
                Some("py") | Some("rb") | Some("sh") | Some("go") => FileType::Code,
                _ => FileType::Unknown,
            }
        }
    };

    (file_type, mime_str, extension)
}

/// 统计文件数量（用于日志）
fn count_files(node: &FileNode) -> usize {
    let mut count = if node.is_dir { 0 } else { 1 };

    if let Some(children) = &node.children {
        for child in children {
            count += count_files(child);
        }
    }

    count
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_scan_empty_directory() {
        let temp_dir = TempDir::new().unwrap();
        let path = temp_dir.path();

        let result = scan_directory(path).unwrap();

        assert!(result.is_dir);
        assert_eq!(result.children.unwrap().len(), 0);
    }

    #[test]
    fn test_scan_directory_with_files() {
        let temp_dir = TempDir::new().unwrap();
        let path = temp_dir.path();

        // 创建测试文件
        fs::write(path.join("file1.txt"), "test").unwrap();
        fs::write(path.join("file2.txt"), "test").unwrap();
        fs::create_dir(path.join("subdir")).unwrap();
        fs::write(path.join("subdir/file3.txt"), "test").unwrap();

        let result = scan_directory(path).unwrap();

        assert!(result.is_dir);
        let children = result.children.unwrap();
        assert_eq!(children.len(), 3); // 2 files + 1 dir

        // 验证排序：目录优先
        assert!(children[0].is_dir);
        assert_eq!(children[0].name, "subdir");
    }

    #[test]
    fn test_scan_large_directory() {
        let temp_dir = TempDir::new().unwrap();
        let path = temp_dir.path();

        // 创建 100 个文件
        for i in 0..100 {
            fs::write(path.join(format!("file{}.txt", i)), "test").unwrap();
        }

        let start = std::time::Instant::now();
        let result = scan_directory(path).unwrap();
        let duration = start.elapsed();

        assert_eq!(count_files(&result), 100);

        // 性能要求：100 个文件应在 50ms 内完成
        assert!(duration.as_millis() < 50, "Scan took {:?}", duration);
    }

    #[test]
    fn test_scan_nonexistent_path() {
        let result = std::panic::catch_unwind(|| {
            scan_directory(Path::new("/nonexistent/path"))
        });

        assert!(result.is_ok());
        assert!(result.unwrap().is_err());
    }

    #[test]
    fn test_detect_file_type_images() {
        let (file_type, _, ext) = detect_file_type(Path::new("test.jpg"));
        assert_eq!(file_type, FileType::Image);
        assert_eq!(ext, Some("jpg".to_string()));

        let (file_type, _, _) = detect_file_type(Path::new("test.png"));
        assert_eq!(file_type, FileType::Image);
    }

    #[test]
    fn test_detect_file_type_documents() {
        let (file_type, _, _) = detect_file_type(Path::new("test.pdf"));
        assert_eq!(file_type, FileType::Document);

        let (file_type, _, _) = detect_file_type(Path::new("test.docx"));
        assert_eq!(file_type, FileType::Document);
    }

    #[test]
    fn test_detect_file_type_code() {
        let (file_type, _, _) = detect_file_type(Path::new("test.rs"));
        assert_eq!(file_type, FileType::Code);

        let (file_type, _, _) = detect_file_type(Path::new("test.ts"));
        assert_eq!(file_type, FileType::Code);
    }

    #[test]
    fn test_detect_file_type_archives() {
        let (file_type, _, _) = detect_file_type(Path::new("test.zip"));
        assert_eq!(file_type, FileType::Archive);

        let (file_type, _, _) = detect_file_type(Path::new("test.7z"));
        assert_eq!(file_type, FileType::Archive);
    }

    #[test]
    fn test_detect_file_type_unknown() {
        let (file_type, _, _) = detect_file_type(Path::new("test.unknown"));
        assert_eq!(file_type, FileType::Unknown);
    }
}
