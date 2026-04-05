"""
Shared configuration utilities for skills

Provides common configuration loading functions used across multiple skills.
"""

from pathlib import Path
from typing import Dict, Optional, Literal
from dataclasses import dataclass
import json


class ConfigError(Exception):
    """Configuration-related errors"""
    pass


class ProfileError(ConfigError):
    """Profile-specific configuration errors"""
    pass


@dataclass
class Profile:
    """
    Profile configuration object

    Attributes:
        name: Profile name (tauri, nextjs-aws, minimal, etc.)
        source: Where the profile was detected from
    """
    name: str
    source: Literal["CLAUDE.md", "project-profile.md"]


def load_profile_config(profile: str, project_root: Optional[Path] = None) -> Dict:
    """
    Load profile configuration from .claude/profiles/ or framework/profiles/

    Args:
        profile: Profile name
        project_root: Optional project root path (default: current directory)

    Returns:
        dict: Profile configuration

    Raises:
        ConfigError: If config invalid or not found
    """
    if project_root is None:
        project_root = Path.cwd()

    # 查找 profile 配置文件
    profile_paths = [
        project_root / ".claude" / "profiles" / f"{profile}.json",
        project_root / "framework" / "profiles" / f"{profile}.json"
    ]

    profile_file = None
    for path in profile_paths:
        if path.exists():
            profile_file = path
            break

    if not profile_file:
        raise ConfigError(f"Profile config not found: {profile}")

    try:
        with open(profile_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 验证必需字段
        if 'rules' not in config:
            raise ConfigError(f"Profile config missing 'rules' field: {profile}")

        if 'include' not in config['rules']:
            raise ConfigError(f"Profile config missing 'rules.include' field: {profile}")

        # 添加默认的 exclude 字段（如果缺失）
        if 'exclude' not in config['rules']:
            config['rules']['exclude'] = []

        return config

    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in profile config: {e}")
    except Exception as e:
        raise ConfigError(f"Error loading profile config: {e}")


def read_profile(project_root: Optional[Path] = None) -> Profile:
    """
    Read profile from CLAUDE.md (priority) or project-profile.md

    Priority order (Issue #481):
    1. CLAUDE.md frontmatter (field: profile)
    2. docs/project-profile.md frontmatter (field: profile)

    Args:
        project_root: Optional project root path (default: current directory)

    Returns:
        Profile: Profile object with name and source

    Raises:
        ProfileError: If profile not found or invalid in both locations

    Example:
        >>> profile = read_profile()
        >>> print(f"Detected {profile.name} from {profile.source}")
        Detected tauri from CLAUDE.md
    """
    if project_root is None:
        project_root = Path.cwd()

    # Priority 1: Try CLAUDE.md first
    claude_md = project_root / "CLAUDE.md"
    if claude_md.exists():
        profile_name = _extract_profile_from_frontmatter(claude_md)
        if profile_name:
            return Profile(name=profile_name, source="CLAUDE.md")

    # Priority 2: Fallback to project-profile.md
    profile_md = project_root / "docs" / "project-profile.md"
    if profile_md.exists():
        profile_name = _extract_profile_from_frontmatter(profile_md)
        if profile_name:
            return Profile(name=profile_name, source="project-profile.md")

    # Neither location has valid profile
    raise ProfileError(
        "Profile not found. Expected 'profile' field in YAML frontmatter of:\n"
        f"  1. {claude_md} (priority), or\n"
        f"  2. {profile_md}"
    )


def _extract_profile_from_frontmatter(file_path: Path) -> Optional[str]:
    """
    Extract profile field from YAML frontmatter

    YAML frontmatter format:
    ---
    profile: tauri
    name: My Project
    ---

    Args:
        file_path: Path to markdown file with frontmatter

    Returns:
        str: Profile name if found, None otherwise

    Note:
        Silently returns None on parsing errors to allow fallback logic
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for YAML frontmatter delimiter
        if not content.startswith('---\n'):
            return None

        # Extract frontmatter between first two '---'
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None

        # Parse YAML frontmatter
        import yaml
        frontmatter = yaml.safe_load(parts[1])

        # Return profile field (None if missing)
        if isinstance(frontmatter, dict):
            return frontmatter.get('profile')

        return None

    except Exception:
        # Silently ignore parsing errors to allow fallback
        return None
