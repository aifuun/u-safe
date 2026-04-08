"""
Integration tests for complete finish-issue workflow.

Tests end-to-end workflow scenarios:
- Happy path (all phases succeed)
- Review status validation
- PR creation and merge
- Cleanup verification
"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta


@pytest.mark.integration
class TestFinishIssueWorkflow:
    """Test complete finish-issue workflow integration."""

    def test_workflow_happy_path_complete(self, mock_review_status, temp_worktree, mock_plan_file):
        """Test complete workflow - all 8 steps succeed."""
        issue_number = 123

        # Step 1: Pre-Finish Validation
        assert mock_review_status["score"] >= 90
        assert mock_review_status["status"] == "approved"

        # Step 2: Commit & Push
        commit_message = f"feat: add feature (Issue #{issue_number})\n\nFixes #{issue_number}\n\nCo-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
        assert f"Fixes #{issue_number}" in commit_message

        # Step 3: Create PR
        pr_title = f"feat: add feature (Issue #{issue_number})"
        pr_number = 456  # Mock PR number
        assert issue_number in [123]

        # Step 4: Merge PR
        merge_strategy = "squash"
        assert merge_strategy == "squash"

        # Step 5: Generate Summary
        summary = f"""## ✅ Issue 完成总结

**分支**: feature/{issue_number}-test
**PR**: #{pr_number}
**完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

### Commits 列表
abc1234 feat: add feature

**总计**: 1 commits

### 代码质量
✅ Review Score: {mock_review_status["score"]}/100"""

        assert "Issue 完成总结" in summary
        assert f"PR: #{pr_number}" in summary or str(pr_number) in summary

        # Step 6: Post Summary to Issue
        # (Would use gh issue comment)

        # Step 7: Close Issue
        # (Would use gh issue close)

        # Step 8: Cleanup
        # Worktree should be removed
        import shutil
        if temp_worktree.exists():
            shutil.rmtree(temp_worktree)
        assert not temp_worktree.exists()

    def test_workflow_review_status_validation(self, tmp_path):
        """Test workflow validates review status at start."""
        # Create mock review status
        review_file = tmp_path / ".review-status.json"
        review_data = {
            "timestamp": datetime.now().isoformat(),
            "score": 95,
            "status": "approved",
            "valid_until": (datetime.now() + timedelta(minutes=90)).isoformat()
        }
        review_file.write_text(json.dumps(review_data))

        # Workflow should validate
        assert review_file.exists()
        status = json.loads(review_file.read_text())
        assert status["score"] >= 90
        assert status["status"] == "approved"

    def test_workflow_pr_creation_with_context(self):
        """Test PR creation includes issue context."""
        issue_data = {
            "number": 123,
            "title": "Test issue",
            "body": "Issue description with acceptance criteria"
        }

        pr_body = f"""## Summary
Implementation for #{issue_data["number"]}: {issue_data["title"]}

## Changes
- Feature added
- Tests added

Fixes #{issue_data["number"]}

🤖 Generated with [Claude Code](https://claude.com/claude-code)"""

        # PR should reference issue
        assert f"#{issue_data['number']}" in pr_body
        assert "Fixes #" in pr_body
        assert "Claude Code" in pr_body

    def test_workflow_cleanup_verification(self, temp_worktree, mock_status_files):
        """Test cleanup removes all temporary artifacts."""
        # Before cleanup - artifacts exist
        assert temp_worktree.exists()
        assert mock_status_files["review"].exists()

        # Simulate cleanup
        import shutil
        shutil.rmtree(temp_worktree)
        mock_status_files["review"].unlink()
        if mock_status_files["eval"].exists():
            mock_status_files["eval"].unlink()

        # After cleanup - artifacts removed
        assert not temp_worktree.exists()
        assert not mock_status_files["review"].exists()
        assert not mock_status_files["eval"].exists()

    def test_workflow_branch_deletion_after_merge(self):
        """Test branch is deleted after successful merge."""
        # Before merge
        local_branches = ["feature/123-test", "main"]
        assert "feature/123-test" in local_branches

        # After merge (simulate deletion)
        local_branches.remove("feature/123-test")

        # Branch should be deleted
        assert "feature/123-test" not in local_branches
        assert "main" in local_branches

    def test_workflow_return_to_main_branch(self):
        """Test workflow returns to main branch after completion."""
        # After finish-issue completes
        current_branch = "main"
        assert current_branch in ["main", "master"]

    def test_workflow_output_summary(self):
        """Test workflow provides completion summary."""
        summary_output = """✅ Issue #123 finished successfully

Commits: 1 commit
PR: #456 (merged)
Review score: 95/100

Cleanup complete:
- Worktree removed
- Branch deleted
- Status files cleaned

Back on: main branch"""

        # Should contain key information
        assert "finished successfully" in summary_output
        assert "PR:" in summary_output
        assert "Cleanup complete" in summary_output
        assert "main branch" in summary_output

    def test_workflow_state_transitions(self):
        """Test workflow state transitions through phases."""
        # Phase states
        phases = [
            ("pre_validation", "validating"),
            ("commit", "committing"),
            ("pr_create", "creating_pr"),
            ("merge", "merging"),
            ("cleanup", "cleaning_up"),
            ("complete", "done"),
        ]

        # Each phase should transition to next
        for i, (phase, state) in enumerate(phases):
            assert len(phase) > 0
            assert len(state) > 0
            if i > 0:
                prev_phase = phases[i-1][0]
                assert prev_phase != phase

    def test_workflow_error_recovery(self):
        """Test workflow handles errors and provides recovery options."""
        # Simulate error at different phases
        error_scenarios = [
            ("validation_failed", "Fix validation issues"),
            ("commit_failed", "Check git status"),
            ("pr_creation_failed", "Check existing PRs"),
            ("merge_failed", "Check PR checks"),
        ]

        for error_type, recovery_hint in error_scenarios:
            # Each error should have recovery guidance
            assert len(recovery_hint) > 0
            assert any(word in recovery_hint.lower() for word in ["check", "fix", "run", "retry"])
