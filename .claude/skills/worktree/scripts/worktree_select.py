#!/usr/bin/env python3
"""Interactive worktree selection for easy switching."""

import sys
from pathlib import Path

# Add _scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_scripts"))

from git.worktree import list_worktrees, detect_current_worktree


def prompt_selection(worktrees: list) -> dict:
    """Show worktree list and prompt for selection.

    Args:
        worktrees: List of worktree dicts

    Returns:
        Selected worktree dict or None if quit
    """
    if not worktrees:
        print("\n📋 No worktrees found\n")
        print("Create one with: /start-issue <number>\n")
        return None

    # Import list display function
    from worktree_list import print_worktree_table

    # Show table
    current = detect_current_worktree()
    current_path = current['path'] if current else None
    print_worktree_table(worktrees, current_path)

    # Prompt for selection
    try:
        choice = input(f"Select worktree (1-{len(worktrees)}) or 'q' to quit: ").strip()

        if choice.lower() in ['q', 'quit', 'exit']:
            print("\n👋 Cancelled\n")
            return None

        # Parse selection
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(worktrees):
                return worktrees[idx]
            else:
                print(f"\n❌ Invalid selection. Please enter 1-{len(worktrees)}\n")
                return None
        except ValueError:
            print("\n❌ Invalid input. Please enter a number\n")
            return None

    except (EOFError, KeyboardInterrupt):
        print("\n\n👋 Cancelled\n")
        return None


def main() -> None:
    """CLI entry point for interactive selection."""
    try:
        worktrees = list_worktrees()
        selected = prompt_selection(worktrees)

        if selected:
            print(f"\n📍 To switch to worktree, run:\n")
            print(f"   cd {selected['path']}\n")

            issue_num = selected.get('issue_number')
            if issue_num:
                print(f"💡 Or copy to clipboard and paste in new terminal tab")
                print(f"   (Issue #{issue_num})\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
