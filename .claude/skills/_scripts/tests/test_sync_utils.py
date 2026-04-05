#!/usr/bin/env python3
"""
Unit tests for sync.py utilities.

Tests for Issue #401 framework-only filtering and sync modes.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path

from utils.sync import (
    parse_skill_metadata,
    filter_framework_only_skills,
    sync_skills,
    SyncMode,
    SkillMetadata
)


class TestParseSkillMetadata(unittest.TestCase):
    """Test YAML metadata parsing"""

    def test_parse_valid_yaml(self):
        """Test parsing valid YAML frontmatter"""
        content = """---
name: test-skill
version: "1.0.0"
framework-only: true
user-invocable: true
---
# Test Skill Content
"""
        metadata = parse_skill_metadata(content)

        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.name, "test-skill")
        self.assertEqual(metadata.version, "1.0.0")
        self.assertTrue(metadata.framework_only)
        self.assertTrue(metadata.user_invocable)

    def test_parse_without_framework_only(self):
        """Test default framework-only is False"""
        content = """---
name: regular-skill
version: "2.0.0"
---
# Regular Skill
"""
        metadata = parse_skill_metadata(content)

        self.assertIsNotNone(metadata)
        self.assertFalse(metadata.framework_only)

    def test_parse_no_yaml(self):
        """Test file without YAML frontmatter"""
        content = "# Just a markdown file\nNo YAML here"

        metadata = parse_skill_metadata(content)

        self.assertIsNone(metadata)

    def test_parse_invalid_yaml(self):
        """Test handling of invalid YAML"""
        content = """---
name: bad-skill
invalid yaml: [unclosed
---
Content
"""
        metadata = parse_skill_metadata(content)

        self.assertIsNone(metadata)


class TestFilterFrameworkOnlySkills(unittest.TestCase):
    """Test framework-only skill filtering (Issue #401)"""

    def setUp(self):
        """Create temporary skill directories for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.skills_dir = Path(self.temp_dir) / ".claude" / "skills"
        self.skills_dir.mkdir(parents=True)

        # Create test skills
        self.create_skill("start-issue", framework_only=False)
        self.create_skill("update-skills", framework_only=True)
        self.create_skill("review", framework_only=False)
        self.create_skill("update-framework", framework_only=True)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def create_skill(self, name: str, framework_only: bool):
        """Create a test skill directory with SKILL.md"""
        skill_dir = self.skills_dir / name
        skill_dir.mkdir()

        skill_md = skill_dir / "SKILL.md"
        content = f"""---
name: {name}
version: "1.0.0"
framework-only: {str(framework_only).lower()}
---
# {name.title()} Skill
"""
        skill_md.write_text(content)

    def test_filter_framework_only_skills(self):
        """Test filtering excludes framework-only skills"""
        skill_dirs = list(self.skills_dir.iterdir())

        to_sync, excluded = filter_framework_only_skills(skill_dirs)

        # Should sync 2 skills (start-issue, review)
        self.assertEqual(len(to_sync), 2)
        to_sync_names = [s.name for s in to_sync]
        self.assertIn("start-issue", to_sync_names)
        self.assertIn("review", to_sync_names)

        # Should exclude 2 skills (update-skills, update-framework)
        self.assertEqual(len(excluded), 2)
        self.assertIn("update-skills", excluded)
        self.assertIn("update-framework", excluded)

    def test_filter_empty_list(self):
        """Test filtering with empty input"""
        to_sync, excluded = filter_framework_only_skills([])

        self.assertEqual(len(to_sync), 0)
        self.assertEqual(len(excluded), 0)

    def test_filter_missing_skill_md(self):
        """Test handling of directory without SKILL.md"""
        # Create skill dir without SKILL.md
        bad_skill = self.skills_dir / "no-skill-md"
        bad_skill.mkdir()

        skill_dirs = list(self.skills_dir.iterdir())
        to_sync, excluded = filter_framework_only_skills(skill_dirs)

        # Should skip the bad skill
        self.assertEqual(len(to_sync), 2)
        self.assertEqual(len(excluded), 2)


class TestSyncSkills(unittest.TestCase):
    """Test sync_skills function"""

    def setUp(self):
        """Create source and target directories"""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "source" / ".claude" / "skills"
        self.target_dir = Path(self.temp_dir) / "target" / ".claude" / "skills"

        self.source_dir.mkdir(parents=True)
        self.target_dir.mkdir(parents=True)

        # Create test skills in source
        self.create_skill(self.source_dir, "skill-a", framework_only=False)
        self.create_skill(self.source_dir, "skill-b", framework_only=False)
        self.create_skill(self.source_dir, "update-foo", framework_only=True)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def create_skill(self, parent_dir: Path, name: str, framework_only: bool):
        """Create a test skill"""
        skill_dir = parent_dir / name
        skill_dir.mkdir()

        skill_md = skill_dir / "SKILL.md"
        content = f"""---
name: {name}
version: "1.0.0"
framework-only: {str(framework_only).lower()}
---
# {name}
"""
        skill_md.write_text(content)

    def test_sync_replace_mode(self):
        """Test complete replacement sync mode"""
        result = sync_skills(
            self.source_dir,
            self.target_dir,
            mode=SyncMode.REPLACE,
            dry_run=False
        )

        # Should sync 2 non-framework skills
        self.assertEqual(result.synced_count, 2)
        self.assertEqual(len(result.excluded_framework), 1)
        self.assertIn("update-foo", result.excluded_framework)

        # Verify target has 2 skills
        target_skills = list(self.target_dir.iterdir())
        self.assertEqual(len(target_skills), 2)

    def test_sync_dry_run(self):
        """Test dry run doesn't modify target"""
        # Create existing skill in target
        (self.target_dir / "existing-skill").mkdir()

        result = sync_skills(
            self.source_dir,
            self.target_dir,
            mode=SyncMode.REPLACE,
            dry_run=True
        )

        # Should report what would be synced
        self.assertEqual(result.synced_count, 2)

        # Target should still have only 1 skill (unchanged)
        target_skills = list(self.target_dir.iterdir())
        self.assertEqual(len(target_skills), 1)

    def test_sync_selective_mode(self):
        """Test selective sync with skill filter"""
        result = sync_skills(
            self.source_dir,
            self.target_dir,
            mode=SyncMode.SELECTIVE,
            selected_skills=["skill-a"],
            dry_run=False
        )

        # Should sync only skill-a
        self.assertEqual(result.synced_count, 1)

        # Verify target has 1 skill
        target_skills = list(self.target_dir.iterdir())
        self.assertEqual(len(target_skills), 1)
        self.assertEqual(target_skills[0].name, "skill-a")


if __name__ == "__main__":
    unittest.main()
