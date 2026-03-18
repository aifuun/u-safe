#!/usr/bin/env python3
"""Update skills between projects with clean mode support.

This script provides:
1. Smart sync with version detection
2. Clean mode for complete directory replacement
3. Dry-run preview capabilities
4. Safety measures (backup, confirmation, mutual exclusion)
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def parse_arguments():
    """Parse command line arguments with mutual exclusion checks."""
    parser = argparse.ArgumentParser(
        description="Sync skills between projects with optional clean mode"
    )

    # Direction (mutually exclusive)
    direction_group = parser.add_mutually_exclusive_group(required=True)
    direction_group.add_argument(
        "--from",
        dest="source",
        help="Source project path (pull skills from)"
    )
    direction_group.add_argument(
        "--to",
        dest="target_push",
        help="Target project path (push skills to)"
    )

    # Clean mode
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Complete directory replacement (delete target, copy all from source)"
    )

    # Selective sync (mutually exclusive with --clean)
    parser.add_argument(
        "--skills",
        help="Comma-separated list of specific skills to sync"
    )

    parser.add_argument(
        "--filter-config",
        help="Path to filter configuration JSON"
    )

    # Dry run
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without executing"
    )

    args = parser.parse_args()

    # Mutual exclusion validation
    if args.clean and args.skills:
        parser.error("--clean and --skills are mutually exclusive. "
                    "--clean performs full directory replacement.")

    if args.clean and args.filter_config:
        parser.error("--clean and --filter-config are mutually exclusive. "
                    "--clean performs full directory replacement.")

    return args


def clean_sync(source_skills_dir: Path, target_skills_dir: Path, dry_run: bool = False) -> dict:
    """Complete directory replacement - delete target and copy all from source.

    Args:
        source_skills_dir: Source .claude/skills directory
        target_skills_dir: Target .claude/skills directory
        dry_run: If True, preview only without executing

    Returns:
        Dict with operation results
    """
    results = {
        "operation": "clean_sync",
        "dry_run": dry_run,
        "source": str(source_skills_dir),
        "target": str(target_skills_dir),
        "skills_deleted": 0,
        "skills_copied": 0,
        "backup_created": False,
        "backup_path": None
    }

    # Count skills
    source_skills = list_skills(source_skills_dir)
    target_skills = list_skills(target_skills_dir) if target_skills_dir.exists() else []

    results["skills_copied"] = len(source_skills)
    results["skills_deleted"] = len(target_skills)

    # Find skills that will be lost (in target but not in source)
    target_skill_names = {s.name for s in target_skills}
    source_skill_names = {s.name for s in source_skills}
    lost_skills = target_skill_names - source_skill_names
    results["lost_skills"] = list(lost_skills)

    if dry_run:
        # Dry run - just preview
        print(f"\n📊 Clean Sync Preview (--dry-run)\n")
        print(f"Target: {target_skills_dir}")
        print(f"\nWill DELETE:")
        print(f"- {len(target_skills)} existing skills")
        print(f"\nWill COPY:")
        print(f"- {len(source_skills)} skills from source")

        if lost_skills:
            print(f"\n⚠️  Skills in target but not in source will be LOST:")
            print(f"- {', '.join(sorted(lost_skills))}")
            print(f"- ({len(lost_skills)} skills)")

        print(f"\nUse --clean without --dry-run to execute.")
        return results

    # Real execution - display warning
    print(f"\n⚠️  WARNING: Clean mode will DELETE entire .claude/skills directory")
    print(f"   Target: {target_skills_dir}")
    print(f"   Source: {source_skills_dir}")
    print(f"\nThis will:")
    print(f"- Delete all existing skills in target ({len(target_skills)} skills)")
    print(f"- Copy all skills from source ({len(source_skills)} skills)")

    if lost_skills:
        print(f"\n⚠️  Skills that will be LOST (in target only):")
        print(f"   {', '.join(sorted(lost_skills))}")

    # Confirmation
    response = input(f"\nType 'yes' to confirm: ").strip()
    if response != 'yes':
        print("❌ Operation cancelled")
        sys.exit(1)

    # Create backup
    if target_skills_dir.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = target_skills_dir.parent / f".skills-backup-{timestamp}"
        print(f"\n📦 Creating backup: {backup_dir}")
        shutil.copytree(target_skills_dir, backup_dir)
        results["backup_created"] = True
        results["backup_path"] = str(backup_dir)

    # Delete target directory
    if target_skills_dir.exists():
        print(f"🗑️  Deleting: {target_skills_dir}")
        shutil.rmtree(target_skills_dir)

    # Copy source directory
    print(f"📋 Copying from source...")
    shutil.copytree(source_skills_dir, target_skills_dir)

    # Report
    print(f"\n✅ Clean sync complete!")
    print(f"   - Skills synced: {len(source_skills)}")
    if results["backup_created"]:
        print(f"   - Backup location: {results['backup_path']}")

    print(f"\n⚠️  All skills replaced. Target is now identical to source.")

    return results


def preview_clean_sync(source_skills_dir: Path, target_skills_dir: Path) -> dict:
    """Preview what will happen in clean sync mode.

    This is a convenience wrapper around clean_sync with dry_run=True.

    Args:
        source_skills_dir: Source directory
        target_skills_dir: Target directory

    Returns:
        Preview results dict
    """
    return clean_sync(source_skills_dir, target_skills_dir, dry_run=True)


def list_skills(skills_dir: Path) -> list[Path]:
    """List all skill directories in a skills directory.

    Args:
        skills_dir: Path to .claude/skills directory

    Returns:
        List of skill directory paths
    """
    if not skills_dir.exists():
        return []

    skills = []
    for item in skills_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            skills.append(item)

    return sorted(skills, key=lambda p: p.name)


def main():
    """Main entry point."""
    args = parse_arguments()

    # Determine source and target
    if args.source:
        # Pull from source
        source_project = Path(args.source).expanduser().resolve()
        target_project = Path.cwd()
    else:
        # Push to target
        source_project = Path.cwd()
        target_project = Path(args.target_push).expanduser().resolve()

    source_skills = source_project / ".claude" / "skills"
    target_skills = target_project / ".claude" / "skills"

    # Validate paths
    if not source_skills.exists():
        print(f"❌ Source skills directory not found: {source_skills}")
        sys.exit(1)

    # Execute based on mode
    if args.clean:
        # Clean mode
        results = clean_sync(source_skills, target_skills, dry_run=args.dry_run)

        # Exit with success
        sys.exit(0)
    else:
        # Normal mode (not implemented in this script - delegated to AI orchestration)
        print("❌ Normal sync mode not implemented in Python script")
        print("   Use AI orchestration via SKILL.md for normal sync")
        print("   Or use --clean for complete directory replacement")
        sys.exit(1)


if __name__ == "__main__":
    main()
