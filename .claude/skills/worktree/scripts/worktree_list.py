#!/usr/bin/env python3
"""List all git worktrees with formatted table display."""

import os
import sys
from pathlib import Path

# Add _scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_scripts"))

from git.worktree import list_worktrees, detect_current_worktree


def format_path(path: str, max_length: int = 30) -> str:
    """Truncate path if too long, preserving important parts.

    Args:
        path: Full path string
        max_length: Maximum length before truncation

    Returns:
        Formatted path with ellipsis if truncated
    """
    if len(path) <= max_length:
        return path

    # Try to preserve the end (most specific part)
    parts = path.split('/')
    result = parts[-1]

    for part in reversed(parts[:-1]):
        if len(result) + len(part) + 4 < max_length:  # +4 for ".../"
            result = part + '/' + result
        else:
            break

    return '...' + result if not result.startswith('/') else result


def get_status_emoji(status: str, is_current: bool) -> str:
    """Get emoji for worktree status.

    Args:
        status: Worktree status string
        is_current: Whether this is the current worktree

    Returns:
        Emoji string representing status
    """
    if is_current:
        return '🟡'
    elif status == 'main':
        return '🏠'
    elif status == 'active':
        return '🟢'
    elif status == 'merged':
        return '✅'
    elif status == 'stale':
        return '🔴'
    else:
        return '⚪'


def print_worktree_table(worktrees: list, current_path: str = None) -> None:
    """Print worktrees as formatted ASCII table.

    Args:
        worktrees: List of worktree dicts
        current_path: Path of current worktree (if any)
    """
    if not worktrees:
        print("\n📋 No worktrees found\n")
        print("Create one with: /start-issue <number>\n")
        return

    print("\n📋 Git Worktrees:\n")

    # Table header
    print("┌────┬────────┬──────────────────────────────────┬─────────────────────────────┬──────────┐")
    print("│ #  │ Issue  │ Branch                           │ Path                        │ Status   │")
    print("├────┼────────┼──────────────────────────────────┼─────────────────────────────┼──────────┤")

    # Table rows
    for idx, wt in enumerate(worktrees, 1):
        issue = wt.get('issue_number')
        issue_str = f"#{issue}" if issue else "main"

        branch = wt['branch']
        if len(branch) > 35:
            branch = branch[:32] + "..."

        path = format_path(wt['path'], max_length=30)

        status = wt.get('status', 'unknown')
        is_current = current_path and os.path.samefile(wt['path'], current_path)
        emoji = get_status_emoji(status, is_current)

        status_str = "Current" if is_current else status.capitalize()

        print(f"│ {idx:<2} │ {issue_str:<6} │ {branch:<32} │ {path:<27} │ {emoji} {status_str:<6} │")

    print("└────┴────────┴──────────────────────────────────┴─────────────────────────────┴──────────┘")

    # Show current worktree
    if current_path:
        for idx, wt in enumerate(worktrees, 1):
            if os.path.samefile(wt['path'], current_path):
                issue_num = wt.get('issue_number')
                if issue_num:
                    print(f"\n💡 Current: #{idx} (Issue #{issue_num})")
                else:
                    print(f"\n💡 Current: #{idx} (Main repository)")
                break

    print()


def main() -> None:
    """CLI entry point."""
    try:
        worktrees = list_worktrees()
        current = detect_current_worktree()
        current_path = current['path'] if current else None

        print_worktree_table(worktrees, current_path)

    except Exception as e:
        print(f"\n❌ Error: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
