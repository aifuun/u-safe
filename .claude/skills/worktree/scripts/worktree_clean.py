#!/usr/bin/env python3
"""Clean up merged and stale worktrees."""

import sys
from pathlib import Path

# Add _scripts to path

from git.worktree import list_worktrees, cleanup_worktree, prune_worktrees


def find_cleanable(worktrees: list) -> list:
    """Find worktrees that can be cleaned up.

    Args:
        worktrees: List of all worktrees

    Returns:
        List of cleanable worktrees (merged or stale status)
    """
    cleanable = []
    for wt in worktrees:
        status = wt.get('status', '')
        # Skip main repository
        if status == 'main':
            continue
        # Include merged or stale worktrees
        if status in ['merged', 'stale', 'cleaned']:
            cleanable.append(wt)
    return cleanable


def confirm_cleanup(worktrees: list) -> list:
    """Prompt user to confirm cleanup of worktrees.

    Args:
        worktrees: List of worktrees to clean

    Returns:
        List of confirmed worktrees to remove
    """
    if not worktrees:
        print("\n✨ No worktrees to clean up\n")
        print("All worktrees are active or this is the main repository.\n")
        return []

    print(f"\n🧹 Found {len(worktrees)} worktree(s) ready for cleanup:\n")

    for wt in worktrees:
        issue_num = wt.get('issue_number')
        title = wt.get('issue_title', 'Unknown')
        status = wt.get('status', 'unknown')
        path = wt.get('path', '')

        if issue_num:
            print(f"  • Issue #{issue_num}: {title}")
            print(f"    Status: {status}, Path: {path}")
        else:
            print(f"  • {wt.get('branch', 'unknown branch')}")
            print(f"    Status: {status}, Path: {path}")
        print()

    try:
        response = input("Remove these worktrees? [y/N]: ").strip().lower()
        if response in ['y', 'yes']:
            return worktrees
        else:
            print("\n👋 Cleanup cancelled\n")
            return []

    except (EOFError, KeyboardInterrupt):
        print("\n\n👋 Cleanup cancelled\n")
        return []


def main() -> None:
    """CLI entry point for worktree cleanup."""
    try:
        # List all worktrees
        all_worktrees = list_worktrees()

        # Find cleanable ones
        cleanable = find_cleanable(all_worktrees)

        # Confirm with user
        to_remove = confirm_cleanup(cleanable)

        # Clean up confirmed worktrees
        removed_count = 0
        for wt in to_remove:
            issue_num = wt.get('issue_number')
            if issue_num:
                try:
                    cleanup_worktree(issue_num, delete_branches=True)
                    print(f"✅ Removed worktree for issue #{issue_num}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Failed to remove worktree for issue #{issue_num}: {e}", file=sys.stderr)
                    print(f"   You can manually remove it: rm -rf {wt['path']}")
            else:
                print(f"⚠️  Skipping worktree without issue number: {wt.get('branch')}")

        # Prune orphaned references
        if removed_count > 0:
            print(f"\n🔧 Pruning orphaned worktree references...")
            try:
                prune_worktrees()
                print(f"✅ Pruned worktree references")
            except Exception as e:
                print(f"⚠️  Prune failed: {e}", file=sys.stderr)

        # Summary
        if removed_count > 0:
            print(f"\n🎉 Cleanup complete: {removed_count} worktree(s) removed\n")
        elif len(to_remove) == 0 and len(cleanable) > 0:
            print()  # Newline after cancellation message
        else:
            print()  # Newline after "no worktrees" message

    except Exception as e:
        print(f"\n❌ Error: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
