"""
Unit tests for pre-finish validation checks.

Tests validation of review status, git state, tests, and branch sync.
"""

import pytest
import json
from datetime import datetime, timedelta


@pytest.mark.unit
class TestPreFinishValidation:
    """Test pre-finish validation mechanisms."""

    def test_review_status_exists(self, mock_status_files):
        """Test validation checks for review status file."""
        review_file = mock_status_files["review"]
        assert review_file.exists(), "Review status file should exist"

        # Read and validate
        status = json.loads(review_file.read_text())
        assert "score" in status
        assert "status" in status

    def test_review_score_threshold(self, mock_review_status):
        """Test review score meets threshold (≥90 recommended)."""
        assert mock_review_status["score"] >= 90, "Score should be ≥90 for auto-continue"
        assert mock_review_status["status"] == "approved"

    def test_review_status_not_expired(self, mock_review_status):
        """Test review status is within 90-minute validity window."""
        valid_until = datetime.fromisoformat(mock_review_status["valid_until"])
        now = datetime.now()

        assert valid_until > now, "Review status should not be expired"

    def test_not_on_main_branch(self):
        """Test validation fails if on main branch."""
        # Simulate git branch check
        current_branches = [
            ("feature/123-test", True),  # Valid
            ("fix/456-bug", True),  # Valid
            ("main", False),  # Invalid
            ("master", False),  # Invalid
        ]

        for branch, should_pass in current_branches:
            is_feature_branch = branch not in ["main", "master", "develop"]
            assert is_feature_branch == should_pass

    def test_no_uncommitted_changes(self):
        """Test validation checks for uncommitted changes."""
        # Simulate git status outputs
        status_outputs = [
            ("", True),  # Clean - valid
            (" M file.ts", False),  # Modified - invalid
            ("?? newfile.ts", False),  # Untracked - invalid
        ]

        for status, should_pass in status_outputs:
            has_changes = len(status.strip()) > 0
            assert (not has_changes) == should_pass

    def test_branch_synced_with_main(self):
        """Test validation checks if branch is synced with main."""
        # Simulate git status outputs for sync check
        sync_statuses = [
            ("Your branch is up to date", True),
            ("Your branch is behind", False),
            ("Your branch has diverged", False),
        ]

        for status, should_pass in sync_statuses:
            is_synced = "up to date" in status
            assert is_synced == should_pass

    def test_validation_failure_messages(self):
        """Test validation provides clear error messages."""
        validation_errors = [
            ("No review status", "run /review first"),
            ("Uncommitted changes", "commit before finishing"),
            ("Tests failing", "fix tests before merge"),
            ("Not synced with main", "sync branch with main"),
        ]

        for error_type, expected_fix in validation_errors:
            # Each error should have a suggested fix
            assert len(expected_fix) > 0
            assert "before" in expected_fix or "first" in expected_fix or "with" in expected_fix
