"""
Shared validation utilities for skills

Provides common validation functions used across multiple skills.
"""

from pathlib import Path
from typing import Optional
import json


def validate_profile(profile: str, project_root: Optional[Path] = None) -> bool:
    """
    Validate profile exists and has valid config

    Args:
        profile: Profile name to validate
        project_root: Optional project root path (default: current directory)

    Returns:
        bool: True if valid, False otherwise
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
        return False

    # 验证 JSON 格式
    try:
        with open(profile_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 验证必需字段
        if 'rules' not in config:
            return False

        if 'include' not in config['rules']:
            return False

        return True

    except (json.JSONDecodeError, Exception):
        return False
