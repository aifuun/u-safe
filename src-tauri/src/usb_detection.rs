use std::path::PathBuf;
use std::env;

/// Detect if running from USB drive
pub fn is_running_from_usb() -> bool {
    // For MVP, return false (run from local directory)
    // In production, check if current_dir() is on removable media
    false
}

/// Get USB root directory
/// Returns None if not running from USB
pub fn get_usb_root() -> Option<PathBuf> {
    if !is_running_from_usb() {
        return None;
    }

    // For now, return current directory
    // In production, return the mount point of the USB drive
    env::current_dir().ok()
}

/// Get data directory (.u-safe/)
/// Returns USB root if on USB, otherwise local directory
pub fn get_data_dir() -> PathBuf {
    if let Some(usb_root) = get_usb_root() {
        // USB mode: .u-safe in USB root
        usb_root.join(".u-safe")
    } else {
        // Local mode: .u-safe in current directory (development)
        PathBuf::from(".u-safe")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_running_from_usb() {
        // In MVP, always returns false
        assert!(!is_running_from_usb());
    }

    #[test]
    fn test_get_data_dir() {
        let data_dir = get_data_dir();
        assert!(data_dir.ends_with(".u-safe"));
    }
}
