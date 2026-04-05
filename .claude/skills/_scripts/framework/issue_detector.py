#!/usr/bin/env python3
"""Multi-strategy issue number detection for workflow skills.

This module provides robust issue number detection with 4 fallback strategies:
1. Extract from branch name (feature/N-)
2. Find single active plan file
3. Extract from worktree path
4. Ask user (requires external handling)

Usage:
    from framework.issue_detector import detect_issue_number

    issue_num = detect_issue_number()
    if issue_num is None:
        print("Failed to detect issue number")
        sys.exit(1)
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Optional


class IssueDetectionError(Exception):
    """Raised when issue number cannot be detected."""
    pass


def extract_from_branch() -> Optional[int]:
    """Strategy 1: Extract issue number from current branch name.

    Patterns matched:
    - feature/137-python-shared-libs → 137
    - fix/42-bug-fix → 42
    - hotfix/999-critical → 999

    Returns:
        Issue number or None if not matched
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        branch = result.stdout.strip()

        # Match pattern: <prefix>/NUMBER-<description>
        match = re.search(r'(?:feature|fix|hotfix)/(\d+)-', branch)
        if match:
            issue_num = int(match.group(1))
            print(f"✅ Auto-detected from branch '{branch}': #{issue_num}")
            return issue_num

        return None

    except subprocess.CalledProcessError:
        return None


def find_single_active_plan() -> Optional[int]:
    """Strategy 2: Find issue number from single active plan file.

    If exactly ONE plan file exists in .claude/plans/active/, use it.
    If 0 or multiple plans exist, return None.

    Returns:
        Issue number or None if ambiguous
    """
    plans_dir = Path(".claude/plans/active")

    if not plans_dir.exists():
        return None

    # Find all plan files matching: issue-N-plan.md
    plan_files = list(plans_dir.glob("issue-*-plan.md"))

    if len(plan_files) == 1:
        # Extract issue number from filename
        match = re.search(r'issue-(\d+)-plan\.md', plan_files[0].name)
        if match:
            issue_num = int(match.group(1))
            print(f"✅ Auto-detected from active plan '{plan_files[0].name}': #{issue_num}")
            return issue_num

    return None


def extract_from_worktree_path() -> Optional[int]:
    """Strategy 3: Extract issue number from worktree directory path.

    Patterns matched:
    - /path/to/ai-dev-137-python-shared-libs → 137
    - /path/to/repo-42-feature → 42

    Returns:
        Issue number or None if not in worktree or no match
    """
    try:
        cwd = Path.cwd()

        # Match pattern: <repo>-NUMBER-<description>
        match = re.search(r'-(\d+)-', cwd.name)
        if match:
            issue_num = int(match.group(1))
            print(f"✅ Auto-detected from worktree path '{cwd.name}': #{issue_num}")
            return issue_num

        return None

    except Exception:
        return None


def ask_user_for_issue_number() -> Optional[int]:
    """Strategy 4: Ask user to provide issue number.

    This function should be overridden by the calling context:
    - When called by Claude: Claude should use AskUserQuestion tool
    - When called by script: Read from stdin

    Returns:
        Issue number from user input or None if invalid
    """
    print("\n⚠️  Cannot auto-detect issue number from any strategy")
    print("\nStrategies tried:")
    print("  ❌ Branch pattern (feature/N-, fix/N-, hotfix/N-)")
    print("  ❌ Active plans (expected exactly 1 plan file)")
    print("  ❌ Worktree path (expected pattern: repo-N-description)")
    print()

    try:
        user_input = input("Please enter issue number: ").strip()

        # Validate input is a number
        if user_input.isdigit():
            issue_num = int(user_input)
            print(f"✅ Using issue #{issue_num}")
            return issue_num
        else:
            print(f"❌ Invalid input: '{user_input}' (must be a number)")
            return None

    except (EOFError, KeyboardInterrupt):
        print("\n❌ User cancelled input")
        return None


def validate_issue_number(issue_num: int, check_github: bool = True) -> bool:
    """Validate that an issue number is valid.

    Args:
        issue_num: Issue number to validate
        check_github: If True, verify issue exists on GitHub

    Returns:
        True if valid, False otherwise
    """
    # Check plan file exists
    plan_file = Path(f".claude/plans/active/issue-{issue_num}-plan.md")
    if not plan_file.exists():
        print(f"⚠️  Warning: Plan file not found: {plan_file}")
        print(f"   Expected location: .claude/plans/active/issue-{issue_num}-plan.md")
        print(f"   Run: /start-issue {issue_num}")
        return False

    # Check GitHub issue exists (optional)
    if check_github:
        try:
            result = subprocess.run(
                ["gh", "issue", "view", str(issue_num)],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ Verified issue #{issue_num} exists on GitHub")
            return True

        except subprocess.CalledProcessError:
            print(f"⚠️  Warning: Issue #{issue_num} not found on GitHub")
            print(f"   This might be okay if working offline or issue was deleted")

            # Ask user if they want to continue
            try:
                response = input("Continue anyway? [y/N]: ").strip().lower()
                return response == 'y'
            except (EOFError, KeyboardInterrupt):
                return False

    return True


def detect_issue_number(
    check_github: bool = True,
    required: bool = True
) -> Optional[int]:
    """Multi-strategy issue number detection with validation.

    Tries detection strategies in order:
    1. Extract from branch name
    2. Find single active plan file
    3. Extract from worktree path
    4. Ask user (fallback)

    Args:
        check_github: If True, validate issue exists on GitHub
        required: If True, raise error if detection fails completely

    Returns:
        Issue number or None if all strategies fail

    Raises:
        IssueDetectionError: If required=True and detection fails
    """
    print("🔍 Detecting issue number...")
    print()

    # Strategy 1: Branch name
    issue_num = extract_from_branch()
    if issue_num:
        if validate_issue_number(issue_num, check_github):
            return issue_num

    # Strategy 2: Single active plan
    issue_num = find_single_active_plan()
    if issue_num:
        if validate_issue_number(issue_num, check_github):
            return issue_num

    # Strategy 3: Worktree path
    issue_num = extract_from_worktree_path()
    if issue_num:
        if validate_issue_number(issue_num, check_github):
            return issue_num

    # Strategy 4: Ask user
    issue_num = ask_user_for_issue_number()
    if issue_num:
        if validate_issue_number(issue_num, check_github):
            return issue_num

    # All strategies failed
    if required:
        raise IssueDetectionError(
            "Failed to detect issue number from all strategies. "
            "Please provide issue number explicitly."
        )

    return None


def main():
    """CLI entry point for testing."""
    try:
        issue_num = detect_issue_number(check_github=True, required=True)
        print()
        print(f"✅ Final result: Issue #{issue_num}")
        print()
        sys.exit(0)

    except IssueDetectionError as e:
        print()
        print(f"❌ Error: {e}")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
