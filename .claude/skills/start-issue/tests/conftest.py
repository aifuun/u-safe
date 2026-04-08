"""
Shared fixtures for start-issue tests.
"""
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

import pytest


@pytest.fixture
def mock_gh_issue() -> Dict[str, Any]:
    """Mock GitHub issue data."""
    return {
        "number": 123,
        "title": "Test Issue for Testing",
        "body": "## Tasks\n- [ ] Task 1\n- [ ] Task 2\n\n## Acceptance Criteria\n- Criterion 1",
        "state": "OPEN",
        "labels": [{"name": "bug"}, {"name": "P1"}]
    }


@pytest.fixture
def temp_git_repo(tmp_path: Path) -> Path:
    """Create temporary git repository for testing."""
    repo_dir = tmp_path / "test-repo"
    repo_dir.mkdir()

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True, capture_output=True)

    # Create initial commit
    readme = repo_dir / "README.md"
    readme.write_text("# Test Repo\n")
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True, capture_output=True)

    # Create main branch
    subprocess.run(["git", "branch", "-M", "main"], cwd=repo_dir, check=True, capture_output=True)

    return repo_dir


@pytest.fixture
def sample_issue_body() -> str:
    """Sample issue body with tasks and acceptance criteria."""
    return """## Background

This is a test issue for validation.

## Tasks

- [ ] Create test directory structure
- [ ] Implement test cases
- [ ] Validate coverage

## Acceptance Criteria

- All tests pass
- Coverage >= 80%
- ADR-015 compliant
"""


@pytest.fixture
def mock_gh_cli(monkeypatch, mock_gh_issue):
    """Mock gh CLI commands."""
    def mock_run(*args, **kwargs):
        cmd = args[0] if args else kwargs.get('args', [])

        if 'gh' in cmd and 'issue' in cmd and 'view' in cmd:
            # Mock gh issue view
            result = subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout=json.dumps(mock_gh_issue).encode(),
                stderr=b''
            )
            return result
        elif 'gh' in cmd and 'auth' in cmd and 'status' in cmd:
            # Mock gh auth status
            result = subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout='github.com\n  Logged in\n'.encode('utf-8'),
                stderr=b''
            )
            return result
        else:
            # Default to actual subprocess call
            return subprocess.run(*args, **kwargs)

    monkeypatch.setattr(subprocess, 'run', mock_run)
