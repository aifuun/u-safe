"""
Safety mechanism tests for update-framework skill.

Tests security features and protection mechanisms.
Following ADR-020 standards.
"""

import os
import stat
from pathlib import Path
from typing import Callable

import pytest


@pytest.mark.safety
def test_path_traversal_prevention(tmp_path: Path):
    """Test protection against path traversal attacks.

    Prevents attempts to write outside target directory using ../

    Arrange:
        - Malicious path with ../ sequences
    Act:
        - Attempt to resolve and validate path
    Assert:
        - Path traversal detected and blocked
        - Error message indicates security violation
    """
    target_dir = tmp_path / "project"
    target_dir.mkdir()

    malicious_paths = [
        "../../../etc/passwd",
        "../../escape/attack",
        "./../outside/target"
    ]

    def safe_resolve(base: Path, relative_path: str) -> Path:
        """Safely resolve path and ensure it's within base directory."""
        resolved = (base / relative_path).resolve()

        # Check if resolved path is within base directory
        try:
            resolved.relative_to(base.resolve())
        except ValueError:
            raise ValueError(
                f"Path traversal detected: {relative_path} "
                f"resolves outside target directory"
            )

        return resolved

    # Test each malicious path
    for malicious_path in malicious_paths:
        with pytest.raises(ValueError, match="Path traversal detected"):
            safe_resolve(target_dir, malicious_path)


@pytest.mark.safety
def test_symlink_handling(tmp_path: Path):
    """Test proper handling of symbolic links during sync.

    Symlinks should either be:
    1. Followed and content copied (safer)
    2. Blocked entirely (most secure)

    This test verifies symlinks don't cause unintended behavior.

    Arrange:
        - Framework with symlink to external file
        - Target project directory
    Act:
        - Attempt sync with symlink
    Assert:
        - Symlink handled safely (not followed outside framework)
        - No security violation
    """
    framework = tmp_path / "ai-dev"
    framework.mkdir()
    (framework / ".claude/pillars").mkdir(parents=True)

    # Create symlink to file outside framework
    external_file = tmp_path / "external-sensitive.txt"
    external_file.write_text("Sensitive data")

    symlink = framework / ".claude/pillars/link.md"

    # Create symlink (Unix-like systems)
    try:
        symlink.symlink_to(external_file)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks not supported on this system")

    # Function to detect and handle symlinks
    def is_safe_symlink(path: Path, base_dir: Path) -> bool:
        """Check if symlink is safe to follow."""
        if not path.is_symlink():
            return True

        # Resolve symlink target
        target = path.resolve()

        # Ensure target is within base directory
        try:
            target.relative_to(base_dir.resolve())
            return True
        except ValueError:
            # Symlink points outside framework
            return False

    # Verify symlink detected as unsafe
    assert symlink.is_symlink()
    assert not is_safe_symlink(symlink, framework)


@pytest.mark.safety
def test_permission_validation(tmp_path: Path):
    """Test validation of directory permissions before sync.

    Ensures target directory is writable before attempting sync.

    Arrange:
        - Target directory with read-only permissions
    Act:
        - Attempt to validate write permissions
    Assert:
        - Permission error detected
        - Clear error message provided
    """
    target_dir = tmp_path / "readonly-project"
    target_dir.mkdir()

    # Make directory read-only (Unix-like systems)
    try:
        target_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)  # r-x------

        def validate_writable(path: Path) -> None:
            """Check if directory is writable."""
            if not os.access(path, os.W_OK):
                raise PermissionError(
                    f"Target directory not writable: {path}\n"
                    f"Check permissions with: ls -ld {path}"
                )

        with pytest.raises(PermissionError, match="not writable"):
            validate_writable(target_dir)

    finally:
        # Restore write permissions for cleanup
        target_dir.chmod(stat.S_IRWXU)  # rwx------


@pytest.mark.safety
def test_disk_space_check(tmp_path: Path):
    """Test pre-sync disk space validation.

    Verifies adequate disk space before starting large sync operation.

    Arrange:
        - Simulated low disk space condition
    Act:
        - Check disk space availability
    Assert:
        - Warning or error if space insufficient
    """
    import shutil

    def check_disk_space(path: Path, required_mb: int = 100) -> bool:
        """Check if path has sufficient disk space.

        Args:
            path: Directory to check
            required_mb: Minimum required space in MB

        Returns:
            True if sufficient space available

        Raises:
            RuntimeError: If insufficient disk space
        """
        stat_result = shutil.disk_usage(path)
        available_mb = stat_result.free / (1024 * 1024)

        if available_mb < required_mb:
            raise RuntimeError(
                f"Insufficient disk space: {available_mb:.1f}MB available, "
                f"{required_mb}MB required"
            )

        return True

    # Test with current directory (should have space)
    assert check_disk_space(tmp_path, required_mb=1)  # Only need 1MB for test

    # Test with unrealistic requirement (should fail on most systems)
    with pytest.raises(RuntimeError, match="Insufficient disk space"):
        check_disk_space(tmp_path, required_mb=999999999)  # 1PB


@pytest.mark.safety
def test_backup_integrity(tmp_path: Path):
    """Test backup integrity verification.

    Ensures backups are complete and uncorrupted before replacing original.

    Arrange:
        - Original files to backup
        - Backup operation
    Act:
        - Create backup
        - Verify backup integrity
    Assert:
        - Backup contains all original files
        - Backup file content matches original
    """
    import hashlib

    project = tmp_path / "project"
    (project / ".claude/pillars").mkdir(parents=True)

    # Create original files
    original_files = {
        "pillar-1.md": "# Pillar 1 Content",
        "pillar-2.md": "# Pillar 2 Content",
        "pillar-3.md": "# Pillar 3 Content"
    }

    for filename, content in original_files.items():
        (project / ".claude/pillars" / filename).write_text(content)

    # Function to create and verify backup
    def create_verified_backup(source: Path, backup: Path) -> bool:
        """Create backup and verify integrity.

        Args:
            source: Source directory
            backup: Backup directory

        Returns:
            True if backup verified successfully

        Raises:
            RuntimeError: If backup integrity check fails
        """
        import shutil

        # Create backup
        shutil.copytree(source, backup)

        # Verify file count matches
        source_files = set(f.name for f in source.iterdir())
        backup_files = set(f.name for f in backup.iterdir())

        if source_files != backup_files:
            raise RuntimeError(
                f"Backup incomplete: missing {source_files - backup_files}"
            )

        # Verify content matches (hash comparison)
        for source_file in source.iterdir():
            backup_file = backup / source_file.name

            source_hash = hashlib.md5(source_file.read_bytes()).hexdigest()
            backup_hash = hashlib.md5(backup_file.read_bytes()).hexdigest()

            if source_hash != backup_hash:
                raise RuntimeError(
                    f"Backup corrupted: {source_file.name} hash mismatch"
                )

        return True

    # Create backup
    backup_dir = tmp_path / "backup-pillars"
    assert create_verified_backup(
        project / ".claude/pillars",
        backup_dir
    )

    # Verify backup integrity
    assert len(list(backup_dir.iterdir())) == 3
    assert (backup_dir / "pillar-1.md").read_text() == "# Pillar 1 Content"
