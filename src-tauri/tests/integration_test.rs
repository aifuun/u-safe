use u_safe_lib::db::{Database, get_default_db_path};

#[test]
fn test_database_integration() {
    // Test database creation and initialization
    let db_path = get_default_db_path();
    
    // Clean up any existing test database
    if db_path.exists() {
        std::fs::remove_file(&db_path).ok();
    }
    if let Some(parent) = db_path.parent() {
        if parent.exists() {
            std::fs::remove_dir_all(parent).ok();
        }
    }

    // Create new database
    let db = Database::new(db_path.clone()).unwrap();

    // Verify schema is initialized
    let version: String = db.connection()
        .query_row(
            "SELECT value FROM config WHERE key = 'schema_version'",
            [],
            |row| row.get(0)
        )
        .unwrap();
    
    assert_eq!(version, "1");

    // Verify all tables exist
    let table_count: i32 = db.connection()
        .query_row(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table'",
            [],
            |row| row.get(0)
        )
        .unwrap();
    
    assert!(table_count >= 5, "Expected at least 5 tables, got {}", table_count);

    // Clean up
    std::fs::remove_file(db_path).ok();
}
