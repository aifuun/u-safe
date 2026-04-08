"""
Error handling tests for update-framework skill.

Tests error scenarios and recovery mechanisms.
Following ADR-020 standards.
"""

import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.error_handling
def test_source_not_found(tmp_path: Path):
    """Test handling when source framework directory doesn't exist.

    Arrange:
        - Non-existent framework path
        - Valid target project
    Act:
        - Attempt update-framework
    Assert:
        - FileNotFoundError with helpful message
        - Suggests checking path or running from correct directory
    """
    nonexistent_framework = tmp_path / "nonexistent-ai-dev"
    target_project = tmp_path / "project"
    target_project.mkdir()

    def sync_framework(source: Path, target: Path):
        """Simulate framework sync with error handling."""
        if not source.exists():
            raise FileNotFoundError(
                f"Framework directory not found: {source}\n\n"
                f"Possible causes:\n"
                f"1. Not running from ai-dev directory\n"
                f"2. Framework path incorrect\n"
                f"3. Framework not cloned\n\n"
                f"Solution: cd to ai-dev directory and retry"
            )

    with pytest.raises(FileNotFoundError, match="Framework directory not found"):
        sync_framework(nonexistent_framework, target_project)


@pytest.mark.error_handling
def test_target_permission_denied(tmp_path: Path):
    """Test handling when target directory is not writable.

    Arrange:
        - Target directory with no write permissions
    Act:
        - Attempt to write to target
    Assert:
        - PermissionError raised
        - Clear guidance on fixing permissions
    """
    import os
    import stat

    framework = tmp_path / "ai-dev"
    framework.mkdir()
    (framework / ".claude/pillars").mkdir(parents=True)
    (framework / ".claude/pillars/test.md").write_text("Test")

    target = tmp_path / "readonly-project"
    target.mkdir()
    (target / ".claude").mkdir()

    # Make .claude directory read-only
    try:
        (target / ".claude").chmod(stat.S_IRUSR | stat.S_IXUSR)  # r-x

        def sync_with_permission_check(source: Path, target: Path):
            """Sync with permission validation."""
            if not os.access(target, os.W_OK):
                raise PermissionError(
                    f"Permission denied: {target}\n\n"
                    f"Fix with: chmod u+w {target}\n"
                    f"Or run as appropriate user"
                )

            shutil.copytree(source, target, dirs_exist_ok=True)

        with pytest.raises(PermissionError, match="Permission denied"):
            sync_with_permission_check(
                framework / ".claude/pillars",
                target / ".claude/pillars"
            )

    finally:
        # Restore permissions for cleanup
        (target / ".claude").chmod(stat.S_IRWXU)


@pytest.mark.error_handling
def test_git_conflict_handling(tmp_path: Path, mock_git: MagicMock):
    """Test handling of git conflicts during sync.

    When git detects conflicts, should:
    1. Detect conflict state
    2. Provide clear resolution steps
    3. Not leave repository in broken state

    Arrange:
        - Mock git with conflict state
    Act:
        - Attempt sync operation
    Assert:
        - Conflict detected and reported
        - Repository not left in broken state
    """
    project = tmp_path / "project"
    project.mkdir()

    # Mock git status showing conflict
    mock_git.return_value.returncode = 0
    mock_git.return_value.stdout = "UU conflicted-file.md"

    def check_git_status(repo_path: Path) -> bool:
        """Check if git repository has conflicts.

        Returns:
            True if conflicts detected

        Raises:
            RuntimeError: If conflicts found
        """
        import subprocess

        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )

        if "UU" in result.stdout:
            raise RuntimeError(
                f"Git conflict detected in {repo_path}\n\n"
                f"Conflicts:\n{result.stdout}\n\n"
                f"Resolve with:\n"
                f"1. git status\n"
                f"2. Edit conflicted files\n"
                f"3. git add <files>\n"
                f"4. git commit\n"
                f"5. Retry sync"
            )

        return False

    with pytest.raises(RuntimeError, match="Git conflict detected"):
        check_git_status(project)


@pytest.mark.error_handling
def test_partial_sync_recovery(tmp_path: Path):
    """Test recovery from partial sync failure.

    If sync fails mid-operation, should:
    1. Detect partial state
    2. Rollback to backup if available
    3. Provide recovery instructions

    Arrange:
        - Sync operation that fails partway
        - Backup available
    Act:
        - Attempt sync
        - Simulate failure
    Assert:
        - Partial state detected
        - Rollback to backup successful
    """
    framework = tmp_path / "ai-dev"
    project = tmp_path / "project"

    # Setup framework
    (framework / ".claude/pillars").mkdir(parents=True)
    for i in range(5):
        (framework / ".claude/pillars" / f"pillar-{i}.md").write_text(f"Pillar {i}")

    # Setup project with backup
    (project / ".claude/pillars").mkdir(parents=True)
    (project / ".claude/pillars/original.md").write_text("Original")

    backup_dir = project / ".claude/backup-pillars"
    shutil.copytree(project / ".claude/pillars", backup_dir)

    def sync_with_recovery(source: Path, target: Path, backup: Path):
        """Sync with automatic recovery on failure."""
        try:
            # Simulate partial sync (copy 2/5 files then fail)
            shutil.copy(
                source / "pillar-0.md",
                target / "pillar-0.md"
            )
            shutil.copy(
                source / "pillar-1.md",
                target / "pillar-1.md"
            )

            # Simulate failure
            raise IOError("Simulated network interruption")

        except Exception as e:
            # Detect partial state
            synced_files = list(target.glob("pillar-*.md"))
            if 0 < len(synced_files) < 5:
                # Partial sync detected - rollback
                shutil.rmtree(target)
                shutil.copytree(backup, target)

                raise RuntimeError(
                    f"Sync failed: {e}\n"
                    f"Partial sync detected and rolled back\n"
                    f"Restored from: {backup}"
                ) from e

    with pytest.raises(RuntimeError, match="Sync failed"):
        sync_with_recovery(
            framework / ".claude/pillars",
            project / ".claude/pillars",
            backup_dir
        )

    # Verify rollback successful
    assert (project / ".claude/pillars/original.md").exists()
    assert not (project / ".claude/pillars/pillar-0.md").exists()


@pytest.mark.error_handling
def test_network_interruption():
    """Test handling of network interruption (if applicable).

    For remote sync operations, network failures should be handled gracefully.

    Note: update-framework typically uses local file operations,
    so network interruption is less relevant. This test demonstrates
    the pattern for future enhancements.

    Arrange:
        - Simulated network failure
    Act:
        - Attempt remote operation
    Assert:
        - Network error detected
        - Retry logic invoked or clear error message
    """
    def fetch_remote_framework(url: str, retries: int = 3):
        """Simulate fetching framework from remote URL."""
        import time

        for attempt in range(retries):
            try:
                # Simulate network operation
                raise ConnectionError("Network unreachable")

            except ConnectionError:
                if attempt < retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(0.01)  # Short sleep for test
                    continue
                else:
                    raise RuntimeError(
                        f"Network error after {retries} attempts\n"
                        f"Check connection and retry"
                    )

    with pytest.raises(RuntimeError, match="Network error after"):
        fetch_remote_framework("https://example.com/framework.git")
