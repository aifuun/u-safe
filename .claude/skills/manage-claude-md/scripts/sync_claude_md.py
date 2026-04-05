#!/usr/bin/env python3
"""
同步 CLAUDE.md 的 Skills 列表

扫描 .claude/skills/ 目录，更新 CLAUDE.md 中的 Skills System 部分。
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import re


def find_project_root() -> Path:
    """查找项目根目录（包含 CLAUDE.md 的目录）"""
    current = Path.cwd()

    # 向上查找直到找到 CLAUDE.md
    while current != current.parent:
        if (current / "CLAUDE.md").exists():
            return current
        current = current.parent

    raise FileNotFoundError("未找到 CLAUDE.md - 请在项目根目录运行此脚本")


def scan_skills(skills_dir: Path) -> Dict[str, List[str]]:
    """
    扫描 .claude/skills/ 目录，按分类收集技能

    Returns:
        Dict[category, List[skill_name]]
    """
    if not skills_dir.exists():
        raise FileNotFoundError(f"Skills 目录不存在: {skills_dir}")

    skills_by_category = {
        "Issue Lifecycle": [],
        "Quality": [],
        "Management": [],
        "Sync": [],
        "Utilities": [],
        "Internal": [],
        "Maintenance": [],
        "Deprecated": []
    }

    # 硬编码分类映射（可以后续改为从 SKILL.md 读取）
    category_mapping = {
        # Issue Lifecycle
        "solve-issues": "Issue Lifecycle",
        "auto-solve-issue": "Issue Lifecycle",
        "start-issue": "Issue Lifecycle",
        "execute-plan": "Issue Lifecycle",
        "finish-issue": "Issue Lifecycle",

        # Quality
        "review": "Quality",
        "eval-plan": "Quality",

        # Management
        "manage-project": "Management",
        "manage-rules": "Management",
        "manage-adrs": "Management",
        "manage-claude-md": "Management",
        "manage-docs": "Management",
        "init-docs": "Management",
        "check-docs": "Management",

        # Sync
        "update-framework": "Sync",
        "update-pillars": "Sync",
        "update-workflow": "Sync",
        "update-skills": "Sync",
        "update-guides": "Sync",

        # Utilities
        "status": "Utilities",
        "preflight-check": "Utilities",
        "create-issue": "Utilities",
        "skill-creator": "Utilities",
        "overview": "Utilities",

        # Internal
        "migrate-docs": "Internal",
        "update-doc-refs": "Internal",
        "worktree": "Internal",
        "plan": "Internal",
        "next": "Internal",
        "sync": "Internal",
        "update-permissions": "Internal",

        # Maintenance
        "configure-permissions": "Maintenance",
        "cleanup-project": "Maintenance",

        # Deprecated
        "adr": "Deprecated",
        "maintain-project": "Deprecated",
        "dev-issue": "Deprecated",
        "update-rules": "Deprecated"
    }

    # 扫描所有 skill 目录
    for item in sorted(skills_dir.iterdir()):
        if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('_'):
            skill_name = item.name
            category = category_mapping.get(skill_name, "Utilities")
            skills_by_category[category].append(skill_name)

    # 移除空分类
    return {k: v for k, v in skills_by_category.items() if v}


def generate_skills_table(skills_by_category: Dict[str, List[str]]) -> str:
    """生成 Skills System 的 Markdown 表格"""
    lines = []
    lines.append("| Category | Key Skills | Purpose |")
    lines.append("|----------|------------|---------|")

    category_descriptions = {
        "Issue Lifecycle": "Complete workflow from planning to merge",
        "Quality": "Code review and plan validation",
        "Management": "Profile and content management (unified manage-* naming)",
        "Sync": "Keep projects in sync",
        "Utilities": "Status checks, issue creation, skill development",
        "Internal": "Framework development utilities",
        "Maintenance": "Project upkeep and config",
        "Deprecated": "Use manage-adrs, manage-claude-md, execute-plan, manage-rules instead"
    }

    for category, skills in skills_by_category.items():
        skills_text = ", ".join(skills)
        purpose = category_descriptions.get(category, "")
        lines.append(f"| **{category}** | {skills_text} | {purpose} |")

    return "\n".join(lines)


def update_claude_md(claude_md_path: Path, skills_table: str) -> None:
    """更新 CLAUDE.md 中的 Skills System 部分"""

    if not claude_md_path.exists():
        raise FileNotFoundError(f"CLAUDE.md 不存在: {claude_md_path}")

    content = claude_md_path.read_text(encoding='utf-8')

    # 查找 Skills System 部分的开始和结束标记
    # 开始: ## ⚡ Skills System
    # 结束: 下一个 ## 标题或 **Meta-skill example**

    pattern = r'(## ⚡ Skills System\s+.*?\n\n)(.*?)(\n\n\*\*Meta-skill example\*\*:)'

    def replace_table(match):
        before = match.group(1)
        after = match.group(3)
        return f"{before}{skills_table}{after}"

    updated_content, count = re.subn(pattern, replace_table, content, flags=re.DOTALL)

    if count == 0:
        raise ValueError("未找到 Skills System 部分 - CLAUDE.md 格式可能已更改")

    claude_md_path.write_text(updated_content, encoding='utf-8')
    print(f"✅ 已更新 CLAUDE.md Skills System 部分 ({count} 处)")


def main():
    """主函数"""
    try:
        # 查找项目根目录
        project_root = find_project_root()
        print(f"📁 项目根目录: {project_root}")

        # 扫描 skills
        skills_dir = project_root / ".claude" / "skills"
        print(f"🔍 扫描 skills 目录: {skills_dir}")
        skills_by_category = scan_skills(skills_dir)

        # 统计
        total_skills = sum(len(skills) for skills in skills_by_category.values())
        print(f"📊 找到 {total_skills} 个 skills，{len(skills_by_category)} 个分类")

        # 生成表格
        skills_table = generate_skills_table(skills_by_category)

        # 更新 CLAUDE.md
        claude_md_path = project_root / "CLAUDE.md"
        update_claude_md(claude_md_path, skills_table)

        print("✅ 同步完成")

    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
