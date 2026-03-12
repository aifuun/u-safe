#!/usr/bin/env python3
"""Unit tests for fs_utils module."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fs_utils import (
    check_file_exists,
    find_files,
    read_yaml_frontmatter,
    count_files
)
from test_utils import temp_directory, create_test_markdown


class TestCheckFileExists:
    """Tests for check_file_exists function."""

    def test_existing_file(self):
        """Test checking existing file."""
        with temp_directory() as tmpdir:
            test_file = tmpdir / 'test.txt'
            test_file.write_text('content')
            assert check_file_exists(str(test_file)) is True

    def test_nonexistent_file(self):
        """Test checking non-existent file."""
        assert check_file_exists('/nonexistent/file/path.txt') is False

    def test_existing_directory(self):
        """Test checking existing directory."""
        with temp_directory() as tmpdir:
            test_dir = tmpdir / 'testdir'
            test_dir.mkdir()
            assert check_file_exists(str(test_dir)) is True

    def test_relative_path(self):
        """Test with relative path."""
        # This file should exist (the test file itself)
        assert check_file_exists(__file__) is True

    def test_returns_boolean(self):
        """Test that function returns boolean."""
        result = check_file_exists('/some/path')
        assert isinstance(result, bool)


class TestFindFiles:
    """Tests for find_files function."""

    def test_find_all_files(self):
        """Test finding all files with * pattern."""
        with temp_directory() as tmpdir:
            # Create test files
            (tmpdir / 'file1.txt').write_text('content')
            (tmpdir / 'file2.txt').write_text('content')
            (tmpdir / 'file3.py').write_text('content')

            files = find_files('*', str(tmpdir))
            assert len(files) == 3
            assert 'file1.txt' in files
            assert 'file2.txt' in files
            assert 'file3.py' in files

    def test_find_by_extension(self):
        """Test finding files by extension."""
        with temp_directory() as tmpdir:
            # Create test files
            (tmpdir / 'test1.py').write_text('content')
            (tmpdir / 'test2.py').write_text('content')
            (tmpdir / 'test.txt').write_text('content')

            files = find_files('*.py', str(tmpdir))
            assert len(files) == 2
            assert all(f.endswith('.py') for f in files)

    def test_recursive_search(self):
        """Test recursive file search."""
        with temp_directory() as tmpdir:
            # Create nested structure
            subdir = tmpdir / 'subdir'
            subdir.mkdir()
            (tmpdir / 'root.py').write_text('content')
            (subdir / 'nested.py').write_text('content')

            files = find_files('**/*.py', str(tmpdir))
            assert len(files) == 2
            assert 'root.py' in files
            assert 'subdir/nested.py' in files or 'subdir\\nested.py' in files

    def test_nonexistent_directory(self):
        """Test with non-existent directory."""
        files = find_files('*.py', '/nonexistent/directory')
        assert files == []

    def test_empty_directory(self):
        """Test with empty directory."""
        with temp_directory() as tmpdir:
            files = find_files('*.py', str(tmpdir))
            assert files == []

    def test_returns_sorted_list(self):
        """Test that results are sorted."""
        with temp_directory() as tmpdir:
            # Create files in non-alphabetical order
            (tmpdir / 'zebra.txt').write_text('content')
            (tmpdir / 'apple.txt').write_text('content')
            (tmpdir / 'banana.txt').write_text('content')

            files = find_files('*.txt', str(tmpdir))
            assert files == sorted(files)


class TestReadYamlFrontmatter:
    """Tests for read_yaml_frontmatter function."""

    def test_read_valid_frontmatter(self):
        """Test reading valid YAML frontmatter."""
        with temp_directory() as tmpdir:
            test_file = tmpdir / 'test.md'
            create_test_markdown(
                test_file,
                frontmatter={'name': 'test-skill', 'version': '1.0.0'},
                content='## Overview\n\nContent here.'
            )

            metadata = read_yaml_frontmatter(str(test_file))
            assert isinstance(metadata, dict)
            assert metadata['name'] == 'test-skill'
            assert metadata['version'] == '1.0.0'

    def test_no_frontmatter(self):
        """Test file without frontmatter."""
        with temp_directory() as tmpdir:
            test_file = tmpdir / 'test.md'
            test_file.write_text('# Regular Markdown\n\nNo frontmatter here.')

            metadata = read_yaml_frontmatter(str(test_file))
            assert metadata == {}

    def test_nonexistent_file(self):
        """Test with non-existent file."""
        metadata = read_yaml_frontmatter('/nonexistent/file.md')
        assert metadata == {}

    def test_complex_frontmatter(self):
        """Test reading complex frontmatter with nested data."""
        with temp_directory() as tmpdir:
            test_file = tmpdir / 'test.md'
            frontmatter_text = """---
name: complex-skill
version: 2.0.0
tags:
  - python
  - testing
config:
  enabled: true
  threshold: 80
---

# Content
"""
            test_file.write_text(frontmatter_text)

            metadata = read_yaml_frontmatter(str(test_file))
            assert metadata['name'] == 'complex-skill'
            assert isinstance(metadata['tags'], list)
            assert 'python' in metadata['tags']
            assert isinstance(metadata['config'], dict)
            assert metadata['config']['enabled'] is True
            assert metadata['config']['threshold'] == 80

    def test_invalid_yaml(self):
        """Test with invalid YAML."""
        with temp_directory() as tmpdir:
            test_file = tmpdir / 'test.md'
            test_file.write_text("""---
invalid: yaml: content:
---

Content
""")
            metadata = read_yaml_frontmatter(str(test_file))
            assert metadata == {}


class TestCountFiles:
    """Tests for count_files function."""

    def test_count_all_files(self):
        """Test counting all files."""
        with temp_directory() as tmpdir:
            # Create test files
            (tmpdir / 'file1.txt').write_text('content')
            (tmpdir / 'file2.txt').write_text('content')
            (tmpdir / 'file3.py').write_text('content')

            count = count_files(str(tmpdir), '*')
            assert count == 3

    def test_count_by_extension(self):
        """Test counting files by extension."""
        with temp_directory() as tmpdir:
            # Create test files
            (tmpdir / 'test1.py').write_text('content')
            (tmpdir / 'test2.py').write_text('content')
            (tmpdir / 'test.txt').write_text('content')

            count = count_files(str(tmpdir), '*.py')
            assert count == 2

    def test_nonexistent_directory(self):
        """Test with non-existent directory."""
        count = count_files('/nonexistent/directory', '*.py')
        assert count == 0

    def test_empty_directory(self):
        """Test with empty directory."""
        with temp_directory() as tmpdir:
            count = count_files(str(tmpdir), '*.py')
            assert count == 0

    def test_not_recursive(self):
        """Test that count is not recursive."""
        with temp_directory() as tmpdir:
            # Create files in root and subdirectory
            (tmpdir / 'root.py').write_text('content')
            subdir = tmpdir / 'subdir'
            subdir.mkdir()
            (subdir / 'nested.py').write_text('content')

            # Should only count root.py, not nested.py
            count = count_files(str(tmpdir), '*.py')
            assert count == 1

    def test_returns_integer(self):
        """Test that function returns integer."""
        with temp_directory() as tmpdir:
            count = count_files(str(tmpdir), '*')
            assert isinstance(count, int)
            assert count >= 0
