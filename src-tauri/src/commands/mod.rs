mod file_scanner;
mod file_encryption;
mod tag_management;

pub use file_scanner::scan_file_tree;
pub use file_encryption::{encrypt_file, decrypt_file};
pub use tag_management::{create_tag, update_tag};
