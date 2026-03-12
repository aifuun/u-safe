#!/usr/bin/env python3
"""Output formatting utilities for skill scripts.

Provides Python functions for formatting terminal output, including emoji status
indicators, ASCII tables, and text truncation.
"""

from typing import List, Any


def format_status(status: str) -> str:
    """
    Format status with emoji indicator.

    Args:
        status: Status string (success/pass/ok, fail/error, pending/waiting, etc.)

    Returns:
        Status with appropriate emoji prefix

    Example:
        >>> print(format_status("success"))
        ✅ success
        >>> print(format_status("error"))
        ❌ error
        >>> print(format_status("pending"))
        ⏳ pending
    """
    status_lower = status.lower().strip()

    # Success indicators
    if status_lower in ('success', 'pass', 'passed', 'ok', 'done', 'complete', 'synced'):
        return f"✅ {status}"

    # Failure indicators
    if status_lower in ('fail', 'failed', 'error', 'failure'):
        return f"❌ {status}"

    # Warning indicators
    if status_lower in ('warning', 'warn', 'need sync', 'outdated'):
        return f"⚠️ {status}"

    # Pending/In-progress indicators
    if status_lower in ('pending', 'waiting', 'in progress', 'running'):
        return f"⏳ {status}"

    # Info indicators
    if status_lower in ('info', 'note', 'no tests'):
        return f"ℹ️ {status}"

    # Default: no emoji
    return status


def format_table(headers: List[str], rows: List[List[Any]]) -> str:
    """
    Format data as ASCII table.

    Args:
        headers: List of column headers
        rows: List of rows, each row is list of values

    Returns:
        Formatted ASCII table string

    Example:
        >>> headers = ['Name', 'Status', 'Count']
        >>> rows = [
        ...     ['git_utils.py', 'Done', 5],
        ...     ['fs_utils.py', 'Done', 4],
        ...     ['format_utils.py', 'In Progress', 3]
        ... ]
        >>> print(format_table(headers, rows))
        Name              | Status      | Count
        ------------------|-------------|-------
        git_utils.py      | Done        | 5
        fs_utils.py       | Done        | 4
        format_utils.py   | In Progress | 3
    """
    if not headers or not rows:
        return ""

    # Convert all values to strings
    str_headers = [str(h) for h in headers]
    str_rows = [[str(cell) for cell in row] for row in rows]

    # Calculate column widths (max of header and all row values)
    col_widths = []
    for i, header in enumerate(str_headers):
        max_width = len(header)
        for row in str_rows:
            if i < len(row):
                max_width = max(max_width, len(row[i]))
        col_widths.append(max_width)

    # Format header
    header_line = ' | '.join(
        header.ljust(width)
        for header, width in zip(str_headers, col_widths)
    )

    # Format separator
    separator = '-|-'.join('-' * width for width in col_widths)

    # Format rows
    row_lines = []
    for row in str_rows:
        # Pad row if it has fewer columns than headers
        padded_row = row + [''] * (len(headers) - len(row))
        row_line = ' | '.join(
            cell.ljust(width)
            for cell, width in zip(padded_row, col_widths)
        )
        row_lines.append(row_line)

    # Combine all parts
    return '\n'.join([header_line, separator] + row_lines)


def truncate_text(text: str, max_len: int, suffix: str = '...') -> str:
    """
    Truncate text to max length with ellipsis.

    Args:
        text: Text to truncate
        max_len: Maximum length (including suffix)
        suffix: Suffix to add when truncated (default: '...')

    Returns:
        Truncated text with suffix if longer than max_len, otherwise original text

    Example:
        >>> long_text = "This is a very long commit message that needs truncation"
        >>> print(truncate_text(long_text, 30))
        This is a very long comm...
        >>> print(truncate_text("Short", 30))
        Short
    """
    if len(text) <= max_len:
        return text

    # Ensure we have room for suffix
    if max_len <= len(suffix):
        return suffix[:max_len]

    truncate_at = max_len - len(suffix)
    return text[:truncate_at] + suffix
