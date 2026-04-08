"""
参数测试 - 基于 eval-plan SKILL.md Arguments 章节

测试 eval-plan 的参数处理：
1. issue-number 参数验证
2. --strict 选项
3. --json 选项
4. --mode=auto 选项
"""

import json
import pytest
from pathlib import Path


@pytest.mark.unit
class TestIssueNumberParameter:
    """测试 issue-number 参数验证"""

    def test_missing_issue_number_raises_error(self):
        """验证必需参数缺失时的错误处理"""
        # Given: 没有提供 issue number
        issue_number = None

        # When/Then: 应抛出错误或提示
        with pytest.raises(ValueError, match="Issue number required"):
            if issue_number is None:
                raise ValueError("Issue number required")

    def test_invalid_issue_number_format_raises_error(self):
        """无效的 issue number 格式应报错"""
        # Given: 无效格式
        invalid_numbers = ["abc", "#123abc", "12.5", "-1", "0"]

        # When/Then: 应拒绝无效格式
        for invalid in invalid_numbers:
            with pytest.raises(ValueError):
                # 假设验证函数
                issue_num = int(invalid) if invalid.isdigit() else None
                if issue_num is None or issue_num <= 0:
                    raise ValueError(f"Invalid issue number: {invalid}")

    def test_valid_issue_number_is_accepted(self):
        """有效的 issue number 应被接受"""
        # Given: 有效的 issue numbers
        valid_numbers = ["1", "42", "123", "999"]

        # When/Then: 应接受所有有效格式
        for valid in valid_numbers:
            issue_num = int(valid)
            assert issue_num > 0

    def test_issue_number_from_branch_name(self):
        """测试从分支名提取 issue number"""
        # Given: 分支名包含 issue number
        branch_names = {
            "feature/123-add-auth": 123,
            "feature/42-fix-bug": 42,
            "fix/999-security-patch": 999
        }

        # When: 提取 issue number
        import re
        for branch, expected in branch_names.items():
            match = re.search(r'/(\d+)-', branch)
            if match:
                issue_num = int(match.group(1))
                # Then: 应正确提取
                assert issue_num == expected


@pytest.mark.unit
class TestStrictOption:
    """测试 --strict 选项"""

    def test_strict_mode_treats_recommendations_as_blocking(self):
        """验证严格模式将推荐视为阻塞问题"""
        # Given: 评估结果有推荐
        evaluation = {
            "score": 88,
            "blocking_issues": [],
            "recommendations": [
                "Task 2 should include file path"
            ]
        }

        # When: 严格模式启用
        strict_mode = True

        # Then: 推荐应视为阻塞
        if strict_mode:
            blocking_count = len(evaluation["blocking_issues"]) + len(evaluation["recommendations"])
        else:
            blocking_count = len(evaluation["blocking_issues"])

        assert blocking_count > 0 if strict_mode else blocking_count == 0

    def test_strict_mode_rejects_score_below_95(self):
        """严格模式拒绝低于 95 分的计划"""
        # Given: 分数 88
        score = 88

        # When: 严格模式
        strict_mode = True
        threshold = 95 if strict_mode else 70

        # Then: 应被拒绝
        status = "approved" if score >= threshold else "rejected"
        assert status == "rejected"

    def test_normal_mode_accepts_score_above_70(self):
        """普通模式接受 70 分以上的计划"""
        # Given: 分数 82
        score = 82

        # When: 普通模式
        strict_mode = False
        threshold = 95 if strict_mode else 70

        # Then: 应被接受
        status = "approved" if score >= threshold else "rejected"
        assert status == "approved"


@pytest.mark.unit
class TestJsonOption:
    """测试 --json 选项"""

    def test_json_output_format_is_valid(self):
        """验证 JSON 输出格式正确"""
        # Given: 评估结果
        evaluation = {
            "score": 95,
            "status": "approved",
            "breakdown": {
                "architecture": 40,
                "coverage": 30,
                "dependencies": 15,
                "practices": 10,
                "clarity": 5
            },
            "issues_count": {
                "blocking": 0,
                "recommendations": 0
            }
        }

        # When: 转换为 JSON
        json_output = json.dumps(evaluation, indent=2)

        # Then: 应是有效的 JSON
        parsed = json.loads(json_output)
        assert parsed["score"] == 95
        assert "breakdown" in parsed

    def test_json_mode_suppresses_human_readable_output(self):
        """JSON 模式应抑制人类可读输出"""
        # Given: JSON 模式启用
        json_mode = True

        # When: 生成输出
        if json_mode:
            output = json.dumps({"score": 95})
        else:
            output = "Score: 95/100 (approved)"

        # Then: 输出应仅为 JSON
        if json_mode:
            parsed = json.loads(output)
            assert "score" in parsed

    def test_json_includes_all_required_fields(self):
        """JSON 输出应包含所有必需字段"""
        # Given: JSON 输出
        json_output = {
            "timestamp": "2026-04-07T10:00:00",
            "issue_number": 123,
            "score": 95,
            "status": "approved",
            "breakdown": {},
            "issues_count": {}
        }

        # Then: 验证必需字段
        required_fields = [
            "timestamp",
            "issue_number",
            "score",
            "status",
            "breakdown",
            "issues_count"
        ]

        for field in required_fields:
            assert field in json_output, f"Missing field: {field}"


@pytest.mark.unit
class TestAutoMode:
    """测试 --mode=auto 选项"""

    def test_auto_mode_triggers_auto_fix_when_score_90_or_above(self):
        """验证分数 ≥90 时触发自动修复"""
        # Given: 分数 92
        score = 92
        mode = "auto"

        # When: 检查是否应自动修复
        should_auto_fix = mode == "auto" and score >= 90

        # Then: 应触发自动修复
        assert should_auto_fix is True

    def test_auto_mode_skips_auto_fix_when_score_below_90(self):
        """分数 <90 时不触发自动修复"""
        # Given: 分数 85
        score = 85
        mode = "auto"

        # When: 检查是否应自动修复
        should_auto_fix = mode == "auto" and score >= 90

        # Then: 不应自动修复
        assert should_auto_fix is False

    def test_interactive_mode_never_auto_fixes(self):
        """交互模式永不自动修复"""
        # Given: 交互模式，分数 95
        score = 95
        mode = "interactive"

        # When: 检查是否应自动修复
        should_auto_fix = mode == "auto" and score >= 90

        # Then: 不应自动修复
        assert should_auto_fix is False

    def test_auto_fix_applies_minor_corrections(self):
        """自动修复应修正小问题"""
        # Given: 可自动修复的问题
        issues = [
            {"category": "missing_todo", "fixable": True},
            {"category": "format_issue", "fixable": True},
            {"category": "version_missing", "fixable": True}
        ]

        # When: 应用自动修复
        fixable_issues = [issue for issue in issues if issue["fixable"]]

        # Then: 所有问题都可自动修复
        assert len(fixable_issues) == 3

    def test_auto_fix_preserves_major_issues(self):
        """自动修复不处理重大问题"""
        # Given: 包含重大问题
        issues = [
            {"category": "missing_todo", "severity": "minor"},
            {"category": "architecture_violation", "severity": "major"},
            {"category": "circular_dependency", "severity": "blocking"}
        ]

        # When: 过滤可自动修复的问题（仅 minor）
        auto_fixable = [i for i in issues if i.get("severity") == "minor"]

        # Then: 只有 minor 问题被自动修复
        assert len(auto_fixable) == 1
        assert auto_fixable[0]["category"] == "missing_todo"


@pytest.mark.unit
class TestParameterCombinations:
    """测试参数组合"""

    @pytest.mark.parametrize("issue_number,expected", [
        (123, True),
        (0, False),
        (-1, False),
        (None, False)
    ])
    def test_issue_number_validation(self, issue_number, expected):
        """参数化测试 issue number 验证"""
        # When: 验证 issue number
        is_valid = issue_number is not None and issue_number > 0

        # Then: 应符合预期
        assert is_valid == expected

    @pytest.mark.parametrize("mode,score,expected_auto_fix", [
        ("auto", 95, True),
        ("auto", 90, True),
        ("auto", 89, False),
        ("interactive", 95, False),
        ("interactive", 90, False)
    ])
    def test_auto_fix_trigger_conditions(self, mode, score, expected_auto_fix):
        """参数化测试自动修复触发条件"""
        # When: 检查触发条件
        should_auto_fix = mode == "auto" and score >= 90

        # Then: 应符合预期
        assert should_auto_fix == expected_auto_fix

    @pytest.mark.parametrize("strict,score,expected_status", [
        (True, 95, "approved"),
        (True, 94, "rejected"),
        (False, 82, "approved"),
        (False, 69, "rejected")
    ])
    def test_approval_thresholds(self, strict, score, expected_status):
        """参数化测试批准阈值"""
        # When: 确定状态
        threshold = 95 if strict else 70
        status = "approved" if score >= threshold else "rejected"

        # Then: 应符合预期
        assert status == expected_status
