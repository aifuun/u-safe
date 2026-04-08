"""人类友好的 issue 完成总结格式化器

提供标准化、易读的输出格式，突出业务价值而非技术细节。
"""

from dataclasses import dataclass
from typing import List, Optional
import re


@dataclass
class HumanReadableSummary:
    """人类友好的完成总结

    将技术性的 issue 完成信息转换为人类可读的业务总结。
    """

    # 业务信息
    issue_number: int
    issue_title: str
    why_reason: str  # 从 issue body 提取背景
    what_changes: List[str]  # 从 commits/plan 提取主要改动
    achievements: List[str]  # 从验收标准提取功能
    notes: List[str]  # 从 review/plan 提取注意事项

    # 快速指标
    review_score: int
    commits_count: int
    files_changed: int
    lines_summary: str
    duration: str
    issue_url: str
    pr_number: int

    def format_output(self) -> str:
        """生成人类友好的输出"""
        return f"""🎉 Issue #{self.issue_number} 完成：{self.issue_title}

## 💡 实现原因

{self.why_reason}

## ✨ 主要改动

{self._format_list(self.what_changes)}

## 🎯 实现功能

{self._format_list(self.achievements)}

## ⚠️ 注意事项

{self._format_list(self.notes) if self.notes else '无特殊注意事项'}

---
📊 质量：{self.review_score}/100 | {self.commits_count} commits | {self.files_changed} files {self.lines_summary}
🔗 Issue #{self.issue_number} | PR #{self.pr_number} | 用时：{self.duration}
"""

    def _format_list(self, items: List[str]) -> str:
        """格式化列表项为 markdown"""
        if not items:
            return ""
        return "\n".join(f"- {item}" for item in items)

    @classmethod
    def from_issue_data(
        cls,
        issue_number: int,
        issue_title: str,
        issue_body: str,
        commits: str,
        plan_content: Optional[str],
        review_data: Optional[dict],
        files_changed: int,
        lines_summary: str,
        duration: str,
        issue_url: str,
        pr_number: int
    ) -> "HumanReadableSummary":
        """从原始数据构建人类友好总结

        Args:
            issue_number: Issue 编号
            issue_title: Issue 标题
            issue_body: Issue 正文（用于提取 why）
            commits: Commit 列表字符串
            plan_content: 实现计划内容（可选）
            review_data: 代码审查数据（可选）
            files_changed: 变更文件数
            lines_summary: 行数摘要（如 "+100/-50"）
            duration: 用时（如 "2小时"）
            issue_url: Issue URL
            pr_number: PR 编号

        Returns:
            HumanReadableSummary 实例
        """
        # 提取 why（实现原因）
        why_reason = cls._extract_why_section(issue_body)

        # 提取 what（主要改动）
        what_changes = cls._extract_what_changes(plan_content, commits)

        # 提取 achievements（实现功能）
        achievements = cls._extract_achievements(plan_content, issue_body)

        # 提取 notes（注意事项）
        notes = cls._extract_notes(review_data, plan_content)

        # 获取 review 分数
        review_score = review_data.get('score', 0) if review_data else 0

        # 计算 commits 数量
        commits_count = len([line for line in commits.strip().split('\n') if line.strip()])

        return cls(
            issue_number=issue_number,
            issue_title=issue_title,
            why_reason=why_reason,
            what_changes=what_changes,
            achievements=achievements,
            notes=notes,
            review_score=review_score,
            commits_count=commits_count,
            files_changed=files_changed,
            lines_summary=lines_summary,
            duration=duration,
            issue_url=issue_url,
            pr_number=pr_number
        )

    @staticmethod
    def _extract_why_section(issue_body: str) -> str:
        """提取背景/问题描述

        优先从 ## 背景、## 问题、## Background 部分提取。
        降级：取 issue body 第一段。
        """
        patterns = [
            r'## 背景\s*\n(.*?)(?=\n##|\Z)',
            r'## 问题\s*\n(.*?)(?=\n##|\Z)',
            r'## Background\s*\n(.*?)(?=\n##|\Z)',
        ]

        for pattern in patterns:
            match = re.search(pattern, issue_body, re.DOTALL)
            if match:
                content = match.group(1).strip()
                # 限制长度，保留核心信息
                return content[:500] if len(content) > 500 else content

        # 降级：取第一段
        first_paragraph = issue_body.split('\n\n')[0] if issue_body else ""
        return first_paragraph[:500] if len(first_paragraph) > 500 else first_paragraph

    @staticmethod
    def _extract_what_changes(plan_content: Optional[str], commits: str) -> List[str]:
        """提取主要改动

        优先从 plan 的 Part 结构提取，降级到 commits。
        最多返回 5 个核心改动。
        """
        changes = []

        if plan_content:
            # 尝试从 Part 结构提取
            part_pattern = r'### (Part \d+:.*?)\n(.*?)(?=\n###|\Z)'
            matches = re.finditer(part_pattern, plan_content, re.DOTALL)

            for match in matches:
                part_title = match.group(1).strip()
                part_content = match.group(2).strip()

                # 提取该 Part 的前 2-3 个要点
                lines = [line.strip() for line in part_content.split('\n') if line.strip().startswith('-')]
                if lines:
                    # 格式化为 "Part X: 要点"
                    part_summary = f"{part_title}: {lines[0].lstrip('- ')}"
                    changes.append(part_summary)

        # 如果从 plan 提取失败或不够，从 commits 提取
        if len(changes) < 3 and commits:
            commit_lines = [line.strip() for line in commits.split('\n') if line.strip()]
            for commit_line in commit_lines[:5]:  # 最多 5 个 commits
                # 提取 commit message（跳过 hash）
                parts = commit_line.split(' ', 1)
                if len(parts) > 1:
                    message = parts[1].strip()
                    if message and message not in changes:
                        changes.append(message)

        # 限制最多 5 个改动
        return changes[:5]

    @staticmethod
    def _extract_achievements(plan_content: Optional[str], issue_body: str) -> List[str]:
        """提取实现功能

        从验收标准提取已完成项。
        最多返回 5 个核心功能。
        """
        achievements = []

        # 尝试从 plan 的验收标准提取
        if plan_content:
            # 匹配 ## 验收标准 部分
            ac_pattern = r'## 验收标准\s*\n(.*?)(?=\n##|\Z)'
            match = re.search(ac_pattern, plan_content, re.DOTALL)

            if match:
                ac_content = match.group(1).strip()
                # 提取已完成的项（- [x] 或 - ✅）
                lines = ac_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('- [x]') or line.startswith('- ✅') or line.startswith('✅'):
                        # 去掉 checkbox，保留描述
                        achievement = re.sub(r'^-\s*\[x\]\s*|^-\s*✅\s*|^✅\s*', '', line).strip()
                        if achievement:
                            achievements.append(achievement)

        # 如果 plan 没有，尝试从 issue body 提取
        if not achievements and issue_body:
            ac_pattern = r'## 验收标准\s*\n(.*?)(?=\n##|\Z)'
            match = re.search(ac_pattern, issue_body, re.DOTALL)

            if match:
                ac_content = match.group(1).strip()
                lines = ac_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('- ['):
                        # 提取所有验收标准（完成或未完成）
                        achievement = re.sub(r'^-\s*\[.\]\s*', '', line).strip()
                        if achievement:
                            achievements.append(achievement)

        # 限制最多 5 个
        return achievements[:5]

    @staticmethod
    def _extract_notes(review_data: Optional[dict], plan_content: Optional[str]) -> List[str]:
        """提取注意事项

        从 review 推荐和 plan 技术要点提取。
        """
        notes = []

        # 从 review 数据提取推荐
        if review_data and 'issues' in review_data:
            for issue in review_data['issues']:
                if issue.get('severity') in ['warning', 'error']:
                    notes.append(issue.get('message', ''))

        # 从 plan 的技术要点提取
        if plan_content:
            # 匹配 ## 技术要点 或 ## 注意事项
            patterns = [
                r'## 技术要点\s*\n(.*?)(?=\n##|\Z)',
                r'## 注意事项\s*\n(.*?)(?=\n##|\Z)',
            ]

            for pattern in patterns:
                match = re.search(pattern, plan_content, re.DOTALL)
                if match:
                    content = match.group(1).strip()
                    lines = [line.strip() for line in content.split('\n') if line.strip().startswith('-')]
                    notes.extend([line.lstrip('- ').strip() for line in lines])

        # 去重并限制最多 5 个
        unique_notes = []
        for note in notes:
            if note and note not in unique_notes:
                unique_notes.append(note)

        return unique_notes[:5]
