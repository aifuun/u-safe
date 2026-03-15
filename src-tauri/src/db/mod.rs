pub mod schema;
pub mod migrations;

use rusqlite::{Connection, Result};
use std::path::PathBuf;

/// Database connection manager
pub struct Database {
    conn: Connection,
}

impl Database {
    /// Initialize database at the specified path
    /// Creates the .u-safe directory if it doesn't exist
    pub fn new(db_path: PathBuf) -> Result<Self> {
        // Ensure parent directory exists
        if let Some(parent) = db_path.parent() {
            std::fs::create_dir_all(parent)
                .map_err(|e| rusqlite::Error::ToSqlConversionFailure(Box::new(e)))?;
        }

        // Open or create database
        let conn = Connection::open(&db_path)?;

        // Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON", [])?;

        // Initialize schema
        schema::initialize_schema(&conn)?;

        Ok(Self { conn })
    }

    /// Get database connection
    pub fn connection(&self) -> &Connection {
        &self.conn
    }

    /// Get mutable database connection
    pub fn connection_mut(&mut self) -> &mut Connection {
        &mut self.conn
    }
}

/// Get the default database path: .u-safe/u-safe.db
pub fn get_default_db_path() -> PathBuf {
    // Use USB detection to determine data directory
    let data_dir = crate::usb_detection::get_data_dir();
    data_dir.join("u-safe.db")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_database_creation() {
        let db_path = PathBuf::from("test.db");
        let db = Database::new(db_path.clone());
        assert!(db.is_ok());

        // Cleanup
        std::fs::remove_file(db_path).ok();
    }
}
