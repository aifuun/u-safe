#!/usr/bin/env python3
"""Testing utilities for skill scripts.

Provides helper functions for writing tests including fixtures,
temporary directories, and mock git repositories.
"""

import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Generator
from contextlib import contextmanager


@contextmanager
def temp_directory() -> Generator[Path, None, None]:
    """
    Create temporary directory for tests.

    Yields:
        Path to temporary directory (automatically cleaned up)

    Example:
        >>> with temp_directory() as tmpdir:
        ...     test_file = tmpdir / 'test.txt'
        ...     test_file.write_text('Hello')
        ...     assert test_file.exists()
        >>> # tmpdir is automatically removed after with block
    """
    tmpdir = tempfile.mkdtemp()
    try:
        yield Path(tmpdir)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


@contextmanager
def mock_git_repo() -> Generator[Path, None, None]:
    """
    Create temporary git repository for testing.

    Yields:
        Path to temporary git repo (automatically cleaned up)

    Example:
        >>> with mock_git_repo() as repo:
        ...     # Create a test file
        ...     test_file = repo / 'test.txt'
        ...     test_file.write_text('content')
        ...     # Commit it
        ...     subprocess.run(['git', 'add', '.'], cwd=repo)
        ...     subprocess.run(['git', 'commit', '-m', 'test'], cwd=repo)
        ...     # Verify commit exists
        ...     result = subprocess.run(['git', 'log', '--oneline'],
        ...                           cwd=repo, capture_output=True, text=True)
        ...     assert 'test' in result.stdout
    """
    with temp_directory() as tmpdir:
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=tmpdir, check=True,
                      capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'],
                      cwd=tmpdir, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'],
                      cwd=tmpdir, check=True, capture_output=True)

        # Create initial commit
        readme = tmpdir / 'README.md'
        readme.write_text('# Test Repository\n')
        subprocess.run(['git', 'add', '.'], cwd=tmpdir, check=True,
                      capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'],
                      cwd=tmpdir, check=True, capture_output=True)

        yield tmpdir


def create_test_markdown(path: Path, frontmatter: dict = None, content: str = '') -> None:
    """
    Create test markdown file with YAML frontmatter.

    Args:
        path: Path where to create file
        frontmatter: Dict of frontmatter fields (optional)
        content: Markdown content after frontmatter (optional)

    Example:
        >>> with temp_directory() as tmpdir:
        ...     test_file = tmpdir / 'test.md'
        ...     create_test_markdown(
        ...         test_file,
        ...         frontmatter={'name': 'test-skill', 'version': '1.0.0'},
        ...         content='## Overview\\n\\nThis is a test skill.'
        ...     )
        ...     assert test_file.exists()
        ...     text = test_file.read_text()
        ...     assert 'name: test-skill' in text
    """
    lines = []

    if frontmatter:
        lines.append('---')
        for key, value in frontmatter.items():
            if isinstance(value, str):
                lines.append(f'{key}: {value}')
            else:
                lines.append(f'{key}: {value}')
        lines.append('---')
        lines.append('')

    if content:
        lines.append(content)

    path.write_text('\n'.join(lines), encoding='utf-8')
