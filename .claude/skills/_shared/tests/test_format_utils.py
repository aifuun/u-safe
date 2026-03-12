#!/usr/bin/env python3
"""Unit tests for format_utils module."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from format_utils import (
    format_status,
    format_table,
    truncate_text
)


class TestFormatStatus:
    """Tests for format_status function."""

    def test_success_status(self):
        """Test formatting success status."""
        assert format_status('success').startswith('✅')
        assert format_status('pass').startswith('✅')
        assert format_status('passed').startswith('✅')
        assert format_status('ok').startswith('✅')
        assert format_status('done').startswith('✅')
        assert format_status('complete').startswith('✅')
        assert format_status('synced').startswith('✅')

    def test_failure_status(self):
        """Test formatting failure status."""
        assert format_status('fail').startswith('❌')
        assert format_status('failed').startswith('❌')
        assert format_status('error').startswith('❌')
        assert format_status('failure').startswith('❌')

    def test_warning_status(self):
        """Test formatting warning status."""
        assert format_status('warning').startswith('⚠️')
        assert format_status('warn').startswith('⚠️')
        assert format_status('need sync').startswith('⚠️')
        assert format_status('outdated').startswith('⚠️')

    def test_pending_status(self):
        """Test formatting pending status."""
        assert format_status('pending').startswith('⏳')
        assert format_status('waiting').startswith('⏳')
        assert format_status('in progress').startswith('⏳')
        assert format_status('running').startswith('⏳')

    def test_info_status(self):
        """Test formatting info status."""
        assert format_status('info').startswith('ℹ️')
        assert format_status('note').startswith('ℹ️')
        assert format_status('no tests').startswith('ℹ️')

    def test_unknown_status(self):
        """Test formatting unknown status (no emoji)."""
        result = format_status('custom status')
        assert result == 'custom status'
        assert not result.startswith('✅')
        assert not result.startswith('❌')

    def test_case_insensitive(self):
        """Test that status matching is case-insensitive."""
        assert format_status('SUCCESS').startswith('✅')
        assert format_status('Success').startswith('✅')
        assert format_status('FAILED').startswith('❌')
        assert format_status('Failed').startswith('❌')

    def test_preserves_original_text(self):
        """Test that original status text is preserved."""
        result = format_status('success')
        assert 'success' in result


class TestFormatTable:
    """Tests for format_table function."""

    def test_simple_table(self):
        """Test formatting simple table."""
        headers = ['Name', 'Age']
        rows = [
            ['Alice', 30],
            ['Bob', 25]
        ]
        result = format_table(headers, rows)

        # Check that result contains all data
        assert 'Name' in result
        assert 'Age' in result
        assert 'Alice' in result
        assert 'Bob' in result
        assert '30' in result
        assert '25' in result

        # Check that it has separator line
        assert '-' in result

    def test_table_with_varying_lengths(self):
        """Test table with varying column widths."""
        headers = ['Short', 'Very Long Header']
        rows = [
            ['A', 'B'],
            ['C', 'D']
        ]
        result = format_table(headers, rows)

        lines = result.split('\n')
        # All lines should have similar length (accounting for separators)
        # The columns should be properly aligned
        assert 'Very Long Header' in lines[0]

    def test_empty_table(self):
        """Test empty table."""
        assert format_table([], []) == ""
        assert format_table(['Header'], []) == ""

    def test_table_alignment(self):
        """Test that columns are properly aligned."""
        headers = ['Name', 'Status', 'Count']
        rows = [
            ['git_utils.py', 'Done', 5],
            ['fs_utils.py', 'Done', 4]
        ]
        result = format_table(headers, rows)

        lines = result.split('\n')
        # Header and separator should exist
        assert len(lines) >= 3

        # Check column separator exists
        assert '|' in lines[0]
        assert '|' in lines[1]
        assert '|' in lines[2]

    def test_handles_different_types(self):
        """Test that table handles different data types."""
        headers = ['String', 'Int', 'Float', 'Bool']
        rows = [
            ['text', 42, 3.14, True],
            ['more', 0, 2.71, False]
        ]
        result = format_table(headers, rows)

        # All values should be converted to strings
        assert 'text' in result
        assert '42' in result
        assert '3.14' in result
        assert 'True' in result

    def test_uneven_rows(self):
        """Test table with rows having fewer columns than headers."""
        headers = ['Col1', 'Col2', 'Col3']
        rows = [
            ['A', 'B', 'C'],
            ['D', 'E'],  # Missing Col3
            ['F']  # Missing Col2 and Col3
        ]
        result = format_table(headers, rows)

        # Should not crash, should handle gracefully
        assert 'Col1' in result
        assert 'Col2' in result
        assert 'Col3' in result


class TestTruncateText:
    """Tests for truncate_text function."""

    def test_truncate_long_text(self):
        """Test truncating text longer than max length."""
        text = "This is a very long text that needs to be truncated"
        result = truncate_text(text, 20)

        assert len(result) == 20
        assert result.endswith('...')
        assert result.startswith('This is a very')

    def test_keep_short_text(self):
        """Test that short text is not truncated."""
        text = "Short text"
        result = truncate_text(text, 20)

        assert result == text
        assert not result.endswith('...')

    def test_exact_length(self):
        """Test text exactly at max length."""
        text = "Exactly20Characters!"
        result = truncate_text(text, 20)

        assert result == text

    def test_custom_suffix(self):
        """Test with custom suffix."""
        text = "Long text that needs truncation"
        result = truncate_text(text, 15, suffix='...')

        assert len(result) == 15
        assert result.endswith('...')

    def test_very_short_max_len(self):
        """Test with max_len shorter than suffix."""
        text = "Some text"
        result = truncate_text(text, 2, suffix='...')

        # Should return truncated suffix
        assert len(result) == 2
        assert result == '..'

    def test_max_len_equals_suffix(self):
        """Test when max_len equals suffix length."""
        text = "Some text"
        result = truncate_text(text, 3, suffix='...')

        assert len(result) == 3
        assert result == '...'

    def test_empty_text(self):
        """Test with empty text."""
        result = truncate_text('', 10)
        assert result == ''

    def test_preserves_beginning(self):
        """Test that beginning of text is preserved."""
        text = "Important information at the start"
        result = truncate_text(text, 20)

        assert result.startswith('Important')

    def test_no_truncation_needed(self):
        """Test that exactly sized text is not modified."""
        text = "12345"
        result = truncate_text(text, 5)
        assert result == text
        assert not result.endswith('...')
