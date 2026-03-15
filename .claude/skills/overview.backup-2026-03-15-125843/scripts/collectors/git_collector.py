#!/usr/bin/env python3
"""Git status data collection module.

Collects git repository information including branch, commits, and file changes.
Replaces collect-git.sh per ADR-003.

Example:
    >>> from collectors import git_collector
    >>> status = git_collector.collect_git_status()
    >>> print(f"Branch: {status['branch']}")
    >>> print(f"Uncommitted files: {status['staged'] + status['unstaged']}")
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List

# Add _shared to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / '_shared'))

from git_utils import run_git_command, get_current_branch


def collect_git_status() -> Dict[str, Any]:
    """
    Collect current git repository status.

    Gathers information about the current branch, latest commit,
    and counts of staged, unstaged, and untracked files.

    Returns:
        Dictionary with keys:
        - branch (str): Current branch name or "unknown"
        - commit (str): Short commit hash or "N/A"
        - commitMessage (str): Latest commit message
        - staged (int): Number of staged files
        - unstaged (int): Number of modified files
        - untracked (int): Number of untracked files

    Example:
        >>> status = collect_git_status()
        >>> print(status['branch'])
        main
        >>> print(f"Files to commit: {status['staged']}")
        2
    """
    # Default values for non-git repositories
    result = {
        'branch': 'unknown',
        'commit': 'N/A',
        'commitMessage': 'Git not available',
        'staged': 0,
        'unstaged': 0,
        'untracked': 0
    }

    # Check if we're in a git repository
    check_code, _, _ = run_git_command(['rev-parse', '--git-dir'])
    if check_code != 0:
        return result

    # Get branch name
    try:
        result['branch'] = get_current_branch()
    except RuntimeError:
        result['branch'] = 'unknown'

    # Get commit hash
    code, stdout, _ = run_git_command(['rev-parse', '--short', 'HEAD'])
    if code == 0:
        result['commit'] = stdout.strip()

    # Get commit message
    code, stdout, _ = run_git_command(['log', '-1', '--format=%s'])
    if code == 0:
        result['commitMessage'] = stdout.strip()

    # Count staged files
    code, stdout, _ = run_git_command(['diff', '--cached', '--name-only'])
    if code == 0:
        result['staged'] = len([f for f in stdout.strip().split('\n') if f])

    # Count unstaged files
    code, stdout, _ = run_git_command(['diff', '--name-only'])
    if code == 0:
        result['unstaged'] = len([f for f in stdout.strip().split('\n') if f])

    # Count untracked files
    code, stdout, _ = run_git_command(['ls-files', '--others', '--exclude-standard'])
    if code == 0:
        result['untracked'] = len([f for f in stdout.strip().split('\n') if f])

    return result


def collect_recent_commits(limit: int = 10) -> List[Dict[str, str]]:
    """
    Collect recent commit history.

    Args:
        limit: Maximum number of commits to return (default: 10)

    Returns:
        List of dictionaries with keys:
        - hash (str): Short commit hash
        - message (str): Commit message
        - date (str): Relative date (e.g., "2 hours ago")

    Example:
        >>> commits = collect_recent_commits(5)
        >>> for commit in commits:
        ...     print(f"{commit['hash']}: {commit['message']}")
        abc123: feat: add new feature
        def456: fix: resolve bug
    """
    # Check if we're in a git repository
    check_code, _, _ = run_git_command(['rev-parse', '--git-dir'])
    if check_code != 0:
        return []

    # Get commit history
    code, stdout, _ = run_git_command([
        'log',
        f'-{limit}',
        '--format={"hash":"%h","message":"%s","date":"%ar"}'
    ])

    if code != 0 or not stdout.strip():
        return []

    # Parse JSON lines into list
    commits = []
    for line in stdout.strip().split('\n'):
        if line:
            try:
                commit = json.loads(line)
                commits.append(commit)
            except json.JSONDecodeError:
                continue

    return commits


if __name__ == '__main__':
    # CLI interface for direct invocation
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'commits':
        # Print recent commits
        commits = collect_recent_commits()
        print(json.dumps(commits, indent=2))
    else:
        # Print git status
        status = collect_git_status()
        print(json.dumps(status, indent=2))
