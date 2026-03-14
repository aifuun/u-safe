# ADR 0002: 技术栈选型决策

## TL;DR (For AI Context)

**Decision**: Tauri 2.0 + Rust + React 18 + TailwindCSS 3 + SQLite

**Key Metrics** (执行参考):
| Component | Choice | Size/Performance | Security Feature |
|-----------|--------|------------------|------------------|
| Desktop | Tauri 2.0 | 10 MB, <1s startup | Sandboxing, minimal permissions |
| Backend | Rust | 3-5x faster than Node.js | Memory safety (ownership system) |
| Frontend | React 18 + TailwindCSS | Mature ecosystem | Type-safe (TypeScript) |
| Database | SQLite + SQLCipher | Single file, zero-config | AES-256 encryption |

**Why** (核心理由):
1. **Security First**: Rust 消除内存漏洞 + Tauri 沙箱隔离（财务数据安全）
2. **Performance**: 启动 <1s，内存 ~50 MB（vs Electron 200+ MB）
3. **User Experience**: 10 MB 安装包（vs Electron 150 MB），低资源占用
4. **Developer Efficiency**: React 成熟生态 + Rust 类型安全 + SQLite 零配置

**Trade-offs**:
- 👍 安全性、性能、体积优势显著
- 👎 Rust 学习曲线 2-4 周，生态小于 Electron
- ⚖️ WebView 跨平台差异（Windows: Edge, macOS: Safari, Linux: WebKit）

**Rejected Alternatives**: Electron (安全/体积), Qt (开发效率), Flutter (桌面成熟度)

---

## Full Documentation (详细文档)

以下内容补充 TL;DR 中未涉及的背景分析和决策依据。

## Context

U-Safe 定位为本地优先的加密财务管理工具，核心挑战：
- 处理敏感财务数据（收入、支出、银行账户），安全是第一优先级
- 用户期望低资源占用（不希望财务工具占用大量内存）
- 需要跨平台支持（Windows/macOS/Linux）
- 开发团队更熟悉 Web 技术栈（TypeScript/React）

传统桌面框架的问题：
- **Electron**: 体积臃肿（150+ MB），安全风险（Node.js 集成带来 RCE 风险）
- **Qt**: C++ 内存管理复杂，开发效率低，Web 集成（Qt WebEngine）本质也是 Chromium
- **Flutter**: 桌面支持不成熟（2024 仍在 Beta），Dart 加密库生态弱

## Decision Details

选择 Tauri 而非 Electron 的决定性因素：
- **安全模型差异**: Tauri 前端无法直接访问系统 API，必须通过 Rust 后端（显式权限）；Electron 即使禁用 `nodeIntegration` 仍有 `contextBridge` 误用风险
- **体积差异根源**: Tauri 使用系统 WebView（无需捆绑 Chromium），Electron 捆绑完整 Chromium（~100 MB）
- **性能优势**: Rust 后端 + 系统 WebView 消除了 Node.js 运行时开销

选择 Rust 的关键考量：
- **内存安全保证**: 所有权系统在编译期防止缓冲区溢出、悬垂指针、数据竞争
- **加密库质量**: ring (Google BoringSSL), aes-gcm, argon2 都经过严格安全审计
- **性能**: AES-256-GCM 加密 100MB 文件 ~50ms（vs Node.js ~200ms）

SQLite 适配性分析：
- U-Safe 预计数据规模：每年 1-5 万条交易记录
- SQLite 性能瓶颈：~100 万条记录，远超需求
- SQLCipher 集成：通过 rusqlite，整个数据库文件 AES-256 加密

## Consequences

### Positive (TL;DR 中未详述的优势)
- **便携性**: SQLite 单文件，用户可轻松备份、迁移、同步（U 盘拷贝即可）
- **离线完整**: 无需数据库服务器，完全本地运行，无网络依赖
- **类型安全链**: TypeScript (前端) → Rust (后端) → SQLite (数据)，编译期捕获错误

### Negative (TL;DR 中未详述的挑战)
- **调试复杂度**: Rust 编译错误信息详细但冗长，新手需适应
- **依赖管理**: Cargo 在国内网络环境下较慢（可通过 USTC 镜像缓解）
- **跨平台构建**: 需要在 Windows/macOS/Linux 上分别构建（无法交叉编译）

### Neutral (实施考量)
- **学习投入**: 团队需投入 2-4 周学习 Rust，但长期收益（安全性、性能）明显
- **WebView 差异**: 需要在三个平台上测试 UI 一致性（Edge/Safari/WebKit 渲染差异）

## Alternatives Considered

### Alternative 1: Electron + Node.js
**不选原因**: 历史安全漏洞（CVE-2018-15685 RCE），威胁模型不符（财务数据泄露后果严重），体积大（150 MB 引起用户疑虑）

### Alternative 2: Qt + C++
**不选原因**: C++ 内存管理学习成本高，QML 构建 UI 效率低于 React，LGPL 许可证对商业化有限制

### Alternative 3: Flutter Desktop
**不选原因**: 桌面成熟度不足（2024 仍 Beta），Dart 加密库未经广泛审计

## References

- [Tauri Security Model](https://tauri.app/v1/references/architecture/security/)
- [Rust Memory Safety](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html)
- [SQLite Limits](https://www.sqlite.org/limits.html)
