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
# Base permissions (shared by all profiles)
BASE_PERMISSIONS = [
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
]

PERMISSION_TEMPLATES = {
    "tauri": [
        # Desktop app (local) - Base + npm + Tauri
        *BASE_PERMISSIONS,
        {"tool": "Bash", "prompt": "npm test"},
        {"tool": "Bash", "prompt": "npm run lint"},
        {"tool": "Bash", "prompt": "npm run build"},
        {"tool": "Bash", "prompt": "npm install"},
        {"tool": "Bash", "prompt": "npm ci"},
        {"tool": "Bash", "prompt": "npm run dev"},
        {"tool": "Bash", "prompt": "cargo *"},
        {"tool": "Bash", "prompt": "tauri *"},
        {"tool": "Bash", "prompt": "npm run tauri *"},
    ],
    "tauri-aws": [
        # Desktop + cloud - tauri + AWS CLI
        *BASE_PERMISSIONS,
        {"tool": "Bash", "prompt": "npm test"},
        {"tool": "Bash", "prompt": "npm run lint"},
        {"tool": "Bash", "prompt": "npm run build"},
        {"tool": "Bash", "prompt": "npm install"},
        {"tool": "Bash", "prompt": "npm ci"},
        {"tool": "Bash", "prompt": "npm run dev"},
        {"tool": "Bash", "prompt": "cargo *"},
        {"tool": "Bash", "prompt": "tauri *"},
        {"tool": "Bash", "prompt": "npm run tauri *"},
        {"tool": "Bash", "prompt": "aws *"},
        {"tool": "Bash", "prompt": "cdk *"},
    ],
    "nextjs-aws": [
        # Web full-stack - Base + npm + Next.js + AWS
        *BASE_PERMISSIONS,
        {"tool": "Bash", "prompt": "npm test"},
        {"tool": "Bash", "prompt": "npm run lint"},
        {"tool": "Bash", "prompt": "npm run build"},
        {"tool": "Bash", "prompt": "npm install"},
        {"tool": "Bash", "prompt": "npm ci"},
        {"tool": "Bash", "prompt": "npm run dev"},
        {"tool": "Bash", "prompt": "next *"},
        {"tool": "Bash", "prompt": "npm run next *"},
        {"tool": "Bash", "prompt": "aws *"},
        {"tool": "Bash", "prompt": "cdk *"},
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
                    # Check if has AWS dependencies
                    if "aws-cdk-lib" in deps or "@aws-sdk" in str(deps):
                        return "tauri-aws"
                    return "tauri"

                # Next.js project
                if "next" in deps:
                    return "nextjs-aws"

                # Default to nextjs-aws for Node.js projects
                return "nextjs-aws"
        except Exception:
            pass

    # Default to tauri (simplest profile)
    return "tauri"


def get_permissions_for_profile(profile: str) -> List[Dict[str, str]]:
    """Get all permissions for a given profile."""
    # Each profile now contains all its permissions directly
    if profile in PERMISSION_TEMPLATES:
        return PERMISSION_TEMPLATES[profile]

    # Fallback to tauri if unknown profile
    print(f"   ⚠️  Unknown profile '{profile}', using 'tauri' as fallback")
    return PERMISSION_TEMPLATES["tauri"]


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


def load_template(template_name: str, target_path: Path) -> Optional[Dict]:
    """
    Load permission template from file.

    Args:
        template_name: Template name (without .json extension)
        target_path: Project root path

    Returns:
        Template dict or None if not found
    """
    # Check project-specific templates first
    project_template = target_path / ".claude" / "permission-templates" / f"{template_name}.json"
    if project_template.exists():
        try:
            with open(project_template) as f:
                return json.load(f)
        except Exception as e:
            print(f"   ⚠️  Error loading project template: {e}", file=sys.stderr)

    # Check framework templates
    framework_template = target_path / "framework" / ".claude-template" / "permission-templates" / f"{template_name}.json"
    if framework_template.exists():
        try:
            with open(framework_template) as f:
                return json.load(f)
        except Exception as e:
            print(f"   ⚠️  Error loading framework template: {e}", file=sys.stderr)

    return None


def configure_permissions(
    target_path: str = ".",
    profile: Optional[str] = None,
    template: Optional[str] = None,
    dry_run: bool = False
) -> int:
    """
    Configure permissions for work-issue auto mode.

    Args:
        target_path: Path to project directory
        profile: Override profile detection
        template: Use permission template (all, safe, minimal, read-only, or custom name)
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

    # Step 1: Determine permission source (template or profile)
    print(f"📋 Configuring permissions for work-issue auto mode\n")

    if template:
        # Template mode
        print(f"1. Loading permission template...")
        print(f"   Template: {template}")

        template_data = load_template(template, target)
        if not template_data:
            print(f"   ❌ Template not found: {template}", file=sys.stderr)
            print(f"   Searched:", file=sys.stderr)
            print(f"     - .claude/permission-templates/{template}.json", file=sys.stderr)
            print(f"     - framework/.claude-template/permission-templates/{template}.json", file=sys.stderr)
            return 1

        # Extract permissions from template
        if "permissions" not in template_data or "bash" not in template_data["permissions"]:
            print(f"   ❌ Invalid template format", file=sys.stderr)
            print(f"   Expected: {{'permissions': {{'bash': {{'prompts': [...]}}}}}}", file=sys.stderr)
            return 1

        bash_perms = template_data["permissions"]["bash"]
        new_permissions = []

        # Add tool permissions (always required)
        for perm in BASE_PERMISSIONS:
            if perm["tool"] != "Bash":
                new_permissions.append(perm)

        # Add bash prompts from template
        for prompt in bash_perms.get("prompts", []):
            new_permissions.append({"tool": "Bash", "prompt": prompt})

        print(f"   ✅ Loaded {len(bash_perms.get('prompts', []))} bash permissions")
        if "blocked" in bash_perms and bash_perms["blocked"]:
            print(f"   ✅ Blocked {len(bash_perms['blocked'])} destructive operations")

    else:
        # Profile mode (current behavior)
        detected_profile = profile or detect_profile(target)
        print(f"1. Detecting profile...")
        print(f"   ✅ Profile: {detected_profile}" + (" (detected)" if not profile else " (specified)"))

        # Generate permissions from profile
        print(f"\n2. Generating permission templates...")
        new_permissions = get_permissions_for_profile(detected_profile)
        print(f"   ✅ Generated {len(new_permissions)} permissions")

    # Step 2: Load or create settings
    step_num = 2 if template else 3
    print(f"\n{step_num}. Loading settings.json...")
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

    # Step 3: Merge permissions
    step_num = 3 if template else 4
    print(f"\n{step_num}. Merging permissions...")
    updated_settings, added_count, existing_count = merge_permissions(
        existing_settings.copy(), new_permissions
    )
    print(f"   ✅ Added {added_count} new permissions")
    if existing_count > 0:
        print(f"   ✅ Preserved {existing_count} existing permissions")

    # Step 4: Validate
    step_num = 4 if template else 5
    print(f"\n{step_num}. Validating configuration...")
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

    # Step 5: Create backup
    if settings_file.exists():
        step_num = 5 if template else 6
        print(f"\n{step_num}. Creating backup...")
        backup_file = create_backup(settings_file)
        if backup_file:
            print(f"   ✅ Backup: {backup_file.name}")
        else:
            print(f"   ⚠️  Backup failed (continuing anyway)")

    # Step 6: Write updated settings
    if settings_file.exists():
        step_num = 6 if template else 7
    else:
        step_num = 5 if template else 6
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
        help="Override profile detection (profile mode)"
    )
    parser.add_argument(
        "--all",
        action="store_const",
        const="all",
        dest="template",
        help="Use 'all' template (full automation)"
    )
    parser.add_argument(
        "--safe",
        action="store_const",
        const="safe",
        dest="template",
        help="Use 'safe' template (except critical operations)"
    )
    parser.add_argument(
        "--minimal",
        action="store_const",
        const="minimal",
        dest="template",
        help="Use 'minimal' template (basic operations)"
    )
    parser.add_argument(
        "--read-only",
        action="store_const",
        const="read-only",
        dest="template",
        help="Use 'read-only' template (no modifications)"
    )
    parser.add_argument(
        "--template",
        help="Use custom template by name"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying"
    )

    args = parser.parse_args()

    # Check for conflicting arguments
    if args.template and args.profile:
        print("❌ Error: Cannot use both --template and --profile flags", file=sys.stderr)
        print("   Template mode and profile mode are mutually exclusive", file=sys.stderr)
        sys.exit(1)

    try:
        sys.exit(configure_permissions(
            args.target,
            profile=args.profile,
            template=args.template,
            dry_run=args.dry_run
        ))
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
