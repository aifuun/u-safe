#!/usr/bin/env python3
"""
Maintain Project - CLI Entry Point

统一的 CLI 接口，协调所有维护组件。

Usage:
    ./maintain_project.py                    # 完整维护
    ./maintain_project.py --dry-run          # 预览模式
    ./maintain_project.py --component claude-md  # 仅 CLAUDE.md
    ./maintain_project.py --component plans      # 仅 plans/
    ./maintain_project.py --report-only      # 仅健康报告
    ./maintain_project.py --verbose          # 详细日志
"""

import sys
import argparse
from pathlib import Path

# 导入维护模块
from sync_claude_md import scan_installed_skills, parse_claude_md_skills, update_claude_md_skills, detect_differences
from cleanup_plans import archive_completed_plans, delete_old_archived_plans, count_files
from health_report import calculate_overall_health, print_health_report


def validate_project_structure() -> bool:
    """
    验证项目结构。

    Returns:
        是否为有效的 ai-dev 项目
    """
    required_paths = [
        Path(".claude"),
        Path("CLAUDE.md"),
    ]

    missing = []
    for path in required_paths:
        if not path.exists():
            missing.append(str(path))

    if missing:
        print("❌ Error: Invalid project structure\n")
        print("Missing required components:")
        for path in missing:
            print(f"  - {path}")
        print("\nPlease ensure this is a valid ai-dev project.")
        return False

    return True


def run_full_maintenance(dry_run: bool = False, verbose: bool = False):
    """
    运行完整维护流程。

    Args:
        dry_run: 是否为预览模式
        verbose: 是否显示详细日志
    """
    print("🚀 Starting project maintenance...\n")

    if dry_run:
        print("🔍 Dry run mode - no changes will be made\n")

    results = {
        "claude_md": {"updated": False, "added": 0, "removed": 0},
        "plans": {"archived": 0, "deleted": 0}
    }

    # 1. CLAUDE.md 同步
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Task 1/3: Sync CLAUDE.md skills list")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    installed = scan_installed_skills()
    documented = parse_claude_md_skills()
    diff = detect_differences(installed, documented)

    if diff["added"] or diff["removed"]:
        print(f"✅ Found differences: +{len(diff['added'])}, -{len(diff['removed'])}")
        update_claude_md_skills("CLAUDE.md", installed, dry_run=dry_run)
        results["claude_md"]["updated"] = True
        results["claude_md"]["added"] = len(diff["added"])
        results["claude_md"]["removed"] = len(diff["removed"])
    else:
        print("✅ CLAUDE.md skills list is already up to date")

    print()

    # 2. plans/ 清理
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Task 2/3: Clean up plans/ directory")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    archived_count, _ = archive_completed_plans(dry_run=dry_run)
    deleted_count, _ = delete_old_archived_plans(dry_run=dry_run)

    results["plans"]["archived"] = archived_count
    results["plans"]["deleted"] = deleted_count

    if archived_count > 0 or deleted_count > 0:
        print(f"\n✅ Plans cleanup: {archived_count} archived, {deleted_count} deleted")
    else:
        print("✅ No plans cleanup needed")

    print()

    # 3. 健康报告
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Task 3/3: Generate health report")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    health = calculate_overall_health()
    print_health_report(health, verbose=verbose)

    # 总结
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Summary")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    if dry_run:
        print("🔍 Preview complete - no changes made\n")
        print("Would apply:")
    else:
        print("Changes applied:")

    if results["claude_md"]["updated"]:
        print(f"  - CLAUDE.md: +{results['claude_md']['added']}, -{results['claude_md']['removed']} skills")

    if results["plans"]["archived"] > 0 or results["plans"]["deleted"] > 0:
        print(f"  - plans/: {results['plans']['archived']} archived, {results['plans']['deleted']} deleted")

    if not results["claude_md"]["updated"] and results["plans"]["archived"] == 0 and results["plans"]["deleted"] == 0:
        print("  - No changes needed")

    print(f"\nHealth: {health['overall']}/100")

    if not dry_run:
        print("\n✅ Project maintenance complete")


def run_component_maintenance(component: str, dry_run: bool = False, verbose: bool = False):
    """
    运行单个组件维护。

    Args:
        component: 组件名称 (claude-md 或 plans)
        dry_run: 是否为预览模式
        verbose: 是否显示详细日志
    """
    if component == "claude-md":
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("CLAUDE.md Skills Sync")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

        if dry_run:
            print("🔍 Dry run mode - no changes will be made\n")

        installed = scan_installed_skills()
        documented = parse_claude_md_skills()
        diff = detect_differences(installed, documented)

        print(f"✅ Scanning .claude/skills/ directory...")
        print(f"✅ Found {len(installed)} installed skills")
        print(f"✅ Parsing CLAUDE.md current skills table...")
        print(f"✅ Found {len(documented)} documented skills\n")

        if diff["added"]:
            print(f"Differences:")
            for name in diff["added"]:
                skill = next((s for s in installed if s.name == name), None)
                if skill:
                    print(f"  + {name} v{skill.version} (new)")
            print()

        if diff["removed"]:
            for name in diff["removed"]:
                print(f"  - {name} (removed)")
            print()

        if not diff["added"] and not diff["removed"]:
            print("✅ CLAUDE.md skills list is already up to date\n")
            return

        update_claude_md_skills("CLAUDE.md", installed, dry_run=dry_run)

        if not dry_run:
            print(f"\n✅ CLAUDE.md updated: +{len(diff['added'])}, -{len(diff['removed'])}")

    elif component == "plans":
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("Plans Directory Cleanup")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

        if dry_run:
            print("🔍 Dry run mode - no changes will be made\n")

        active_before = count_files(".claude/plans/active")
        print(f"Before: {active_before} files in active/\n")

        archived_count, _ = archive_completed_plans(dry_run=dry_run)
        deleted_count, _ = delete_old_archived_plans(dry_run=dry_run)

        active_after = count_files(".claude/plans/active") if not dry_run else active_before - archived_count

        print(f"\nAfter:  {active_after} files in active/ {'✅' if active_after <= 5 else '⚠️'}")

        if archived_count > 0 or deleted_count > 0:
            print(f"\n✅ Plans cleanup: {archived_count} archived, {deleted_count} deleted")
        else:
            print("\n✅ No cleanup needed - plans directory is clean")

    else:
        print(f"❌ Error: Unknown component '{component}'")
        print("\nAvailable components:")
        print("  - claude-md  (CLAUDE.md skills list sync)")
        print("  - plans      (plans/ directory cleanup)")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Maintain Project - Automated project content maintenance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Full maintenance
  %(prog)s --dry-run                 # Preview mode
  %(prog)s --component claude-md     # CLAUDE.md only
  %(prog)s --component plans         # plans/ only
  %(prog)s --report-only             # Health report only
  %(prog)s --verbose                 # Detailed logging

Components:
  claude-md   Sync CLAUDE.md skills list
  plans       Clean up plans/ directory
        """
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview mode - no changes will be made"
    )

    parser.add_argument(
        "--component",
        choices=["claude-md", "plans"],
        help="Run specific component only"
    )

    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Generate health report only (no modifications)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed logging"
    )

    args = parser.parse_args()

    # 验证项目结构
    if not validate_project_structure():
        sys.exit(1)

    # 执行维护
    if args.report_only:
        # 仅健康报告
        health = calculate_overall_health()
        print_health_report(health, verbose=args.verbose)

    elif args.component:
        # 单个组件维护
        run_component_maintenance(args.component, dry_run=args.dry_run, verbose=args.verbose)

    else:
        # 完整维护
        run_full_maintenance(dry_run=args.dry_run, verbose=args.verbose)


if __name__ == "__main__":
    main()
