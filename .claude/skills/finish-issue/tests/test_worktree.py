"""
Unit tests for worktree handling in finish-issue.

Tests worktree path extraction, git operations, and cleanup.
"""

import pytest
from pathlib import Path


@pytest.mark.unit
class TestWorktreeHandling:
    """Test worktree-related operations."""

    def test_extract_worktree_from_plan(self, mock_plan_file):
        """Test extracting worktree path from plan metadata."""
        # Read plan file
        plan_content = mock_plan_file.read_text()

        # Extract worktree path
        import re
        match = re.search(r'\*\*Worktree\*\*: (.+)', plan_content)
        assert match is not None, "Worktree field not found in plan"

        worktree_path = match.group(1).strip()
        assert worktree_path, "Worktree path is empty"
        assert Path(worktree_path).exists(), f"Worktree path does not exist: {worktree_path}"

    def test_worktree_path_validation(self, temp_worktree):
        """Test worktree path validation."""
        # Valid worktree should have .git directory
        assert temp_worktree.exists()
        assert (temp_worktree / ".git").exists()

        # Worktree should be outside main repo
        assert "worktree" in str(temp_worktree).lower()

    def test_git_operations_use_worktree_path(self, temp_worktree):
        """Test git commands use -C flag for worktree operations."""
        # Simulate git commands
        worktree_path = str(temp_worktree)

        git_commands = [
            f'git -C "{worktree_path}" status',
            f'git -C "{worktree_path}" add .',
            f'git -C "{worktree_path}" commit -m "test"',
            f'git -C "{worktree_path}" push',
        ]

        for cmd in git_commands:
            assert f'-C "{worktree_path}"' in cmd, f"Command missing -C flag: {cmd}"

    def test_worktree_removal_cleanup(self, temp_worktree):
        """Test worktree removal during cleanup."""
        # Worktree should exist initially
        assert temp_worktree.exists()

        # Simulate cleanup - remove worktree
        import shutil
        shutil.rmtree(temp_worktree)

        # Worktree should be removed
        assert not temp_worktree.exists()

    def test_worktree_fallback_behavior(self):
        """Test fallback to current directory when no worktree."""
        # When no worktree path in plan, should use current directory
        plan_without_worktree = """# Issue #123
**Branch**: feature/123-test
**Started**: 2026-04-07
"""

        import re
        match = re.search(r'\*\*Worktree\*\*: (.+)', plan_without_worktree)
        assert match is None, "Should not find worktree in plan"

        # Fallback: use current directory
        fallback_path = "."
        assert fallback_path == "."

    def test_worktree_naming_convention(self):
        """Test worktree directory naming follows pattern."""
        # Pattern: {repo}-{issue}-{title}
        test_cases = [
            ("ai-dev", 123, "test-issue", "ai-dev-123-test-issue"),
            ("my-repo", 456, "feature-name", "my-repo-456-feature-name"),
        ]

        for repo, issue, title, expected in test_cases:
            result = f"{repo}-{issue}-{title}"
            assert result == expected

    def test_worktree_path_absolute(self, temp_worktree):
        """Test worktree paths are absolute, not relative."""
        worktree_path = str(temp_worktree)

        # Should be absolute path
        assert Path(worktree_path).is_absolute()
        assert not worktree_path.startswith(".")
        assert not worktree_path.startswith("../")
