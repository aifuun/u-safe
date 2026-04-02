"""版本管理和验证模块

提供统一的版本检查和比较逻辑，用于eval-plan和review等skills。

Created: 2026-03-30 (Issue #406)
"""

import re
from pathlib import Path
from typing import Optional, Dict
import yaml


class VersionError(Exception):
    """版本验证失败异常"""
    pass


def validate_version_format(version: str) -> bool:
    """验证版本格式（语义化版本: MAJOR.MINOR.PATCH）

    Args:
        version: 版本号字符串

    Returns:
        bool: 版本格式是否有效

    Examples:
        >>> validate_version_format("1.0.0")
        True
        >>> validate_version_format("2.3.1")
        True
        >>> validate_version_format("v1.0.0")
        False
        >>> validate_version_format("1.0")
        False
    """
    if not isinstance(version, str):
        return False

    # 语义化版本格式: X.Y 或 X.Y.Z（不允许v前缀）
    pattern = r'^\d+\.\d+(\.\d+)?$'
    return bool(re.match(pattern, version))


def get_version_from_frontmatter(content: str) -> Optional[str]:
    """从YAML frontmatter提取version字段

    Args:
        content: 文件内容（包含YAML frontmatter）

    Returns:
        Optional[str]: 版本号，如果不存在则返回None

    Examples:
        >>> content = '''---
        ... version: "1.4.0"
        ... name: test-skill
        ... ---
        ... # Skill
        ... '''
        >>> get_version_from_frontmatter(content)
        '1.4.0'
    """
    # 提取YAML frontmatter
    frontmatter_match = re.match(r'^---\n(.+?)\n---', content, re.DOTALL)

    if not frontmatter_match:
        return None

    try:
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
        return frontmatter.get("version")
    except yaml.YAMLError:
        return None


def check_version_field(skill_path: Path) -> Dict[str, any]:
    """检查SKILL.md的YAML frontmatter是否包含version字段

    Args:
        skill_path: SKILL.md文件路径

    Returns:
        dict: 包含以下键:
            - has_version: bool - 是否有version字段
            - version: str | None - 版本号
            - valid_format: bool - 格式是否有效
            - errors: List[str] - 错误列表

    Examples:
        >>> result = check_version_field(Path(".claude/skills/eval-plan/SKILL.md"))
        >>> result['has_version']
        True
        >>> result['version']
        '1.4.0'
    """
    if not skill_path.exists():
        return {
            "has_version": False,
            "version": None,
            "valid_format": False,
            "errors": [f"File not found: {skill_path}"]
        }

    try:
        content = skill_path.read_text(encoding='utf-8')
    except Exception as e:
        return {
            "has_version": False,
            "version": None,
            "valid_format": False,
            "errors": [f"Failed to read file: {e}"]
        }

    # 提取YAML frontmatter
    frontmatter_match = re.match(r'^---\n(.+?)\n---', content, re.DOTALL)

    if not frontmatter_match:
        return {
            "has_version": False,
            "version": None,
            "valid_format": False,
            "errors": ["No YAML frontmatter found"]
        }

    try:
        frontmatter = yaml.safe_load(frontmatter_match.group(1))

        # 检查version字段
        if "version" not in frontmatter:
            return {
                "has_version": False,
                "version": None,
                "valid_format": False,
                "errors": ["Missing 'version' field in frontmatter"]
            }

        version = frontmatter["version"]

        # 验证版本格式
        if not validate_version_format(str(version)):
            return {
                "has_version": True,
                "version": version,
                "valid_format": False,
                "errors": [f"Invalid version format: '{version}' (expected: X.Y or X.Y.Z)"]
            }

        return {
            "has_version": True,
            "version": version,
            "valid_format": True,
            "errors": []
        }

    except yaml.YAMLError as e:
        return {
            "has_version": False,
            "version": None,
            "valid_format": False,
            "errors": [f"YAML parsing error: {e}"]
        }


def compare_versions(v1: str, v2: str) -> int:
    """比较两个版本号

    Args:
        v1: 第一个版本号
        v2: 第二个版本号

    Returns:
        int: 比较结果
            -1: v1 < v2
             0: v1 == v2
             1: v1 > v2

    Raises:
        VersionError: 如果版本格式无效

    Examples:
        >>> compare_versions("1.0.0", "2.0.0")
        -1
        >>> compare_versions("2.0.0", "2.0.0")
        0
        >>> compare_versions("2.1.0", "2.0.0")
        1
    """
    if not validate_version_format(v1):
        raise VersionError(f"Invalid version format: '{v1}'")
    if not validate_version_format(v2):
        raise VersionError(f"Invalid version format: '{v2}'")

    # 解析版本号为元组 (major, minor, patch)
    def parse_version(v: str) -> tuple:
        parts = v.split('.')
        if len(parts) == 2:
            # X.Y格式，补充patch=0
            return (int(parts[0]), int(parts[1]), 0)
        else:
            # X.Y.Z格式
            return (int(parts[0]), int(parts[1]), int(parts[2]))

    v1_tuple = parse_version(v1)
    v2_tuple = parse_version(v2)

    if v1_tuple < v2_tuple:
        return -1
    elif v1_tuple > v2_tuple:
        return 1
    else:
        return 0
