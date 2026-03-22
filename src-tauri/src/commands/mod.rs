mod file_scanner;
mod file_encryption;
mod file_operations;
mod tag_management;
mod auth;

pub use file_scanner::scan_file_tree;
pub use file_encryption::{encrypt_file, decrypt_file};
pub use file_operations::{delete_file, rename_file};
pub use tag_management::create_tag;
pub use auth::{is_master_key_set, derive_master_key, verify_password};
