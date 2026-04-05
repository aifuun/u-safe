#!/usr/bin/env python3
"""
configure_profile.py - Interactive profile configuration for CLAUDE.md

Replaces manage-project functionality by writing profile config directly
to CLAUDE.md frontmatter (Issue #481).

Usage:
    python configure_profile.py                  # Interactive mode
    python configure_profile.py --profile tauri  # Set profile non-interactively
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Optional, List


def find_claude_md() -> Path:
    """
    Find CLAUDE.md in current or parent directories

    Returns:
        Path to CLAUDE.md

    Raises:
        FileNotFoundError: If CLAUDE.md not found
    """
    current = Path.cwd()

    while current != current.parent:
        claude_md = current / "CLAUDE.md"
        if claude_md.exists():
            return claude_md
        current = current.parent

    raise FileNotFoundError(
        "CLAUDE.md not found in current or parent directories.\n"
        "Please run this command from your project directory."
    )


def read_claude_md_frontmatter(claude_md: Path) -> tuple[Optional[Dict], str]:
    """
    Read existing CLAUDE.md and extract frontmatter

    Args:
        claude_md: Path to CLAUDE.md

    Returns:
        Tuple of (frontmatter dict or None, markdown content)
    """
    with open(claude_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for existing frontmatter
    if not content.startswith('---'):
        return None, content

    yaml_end = content.find('\n---\n', 3)
    if yaml_end == -1:
        return None, content

    frontmatter_text = content[3:yaml_end].strip()
    markdown_content = content[yaml_end + 5:]  # Skip '\n---\n'

    try:
        frontmatter = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError:
        # Invalid YAML, treat as no frontmatter
        return None, content

    return frontmatter, markdown_content


def write_claude_md_with_frontmatter(
    claude_md: Path,
    frontmatter: Dict,
    markdown_content: str
) -> None:
    """
    Write CLAUDE.md with updated frontmatter

    Args:
        claude_md: Path to CLAUDE.md
        frontmatter: Frontmatter dictionary
        markdown_content: Markdown content (without frontmatter)
    """
    # Convert frontmatter to YAML
    yaml_text = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)

    # Combine frontmatter and content
    new_content = f"---\n{yaml_text}---\n\n{markdown_content.lstrip()}"

    # Write to file
    with open(claude_md, 'w', encoding='utf-8') as f:
        f.write(new_content)


def prompt_profile_config() -> Dict:
    """
    Interactive prompt for profile configuration

    Returns:
        Profile configuration dictionary
    """
    print("🔧 Profile Configuration")
    print("=" * 60)
    print()

    # Profile name
    print("Available profiles:")
    print("  1. tauri        - Desktop app (Tauri + React)")
    print("  2. nextjs-aws   - Full-stack web (Next.js + AWS)")
    print("  3. tauri-aws    - Hybrid desktop + cloud (Tauri + AWS)")
    print("  4. minimal      - Minimal configuration")
    print("  5. custom       - Custom profile")
    print()

    profile_choice = input("Select profile [1-5]: ").strip()

    profile_map = {
        '1': 'tauri',
        '2': 'nextjs-aws',
        '3': 'tauri-aws',
        '4': 'minimal',
        '5': 'custom'
    }

    if profile_choice not in profile_map:
        print("Invalid choice, defaulting to 'custom'")
        profile_name = 'custom'
    else:
        profile_name = profile_map[profile_choice]

    if profile_name == 'custom':
        profile_name = input("Enter custom profile name: ").strip() or 'custom'

    # Project type
    print("\nProject type:")
    print("  1. desktop-app")
    print("  2. web-app")
    print("  3. mobile-app")
    print("  4. library")
    print("  5. cli-tool")
    print("  6. custom")
    print()

    type_choice = input("Select type [1-6]: ").strip()

    type_map = {
        '1': 'desktop-app',
        '2': 'web-app',
        '3': 'mobile-app',
        '4': 'library',
        '5': 'cli-tool',
        '6': 'custom'
    }

    project_type = type_map.get(type_choice, 'custom')
    if project_type == 'custom':
        project_type = input("Enter custom type: ").strip() or 'general'

    # Category
    category_map = {
        'desktop-app': 'desktop',
        'web-app': 'web',
        'mobile-app': 'mobile',
        'library': 'library',
        'cli-tool': 'cli'
    }
    category = category_map.get(project_type, 'general')

    # Tech stack (optional)
    print("\nTech stack (optional, press Enter to skip):")
    frontend = input("  Frontend framework: ").strip()
    backend = input("  Backend framework: ").strip()
    desktop = input("  Desktop framework: ").strip()

    tech_stack = {}
    if frontend:
        tech_stack['frontend'] = frontend
    if backend:
        tech_stack['backend'] = backend
    if desktop:
        tech_stack['desktop'] = desktop

    # Pillars (optional)
    print("\nPillars (optional, comma-separated, e.g., A,B,K,L):")
    pillars_input = input("  Enabled pillars: ").strip()
    pillars = [p.strip().upper() for p in pillars_input.split(',') if p.strip()] if pillars_input else []

    # Build profile config
    profile_config = {
        'profile': profile_name,
        'type': project_type,
        'category': category,
        'version': '1.0.0'
    }

    if tech_stack:
        profile_config['tech_stack'] = tech_stack

    if pillars:
        profile_config['pillars'] = pillars

    # Rules config (default)
    profile_config['rules'] = {
        'exclude': []
    }

    return profile_config


def configure_profile(
    profile_name: Optional[str] = None,
    project_type: Optional[str] = None,
    interactive: bool = True
) -> None:
    """
    Configure profile in CLAUDE.md frontmatter

    Args:
        profile_name: Profile name (if provided, skip interactive)
        project_type: Project type (if provided, skip interactive)
        interactive: Whether to use interactive mode
    """
    # Find CLAUDE.md
    try:
        claude_md = find_claude_md()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    print(f"📄 Found CLAUDE.md: {claude_md}")
    print()

    # Read existing frontmatter
    existing_frontmatter, markdown_content = read_claude_md_frontmatter(claude_md)

    if existing_frontmatter:
        print("✅ Existing frontmatter found")
        print(f"   Current profile: {existing_frontmatter.get('profile', 'none')}")
        print()
        overwrite = input("Overwrite existing profile config? [y/N]: ").strip().lower()
        if overwrite != 'y':
            print("❌ Cancelled")
            return
        print()
    else:
        print("ℹ️  No existing frontmatter")
        existing_frontmatter = {}
        print()

    # Get profile config
    if interactive and not profile_name:
        profile_config = prompt_profile_config()
    else:
        # Non-interactive mode
        profile_config = {
            'profile': profile_name or 'custom',
            'type': project_type or 'general',
            'category': 'general',
            'version': '1.0.0',
            'rules': {'exclude': []}
        }

    # Merge with existing frontmatter (preserve non-profile fields)
    merged_frontmatter = {**existing_frontmatter, **profile_config}

    # Write back to CLAUDE.md
    try:
        write_claude_md_with_frontmatter(claude_md, merged_frontmatter, markdown_content)
        print()
        print("=" * 60)
        print("✅ Profile configuration updated successfully!")
        print("=" * 60)
        print()
        print("Profile summary:")
        print(f"  Name: {profile_config['profile']}")
        print(f"  Type: {profile_config['type']}")
        print(f"  Category: {profile_config['category']}")
        if 'tech_stack' in profile_config:
            print(f"  Tech stack: {profile_config['tech_stack']}")
        if 'pillars' in profile_config:
            print(f"  Pillars: {profile_config['pillars']}")
        print()
        print(f"Updated: {claude_md}")
        print()
        print("Next steps:")
        print("  1. Generate rules: uv run .claude/skills/manage-rules/scripts/generate_rules.py")
        print("  2. Verify setup: uv run .claude/skills/manage-claude-md/scripts/health_report.py")
        print()

    except Exception as e:
        print(f"❌ Error writing CLAUDE.md: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Configure profile in CLAUDE.md frontmatter'
    )
    parser.add_argument(
        '--profile',
        type=str,
        help='Profile name (tauri, nextjs-aws, minimal, etc.)'
    )
    parser.add_argument(
        '--type',
        type=str,
        help='Project type (desktop-app, web-app, library, etc.)'
    )
    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Non-interactive mode (requires --profile and --type)'
    )

    args = parser.parse_args()

    # Validate non-interactive mode
    if args.non_interactive and not (args.profile and args.type):
        print("❌ Error: --non-interactive requires both --profile and --type")
        sys.exit(1)

    configure_profile(
        profile_name=args.profile,
        project_type=args.type,
        interactive=not args.non_interactive
    )


if __name__ == '__main__':
    main()
