#!/usr/bin/env python3
"""
CLAUDE.md Skills Synchronization Module

从 .claude/skills/ 扫描已安装技能，并自动更新 CLAUDE.md 中的技能列表。

功能：
1. 扫描 .claude/skills/ 目录获取所有已安装技能
2. 解析每个技能的 YAML frontmatter（name, version, description）
3. 解析 CLAUDE.md 当前技能表格
4. 检测差异（新增/删除/版本不匹配）
5. 自动更新 CLAUDE.md 技能表格
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass


@dataclass
class Skill:
    """技能元数据"""
    name: str
    version: str
    description: str
    category: str = "Other"  # 默认分类


def scan_installed_skills(skills_dir: str = ".claude/skills") -> List[Skill]:
    """
    扫描 .claude/skills/ 目录获取所有已安装技能。

    Args:
        skills_dir: 技能目录路径

    Returns:
        已安装技能列表
    """
    skills = []
    skills_path = Path(skills_dir)

    if not skills_path.exists():
        print(f"❌ Skills directory not found: {skills_dir}")
        return skills

    # 遍历所有子目录
    for skill_path in skills_path.iterdir():
        if not skill_path.is_dir():
            continue

        # 检查是否有 SKILL.md
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            continue

        # 解析 SKILL.md 的 YAML frontmatter
        skill = parse_skill_metadata(skill_md)
        if skill:
            skills.append(skill)

    return sorted(skills, key=lambda s: s.name)


def parse_skill_metadata(skill_md_path: Path) -> Skill:
    """
    解析 SKILL.md 的 YAML frontmatter 获取技能元数据。

    Args:
        skill_md_path: SKILL.md 文件路径

    Returns:
        Skill 对象，如果解析失败返回 None
    """
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取 YAML frontmatter (在 --- 之间)
        yaml_match = re.search(r'^---\n(.*?)\n---', content, re.MULTILINE | re.DOTALL)
        if not yaml_match:
            print(f"⚠️  No YAML frontmatter found in {skill_md_path}")
            return None

        yaml_content = yaml_match.group(1)

        # 解析 name
        name_match = re.search(r'^name:\s*(.+)$', yaml_content, re.MULTILINE)
        name = name_match.group(1).strip() if name_match else skill_md_path.parent.name

        # 解析 version
        version_match = re.search(r'^version:\s*["\']?([^"\']+)["\']?$', yaml_content, re.MULTILINE)
        version = version_match.group(1).strip() if version_match else "unknown"

        # 解析 description (第一行)
        desc_match = re.search(r'^description:\s*\|?\n?\s*(.+)$', yaml_content, re.MULTILINE)
        if desc_match:
            description = desc_match.group(1).strip()
        else:
            # 尝试从 # 标题提取
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            description = title_match.group(1).strip() if title_match else "No description"

        # 自动分类（基于技能名称）
        category = infer_category(name)

        return Skill(
            name=name,
            version=version,
            description=description.split('\n')[0],  # 仅取第一行
            category=category
        )

    except Exception as e:
        print(f"❌ Error parsing {skill_md_path}: {e}")
        return None


def infer_category(skill_name: str) -> str:
    """
    根据技能名称自动推断分类。

    Args:
        skill_name: 技能名称

    Returns:
        分类名称
    """
    # 分类映射
    categories = {
        "Issue Lifecycle": ["start-issue", "execute-plan", "finish-issue", "work-issue", "auto-solve-issue"],
        "Planning & Validation": ["plan", "eval-plan", "next"],
        "Quality Assurance": ["review", "skill-creator"],
        "Framework Sync": ["update-pillars", "update-rules", "update-skills", "update-workflow", "update-framework"],
        "Project Maintenance": ["maintain-project", "check-docs", "init-docs"],
        "Project Management": ["overview", "status", "worktree"],
        "Configuration": ["configure-permissions", "adr"],
        "Development Tools": ["sync"],
    }

    for category, skills in categories.items():
        if skill_name in skills:
            return category

    return "Other"


def parse_claude_md_skills(claude_md_path: str = "CLAUDE.md") -> Dict[str, Skill]:
    """
    解析 CLAUDE.md 当前的技能表格。

    Args:
        claude_md_path: CLAUDE.md 文件路径

    Returns:
        技能字典 {name: Skill}
    """
    skills = {}

    if not Path(claude_md_path).exists():
        print(f"❌ CLAUDE.md not found: {claude_md_path}")
        return skills

    with open(claude_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找技能表格（在 "Skills by Category" 部分）
    # 格式：| **Category** | skill1, skill2, skill3 | Purpose |
    table_pattern = r'\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|'
    matches = re.findall(table_pattern, content)

    for category, skills_str, purpose in matches:
        # 跳过表头
        if "Category" in category or "---" in category:
            continue

        # 解析技能列表
        skill_names = [s.strip() for s in skills_str.split(',')]
        for name in skill_names:
            if name and not name.startswith('-'):
                skills[name] = Skill(
                    name=name,
                    version="unknown",  # CLAUDE.md 表格中没有版本信息
                    description=purpose.strip(),
                    category=category.strip()
                )

    return skills


def detect_differences(installed: List[Skill], documented: Dict[str, Skill]) -> Dict[str, List[str]]:
    """
    检测已安装技能与文档技能之间的差异。

    Args:
        installed: 已安装技能列表
        documented: 已文档化技能字典

    Returns:
        差异字典 {"added": [...], "removed": [...], "updated": [...]}
    """
    installed_names = {s.name for s in installed}
    documented_names = set(documented.keys())

    diff = {
        "added": list(installed_names - documented_names),
        "removed": list(documented_names - installed_names),
        "updated": []
    }

    # 检测版本更新（暂不实现，因为 CLAUDE.md 表格中没有版本信息）

    return diff


def update_claude_md_skills(claude_md_path: str, installed: List[Skill], dry_run: bool = False) -> bool:
    """
    更新 CLAUDE.md 中的技能表格。

    Args:
        claude_md_path: CLAUDE.md 文件路径
        installed: 已安装技能列表
        dry_run: 是否为预览模式

    Returns:
        是否成功更新
    """
    if not Path(claude_md_path).exists():
        print(f"❌ CLAUDE.md not found: {claude_md_path}")
        return False

    with open(claude_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 按分类组织技能
    skills_by_category = {}
    for skill in installed:
        if skill.category not in skills_by_category:
            skills_by_category[skill.category] = []
        skills_by_category[skill.category].append(skill)

    # 生成技能表格
    table_lines = [
        "| Category | Skills | Purpose |",
        "|----------|--------|---------|",
    ]

    # 定义分类顺序
    category_order = [
        "Issue Lifecycle",
        "Planning & Validation",
        "Quality Assurance",
        "Framework Sync",
        "Project Maintenance",
        "Project Management",
        "Configuration",
        "Development Tools",
        "Other"
    ]

    for category in category_order:
        if category not in skills_by_category:
            continue

        skills = skills_by_category[category]
        skill_names = ", ".join(s.name for s in skills)

        # 使用第一个技能的描述作为分类描述（简化处理）
        purpose = get_category_purpose(category)

        table_lines.append(f"| **{category}** | {skill_names} | {purpose} |")

    new_table = "\n".join(table_lines)

    # 替换 CLAUDE.md 中的技能表格
    # 查找 "### Skills by Category" 和下一个 "###" 之间的内容
    pattern = r'(### Skills by Category.*?\n\n)(.*?)(\n\n###)'
    replacement = rf'\1{new_table}\3'

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if new_content == content:
        print("✅ CLAUDE.md skills table is already up to date")
        return True

    if dry_run:
        print("\n🔍 Preview of changes to CLAUDE.md:\n")
        print(new_table)
        print("\n(Dry run - no changes made)")
        return True

    # 写回文件
    with open(claude_md_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("✅ Updated CLAUDE.md skills table")
    return True


def get_category_purpose(category: str) -> str:
    """获取分类描述"""
    purposes = {
        "Issue Lifecycle": "Complete issue workflow automation",
        "Planning & Validation": "Create and validate implementation plans",
        "Quality Assurance": "Code review and skill testing",
        "Framework Sync": "Keep projects in sync with framework",
        "Project Maintenance": "Maintain project-specific content",
        "Project Management": "View project state and manage parallel work",
        "Configuration": "Set up permissions and document decisions",
        "Development Tools": "Development utilities",
        "Other": "Additional utilities"
    }
    return purposes.get(category, "Various utilities")


def main():
    """主函数"""
    # 解析命令行参数
    dry_run = "--dry-run" in sys.argv
    verbose = "--verbose" in sys.argv

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("CLAUDE.md Skills Sync")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    # 1. 扫描已安装技能
    print("✅ Scanning .claude/skills/ directory...")
    installed = scan_installed_skills()
    print(f"✅ Found {len(installed)} installed skills\n")

    if verbose:
        for skill in installed:
            print(f"  - {skill.name} v{skill.version} ({skill.category})")
        print()

    # 2. 解析 CLAUDE.md 当前技能
    print("✅ Parsing CLAUDE.md current skills table...")
    documented = parse_claude_md_skills()
    print(f"✅ Found {len(documented)} documented skills\n")

    # 3. 检测差异
    diff = detect_differences(installed, documented)

    if diff["added"]:
        print(f"✅ Found {len(diff['added'])} new skills not documented:")
        for name in diff["added"]:
            skill = next((s for s in installed if s.name == name), None)
            if skill:
                print(f"   - {name} v{skill.version} ({skill.category})")
        print()

    if diff["removed"]:
        print(f"⚠️  Found {len(diff['removed'])} skills removed from .claude/skills/:")
        for name in diff["removed"]:
            print(f"   - {name}")
        print()

    if not diff["added"] and not diff["removed"]:
        print("✅ CLAUDE.md skills list is already up to date\n")
        return

    # 4. 更新 CLAUDE.md
    if dry_run:
        print("🔍 Dry run mode - previewing changes...\n")

    success = update_claude_md_skills("CLAUDE.md", installed, dry_run=dry_run)

    if success and not dry_run:
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("Summary")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"✅ CLAUDE.md updated: +{len(diff['added'])}, -{len(diff['removed'])}")
        print(f"✅ Total skills: {len(installed)}")


if __name__ == "__main__":
    main()
