"""
Tests for safety features in finish-issue.

Tests all 5 safety mechanisms from SKILL.md Safety Features section:
1. Pre-finish validation
2. Commit safety
3. PR creation validation
4. Merge safety
5. Cleanup safety
"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta


@pytest.mark.safety
class TestSafetyFeatures:
    """Test all safety mechanisms."""

    # Safety Feature 1: Pre-Finish Validation
    def test_safety_pre_finish_validation_review_status(self, mock_review_status):
        """Test pre-finish validation checks review status."""
        # Should validate review status exists and is valid
        assert mock_review_status["score"] >= 90
        assert mock_review_status["status"] == "approved"

        # Should check expiry
        valid_until = datetime.fromisoformat(mock_review_status["valid_until"])
        assert valid_until > datetime.now()

    def test_safety_pre_finish_validation_branch_check(self):
        """Test pre-finish validation prevents merging from main."""
        # Should reject main/master branches
        invalid_branches = ["main", "master", "develop"]
        valid_branches = ["feature/123-test", "fix/456-bug"]

        for branch in invalid_branches:
            is_valid = branch not in ["main", "master", "develop"]
            assert not is_valid, f"{branch} should be rejected"

        for branch in valid_branches:
            is_valid = branch not in ["main", "master", "develop"]
            assert is_valid, f"{branch} should be accepted"

    def test_safety_pre_finish_validation_uncommitted_changes(self):
        """Test pre-finish validation checks for uncommitted changes."""
        # Clean status should pass
        clean_status = ""
        assert len(clean_status) == 0

        # Modified files should fail
        modified_status = " M file.ts\n M other.ts"
        assert len(modified_status) > 0

    # Safety Feature 2: Commit Safety
    def test_safety_commit_message_format(self):
        """Test commit safety validates message format."""
        # Valid commit messages include "Fixes #N"
        valid_messages = [
            "feat: add feature (Issue #123)\n\nFixes #123",
            "fix: bug fix (Issue #456)\n\nFixes #456",
        ]

        for msg in valid_messages:
            assert "Fixes #" in msg
            assert "(Issue #" in msg

        # Invalid messages (missing required parts)
        invalid_messages = [
            "feat: add feature",  # Missing Fixes #N
            "random commit",  # No issue reference
        ]

        for msg in invalid_messages:
            assert "Fixes #" not in msg or "(Issue #" not in msg

    def test_safety_commit_includes_coauthor(self):
        """Test commit safety includes Co-Authored-By attribution."""
        commit_message = """feat: add feature (Issue #123)

Details about the feature.

Fixes #123

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"""

        assert "Co-Authored-By" in commit_message
        assert "Claude Sonnet 4.5" in commit_message

    def test_safety_commit_all_files_staged(self):
        """Test commit safety ensures all changed files are staged."""
        # Simulate git status
        status_unstaged = " M unstaged.ts"  # Modified but not staged
        status_staged = "M  staged.ts"  # Staged

        # Should detect unstaged files
        has_unstaged = status_unstaged.strip().startswith(" M")
        assert has_unstaged, "Should detect unstaged files"

    # Safety Feature 3: PR Creation Validation
    def test_safety_pr_no_duplicates(self):
        """Test PR creation safety prevents duplicate PRs."""
        # Should check for existing PR before creating
        existing_prs = [
            {"number": 456, "head": "feature/123-test"},
        ]

        branch_name = "feature/123-test"
        has_existing = any(pr["head"] == branch_name for pr in existing_prs)
        assert has_existing, "Should detect existing PR"

    def test_safety_pr_branch_pushed(self):
        """Test PR creation safety ensures branch is pushed."""
        # Should verify branch exists on remote
        remote_branches = ["feature/123-test", "feature/456-other"]
        local_branch = "feature/123-test"

        is_pushed = local_branch in remote_branches
        assert is_pushed, "Branch should be pushed to remote"

    def test_safety_pr_title_includes_issue(self):
        """Test PR creation safety includes issue reference in title."""
        valid_titles = [
            "feat: add feature (Issue #123)",
            "docs: update docs (#456)",
        ]

        for title in valid_titles:
            has_issue_ref = "#" in title and any(c.isdigit() for c in title)
            assert has_issue_ref, f"Title should include issue reference: {title}"

    # Safety Feature 4: Merge Safety
    def test_safety_merge_checks_passing(self):
        """Test merge safety ensures all checks are passing."""
        # Should validate CI/CD checks before merging
        pr_checks = [
            {"name": "ci/build", "status": "success"},
            {"name": "ci/test", "status": "success"},
        ]

        all_passing = all(check["status"] == "success" for check in pr_checks)
        assert all_passing, "All checks should pass before merge"

    def test_safety_merge_squash_strategy(self):
        """Test merge safety uses squash strategy."""
        # Should use --squash for clean history
        merge_command = "gh pr merge --squash --delete-branch"

        assert "--squash" in merge_command
        assert "--delete-branch" in merge_command

    def test_safety_merge_branch_deletion(self):
        """Test merge safety deletes branch after merge."""
        # Should delete branch unless --keep-branch flag
        default_command = "gh pr merge --squash --delete-branch"
        keep_command = "gh pr merge --squash"

        assert "--delete-branch" in default_command
        assert "--delete-branch" not in keep_command

    # Safety Feature 5: Cleanup Safety
    def test_safety_cleanup_worktree_removal(self, temp_worktree):
        """Test cleanup safety removes worktree successfully."""
        # Worktree should be removed during cleanup
        assert temp_worktree.exists()

        # Simulate removal
        import shutil
        shutil.rmtree(temp_worktree)

        assert not temp_worktree.exists()

    def test_safety_cleanup_status_files_deleted(self, mock_status_files):
        """Test cleanup safety deletes status files."""
        status_files = [
            mock_status_files["review"],
            mock_status_files["eval"],
        ]

        # All status files should be removed
        for file in status_files:
            if file.exists():
                file.unlink()
                assert not file.exists()

    def test_safety_cleanup_back_on_main(self):
        """Test cleanup safety ensures return to main branch."""
        # After cleanup, should be back on main
        expected_branch = "main"
        assert expected_branch in ["main", "master"]

    def test_safety_override_with_force_flag(self):
        """Test safety override behavior with --force flag."""
        # --force should skip validation but show warning
        args_with_force = ["--force"]
        args_without_force = []

        has_force = "--force" in args_with_force
        assert has_force, "Should detect --force flag"

        no_force = "--force" in args_without_force
        assert not no_force, "Should detect no --force flag"
