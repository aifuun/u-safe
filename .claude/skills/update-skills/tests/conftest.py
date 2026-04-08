"""
Shared pytest fixtures for update-skills tests.

Provides common test infrastructure including:
- Temporary directory fixtures for source/target
- Mock skill structures
- Version file helpers
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List


@pytest.fixture
def temp_source_dir(tmp_path):
    """Create a temporary source directory with .claude/skills/ structure."""
    source = tmp_path / "source"
    skills_dir = source / ".claude" / "skills"
    skills_dir.mkdir(parents=True)

    # Create sample skills
    for skill_name in ["skill-a", "skill-b", "skill-k"]:
        skill_path = skills_dir / skill_name
        skill_path.mkdir()
        (skill_path / "SKILL.md").write_text(f"# {skill_name}\nversion: 1.0.0\n")

    # Create subdirectories
    (skills_dir / "_scripts").mkdir()
    (skills_dir / "_shared").mkdir()
    (skills_dir / "_templates").mkdir()

    yield source

    # Cleanup handled by tmp_path fixture


@pytest.fixture
def temp_target_dir(tmp_path):
    """Create a temporary target directory."""
    target = tmp_path / "target"
    target.mkdir()
    yield target


@pytest.fixture
def mock_skill_with_version():
    """Create a mock skill file content with YAML frontmatter version."""
    def _create(version: str = "1.0.0") -> str:
        return f"""---
name: test-skill
version: {version}
---

# Test Skill

Test content.
"""
    return _create


@pytest.fixture
def create_skill_structure():
    """Helper to create skill directory structure with specific versions."""
    def _create(base_path: Path, skills: Dict[str, str]):
        """
        Create skills at base_path/.claude/skills/

        Args:
            base_path: Root directory
            skills: Dict of skill_name -> version
        """
        skills_dir = base_path / ".claude" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

        for skill_name, version in skills.items():
            skill_path = skills_dir / skill_name
            skill_path.mkdir(exist_ok=True)

            content = f"""---
name: {skill_name}
version: {version}
---

# {skill_name.title()}

Test skill content.
"""
            (skill_path / "SKILL.md").write_text(content)

        return skills_dir

    return _create


@pytest.fixture
def assert_directory_synced():
    """Helper to assert source and target directories are synced."""
    def _assert(source: Path, target: Path, excluded_skills: List[str] = None):
        """
        Assert that target contains same skills as source (minus exclusions).

        Args:
            source: Source .claude/skills/ directory
            target: Target .claude/skills/ directory
            excluded_skills: List of skill names to exclude from comparison
        """
        excluded_skills = excluded_skills or []

        source_skills = {
            d.name for d in source.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        }

        target_skills = {
            d.name for d in target.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        }

        expected_skills = source_skills - set(excluded_skills)

        assert target_skills == expected_skills, (
            f"Target skills {target_skills} != expected {expected_skills}"
        )

        # Verify content of each skill
        for skill in expected_skills:
            source_skill_file = source / skill / "SKILL.md"
            target_skill_file = target / skill / "SKILL.md"

            if source_skill_file.exists():
                assert target_skill_file.exists(), f"Missing {skill}/SKILL.md in target"
                assert (
                    source_skill_file.read_text() == target_skill_file.read_text()
                ), f"{skill}/SKILL.md content mismatch"

    return _assert
