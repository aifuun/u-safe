#!/usr/bin/env python3
"""Finish issue workflow - commit, PR, merge, close, cleanup.

Automates the complete issue finishing lifecycle with quality gates.

Usage:
    # Auto-detect issue from branch
    python finish.py

    # Specify issue number
    python finish.py 97

    # With options
    python finish.py 97 --keep-branch --no-merge

    # Dry run
    python finish.py 97 --dry-run

Exit codes:
    0: Success
    1: Validation failed
    2: User aborted
    3: Command execution failed
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

# Add _scripts to path

try:
    from git.worktree import detect_current_worktree, cleanup_worktree
    WORKTREE_AVAILABLE = True
except ImportError:
    WORKTREE_AVAILABLE = False

try:
    from framework.issue_detector import detect_issue_number as detect_issue_multi_strategy
    ISSUE_DETECTOR_AVAILABLE = True
except ImportError:
    ISSUE_DETECTOR_AVAILABLE = False


def run_command(cmd: list[str], check: bool = True) -> Tuple[int, str, str]:
    """Execute shell command and return result.

    Args:
        cmd: Command and arguments as list
        check: Whether to raise on non-zero exit

    Returns:
        Tuple of (returncode, stdout, stderr)

    Example:
        >>> returncode, out, err = run_command(["git", "status"])
        >>> print(f"Status: {out}")
    """
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False
    )

    if check and result.returncode != 0:
        print(f"❌ Command failed: {' '.join(cmd)}", file=sys.stderr)
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(3)

    return result.returncode, result.stdout.strip(), result.stderr.strip()


def get_current_branch() -> str:
    """Get name of current git branch.

    Returns:
        Branch name

    Example:
        >>> branch = get_current_branch()
        >>> print(branch)
        feature/97-eval-framework
    """
    _, branch, _ = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return branch


def extract_issue_number(branch_name: str) -> Optional[int]:
    """Extract issue number from branch name.

    Args:
        branch_name: Git branch name

    Returns:
        Issue number or None if not found

    Example:
        >>> extract_issue_number("feature/97-eval-framework")
        97
        >>> extract_issue_number("main")
        None
    """
    match = re.search(r'(\d+)', branch_name)
    return int(match.group(1)) if match else None


def check_review_status() -> Optional[dict]:
    """Check if code review status exists and is valid.

    Returns:
        Review status dict or None if not found/invalid

    Example:
        >>> status = check_review_status()
        >>> if status and status['score'] >= 90:
        ...     print("Review passed!")
    """
    status_file = Path(".claude/.review-status.json")

    if not status_file.exists():
        return None

    try:
        with open(status_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def validate_environment(issue_number: int, force: bool = False) -> bool:
    """Validate environment before finishing issue.

    Args:
        issue_number: GitHub issue number
        force: Skip validation checks

    Returns:
        True if valid, False otherwise

    Example:
        >>> if validate_environment(97):
        ...     print("Ready to proceed")
    """
    branch = get_current_branch()

    # Check not on main
    if branch == "main":
        print("❌ Cannot finish from main branch", file=sys.stderr)
        print("   Switch to feature branch first", file=sys.stderr)
        return False

    # Check branch matches issue
    branch_issue = extract_issue_number(branch)
    if branch_issue != issue_number:
        print(f"⚠️  Branch issue ({branch_issue}) != specified issue ({issue_number})", file=sys.stderr)
        if not force:
            return False

    # Check for uncommitted changes
    returncode, output, _ = run_command(["git", "status", "--porcelain"], check=False)
    if output:
        print("❌ Uncommitted changes detected", file=sys.stderr)
        print("   Commit or stash changes first", file=sys.stderr)
        return False

    # Check review status
    review = check_review_status()
    if review:
        score = review.get('score', 0)
        print(f"✅ Review status: {score}/100")
    elif not force:
        print("⚠️  No review status found", file=sys.stderr)
        print("   Run /review first (or use --force)", file=sys.stderr)
        return False

    return True


def create_commit_message(issue_number: int) -> str:
    """Generate commit message for issue.

    Args:
        issue_number: GitHub issue number

    Returns:
        Formatted commit message

    Example:
        >>> msg = create_commit_message(97)
        >>> print(msg)
        feat: implement feature (Issue #97)
        ...
    """
    # Get issue details from GitHub
    returncode, output, _ = run_command([
        "gh", "issue", "view", str(issue_number),
        "--json", "title,body"
    ], check=False)

    if returncode != 0:
        return f"feat: complete issue #{issue_number}\n\nCloses #{issue_number}"

    try:
        issue = json.loads(output)
        title = issue.get('title', f'Issue #{issue_number}')

        # Determine commit type from title
        commit_type = "feat"
        if "fix" in title.lower() or "bug" in title.lower():
            commit_type = "fix"
        elif "doc" in title.lower():
            commit_type = "docs"
        elif "test" in title.lower():
            commit_type = "test"
        elif "refactor" in title.lower():
            commit_type = "refactor"

        return f"""{commit_type}: {title.lower()}

Closes #{issue_number}

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"""

    except (json.JSONDecodeError, KeyError):
        return f"feat: complete issue #{issue_number}\n\nCloses #{issue_number}"


def generate_issue_summary(issue_number: int, branch_name: str) -> str:
    """Generate human-friendly issue completion summary.

    Args:
        issue_number: GitHub issue number
        branch_name: Feature branch name

    Returns:
        Formatted markdown summary focusing on business value (Why/What/Achievements)
    """
    from datetime import datetime
    from formatter import HumanReadableSummary

    # 1. Get issue details (for title and body)
    returncode, issue_json, _ = run_command(
        ["gh", "issue", "view", str(issue_number), "--json", "title,body,url"],
        check=False
    )

    issue_title = f"Issue #{issue_number}"
    issue_body = ""
    issue_url = f"https://github.com/aifuun/ai-dev/issues/{issue_number}"

    if returncode == 0:
        try:
            issue_data = json.loads(issue_json)
            issue_title = issue_data.get("title", issue_title)
            issue_body = issue_data.get("body", "")
            issue_url = issue_data.get("url", issue_url)
        except:
            pass

    # 2. Get commits list from origin/main to HEAD
    returncode, commits, _ = run_command(
        ["git", "log", "origin/main..HEAD", "--oneline"],
        check=False
    )

    # 3. Read plan content (if exists)
    plan_content = None
    plan_file = Path(f".claude/plans/active/issue-{issue_number}-plan.md")
    if not plan_file.exists():
        # Check in archive
        plan_file = Path(f".claude/plans/archive/issue-{issue_number}-plan.md")

    if plan_file.exists():
        try:
            with open(plan_file) as f:
                plan_content = f.read()
        except:
            pass

    # 4. Read review data from .claude/.review-status.json (if exists)
    review_data = None
    review_status_file = Path(".claude/.review-status.json")
    if review_status_file.exists():
        try:
            with open(review_status_file) as f:
                review_data = json.load(f)
        except:
            pass

    # 5. Get file change statistics
    returncode, diff_stat, _ = run_command(
        ["git", "diff", "origin/main..HEAD", "--stat"],
        check=False
    )

    # Extract file count and lines summary
    files_changed = 0
    lines_summary = ""
    if diff_stat:
        lines = diff_stat.strip().split('\n')
        if lines:
            summary_line = lines[-1]
            # Extract "N files changed, X insertions(+), Y deletions(-)"
            import re
            files_match = re.search(r'(\d+) files? changed', summary_line)
            if files_match:
                files_changed = int(files_match.group(1))

            insertions_match = re.search(r'(\d+) insertions?\(\+\)', summary_line)
            deletions_match = re.search(r'(\d+) deletions?\(-\)', summary_line)

            if insertions_match and deletions_match:
                lines_summary = f"(+{insertions_match.group(1)}/-{deletions_match.group(1)})"
            elif insertions_match:
                lines_summary = f"(+{insertions_match.group(1)})"
            elif deletions_match:
                lines_summary = f"(-{deletions_match.group(1)})"

    # 6. Get PR number from merged PRs
    pr_number = 0
    returncode, pr_output, _ = run_command(
        ["gh", "pr", "list", "--state", "all", "--head", branch_name,
         "--json", "number", "--jq", ".[0].number"],
        check=False
    )
    if returncode == 0 and pr_output:
        try:
            pr_number = int(pr_output.strip())
        except:
            pr_number = 0

    # 7. Calculate duration (rough estimate from first commit time)
    returncode, first_commit_time, _ = run_command(
        ["git", "log", "origin/main..HEAD", "--reverse", "--format=%ar", "--max-count=1"],
        check=False
    )
    duration = first_commit_time.strip() if first_commit_time else "未知"

    # 8. Use formatter to generate human-friendly summary
    try:
        summary = HumanReadableSummary.from_issue_data(
            issue_number=issue_number,
            issue_title=issue_title,
            issue_body=issue_body,
            commits=commits,
            plan_content=plan_content,
            review_data=review_data,
            files_changed=files_changed,
            lines_summary=lines_summary,
            duration=duration,
            issue_url=issue_url,
            pr_number=pr_number
        )
        return summary.format_output()
    except Exception as e:
        # Graceful fallback to simple summary if formatter fails
        print(f"⚠️  Formatter failed: {e}", file=sys.stderr)
        print("⚠️  Using simple summary format", file=sys.stderr)

        return f"""## ✅ Issue 完成总结

**Issue**: #{issue_number} - {issue_title}
**分支**: {branch_name}
**PR**: #{pr_number}
**完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

### Commits

{commits if commits else 'No commits found'}

### 变更文件

{diff_stat if diff_stat else 'No changes'}

---

🤖 Generated by [Claude Code](https://claude.com/claude-code) via `/finish-issue`
"""


def post_summary_comment(issue_number: int, summary: str, dry_run: bool = False):
    """Post summary comment to GitHub issue.

    Args:
        issue_number: GitHub issue number
        summary: Markdown summary to post
        dry_run: If True, only preview without posting
    """
    if dry_run:
        print(f"\n📝 Would post to issue #{issue_number}:")
        print("─" * 60)
        print(summary)
        print("─" * 60)
        return

    # Post comment using gh CLI
    returncode, _, stderr = run_command(
        ["gh", "issue", "comment", str(issue_number), "--body", summary],
        check=False
    )

    # Graceful degradation - don't block workflow on failure
    if returncode != 0:
        print(f"⚠️  Failed to post summary: {stderr}", file=sys.stderr)
        print("⚠️  Continuing (summary can be added manually)", file=sys.stderr)
    else:
        print(f"✅ Posted summary to issue #{issue_number}")


def finish_issue(
    issue_number: int,
    keep_branch: bool = False,
    no_merge: bool = False,
    dry_run: bool = False,
    force: bool = False
) -> int:
    """Execute finish issue workflow.

    Args:
        issue_number: GitHub issue number
        keep_branch: Don't delete branch after merge
        no_merge: Create PR but don't merge
        dry_run: Show what would happen without executing
        force: Skip validation checks

    Returns:
        Exit code (0 = success)

    Example:
        >>> exit_code = finish_issue(97, dry_run=True)
        >>> print(f"Would execute finish workflow for #97")
    """
    print(f"🎯 Finishing Issue #{issue_number}\n")

    # Step 1: Validation
    print("📋 Step 1: Pre-Finish Validation")
    if not validate_environment(issue_number, force):
        return 1
    print("✅ Validation passed\n")

    if dry_run:
        print("🔍 DRY RUN - Would execute:")
        print("  1. Commit & Push changes")
        print("  2. Create pull request")
        if not no_merge:
            print("  3. Merge pull request")
        print("  4. Generate issue summary")
        print("  5. Post summary to issue")
        print("  6. Close issue")
        if not keep_branch:
            print("  7. Delete branches")
        print("  8. Cleanup")
        return 0

    # Step 2: Commit & Push
    print("📋 Step 2: Commit & Push")
    commit_msg = create_commit_message(issue_number)
    run_command(["git", "add", "-A"])
    run_command(["git", "commit", "-m", commit_msg])
    run_command(["git", "push"])
    print("✅ Changes committed and pushed\n")

    # Step 3: Create PR
    print("📋 Step 3: Create Pull Request")
    pr_title = commit_msg.split('\n')[0]
    pr_body = f"""## Summary

Completes issue #{issue_number}

## Changes

{commit_msg}

🤖 Generated with [Claude Code](https://claude.com/claude-code)"""

    returncode, pr_url, _ = run_command([
        "gh", "pr", "create",
        "--title", pr_title,
        "--body", pr_body
    ], check=False)

    if returncode != 0:
        print("⚠️  PR may already exist", file=sys.stderr)
    else:
        print(f"✅ PR created: {pr_url}\n")

    # Step 4: Merge PR (if not no_merge)
    if not no_merge:
        print("📋 Step 4: Merge Pull Request")
        delete_flag = [] if keep_branch else ["--delete-branch"]
        run_command([
            "gh", "pr", "merge",
            "--squash"
        ] + delete_flag)
        print("✅ PR merged\n")
    else:
        print("⏭️  Step 4: Skipped (--no-merge)\n")

    # Step 5: Generate Summary Comment
    print("📋 Step 5: Generate Issue Summary")
    branch_name = get_current_branch()
    summary = generate_issue_summary(issue_number, branch_name)
    print("✅ Summary generated\n")

    # Step 6: Post Summary to Issue
    print("📋 Step 6: Post Summary to Issue")
    post_summary_comment(issue_number, summary, dry_run=False)
    print()

    # Step 7: Close issue
    print("📋 Step 7: Close Issue")
    run_command([
        "gh", "issue", "close", str(issue_number),
        "--comment", f"✅ Completed in PR"
    ])
    print(f"✅ Issue #{issue_number} closed\n")

    # Step 8: Cleanup
    print("📋 Step 8: Cleanup")

    # Detect if we're in a worktree
    worktree_info = None
    if WORKTREE_AVAILABLE:
        try:
            worktree_info = detect_current_worktree()
        except Exception:
            pass  # Worktree detection failed, continue without it

    if not no_merge:
        # If in worktree, switch back to main worktree before cleaning
        if worktree_info and worktree_info.get('issue_number') == issue_number:
            main_path = Path.cwd().parent / Path.cwd().parent.name.split('-')[0]
            if main_path.exists():
                os.chdir(str(main_path))
                print(f"📍 Switched to main repository: {main_path}")

        run_command(["git", "checkout", "main"])
        run_command(["git", "pull"])

    # Clean up status files
    Path(".claude/.review-status.json").unlink(missing_ok=True)
    Path(".claude/.eval-plan-status.json").unlink(missing_ok=True)

    # Worktree cleanup (if applicable and not keep_branch)
    if worktree_info and not keep_branch and WORKTREE_AVAILABLE:
        worktree_issue = worktree_info.get('issue_number')
        if worktree_issue == issue_number:
            print(f"\n🌲 Worktree cleanup for issue #{issue_number}")
            print(f"   Path: {worktree_info['path']}")

            response = input("\n   Remove worktree? [Y/n]: ").strip().lower()
            if response in ['', 'y', 'yes']:
                try:
                    cleanup_worktree(issue_number, delete_branches=not keep_branch)
                    print(f"✅ Worktree removed")
                except Exception as e:
                    print(f"⚠️  Worktree cleanup failed: {e}", file=sys.stderr)
                    print(f"   You can manually remove it later with: rm -rf {worktree_info['path']}")
            else:
                print(f"⏭️  Worktree kept at: {worktree_info['path']}")

    print("\n✅ Cleanup complete\n")

    print(f"🎉 Issue #{issue_number} finished successfully!")
    return 0


def main() -> int:
    """Main entry point for finish issue script.

    Returns:
        Exit code

    Example:
        $ python finish.py 97
        🎯 Finishing Issue #97
        ...
    """
    parser = argparse.ArgumentParser(
        description="Finish issue workflow - commit, PR, merge, close, cleanup"
    )
    parser.add_argument(
        "issue_number",
        nargs="?",
        type=int,
        help="GitHub issue number (auto-detect from branch if omitted)"
    )
    parser.add_argument(
        "--keep-branch",
        action="store_true",
        help="Don't delete branch after merge"
    )
    parser.add_argument(
        "--no-merge",
        action="store_true",
        help="Create PR but don't merge automatically"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without executing"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip validation checks"
    )

    args = parser.parse_args()

    # Auto-detect issue number from branch if not provided
    issue_number = args.issue_number
    if not issue_number:
        # Try multi-strategy detector first (4 strategies + validation)
        if ISSUE_DETECTOR_AVAILABLE:
            try:
                issue_number = detect_issue_multi_strategy(
                    check_github=not args.force,
                    required=False
                )
                if issue_number:
                    print()  # Output from detector is verbose, add spacing
            except Exception as e:
                print(f"⚠️  Multi-strategy detection failed: {e}", file=sys.stderr)

        # Fallback to simple branch extraction
        if not issue_number:
            branch = get_current_branch()
            issue_number = extract_issue_number(branch)
            if issue_number:
                print(f"✨ Auto-detected issue #{issue_number} from branch\n")

        # Still no issue number - exit with error
        if not issue_number:
            print("❌ Could not detect issue number from any method", file=sys.stderr)
            print("   Tried:", file=sys.stderr)
            print("   - Branch name pattern (feature/N-)", file=sys.stderr)
            print("   - Active plan files", file=sys.stderr)
            print("   - Worktree path", file=sys.stderr)
            print("", file=sys.stderr)
            print("   Specify issue number: python finish.py <number>", file=sys.stderr)
            return 1

    return finish_issue(
        issue_number,
        keep_branch=args.keep_branch,
        no_merge=args.no_merge,
        dry_run=args.dry_run,
        force=args.force
    )


if __name__ == "__main__":
    sys.exit(main())
