#!/usr/bin/env python3
"""
Configure permissions by copying ai-dev's settings.json to target project.

This script simplifies permission configuration by using ai-dev's
.claude/settings.json as the standard configuration template.
"""

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Optional


def find_ai_dev_root() -> Optional[Path]:
    """Find ai-dev root directory (contains .claude/pillars/)."""
    current = Path.cwd()

    # Check current directory and parents
    for parent in [current] + list(current.parents):
        if (parent / ".claude" / "pillars").exists():
            return parent

    # Check common locations
    common_paths = [
        Path.home() / "dev" / "ai-dev",
        Path.home() / "projects" / "ai-dev",
        Path.home() / "ai-dev",
    ]

    for path in common_paths:
        if path.exists() and (path / ".claude" / "pillars").exists():
            return path

    return None


def copy_settings(source_path: Path, target_path: Path, dry_run: bool = False) -> bool:
    """
    Copy settings.json from source to target.

    Args:
        source_path: Path to ai-dev root directory
        target_path: Path to target project directory
        dry_run: If True, only preview changes

    Returns:
        True if successful, False otherwise
    """
    source_settings = source_path / ".claude" / "settings.json"
    target_settings = target_path / ".claude" / "settings.json"

    # Validate source exists
    if not source_settings.exists():
        print(f"❌ Source settings not found: {source_settings}")
        return False

    # Ensure target .claude directory exists
    target_claude = target_path / ".claude"
    if not target_claude.exists():
        if dry_run:
            print(f"Would create directory: {target_claude}")
        else:
            target_claude.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {target_claude}")

    # Read source settings
    try:
        with open(source_settings, 'r') as f:
            settings_data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read source settings: {e}")
        return False

    # Check if target exists (backup if needed)
    if target_settings.exists():
        if dry_run:
            print(f"Would backup existing: {target_settings} → {target_settings}.backup")
        else:
            backup_path = Path(str(target_settings) + ".backup")
            shutil.copy2(target_settings, backup_path)
            print(f"✅ Backed up existing settings: {backup_path}")

    # Write to target
    if dry_run:
        print(f"\nWould write settings to: {target_settings}")
        print(f"Permissions: {len(settings_data.get('permissions', {}).get('autoApprovePatterns', []))} auto-approve patterns")
    else:
        try:
            with open(target_settings, 'w') as f:
                json.dump(settings_data, f, indent=2)
            print(f"✅ Wrote settings to: {target_settings}")
            print(f"   Permissions: {len(settings_data.get('permissions', {}).get('autoApprovePatterns', []))} auto-approve patterns")
        except Exception as e:
            print(f"❌ Failed to write settings: {e}")
            return False

    return True


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Configure permissions by copying ai-dev settings.json"
    )
    parser.add_argument(
        "target_path",
        nargs="?",
        default=".",
        help="Target project path (default: current directory)"
    )
    parser.add_argument(
        "--source",
        help="Path to ai-dev root (auto-detected if not provided)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files"
    )

    args = parser.parse_args()

    # Resolve target path
    target_path = Path(args.target_path).resolve()
    if not target_path.exists():
        print(f"❌ Target path does not exist: {target_path}")
        return 1

    print(f"Target project: {target_path}")

    # Find or validate ai-dev source
    if args.source:
        source_path = Path(args.source).resolve()
        if not source_path.exists():
            print(f"❌ Source path does not exist: {source_path}")
            return 1
        if not (source_path / ".claude" / "pillars").exists():
            print(f"❌ Source path is not ai-dev root (missing .claude/pillars/): {source_path}")
            return 1
    else:
        source_path = find_ai_dev_root()
        if not source_path:
            print("❌ Could not auto-detect ai-dev root directory")
            print("   Tried:")
            print("   - Current directory and parents")
            print("   - ~/dev/ai-dev")
            print("   - ~/projects/ai-dev")
            print("   - ~/ai-dev")
            print("\n   Please specify --source path explicitly")
            return 1

    print(f"Source (ai-dev): {source_path}")

    if args.dry_run:
        print("\n🔍 DRY RUN - No changes will be made\n")

    # Copy settings
    success = copy_settings(source_path, target_path, dry_run=args.dry_run)

    if success:
        if not args.dry_run:
            print("\n🎉 Configuration complete!")
            print("\nNext steps:")
            print("  1. Review: cat .claude/settings.json")
            print("  2. Test: /work-issue --auto")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
