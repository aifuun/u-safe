"""
Tests for update-skills complete replacement mode (default behavior).

Based on SKILL.md "What it does" + "Sync Modes - Default Mode".
Tests the simple two-step process: rm + cp.
"""

import pytest
from pathlib import Path
import shutil


class TestCompleteReplacement:
    """Test suite for complete directory replacement mode."""

    def test_deletes_target_directory_before_copy(self, temp_source_dir, temp_target_dir, create_skill_structure):
        """
        Verify that sync deletes entire target .claude/skills/ before copying.

        Maps to SKILL.md: "Step 1: Delete target directory"
        """
        # Arrange: Create existing target with old skills
        old_skills = {"old-skill-1": "0.5.0", "old-skill-2": "0.6.0"}
        create_skill_structure(temp_target_dir, old_skills)

        target_skills_dir = temp_target_dir / ".claude" / "skills"
        assert target_skills_dir.exists()
        assert len(list(target_skills_dir.iterdir())) == 2

        source_skills_dir = temp_source_dir / ".claude" / "skills"

        # Act: Simulate complete replacement
        shutil.rmtree(target_skills_dir)
        shutil.copytree(source_skills_dir, target_skills_dir)

        # Assert: Old skills gone, new skills present
        new_skills = {d.name for d in target_skills_dir.iterdir() if d.is_dir()}
        assert "old-skill-1" not in new_skills
        assert "old-skill-2" not in new_skills
        assert "skill-a" in new_skills

    def test_copies_all_skills_from_source(self, temp_source_dir, temp_target_dir):
        """
        Verify complete copy of .claude/skills/ directory.

        Maps to SKILL.md: "Step 2: Complete copy"
        """
        # Arrange
        source_skills = temp_source_dir / ".claude" / "skills"
        target_skills = temp_target_dir / ".claude" / "skills"

        # Act
        shutil.copytree(source_skills, target_skills)

        # Assert: All source skills present in target
        source_skill_names = {d.name for d in source_skills.iterdir() if d.is_dir()}
        target_skill_names = {d.name for d in target_skills.iterdir() if d.is_dir()}

        assert source_skill_names == target_skill_names
        assert "skill-a" in target_skill_names
        assert "skill-b" in target_skill_names
        assert "skill-k" in target_skill_names

    def test_includes_all_subdirectories(self, temp_source_dir, temp_target_dir):
        """
        Verify _scripts, _shared, _templates subdirectories are copied.

        Maps to SKILL.md: "includes all skills, _scripts/, _shared/, _templates/"
        """
        # Arrange
        source_skills = temp_source_dir / ".claude" / "skills"
        target_skills = temp_target_dir / ".claude" / "skills"

        # Act
        shutil.copytree(source_skills, target_skills)

        # Assert: Subdirectories present
        assert (target_skills / "_scripts").exists()
        assert (target_skills / "_shared").exists()
        assert (target_skills / "_templates").exists()

    def test_sync_is_fast_less_than_3_seconds(self, temp_source_dir, temp_target_dir):
        """
        Verify sync completes quickly (performance requirement).

        Maps to SKILL.md Performance: "~1-2 seconds"
        """
        import time

        source_skills = temp_source_dir / ".claude" / "skills"
        target_skills = temp_target_dir / ".claude" / "skills"

        start_time = time.time()

        # Act: Perform sync
        if target_skills.exists():
            shutil.rmtree(target_skills)
        shutil.copytree(source_skills, target_skills)

        elapsed = time.time() - start_time

        # Assert: Completes in < 3 seconds (generous for CI)
        assert elapsed < 3.0, f"Sync took {elapsed:.2f}s, expected < 3s"

    def test_sync_creates_exact_mirror(self, temp_source_dir, temp_target_dir, assert_directory_synced):
        """
        Verify target is exact mirror of source after sync.

        Maps to SKILL.md: "Predictable: Exact mirror"
        """
        # Arrange
        source_skills = temp_source_dir / ".claude" / "skills"
        target_skills = temp_target_dir / ".claude" / "skills"

        # Act
        shutil.copytree(source_skills, target_skills)

        # Assert: Directories match exactly
        assert_directory_synced(source_skills, target_skills)

    def test_preserves_file_content(self, temp_source_dir, temp_target_dir):
        """
        Verify file content is preserved exactly during copy.

        Maps to SKILL.md: "Complete directory copy"
        """
        # Arrange
        source_skill_file = temp_source_dir / ".claude" / "skills" / "skill-a" / "SKILL.md"
        source_content = source_skill_file.read_text()

        source_skills = temp_source_dir / ".claude" / "skills"
        target_skills = temp_target_dir / ".claude" / "skills"

        # Act
        shutil.copytree(source_skills, target_skills)

        # Assert
        target_skill_file = target_skills / "skill-a" / "SKILL.md"
        assert target_skill_file.read_text() == source_content


@pytest.mark.integration
class TestCompleteReplacementIntegration:
    """Integration tests for complete replacement workflow."""

    def test_full_sync_workflow(self, temp_source_dir, temp_target_dir, create_skill_structure):
        """
        Test complete end-to-end sync workflow.

        Simulates: rm -rf target && cp -r source target
        """
        # Arrange: Target has old version
        create_skill_structure(temp_target_dir, {"skill-a": "0.9.0"})

        source_skills = temp_source_dir / ".claude" / "skills"
        target_skills = temp_target_dir / ".claude" / "skills"

        # Act: Full sync
        if target_skills.exists():
            shutil.rmtree(target_skills)
        shutil.copytree(source_skills, target_skills)

        # Assert: Target matches source
        target_skill_file = target_skills / "skill-a" / "SKILL.md"
        assert "version: 1.0.0" in target_skill_file.read_text()
        assert len(list(target_skills.iterdir())) == len(list(source_skills.iterdir()))
