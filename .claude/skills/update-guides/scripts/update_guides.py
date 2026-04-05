#!/usr/bin/env python3
"""Sync AI development guides between projects.

This script synchronizes AI guides (.claude/guides/) from framework
to target projects with version tracking and complete directory replacement.

Usage:
    python update_guides.py --from ~/dev/ai-dev ../u-safe
    python update_guides.py --from ~/dev/ai-dev .
    python update_guides.py --from ~/dev/ai-dev --to ../u-safe --dry-run
"""

import argparse
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Tuple


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Sync AI guides from framework to target project"
    )

    parser.add_argument(
        "--from",
        dest="framework_dir",
        required=True,
        help="Framework directory path (required)"
    )

    parser.add_argument(
        "--to",
        dest="target_dir",
        default=".",
        help="Target project directory (default: current directory)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying"
    )

    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip path validation (used by update-framework)"
    )

    return parser.parse_args()


def validate_paths(
    framework_dir: Path,
    target_dir: Path,
    skip_validation: bool = False
) -> Tuple[Path, Path]:
    """Validate and resolve framework and target paths.

    Args:
        framework_dir: Framework directory path
        target_dir: Target project directory path
        skip_validation: If True, skip validation checks

    Returns:
        Tuple of (framework_guides_path, target_guides_path)

    Raises:
        FileNotFoundError: If required directories don't exist
    """
    if skip_validation:
        framework_guides = framework_dir / ".claude" / "guides"
        target_guides = target_dir / ".claude" / "guides"
        return framework_guides, target_guides

    # Validate framework directory
    if not framework_dir.exists():
        raise FileNotFoundError(
            f"Framework directory not found: {framework_dir}"
        )

    # Validate target directory
    if not target_dir.exists():
        raise FileNotFoundError(
            f"Target directory not found: {target_dir}"
        )

    # Validate framework guides directory
    framework_guides = framework_dir / ".claude" / "guides"
    if not framework_guides.exists():
        raise FileNotFoundError(
            f"Framework guides not found: {framework_guides}\n"
            "Expected .claude/guides/ with 4 subdirectories "
            "(workflow, doc-templates, rules, profiles)"
        )

    target_guides = target_dir / ".claude" / "guides"

    return framework_guides, target_guides


def get_git_commit_hash(directory: Path) -> str:
    """Get current git commit hash for a directory.

    Args:
        directory: Git repository path

    Returns:
        Commit hash or 'unknown' if not a git repo
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return "unknown"


def count_md_files(directory: Path) -> int:
    """Count markdown files in directory recursively.

    Args:
        directory: Directory to search

    Returns:
        Number of .md files found
    """
    if not directory.exists():
        return 0
    return len(list(directory.rglob("*.md")))


def sync_guides(
    framework_guides: Path,
    target_guides: Path,
    framework_dir: Path,
    dry_run: bool = False
) -> int:
    """Sync guides from framework to target.

    Args:
        framework_guides: Source guides directory
        target_guides: Target guides directory
        framework_dir: Framework root directory (for git commit)
        dry_run: If True, only preview changes

    Returns:
        Number of files synced (0 if dry_run)
    """
    print("📋 同步 AI 开发指南")
    print(f"   框架: {framework_guides}")
    print(f"   目标: {target_guides}")
    print()

    # Count source files
    guide_count = count_md_files(framework_guides)
    if guide_count < 20:
        print(f"⚠️  警告：框架中仅找到 {guide_count} 个 guide 文件（期望 20 个）")

    if dry_run:
        print(f"🔍 DRY RUN: 将同步 {guide_count} 个文件")
        print(f"   - 删除: {target_guides} (如果存在)")
        print(f"   - 复制: {framework_guides} → {target_guides}")
        return 0

    # Delete existing target directory
    if target_guides.exists():
        print("🗑️  删除现有 guides 目录...")
        shutil.rmtree(target_guides)

    # Create target docs directory
    target_guides.parent.parent.mkdir(parents=True, exist_ok=True)

    # Copy guides
    print("📋 拷贝 AI 开发指南...")
    shutil.copytree(framework_guides, target_guides)

    # Create version marker
    print("📝 创建版本标记...")
    framework_commit = get_git_commit_hash(framework_dir)
    synced_count = count_md_files(target_guides)

    version_file = target_guides / ".ai-guides-version"
    version_content = (
        f"# AI Guides Version Tracking\n"
        f"# Auto-generated by update_guides.py\n\n"
        f"framework_path: {framework_dir}\n"
        f"framework_commit: {framework_commit}\n"
        f"synced_at: {datetime.now().isoformat()}\n"
        f"synced_by: update_guides.py v2.0.0\n"
        f"guide_count: {synced_count}\n"
    )
    version_file.write_text(version_content)

    print()
    print("✅ 同步完成")
    print()
    print(f"AI 现在可以使用最新的开发参考标准（{synced_count} 个文件）")
    print()
    print(f"版本文件: {version_file}")

    return synced_count


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        args = parse_arguments()

        framework_dir = Path(args.framework_dir).resolve()
        target_dir = Path(args.target_dir).resolve()

        framework_guides, target_guides = validate_paths(
            framework_dir,
            target_dir,
            args.skip_validation
        )

        sync_guides(
            framework_guides,
            target_guides,
            framework_dir,
            args.dry_run
        )

        return 0

    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        return 1
    except Exception as e:
        print(f"❌ 未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
