# U-Safe (万能保险箱)

一款专为 U 盘用户设计的轻量化管理工具，集成军事级文件加密与非侵入式标签整理功能。

## 特性

- 🔒 **军事级加密**: AES-256-GCM 认证加密
- 🏷️ **虚拟标签**: 不改变物理路径的智能整理
- 🚀 **无需提权**: 完全用户态运行，无需管理员权限
- 🔄 **跨平台**: 支持 Windows 10/11 和 macOS (Intel/Apple Silicon)
- ⚡ **原生体验**: 基于 Tauri + Rust，性能卓越

## 技术栈

- **后端**: Rust
- **前端**: React + TailwindCSS
- **框架**: Tauri
- **数据库**: SQLite

## 文档

📘 **[完整文档索引](./docs/README.md)** - 查看所有项目文档

**快速链接**:
- [产品需求文档 (PRD)](./docs/product/PRD.md)
- [数据库设计](./docs/arch/SCHEMA.md)
- [系统架构](./docs/arch/ARCHITECTURE.md)
- [UI/UX 设计系统](./docs/design/UI_UX_DESIGN.md)
- [产品路线图](./docs/product/roadmap.md)
- [开发环境搭建](./docs/dev/SETUP.md)
- [架构决策记录 (ADRs)](./docs/adr/)

## 数据存储

U-Safe 的所有数据统一存储在 `.u-safe/` 目录下：

```
.u-safe/
├── u-safe.db              # 数据库（标签、文件索引）
├── keys/                  # 密钥存储
│   ├── password.hash      # 密码哈希
│   └── master.key         # 加密的主密钥
└── logs/                  # 应用日志（未来）
```

### 数据位置

- **开发环境**: `./u-safe/`（项目根目录）
- **生产环境**: U 盘根目录的 `.u-safe/`（例如 `/Volumes/USB_NAME/.u-safe/`）

### 备份建议

⚠️ **重要提示**：

1. **密码安全**：请设置强密码（至少 8 字符，包含大小写字母、数字）
2. **备份数据**：定期备份 `.u-safe/` 目录到安全位置
3. **U 盘加密**：建议启用 U 盘硬件加密（如 BitLocker）作为额外防护
4. **密码管理**：请妥善保管密码，密码丢失将无法恢复数据

### 数据迁移

如果你从旧版本升级，应用会自动检测并迁移数据：

- 旧位置: `~/Library/Application Support/.u-safe/` (macOS)
- 新位置: `./.u-safe/`（当前目录）

迁移完成后，旧数据会保留，你可以手动删除。

## 开发状态

🚧 项目正在开发中...

## License

TBD
