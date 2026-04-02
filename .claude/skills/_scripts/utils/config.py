"""
Shared configuration utilities for skills

Provides common configuration loading functions used across multiple skills.
"""

from pathlib import Path
from typing import Dict, Optional
import json


class ConfigError(Exception):
    """Configuration-related errors"""
    pass


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
