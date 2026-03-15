#!/usr/bin/env python3
"""
Configure permissions for work-issue auto mode.

This script configures .claude/settings.json with required permissions
for seamless work-issue auto mode execution.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Permission templates by profile
PERMISSION_TEMPLATES = {
    "minimal": [
        # File operation tools (for execute-plan implementation)
        {"tool": "Read", "prompt": "*"},
        {"tool": "Write", "prompt": "*"},
        {"tool": "Edit", "prompt": "*"},
        {"tool": "Glob", "prompt": "*"},
        {"tool": "Grep", "prompt": "*"},
        # Task management tools (for progress tracking)
        {"tool": "TaskCreate", "prompt": "*"},
        {"tool": "TaskUpdate", "prompt": "*"},
        {"tool": "TaskList", "prompt": "*"},
        {"tool": "TaskGet", "prompt": "*"},
        # Git write operations
        {"tool": "Bash", "prompt": "git add *"},
        {"tool": "Bash", "prompt": "git commit *"},
        {"tool": "Bash", "prompt": "git push *"},
        {"tool": "Bash", "prompt": "git checkout *"},
        {"tool": "Bash", "prompt": "git branch *"},
        {"tool": "Bash", "prompt": "git fetch *"},
        {"tool": "Bash", "prompt": "git merge *"},
        {"tool": "Bash", "prompt": "git worktree *"},
        {"tool": "Bash", "prompt": "git rebase *"},
        {"tool": "Bash", "prompt": "git reset *"},
        {"tool": "Bash", "prompt": "git stash *"},
        # Git read operations (for execute-plan validation)
        {"tool": "Bash", "prompt": "git status *"},
        {"tool": "Bash", "prompt": "git diff *"},
        {"tool": "Bash", "prompt": "git log *"},
        # GitHub CLI
        {"tool": "Bash", "prompt": "gh issue *"},
        {"tool": "Bash", "prompt": "gh pr *"},
        {"tool": "Bash", "prompt": "gh api *"},
        {"tool": "Bash", "prompt": "gh auth *"},
    ],
    "node-lambda": [
        # Includes minimal + npm + AWS CLI
        {"tool": "Bash", "prompt": "npm test"},
        {"tool": "Bash", "prompt": "npm run lint"},
        {"tool": "Bash", "prompt": "npm run build"},
        {"tool": "Bash", "prompt": "npm install"},
        {"tool": "Bash", "prompt": "npm ci"},
        {"tool": "Bash", "prompt": "aws *"},
        {"tool": "Bash", "prompt": "cdk *"},
    ],
    "react-aws": [
        # Includes node-lambda + React tools
        {"tool": "Bash", "prompt": "npm start"},
        {"tool": "Bash", "prompt": "npm run dev"},
    ],
    "tauri-react": [
        # Includes react-aws + Tauri CLI
        {"tool": "Bash", "prompt": "cargo *"},
        {"tool": "Bash", "prompt": "tauri *"},
        {"tool": "Bash", "prompt": "npm run tauri *"},
    ],
    "nextjs-aws": [
        # Includes react-aws + Next.js CLI
        {"tool": "Bash", "prompt": "next *"},
        {"tool": "Bash", "prompt": "npm run next *"},
    ],
    "python-fastapi": [
        # Includes minimal + pytest + pip
        {"tool": "Bash", "prompt": "pytest *"},
        {"tool": "Bash", "prompt": "python -m pytest *"},
        {"tool": "Bash", "prompt": "python -m *"},
        {"tool": "Bash", "prompt": "pip install *"},
        {"tool": "Bash", "prompt": "uvicorn *"},
    ],
}


def detect_profile(target_path: Path) -> str:
    """Detect project profile from .framework-install or project files."""
    # Check .framework-install first
    framework_install = target_path / ".framework-install"
    if framework_install.exists():
        try:
            with open(framework_install) as f:
                for line in f:
                    if line.startswith("profile:"):
                        profile = line.split(":", 1)[1].strip()
                        return profile
        except Exception:
            pass

    # Check package.json for Node.js projects
    package_json = target_path / "package.json"
    if package_json.exists():
        try:
            with open(package.json) as f:
                pkg = json.load(f)
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

                # Tauri project
                if "@tauri-apps/cli" in deps or "tauri" in deps:
                    return "tauri-react"

                # Next.js project
                if "next" in deps:
                    return "nextjs-aws"

                # React project with AWS
                if "react" in deps and ("aws-sdk" in deps or "@aws-sdk" in deps):
                    return "react-aws"

                # Lambda project
                if "@aws-cdk/aws-lambda" in deps or "aws-lambda" in pkg.get("keywords", []):
                    return "node-lambda"

                # Generic Node.js
                return "node-lambda"
        except Exception:
            pass

    # Check for Python projects
    pyproject = target_path / "pyproject.toml"
    if pyproject.exists():
        return "python-fastapi"

    # Default to minimal
    return "minimal"


def get_permissions_for_profile(profile: str) -> List[Dict[str, str]]:
    """Get all permissions for a given profile (including inherited)."""
    # Profile inheritance hierarchy
    hierarchy = {
        "minimal": ["minimal"],
        "node-lambda": ["minimal", "node-lambda"],
        "react-aws": ["minimal", "node-lambda", "react-aws"],
        "tauri-react": ["minimal", "node-lambda", "react-aws", "tauri-react"],
        "nextjs-aws": ["minimal", "node-lambda", "react-aws", "nextjs-aws"],
        "python-fastapi": ["minimal", "python-fastapi"],
    }

    profiles = hierarchy.get(profile, ["minimal"])
    permissions = []

    for p in profiles:
        if p in PERMISSION_TEMPLATES:
            permissions.extend(PERMISSION_TEMPLATES[p])

    return permissions


def prompt_exists(prompts: List[Dict[str, str]], target: Dict[str, str]) -> bool:
    """Check if permission prompt already exists."""
    for p in prompts:
        if p.get("tool") == target.get("tool") and p.get("prompt") == target.get("prompt"):
            return True
    return False


def merge_permissions(existing: Dict, new_permissions: List[Dict[str, str]]) -> Tuple[Dict, int, int]:
    """
    Merge new permissions into existing settings.

    Returns:
        (updated_settings, added_count, existing_count)
    """
    existing_prompts = existing.get("allowedPrompts", [])
    added_count = 0

    for new_prompt in new_permissions:
        if not prompt_exists(existing_prompts, new_prompt):
            existing_prompts.append(new_prompt)
            added_count += 1

    existing["allowedPrompts"] = existing_prompts
    return existing, added_count, len(existing_prompts) - added_count


def validate_settings(settings: Dict) -> Tuple[bool, Optional[str]]:
    """Validate settings.json structure."""
    if "allowedPrompts" not in settings:
        return False, "Missing allowedPrompts field"

    if not isinstance(settings["allowedPrompts"], list):
        return False, "allowedPrompts must be an array"

    for i, prompt in enumerate(settings["allowedPrompts"]):
        if "tool" not in prompt:
            return False, f"Prompt {i} missing 'tool' field"
        if "prompt" not in prompt:
            return False, f"Prompt {i} missing 'prompt' field"

    # Check for git operations (critical for work-issue)
    git_prompts = [p for p in settings["allowedPrompts"] if "git" in p["prompt"]]
    if len(git_prompts) < 7:
        return False, f"Only {len(git_prompts)} git operations found (expected at least 7)"

    return True, None


def create_backup(settings_file: Path) -> Optional[Path]:
    """Create timestamped backup of settings.json."""
    if not settings_file.exists():
        return None

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_file = settings_file.parent / f"settings.json.backup-{timestamp}"

    try:
        with open(settings_file) as f:
            content = f.read()
        with open(backup_file, "w") as f:
            f.write(content)
        return backup_file
    except Exception as e:
        print(f"❌ Failed to create backup: {e}", file=sys.stderr)
        return None


def configure_permissions(
    target_path: str = ".",
    profile: Optional[str] = None,
    dry_run: bool = False
) -> int:
    """
    Configure permissions for work-issue auto mode.

    Args:
        target_path: Path to project directory
        profile: Override profile detection
        dry_run: Preview changes without applying

    Returns:
        0 on success, 1 on error
    """
    # Resolve target path
    target = Path(target_path).resolve()
    if not target.exists():
        print(f"❌ Error: Target path does not exist: {target}", file=sys.stderr)
        return 1

    claude_dir = target / ".claude"
    if not claude_dir.exists():
        print(f"❌ Error: .claude directory not found in: {target}", file=sys.stderr)
        print("Expected: .claude/settings.json", file=sys.stderr)
        return 1

    settings_file = claude_dir / "settings.json"

    # Step 1: Detect profile
    detected_profile = profile or detect_profile(target)
    print(f"📋 Configuring permissions for work-issue auto mode\n")
    print(f"1. Detecting profile...")
    print(f"   ✅ Profile: {detected_profile}" + (" (detected)" if not profile else " (specified)"))

    # Step 2: Load or create settings
    print(f"\n2. Loading settings.json...")
    existing_settings = {}
    if settings_file.exists():
        try:
            with open(settings_file) as f:
                existing_settings = json.load(f)
            print(f"   ✅ Found existing settings")
        except Exception as e:
            print(f"   ❌ Error reading settings.json: {e}", file=sys.stderr)
            return 1
    else:
        print(f"   ℹ️  Creating new settings.json")
        existing_settings = {}

    # Step 3: Generate permission templates
    print(f"\n3. Generating permission templates...")
    new_permissions = get_permissions_for_profile(detected_profile)
    print(f"   ✅ Generated {len(new_permissions)} permissions")

    # Step 4: Merge permissions
    print(f"\n4. Merging permissions...")
    updated_settings, added_count, existing_count = merge_permissions(
        existing_settings.copy(), new_permissions
    )
    print(f"   ✅ Added {added_count} new permissions")
    if existing_count > 0:
        print(f"   ✅ Preserved {existing_count} existing permissions")

    # Step 5: Validate
    print(f"\n5. Validating configuration...")
    valid, error = validate_settings(updated_settings)
    if not valid:
        print(f"   ❌ Validation failed: {error}", file=sys.stderr)
        return 1
    print(f"   ✅ Valid structure")
    print(f"   ✅ All git operations present")

    # Dry run - show preview and exit
    if dry_run:
        print(f"\n📋 Dry Run - Preview Changes (no files modified)\n")
        print(f"Would add {added_count} permissions:")
        for perm in new_permissions:
            if not prompt_exists(existing_settings.get("allowedPrompts", []), perm):
                print(f"+ {json.dumps(perm)}")
        print(f"\nWould preserve {existing_count} existing permissions")
        print(f"Total permissions after merge: {len(updated_settings['allowedPrompts'])}")
        print(f"\n✅ Dry run complete - no changes written")
        return 0

    # Step 6: Create backup
    if settings_file.exists():
        print(f"\n6. Creating backup...")
        backup_file = create_backup(settings_file)
        if backup_file:
            print(f"   ✅ Backup: {backup_file.name}")
        else:
            print(f"   ⚠️  Backup failed (continuing anyway)")

    # Step 7: Write updated settings
    step_num = 7 if settings_file.exists() else 6
    print(f"\n{step_num}. Writing updated settings...")
    try:
        with open(settings_file, "w") as f:
            json.dump(updated_settings, f, indent=2)
        print(f"   ✅ Updated {settings_file.relative_to(target)}")
    except Exception as e:
        print(f"   ❌ Error writing settings.json: {e}", file=sys.stderr)
        return 1

    # Success summary
    print(f"\n✅ Configuration complete!\n")
    print(f"work-issue auto mode is now ready to run without permission prompts.")

    return 0


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Configure permissions for work-issue auto mode"
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target project directory (default: current directory)"
    )
    parser.add_argument(
        "--profile",
        choices=list(PERMISSION_TEMPLATES.keys()),
        help="Override profile detection"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying"
    )

    args = parser.parse_args()

    try:
        sys.exit(configure_permissions(args.target, args.profile, args.dry_run))
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
