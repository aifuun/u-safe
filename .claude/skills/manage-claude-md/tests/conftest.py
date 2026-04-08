"""
Pytest fixtures for manage-claude-md tests

Provides reusable test fixtures for all test files.
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create temporary directory for test isolation"""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def mock_claude_md(temp_dir):
    """Mock CLAUDE.md file with skills list"""
    claude_md = temp_dir / "CLAUDE.md"
    content = """# AI Development Framework

## Skills

- /skill1 - First skill
- /skill2 - Second skill
- /skill3 - Third skill

## Other sections

Some other content here.
"""
    claude_md.write_text(content)
    return claude_md


@pytest.fixture
def mock_plans_dir(temp_dir):
    """Mock plans directory with active and archive plans"""
    plans_dir = temp_dir / ".claude" / "plans"
    active_dir = plans_dir / "active"
    archive_dir = plans_dir / "archive"

    active_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)

    # Create some active plans
    (active_dir / "issue-123-plan.md").write_text("# Issue #123\nActive plan")
    (active_dir / "issue-456-plan.md").write_text("# Issue #456\nActive plan")

    # Create some archived plans
    (archive_dir / "issue-100-plan.md").write_text("# Issue #100\nArchived")

    return {
        "root": plans_dir,
        "active": active_dir,
        "archive": archive_dir
    }


@pytest.fixture
def mock_git_env(temp_dir, monkeypatch):
    """Mock git environment for testing"""
    # Mock git commands to avoid real git operations
    def mock_git_status(*args, **kwargs):
        return ("On branch main\nnothing to commit, working tree clean", 0)

    def mock_git_branch(*args, **kwargs):
        return ("* main\n  feature/123-test\n", 0)

    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: type('obj', (object,), {
        'returncode': 0,
        'stdout': 'mocked output',
        'stderr': ''
    })())

    return {
        "status": mock_git_status,
        "branch": mock_git_branch
    }


@pytest.fixture
def mock_skill_files(temp_dir):
    """Mock skill files in .claude/skills directory"""
    skills_dir = temp_dir / ".claude" / "skills"
    skills_dir.mkdir(parents=True)

    # Create sample skills
    for skill_name in ["skill1", "skill2", "skill3"]:
        skill_dir = skills_dir / skill_name
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(f"""---
name: {skill_name}
description: Description of {skill_name}
---

# {skill_name.title()}

This is {skill_name}.
""")

    return skills_dir


@pytest.fixture
def mock_state_files(temp_dir):
    """Mock status files (.eval-plan-status.json, etc.)"""
    claude_dir = temp_dir / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)

    import json
    from datetime import datetime, timedelta

    # Create stale status file (>24h old)
    old_timestamp = (datetime.now() - timedelta(hours=25)).isoformat()
    eval_status = {
        "timestamp": old_timestamp,
        "issue_number": 123,
        "score": 95
    }
    (claude_dir / ".eval-plan-status.json").write_text(json.dumps(eval_status))

    # Create recent status file
    recent_timestamp = datetime.now().isoformat()
    review_status = {
        "timestamp": recent_timestamp,
        "issue_number": 456,
        "score": 88
    }
    (claude_dir / ".review-status.json").write_text(json.dumps(review_status))

    return {
        "eval_status": claude_dir / ".eval-plan-status.json",
        "review_status": claude_dir / ".review-status.json",
        "claude_dir": claude_dir
    }


@pytest.fixture
def mock_profile_config(temp_dir):
    """Mock profile configuration in CLAUDE.md"""
    claude_md = temp_dir / "CLAUDE.md"
    content = """# Project

**Profile**: tauri

## Configuration

This is a Tauri project.
"""
    claude_md.write_text(content)
    return claude_md
