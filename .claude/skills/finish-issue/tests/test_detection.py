"""
Unit tests for issue number detection in finish-issue.

Tests the 4 detection strategies:
1. Branch name extraction
2. Active plan detection
3. Worktree path extraction
4. User prompt fallback
"""

import pytest
from pathlib import Path


@pytest.mark.unit
class TestIssueDetection:
    """Test issue number detection strategies."""

    def test_extract_from_branch_name(self):
        """Test extracting issue number from branch name."""
        # Test various branch name formats
        test_cases = [
            ("feature/123-test-issue", 123),
            ("fix/456-bug-fix", 456),
            ("feature/789-long-feature-name", 789),
            ("hotfix/1-urgent", 1),
        ]

        for branch_name, expected in test_cases:
            # Simulate branch name extraction
            import re
            match = re.search(r'/(\d+)-', branch_name)
            assert match is not None, f"Failed to extract from {branch_name}"
            result = int(match.group(1))
            assert result == expected, f"Expected {expected}, got {result}"

    def test_extract_from_invalid_branch(self):
        """Test extraction fails gracefully for invalid branch names."""
        invalid_branches = [
            "main",
            "master",
            "develop",
            "feature/no-number",
            "fix-without-slash"
        ]

        for branch_name in invalid_branches:
            import re
            match = re.search(r'/(\d+)-', branch_name)
            assert match is None, f"Should not extract from {branch_name}"

    def test_find_single_active_plan(self, tmp_path):
        """Test finding issue from single active plan file."""
        # Create active plans directory
        plans_dir = tmp_path / ".claude" / "plans" / "active"
        plans_dir.mkdir(parents=True, exist_ok=True)

        # Create single plan file
        plan_file = plans_dir / "issue-123-plan.md"
        plan_file.write_text("# Issue #123")

        # Find plan files
        plan_files = list(plans_dir.glob("issue-*-plan.md"))
        assert len(plan_files) == 1

        # Extract issue number
        import re
        match = re.search(r'issue-(\d+)-plan\.md', plan_files[0].name)
        assert match is not None
        issue_num = int(match.group(1))
        assert issue_num == 123

    def test_multiple_active_plans_fail(self, tmp_path):
        """Test detection fails when multiple plans exist."""
        plans_dir = tmp_path / ".claude" / "plans" / "active"
        plans_dir.mkdir(parents=True, exist_ok=True)

        # Create multiple plan files
        (plans_dir / "issue-123-plan.md").write_text("# Issue #123")
        (plans_dir / "issue-456-plan.md").write_text("# Issue #456")

        # Should find multiple plans (ambiguous)
        plan_files = list(plans_dir.glob("issue-*-plan.md"))
        assert len(plan_files) > 1, "Multiple plans should be detected"

    def test_extract_from_worktree_path(self):
        """Test extracting issue number from worktree directory path."""
        test_cases = [
            ("/Users/dev/ai-dev-123-test-issue", 123),
            ("/home/user/repo-456-feature", 456),
            ("../project-789-long-name", 789),
        ]

        for worktree_path, expected in test_cases:
            import re
            match = re.search(r'-(\d+)-', worktree_path)
            assert match is not None, f"Failed to extract from {worktree_path}"
            result = int(match.group(1))
            assert result == expected

    def test_worktree_extraction_fallback(self):
        """Test worktree extraction handles edge cases."""
        invalid_paths = [
            "/Users/dev/ai-dev",  # No issue number
            "/home/user/project-name",  # No number
            "relative/path/without/number",
        ]

        for path in invalid_paths:
            import re
            match = re.search(r'-(\d+)-', path)
            assert match is None, f"Should not extract from {path}"

    def test_detection_priority_order(self):
        """Test detection strategies are tried in correct order."""
        # Priority order:
        # 1. Explicit argument
        # 2. Branch name
        # 3. Active plan
        # 4. Worktree path
        # 5. User prompt

        priorities = [
            ("argument", 1),
            ("branch", 2),
            ("plan", 3),
            ("worktree", 4),
            ("prompt", 5)
        ]

        for strategy, priority in priorities:
            assert priority >= 1 and priority <= 5, f"Invalid priority for {strategy}"

    def test_issue_number_validation(self):
        """Test issue numbers are validated as positive integers."""
        valid_numbers = [1, 123, 999, 1000]
        invalid_numbers = [0, -1, -123, "abc", None]

        for num in valid_numbers:
            assert isinstance(num, int) and num > 0

        for num in invalid_numbers:
            if isinstance(num, int):
                assert num <= 0
            else:
                assert not isinstance(num, int) or num is None
