#!/usr/bin/env python3
"""File system utilities for skill scripts.

Provides Python functions for common file system operations used across skill scripts.
All functions return structured data rather than printing output.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any
import yaml


def check_file_exists(path: str) -> bool:
    """
    Check if file or directory exists.

    Args:
        path: File or directory path (relative or absolute)

    Returns:
        True if path exists, False otherwise

    Example:
        >>> if check_file_exists('package.json'):
        ...     print("✅ Found package.json")
        ... else:
        ...     print("❌ No package.json")
        ✅ Found package.json
    """
    return Path(path).exists()


def find_files(pattern: str, root: str = '.') -> List[str]:
    """
    Find files matching glob pattern.

    Args:
        pattern: Glob pattern (e.g., '**/*.py', '*.md')
        root: Root directory to search from (default: current directory)

    Returns:
        List of matching file paths (relative to root)

    Example:
        >>> py_files = find_files('**/*.py', '.claude/skills')
        >>> print(f"Found {len(py_files)} Python files")
        Found 42 Python files
        >>> for f in py_files[:3]:
        ...     print(f"- {f}")
        - _shared/git_utils.py
        - _shared/fs_utils.py
        - _shared/format_utils.py
    """
    root_path = Path(root)

    if not root_path.exists():
        return []

    matches = []
    for path in root_path.glob(pattern):
        if path.is_file():
            # Return path relative to root
            rel_path = path.relative_to(root_path)
            matches.append(str(rel_path))

    return sorted(matches)


def read_yaml_frontmatter(file: str) -> Dict[str, Any]:
    """
    Parse YAML frontmatter from markdown file.

    Args:
        file: Path to markdown file

    Returns:
        Dict of frontmatter fields, empty dict if no frontmatter found

    Example:
        >>> metadata = read_yaml_frontmatter('.claude/skills/sync/SKILL.md')
        >>> print(f"Skill: {metadata['name']}")
        Skill: sync
        >>> print(f"Version: {metadata.get('version', 'unknown')}")
        Version: 2.3.0
    """
    file_path = Path(file)

    if not file_path.exists():
        return {}

    content = file_path.read_text(encoding='utf-8')

    # Match YAML frontmatter: ---\n...\n---
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}

    yaml_content = match.group(1)

    try:
        return yaml.safe_load(yaml_content) or {}
    except yaml.YAMLError:
        return {}


def count_files(directory: str, pattern: str = '*') -> int:
    """
    Count files matching pattern in directory.

    Args:
        directory: Directory path to search
        pattern: Glob pattern (default: '*' for all files)

    Returns:
        Count of matching files (non-recursive)

    Example:
        >>> ts_count = count_files('src', '*.ts')
        >>> js_count = count_files('src', '*.js')
        >>> print(f"TypeScript: {ts_count}, JavaScript: {js_count}")
        TypeScript: 42, JavaScript: 8
    """
    dir_path = Path(directory)

    if not dir_path.exists() or not dir_path.is_dir():
        return 0

    count = 0
    for path in dir_path.glob(pattern):
        if path.is_file():
            count += 1

    return count
