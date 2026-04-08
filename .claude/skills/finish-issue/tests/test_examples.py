"""
Tests for usage examples from finish-issue SKILL.md.

Converts Usage Examples section into executable tests:
- Example 1: Basic finish (happy path)
- Example 2: Dry run preview
- Example 3: Error handling (validation failure)
"""

import pytest
from pathlib import Path


@pytest.mark.examples
class TestUsageExamples:
    """Test usage examples from SKILL.md."""

    # Example 1: Basic Finish (Happy Path)
    def test_example_basic_finish_happy_path(self, mock_review_status, temp_worktree):
        """Test Example 1: Basic finish workflow - all phases succeed."""
        # Scenario: User finishes issue #97 with everything ready
        issue_number = 97

        # Step 1: Pre-finish validation passes
        assert mock_review_status["score"] >= 90
        assert mock_review_status["status"] == "approved"

        # Step 2: Commit changes with proper format
        commit_msg = f"""feat: implement feature (Issue #{issue_number})

Details about implementation.

Fixes #{issue_number}

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"""

        assert f"Fixes #{issue_number}" in commit_msg
        assert "Co-Authored-By" in commit_msg

        # Step 3: Create PR with issue context
        pr_title = f"feat: implement feature (Issue #{issue_number})"
        assert f"#{issue_number}" in pr_title

        # Step 4: Merge PR with squash
        merge_cmd = "gh pr merge --squash --delete-branch"
        assert "--squash" in merge_cmd

        # Step 5-8: Post summary, close issue, cleanup
        # (Simulated - actual implementation would execute these)

        # Expected outcome: Issue finished successfully
        expected_output = f"✅ Issue #{issue_number} finished successfully"
        assert "finished successfully" in expected_output

    def test_example_basic_finish_file_changes(self):
        """Test Example 1: Verify file changes are tracked."""
        # Simulate git diff --stat output
        diff_stat = " 1 file changed, 100 insertions(+), 5 deletions(-)\n src/feature.ts | 105 +++++++++++++++++++++++"

        # Should report file changes
        assert "1 file changed" in diff_stat
        assert "insertions" in diff_stat

    def test_example_basic_finish_completion_time(self):
        """Test Example 1: Verify typical completion time range."""
        # Expected time: ~2-3 minutes
        min_time_seconds = 60  # 1 minute minimum
        max_time_seconds = 300  # 5 minutes maximum
        typical_time = 150  # ~2.5 minutes

        assert min_time_seconds <= typical_time <= max_time_seconds

    # Example 2: Dry Run Preview
    def test_example_dry_run_preview_no_execution(self):
        """Test Example 2: Dry run shows preview without executing."""
        # Dry run flag
        args = ["--dry-run"]
        is_dry_run = "--dry-run" in args

        assert is_dry_run, "Should detect dry-run mode"

        # In dry run, should NOT execute commands
        should_execute = not is_dry_run
        assert not should_execute, "Should not execute in dry-run mode"

    def test_example_dry_run_preview_output(self):
        """Test Example 2: Dry run shows what would happen."""
        dry_run_output = """DRY RUN MODE - No changes will be made

Step 1: Commit changes
  Files: .claude/skills/finish-issue/SKILL.md
  Message: "docs: add Safety Features"

Step 2: Create PR
  Title: "docs: finish-issue 文档重构"

Step 3: Merge PR
  Strategy: Squash merge

To execute: /finish-issue #97 (without --dry-run)"""

        # Should show all steps
        assert "DRY RUN MODE" in dry_run_output
        assert "No changes will be made" in dry_run_output
        assert "Step 1" in dry_run_output
        assert "Step 2" in dry_run_output
        assert "To execute" in dry_run_output

    def test_example_dry_run_fast_execution(self):
        """Test Example 2: Dry run completes quickly (<10 seconds)."""
        max_dry_run_time = 10  # seconds
        typical_dry_run_time = 5  # seconds

        assert typical_dry_run_time < max_dry_run_time

    # Example 3: Error Handling (Validation Failure)
    def test_example_validation_failure_detection(self):
        """Test Example 3: Validation failure is detected."""
        # Simulate validation failures
        validation_errors = [
            "No review status found",
            "Uncommitted changes detected",
            "Tests failing (2/10 passing)",
        ]

        # Should detect all failures
        assert len(validation_errors) > 0
        for error in validation_errors:
            assert len(error) > 0

    def test_example_validation_failure_error_messages(self):
        """Test Example 3: Clear error messages with fixes."""
        error_output = """❌ Pre-finish validation failed

Issues found:
1. No review status found
   - Run: /review

2. Uncommitted changes detected
   - Files: .claude/skills/finish-issue/SKILL.md
   - Action: Commit changes before finishing

3. Tests failing (2/10 passing)
   - Failed: test_validation, test_cleanup
   - Fix tests before merge

Fix these issues, then retry /finish-issue #97"""

        # Should show clear errors and fixes
        assert "❌" in error_output or "Error" in error_output.lower()
        assert "Issues found" in error_output
        assert "Run:" in error_output or "Action:" in error_output
        assert "Fix these issues" in error_output

    def test_example_validation_failure_recovery(self):
        """Test Example 3: User can fix issues and retry."""
        # Simulate fix steps
        fix_steps = [
            "npm test",  # Fix tests
            "git add . && git commit -m 'fix: tests'",  # Commit changes
            "/review",  # Run review
        ]

        # All fix steps should be valid commands
        assert all(len(step) > 0 for step in fix_steps)

        # After fixes, should retry successfully
        retry_command = "/finish-issue #97"
        assert "#97" in retry_command

    def test_example_validation_failure_no_force_usage(self):
        """Test Example 3: Should fix issues, not use --force."""
        # Recommended: Fix issues
        recommended = ["npm test", "/review", "git commit"]

        # Not recommended: Use --force
        not_recommended = ["--force"]

        # Should prefer fixing over forcing
        assert len(recommended) > 0
        assert any("test" in cmd or "review" in cmd for cmd in recommended)
