"""
pytest fixtures for update-guides tests

Provides:
- temp_framework_dir: 临时 ai-dev framework 目录
- temp_target_project: 临时目标项目目录
- setup_guides_structure: 创建完整的 .claude/guides/ 结构（20 个文件）
- version_file_path: .ai-guides-version 文件路径
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_framework_dir(tmp_path):
    """创建临时 framework 目录（ai-dev）"""
    framework_dir = tmp_path / "ai-dev"
    framework_dir.mkdir()
    return framework_dir


@pytest.fixture
def temp_target_project(tmp_path):
    """创建临时目标项目目录"""
    target_dir = tmp_path / "target-project"
    target_dir.mkdir()
    return target_dir


@pytest.fixture
def setup_guides_structure(temp_framework_dir):
    """
    创建完整的 .claude/guides/ 结构（20 个文件）

    目录结构:
    .claude/guides/
    ├── workflow/ (6 files)
    ├── doc-templates/ (3 files)
    ├── rules/ (5 files)
    ├── profiles/ (4 files)
    └── templates/ (2 files)
    """
    guides_dir = temp_framework_dir / ".claude" / "guides"
    guides_dir.mkdir(parents=True)

    # workflow/ (6 files)
    workflow_dir = guides_dir / "workflow"
    workflow_dir.mkdir()
    workflow_files = [
        "README.md",
        "ADR_GUIDE.md",
        "CLAUDE_MD_GUIDE.md",
        "ISSUE_LIFECYCLE_GUIDE.md",
        "PROJECT_PLANNING_GUIDE.md",
        "SKILL_GUIDE.md"
    ]
    for filename in workflow_files:
        (workflow_dir / filename).write_text(f"# {filename}\nWorkflow guide content")

    # doc-templates/ (3 files)
    doc_templates_dir = guides_dir / "doc-templates"
    doc_templates_dir.mkdir()
    doc_template_files = [
        "README.md",
        "MANAGE_DOCS_GUIDE.md",
        "STACK_TAGS.md"
    ]
    for filename in doc_template_files:
        (doc_templates_dir / filename).write_text(f"# {filename}\nDoc template content")

    # rules/ (5 files)
    rules_dir = guides_dir / "rules"
    rules_dir.mkdir()
    rules_files = [
        "README.md",
        "RULES_GUIDE.md",
        "RULES_MAPPING.md",
        "PROFILE_CONSISTENCY.md",
        "MIGRATION_REPORT.md"
    ]
    for filename in rules_files:
        (rules_dir / filename).write_text(f"# {filename}\nRules guide content")

    # profiles/ (4 files)
    profiles_dir = guides_dir / "profiles"
    profiles_dir.mkdir()
    profile_files = [
        "README.md",
        "tauri.md",
        "nextjs-aws.md",
        "framework.md"
    ]
    for filename in profile_files:
        (profiles_dir / filename).write_text(f"# {filename}\nProfile content")

    # templates/ (2 files)
    templates_dir = guides_dir / "templates"
    templates_dir.mkdir()
    template_files = [
        "README.md",
        "TEMPLATE_GUIDE.md"
    ]
    for filename in template_files:
        (templates_dir / filename).write_text(f"# {filename}\nTemplate content")

    return guides_dir


@pytest.fixture
def version_file_path(temp_target_project):
    """返回 .ai-guides-version 文件路径"""
    return temp_target_project / ".ai-guides-version"
