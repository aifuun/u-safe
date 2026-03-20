# Database Schema - U-Safe

**版本**: v1.0
**状态**: 设计文档
**数据库**: SQLite 3.x
**日期**: 2026-03-09

---

## 概述

U-Safe 使用 SQLite 存储文件元数据、标签、加密信息和用户配置。数据库文件位于 U 盘根目录 `/.u-safe/metadata.db`（加密存储）。

**设计原则**：
1. **性能优先**：索引覆盖所有查询场景（标签搜索、文件查找）
2. **加密支持**：存储 ADR 0003 所需的所有加密元数据（Nonce、Salt、分块信息）
3. **完整性保证**：外键约束 + CHECK 约束确保数据一致性
4. **可扩展性**：支持未来功能（版本历史、分享链接）

---

## 表结构

### 1. files - 文件元数据表

存储 U 盘上所有被管理文件的元数据。

```sql
CREATE TABLE files (
    -- 主键
    file_id         TEXT PRIMARY KEY,           -- UUID v4 格式 (e.g., "f47ac10b-58cc-4372-a567-0e02b2c3d479")

    -- 文件路径
    relative_path   TEXT NOT NULL UNIQUE,       -- 相对于 U 盘根目录的路径 (e.g., "documents/report.pdf")
    file_name       TEXT NOT NULL,              -- 文件名 (e.g., "report.pdf")

    -- 文件属性
    file_size       INTEGER NOT NULL,           -- 原始文件大小（字节）
    mime_type       TEXT,                       -- MIME 类型 (e.g., "application/pdf")

    -- 加密状态
    is_encrypted    INTEGER NOT NULL DEFAULT 0, -- 0=未加密, 1=已加密
    encryption_version TEXT,                    -- 加密版本 (e.g., "v1", 用于未来升级)

    -- 时间戳
    created_at      TEXT NOT NULL,              -- ISO 8601 格式 (e.g., "2026-03-09T10:30:00Z")
    modified_at     TEXT NOT NULL,              -- ISO 8601 格式
    encrypted_at    TEXT,                       -- 加密时间（仅加密文件有值）

    -- 元数据
    file_hash       TEXT,                       -- SHA-256 哈希（原始文件，用于去重检测）
    notes           TEXT,                       -- 用户备注

    -- 约束
    CHECK (is_encrypted IN (0, 1)),
    CHECK (file_size >= 0),
    CHECK (length(file_id) = 36)                -- UUID 长度验证
);

-- 索引
CREATE INDEX idx_files_path ON files(relative_path);
CREATE INDEX idx_files_encrypted ON files(is_encrypted);
CREATE INDEX idx_files_created ON files(created_at DESC);
CREATE INDEX idx_files_hash ON files(file_hash) WHERE file_hash IS NOT NULL;

-- 全文搜索索引
CREATE VIRTUAL TABLE files_fts USING fts5(
    file_name,
    notes,
    content='files',
    content_rowid='rowid'
);
```

**字段说明**：
- `file_id`: UUID 主键，保证跨设备唯一性
- `relative_path`: 相对路径，支持跨平台（统一使用 `/` 分隔符）
- `is_encrypted`: 布尔值（SQLite 使用 INTEGER 0/1）
- `file_hash`: 用于检测重复文件和验证完整性

---

### 2. tags - 标签表

支持层级标签系统（如 "工作/项目A"）。

```sql
CREATE TABLE tags (
    -- 主键
    tag_id          TEXT PRIMARY KEY,           -- UUID v4

    -- 标签信息
    tag_name        TEXT NOT NULL,              -- 标签名称 (e.g., "工作")
    tag_color       TEXT,                       -- 颜色代码 (e.g., "#FF5733")

    -- 层级结构
    parent_tag_id   TEXT,                       -- 父标签 ID (NULL 表示根标签)
    tag_level       INTEGER NOT NULL DEFAULT 0, -- 层级深度 (0=根, 1=一级子标签...)
    full_path       TEXT NOT NULL,              -- 完整路径 (e.g., "工作/项目A/文档")

    -- 元数据
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    usage_count     INTEGER DEFAULT 0,          -- 使用次数（优化搜索排序）

    -- 约束
    FOREIGN KEY (parent_tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE,
    CHECK (tag_level >= 0),
    CHECK (length(tag_id) = 36),
    UNIQUE (full_path)                          -- 路径唯一
);

-- 索引
CREATE INDEX idx_tags_parent ON tags(parent_tag_id);
CREATE INDEX idx_tags_name ON tags(tag_name);
CREATE INDEX idx_tags_usage ON tags(usage_count DESC);

-- 全文搜索索引
CREATE VIRTUAL TABLE tags_fts USING fts5(
    tag_name,
    full_path,
    content='tags',
    content_rowid='rowid'
);
```

**字段说明**：
- `parent_tag_id`: 自引用外键，支持无限层级
- `full_path`: 冗余字段，加速路径查询（如 "工作/项目A"）
- `usage_count`: 统计字段，用于搜索时优先显示常用标签

**层级示例**：
```
工作 (tag_level=0, parent_tag_id=NULL)
└── 项目A (tag_level=1, parent_tag_id=工作的tag_id)
    └── 文档 (tag_level=2, parent_tag_id=项目A的tag_id)
```

---

### 3. file_tags - 文件-标签关联表

多对多关系：一个文件可以有多个标签，一个标签可以关联多个文件。

```sql
CREATE TABLE file_tags (
    -- 复合主键
    file_id         TEXT NOT NULL,
    tag_id          TEXT NOT NULL,

    -- 关联元数据
    tagged_at       TEXT NOT NULL,              -- 打标签时间
    tagged_by       TEXT,                       -- 操作来源 (e.g., "user", "auto-rule")

    -- 主键和外键
    PRIMARY KEY (file_id, tag_id),
    FOREIGN KEY (file_id) REFERENCES files(file_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_file_tags_file ON file_tags(file_id);
CREATE INDEX idx_file_tags_tag ON file_tags(tag_id);
CREATE INDEX idx_file_tags_time ON file_tags(tagged_at DESC);
```

**字段说明**：
- `PRIMARY KEY (file_id, tag_id)`: 保证同一文件不会被同一标签重复打标
- `ON DELETE CASCADE`: 删除文件或标签时自动清理关联

**查询示例**：
```sql
-- 查询文件的所有标签
SELECT t.* FROM tags t
JOIN file_tags ft ON t.tag_id = ft.tag_id
WHERE ft.file_id = 'f47ac10b-58cc-4372-a567-0e02b2c3d479';

-- 查询标签下的所有文件
SELECT f.* FROM files f
JOIN file_tags ft ON f.file_id = ft.file_id
WHERE ft.tag_id = 'tag-uuid-here';
```

---

### 4. encryption_meta - 加密元数据表

存储 AES-256-GCM 加密所需的元数据（基于 ADR 0003）。

```sql
CREATE TABLE encryption_meta (
    -- 主键（一对一关系）
    file_id         TEXT PRIMARY KEY,

    -- 加密算法
    algorithm       TEXT NOT NULL DEFAULT 'AES-256-GCM', -- 加密算法
    key_derivation  TEXT NOT NULL DEFAULT 'Argon2id',    -- KDF 算法

    -- 密钥派生参数（Argon2id）
    salt            BLOB NOT NULL,                       -- 32 bytes 随机盐
    kdf_memory      INTEGER NOT NULL DEFAULT 65536,     -- Argon2 内存参数 (64 MB)
    kdf_iterations  INTEGER NOT NULL DEFAULT 3,          -- Argon2 迭代次数
    kdf_parallelism INTEGER NOT NULL DEFAULT 1,          -- Argon2 并行度

    -- 分块信息（64KB per chunk）
    chunk_size      INTEGER NOT NULL DEFAULT 65536,     -- 分块大小 (64 KB)
    total_chunks    INTEGER NOT NULL,                   -- 总分块数

    -- Nonce 存储（每块一个 Nonce）
    nonce_list      BLOB NOT NULL,                      -- 连续存储的 Nonce (12 bytes * total_chunks)

    -- MAC 存储（每块一个 MAC）
    mac_list        BLOB NOT NULL,                      -- 连续存储的 MAC (16 bytes * total_chunks)

    -- 文件头信息
    header_version  TEXT NOT NULL DEFAULT 'v1',         -- 文件头版本
    encrypted_size  INTEGER NOT NULL,                   -- 加密后文件大小（字节）

    -- 时间戳
    encrypted_at    TEXT NOT NULL,

    -- 外键
    FOREIGN KEY (file_id) REFERENCES files(file_id) ON DELETE CASCADE,

    -- 约束
    CHECK (length(salt) = 32),
    CHECK (chunk_size = 65536),
    CHECK (total_chunks > 0),
    CHECK (length(nonce_list) = total_chunks * 12),
    CHECK (length(mac_list) = total_chunks * 16)
);

-- 索引
CREATE INDEX idx_encryption_algorithm ON encryption_meta(algorithm);
CREATE INDEX idx_encryption_time ON encryption_meta(encrypted_at DESC);
```

**字段说明**：
- `salt`: 32 bytes BLOB，用于 Argon2id 密钥派生
- `nonce_list`: 所有分块的 Nonce 连续存储（块 0 的 12 bytes + 块 1 的 12 bytes + ...）
- `mac_list`: 所有分块的 MAC 连续存储（块 0 的 16 bytes + 块 1 的 16 bytes + ...）
- `total_chunks`: 计算公式 = `CEIL(file_size / chunk_size)`

**存储示例**（100KB 文件）：
- `file_size`: 102,400 bytes
- `chunk_size`: 65,536 bytes (64 KB)
- `total_chunks`: 2 (块 0: 64KB, 块 1: 36.4KB)
- `nonce_list`: 24 bytes (12 * 2)
- `mac_list`: 32 bytes (16 * 2)

**Nonce/MAC 提取**：
```python
# 伪代码：提取第 i 块的 Nonce
chunk_index = i
nonce = nonce_list[chunk_index * 12 : (chunk_index + 1) * 12]

# 提取第 i 块的 MAC
mac = mac_list[chunk_index * 16 : (chunk_index + 1) * 16]
```

---

### 5. config - 配置表

Key-Value 存储，支持应用配置和用户偏好。

```sql
CREATE TABLE config (
    -- 主键
    config_key      TEXT PRIMARY KEY,           -- 配置键 (e.g., "theme", "language")

    -- 值和类型
    config_value    TEXT,                       -- 配置值（JSON 格式存储复杂对象）
    value_type      TEXT NOT NULL DEFAULT 'string', -- 值类型 (string, int, bool, json)

    -- 分类
    category        TEXT NOT NULL DEFAULT 'general', -- 配置分类 (general, ui, security)

    -- 元数据
    description     TEXT,                       -- 配置说明
    is_user_editable INTEGER NOT NULL DEFAULT 1, -- 是否用户可编辑 (0=系统配置, 1=用户配置)

    -- 时间戳
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL,

    -- 约束
    CHECK (value_type IN ('string', 'int', 'bool', 'json')),
    CHECK (is_user_editable IN (0, 1))
);

-- 索引
CREATE INDEX idx_config_category ON config(category);
CREATE INDEX idx_config_editable ON config(is_user_editable);
```

**字段说明**：
- `config_key`: 配置键，使用点分命名（如 `ui.theme.mode`）
- `config_value`: 所有值都存储为 TEXT，复杂对象用 JSON
- `value_type`: 类型提示，方便应用层解析
- `is_user_editable`: 区分系统配置和用户配置

**配置示例**：
```sql
INSERT INTO config (config_key, config_value, value_type, category, description) VALUES
('ui.theme.mode', 'dark', 'string', 'ui', '主题模式: light/dark/auto'),
('security.auto_lock_timeout', '300', 'int', 'security', '自动锁定超时（秒）'),
('ui.language', 'zh-CN', 'string', 'ui', '界面语言'),
('search.max_results', '100', 'int', 'general', '搜索最大结果数'),
('encryption.default_enabled', 'true', 'bool', 'security', '新文件默认加密');
```

---

## 数据库文件结构

```
U 盘根目录/
└── .u-safe/                    # 隐藏目录
    ├── metadata.db             # SQLite 数据库（加密存储）
    ├── metadata.db-shm         # SQLite 共享内存文件
    ├── metadata.db-wal         # SQLite Write-Ahead Log
    └── keys/                   # 密钥存储（Argon2id 派生后的主密钥）
        └── master.key.enc      # 加密的主密钥文件
```

---

## 索引策略

### 性能优化索引

| 索引名 | 表 | 字段 | 目的 |
|--------|------|------|------|
| `idx_files_path` | files | relative_path | 路径查询 |
| `idx_files_encrypted` | files | is_encrypted | 按加密状态筛选 |
| `idx_files_created` | files | created_at DESC | 按时间排序 |
| `idx_tags_parent` | tags | parent_tag_id | 层级查询 |
| `idx_file_tags_file` | file_tags | file_id | 查询文件的标签 |
| `idx_file_tags_tag` | file_tags | tag_id | 查询标签下的文件 |

### 全文搜索索引

使用 SQLite FTS5 (Full-Text Search) 扩展：

```sql
-- 文件名搜索
SELECT * FROM files WHERE file_id IN (
    SELECT rowid FROM files_fts WHERE files_fts MATCH '报告'
);

-- 标签搜索
SELECT * FROM tags WHERE tag_id IN (
    SELECT rowid FROM tags_fts WHERE tags_fts MATCH '工作'
);
```

---

## 数据完整性约束

### 外键约束

```sql
-- 启用外键支持（SQLite 默认关闭）
PRAGMA foreign_keys = ON;
```

| 子表 | 外键 | 父表 | 级联操作 |
|------|------|------|----------|
| file_tags | file_id | files(file_id) | CASCADE DELETE |
| file_tags | tag_id | tags(tag_id) | CASCADE DELETE |
| tags | parent_tag_id | tags(tag_id) | CASCADE DELETE |
| encryption_meta | file_id | files(file_id) | CASCADE DELETE |

### CHECK 约束

- `files.is_encrypted IN (0, 1)` - 布尔值验证
- `files.file_size >= 0` - 文件大小非负
- `tags.tag_level >= 0` - 标签层级非负
- `encryption_meta.chunk_size = 65536` - 强制 64KB 分块
- `encryption_meta.length(salt) = 32` - Salt 固定 32 bytes

---

## 迁移策略

### Schema 版本管理

在 `config` 表存储 Schema 版本：

```sql
INSERT INTO config (config_key, config_value, value_type, category, is_user_editable)
VALUES ('schema.version', '1', 'int', 'system', 0);
```

### 未来升级路径

**版本 2.0 可能的改动**：
- 添加 `file_versions` 表（文件历史版本）
- 添加 `sharing_links` 表（分享链接）
- 扩展 `encryption_meta` 支持新算法（如量子安全加密）

**迁移脚本示例**：
```sql
-- V1 to V2 Migration
BEGIN TRANSACTION;

-- 添加新表
CREATE TABLE file_versions (...);

-- 更新 schema 版本
UPDATE config SET config_value = '2' WHERE config_key = 'schema.version';

COMMIT;
```

---

## 示例 SQL 查询

### 查询 1: 获取所有加密文件及其标签

```sql
SELECT
    f.file_id,
    f.file_name,
    f.relative_path,
    GROUP_CONCAT(t.tag_name, ', ') AS tags
FROM files f
LEFT JOIN file_tags ft ON f.file_id = ft.file_id
LEFT JOIN tags t ON ft.tag_id = t.tag_id
WHERE f.is_encrypted = 1
GROUP BY f.file_id
ORDER BY f.created_at DESC;
```

### 查询 2: 统计各标签下的文件数量

```sql
SELECT
    t.tag_name,
    t.full_path,
    COUNT(ft.file_id) AS file_count
FROM tags t
LEFT JOIN file_tags ft ON t.tag_id = ft.tag_id
GROUP BY t.tag_id
ORDER BY file_count DESC;
```

### 查询 3: 查找大于 10MB 的未加密文件

```sql
SELECT
    file_id,
    file_name,
    file_size,
    relative_path
FROM files
WHERE is_encrypted = 0
  AND file_size > 10485760  -- 10 MB in bytes
ORDER BY file_size DESC;
```

### 查询 4: 搜索文件名包含 "报告" 的文件

```sql
SELECT f.* FROM files f
WHERE f.file_id IN (
    SELECT rowid FROM files_fts
    WHERE files_fts MATCH '报告'
)
ORDER BY f.created_at DESC;
```

### 查询 5: 获取加密文件的完整元数据

```sql
SELECT
    f.file_id,
    f.file_name,
    f.file_size,
    e.algorithm,
    e.total_chunks,
    e.encrypted_size,
    e.encrypted_at
FROM files f
JOIN encryption_meta e ON f.file_id = e.file_id
WHERE f.is_encrypted = 1;
```

---

## 性能考虑

### 1. 索引覆盖率

所有常用查询场景都有索引支持：
- ✅ 按路径查找文件
- ✅ 按加密状态筛选
- ✅ 按时间排序
- ✅ 标签层级查询
- ✅ 文件-标签关联查询

### 2. 查询优化

**使用 EXPLAIN QUERY PLAN 验证索引使用**：

```sql
EXPLAIN QUERY PLAN
SELECT * FROM files WHERE is_encrypted = 1;
-- 应该显示: SEARCH files USING INDEX idx_files_encrypted (is_encrypted=?)
```

### 3. 数据库大小估算

假设管理 10,000 个文件：

| 表 | 平均行大小 | 行数 | 估算大小 |
|------|-----------|------|----------|
| files | ~300 bytes | 10,000 | ~3 MB |
| tags | ~150 bytes | 500 | ~75 KB |
| file_tags | ~100 bytes | 30,000 | ~3 MB |
| encryption_meta | ~1 KB | 5,000 | ~5 MB |
| config | ~200 bytes | 50 | ~10 KB |
| **总计** | | | **~11 MB** |

**结论**: 数据库文件大小适中，适合 U 盘存储。

---

## 安全考虑

### 1. 数据库加密

整个 `metadata.db` 文件使用 AES-256-GCM 加密（基于 ADR 0003）：
- 密钥派生：用户密码 → Argon2id → 数据库密钥
- 存储：`.u-safe/metadata.db.enc`（加密后的数据库）
- 解密：应用启动时，用户输入密码解密到内存

### 2. 敏感字段保护

- `encryption_meta.salt`: 每个文件独立的 Salt
- `encryption_meta.nonce_list`: 每个分块独立的 Nonce
- `config` 表中的密码类配置：使用 Argon2id 哈希存储

### 3. SQL 注入防护

使用参数化查询（Prepared Statements）：

```rust
// Rust 示例（使用 rusqlite）
let stmt = conn.prepare("SELECT * FROM files WHERE file_id = ?1")?;
let file = stmt.query_row([file_id], |row| {
    Ok(File {
        file_id: row.get(0)?,
        file_name: row.get(1)?,
        // ...
    })
})?;
```

---

## 实现清单

### Rust 数据结构映射

```rust
// files 表
#[derive(Debug, Clone)]
pub struct File {
    pub file_id: String,           // UUID
    pub relative_path: String,
    pub file_name: String,
    pub file_size: i64,
    pub mime_type: Option<String>,
    pub is_encrypted: bool,
    pub encryption_version: Option<String>,
    pub created_at: String,        // ISO 8601
    pub modified_at: String,
    pub encrypted_at: Option<String>,
    pub file_hash: Option<String>,
    pub notes: Option<String>,
}

// tags 表
#[derive(Debug, Clone)]
pub struct Tag {
    pub tag_id: String,
    pub tag_name: String,
    pub tag_color: Option<String>,
    pub parent_tag_id: Option<String>,
    pub tag_level: i32,
    pub full_path: String,
    pub created_at: String,
    pub updated_at: String,
    pub usage_count: i32,
}

// encryption_meta 表
#[derive(Debug, Clone)]
pub struct EncryptionMeta {
    pub file_id: String,
    pub algorithm: String,
    pub key_derivation: String,
    pub salt: Vec<u8>,             // 32 bytes
    pub kdf_memory: i32,
    pub kdf_iterations: i32,
    pub kdf_parallelism: i32,
    pub chunk_size: i32,
    pub total_chunks: i32,
    pub nonce_list: Vec<u8>,       // 12 * total_chunks bytes
    pub mac_list: Vec<u8>,         // 16 * total_chunks bytes
    pub header_version: String,
    pub encrypted_size: i64,
    pub encrypted_at: String,
}
```

### 数据库初始化脚本

```rust
// 创建所有表
pub fn initialize_database(conn: &Connection) -> Result<()> {
    // 启用外键
    conn.execute("PRAGMA foreign_keys = ON", [])?;

    // 创建 files 表
    conn.execute(include_str!("../sql/create_files.sql"), [])?;

    // 创建 tags 表
    conn.execute(include_str!("../sql/create_tags.sql"), [])?;

    // 创建 file_tags 表
    conn.execute(include_str!("../sql/create_file_tags.sql"), [])?;

    // 创建 encryption_meta 表
    conn.execute(include_str!("../sql/create_encryption_meta.sql"), [])?;

    // 创建 config 表
    conn.execute(include_str!("../sql/create_config.sql"), [])?;

    // 创建索引
    conn.execute(include_str!("../sql/create_indexes.sql"), [])?;

    // 创建全文搜索表
    conn.execute(include_str!("../sql/create_fts.sql"), [])?;

    // 插入默认配置
    conn.execute(include_str!("../sql/insert_default_config.sql"), [])?;

    Ok(())
}
```

---

## 参考资料

- **ADR 003**: 技术栈选型 (`docs/ADRs/003-technical-stack.md`)
- **ADR 004**: 加密方案选型 (`docs/ADRs/004-encryption-strategy.md`)
- **PRD**: 产品需求文档 (`docs/prd/PRD.md`)
- **SQLite 文档**: https://www.sqlite.org/docs.html
- **SQLite FTS5**: https://www.sqlite.org/fts5.html
- **rusqlite**: https://docs.rs/rusqlite/

---

**版本历史**:
- v1.0 (2026-03-09): 初始设计，包含 5 个核心表
