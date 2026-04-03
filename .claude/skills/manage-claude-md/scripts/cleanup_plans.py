#!/usr/bin/env python3
"""
归档已完成的 Plans

检查 .claude/plans/active/ 中的 plan 文件，如果对应的 GitHub issue 已关闭，
将 plan 文件移动到 .claude/plans/archive/
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional
import re


def find_project_root() -> Path:
    """查找项目根目录（包含 .claude/ 的目录）"""
    current = Path.cwd()

    # 向上查找直到找到 .claude/
    while current != current.parent:
        if (current / ".claude").exists():
            return current
        current = current.parent

    raise FileNotFoundError("未找到 .claude/ 目录 - 请在项目根目录运行此脚本")


def extract_issue_number(plan_file: Path) -> Optional[int]:
    """
    从 plan 文件名或内容中提取 issue 编号

    支持格式:
    - issue-123-plan.md (文件名)
    - **GitHub**: https://github.com/user/repo/issues/123 (内容)
    """
    # 尝试从文件名提取
    match = re.search(r'issue-(\d+)', plan_file.name)
    if match:
        return int(match.group(1))

    # 尝试从文件内容提取
    try:
        content = plan_file.read_text(encoding='utf-8')
        match = re.search(r'issues/(\d+)', content)
        if match:
            return int(match.group(1))
    except:
        pass

    return None


def is_issue_closed(issue_number: int) -> bool:
    """
    检查 GitHub issue 是否已关闭

    使用 gh CLI 命令
    """
    try:
        result = subprocess.run(
            ['gh', 'issue', 'view', str(issue_number), '--json', 'state'],
            capture_output=True,
            text=True,
            check=True
        )

        # 解析 JSON 输出
        import json
        data = json.loads(result.stdout)
        return data.get('state', '').upper() == 'CLOSED'

    except subprocess.CalledProcessError:
        # issue 不存在或 gh 命令失败
        return False
    except Exception as e:
        print(f"⚠️  检查 issue #{issue_number} 状态失败: {e}", file=sys.stderr)
        return False


def archive_plan(plan_file: Path, archive_dir: Path) -> None:
    """将 plan 文件移动到 archive 目录"""
    archive_dir.mkdir(parents=True, exist_ok=True)

    target_path = archive_dir / plan_file.name

    # 如果目标文件已存在，添加时间戳
    if target_path.exists():
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        stem = target_path.stem
        target_path = archive_dir / f"{stem}-{timestamp}{target_path.suffix}"

    plan_file.rename(target_path)
    print(f"  ✅ 已归档: {plan_file.name} → {target_path.name}")


def cleanup_plans(project_root: Path, dry_run: bool = False) -> None:
    """清理已完成的 plans"""

    active_dir = project_root / ".claude" / "plans" / "active"
    archive_dir = project_root / ".claude" / "plans" / "archive"

    if not active_dir.exists():
        print(f"⚠️  Active plans 目录不存在: {active_dir}")
        return

    # 扫描所有 plan 文件
    plan_files = list(active_dir.glob("*.md"))

    if not plan_files:
        print("ℹ️  没有找到 active plans")
        return

    print(f"🔍 扫描 {len(plan_files)} 个 active plans...")

    archived_count = 0
    skipped_count = 0

    for plan_file in plan_files:
        issue_number = extract_issue_number(plan_file)

        if issue_number is None:
            print(f"  ⏭️  跳过: {plan_file.name} (无法提取 issue 编号)")
            skipped_count += 1
            continue

        print(f"  🔍 检查 issue #{issue_number}...", end=" ")

        if is_issue_closed(issue_number):
            print("CLOSED")
            if not dry_run:
                archive_plan(plan_file, archive_dir)
            else:
                print(f"    [DRY RUN] 将归档: {plan_file.name}")
            archived_count += 1
        else:
            print("OPEN (保留)")

    # 总结
    print(f"\n📊 总结:")
    print(f"  - 已归档: {archived_count} 个 plans")
    print(f"  - 跳过: {skipped_count} 个 plans")
    print(f"  - 保留: {len(plan_files) - archived_count - skipped_count} 个 plans")

    if dry_run and archived_count > 0:
        print(f"\nℹ️  DRY RUN 模式 - 未实际归档文件")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="归档已完成的 plans")
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='预览模式 - 不实际移动文件'
    )

    args = parser.parse_args()

    try:
        # 查找项目根目录
        project_root = find_project_root()
        print(f"📁 项目根目录: {project_root}")

        # 清理 plans
        cleanup_plans(project_root, dry_run=args.dry_run)

        print("✅ 清理完成")

    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
