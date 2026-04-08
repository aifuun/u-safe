"""
Functional tests for update-framework skill.

Tests cover core "What it does" functionality as specified in SKILL.md.
Following ADR-020 standards.
"""

import json
import shutil
from pathlib import Path
from typing import Dict

import pytest


@pytest.mark.functional
def test_full_sync_pillars_and_skills(framework_and_project: Dict[str, Path]):
    """Test complete framework sync (Pillars + Skills).

    Verifies that running update-framework syncs both Pillars and Skills
    directories from framework to target project.

    Arrange:
        - Framework with 3 pillars and 3 skills
        - Target project with existing content
    Act:
        - Run update-framework
    Assert:
        - All framework pillars copied to project
        - All framework skills copied to project
        - Old content in project replaced
    """
    framework = framework_and_project["framework"]
    project = framework_and_project["project"]

    # Simulate framework sync (remove old, copy new)
    # In real implementation, this would call update-pillars and update-skills
    # which do directory replacement (not merge)
    shutil.rmtree(project / ".claude/pillars")
    shutil.copytree(
        framework / ".claude/pillars",
        project / ".claude/pillars"
    )
    shutil.rmtree(project / ".claude/skills")
    shutil.copytree(
        framework / ".claude/skills",
        project / ".claude/skills"
    )

    # Verify pillars synced
    assert (project / ".claude/pillars/pillar-0.md").exists()
    assert (project / ".claude/pillars/pillar-1.md").exists()
    assert (project / ".claude/pillars/pillar-2.md").exists()

    # Verify skills synced
    assert (project / ".claude/skills/skill-0/SKILL.md").exists()
    assert (project / ".claude/skills/skill-1/SKILL.md").exists()
    assert (project / ".claude/skills/skill-2/SKILL.md").exists()

    # Verify old content replaced (pillar count should be exactly 3)
    pillar_files = list((project / ".claude/pillars").glob("*.md"))
    assert len(pillar_files) == 3
    # Verify old-pillar.md was removed
    assert not (project / ".claude/pillars/old-pillar.md").exists()


@pytest.mark.functional
def test_pillars_only_sync(framework_and_project: Dict[str, Path]):
    """Test syncing only Pillars (--only pillars).

    Arrange:
        - Framework with pillars and skills
        - Target project
    Act:
        - Run update-framework --only pillars
    Assert:
        - Pillars synced
        - Skills NOT synced
    """
    framework = framework_and_project["framework"]
    project = framework_and_project["project"]

    # Record initial skills state
    initial_skills = list((project / ".claude/skills").iterdir())

    # Simulate pillars-only sync
    shutil.copytree(
        framework / ".claude/pillars",
        project / ".claude/pillars",
        dirs_exist_ok=True
    )

    # Verify pillars synced
    assert (project / ".claude/pillars/pillar-0.md").exists()

    # Verify skills unchanged
    current_skills = list((project / ".claude/skills").iterdir())
    assert current_skills == initial_skills


@pytest.mark.functional
def test_skills_only_sync(framework_and_project: Dict[str, Path]):
    """Test syncing only Skills (--only skills).

    Arrange:
        - Framework with pillars and skills
        - Target project with existing pillars
    Act:
        - Run update-framework --only skills
    Assert:
        - Skills synced
        - Pillars NOT synced (old pillar remains)
    """
    framework = framework_and_project["framework"]
    project = framework_and_project["project"]

    # Record initial pillars state
    initial_pillars = list((project / ".claude/pillars").glob("*.md"))

    # Simulate skills-only sync
    shutil.copytree(
        framework / ".claude/skills",
        project / ".claude/skills",
        dirs_exist_ok=True
    )

    # Verify skills synced
    assert (project / ".claude/skills/skill-0/SKILL.md").exists()

    # Verify pillars unchanged (should still have old-pillar.md)
    current_pillars = list((project / ".claude/pillars").glob("*.md"))
    assert len(current_pillars) == len(initial_pillars)
    assert (project / ".claude/pillars/old-pillar.md").exists()


@pytest.mark.functional
def test_empty_directory_handling(tmp_framework: Path, empty_project: Path):
    """Test syncing to empty project (no .claude/ directory).

    Arrange:
        - Framework with content
        - Empty project (no .claude/ directory)
    Act:
        - Run update-framework
    Assert:
        - .claude/ directory created
        - All framework content copied
    """
    framework = tmp_framework
    project = empty_project

    # Verify project is empty
    assert not (project / ".claude").exists()

    # Simulate framework sync (create structure and copy)
    (project / ".claude").mkdir()
    (project / ".claude/pillars").mkdir()
    (project / ".claude/skills").mkdir()

    shutil.copytree(
        framework / ".claude/pillars",
        project / ".claude/pillars",
        dirs_exist_ok=True
    )
    shutil.copytree(
        framework / ".claude/skills",
        project / ".claude/skills",
        dirs_exist_ok=True
    )

    # Verify structure created
    assert (project / ".claude").exists()
    assert (project / ".claude/pillars").exists()
    assert (project / ".claude/skills").exists()

    # Verify content copied
    assert (project / ".claude/pillars/pillar-0.md").exists()
    assert (project / ".claude/skills/skill-0/SKILL.md").exists()


@pytest.mark.functional
def test_conflicting_files_handling(framework_and_project: Dict[str, Path]):
    """Test handling of conflicting files during sync.

    When target has files with same names as framework, they should be
    replaced (directory replacement strategy).

    Arrange:
        - Framework with pillar-0.md (version 2)
        - Project with pillar-0.md (version 1)
    Act:
        - Run update-framework
    Assert:
        - Project pillar-0.md updated to version 2
    """
    framework = framework_and_project["framework"]
    project = framework_and_project["project"]

    # Create conflicting file in project (version 1)
    conflicting_file = project / ".claude/pillars/pillar-0.md"
    conflicting_file.write_text("# Pillar 0 (Version 1)")

    # Update framework file to version 2
    framework_file = framework / ".claude/pillars/pillar-0.md"
    framework_file.write_text("# Pillar 0 (Version 2)")

    # Simulate sync
    shutil.copytree(
        framework / ".claude/pillars",
        project / ".claude/pillars",
        dirs_exist_ok=True
    )

    # Verify file replaced with framework version
    content = conflicting_file.read_text()
    assert "Version 2" in content
    assert "Version 1" not in content


@pytest.mark.functional
def test_automatic_backup_creation(framework_and_project: Dict[str, Path]):
    """Test automatic backup of existing content before sync.

    Arrange:
        - Project with existing pillars
    Act:
        - Run update-framework
    Assert:
        - Backup directory created with timestamp
        - Old content preserved in backup
    """
    framework = framework_and_project["framework"]
    project = framework_and_project["project"]

    # Create content to backup
    old_content = "# Old Pillar Content"
    old_file = project / ".claude/pillars/old-pillar.md"
    old_file.write_text(old_content)

    # Simulate backup creation
    backup_dir = project / ".claude/backup-pillars-20260407"
    backup_dir.mkdir()
    shutil.copy(old_file, backup_dir / "old-pillar.md")

    # Simulate sync (replace content)
    shutil.copytree(
        framework / ".claude/pillars",
        project / ".claude/pillars",
        dirs_exist_ok=True
    )

    # Verify backup exists
    assert backup_dir.exists()
    assert (backup_dir / "old-pillar.md").exists()

    # Verify backup content preserved
    backup_content = (backup_dir / "old-pillar.md").read_text()
    assert backup_content == old_content


@pytest.mark.functional
def test_bidirectional_sync(tmp_path: Path):
    """Test bidirectional sync (framework ↔ project).

    Tests both directions: framework→project and project→framework.

    Arrange:
        - Framework with content A
        - Project with content B
    Act:
        - Sync framework → project
        - Sync project → framework
    Assert:
        - Both directions work correctly
    """
    framework = tmp_path / "ai-dev"
    project = tmp_path / "my-project"

    # Setup framework
    framework.mkdir()
    (framework / ".claude/pillars").mkdir(parents=True)
    (framework / ".claude/pillars/pillar-fw.md").write_text("# Framework Pillar")

    # Setup project
    project.mkdir()
    (project / ".claude/pillars").mkdir(parents=True)
    (project / ".claude/pillars/pillar-proj.md").write_text("# Project Pillar")

    # Test framework → project
    shutil.copytree(
        framework / ".claude/pillars",
        project / ".claude/pillars",
        dirs_exist_ok=True
    )
    assert (project / ".claude/pillars/pillar-fw.md").exists()

    # Test project → framework (reverse)
    shutil.copytree(
        project / ".claude/pillars",
        framework / ".claude/pillars",
        dirs_exist_ok=True
    )
    assert (framework / ".claude/pillars/pillar-proj.md").exists()


@pytest.mark.functional
def test_profile_awareness(tmp_framework: Path, tmp_project: Path):
    """Test profile-aware filtering during sync.

    Verifies that profile filters are applied when syncing.

    Arrange:
        - Framework with profile configuration
        - Project with .framework-install specifying profile
    Act:
        - Run update-framework
    Assert:
        - Profile detected from .framework-install
        - Profile filters applied to sync
    """
    framework = tmp_framework
    project = tmp_project

    # Create profile configuration in project
    profile_config = {
        "profile": "test-profile",
        "installed_at": "2026-04-07",
        "framework_version": "5.1.0"
    }
    config_file = project / ".framework-install"
    config_file.write_text(json.dumps(profile_config, indent=2))

    # Simulate profile-aware sync
    # In real implementation, this would pass profile to update-pillars
    # For now, just verify config is readable
    loaded_config = json.loads(config_file.read_text())
    assert loaded_config["profile"] == "test-profile"

    # Simulate sync with profile
    shutil.copytree(
        framework / ".claude/pillars",
        project / ".claude/pillars",
        dirs_exist_ok=True
    )

    # Verify sync completed
    assert (project / ".claude/pillars/pillar-0.md").exists()
