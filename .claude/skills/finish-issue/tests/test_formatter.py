"""Unit tests for formatter.py - human-friendly summary generation.

Tests extraction functions, format output, and graceful degradation.
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from formatter import HumanReadableSummary


class TestExtractWhySection:
    """Test _extract_why_section() - extracts background from issue body."""

    def test_extract_from_background_section(self):
        """Should extract content from ## 背景 section."""
        issue_body = """
## 背景

当前 finish-issue 输出格式不够标准化。
用户更关心业务价值，而不是技术细节。

## 目标

创建标准化输出格式。
"""
        result = HumanReadableSummary._extract_why_section(issue_body)

        assert "当前 finish-issue 输出格式不够标准化" in result
        assert "用户更关心业务价值" in result
        assert "## 目标" not in result  # Should stop at next section

    def test_extract_from_problem_section(self):
        """Should extract content from ## 问题 section."""
        issue_body = """
## 问题

Login button is misaligned on mobile devices.
This causes poor UX on small screens.

## Solution

Fix CSS alignment.
"""
        result = HumanReadableSummary._extract_why_section(issue_body)

        assert "Login button is misaligned" in result
        assert "poor UX" in result
        assert "## Solution" not in result

    def test_extract_from_background_english(self):
        """Should extract content from ## Background section."""
        issue_body = """
## Background

Current implementation lacks proper error handling.

## Proposal

Add try-catch blocks.
"""
        result = HumanReadableSummary._extract_why_section(issue_body)

        assert "Current implementation lacks" in result
        assert "Add try-catch" not in result

    def test_fallback_to_first_paragraph(self):
        """Should fall back to first paragraph if no ## 背景 found."""
        issue_body = """This is the first paragraph describing the problem.

This is the second paragraph with more details.

## Some Section

Content here.
"""
        result = HumanReadableSummary._extract_why_section(issue_body)

        assert "This is the first paragraph" in result
        assert "second paragraph" not in result  # Should only take first

    def test_truncate_long_content(self):
        """Should truncate content longer than 500 characters."""
        issue_body = "## 背景\n\n" + "A" * 600

        result = HumanReadableSummary._extract_why_section(issue_body)

        assert len(result) <= 500


class TestExtractWhatChanges:
    """Test _extract_what_changes() - extracts main changes from plan/commits."""

    def test_extract_from_part_structure(self):
        """Should extract changes from ### Part N: structure."""
        plan_content = """
### Part 1: Commit 消息增强

- Auto-commit 添加文件列表
- Merge 添加分支名和 commit 数量
- Conflict 添加冲突文件列表

### Part 2: 文档简化

- SKILL.md 精简到 275 行
- 新建 CONFLICT-HANDLING.md
"""
        commits = ""

        result = HumanReadableSummary._extract_what_changes(plan_content, commits)

        assert len(result) > 0
        assert any("Part 1" in item for item in result)
        assert any("Part 2" in item for item in result)

    def test_extract_from_commits_fallback(self):
        """Should fall back to commits if plan has no Part structure."""
        plan_content = None
        commits = """
abc123 feat: add user authentication
def456 fix: resolve login bug
ghi789 docs: update README
"""
        result = HumanReadableSummary._extract_what_changes(plan_content, commits)

        assert len(result) > 0
        assert any("user authentication" in item for item in result)
        assert any("login bug" in item for item in result)

    def test_limit_to_five_changes(self):
        """Should return maximum 5 changes."""
        plan_content = None
        commits = "\n".join([f"abc{i} feat: feature {i}" for i in range(10)])

        result = HumanReadableSummary._extract_what_changes(plan_content, commits)

        assert len(result) <= 5


class TestExtractAchievements:
    """Test _extract_achievements() - extracts completed acceptance criteria."""

    def test_extract_from_plan_acceptance_criteria(self):
        """Should extract completed items from ## 验收标准 in plan."""
        plan_content = """
## 验收标准

- [x] 输出包含 4 个标准部分
- [x] 技术指标压缩到 1 行显示
- [ ] 从 issue body 成功提取背景信息
- ✅ 从 plan 成功提取主要改动
"""
        issue_body = ""

        result = HumanReadableSummary._extract_achievements(plan_content, issue_body)

        assert len(result) == 3  # 2 [x] + 1 ✅
        assert any("输出包含 4 个标准部分" in item for item in result)
        assert any("技术指标压缩" in item for item in result)

    def test_extract_from_issue_body_fallback(self):
        """Should fall back to issue body if plan has no 验收标准."""
        plan_content = None
        issue_body = """
## 验收标准

- [ ] Feature works as expected
- [ ] Tests pass
- [ ] Documentation updated
"""
        result = HumanReadableSummary._extract_achievements(plan_content, issue_body)

        assert len(result) == 3
        assert any("Feature works" in item for item in result)

    def test_limit_to_five_achievements(self):
        """Should return maximum 5 achievements."""
        plan_content = """
## 验收标准

""" + "\n".join([f"- [x] Achievement {i}" for i in range(10)])
        issue_body = ""

        result = HumanReadableSummary._extract_achievements(plan_content, issue_body)

        assert len(result) <= 5


class TestExtractNotes:
    """Test _extract_notes() - extracts warnings/recommendations."""

    def test_extract_from_review_data(self):
        """Should extract warnings from review data."""
        review_data = {
            'issues': [
                {'severity': 'warning', 'message': 'Missing error handling'},
                {'severity': 'error', 'message': 'Security vulnerability'},
                {'severity': 'info', 'message': 'Consider optimization'}
            ]
        }
        plan_content = None

        result = HumanReadableSummary._extract_notes(review_data, plan_content)

        assert len(result) == 2  # Only warning + error
        assert 'Missing error handling' in result
        assert 'Security vulnerability' in result
        assert 'Consider optimization' not in result  # Info ignored

    def test_extract_from_plan_technical_points(self):
        """Should extract notes from ## 技术要点 in plan."""
        review_data = None
        plan_content = """
## 技术要点

- 新的 commit 格式需要 bash 变量捕获
- 如果生成失败，会降级到简单格式
- 确保 shell 环境支持
"""
        result = HumanReadableSummary._extract_notes(review_data, plan_content)

        assert len(result) > 0
        assert any("bash 变量捕获" in item for item in result)

    def test_combine_review_and_plan_notes(self):
        """Should combine notes from both sources."""
        review_data = {
            'issues': [
                {'severity': 'warning', 'message': 'Review warning'}
            ]
        }
        plan_content = """
## 注意事项

- Plan note here
"""
        result = HumanReadableSummary._extract_notes(review_data, plan_content)

        assert 'Review warning' in result
        assert any("Plan note" in item for item in result)

    def test_deduplicate_notes(self):
        """Should remove duplicate notes."""
        review_data = {
            'issues': [
                {'severity': 'warning', 'message': 'Same warning'},
                {'severity': 'error', 'message': 'Same warning'}
            ]
        }
        plan_content = None

        result = HumanReadableSummary._extract_notes(review_data, plan_content)

        assert result.count('Same warning') == 1  # Deduplicated


class TestFormatOutput:
    """Test format_output() - generates final markdown."""

    def test_format_output_structure(self):
        """Should generate output with all 4 sections."""
        summary = HumanReadableSummary(
            issue_number=560,
            issue_title="Test feature",
            why_reason="因为需要改进输出格式",
            what_changes=["改进 A", "优化 B"],
            achievements=["功能 X 实现", "测试通过"],
            notes=["注意 Y"],
            review_score=92,
            commits_count=3,
            files_changed=5,
            lines_summary="(+100/-50)",
            duration="2小时",
            issue_url="https://github.com/aifuun/ai-dev/issues/560",
            pr_number=561
        )

        output = summary.format_output()

        # Check all 4 sections present
        assert "## 💡 实现原因" in output
        assert "## ✨ 主要改动" in output
        assert "## 🎯 实现功能" in output
        assert "## ⚠️ 注意事项" in output

        # Check content
        assert "因为需要改进输出格式" in output
        assert "改进 A" in output
        assert "功能 X 实现" in output
        assert "注意 Y" in output

        # Check metrics line
        assert "📊 质量：92/100" in output
        assert "3 commits" in output
        assert "5 files" in output

    def test_format_output_empty_notes(self):
        """Should show '无特殊注意事项' when notes are empty."""
        summary = HumanReadableSummary(
            issue_number=560,
            issue_title="Test",
            why_reason="Test reason",
            what_changes=["Change 1"],
            achievements=["Achievement 1"],
            notes=[],  # Empty
            review_score=90,
            commits_count=1,
            files_changed=1,
            lines_summary="(+10)",
            duration="1小时",
            issue_url="https://github.com/example/issues/1",
            pr_number=2
        )

        output = summary.format_output()

        assert "无特殊注意事项" in output


class TestFromIssueData:
    """Test from_issue_data() - constructs summary from raw data."""

    def test_from_issue_data_complete(self):
        """Should construct summary from complete data."""
        issue_body = """
## 背景

当前输出格式不够友好。

## 目标

改进输出。
"""
        plan_content = """
### Part 1: 实现功能

- 创建 formatter.py
- 添加测试

## 验收标准

- [x] 输出标准化
- [x] 测试通过
"""
        commits = "abc123 feat: add formatter"

        summary = HumanReadableSummary.from_issue_data(
            issue_number=560,
            issue_title="改进输出格式",
            issue_body=issue_body,
            commits=commits,
            plan_content=plan_content,
            review_data={'score': 95},
            files_changed=3,
            lines_summary="(+200/-50)",
            duration="3小时",
            issue_url="https://github.com/example/issues/560",
            pr_number=561
        )

        assert summary.issue_number == 560
        assert summary.review_score == 95
        assert len(summary.why_reason) > 0
        assert len(summary.what_changes) > 0
        assert len(summary.achievements) > 0

    def test_from_issue_data_graceful_degradation(self):
        """Should handle missing optional data gracefully."""
        summary = HumanReadableSummary.from_issue_data(
            issue_number=560,
            issue_title="Test",
            issue_body="Simple description",
            commits="",
            plan_content=None,  # Missing
            review_data=None,  # Missing
            files_changed=0,
            lines_summary="",
            duration="未知",
            issue_url="https://github.com/example/issues/560",
            pr_number=0
        )

        # Should not crash, use defaults
        assert summary.review_score == 0
        assert len(summary.why_reason) > 0  # Falls back to issue_body
        assert summary.commits_count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
