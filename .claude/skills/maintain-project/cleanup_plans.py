#!/usr/bin/env python3
"""
Plans Directory Cleanup Module

清理 .claude/plans/ 目录，归档已完成计划，删除废弃计划。

功能：
1. 扫描 .claude/plans/active/ 目录
2. 检查每个计划对应的 GitHub issue 状态
3. 归档已关闭 issue 的计划（移到 archived/）
4. 删除超过 30 天的归档计划
"""

import os
import re
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Tuple, Optional


def extract_issue_number(plan_file: Path) -> Optional[int]:
    """
    从计划文件中提取 issue 编号。

    Args:
        plan_file: 计划文件路径

    Returns:
        issue 编号，如果未找到返回 None
    """
    try:
        with open(plan_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找 "Issue #123" 或 "**GitHub**: https://github.com/.../issues/123"
        # 尝试多种模式
        patterns = [
            r'Issue #(\d+)',
            r'issues/(\d+)',
            r'#(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return int(match.group(1))

        return None

    except Exception as e:
        print(f"⚠️  Error reading {plan_file}: {e}")
        return None


def check_issue_status(issue_num: int) -> Optional[str]:
    """
    检查 GitHub issue 状态。

    Args:
        issue_num: issue 编号

    Returns:
        状态字符串 ("OPEN" 或 "CLOSED")，如果检查失败返回 None
    """
    try:
        result = subprocess.run(
            ["gh", "issue", "view", str(issue_num), "--json", "state", "-q", ".state"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"⚠️  Failed to check issue #{issue_num}: {result.stderr.strip()}")
            return None

    except subprocess.TimeoutExpired:
        print(f"⚠️  Timeout checking issue #{issue_num}")
        return None
    except FileNotFoundError:
        print("❌ GitHub CLI (gh) not found. Please install: brew install gh")
        sys.exit(1)
    except Exception as e:
        print(f"⚠️  Error checking issue #{issue_num}: {e}")
        return None


def get_issue_closed_date(issue_num: int) -> Optional[datetime]:
    """
    获取 issue 关闭日期。

    Args:
        issue_num: issue 编号

    Returns:
        关闭日期，如果未关闭或检查失败返回 None
    """
    try:
        result = subprocess.run(
            ["gh", "issue", "view", str(issue_num), "--json", "closedAt", "-q", ".closedAt"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and result.stdout.strip():
            # 解析 ISO 8601 格式日期
            date_str = result.stdout.strip().rstrip('Z')
            return datetime.fromisoformat(date_str)
        else:
            return None

    except Exception as e:
        print(f"⚠️  Error getting closed date for issue #{issue_num}: {e}")
        return None


def archive_completed_plans(active_dir: str = ".claude/plans/active",
                           archived_dir: str = ".claude/plans/archived",
                           dry_run: bool = False) -> Tuple[int, List[str]]:
    """
    归档已完成的计划。

    Args:
        active_dir: 活动计划目录
        archived_dir: 归档计划目录
        dry_run: 是否为预览模式

    Returns:
        (归档数量, 归档文件列表)
    """
    active_path = Path(active_dir)
    archived_path = Path(archived_dir)

    if not active_path.exists():
        print(f"⚠️  Active plans directory not found: {active_dir}")
        return 0, []

    # 确保归档目录存在
    if not dry_run:
        archived_path.mkdir(parents=True, exist_ok=True)

    archived_count = 0
    archived_files = []

    # 扫描所有活动计划
    plan_files = list(active_path.glob("*.md"))

    if not plan_files:
        print("✅ No active plans found")
        return 0, []

    print(f"✅ Found {len(plan_files)} active plans\n")
    print("Checking GitHub issue status...")

    for plan_file in plan_files:
        # 提取 issue 编号
        issue_num = extract_issue_number(plan_file)
        if issue_num is None:
            print(f"⚠️  Could not extract issue number from {plan_file.name}")
            continue

        # 检查 issue 状态
        status = check_issue_status(issue_num)
        if status is None:
            continue

        if status == "CLOSED":
            print(f"  - Issue #{issue_num}: CLOSED → archive")

            if not dry_run:
                # 移动到归档目录
                dest = archived_path / plan_file.name
                plan_file.rename(dest)

            archived_count += 1
            archived_files.append(plan_file.name)
        else:
            print(f"  - Issue #{issue_num}: {status} → keep")

    return archived_count, archived_files


def delete_old_archived_plans(archived_dir: str = ".claude/plans/archived",
                              days_threshold: int = 30,
                              dry_run: bool = False) -> Tuple[int, List[str]]:
    """
    删除超过指定天数的归档计划。

    Args:
        archived_dir: 归档计划目录
        days_threshold: 天数阈值（默认 30 天）
        dry_run: 是否为预览模式

    Returns:
        (删除数量, 删除文件列表)
    """
    archived_path = Path(archived_dir)

    if not archived_path.exists():
        print(f"✅ No archived plans directory found")
        return 0, []

    deleted_count = 0
    deleted_files = []

    # 扫描所有归档计划
    plan_files = list(archived_path.glob("*.md"))

    if not plan_files:
        print("✅ No archived plans found")
        return 0, []

    print(f"\nChecking archived plans (older than {days_threshold} days)...")

    now = datetime.now()

    for plan_file in plan_files:
        # 提取 issue 编号
        issue_num = extract_issue_number(plan_file)
        if issue_num is None:
            continue

        # 获取关闭日期
        closed_date = get_issue_closed_date(issue_num)
        if closed_date is None:
            continue

        # 计算天数
        days_ago = (now - closed_date).days

        if days_ago > days_threshold:
            print(f"  - Issue #{issue_num}: closed {days_ago} days ago → delete")

            if not dry_run:
                plan_file.unlink()

            deleted_count += 1
            deleted_files.append(plan_file.name)

    return deleted_count, deleted_files


def count_files(directory: str) -> int:
    """统计目录中的文件数量"""
    path = Path(directory)
    if not path.exists():
        return 0
    return len(list(path.glob("*.md")))


def main():
    """主函数"""
    # 解析命令行参数
    dry_run = "--dry-run" in sys.argv
    verbose = "--verbose" in sys.argv
    skip_delete = "--skip-delete" in sys.argv

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Plans Directory Cleanup")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    if dry_run:
        print("🔍 Dry run mode - no changes will be made\n")

    # 统计初始状态
    active_before = count_files(".claude/plans/active")
    archived_before = count_files(".claude/plans/archived")

    print(f"Before: {active_before} files in active/, {archived_before} files in archived/\n")

    # 1. 归档已完成计划
    archived_count, archived_files = archive_completed_plans(dry_run=dry_run)

    # 2. 删除旧归档计划（可选）
    deleted_count = 0
    deleted_files = []

    if not skip_delete:
        deleted_count, deleted_files = delete_old_archived_plans(dry_run=dry_run)

    # 统计最终状态
    active_after = count_files(".claude/plans/active") if not dry_run else active_before - archived_count
    archived_after = count_files(".claude/plans/archived") if not dry_run else archived_before + archived_count - deleted_count

    # 显示结果
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Summary")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    if dry_run:
        print("🔍 Preview of changes:\n")

    if archived_count > 0:
        print(f"✅ Would archive {archived_count} completed plans:" if dry_run else f"✅ Archived {archived_count} completed plans:")
        for filename in archived_files[:5]:  # 最多显示 5 个
            print(f"   - {filename}")
        if len(archived_files) > 5:
            print(f"   ... and {len(archived_files) - 5} more")
        print()

    if deleted_count > 0:
        print(f"✅ Would delete {deleted_count} old archived plans:" if dry_run else f"✅ Deleted {deleted_count} old archived plans:")
        for filename in deleted_files[:5]:
            print(f"   - {filename}")
        if len(deleted_files) > 5:
            print(f"   ... and {len(deleted_files) - 5} more")
        print()

    if archived_count == 0 and deleted_count == 0:
        print("✅ No cleanup needed - plans directory is clean\n")

    print(f"Before: {active_before} files in active/")
    print(f"After:  {active_after} files in active/ {'✅' if active_after <= 5 else '⚠️'}\n")

    if not dry_run and (archived_count > 0 or deleted_count > 0):
        print("✅ Plans cleanup complete")


if __name__ == "__main__":
    main()
