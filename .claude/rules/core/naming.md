# Naming Rules

> 代码结构使用中性名称，不硬编码产品名。

## 命名规范

| 上下文 | 规范 | 示例 |
|--------|------|------|
| 类型/组件 | PascalCase | `FileEncryptor`, `TagManager` |
| 函数/变量 | camelCase | `encryptFile`, `tagList` |
| 文件名 | kebab-case | `file-encryptor.ts`, `tag-manager.rs` |
| CSS 类名 | kebab-case | `.file-card`, `.tag-tree` |
| 数据库表 | snake_case | `file_tags`, `encryption_meta` |
| Rust 模块 | snake_case | `crypto_engine`, `tag_service` |

## 产品名分离

| 层级 | 说明 | 示例 |
|------|------|------|
| **代码结构** | 中性名称，不含品牌 | `MainWindow`, `AppConfig` |
| **运行时资源** | 可含产品名 | `.u-safe/`, `metadata.db` |
| **用户界面** | 产品显示名 | "U-Safe", "万能保险箱" |

```rust
// ✅ 中性代码结构
pub struct CryptoEngine { }
pub fn initialize_app() { }

// ❌ 品牌耦合
pub struct USafeCryptoEngine { }
pub fn u_safe_init() { }
```
