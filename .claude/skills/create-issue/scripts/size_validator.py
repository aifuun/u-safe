#!/usr/bin/env python3
"""
size_validator: Issue 尺寸验证模块

提供智能的 issue 尺寸分析和建议功能。
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


class SizeRecommendation(Enum):
    """尺寸建议枚举"""
    PASS = "PASS"      # 尺寸理想，可直接创建
    WARN = "WARN"      # 尺寸偏大，建议拆分
    BLOCK = "BLOCK"    # 尺寸过大，必须拆分


@dataclass
class SizeResult:
    """尺寸验证结果"""
    # 任务数量
    tasks_count: int

    # 估算时间（小时）
    estimated_hours: float

    # 估算代码行数
    estimated_lines: int

    # 估算影响文件数
    estimated_files: int

    # 建议类型
    recommendation: SizeRecommendation

    # 建议消息
    message: str

    # 拆分建议（如果需要拆分）
    split_suggestions: Optional[List[str]] = None


class SizeValidator:
    """Issue 尺寸验证器"""

    # 尺寸限制配置
    IDEAL_TASKS = (3, 5)
    IDEAL_HOURS = (2, 3)
    IDEAL_LINES = (100, 200)
    IDEAL_FILES = (3, 5)

    RECOMMENDED_TASKS_MAX = 8
    RECOMMENDED_HOURS_MAX = 4
    RECOMMENDED_LINES_MAX = 300
    RECOMMENDED_FILES_MAX = 8

    HARD_TASKS_MAX = 15
    HARD_HOURS_MAX = 8
    HARD_LINES_MAX = 500
    HARD_FILES_MAX = 15

    def validate_size(self, title: str, body: str) -> SizeResult:
        """
        验证 issue 尺寸

        Args:
            title: Issue 标题
            body: Issue 内容

        Returns:
            尺寸验证结果
        """
        # 1. 解析任务数量
        tasks = parse_tasks_from_body(body)
        tasks_count = len(tasks)

        # 2. 估算复杂度
        complexity = estimate_complexity(title, body, tasks)

        # 3. 估算时间、代码量、文件数
        estimated_hours = self._estimate_hours(tasks_count, complexity)
        estimated_lines = self._estimate_lines(tasks_count, complexity)
        estimated_files = self._estimate_files(tasks_count, complexity)

        # 4. 生成建议
        recommendation = self._get_recommendation(
            tasks_count, estimated_hours, estimated_lines, estimated_files
        )

        # 5. 生成消息
        message = self._generate_message(
            tasks_count, estimated_hours, estimated_lines, estimated_files, recommendation
        )

        # 6. 生成拆分建议（如果需要）
        split_suggestions = None
        if recommendation in (SizeRecommendation.WARN, SizeRecommendation.BLOCK):
            split_suggestions = self._generate_split_suggestions(tasks, tasks_count)

        return SizeResult(
            tasks_count=tasks_count,
            estimated_hours=estimated_hours,
            estimated_lines=estimated_lines,
            estimated_files=estimated_files,
            recommendation=recommendation,
            message=message,
            split_suggestions=split_suggestions
        )

    def _estimate_hours(self, tasks_count: int, complexity: float) -> float:
        """
        估算完成时间（小时）

        基础假设:
        - 简单任务: 0.5 小时
        - 中等任务: 1 小时
        - 复杂任务: 2 小时

        Args:
            tasks_count: 任务数量
            complexity: 复杂度系数（0.5-2.0）

        Returns:
            估算小时数
        """
        base_hours_per_task = 1.0
        return tasks_count * base_hours_per_task * complexity

    def _estimate_lines(self, tasks_count: int, complexity: float) -> int:
        """
        估算代码行数

        基础假设:
        - 简单任务: 30 行
        - 中等任务: 50 行
        - 复杂任务: 100 行

        Args:
            tasks_count: 任务数量
            complexity: 复杂度系数

        Returns:
            估算行数
        """
        base_lines_per_task = 50
        return int(tasks_count * base_lines_per_task * complexity)

    def _estimate_files(self, tasks_count: int, complexity: float) -> int:
        """
        估算影响文件数

        基础假设:
        - 简单任务: 1 个文件
        - 中等任务: 1-2 个文件
        - 复杂任务: 2-3 个文件

        Args:
            tasks_count: 任务数量
            complexity: 复杂度系数

        Returns:
            估算文件数
        """
        base_files_per_task = 1.2
        return max(1, int(tasks_count * base_files_per_task * complexity))

    def _get_recommendation(
        self,
        tasks_count: int,
        hours: float,
        lines: int,
        files: int
    ) -> SizeRecommendation:
        """
        生成尺寸建议

        优先级:
        1. 硬限制（任何一项超过硬限制 → BLOCK）
        2. 推荐限制（任何一项超过推荐限制 → WARN）
        3. 理想范围（所有指标都在理想范围 → PASS）

        Args:
            tasks_count: 任务数量
            hours: 估算时间
            lines: 估算代码行数
            files: 估算文件数

        Returns:
            建议类型
        """
        # 检查硬限制
        if (tasks_count > self.HARD_TASKS_MAX or
            hours > self.HARD_HOURS_MAX or
            lines > self.HARD_LINES_MAX or
            files > self.HARD_FILES_MAX):
            return SizeRecommendation.BLOCK

        # 检查推荐限制
        if (tasks_count > self.RECOMMENDED_TASKS_MAX or
            hours > self.RECOMMENDED_HOURS_MAX or
            lines > self.RECOMMENDED_LINES_MAX or
            files > self.RECOMMENDED_FILES_MAX):
            return SizeRecommendation.WARN

        # 理想范围
        return SizeRecommendation.PASS

    def _generate_message(
        self,
        tasks_count: int,
        hours: float,
        lines: int,
        files: int,
        recommendation: SizeRecommendation
    ) -> str:
        """生成建议消息"""
        if recommendation == SizeRecommendation.PASS:
            return (
                f"尺寸理想（{tasks_count} 任务，{hours:.1f} 小时，"
                f"~{lines} 行代码，~{files} 个文件）"
            )

        elif recommendation == SizeRecommendation.WARN:
            exceeded = []
            if tasks_count > self.RECOMMENDED_TASKS_MAX:
                exceeded.append(f"任务数 {tasks_count}（推荐 ≤{self.RECOMMENDED_TASKS_MAX}）")
            if hours > self.RECOMMENDED_HOURS_MAX:
                exceeded.append(f"时间 {hours:.1f}h（推荐 ≤{self.RECOMMENDED_HOURS_MAX}h）")
            if lines > self.RECOMMENDED_LINES_MAX:
                exceeded.append(f"代码量 ~{lines} 行（推荐 ≤{self.RECOMMENDED_LINES_MAX}）")
            if files > self.RECOMMENDED_FILES_MAX:
                exceeded.append(f"文件数 ~{files}（推荐 ≤{self.RECOMMENDED_FILES_MAX}）")

            return f"尺寸偏大，建议拆分: {', '.join(exceeded)}"

        else:  # BLOCK
            exceeded = []
            if tasks_count > self.HARD_TASKS_MAX:
                exceeded.append(f"任务数 {tasks_count}（硬限制 ≤{self.HARD_TASKS_MAX}）")
            if hours > self.HARD_HOURS_MAX:
                exceeded.append(f"时间 {hours:.1f}h（硬限制 ≤{self.HARD_HOURS_MAX}h）")
            if lines > self.HARD_LINES_MAX:
                exceeded.append(f"代码量 ~{lines} 行（硬限制 ≤{self.HARD_LINES_MAX}）")
            if files > self.HARD_FILES_MAX:
                exceeded.append(f"文件数 ~{files}（硬限制 ≤{self.HARD_FILES_MAX}）")

            return f"尺寸过大，必须拆分: {', '.join(exceeded)}"

    def _generate_split_suggestions(
        self,
        tasks: List[str],
        tasks_count: int
    ) -> List[str]:
        """
        生成拆分建议

        策略:
        - 如果 6-8 个任务 → 拆分为 2 个 issues
        - 如果 9-12 个任务 → 拆分为 3 个 issues
        - 如果 >12 个任务 → 拆分为 4+ issues

        Args:
            tasks: 任务列表
            tasks_count: 任务数量

        Returns:
            拆分建议列表
        """
        if tasks_count <= self.RECOMMENDED_TASKS_MAX:
            # 不需要拆分
            return []

        # 确定拆分数量
        if tasks_count <= 8:
            num_issues = 2
        elif tasks_count <= 12:
            num_issues = 3
        else:
            num_issues = 4

        # 平均分配任务
        tasks_per_issue = tasks_count // num_issues
        remainder = tasks_count % num_issues

        suggestions = []
        start = 0

        for i in range(num_issues):
            # 前 remainder 个 issue 多分配一个任务
            count = tasks_per_issue + (1 if i < remainder else 0)
            end = start + count

            issue_tasks = tasks[start:end]
            suggestions.append(
                f"Issue {i+1}: {count} 个任务 ({', '.join(issue_tasks[:2])}...)"
            )

            start = end

        return suggestions


def parse_tasks_from_body(body: str) -> List[str]:
    """
    从 issue body 中解析任务列表

    支持的格式:
    - [ ] Task description
    - [x] Task description
    - 1. Task description
    - * Task description
    - - Task description

    Args:
        body: Issue 内容

    Returns:
        任务列表
    """
    tasks = []

    # 正则匹配任务行
    # 匹配: - [ ] / - [x] / 1. / * / - 开头的行
    task_patterns = [
        r'^[-*]\s*\[[ xX]\]\s+(.+)$',  # - [ ] / - [x]
        r'^\d+\.\s+(.+)$',              # 1.
        r'^[-*]\s+(.+)$',               # - / *
    ]

    for line in body.split('\n'):
        line = line.strip()
        for pattern in task_patterns:
            match = re.match(pattern, line)
            if match:
                task_text = match.group(1).strip()
                # 过滤空任务和过短的任务
                if len(task_text) > 5:
                    tasks.append(task_text)
                break

    return tasks


def estimate_complexity(title: str, body: str, tasks: List[str]) -> float:
    """
    估算 issue 复杂度系数（0.5-2.0）

    考虑因素:
    1. 关键词权重（refactor, architecture, system 等增加复杂度）
    2. 任务描述长度（更长的描述通常更复杂）
    3. 技术栈提及（多技术栈增加复杂度）

    Args:
        title: Issue 标题
        body: Issue 内容
        tasks: 任务列表

    Returns:
        复杂度系数
    """
    complexity = 1.0  # 基础复杂度

    # 1. 关键词分析
    high_complexity_keywords = [
        'refactor', 'architecture', 'system', 'migration', 'redesign',
        'optimization', 'performance', 'security', 'authentication',
        'infrastructure', 'deployment', 'ci/cd', 'testing framework'
    ]

    low_complexity_keywords = [
        'fix', 'typo', 'update', 'docs', 'comment', 'format',
        'style', 'lint', 'minor', 'simple'
    ]

    combined_text = (title + ' ' + body).lower()

    # 高复杂度关键词每个 +0.2
    for keyword in high_complexity_keywords:
        if keyword in combined_text:
            complexity += 0.2

    # 低复杂度关键词每个 -0.1
    for keyword in low_complexity_keywords:
        if keyword in combined_text:
            complexity -= 0.1

    # 2. 任务描述长度分析
    if tasks:
        avg_task_length = sum(len(task) for task in tasks) / len(tasks)
        if avg_task_length > 100:
            complexity += 0.3
        elif avg_task_length < 30:
            complexity -= 0.2

    # 3. 技术栈复杂度
    tech_stacks = [
        'react', 'vue', 'angular', 'node', 'python', 'rust', 'go',
        'aws', 'docker', 'kubernetes', 'database', 'api', 'graphql'
    ]

    tech_count = sum(1 for tech in tech_stacks if tech in combined_text)
    if tech_count > 3:
        complexity += 0.3
    elif tech_count > 1:
        complexity += 0.1

    # 限制范围 [0.5, 2.0]
    complexity = max(0.5, min(2.0, complexity))

    return complexity


# 测试函数
def test_size_validator():
    """测试尺寸验证功能"""
    validator = SizeValidator()

    # 测试用例 1: 理想尺寸
    title1 = "Add login component"
    body1 = """
    ## Tasks
    1. Create Login component
    2. Add form validation
    3. Integrate with API
    4. Add error handling
    """

    result1 = validator.validate_size(title1, body1)
    print(f"测试 1: {result1.recommendation.name}")
    print(f"  {result1.message}")
    assert result1.recommendation == SizeRecommendation.PASS

    # 测试用例 2: 需要警告
    title2 = "Add user profile features"
    body2 = """
    ## Tasks
    1. Create user profile component
    2. Add profile edit form
    3. Implement avatar upload
    4. Add profile validation
    5. Create profile API endpoints
    6. Add unit tests
    7. Update documentation
    """

    result2 = validator.validate_size(title2, body2)
    print(f"\n测试 2: {result2.recommendation.name}")
    print(f"  {result2.message}")
    assert result2.recommendation == SizeRecommendation.WARN

    # 测试用例 3: 应该阻止
    title3 = "Complete system refactoring"
    body3 = """
    ## Tasks
    """ + '\n'.join([f"{i}. Task {i}" for i in range(1, 17)])

    result3 = validator.validate_size(title3, body3)
    print(f"\n测试 3: {result3.recommendation.name}")
    print(f"  {result3.message}")
    print(f"  拆分建议: {result3.split_suggestions}")
    assert result3.recommendation == SizeRecommendation.BLOCK

    print("\n✅ 所有测试通过!")


if __name__ == "__main__":
    test_size_validator()
