mod file_scanner;
mod file_encryption;
mod tag_management;

pub use file_scanner::scan_file_tree;
pub use file_encryption::{encrypt_file, decrypt_file};
pub use tag_management::{
    create_tag, update_tag, get_tag_tree, delete_tag, get_tag_info,
    add_tag_to_file, remove_tag_from_file,
    add_tags_to_file, remove_tags_from_file,
    get_file_tags, get_tag_files
};
