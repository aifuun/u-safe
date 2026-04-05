#!/usr/bin/env python3
"""Git worktree management utilities for issue workflow integration.

This module provides functions to create, list, and manage git worktrees
for parallel issue development.
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


def get_repo_name() -> str:
    """Get the repository name from git config.

    Returns:
        Repository name (e.g., "ai-dev")

    Raises:
        RuntimeError: If not in a git repository
    """
    try:
        # Get remote URL
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True
        )
        url = result.stdout.strip()

        # Extract repo name from URL
        # Handles: git@github.com:user/repo.git or https://github.com/user/repo.git
        match = re.search(r'/([^/]+?)(\.git)?$', url)
        if match:
            return match.group(1)

        # Fallback: use directory name
        return Path.cwd().name

    except subprocess.CalledProcessError:
        raise RuntimeError("Not in a git repository")


def slugify(text: str, max_length: int = 30) -> str:
    """Convert text to kebab-case slug suitable for branch/directory names.

    Args:
        text: Input text to slugify
        max_length: Maximum length of output slug

    Returns:
        Kebab-case slug (e.g., "fix-login-bug")

    Examples:
        >>> slugify("Fix Login Bug")
        'fix-login-bug'
        >>> slugify("Update API Documentation", max_length=15)
        'update-api-doc'
    """
    # Convert to lowercase
    slug = text.lower()

    # Replace spaces and underscores with hyphens
    slug = re.sub(r'[\s_]+', '-', slug)

    # Remove non-alphanumeric characters except hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)

    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)

    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    # Truncate to max length
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')

    return slug


def get_metadata_path() -> Path:
    """Get path to worktree metadata file.

    Returns:
        Path to .git/worktree-metadata.json
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            check=True
        )
        git_dir = Path(result.stdout.strip())
        return git_dir / "worktree-metadata.json"
    except subprocess.CalledProcessError:
        raise RuntimeError("Not in a git repository")


def load_metadata() -> dict[str, Any]:
    """Load worktree metadata from JSON file.

    Returns:
        Metadata dictionary with "worktrees" key
        Empty dict with "worktrees" if file doesn't exist
    """
    metadata_path = get_metadata_path()

    if not metadata_path.exists():
        return {"worktrees": {}}

    try:
        with open(metadata_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # Corrupted file, return empty metadata
        return {"worktrees": {}}


def save_metadata(metadata: dict[str, Any]) -> None:
    """Save worktree metadata to JSON file.

    Args:
        metadata: Metadata dictionary to save
    """
    metadata_path = get_metadata_path()

    # Ensure .git directory exists
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)


def parse_git_worktree_list() -> list[dict[str, str]]:
    """Parse output of 'git worktree list' command.

    Returns:
        List of worktree dicts with keys: path, branch, commit

    Example output:
        [
            {"path": "/Users/woo/dev/ai-dev", "branch": "main", "commit": "abc123"},
            {"path": "/Users/woo/dev/ai-dev-101", "branch": "feature/101", "commit": "def456"}
        ]
    """
    try:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )

        worktrees = []
        current = {}

        for line in result.stdout.strip().split('\n'):
            if not line:
                if current:
                    worktrees.append(current)
                    current = {}
                continue

            if line.startswith('worktree '):
                current['path'] = line.split(' ', 1)[1]
            elif line.startswith('HEAD '):
                current['commit'] = line.split(' ', 1)[1]
            elif line.startswith('branch '):
                # Extract branch name (refs/heads/feature/101 -> feature/101)
                branch_ref = line.split(' ', 1)[1]
                current['branch'] = branch_ref.replace('refs/heads/', '')

        # Add last worktree
        if current:
            worktrees.append(current)

        return worktrees

    except subprocess.CalledProcessError:
        return []


def create_worktree(issue_number: int, issue_title: str, branch_name: str) -> dict[str, str]:
    """Create a new git worktree for an issue.

    Args:
        issue_number: GitHub issue number
        issue_title: Issue title for directory naming
        branch_name: Branch name to create (e.g., "feature/101-fix-bug")

    Returns:
        Dict with keys: path, branch

    Raises:
        RuntimeError: If worktree creation fails

    Example:
        >>> create_worktree(101, "Remove TaskCreate pattern", "feature/101-remove-taskcreate")
        {
            "path": "../ai-dev-101-remove-taskcreate-pattern",
            "branch": "feature/101-remove-taskcreate"
        }
    """
    repo_name = get_repo_name()
    slug = slugify(issue_title)

    # Generate worktree name: {repo}-{issue}-{slug}
    worktree_name = f"{repo_name}-{issue_number}-{slug}"
    worktree_path = Path.cwd().parent / worktree_name

    # Check if worktree already exists
    if worktree_path.exists():
        raise RuntimeError(
            f"Worktree directory already exists: {worktree_path}\n"
            f"Remove it with: rm -rf {worktree_path}"
        )

    # Create worktree
    try:
        subprocess.run(
            ["git", "worktree", "add", str(worktree_path), "-b", branch_name],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create worktree: {e.stderr}")

    # Save metadata
    metadata = load_metadata()
    metadata["worktrees"][str(issue_number)] = {
        "issue_number": issue_number,
        "issue_title": issue_title,
        "path": str(worktree_path),
        "branch": branch_name,
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "pr_number": None
    }
    save_metadata(metadata)

    return {
        "path": str(worktree_path),
        "branch": branch_name
    }


def list_worktrees() -> list[dict[str, Any]]:
    """List all git worktrees with metadata.

    Returns:
        List of worktree dicts with merged git + metadata info

    Example:
        [
            {
                "path": "/Users/woo/dev/ai-dev",
                "branch": "main",
                "issue_number": None,
                "issue_title": None,
                "status": "main",
                "created_at": None
            },
            {
                "path": "/Users/woo/dev/ai-dev-101-remove",
                "branch": "feature/101-remove-taskcreate",
                "issue_number": 101,
                "issue_title": "Remove TaskCreate pattern",
                "status": "active",
                "created_at": "2026-03-11T12:00:00"
            }
        ]
    """
    git_worktrees = parse_git_worktree_list()
    metadata = load_metadata()

    # Merge git data with metadata
    result = []
    for wt in git_worktrees:
        # Try to find matching metadata by branch name
        issue_meta = None
        for issue_num, meta in metadata["worktrees"].items():
            if meta["branch"] == wt["branch"]:
                issue_meta = meta
                break

        if issue_meta:
            # Merge git + metadata
            merged = {
                "path": wt["path"],
                "branch": wt["branch"],
                "commit": wt.get("commit"),
                "issue_number": issue_meta["issue_number"],
                "issue_title": issue_meta["issue_title"],
                "status": issue_meta["status"],
                "created_at": issue_meta.get("created_at"),
                "pr_number": issue_meta.get("pr_number")
            }
        else:
            # No metadata, just git info
            merged = {
                "path": wt["path"],
                "branch": wt["branch"],
                "commit": wt.get("commit"),
                "issue_number": None,
                "issue_title": None,
                "status": "main" if wt["branch"] == "main" else "unknown",
                "created_at": None,
                "pr_number": None
            }

        result.append(merged)

    return result


def detect_current_worktree() -> Optional[dict[str, Any]]:
    """Detect if current directory is inside a worktree.

    Returns:
        Worktree dict if in a worktree, None if in main repo
    """
    cwd = Path.cwd().resolve()
    worktrees = list_worktrees()

    for wt in worktrees:
        wt_path = Path(wt["path"]).resolve()
        if cwd == wt_path or wt_path in cwd.parents:
            return wt

    return None


def cleanup_worktree(issue_number: int, delete_branches: bool = True) -> None:
    """Remove worktree and optionally delete associated branches.

    Args:
        issue_number: Issue number whose worktree to remove
        delete_branches: If True, delete local and remote branches

    Raises:
        RuntimeError: If worktree removal fails or worktree not found
    """
    metadata = load_metadata()
    wt_meta = metadata["worktrees"].get(str(issue_number))

    if not wt_meta:
        raise RuntimeError(f"No worktree metadata found for issue #{issue_number}")

    worktree_path = wt_meta["path"]
    branch_name = wt_meta["branch"]

    # Remove worktree
    try:
        subprocess.run(
            ["git", "worktree", "remove", worktree_path],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        # Try force removal
        try:
            subprocess.run(
                ["git", "worktree", "remove", "--force", worktree_path],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError:
            raise RuntimeError(f"Failed to remove worktree: {e.stderr}")

    if delete_branches:
        # Delete local branch
        try:
            subprocess.run(
                ["git", "branch", "-D", branch_name],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError:
            # Branch might not exist or already deleted
            pass

        # Delete remote branch
        try:
            subprocess.run(
                ["git", "push", "origin", "--delete", branch_name],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError:
            # Remote branch might not exist or already deleted
            pass

    # Update metadata status
    wt_meta["status"] = "cleaned"
    wt_meta["cleaned_at"] = datetime.now().isoformat()
    metadata["worktrees"][str(issue_number)] = wt_meta
    save_metadata(metadata)


def prune_worktrees() -> None:
    """Clean up stale worktree administrative files.

    Runs 'git worktree prune' to remove references to deleted worktrees.
    """
    try:
        subprocess.run(
            ["git", "worktree", "prune"],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to prune worktrees: {e.stderr}")


if __name__ == "__main__":
    # Simple CLI for testing
    import sys

    if len(sys.argv) < 2:
        print("Usage: python worktree_manager.py <command>")
        print("Commands: list, create <issue> <title> <branch>, cleanup <issue>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        worktrees = list_worktrees()
        for wt in worktrees:
            print(f"{wt['branch']:40} {wt['path']:50} [{wt['status']}]")

    elif command == "create" and len(sys.argv) >= 5:
        issue_num = int(sys.argv[2])
        title = sys.argv[3]
        branch = sys.argv[4]
        result = create_worktree(issue_num, title, branch)
        print(f"Created worktree: {result['path']}")

    elif command == "cleanup" and len(sys.argv) >= 3:
        issue_num = int(sys.argv[2])
        cleanup_worktree(issue_num)
        print(f"Cleaned up worktree for issue #{issue_num}")

    elif command == "detect":
        wt = detect_current_worktree()
        if wt:
            print(f"In worktree: {wt['branch']} (issue #{wt['issue_number']})")
        else:
            print("In main repository")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
