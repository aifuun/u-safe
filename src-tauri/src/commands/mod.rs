mod file_scanner;
mod file_encryption;
mod tag_management;

pub use file_scanner::scan_file_tree;
pub use file_encryption::{encrypt_file, decrypt_file};
pub use tag_management::{
    create_tag, update_tag, get_tag_tree, delete_tag, get_tag_info,
    add_tag_to_file, remove_tag_from_file,
    add_tags_to_file, remove_tags_from_file,
    get_file_tags, get_tag_files, search_files,
    get_all_files, get_encrypted_files, get_recent_files,
    // Phase 6: Extensions
    bulk_add_tags, bulk_remove_tags, bulk_delete_tags,
    export_tags, import_tags, get_tag_statistics
};
