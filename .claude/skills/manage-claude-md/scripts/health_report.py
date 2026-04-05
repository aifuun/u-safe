#!/usr/bin/env python3
"""
生成项目健康报告

检查项目的健康状况（skills, plans, rules, docs 等），生成 0-100 分的健康评分。
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import yaml


class ProfileError(Exception):
    """Profile 配置错误"""
    pass


def read_profile(project_root: Path) -> Optional[Dict]:
    """
    读取项目 profile 配置

    Returns:
        Dict 包含 profile 信息，或 None 如果不存在
    """
    profile_path = project_root / "docs" / "project-profile.md"

    if not profile_path.exists():
        return None

    try:
        content = profile_path.read_text(encoding='utf-8')

        # 提取 YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                return yaml.safe_load(yaml_content)

        return None
    except Exception as e:
        raise ProfileError(f"Failed to read profile: {e}")


def find_project_root() -> Path:
    """查找项目根目录（包含 .claude/ 的目录）"""
    current = Path.cwd()

    # 向上查找直到找到 .claude/
    while current != current.parent:
        if (current / ".claude").exists():
            return current
        current = current.parent

    raise FileNotFoundError("未找到 .claude/ 目录 - 请在项目根目录运行此脚本")


def check_skills_health(project_root: Path) -> Tuple[int, Dict]:
    """
    检查 Skills 健康度 (0-25 分)

    评分标准:
    - Skills 目录存在: 5 分
    - 至少 10 个 skills: 10 分
    - 所有 skills 有 SKILL.md: 5 分
    - Skills 分类清晰: 5 分
    """
    score = 0
    details = {}

    skills_dir = project_root / ".claude" / "skills"

    if not skills_dir.exists():
        details["skills_dir"] = "❌ 不存在"
        return 0, details

    score += 5
    details["skills_dir"] = "✅ 存在"

    # 统计 skills 数量
    skills = [d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith('.') and not d.name.startswith('_')]
    skill_count = len(skills)
    details["skill_count"] = skill_count

    if skill_count >= 10:
        score += 10
    elif skill_count >= 5:
        score += 5

    # 检查 SKILL.md 存在性
    skills_with_docs = sum(1 for s in skills if (s / "SKILL.md").exists())
    if skills_with_docs == skill_count:
        score += 5
        details["skill_docs"] = f"✅ 全部有文档 ({skills_with_docs}/{skill_count})"
    else:
        details["skill_docs"] = f"⚠️  部分缺失文档 ({skills_with_docs}/{skill_count})"

    # 检查分类（有 README.md）
    if (skills_dir / "README.md").exists():
        score += 5
        details["skill_index"] = "✅ 有索引文档"
    else:
        details["skill_index"] = "⚠️  缺少索引文档"

    return score, details


def check_plans_health(project_root: Path) -> Tuple[int, Dict]:
    """
    检查 Plans 健康度 (0-15 分)

    评分标准:
    - Plans 目录结构完整: 5 分
    - Active plans < 5 个: 5 分
    - 有归档记录: 5 分
    """
    score = 0
    details = {}

    plans_dir = project_root / ".claude" / "plans"

    if not plans_dir.exists():
        details["plans_dir"] = "❌ 不存在"
        return 0, details

    score += 5
    details["plans_dir"] = "✅ 存在"

    # 检查 active plans
    active_dir = plans_dir / "active"
    if active_dir.exists():
        active_plans = list(active_dir.glob("*.md"))
        active_count = len(active_plans)
        details["active_plans"] = active_count

        if active_count < 5:
            score += 5
        elif active_count < 10:
            score += 3
    else:
        details["active_plans"] = "⚠️  active/ 目录不存在"

    # 检查 archive
    archive_dir = plans_dir / "archive"
    if archive_dir.exists() and any(archive_dir.iterdir()):
        score += 5
        archive_count = len(list(archive_dir.glob("*.md")))
        details["archive"] = f"✅ 有归档 ({archive_count} 个)"
    else:
        details["archive"] = "ℹ️  无归档记录"

    return score, details


def check_rules_health(project_root: Path) -> Tuple[int, Dict]:
    """
    检查 Rules 健康度 (0-20 分)

    评分标准:
    - Rules 目录存在: 5 分
    - 至少 15 个 rules: 10 分
    - 有 profile 配置: 5 分
    """
    score = 0
    details = {}

    rules_dir = project_root / ".claude" / "rules"

    if not rules_dir.exists():
        details["rules_dir"] = "❌ 不存在"
        return 0, details

    score += 5
    details["rules_dir"] = "✅ 存在"

    # 统计 rules 数量
    rule_files = list(rules_dir.rglob("*.md"))
    rule_count = len(rule_files)
    details["rule_count"] = rule_count

    if rule_count >= 15:
        score += 10
    elif rule_count >= 10:
        score += 5
    elif rule_count >= 5:
        score += 3

    # 检查 profile (Issue #481: Use shared config reader)
    try:
        profile_data = read_profile(project_root)
        if profile_data:
            score += 5
            profile_name = profile_data.get('name', 'unknown')
            details["profile"] = f"✅ 有 profile 配置 ({profile_name})"
        else:
            details["profile"] = "⚠️  缺少 profile 配置（project-profile.md）"
    except ProfileError as e:
        details["profile"] = f"⚠️  Profile 配置错误: {e}"

    return score, details


def check_docs_health(project_root: Path) -> Tuple[int, Dict]:
    """
    检查 Docs 健康度 (0-20 分)

    评分标准:
    - CLAUDE.md 存在: 5 分
    - README.md 存在: 5 分
    - ADRs 目录存在: 5 分
    - 至少 5 个 ADRs: 5 分
    """
    score = 0
    details = {}

    # CLAUDE.md
    if (project_root / "CLAUDE.md").exists():
        score += 5
        details["claude_md"] = "✅ 存在"
    else:
        details["claude_md"] = "❌ 不存在"

    # README.md
    if (project_root / "README.md").exists():
        score += 5
        details["readme"] = "✅ 存在"
    else:
        details["readme"] = "⚠️  不存在"

    # ADRs
    adrs_dir = project_root / "docs" / "adr"
    if adrs_dir.exists():
        score += 5
        details["adrs_dir"] = "✅ 存在"

        adr_files = list(adrs_dir.glob("*.md"))
        adr_count = len([f for f in adr_files if f.name != "README.md"])
        details["adr_count"] = adr_count

        if adr_count >= 5:
            score += 5
        elif adr_count >= 3:
            score += 3
    else:
        details["adrs_dir"] = "⚠️  不存在"

    return score, details


def check_git_health(project_root: Path) -> Tuple[int, Dict]:
    """
    检查 Git 健康度 (0-20 分)

    评分标准:
    - 是 Git 仓库: 5 分
    - 有 .gitignore: 5 分
    - Working directory clean: 5 分
    - 有远程仓库: 5 分
    """
    score = 0
    details = {}

    git_dir = project_root / ".git"

    if not git_dir.exists():
        details["git"] = "⚠️  不是 Git 仓库"
        return 0, details

    score += 5
    details["git"] = "✅ Git 仓库"

    # .gitignore
    if (project_root / ".gitignore").exists():
        score += 5
        details["gitignore"] = "✅ 存在"
    else:
        details["gitignore"] = "⚠️  不存在"

    # Working directory status (通过 git status 检查)
    import subprocess
    try:
        result = subprocess.run(
            ['git', '-C', str(project_root), 'status', '--porcelain'],
            capture_output=True,
            text=True,
            check=True
        )

        if not result.stdout.strip():
            score += 5
            details["working_dir"] = "✅ Clean"
        else:
            details["working_dir"] = "⚠️  有未提交更改"
    except:
        details["working_dir"] = "⚠️  检查失败"

    # 远程仓库
    try:
        result = subprocess.run(
            ['git', '-C', str(project_root), 'remote', '-v'],
            capture_output=True,
            text=True,
            check=True
        )

        if result.stdout.strip():
            score += 5
            details["remote"] = "✅ 有远程仓库"
        else:
            details["remote"] = "⚠️  无远程仓库"
    except:
        details["remote"] = "⚠️  检查失败"

    return score, details


def generate_report(project_root: Path) -> Dict:
    """生成完整健康报告"""

    print("🏥 项目健康检查")
    print(f"📁 项目: {project_root}\n")

    # 各维度检查
    skills_score, skills_details = check_skills_health(project_root)
    print(f"1️⃣  Skills 健康度: {skills_score}/25")
    for k, v in skills_details.items():
        print(f"   - {k}: {v}")
    print()

    plans_score, plans_details = check_plans_health(project_root)
    print(f"2️⃣  Plans 健康度: {plans_score}/15")
    for k, v in plans_details.items():
        print(f"   - {k}: {v}")
    print()

    rules_score, rules_details = check_rules_health(project_root)
    print(f"3️⃣  Rules 健康度: {rules_score}/20")
    for k, v in rules_details.items():
        print(f"   - {k}: {v}")
    print()

    docs_score, docs_details = check_docs_health(project_root)
    print(f"4️⃣  Docs 健康度: {docs_score}/20")
    for k, v in docs_details.items():
        print(f"   - {k}: {v}")
    print()

    git_score, git_details = check_git_health(project_root)
    print(f"5️⃣  Git 健康度: {git_score}/20")
    for k, v in git_details.items():
        print(f"   - {k}: {v}")
    print()

    # 总分
    total_score = skills_score + plans_score + rules_score + docs_score + git_score

    print("=" * 50)
    print(f"📊 总体健康度: {total_score}/100")

    if total_score >= 90:
        grade = "🌟 优秀"
    elif total_score >= 75:
        grade = "✅ 良好"
    elif total_score >= 60:
        grade = "⚠️  中等"
    else:
        grade = "❌ 需要改进"

    print(f"   等级: {grade}")

    return {
        "total_score": total_score,
        "breakdown": {
            "skills": skills_score,
            "plans": plans_score,
            "rules": rules_score,
            "docs": docs_score,
            "git": git_score
        },
        "details": {
            "skills": skills_details,
            "plans": plans_details,
            "rules": rules_details,
            "docs": docs_details,
            "git": git_details
        }
    }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="生成项目健康报告")
    parser.add_argument(
        '--json',
        action='store_true',
        help='输出 JSON 格式'
    )

    args = parser.parse_args()

    try:
        # 查找项目根目录
        project_root = find_project_root()

        # 生成报告
        report = generate_report(project_root)

        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
