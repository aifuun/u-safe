use rusqlite::{Connection, Result};

/// Run database migrations
pub fn run_migrations(conn: &Connection) -> Result<()> {
    // Check current schema version
    let current_version: i32 = conn
        .query_row(
            "SELECT value FROM config WHERE key = 'schema_version'",
            [],
            |row| row.get::<_, String>(0)
        )
        .unwrap_or_else(|_| "0".to_string())
        .parse()
        .unwrap_or(0);

    log::info!("[db:migrations] Current schema version: {}", current_version);

    // Apply migrations if needed
    if current_version < 1 {
        log::info!("[db:migrations] Applying migration 001...");
        // Schema is already initialized by schema::initialize_schema()
        // This is a no-op for version 1
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_migrations() {
        let conn = Connection::open_in_memory().unwrap();
        
        // Initialize schema first (simulates Database::new)
        crate::db::schema::initialize_schema(&conn).unwrap();
        
        // Run migrations
        let result = run_migrations(&conn);
        assert!(result.is_ok());

        // Verify schema version
        let version: String = conn
            .query_row(
                "SELECT value FROM config WHERE key = 'schema_version'",
                [],
                |row| row.get(0)
            )
            .unwrap();
        assert_eq!(version, "1");
    }
}
