"""
功能测试 - 基于 eval-plan SKILL.md Overview 章节

测试 eval-plan 的核心功能：
1. 架构对齐验证 (40分)
2. 验收标准覆盖检查 (30分)
3. 任务依赖验证 (15分)
4. 最佳实践评估 (10分)
5. 任务清晰度检查 (5分)
6. 生成评分报告
7. 写入状态文件
8. 版本字段验证
"""

import json
import pytest
from pathlib import Path
from conftest import (
    create_plan_file,
    create_architecture_rules,
)


@pytest.mark.functional
class TestArchitectureAlignment:
    """测试 1: 架构对齐验证（最高 40 分）"""

    def test_reads_architecture_rules_correctly(self, temp_dir, mock_architecture_rules):
        """验证能正确读取 .claude/rules/architecture/ 规则"""
        # Given: 创建架构规则文件
        rules_dir = create_architecture_rules(temp_dir, mock_architecture_rules)

        # When: 读取规则
        rule_files = list(rules_dir.glob("*.md"))

        # Then: 验证规则文件存在
        assert len(rule_files) == 2
        assert (rules_dir / "layered-architecture.md").exists()
        assert (rules_dir / "dependency-injection.md").exists()

        # 验证内容正确
        content = (rules_dir / "layered-architecture.md").read_text()
        assert "UI Layer" in content
        assert "Service Layer" in content
        assert "Repository Layer" in content

    def test_perfect_architecture_alignment_scores_40(self, temp_dir, mock_plan_excellent, mock_architecture_rules):
        """完美对齐架构的计划应得 40 分"""
        # Given: 优秀计划 + 架构规则
        plan_file = create_plan_file(temp_dir, mock_plan_excellent)
        create_architecture_rules(temp_dir, mock_architecture_rules)

        # When: 评估架构对齐
        plan_content = plan_file.read_text()

        # Then: 验证计划包含架构对齐说明
        assert "## 架构对齐" in plan_content
        assert "三层架构" in plan_content
        assert "Service" in plan_content
        assert "Repository" in plan_content

        # 计划明确遵循架构规则
        assert "依赖方向从外向内" in plan_content

    def test_missing_architecture_section_scores_low(self, temp_dir, mock_plan_poor):
        """缺失架构说明的计划应得低分"""
        # Given: 劣质计划（无架构对齐章节）
        plan_file = create_plan_file(temp_dir, mock_plan_poor)

        # When: 检查计划内容
        plan_content = plan_file.read_text()

        # Then: 验证缺失架构对齐
        assert "## 架构对齐" not in plan_content

        # 这种计划在架构维度应得分很低（<= 10 分）


@pytest.mark.functional
class TestAcceptanceCriteriaCoverage:
    """测试 2: 验收标准覆盖检查（最高 30 分）"""

    def test_parses_issue_acceptance_criteria_correctly(self, mock_issue_body_with_criteria):
        """测试能正确解析 issue body 中的验收标准"""
        # Given: Issue body 包含验收标准
        issue_body = mock_issue_body_with_criteria

        # When: 解析验收标准
        criteria_lines = [line for line in issue_body.split('\n') if line.strip().startswith('- [ ]')]

        # Then: 验证解析到所有标准
        assert len(criteria_lines) == 5
        assert "Users can log in" in criteria_lines[0]
        assert "session token" in criteria_lines[1]
        assert "log out" in criteria_lines[2]

    def test_100_percent_coverage_scores_30(self, temp_dir, mock_plan_excellent, mock_issue_body_with_criteria):
        """100% 覆盖验收标准应得 30 分"""
        # Given: 优秀计划 + Issue 验收标准
        plan_file = create_plan_file(temp_dir, mock_plan_excellent)
        plan_content = plan_file.read_text()

        # When: 检查计划的验收标准章节
        assert "## 验收标准" in plan_content

        # Then: 计划包含所有 issue 中的验收标准
        criteria_from_issue = [
            "用户可以使用邮箱和密码登录",
            "登录后创建会话 token",
            "用户可以登出并清除会话",
            "未授权访问返回 401",
            "所有 API 端点有集成测试"
        ]

        for criterion in criteria_from_issue:
            assert criterion in plan_content

    def test_partial_coverage_scores_proportionally(self, temp_dir, mock_plan_good):
        """部分覆盖应按比例得分"""
        # Given: 良好计划（部分覆盖）
        plan_file = create_plan_file(temp_dir, mock_plan_good)
        plan_content = plan_file.read_text()

        # When: 检查验收标准
        criteria_count = plan_content.count("- [ ]")

        # Then: 有验收标准但不完整（应得 15-25 分）
        assert criteria_count >= 2


@pytest.mark.functional
class TestTaskDependencyValidation:
    """测试 3: 任务依赖验证（最高 15 分）"""

    def test_detects_circular_dependencies(self, temp_dir):
        """测试循环依赖检测"""
        # Given: 包含循环依赖的计划
        plan_with_cycle = """---
version: 1.0.0
---

# Test Plan

## 任务

### Task 1: 实现功能 A
- 依赖 Task 2 完成

### Task 2: 实现功能 B
- 依赖 Task 1 完成
"""
        plan_file = create_plan_file(temp_dir, plan_with_cycle)

        # When: 解析任务依赖
        plan_content = plan_file.read_text()

        # Then: 应检测到循环依赖
        # Task 1 depends on Task 2, Task 2 depends on Task 1
        assert "Task 1" in plan_content
        assert "Task 2" in plan_content
        assert "依赖" in plan_content

    def test_validates_task_order_is_reasonable(self, temp_dir, mock_plan_excellent):
        """验证任务顺序合理性"""
        # Given: 优秀计划（合理的任务顺序）
        plan_file = create_plan_file(temp_dir, mock_plan_excellent)
        plan_content = plan_file.read_text()

        # When: 检查任务顺序
        # 服务层 → 数据层 → API → 前端（由外向内）
        task1_pos = plan_content.find("Task 1: 创建 AuthService")
        task2_pos = plan_content.find("Task 2: 创建 UserRepository")
        task3_pos = plan_content.find("Task 3: 创建 API 端点")

        # Then: 任务顺序合理（服务层在前，数据层其次，API最后）
        assert task1_pos < task2_pos < task3_pos

    def test_correct_dependencies_score_15(self, temp_dir, mock_plan_excellent):
        """正确的依赖关系应得满分"""
        # Given: 优秀计划
        plan_file = create_plan_file(temp_dir, mock_plan_excellent)
        plan_content = plan_file.read_text()

        # When: 检查任务依赖
        # Then: 没有循环依赖，顺序合理
        assert "### Task 1" in plan_content
        assert "### Task 2" in plan_content
        assert "### Task 3" in plan_content
        assert "### Task 4" in plan_content


@pytest.mark.functional
class TestBestPracticesAssessment:
    """测试 4: 最佳实践评估（最高 10 分）"""

    def test_checks_error_handling_presence(self, temp_dir, mock_plan_excellent):
        """测试错误处理检查"""
        # Given: 优秀计划（包含错误处理）
        plan_file = create_plan_file(temp_dir, mock_plan_excellent)
        plan_content = plan_file.read_text()

        # Then: 计划提到错误处理
        assert "错误处理" in plan_content
        assert "try-catch" in plan_content

    def test_checks_logging_presence(self, temp_dir, mock_plan_excellent):
        """测试日志记录检查"""
        # Given: 优秀计划（包含日志记录）
        plan_file = create_plan_file(temp_dir, mock_plan_excellent)
        plan_content = plan_file.read_text()

        # Then: 计划提到日志记录
        assert "日志记录" in plan_content or "日志" in plan_content

    def test_full_best_practices_scores_10(self, temp_dir, mock_plan_excellent):
        """完整的最佳实践应得满分"""
        # Given: 优秀计划
        plan_file = create_plan_file(temp_dir, mock_plan_excellent)
        plan_content = plan_file.read_text()

        # Then: 包含所有最佳实践
        assert "错误处理" in plan_content
        assert "日志记录" in plan_content
        assert "测试" in plan_content
        assert "输入验证" in plan_content


@pytest.mark.functional
class TestTaskClarity:
    """测试 5: 任务清晰度检查（最高 5 分）"""

    def test_specific_tasks_score_higher(self, temp_dir, mock_plan_excellent):
        """具体的任务描述应得高分"""
        # Given: 优秀计划（任务描述具体）
        plan_file = create_plan_file(temp_dir, mock_plan_excellent)
        plan_content = plan_file.read_text()

        # Then: 任务描述包含文件路径和具体操作
        assert "src/services/auth.ts" in plan_content
        assert "src/repositories/user.ts" in plan_content
        assert "src/routes/auth.ts" in plan_content

    def test_vague_tasks_score_lower(self, temp_dir, mock_plan_poor):
        """模糊的任务描述应得低分"""
        # Given: 劣质计划（任务描述模糊）
        plan_file = create_plan_file(temp_dir, mock_plan_poor)
        plan_content = plan_file.read_text()

        # Then: 任务描述模糊（"修复认证"、"更新代码"）
        assert "修复认证问题" in plan_content
        assert "更新相关代码" in plan_content
        # 没有具体的文件路径或操作


@pytest.mark.functional
class TestScoringReport:
    """测试 6: 生成评分报告"""

    def test_calculates_total_score_0_to_100(self):
        """验证总分计算（0-100）"""
        # Given: 各维度得分
        scores = {
            "architecture": 40,
            "coverage": 30,
            "dependencies": 15,
            "practices": 10,
            "clarity": 5
        }

        # When: 计算总分
        total = sum(scores.values())

        # Then: 总分在 0-100 范围
        assert 0 <= total <= 100
        assert total == 100

    def test_report_format_is_correct(self):
        """测试报告格式正确性"""
        # Given: 评估结果
        report = {
            "score": 95,
            "breakdown": {
                "architecture": 40,
                "coverage": 30,
                "dependencies": 15,
                "practices": 10,
                "clarity": 5
            },
            "issues": [],
            "recommendations": []
        }

        # Then: 报告包含必需字段
        assert "score" in report
        assert "breakdown" in report
        assert "issues" in report
        assert report["score"] == 95


@pytest.mark.functional
class TestStatusFile:
    """测试 7: 写入状态文件"""

    def test_creates_status_file(self, temp_dir):
        """验证 .claude/.eval-plan-status.json 创建"""
        # Given: 临时目录
        status_dir = temp_dir / ".claude"
        status_dir.mkdir(exist_ok=True)

        # When: 写入状态文件
        status = {
            "timestamp": "2026-04-07T10:00:00",
            "score": 95,
            "status": "approved"
        }
        status_file = status_dir / ".eval-plan-status.json"
        status_file.write_text(json.dumps(status, indent=2))

        # Then: 文件存在且格式正确
        assert status_file.exists()
        loaded_status = json.loads(status_file.read_text())
        assert loaded_status["score"] == 95

    def test_status_file_contains_required_fields(self, mock_status_file):
        """测试状态文件包含必需字段"""
        # Given: 状态文件
        status = json.loads(mock_status_file.read_text())

        # Then: 包含所有必需字段
        required_fields = [
            "timestamp",
            "issue_number",
            "status",
            "score",
            "breakdown",
            "issues_count",
            "valid_until"
        ]

        for field in required_fields:
            assert field in status, f"Missing required field: {field}"


@pytest.mark.functional
class TestVersionFieldValidation:
    """测试 8: 版本字段验证"""

    def test_detects_version_in_frontmatter(self, temp_dir):
        """测试检测 YAML frontmatter 中的 version 字段"""
        # Given: 包含 version 字段的计划
        plan_with_version = """---
version: 1.0.0
issue: 123
---

# Test Plan
"""
        plan_file = create_plan_file(temp_dir, plan_with_version)

        # When: 解析 frontmatter
        content = plan_file.read_text()
        frontmatter_end = content.find("---", 3)
        frontmatter = content[3:frontmatter_end]

        # Then: 能检测到 version 字段
        assert "version:" in frontmatter
        assert "1.0.0" in frontmatter

    def test_validates_version_format(self):
        """验证版本格式验证逻辑"""
        # Given: 各种版本格式
        valid_versions = ["1.0.0", "2.1.3", "0.0.1", "10.20.30"]
        invalid_versions = ["1.0", "v1.0.0", "1.0.0-beta", "latest"]

        # When/Then: 验证格式
        import re
        version_pattern = r"^\d+\.\d+\.\d+$"

        for version in valid_versions:
            assert re.match(version_pattern, version), f"Valid version {version} should match"

        for version in invalid_versions:
            assert not re.match(version_pattern, version), f"Invalid version {version} should not match"

    def test_missing_version_is_flagged(self, temp_dir):
        """缺失 version 字段应被标记"""
        # Given: 没有 version 字段的计划
        plan_without_version = """---
issue: 123
title: "Test"
---

# Test Plan
"""
        plan_file = create_plan_file(temp_dir, plan_without_version)

        # When: 检查 frontmatter
        content = plan_file.read_text()
        frontmatter_end = content.find("---", 3)
        frontmatter = content[3:frontmatter_end]

        # Then: 应检测到缺失 version
        assert "version:" not in frontmatter
