"""Unit tests for version.py module

Tests version validation, comparison, and frontmatter extraction logic.

Created: 2026-03-30 (Issue #406)
Coverage Target: >80%
"""

import pytest
from pathlib import Path
import tempfile
import sys

# Add parent directory to path

from version import (
    validate_version_format,
    get_version_from_frontmatter,
    check_version_field,
    compare_versions,
    VersionError
)


class TestValidateVersionFormat:
    """Test validate_version_format() function"""

    def test_valid_formats(self):
        """Test valid semantic version formats"""
        assert validate_version_format("1.0.0") is True
        assert validate_version_format("2.3.1") is True
        assert validate_version_format("10.20.30") is True
        assert validate_version_format("1.0") is True  # X.Y format
        assert validate_version_format("2.5") is True

    def test_invalid_formats(self):
        """Test invalid version formats"""
        assert validate_version_format("v1.0.0") is False  # v prefix not allowed
        assert validate_version_format("1") is False  # Missing minor
        assert validate_version_format("1.x.0") is False  # Non-numeric
        assert validate_version_format("1.0.0.0") is False  # Too many parts
        assert validate_version_format("") is False  # Empty string
        assert validate_version_format("abc") is False  # Not a version

    def test_non_string_input(self):
        """Test handling of non-string input"""
        assert validate_version_format(123) is False
        assert validate_version_format(None) is False
        assert validate_version_format([1, 0, 0]) is False


class TestGetVersionFromFrontmatter:
    """Test get_version_from_frontmatter() function"""

    def test_extract_version_from_valid_frontmatter(self):
        """Test extracting version from valid YAML frontmatter"""
        content = '''---
version: "1.4.0"
name: test-skill
---
# Skill
'''
        assert get_version_from_frontmatter(content) == "1.4.0"

    def test_extract_version_with_extra_fields(self):
        """Test extraction when frontmatter has multiple fields"""
        content = '''---
name: eval-plan
description: Plan validator
version: "2.0.1"
last-updated: 2026-03-30
---
# Eval Plan
'''
        assert get_version_from_frontmatter(content) == "2.0.1"

    def test_no_frontmatter(self):
        """Test handling of content without frontmatter"""
        content = "# Skill\n\nNo frontmatter here"
        assert get_version_from_frontmatter(content) is None

    def test_missing_version_field(self):
        """Test handling when frontmatter exists but no version field"""
        content = '''---
name: test-skill
description: A test
---
# Skill
'''
        assert get_version_from_frontmatter(content) is None

    def test_invalid_yaml(self):
        """Test handling of malformed YAML"""
        content = '''---
version: "1.0.0
name: broken
---
# Skill
'''
        assert get_version_from_frontmatter(content) is None


class TestCompareVersions:
    """Test compare_versions() function"""

    def test_less_than(self):
        """Test version comparison: v1 < v2"""
        assert compare_versions("1.0.0", "2.0.0") == -1
        assert compare_versions("1.5.0", "1.6.0") == -1
        assert compare_versions("1.0.0", "1.0.1") == -1
        assert compare_versions("1.0", "2.0") == -1

    def test_equal(self):
        """Test version comparison: v1 == v2"""
        assert compare_versions("1.0.0", "1.0.0") == 0
        assert compare_versions("2.3.1", "2.3.1") == 0
        assert compare_versions("1.0", "1.0") == 0

    def test_greater_than(self):
        """Test version comparison: v1 > v2"""
        assert compare_versions("2.0.0", "1.0.0") == 1
        assert compare_versions("1.6.0", "1.5.0") == 1
        assert compare_versions("1.0.1", "1.0.0") == 1
        assert compare_versions("2.0", "1.0") == 1

    def test_compare_mixed_formats(self):
        """Test comparison between X.Y and X.Y.Z formats"""
        assert compare_versions("1.0", "1.0.0") == 0  # 1.0 = 1.0.0
        assert compare_versions("1.0", "1.0.1") == -1  # 1.0 < 1.0.1
        assert compare_versions("1.1", "1.0.9") == 1  # 1.1 > 1.0.9

    def test_invalid_version_raises_error(self):
        """Test that invalid versions raise VersionError"""
        with pytest.raises(VersionError):
            compare_versions("v1.0.0", "1.0.0")

        with pytest.raises(VersionError):
            compare_versions("1.0.0", "invalid")

        with pytest.raises(VersionError):
            compare_versions("bad", "worse")


class TestCheckVersionField:
    """Test check_version_field() function"""

    def create_temp_skill_file(self, content: str) -> Path:
        """Helper to create temporary SKILL.md file"""
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.md',
            delete=False,
            encoding='utf-8'
        )
        temp_file.write(content)
        temp_file.close()
        return Path(temp_file.name)

    def test_valid_version_field(self):
        """Test checking a SKILL.md with valid version"""
        content = '''---
version: "1.4.0"
name: test-skill
---
# Test Skill
'''
        skill_path = self.create_temp_skill_file(content)

        try:
            result = check_version_field(skill_path)
            assert result['has_version'] is True
            assert result['version'] == "1.4.0"
            assert result['valid_format'] is True
            assert len(result['errors']) == 0
        finally:
            skill_path.unlink()  # Cleanup

    def test_missing_version_field(self):
        """Test checking a SKILL.md without version field"""
        content = '''---
name: test-skill
description: Test
---
# Test Skill
'''
        skill_path = self.create_temp_skill_file(content)

        try:
            result = check_version_field(skill_path)
            assert result['has_version'] is False
            assert result['version'] is None
            assert result['valid_format'] is False
            assert "Missing 'version' field" in result['errors'][0]
        finally:
            skill_path.unlink()

    def test_invalid_version_format(self):
        """Test checking a SKILL.md with invalid version format"""
        content = '''---
version: "v1.0.0"
name: test-skill
---
# Test Skill
'''
        skill_path = self.create_temp_skill_file(content)

        try:
            result = check_version_field(skill_path)
            assert result['has_version'] is True
            assert result['version'] == "v1.0.0"
            assert result['valid_format'] is False
            assert "Invalid version format" in result['errors'][0]
        finally:
            skill_path.unlink()

    def test_no_frontmatter(self):
        """Test checking a file without YAML frontmatter"""
        content = '''# Test Skill

No frontmatter here.
'''
        skill_path = self.create_temp_skill_file(content)

        try:
            result = check_version_field(skill_path)
            assert result['has_version'] is False
            assert "No YAML frontmatter found" in result['errors'][0]
        finally:
            skill_path.unlink()

    def test_file_not_found(self):
        """Test checking a non-existent file"""
        skill_path = Path("/nonexistent/file.md")
        result = check_version_field(skill_path)

        assert result['has_version'] is False
        assert "File not found" in result['errors'][0]


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
