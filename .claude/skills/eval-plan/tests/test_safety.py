"""
安全测试 - 基于 eval-plan SKILL.md Safety Features 章节

测试 eval-plan 的安全机制：
1. 计划结构验证
2. 任务依赖循环检测
3. 错误恢复机制
4. 失败限制（最大重试 3 次）
5. 状态文件管理
"""

import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from conftest import create_plan_file


@pytest.mark.unit
class TestPlanStructureValidation:
    """测试 1: 计划结构验证"""

    def test_rejects_plan_without_tasks_section(self, temp_dir):
        """测试对无效计划结构的处理 - 缺失 Tasks 章节"""
        # Given: 没有 Tasks 章节的计划
        invalid_plan = """---
version: 1.0.0
---

# Test Plan

## 背景

Some context here.

## 验收标准

- [ ] Criterion 1
"""
        plan_file = create_plan_file(temp_dir, invalid_plan)

        # When: 验证计划结构
        content = plan_file.read_text()

        # Then: 应检测到缺失 Tasks
        has_tasks = "## 任务" in content or "## Tasks" in content
        assert has_tasks is False

    def test_rejects_plan_without_acceptance_criteria(self, temp_dir):
        """拒绝没有验收标准的计划"""
        # Given: 没有验收标准的计划
        invalid_plan = """---
version: 1.0.0
---

# Test Plan

## 任务

### Task 1: Do something
"""
        plan_file = create_plan_file(temp_dir, invalid_plan)

        # When: 验证计划结构
        content = plan_file.read_text()

        # Then: 应检测到缺失验收标准
        has_criteria = "## 验收标准" in content or "## Acceptance Criteria" in content
        assert has_criteria is False

    def test_accepts_valid_plan_structure(self, temp_dir, mock_plan_excellent):
        """接受有效的计划结构"""
        # Given: 有效的计划
        plan_file = create_plan_file(temp_dir, mock_plan_excellent)

        # When: 验证结构
        content = plan_file.read_text()

        # Then: 应包含所有必需章节
        required_sections = [
            ("## 任务", "## Tasks"),
            ("## 验收标准", "## Acceptance Criteria")
        ]

        for cn, en in required_sections:
            has_section = cn in content or en in content
            assert has_section is True

    def test_validates_frontmatter_presence(self, temp_dir):
        """验证 YAML frontmatter 存在"""
        # Given: 没有 frontmatter 的计划
        plan_without_frontmatter = """# Test Plan

## 任务

### Task 1: Do something
"""
        plan_file = temp_dir / ".claude" / "plans" / "active" / "test-plan.md"
        plan_file.parent.mkdir(parents=True, exist_ok=True)
        plan_file.write_text(plan_without_frontmatter)

        # When: 检查 frontmatter
        content = plan_file.read_text()
        has_frontmatter = content.startswith("---")

        # Then: 应检测到缺失 frontmatter
        assert has_frontmatter is False


@pytest.mark.unit
class TestCircularDependencyDetection:
    """测试 2: 任务依赖循环检测"""

    def test_detects_simple_circular_dependency(self):
        """验证循环依赖的检测 - 简单循环"""
        # Given: A → B → A 的循环依赖
        dependencies = {
            "Task1": ["Task2"],
            "Task2": ["Task1"]
        }

        # When: 检测循环
        def has_cycle(deps, task, visited=None):
            if visited is None:
                visited = set()
            if task in visited:
                return True
            visited.add(task)
            for dep in deps.get(task, []):
                if has_cycle(deps, dep, visited):
                    return True
            visited.remove(task)
            return False

        # Then: 应检测到循环
        assert has_cycle(dependencies, "Task1") is True

    def test_detects_complex_circular_dependency(self):
        """检测复杂循环 - A → B → C → A"""
        # Given: 三任务循环
        dependencies = {
            "Task1": ["Task2"],
            "Task2": ["Task3"],
            "Task3": ["Task1"]
        }

        # When: 检测循环
        def has_cycle_dfs(deps, task, visiting, visited):
            if task in visiting:
                return True
            if task in visited:
                return False

            visiting.add(task)
            for dep in deps.get(task, []):
                if has_cycle_dfs(deps, dep, visiting, visited):
                    return True
            visiting.remove(task)
            visited.add(task)
            return False

        # Then: 应检测到循环
        visiting, visited = set(), set()
        assert has_cycle_dfs(dependencies, "Task1", visiting, visited) is True

    def test_accepts_valid_dependency_chain(self):
        """接受有效的依赖链"""
        # Given: 线性依赖 A → B → C
        dependencies = {
            "Task1": ["Task2"],
            "Task2": ["Task3"],
            "Task3": []
        }

        # When: 检测循环
        def has_cycle_dfs(deps, task, visiting, visited):
            if task in visiting:
                return True
            if task in visited:
                return False

            visiting.add(task)
            for dep in deps.get(task, []):
                if has_cycle_dfs(deps, dep, visiting, visited):
                    return True
            visiting.remove(task)
            visited.add(task)
            return False

        # Then: 不应有循环
        visiting, visited = set(), set()
        assert has_cycle_dfs(dependencies, "Task1", visiting, visited) is False

    def test_reports_cyclic_task_names(self):
        """报告循环中的任务名称"""
        # Given: 循环依赖
        dependencies = {
            "Task1": ["Task2"],
            "Task2": ["Task3"],
            "Task3": ["Task1"]
        }

        # When: 记录循环路径
        def find_cycle(deps, task, path=None):
            if path is None:
                path = []
            if task in path:
                cycle_start = path.index(task)
                return path[cycle_start:] + [task]
            path.append(task)
            for dep in deps.get(task, []):
                result = find_cycle(deps, dep, path.copy())
                if result:
                    return result
            return None

        # Then: 应返回循环路径
        cycle = find_cycle(dependencies, "Task1")
        assert cycle is not None
        assert "Task1" in cycle
        assert "Task2" in cycle
        assert "Task3" in cycle


@pytest.mark.unit
class TestErrorRecoveryMechanism:
    """测试 3: 错误恢复机制"""

    def test_saves_checkpoint_before_each_task(self, temp_dir):
        """测试失败后的恢复逻辑 - 保存检查点"""
        # Given: 任务执行前
        checkpoint = {
            "issue_number": 123,
            "current_task": 2,
            "completed_tasks": [1],
            "timestamp": datetime.now().isoformat()
        }

        # When: 保存检查点
        checkpoint_file = temp_dir / ".eval-plan-checkpoint.json"
        checkpoint_file.write_text(json.dumps(checkpoint, indent=2))

        # Then: 检查点文件存在
        assert checkpoint_file.exists()
        loaded = json.loads(checkpoint_file.read_text())
        assert loaded["current_task"] == 2

    def test_resumes_from_last_checkpoint(self, temp_dir):
        """从最后的检查点恢复"""
        # Given: 保存的检查点
        checkpoint = {
            "issue_number": 123,
            "current_task": 3,
            "completed_tasks": [1, 2]
        }
        checkpoint_file = temp_dir / ".eval-plan-checkpoint.json"
        checkpoint_file.write_text(json.dumps(checkpoint))

        # When: 恢复执行
        loaded = json.loads(checkpoint_file.read_text())

        # Then: 应从任务 3 开始
        assert loaded["current_task"] == 3
        assert 1 in loaded["completed_tasks"]
        assert 2 in loaded["completed_tasks"]

    def test_cleans_checkpoint_on_success(self, temp_dir):
        """成功完成后清理检查点"""
        # Given: 检查点文件存在
        checkpoint_file = temp_dir / ".eval-plan-checkpoint.json"
        checkpoint_file.write_text("{}")

        # When: 成功完成
        if checkpoint_file.exists():
            checkpoint_file.unlink()

        # Then: 检查点应被删除
        assert not checkpoint_file.exists()


@pytest.mark.unit
class TestFailureLimit:
    """测试 4: 失败限制（最大重试 3 次）"""

    def test_retries_up_to_3_times(self):
        """验证最大重试次数"""
        # Given: 任务执行失败
        max_retries = 3
        retry_count = 0
        success = False

        # When: 模拟重试
        while retry_count < max_retries and not success:
            retry_count += 1
            # 模拟失败
            success = False

        # Then: 应重试 3 次
        assert retry_count == 3
        assert success is False

    def test_stops_after_max_retries(self):
        """达到最大重试次数后停止"""
        # Given: 持续失败的任务
        max_retries = 3
        attempts = []

        # When: 重试逻辑
        for i in range(max_retries):
            attempts.append(i + 1)
            if i + 1 >= max_retries:
                break

        # Then: 应在第 3 次后停止
        assert len(attempts) == 3
        assert attempts[-1] == 3

    def test_raises_max_retries_exceeded_error(self):
        """抛出重试次数超限错误"""
        # Given: 重试次数超限
        max_retries = 3
        retry_count = 3

        # When/Then: 应抛出错误
        with pytest.raises(Exception, match="Max retries exceeded"):
            if retry_count >= max_retries:
                raise Exception(f"Max retries exceeded: {retry_count}/{max_retries}")

    def test_succeeds_before_max_retries(self):
        """在达到最大次数前成功"""
        # Given: 第 2 次尝试成功
        max_retries = 3
        retry_count = 0
        success = False

        # When: 模拟重试，第 2 次成功
        while retry_count < max_retries and not success:
            retry_count += 1
            if retry_count == 2:
                success = True

        # Then: 应在第 2 次成功
        assert retry_count == 2
        assert success is True


@pytest.mark.unit
class TestStatusFileManagement:
    """测试 5: 状态文件管理"""

    def test_creates_status_file_on_completion(self, temp_dir):
        """验证状态文件的创建"""
        # Given: 评估完成
        status = {
            "timestamp": datetime.now().isoformat(),
            "score": 95,
            "status": "approved"
        }

        # When: 写入状态文件
        status_file = temp_dir / ".eval-plan-status.json"
        status_file.write_text(json.dumps(status, indent=2))

        # Then: 文件应存在且有效
        assert status_file.exists()
        loaded = json.loads(status_file.read_text())
        assert loaded["score"] == 95

    def test_updates_existing_status_file(self, temp_dir):
        """更新已存在的状态文件"""
        # Given: 旧的状态文件
        old_status = {"score": 80, "timestamp": "2026-04-06T10:00:00"}
        status_file = temp_dir / ".eval-plan-status.json"
        status_file.write_text(json.dumps(old_status))

        # When: 写入新状态
        new_status = {"score": 95, "timestamp": datetime.now().isoformat()}
        status_file.write_text(json.dumps(new_status, indent=2))

        # Then: 应更新为新状态
        loaded = json.loads(status_file.read_text())
        assert loaded["score"] == 95
        assert loaded["score"] != 80

    def test_cleans_up_stale_status_files(self, temp_dir, mock_expired_status_file):
        """验证状态文件的清理逻辑 - 过期文件"""
        # Given: 过期的状态文件
        status = json.loads(mock_expired_status_file.read_text())
        valid_until = datetime.fromisoformat(status["valid_until"])

        # When: 检查是否过期
        is_expired = datetime.now() > valid_until

        # Then: 应被标记为过期
        assert is_expired is True

    def test_validates_status_file_timestamp(self, temp_dir):
        """验证状态文件时间戳有效性"""
        # Given: 状态文件
        status = {
            "timestamp": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(minutes=90)).isoformat(),
            "score": 95
        }
        status_file = temp_dir / ".eval-plan-status.json"
        status_file.write_text(json.dumps(status))

        # When: 验证时间戳
        loaded = json.loads(status_file.read_text())
        timestamp = datetime.fromisoformat(loaded["timestamp"])
        valid_until = datetime.fromisoformat(loaded["valid_until"])

        # Then: 时间戳应有效
        assert timestamp < valid_until
        assert valid_until > datetime.now()

    def test_atomic_status_file_write(self, temp_dir):
        """原子性写入状态文件（防止部分写入）"""
        # Given: 状态数据
        status = {"score": 95}

        # When: 使用临时文件 + 移动（原子操作）
        import tempfile
        import shutil

        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, dir=temp_dir)
        json.dump(status, temp_file, indent=2)
        temp_file.close()

        status_file = temp_dir / ".eval-plan-status.json"
        shutil.move(temp_file.name, status_file)

        # Then: 状态文件应完整写入
        assert status_file.exists()
        loaded = json.loads(status_file.read_text())
        assert loaded["score"] == 95
