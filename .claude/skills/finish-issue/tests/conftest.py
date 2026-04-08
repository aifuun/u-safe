"""
Pytest fixtures for finish-issue test suite.

Provides reusable test fixtures for mocking common scenarios.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_issue_data():
    """Mock GitHub issue data."""
    return {
        "number": 123,
        "title": "Test issue for finish-issue",
        "body": "Test issue body with acceptance criteria",
        "state": "OPEN",
        "url": "https://github.com/test/repo/issues/123"
    }


@pytest.fixture
def mock_review_status():
    """Mock review status file data."""
    return {
        "timestamp": datetime.now().isoformat(),
        "issue_number": 123,
        "status": "approved",
        "score": 95,
        "breakdown": {
            "goal_coverage": 30,
            "architecture": 38,
            "best_practices": 18,
            "quality": 9
        },
        "issues_count": {
            "blocking": 0,
            "recommendations": 1
        },
        "valid_until": (datetime.now() + timedelta(minutes=90)).isoformat()
    }


@pytest.fixture
def mock_eval_plan_status():
    """Mock eval-plan status file data."""
    return {
        "timestamp": datetime.now().isoformat(),
        "issue_number": 123,
        "status": "approved",
        "score": 92,
        "breakdown": {
            "architecture": 40,
            "coverage": 28,
            "dependencies": 15,
            "practices": 9,
            "clarity": 5
        },
        "issues_count": {
            "blocking": 0,
            "recommendations": 2,
            "suggestions": 1
        },
        "valid_until": (datetime.now() + timedelta(minutes=90)).isoformat(),
        "plan_file": "/path/to/plan.md"
    }


@pytest.fixture
def temp_worktree(tmp_path):
    """Create temporary worktree directory for testing."""
    worktree_dir = tmp_path / "test-worktree-123-test-issue"
    worktree_dir.mkdir(parents=True, exist_ok=True)

    # Create minimal git-like structure
    (worktree_dir / ".git").mkdir(exist_ok=True)
    (worktree_dir / ".claude").mkdir(exist_ok=True)
    (worktree_dir / ".claude" / "plans").mkdir(exist_ok=True)
    (worktree_dir / ".claude" / "plans" / "active").mkdir(exist_ok=True)

    yield worktree_dir

    # Cleanup
    if worktree_dir.exists():
        shutil.rmtree(worktree_dir)


@pytest.fixture
def mock_git_repo(tmp_path):
    """Create mock git repository structure."""
    repo_dir = tmp_path / "test-repo"
    repo_dir.mkdir(parents=True, exist_ok=True)

    # Create .git directory
    git_dir = repo_dir / ".git"
    git_dir.mkdir(exist_ok=True)

    # Create .claude directory structure
    claude_dir = repo_dir / ".claude"
    claude_dir.mkdir(exist_ok=True)
    (claude_dir / "plans").mkdir(exist_ok=True)
    (claude_dir / "plans" / "active").mkdir(exist_ok=True)
    (claude_dir / "plans" / "archive").mkdir(exist_ok=True)

    yield repo_dir

    # Cleanup
    if repo_dir.exists():
        shutil.rmtree(repo_dir)


@pytest.fixture
def mock_plan_file(temp_worktree):
    """Create mock plan file in worktree."""
    plan_file = temp_worktree / ".claude" / "plans" / "active" / "issue-123-plan.md"
    plan_content = """---
issue: 123
title: "Test issue"
status: active
created: 2026-04-07
version: 1.0.0
---

# Issue #123: Test issue

**GitHub**: https://github.com/test/repo/issues/123
**Branch**: feature/123-test-issue
**Worktree**: {worktree}
**Started**: 2026-04-07

## Tasks

### 1. Task One
**Description**: First test task
**Acceptance**: Task one complete

### 2. Task Two
**Description**: Second test task
**Acceptance**: Task two complete

## Acceptance Criteria

1. Criterion one
2. Criterion two
""".format(worktree=str(temp_worktree))

    plan_file.write_text(plan_content)
    return plan_file


@pytest.fixture
def mock_status_files(tmp_path):
    """Create mock status files (.review-status.json, .eval-plan-status.json)."""
    status_dir = tmp_path / ".claude"
    status_dir.mkdir(parents=True, exist_ok=True)

    review_status = status_dir / ".review-status.json"
    eval_status = status_dir / ".eval-plan-status.json"
    work_state = status_dir / ".work-issue-state.json"

    # Write mock status files
    review_data = {
        "timestamp": datetime.now().isoformat(),
        "score": 95,
        "status": "approved"
    }
    review_status.write_text(json.dumps(review_data, indent=2))

    eval_data = {
        "timestamp": datetime.now().isoformat(),
        "score": 92,
        "status": "approved"
    }
    eval_status.write_text(json.dumps(eval_data, indent=2))

    return {
        "review": review_status,
        "eval": eval_status,
        "work": work_state
    }


@pytest.fixture
def mock_gh_cli():
    """Mock gh CLI commands."""
    mock = MagicMock()

    # Mock gh issue view
    mock.issue_view.return_value = {
        "number": 123,
        "title": "Test issue",
        "state": "OPEN"
    }

    # Mock gh pr create
    mock.pr_create.return_value = "https://github.com/test/repo/pull/456"

    # Mock gh pr merge
    mock.pr_merge.return_value = "Merged successfully"

    # Mock gh issue close
    mock.issue_close.return_value = "Issue closed"

    return mock


@pytest.fixture
def mock_git_commands():
    """Mock git command responses."""
    return {
        "status": "",  # Clean working directory
        "branch": "feature/123-test-issue",
        "diff_stat": " 1 file changed, 100 insertions(+), 10 deletions(-)\n src/test.ts | 110 ++++++++++++++++++++++++\n",
        "log": "abc1234 feat: implement feature\ndef5678 test: add tests",
        "worktree_list": "/path/to/worktree-123-test-issue"
    }


@pytest.fixture
def capture_output(capsys):
    """Fixture to capture stdout/stderr output."""
    def _capture():
        captured = capsys.readouterr()
        return {
            "stdout": captured.out,
            "stderr": captured.err
        }
    return _capture
