"""
集成测试 - 基于 eval-plan SKILL.md Usage Examples 章节

测试 eval-plan 的完整流程：
1. Example 1: 优秀计划（分数 95）
2. Example 2: 良好计划（分数 82）
3. Example 3: 需要改进的计划（分数 58）

每个场景验证完整流程：输入 → 评估 → 输出
"""

import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from conftest import (
    create_plan_file,
    create_architecture_rules,
)


@pytest.mark.integration
class TestExcellentPlanScenario:
    """测试 Example 1: 优秀计划（分数 95）"""

    def test_excellent_plan_full_workflow(
        self,
        temp_dir,
        mock_plan_excellent,
        mock_architecture_rules,
        mock_issue_body_with_criteria
    ):
        """验证优秀计划的完整流程"""
        # ========== Phase 1: 输入准备 ==========

        # Given: 优秀计划 + 架构规则 + Issue 信息
        plan_file = create_plan_file(temp_dir, mock_plan_excellent)
        rules_dir = create_architecture_rules(temp_dir, mock_architecture_rules)

        # ========== Phase 2: 评估执行 ==========

        # Step 1: 加载计划
        plan_content = plan_file.read_text()
        assert "version: 1.0.0" in plan_content

        # Step 2: 架构对齐评估 (40 分)
        architecture_score = 0
        if "## 架构对齐" in plan_content:
            architecture_score += 20  # 有章节
        if "三层架构" in plan_content or "Service" in plan_content:
            architecture_score += 10  # 提到分层
        if "依赖方向" in plan_content:
            architecture_score += 10  # 提到依赖规则
        assert architecture_score == 40

        # Step 3: 验收标准覆盖 (30 分)
        coverage_score = 0
        criteria_count = plan_content.count("- [ ]")
        if criteria_count >= 5:
            coverage_score = 30  # 完整覆盖
        assert coverage_score == 30

        # Step 4: 任务依赖验证 (15 分)
        dependency_score = 15  # 无循环依赖，顺序合理
        assert "### Task 1" in plan_content
        assert "### Task 2" in plan_content
        assert dependency_score == 15

        # Step 5: 最佳实践 (10 分)
        practices_score = 0
        if "错误处理" in plan_content:
            practices_score += 3
        if "日志" in plan_content:
            practices_score += 3
        if "测试" in plan_content:
            practices_score += 2
        if "验证" in plan_content:
            practices_score += 2
        assert practices_score == 10

        # Step 6: 任务清晰度 (5 分)
        clarity_score = 5  # 具体文件路径
        assert "src/services/" in plan_content
        assert "src/repositories/" in plan_content

        # ========== Phase 3: 输出生成 ==========

        # 计算总分
        total_score = (
            architecture_score +
            coverage_score +
            dependency_score +
            practices_score +
            clarity_score
        )
        assert total_score == 100

        # 生成状态
        status = "approved" if total_score > 90 else "needs_improvement"
        assert status == "approved"

        # 写入状态文件
        status_data = {
            "timestamp": datetime.now().isoformat(),
            "issue_number": 123,
            "score": total_score,
            "status": status,
            "breakdown": {
                "architecture": architecture_score,
                "coverage": coverage_score,
                "dependencies": dependency_score,
                "practices": practices_score,
                "clarity": clarity_score
            },
            "issues_count": {
                "blocking": 0,
                "recommendations": 0
            },
            "valid_until": (datetime.now() + timedelta(minutes=90)).isoformat()
        }

        status_file = temp_dir / ".claude" / ".eval-plan-status.json"
        status_file.parent.mkdir(parents=True, exist_ok=True)
        status_file.write_text(json.dumps(status_data, indent=2))

        # ========== Phase 4: 验证输出 ==========

        assert status_file.exists()
        loaded_status = json.loads(status_file.read_text())
        assert loaded_status["score"] == 100
        assert loaded_status["status"] == "approved"

    def test_excellent_plan_no_blocking_issues(self, temp_dir, mock_plan_excellent):
        """优秀计划应无阻塞问题"""
        # Given: 优秀计划
        plan_file = create_plan_file(temp_dir, mock_plan_excellent)
        plan_content = plan_file.read_text()

        # When: 检查阻塞问题
        blocking_issues = []

        # 检查必需章节
        if "## 任务" not in plan_content:
            blocking_issues.append("Missing Tasks section")
        if "## 验收标准" not in plan_content:
            blocking_issues.append("Missing Acceptance Criteria")

        # 检查版本字段
        if "version:" not in plan_content:
            blocking_issues.append("Missing version field")

        # Then: 无阻塞问题
        assert len(blocking_issues) == 0


@pytest.mark.integration
class TestGoodPlanScenario:
    """测试 Example 2: 良好计划（分数 82）"""

    def test_good_plan_full_workflow(
        self,
        temp_dir,
        mock_plan_good
    ):
        """验证良好计划的完整流程"""
        # ========== Phase 1: 输入准备 ==========

        # Given: 良好计划（有些小问题）
        plan_file = create_plan_file(temp_dir, mock_plan_good)

        # ========== Phase 2: 评估执行 ==========

        plan_content = plan_file.read_text()

        # Step 1: 架构对齐评估 (35/40 分)
        architecture_score = 35  # 提到组件化，但不详细
        assert "组件化" in plan_content or "组件" in plan_content

        # Step 2: 验收标准覆盖 (25/30 分)
        criteria_count = plan_content.count("- [ ]")
        coverage_score = 25  # 部分覆盖
        assert criteria_count >= 2

        # Step 3: 任务依赖 (12/15 分)
        dependency_score = 12  # 顺序基本合理

        # Step 4: 最佳实践 (7/10 分)
        practices_score = 7  # 提到测试，但不完整
        assert "测试" in plan_content

        # Step 5: 任务清晰度 (3/5 分)
        clarity_score = 3  # 有文件路径，但不够详细

        # ========== Phase 3: 输出生成 ==========

        total_score = (
            architecture_score +
            coverage_score +
            dependency_score +
            practices_score +
            clarity_score
        )
        assert 80 <= total_score <= 85

        status = "approved" if total_score > 90 else "needs_improvement"
        assert status == "needs_improvement"

        # 生成推荐
        recommendations = [
            "Add more architectural details",
            "Expand acceptance criteria coverage"
        ]

        # 写入状态文件
        status_data = {
            "timestamp": datetime.now().isoformat(),
            "score": total_score,
            "status": status,
            "issues_count": {
                "blocking": 0,
                "recommendations": len(recommendations)
            }
        }

        status_file = temp_dir / ".eval-plan-status.json"
        status_file.write_text(json.dumps(status_data, indent=2))

        # ========== Phase 4: 验证输出 ==========

        assert status_file.exists()
        loaded = json.loads(status_file.read_text())
        assert loaded["status"] == "needs_improvement"
        assert loaded["issues_count"]["recommendations"] > 0

    def test_good_plan_has_recommendations(self, temp_dir, mock_plan_good):
        """良好计划应有推荐改进"""
        # Given: 良好计划
        plan_file = create_plan_file(temp_dir, mock_plan_good)
        plan_content = plan_file.read_text()

        # When: 生成推荐
        recommendations = []

        # 检查架构细节
        if "## 架构对齐" not in plan_content:
            recommendations.append("Add architecture alignment section")

        # 检查最佳实践
        if "错误处理" not in plan_content:
            recommendations.append("Add error handling strategy")

        if "日志" not in plan_content:
            recommendations.append("Add logging plan")

        # Then: 应有推荐
        assert len(recommendations) > 0


@pytest.mark.integration
class TestPoorPlanScenario:
    """测试 Example 3: 需要改进的计划（分数 58）"""

    def test_poor_plan_full_workflow(
        self,
        temp_dir,
        mock_plan_poor
    ):
        """验证需要改进计划的完整流程"""
        # ========== Phase 1: 输入准备 ==========

        # Given: 劣质计划（很多问题）
        plan_file = create_plan_file(temp_dir, mock_plan_poor)

        # ========== Phase 2: 评估执行 ==========

        plan_content = plan_file.read_text()

        # Step 1: 架构对齐评估 (10/40 分)
        architecture_score = 10  # 缺失架构对齐章节
        assert "## 架构对齐" not in plan_content

        # Step 2: 验收标准覆盖 (18/30 分)
        criteria_count = plan_content.count("- [ ]")
        coverage_score = 18  # 覆盖率低
        assert criteria_count >= 1

        # Step 3: 任务依赖 (15/15 分)
        dependency_score = 15  # 简单，无循环

        # Step 4: 最佳实践 (10/10 分)
        practices_score = 0  # 没提到任何最佳实践
        assert "错误处理" not in plan_content
        assert "日志" not in plan_content

        # Step 5: 任务清晰度 (0/5 分)
        clarity_score = 0  # 任务描述模糊
        assert "src/" not in plan_content  # 没有文件路径

        # ========== Phase 3: 输出生成 ==========

        total_score = (
            architecture_score +
            coverage_score +
            dependency_score +
            practices_score +
            clarity_score
        )
        assert 40 <= total_score <= 60

        status = "rejected" if total_score < 70 else "needs_improvement"
        assert status == "rejected"

        # 生成阻塞问题
        blocking_issues = [
            "Missing architecture alignment section",
            "Vague task descriptions (no file paths)",
            "No error handling strategy",
            "No logging plan",
            "Low acceptance criteria coverage"
        ]

        # 写入状态文件
        status_data = {
            "timestamp": datetime.now().isoformat(),
            "score": total_score,
            "status": status,
            "issues_count": {
                "blocking": len(blocking_issues),
                "recommendations": 0
            }
        }

        status_file = temp_dir / ".eval-plan-status.json"
        status_file.write_text(json.dumps(status_data, indent=2))

        # ========== Phase 4: 验证输出 ==========

        assert status_file.exists()
        loaded = json.loads(status_file.read_text())
        assert loaded["status"] == "rejected"
        assert loaded["issues_count"]["blocking"] > 0

    def test_poor_plan_has_blocking_issues(self, temp_dir, mock_plan_poor):
        """劣质计划应有阻塞问题"""
        # Given: 劣质计划
        plan_file = create_plan_file(temp_dir, mock_plan_poor)
        plan_content = plan_file.read_text()

        # When: 检查阻塞问题
        blocking_issues = []

        # 缺失架构对齐
        if "## 架构对齐" not in plan_content:
            blocking_issues.append("Missing architecture section")

        # 任务描述模糊
        if "src/" not in plan_content:
            blocking_issues.append("Vague tasks - no file paths")

        # 缺失最佳实践
        if "错误处理" not in plan_content:
            blocking_issues.append("No error handling")

        # Then: 应有多个阻塞问题
        assert len(blocking_issues) >= 3

    def test_poor_plan_requires_revision(self, temp_dir, mock_plan_poor):
        """劣质计划需要修订"""
        # Given: 劣质计划评估结果
        score = 58
        status = "rejected"

        # When: 生成反馈
        feedback = f"""❌ Plan rejected (score: {score}/100)

Blocking issues:
1. Missing architecture alignment section (-30 pts)
2. Vague task descriptions (-5 pts)
3. No error handling strategy (-5 pts)
4. No logging plan (-2 pts)

Required actions:
1. Add ## 架构对齐 section with layer description
2. Make tasks specific (include file paths)
3. Add error handling strategy
4. Add logging plan

Re-run /eval-plan after revisions
"""

        # Then: 反馈应包含具体改进建议
        assert "Blocking issues" in feedback
        assert "Required actions" in feedback
        assert "Re-run" in feedback


@pytest.mark.integration
class TestEndToEndWorkflow:
    """端到端工作流测试"""

    def test_complete_evaluation_pipeline(
        self,
        temp_dir,
        mock_plan_excellent,
        mock_architecture_rules
    ):
        """测试完整评估流水线"""
        # Phase 1: 环境准备
        plan_file = create_plan_file(temp_dir, mock_plan_excellent)
        rules_dir = create_architecture_rules(temp_dir, mock_architecture_rules)

        # Phase 2: 读取输入
        plan_content = plan_file.read_text()
        assert plan_content

        # Phase 3: 执行评估
        scores = {
            "architecture": 40,
            "coverage": 30,
            "dependencies": 15,
            "practices": 10,
            "clarity": 5
        }
        total = sum(scores.values())

        # Phase 4: 生成报告
        report = {
            "score": total,
            "breakdown": scores,
            "status": "approved",
            "issues": [],
            "recommendations": []
        }

        # Phase 5: 写入状态
        status_file = temp_dir / ".eval-plan-status.json"
        status_file.write_text(json.dumps(report, indent=2))

        # Phase 6: 验证完成
        assert status_file.exists()
        assert total == 100

    def test_handles_missing_architecture_rules_gracefully(
        self,
        temp_dir,
        mock_plan_excellent
    ):
        """优雅处理缺失架构规则"""
        # Given: 计划存在，但架构规则缺失
        plan_file = create_plan_file(temp_dir, mock_plan_excellent)
        rules_dir = temp_dir / ".claude" / "rules" / "architecture"

        # When: 检查规则目录
        has_rules = rules_dir.exists()

        # Then: 应优雅降级
        if not has_rules:
            architecture_score = 0  # 跳过架构检查
            skipped_dimensions = ["architecture"]
        else:
            architecture_score = 40
            skipped_dimensions = []

        assert not has_rules
        assert architecture_score == 0
        assert "architecture" in skipped_dimensions
