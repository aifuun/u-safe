use rusqlite::{Connection, Result};

/// Initialize database schema - creates all tables
pub fn initialize_schema(conn: &Connection) -> Result<()> {
    // Create files table
    conn.execute(
        "CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL UNIQUE,
            original_name TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            file_hash TEXT,
            encrypted_path TEXT,
            is_encrypted INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )",
        [],
    )?;

    // Create tags table
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            parent_id INTEGER,
            color TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (parent_id) REFERENCES tags(id) ON DELETE CASCADE
        )",
        [],
    )?;

    // Create file_tags junction table (many-to-many)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS file_tags (
            file_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (file_id, tag_id),
            FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )",
        [],
    )?;

    // Create encryption_meta table
    conn.execute(
        "CREATE TABLE IF NOT EXISTS encryption_meta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER NOT NULL UNIQUE,
            algorithm TEXT NOT NULL,
            salt BLOB NOT NULL,
            nonce BLOB NOT NULL,
            chunk_size INTEGER NOT NULL DEFAULT 65536,
            encrypted_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
        )",
        [],
    )?;

    // Create config table
    conn.execute(
        "CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )",
        [],
    )?;

    // Create indexes for performance
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_files_encrypted ON files(is_encrypted)",
        [],
    )?;

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_tags_parent ON tags(parent_id)",
        [],
    )?;

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_file_tags_file ON file_tags(file_id)",
        [],
    )?;

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_file_tags_tag ON file_tags(tag_id)",
        [],
    )?;

    // Insert schema version
    conn.execute(
        "INSERT OR REPLACE INTO config (key, value) VALUES ('schema_version', '1')",
        [],
    )?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use rusqlite::Connection;

    #[test]
    fn test_schema_initialization() {
        let conn = Connection::open_in_memory().unwrap();
        let result = initialize_schema(&conn);
        assert!(result.is_ok());

        // Verify tables exist
        let tables: Vec<String> = conn
            .prepare("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            .unwrap()
            .query_map([], |row| row.get(0))
            .unwrap()
            .collect::<Result<Vec<_>>>()
            .unwrap();

        assert!(tables.contains(&"files".to_string()));
        assert!(tables.contains(&"tags".to_string()));
        assert!(tables.contains(&"file_tags".to_string()));
        assert!(tables.contains(&"encryption_meta".to_string()));
        assert!(tables.contains(&"config".to_string()));
    }
}
