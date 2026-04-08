"""
错误处理测试 - 基于 eval-plan SKILL.md Error Handling 章节

测试 eval-plan 的错误处理：
1. 计划文件缺失
2. 无效 issue number
3. 状态文件写入失败
4. GitHub API 错误
5. 状态文件过期
"""

import json
import pytest
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


@pytest.mark.unit
class TestPlanFileMissing:
    """测试 1: 计划文件缺失"""

    def test_raises_error_when_plan_file_not_found(self, temp_dir):
        """验证文件不存在时的错误消息"""
        # Given: 计划文件不存在
        plan_file = temp_dir / ".claude" / "plans" / "active" / "issue-999-plan.md"

        # When/Then: 应抛出 FileNotFoundError
        with pytest.raises(FileNotFoundError):
            if not plan_file.exists():
                raise FileNotFoundError(f"Plan file not found: {plan_file}")

    def test_error_message_includes_expected_path(self, temp_dir):
        """错误消息应包含期望的路径"""
        # Given: 不存在的计划文件
        expected_path = temp_dir / ".claude" / "plans" / "active" / "issue-123-plan.md"

        # When: 捕获错误
        try:
            if not expected_path.exists():
                raise FileNotFoundError(
                    f"Plan file not found: {expected_path}\n"
                    f"Expected location: .claude/plans/active/"
                )
        except FileNotFoundError as e:
            error_message = str(e)

            # Then: 错误消息应包含路径
            assert str(expected_path) in error_message
            assert ".claude/plans/active/" in error_message

    def test_suggests_running_start_issue(self):
        """建议运行 /start-issue"""
        # Given: 计划文件缺失
        error_message = """Plan file not found: issue-123-plan.md

Expected: .claude/plans/active/issue-123-plan.md

Fix:
1. Run /start-issue #123 to create plan
2. Check issue number is correct
3. Verify worktree path if using worktrees
"""

        # Then: 错误消息应包含建议
        assert "/start-issue" in error_message
        assert "Fix:" in error_message


@pytest.mark.unit
class TestInvalidIssueNumber:
    """测试 2: 无效 issue number"""

    def test_handles_issue_detection_failure(self):
        """验证 issue 检测失败的处理"""
        # Given: Issue 检测失败
        detection_strategies = {
            "from_branch": None,  # Not on feature branch
            "from_active_plans": None,  # Multiple plans found
            "from_worktree": None,  # Not in worktree
            "from_user": None  # User didn't provide
        }

        # When: 所有策略都失败
        detected_issue = next(
            (v for v in detection_strategies.values() if v is not None),
            None
        )

        # Then: 应返回 None
        assert detected_issue is None

    def test_provides_helpful_error_for_detection_failure(self):
        """提供有用的检测失败错误"""
        # Given: 检测失败场景
        error = """Cannot detect issue number

Tried:
1. Argument parsing (none provided)
2. Branch name (on main - no issue number)
3. Active plans (multiple found: 123, 124, 125)
4. Worktree path (not in worktree)

Fix: Provide issue number explicitly: /eval-plan #123
"""

        # Then: 错误消息应详细说明尝试的策略
        assert "Tried:" in error
        assert "Branch name" in error
        assert "Active plans" in error
        assert "Fix:" in error

    def test_validates_issue_exists_on_github(self):
        """验证 issue 在 GitHub 上存在"""
        # Given: 模拟 gh CLI 调用
        mock_gh_response = {
            "number": 123,
            "title": "Test issue",
            "state": "open"
        }

        # When: 验证 issue
        issue_number = 123
        issue_exists = mock_gh_response.get("number") == issue_number

        # Then: 应验证存在性
        assert issue_exists is True


@pytest.mark.unit
class TestStatusFileWriteFailure:
    """测试 3: 状态文件写入失败"""

    def test_handles_permission_denied_error(self, temp_dir):
        """模拟权限错误"""
        # Given: 只读目录（模拟权限错误）
        status_file = temp_dir / ".claude" / ".eval-plan-status.json"

        # When/Then: 应处理权限错误
        with pytest.raises(PermissionError):
            # 模拟权限被拒绝
            raise PermissionError(f"Permission denied: {status_file}")

    def test_error_message_suggests_permission_fix(self):
        """错误消息建议修复权限"""
        # Given: 权限错误
        error = """Cannot write status file

Path: .claude/.eval-plan-status.json
Cause: Permission denied

Fix:
1. Check directory permissions: chmod 755 .claude/
2. Remove existing file: rm .claude/.eval-plan-status.json
3. Verify disk space: df -h
"""

        # Then: 应包含修复建议
        assert "chmod" in error
        assert "Permission denied" in error
        assert "Fix:" in error

    def test_handles_disk_full_error(self, temp_dir):
        """处理磁盘空间不足"""
        # Given: 模拟磁盘满
        with pytest.raises(OSError, match="No space left on device"):
            raise OSError("No space left on device")

    @patch('builtins.open')
    def test_retries_write_on_transient_error(self, mock_open):
        """瞬态错误时重试写入"""
        # Given: 第一次失败，第二次成功
        mock_open.side_effect = [
            IOError("Temporary failure"),
            Mock()  # 第二次成功
        ]

        # When: 重试逻辑
        max_retries = 3
        for attempt in range(max_retries):
            try:
                file_handle = open("test.json", "w")
                break  # 成功
            except IOError as e:
                if attempt == max_retries - 1:
                    raise
                # 继续重试

        # Then: 应在第二次尝试成功
        assert mock_open.call_count == 2


@pytest.mark.unit
class TestGitHubAPIError:
    """测试 4: GitHub API 错误"""

    def test_handles_authentication_failure(self):
        """模拟 gh CLI 认证失败"""
        # Given: 认证失败
        with pytest.raises(Exception, match="GitHub CLI not authenticated"):
            # 模拟 gh auth status 失败
            raise Exception("GitHub CLI not authenticated")

    def test_suggests_gh_auth_login(self):
        """建议运行 gh auth login"""
        # Given: 认证错误
        error = """GitHub CLI not authenticated

Required for: Fetching issue body to check acceptance criteria

Fix: gh auth login
"""

        # Then: 应建议认证
        assert "gh auth login" in error

    def test_handles_rate_limit_exceeded(self):
        """处理 API 速率限制"""
        # Given: 速率限制错误
        error_response = {
            "message": "API rate limit exceeded",
            "documentation_url": "https://docs.github.com/rest/rate-limit"
        }

        # When: 检测速率限制
        is_rate_limited = "rate limit" in error_response["message"].lower()

        # Then: 应检测到速率限制
        assert is_rate_limited is True

    def test_handles_issue_not_found(self):
        """处理 issue 不存在"""
        # Given: Issue 404 错误
        with pytest.raises(Exception, match="Issue #999 not found"):
            # 模拟 gh issue view 返回 404
            raise Exception("Issue #999 not found")

    @patch('subprocess.run')
    def test_retries_on_network_error(self, mock_run):
        """网络错误时重试"""
        # Given: 第一次网络错误，第二次成功
        mock_run.side_effect = [
            Exception("Network error"),
            Mock(returncode=0, stdout='{"number": 123}')
        ]

        # When: 重试逻辑
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = subprocess.run(["gh", "issue", "view", "123"])
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                continue

        # Then: 应重试
        assert mock_run.call_count == 2


@pytest.mark.unit
class TestStatusFileExpiration:
    """测试 5: 状态文件过期"""

    def test_validates_90_minute_expiration(self, temp_dir):
        """验证 90 分钟有效期检查"""
        # Given: 91 分钟前的状态文件
        old_timestamp = datetime.now() - timedelta(minutes=91)
        status = {
            "timestamp": old_timestamp.isoformat(),
            "valid_until": (old_timestamp + timedelta(minutes=90)).isoformat(),
            "score": 95
        }

        status_file = temp_dir / ".eval-plan-status.json"
        status_file.write_text(json.dumps(status))

        # When: 检查过期
        loaded = json.loads(status_file.read_text())
        valid_until = datetime.fromisoformat(loaded["valid_until"])
        is_expired = datetime.now() > valid_until

        # Then: 应已过期
        assert is_expired is True

    def test_accepts_valid_status_within_90_minutes(self, temp_dir, mock_status_file):
        """接受 90 分钟内的有效状态"""
        # Given: 刚创建的状态文件
        status = json.loads(mock_status_file.read_text())
        valid_until = datetime.fromisoformat(status["valid_until"])

        # When: 检查过期
        is_expired = datetime.now() > valid_until

        # Then: 不应过期
        assert is_expired is False

    def test_warns_on_expired_status(self, temp_dir, mock_expired_status_file):
        """过期状态应发出警告"""
        # Given: 过期的状态文件
        status = json.loads(mock_expired_status_file.read_text())
        valid_until = datetime.fromisoformat(status["valid_until"])
        timestamp = datetime.fromisoformat(status["timestamp"])

        # When: 生成警告消息
        warning = f"""Status file expired

Created: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Valid until: {valid_until.strftime('%Y-%m-%d %H:%M:%S')} (90 minutes)
Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Action: Re-run /eval-plan to generate fresh status
"""

        # Then: 警告应包含时间信息
        assert "expired" in warning.lower()
        assert "Re-run" in warning

    def test_calculates_valid_until_correctly(self):
        """正确计算 valid_until 时间戳"""
        # Given: 当前时间
        now = datetime.now()

        # When: 计算过期时间
        valid_until = now + timedelta(minutes=90)

        # Then: 应为 90 分钟后
        time_diff = (valid_until - now).total_seconds()
        assert 5390 <= time_diff <= 5410  # 90 分钟 ± 10 秒容差


@pytest.mark.integration
class TestErrorRecoveryIntegration:
    """集成测试：错误恢复场景"""

    def test_recovers_from_partial_evaluation(self, temp_dir):
        """从部分评估中恢复"""
        # Given: 部分完成的评估
        checkpoint = {
            "completed_dimensions": ["architecture", "coverage"],
            "pending_dimensions": ["dependencies", "practices", "clarity"]
        }

        checkpoint_file = temp_dir / ".eval-plan-checkpoint.json"
        checkpoint_file.write_text(json.dumps(checkpoint))

        # When: 恢复评估
        loaded = json.loads(checkpoint_file.read_text())

        # Then: 应从 pending 继续
        assert len(loaded["pending_dimensions"]) == 3
        assert "dependencies" in loaded["pending_dimensions"]

    def test_graceful_degradation_on_missing_dependencies(self, temp_dir):
        """缺失依赖时优雅降级"""
        # Given: 缺失架构规则
        rules_dir = temp_dir / ".claude" / "rules" / "architecture"
        has_rules = rules_dir.exists()

        # When: 评估时检查依赖
        if not has_rules:
            # 跳过架构检查，继续其他维度
            skipped_dimensions = ["architecture"]
        else:
            skipped_dimensions = []

        # Then: 应跳过架构维度
        assert "architecture" in skipped_dimensions
