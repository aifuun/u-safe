#!/usr/bin/env python3
"""Start working on a GitHub issue with worktree integration.

This script automates the workflow to start working on an issue:
1. Fetch issue details from GitHub
2. Create feature branch
3. Create git worktree for parallel development
4. Switch to worktree directory
5. Generate implementation plan
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Add _scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_scripts"))

from git.worktree import (
    create_worktree,
    detect_current_worktree,
    slugify,
    get_repo_name
)


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run shell command and return result.

    Args:
        cmd: Command as list of strings
        check: If True, raise on non-zero exit

    Returns:
        CompletedProcess with stdout/stderr
    """
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=check
    )


def get_issue_info(issue_number: int) -> dict:
    """Fetch issue information from GitHub.

    Args:
        issue_number: GitHub issue number

    Returns:
        Dict with keys: number, title, body, state

    Raises:
        RuntimeError: If issue not found or gh CLI fails
    """
    try:
        result = run_command([
            "gh", "issue", "view", str(issue_number),
            "--json", "number,title,body,state"
        ])
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to fetch issue #{issue_number}: {e.stderr}")


def check_git_status() -> bool:
    """Check if git working directory is clean.

    Returns:
        True if clean, False if uncommitted changes
    """
    result = run_command(["git", "status", "--porcelain"], check=False)
    return len(result.stdout.strip()) == 0


def get_current_branch() -> str:
    """Get current git branch name.

    Returns:
        Branch name (e.g., "main")
    """
    result = run_command(["git", "branch", "--show-current"])
    return result.stdout.strip()


def create_branch(branch_name: str) -> None:
    """Create and checkout a new git branch.

    Args:
        branch_name: Name of branch to create

    Raises:
        RuntimeError: If branch creation fails
    """
    try:
        run_command(["git", "checkout", "-b", branch_name])
        run_command(["git", "push", "-u", "origin", branch_name])
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create branch: {e.stderr}")


def generate_plan(issue: dict, plan_path: Path) -> None:
    """Generate implementation plan from issue.

    Args:
        issue: Issue dict from GitHub
        plan_path: Path where to save plan
    """
    plan_path.parent.mkdir(parents=True, exist_ok=True)

    plan_content = f"""# Issue #{issue['number']}: {issue['title']}

**GitHub**: https://github.com/{get_repo_name()}/issues/{issue['number']}
**Branch**: {get_current_branch()}
**Started**: {subprocess.run(['date', '+%Y-%m-%d'], capture_output=True, text=True).stdout.strip()}

## Context

{issue['body'] or 'No description provided'}

## Progress

- [ ] Plan reviewed
- [ ] Implementation started
- [ ] Tests added
- [ ] Ready for review

## Next Steps

1. Review this plan
2. Get first task: /next
3. Start implementation
4. When done: /finish-issue #{issue['number']}
"""

    with open(plan_path, 'w') as f:
        f.write(plan_content)


def start_issue(issue_number: int, no_plan: bool = False, no_worktree: bool = False) -> None:
    """Start working on an issue with full automation.

    Args:
        issue_number: GitHub issue number
        no_plan: If True, skip plan generation
        no_worktree: If True, skip worktree creation (use traditional branch)

    Raises:
        RuntimeError: If any step fails
    """
    # Step 1: Validate environment
    print("🔍 Validating environment...")

    if not check_git_status():
        raise RuntimeError(
            "⚠️  Uncommitted changes detected\n\n"
            "Options:\n"
            "  1. Commit: git add . && git commit -m 'WIP'\n"
            "  2. Stash: git stash\n"
            "  3. Force: Run with --force flag"
        )

    current_branch = get_current_branch()
    if current_branch not in ["main", "master", "develop"]:
        raise RuntimeError(
            f"⚠️  Already on feature branch: {current_branch}\n\n"
            f"Options:\n"
            f"  1. Finish current work: /finish-issue\n"
            f"  2. Switch to main: git checkout main\n"
            f"  3. Force: Run with --force flag"
        )

    # Step 2: Fetch issue
    print(f"📥 Fetching issue #{issue_number}...")
    issue = get_issue_info(issue_number)

    if issue['state'] != 'OPEN':
        print(f"⚠️  Warning: Issue #{issue_number} is {issue['state']}")

    print(f"✅ Found: {issue['title']}")

    # Step 3: Prepare branch name
    slug = slugify(issue['title'])
    branch_name = f"feature/{issue_number}-{slug}"

    # Step 4: Create worktree (if enabled) - this also creates the branch
    worktree_path = None
    if not no_worktree:
        print(f"🌲 Creating worktree with branch: {branch_name}...")
        try:
            result = create_worktree(
                issue_number=issue_number,
                issue_title=issue['title'],
                branch_name=branch_name
            )
            worktree_path = result['path']
            print(f"✅ Worktree created: {worktree_path}")

            # Switch to worktree directory
            os.chdir(worktree_path)
            print(f"📍 Switched to: {worktree_path}")

            # Push branch to remote
            print(f"🚀 Pushing branch to origin...")
            run_command(["git", "push", "-u", "origin", branch_name])
            print(f"✅ Branch pushed")

        except RuntimeError as e:
            print(f"⚠️  Worktree creation failed: {e}")
            print("Falling back to traditional branch...")
            no_worktree = True

    # Fallback: Create traditional branch if worktree disabled or failed
    if no_worktree:
        print(f"🌿 Creating branch: {branch_name}...")
        create_branch(branch_name)

    # Step 5: Generate plan (if enabled)
    if not no_plan:
        plan_path = Path.cwd() / ".claude" / "plans" / "active" / f"issue-{issue_number}-plan.md"
        print(f"📝 Generating plan: {plan_path}...")
        generate_plan(issue, plan_path)
        print(f"✅ Plan created")

    # Step 6: Success message
    print("\n" + "="*60)
    print(f"🎉 Ready to work on Issue #{issue_number}!")
    print("="*60)
    print(f"\n📌 Issue: {issue['title']}")
    print(f"🌿 Branch: {branch_name}")

    if worktree_path:
        print(f"🌲 Worktree: {worktree_path}")
        print(f"\n💡 Terminal command:")
        print(f"   cd {worktree_path}")

    print(f"\n📋 Next steps:")
    if not no_plan:
        print(f"   1. Review plan: cat .claude/plans/active/issue-{issue_number}-plan.md")
    print(f"   2. Start coding!")
    print(f"   3. When done: /finish-issue {issue_number}")
    print()


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Start working on a GitHub issue")
    parser.add_argument("issue_number", type=int, help="GitHub issue number")
    parser.add_argument("--no-plan", action="store_true", help="Skip plan generation")
    parser.add_argument("--no-worktree", action="store_true", help="Skip worktree creation")
    parser.add_argument("--force", action="store_true", help="Override safety checks (not implemented)")

    args = parser.parse_args()

    try:
        start_issue(
            issue_number=args.issue_number,
            no_plan=args.no_plan,
            no_worktree=args.no_worktree
        )
    except RuntimeError as e:
        print(f"\n❌ Error: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
