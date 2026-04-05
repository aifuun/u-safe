#!/usr/bin/env python3
"""Git command wrappers for skill scripts.

Provides Python functions for common git operations used across skill scripts.
All functions return structured data (tuples/dicts) rather than printing output.
"""

import subprocess
import json
from typing import Tuple, Dict, List, Any


def run_git_command(args: list[str]) -> Tuple[int, str, str]:
    """
    Run git command and return (exit_code, stdout, stderr).

    Args:
        args: Git command arguments (e.g., ['status', '--short'])

    Returns:
        Tuple of (exit_code, stdout, stderr)

    Example:
        >>> code, out, err = run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
        >>> if code == 0:
        ...     print(f"Current branch: {out.strip()}")
        Current branch: main
    """
    result = subprocess.run(
        ['git'] + args,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def get_current_branch() -> str:
    """
    Get current git branch name.

    Returns:
        Branch name (e.g., "main", "feature/123-my-feature")

    Raises:
        RuntimeError: If not in a git repository or git command fails

    Example:
        >>> branch = get_current_branch()
        >>> print(f"On branch: {branch}")
        On branch: main
    """
    code, stdout, stderr = run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])

    if code != 0:
        raise RuntimeError(f"Failed to get current branch: {stderr}")

    return stdout.strip()


def check_sync_status() -> bool:
    """
    Check if current branch is synced with origin/main.

    Returns:
        True if local branch is up-to-date with origin/main, False otherwise

    Example:
        >>> if check_sync_status():
        ...     print("✅ Branch is synced")
        ... else:
        ...     print("⚠️ Need to sync with origin/main")
        ✅ Branch is synced
    """
    # Fetch latest from origin (quietly)
    fetch_code, _, _ = run_git_command(['fetch', 'origin', 'main'])
    if fetch_code != 0:
        return False

    # Check if origin/main is ancestor of HEAD
    code, _, _ = run_git_command(['merge-base', '--is-ancestor', 'origin/main', 'HEAD'])

    return code == 0


def get_commit_info(ref: str = 'HEAD') -> Dict[str, str]:
    """
    Get commit information for a given ref.

    Args:
        ref: Git reference (default: 'HEAD')

    Returns:
        Dict with keys: hash, author, date, message

    Example:
        >>> info = get_commit_info('HEAD')
        >>> print(f"Last commit: {info['message']}")
        Last commit: feat: add shared utilities
    """
    # Get commit info in JSON format
    format_str = '{"hash":"%H","author":"%an","date":"%ai","message":"%s"}'
    code, stdout, stderr = run_git_command(['log', '-1', f'--pretty=format:{format_str}', ref])

    if code != 0:
        raise RuntimeError(f"Failed to get commit info for {ref}: {stderr}")

    return json.loads(stdout)


def get_branch_commits(base: str = 'origin/main', head: str = 'HEAD') -> List[Dict[str, str]]:
    """
    Get list of commits between base and head refs.

    Args:
        base: Base reference (default: 'origin/main')
        head: Head reference (default: 'HEAD')

    Returns:
        List of dicts with keys: hash, author, date, message

    Example:
        >>> commits = get_branch_commits('origin/main', 'HEAD')
        >>> print(f"Branch has {len(commits)} commits")
        Branch has 3 commits
        >>> for commit in commits:
        ...     print(f"- {commit['message']}")
        - feat: add git utilities
        - feat: add fs utilities
        - docs: update README
    """
    # Get commits in range as JSON array
    format_str = '{"hash":"%H","author":"%an","date":"%ai","message":"%s"}'
    code, stdout, stderr = run_git_command([
        'log',
        f'{base}..{head}',
        f'--pretty=format:{format_str}'
    ])

    if code != 0:
        raise RuntimeError(f"Failed to get commits {base}..{head}: {stderr}")

    if not stdout.strip():
        return []

    # Parse each line as JSON
    commits = []
    for line in stdout.strip().split('\n'):
        if line:
            commits.append(json.loads(line))

    return commits
