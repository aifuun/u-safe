"""
Shared test fixtures for update-framework skill tests.

This module provides reusable fixtures following ADR-020 standards.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Generator
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def tmp_framework(tmp_path: Path) -> Path:
    """Create temporary framework directory structure.

    Args:
        tmp_path: pytest's tmp_path fixture

    Returns:
        Path to temporary framework directory

    Example:
        >>> def test_sync(tmp_framework):
        ...     assert (tmp_framework / ".claude/pillars").exists()
    """
    framework = tmp_path / "ai-dev"
    framework.mkdir()

    # Create framework structure
    (framework / ".claude").mkdir()
    (framework / ".claude/pillars").mkdir()
    (framework / ".claude/skills").mkdir()
    (framework / ".claude/guides").mkdir()
    (framework / ".claude/profiles").mkdir()

    # Create sample pillars
    for i in range(3):
        pillar_file = framework / ".claude/pillars" / f"pillar-{i}.md"
        pillar_file.write_text(f"# Pillar {i}\n\nContent of pillar {i}")

    # Create sample skills
    for i in range(3):
        skill_dir = framework / ".claude/skills" / f"skill-{i}"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(f"# Skill {i}\n\nContent")

    # Create sample guides
    (framework / ".claude/guides/workflow").mkdir(parents=True)
    (framework / ".claude/guides/workflow/guide-1.md").write_text("# Guide 1")

    # Create sample profile
    profile_content = {
        "name": "test-profile",
        "description": "Test profile",
        "tech_stack": ["python", "pytest"]
    }
    profile_file = framework / ".claude/profiles/test-profile.json"
    profile_file.write_text(json.dumps(profile_content, indent=2))

    return framework


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create temporary target project directory.

    Args:
        tmp_path: pytest's tmp_path fixture

    Returns:
        Path to temporary project directory

    Example:
        >>> def test_sync(tmp_project):
        ...     assert tmp_project.exists()
    """
    project = tmp_path / "my-project"
    project.mkdir()

    # Create basic project structure
    (project / ".claude").mkdir()
    (project / ".claude/pillars").mkdir()
    (project / ".claude/skills").mkdir()
    (project / ".claude/guides").mkdir()

    # Create existing content (will be overwritten)
    (project / ".claude/pillars/old-pillar.md").write_text("# Old Pillar")

    return project


@pytest.fixture
def mock_skill_invocation() -> Generator[MagicMock, None, None]:
    """Mock Skill() tool invocations.

    Yields:
        MagicMock object tracking skill calls

    Example:
        >>> def test_delegation(mock_skill_invocation):
        ...     # Test code that calls Skill()
        ...     mock_skill_invocation.assert_called_with(
        ...         skill="update-pillars",
        ...         args="../my-project"
        ...     )
    """
    with patch("builtins.Skill") as mock:
        yield mock


@pytest.fixture
def mock_git() -> Generator[MagicMock, None, None]:
    """Mock git commands.

    Yields:
        MagicMock object tracking git calls

    Example:
        >>> def test_git_ops(mock_git):
        ...     mock_git.return_value.returncode = 0
        ...     mock_git.return_value.stdout = "clean"
    """
    with patch("subprocess.run") as mock:
        mock.return_value.returncode = 0
        mock.return_value.stdout = ""
        mock.return_value.stderr = ""
        yield mock


@pytest.fixture
def framework_and_project(tmp_framework: Path, tmp_project: Path) -> Dict[str, Path]:
    """Provide both framework and project directories.

    Args:
        tmp_framework: Framework directory fixture
        tmp_project: Project directory fixture

    Returns:
        Dictionary with 'framework' and 'project' paths

    Example:
        >>> def test_sync(framework_and_project):
        ...     src = framework_and_project['framework']
        ...     dst = framework_and_project['project']
    """
    return {
        "framework": tmp_framework,
        "project": tmp_project
    }


@pytest.fixture
def empty_project(tmp_path: Path) -> Path:
    """Create empty project directory (no .claude/).

    Args:
        tmp_path: pytest's tmp_path fixture

    Returns:
        Path to empty project directory

    Example:
        >>> def test_init(empty_project):
        ...     assert not (empty_project / ".claude").exists()
    """
    project = tmp_path / "empty-project"
    project.mkdir()
    return project


@pytest.fixture(autouse=True)
def clean_state_files():
    """Auto-cleanup state files after each test.

    Runs automatically after every test to prevent state pollution.
    """
    yield
    # Cleanup any state files created during tests
    state_files = [
        ".claude/.update-framework-state.json",
        ".claude/.sync-status.json"
    ]
    for file in state_files:
        if Path(file).exists():
            Path(file).unlink()
