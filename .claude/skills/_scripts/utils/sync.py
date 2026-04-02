#!/usr/bin/env python3
"""
Shared synchronization utilities for update-skills skill.

This module provides core functions for syncing skills between projects,
including YAML metadata parsing and framework-only filtering.

Issue #401: Framework-only filtering logic extracted from update-skills SKILL.md
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class SyncMode(Enum):
    """Sync mode enumeration"""
    REPLACE = "replace"  # Complete replacement (delete + copy)
    INCREMENTAL = "incremental"  # Version comparison
    SELECTIVE = "selective"  # With --skills filter


@dataclass
class SkillMetadata:
    """Parsed skill metadata from YAML frontmatter"""
    name: str
    version: Optional[str] = None
    framework_only: bool = False
    user_invocable: bool = True
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> 'SkillMetadata':
        """Create from parsed YAML dict"""
        return cls(
            name=data.get('name', ''),
            version=data.get('version'),
            framework_only=data.get('framework-only', False),
            user_invocable=data.get('user-invocable', True),
            description=data.get('description')
        )


@dataclass
class SyncResult:
    """Result of a sync operation"""
    mode: SyncMode
    synced_count: int
    skipped_count: int
    excluded_framework: List[str]
    errors: List[str]


def parse_skill_metadata(content: str) -> Optional[SkillMetadata]:
    """
    Parse YAML frontmatter from SKILL.md content.

    Args:
        content: Full content of SKILL.md file

    Returns:
        SkillMetadata object if YAML found, None otherwise

    Example:
        >>> content = '''---
        ... name: update-skills
        ... version: "3.1.0"
        ... framework-only: true
        ... ---
        ... # Rest of file...
        ... '''
        >>> metadata = parse_skill_metadata(content)
        >>> metadata.name
        'update-skills'
        >>> metadata.framework_only
        True
    """
    # Extract YAML between --- markers
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)

    if not match:
        return None

    try:
        yaml_content = match.group(1)
        data = yaml.safe_load(yaml_content)

        if not data or not isinstance(data, dict):
            return None

        return SkillMetadata.from_dict(data)

    except yaml.YAMLError as e:
        print(f"⚠️ YAML parsing error: {e}")
        return None


def filter_framework_only_skills(
    skill_dirs: List[Path]
) -> Tuple[List[Path], List[str]]:
    """
    Filter out framework-only skills from sync list.

    This implements Issue #401 framework-only filtering logic.
    Skills marked with 'framework-only: true' in their YAML frontmatter
    are excluded from syncing to target projects.

    Args:
        skill_dirs: List of skill directory paths to check

    Returns:
        Tuple of (skills_to_sync, excluded_skill_names)

    Example:
        >>> skills = [
        ...     Path('.claude/skills/start-issue'),
        ...     Path('.claude/skills/update-skills'),  # framework-only
        ...     Path('.claude/skills/review'),
        ... ]
        >>> to_sync, excluded = filter_framework_only_skills(skills)
        >>> 'update-skills' in excluded
        True
        >>> len(to_sync)
        2
    """
    to_sync = []
    excluded = []

    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"

        # Skip if SKILL.md doesn't exist
        if not skill_md.exists():
            print(f"⚠️ {skill_dir.name}: SKILL.md not found, skipping")
            continue

        # Parse metadata
        try:
            content = skill_md.read_text(encoding='utf-8')
            metadata = parse_skill_metadata(content)

            # Check framework-only field (default: False for backward compatibility)
            if metadata and metadata.framework_only:
                print(f"⏭️  Skipping {skill_dir.name} (framework-only)")
                excluded.append(skill_dir.name)
                continue

        except Exception as e:
            print(f"⚠️ {skill_dir.name}: Error reading metadata: {e}")
            # Continue syncing on error (fail-open for safety)

        # Include in sync list
        to_sync.append(skill_dir)

    return to_sync, excluded


def sync_skills(
    source_dir: Path,
    target_dir: Path,
    mode: SyncMode = SyncMode.REPLACE,
    selected_skills: Optional[List[str]] = None,
    dry_run: bool = False
) -> SyncResult:
    """
    Sync skills from source to target directory.

    Args:
        source_dir: Source .claude/skills directory
        target_dir: Target .claude/skills directory
        mode: Sync mode (replace/incremental/selective)
        selected_skills: List of skill names to sync (for selective mode)
        dry_run: Preview only, don't apply changes

    Returns:
        SyncResult with sync statistics

    Modes:
        - REPLACE: Delete target and copy all from source (default)
        - INCREMENTAL: Compare versions, sync newer only
        - SELECTIVE: Sync only skills in selected_skills list

    Example:
        >>> result = sync_skills(
        ...     Path('~/dev/ai-dev/.claude/skills'),
        ...     Path('.claude/skills'),
        ...     mode=SyncMode.REPLACE,
        ...     dry_run=True
        ... )
        >>> result.synced_count
        28
        >>> len(result.excluded_framework)
        7
    """
    errors = []
    excluded_framework = []
    synced_count = 0
    skipped_count = 0

    # Validate directories
    if not source_dir.exists():
        errors.append(f"Source directory not found: {source_dir}")
        return SyncResult(mode, 0, 0, [], errors)

    # Get all skill directories from source
    skill_dirs = [d for d in source_dir.iterdir() if d.is_dir()]

    # Filter out framework-only skills (Issue #401)
    skills_to_sync, excluded_framework = filter_framework_only_skills(skill_dirs)

    # Apply selective filter if provided
    if selected_skills:
        skills_to_sync = [
            s for s in skills_to_sync
            if s.name in selected_skills
        ]

    if dry_run:
        print(f"\n🔍 DRY RUN - Would sync {len(skills_to_sync)} skills")
        print(f"   Excluded (framework-only): {len(excluded_framework)}")
        return SyncResult(mode, len(skills_to_sync), 0, excluded_framework, errors)

    # Execute sync based on mode
    if mode == SyncMode.REPLACE:
        # Complete replacement: delete target + copy source
        if target_dir.exists():
            import shutil
            shutil.rmtree(target_dir)
            print(f"🗑️  Deleted {target_dir}")

        target_dir.mkdir(parents=True, exist_ok=True)

        for skill_dir in skills_to_sync:
            target_skill = target_dir / skill_dir.name
            import shutil
            shutil.copytree(skill_dir, target_skill)
            synced_count += 1

        print(f"✅ Synced {synced_count} skills")

    elif mode == SyncMode.INCREMENTAL:
        # Incremental: version comparison (placeholder for now)
        # TODO: Implement version comparison logic
        print(f"⚠️ Incremental mode not fully implemented yet")
        synced_count = len(skills_to_sync)

    elif mode == SyncMode.SELECTIVE:
        # Selective: copy only selected skills
        for skill_dir in skills_to_sync:
            target_skill = target_dir / skill_dir.name
            if target_skill.exists():
                import shutil
                shutil.rmtree(target_skill)

            import shutil
            shutil.copytree(skill_dir, target_skill)
            synced_count += 1

        print(f"✅ Synced {synced_count} selected skills")

    return SyncResult(mode, synced_count, skipped_count, excluded_framework, errors)


if __name__ == "__main__":
    # Simple test
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test YAML parsing
        test_content = """---
name: test-skill
version: "1.0.0"
framework-only: true
---
# Test Skill
"""
        metadata = parse_skill_metadata(test_content)
        print(f"Parsed: {metadata}")
        print(f"Framework-only: {metadata.framework_only}")
