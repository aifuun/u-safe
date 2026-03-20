#!/usr/bin/env python3
"""
Project Health Report Module

生成项目健康评分和可操作建议。

功能：
1. 计算 CLAUDE.md 健康评分（技能列表准确性）
2. 计算 plans/ 清洁度评分（活跃计划数量）
3. 生成整体健康评分（加权平均）
4. 提供可操作的改进建议
"""

import sys
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass

# 导入其他模块
from sync_claude_md import scan_installed_skills, parse_claude_md_skills
from cleanup_plans import extract_issue_number, check_issue_status, count_files


@dataclass
class HealthScore:
    """健康评分"""
    score: int  # 0-100
    issues: List[str]  # 问题列表
    recommendations: List[str]  # 改进建议


def check_claude_md_health() -> HealthScore:
    """
    检查 CLAUDE.md 健康状态。

    Returns:
        HealthScore 对象
    """
    # 扫描已安装技能
    installed = scan_installed_skills()
    installed_names = {s.name for s in installed}

    # 解析 CLAUDE.md 已文档化技能
    documented = parse_claude_md_skills()
    documented_names = set(documented.keys())

    # 计算匹配率
    if not installed_names:
        return HealthScore(score=100, issues=[], recommendations=[])

    # 交集
    matched = installed_names & documented_names

    # 计算评分
    match_rate = len(matched) / len(installed_names)
    score = int(match_rate * 100)

    # 检测问题
    issues = []
    recommendations = []

    # 新增技能未文档化
    added = installed_names - documented_names
    if added:
        issues.append(f"{len(added)} new skills not documented")
        recommendations.append(f"Run /maintain-project --component claude-md (adds {len(added)} skills)")

    # 已删除技能仍文档化
    removed = documented_names - installed_names
    if removed:
        issues.append(f"{len(removed)} removed skills still documented")
        recommendations.append(f"Update CLAUDE.md to remove {len(removed)} obsolete skills")

    return HealthScore(
        score=score,
        issues=issues,
        recommendations=recommendations
    )


def check_plans_cleanliness() -> HealthScore:
    """
    检查 plans/ 目录清洁度。

    Returns:
        HealthScore 对象
    """
    active_dir = Path(".claude/plans/active")

    if not active_dir.exists():
        return HealthScore(score=100, issues=[], recommendations=[])

    # 统计活跃计划数量
    active_plans = list(active_dir.glob("*.md"))
    active_count = len(active_plans)

    if active_count == 0:
        return HealthScore(score=100, issues=[], recommendations=[])

    # 检查有多少应该归档
    should_archive = 0
    should_archive_files = []

    for plan_file in active_plans:
        issue_num = extract_issue_number(plan_file)
        if issue_num is None:
            continue

        status = check_issue_status(issue_num)
        if status == "CLOSED":
            should_archive += 1
            should_archive_files.append(plan_file.name)

    # 计算清洁度评分
    # 理想状态：active/ 中只有 0-5 个文件，且都是活跃 issue
    # 评分算法：
    # - 如果有应归档的计划：扣分
    # - 如果文件总数过多（>10）：扣分

    score = 100

    # 扣分：应归档的计划
    if should_archive > 0:
        # 每个应归档的计划扣 5 分
        score -= min(should_archive * 5, 30)

    # 扣分：文件总数过多
    optimal_count = 5
    if active_count > optimal_count:
        excess = active_count - optimal_count
        # 每超出 1 个文件扣 3 分
        score -= min(excess * 3, 20)

    score = max(score, 0)  # 最低 0 分

    # 生成问题和建议
    issues = []
    recommendations = []

    if should_archive > 0:
        issues.append(f"{should_archive} completed plans should be archived")
        recommendations.append(f"Run /maintain-project --component plans (archives {should_archive})")

    if active_count > optimal_count:
        issues.append(f"active/ directory: {active_count} files (optimal: {optimal_count})")

    return HealthScore(
        score=score,
        issues=issues,
        recommendations=recommendations
    )


def calculate_overall_health() -> Dict:
    """
    计算整体健康评分。

    Returns:
        健康评分字典
    """
    # 计算各组件健康评分
    claude_md_health = check_claude_md_health()
    plans_health = check_plans_cleanliness()

    # 加权平均（Phase 1: 仅 2 个组件）
    overall_score = int(
        claude_md_health.score * 0.5 +
        plans_health.score * 0.5
    )

    return {
        "overall": overall_score,
        "components": {
            "claude_md": claude_md_health,
            "plans": plans_health
        }
    }


def print_health_report(health: Dict, verbose: bool = False):
    """
    打印健康报告。

    Args:
        health: 健康评分字典
        verbose: 是否显示详细信息
    """
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Project Health Report")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    # 整体评分
    overall = health["overall"]
    status_emoji = get_status_emoji(overall)
    print(f"Overall Health: {overall}/100 {status_emoji}\n")

    # 组件健康
    print("Component Health:")

    # CLAUDE.md
    claude_md = health["components"]["claude_md"]
    claude_md_emoji = get_status_emoji(claude_md.score)
    print(f"- CLAUDE.md: {claude_md.score}/100 {claude_md_emoji}")
    for issue in claude_md.issues:
        print(f"  - {issue}")
    if not claude_md.issues:
        print("  - All skills documented")
        print("  - Versions up to date")
    print()

    # plans/
    plans = health["components"]["plans"]
    plans_emoji = get_status_emoji(plans.score)
    print(f"- plans/: {plans.score}/100 {plans_emoji}")
    for issue in plans.issues:
        print(f"  - {issue}")
    if not plans.issues:
        active_count = count_files(".claude/plans/active")
        print(f"  - active/ directory: {active_count} files (optimal)")
        print("  - 0 plans need archiving")
    print()

    # 改进建议
    all_recommendations = (
        claude_md.recommendations +
        plans.recommendations
    )

    if all_recommendations:
        print("Recommendations:")
        for i, rec in enumerate(all_recommendations, 1):
            print(f"{i}. {rec}")
        print()
    else:
        print("✅ No issues found - project is healthy!\n")


def get_status_emoji(score: int) -> str:
    """根据评分返回状态 emoji"""
    if score >= 90:
        return "✅"
    elif score >= 70:
        return "⚠️"
    else:
        return "❌"


def main():
    """主函数"""
    verbose = "--verbose" in sys.argv

    # 计算健康评分
    health = calculate_overall_health()

    # 打印报告
    print_health_report(health, verbose=verbose)


if __name__ == "__main__":
    main()
