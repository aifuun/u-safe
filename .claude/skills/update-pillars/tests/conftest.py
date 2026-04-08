"""
共享测试 Fixtures - 为所有测试提供公共测试数据和辅助函数

基于 ADR-020 标准，提供:
- 临时目录 fixtures (source/target project structure)
- Pillar 内容 fixtures (示例 Pillar 文件)
- Profile fixtures (测试用 profile 配置)
- 辅助函数 (创建测试 Pillars, 验证同步结果)
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_test_root(tmp_path):
    """创建临时测试根目录

    Returns:
        Path: 临时测试根目录路径
    """
    return tmp_path


@pytest.fixture
def source_project(temp_test_root):
    """创建源项目结构 (ai-dev framework)

    Returns:
        dict: {
            'root': Path,  # 项目根目录
            'pillars': Path,  # .claude/pillars/ 目录
        }
    """
    source_root = temp_test_root / "ai-dev"
    source_pillars = source_root / ".claude" / "pillars"
    source_pillars.mkdir(parents=True)

    return {
        "root": source_root,
        "pillars": source_pillars,
    }


@pytest.fixture
def target_project(temp_test_root):
    """创建目标项目结构

    Returns:
        dict: {
            'root': Path,  # 项目根目录
            'pillars': Path,  # .claude/pillars/ 目录
            'docs': Path,  # docs/ 目录 (for profile)
        }
    """
    target_root = temp_test_root / "my-app"
    target_pillars = target_root / ".claude" / "pillars"
    target_pillars.mkdir(parents=True)
    target_docs = target_root / "docs"
    target_docs.mkdir()

    return {
        "root": target_root,
        "pillars": target_pillars,
        "docs": target_docs,
    }


@pytest.fixture
def sample_pillar_content():
    """示例 Pillar 文件内容

    Returns:
        dict: {
            'pillar-a': str,  # Pillar A 内容
            'pillar-b': str,  # Pillar B 内容
            'pillar-k': str,  # Pillar K 内容
        }
    """
    return {
        "pillar-a": """# Pillar A: Architecture & Design

## Overview
Architecture decisions and design patterns.

## Best Practices
- Use layered architecture
- Separate concerns
- Follow SOLID principles

## Examples
```python
# Example code
```
""" * 5,  # 250 lines
        "pillar-b": """# Pillar B: Code Quality

## Overview
Code quality standards and practices.

## Guidelines
- Write readable code
- Add meaningful comments
- Follow style guide

## Tools
- Linters
- Formatters
- Type checkers
""" * 4,  # 200 lines
        "pillar-k": """# Pillar K: Testing

## Overview
Testing strategies and best practices.

## Types of Tests
- Unit tests
- Integration tests
- End-to-end tests

## Coverage
Aim for 80%+ coverage.
""" * 6,  # 180 lines
    }


@pytest.fixture
def minimal_profile_content():
    """minimal profile 配置内容

    Returns:
        str: Profile 文件内容
    """
    return """---
profile: minimal
type: basic
rules:
  include:
    - core/*
---

# Project Profile

This project uses the minimal profile.
"""


@pytest.fixture
def node_lambda_profile_content():
    """node-lambda profile 配置内容

    Returns:
        str: Profile 文件内容
    """
    return """---
profile: node-lambda
type: backend
rules:
  include:
    - core/*
    - languages/typescript.md
    - backend/nodejs.md
---

# Project Profile

This project uses the node-lambda profile.
"""


def create_pillar(pillars_dir: Path, pillar_name: str, content: str):
    """创建测试 Pillar

    Args:
        pillars_dir: Pillars 目录路径
        pillar_name: Pillar 名称 (e.g., 'pillar-a')
        content: Pillar 文件内容
    """
    pillar_dir = pillars_dir / pillar_name
    pillar_dir.mkdir(exist_ok=True)
    pillar_file = pillar_dir / f"{pillar_name}.md"
    pillar_file.write_text(content)


def verify_pillar_synced(target_pillars_dir: Path, pillar_name: str, expected_content: str):
    """验证 Pillar 已正确同步

    Args:
        target_pillars_dir: 目标 Pillars 目录
        pillar_name: Pillar 名称
        expected_content: 期望的内容

    Returns:
        bool: 是否同步成功
    """
    pillar_file = target_pillars_dir / pillar_name / f"{pillar_name}.md"
    if not pillar_file.exists():
        return False
    return pillar_file.read_text() == expected_content


def count_pillars(pillars_dir: Path) -> int:
    """统计 Pillars 目录中的 Pillar 数量

    Args:
        pillars_dir: Pillars 目录路径

    Returns:
        int: Pillar 数量
    """
    return len(list(pillars_dir.glob("pillar-*")))
