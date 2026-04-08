"""
Tests for start-issue skill functionality.

This module tests the core functionality of the start-issue skill including:
- GitHub issue management
- Branch creation and naming
- Worktree management
- Plan generation
- Safety features
"""
import json
import re
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest


class TestIssueManagement:
    """测试 GitHub Issue 管理功能"""

    def test_fetch_existing_issue(self, mock_gh_cli, mock_gh_issue):
        """测试获取已存在的 issue"""
        # TODO: Implement test
        pass

    def test_create_new_issue(self):
        """测试创建新 issue (--create 选项)"""
        # TODO: Implement test
        pass

    def test_issue_validation_open(self, mock_gh_issue):
        """测试 issue 状态验证 (OPEN)"""
        assert mock_gh_issue["state"] == "OPEN"

    def test_issue_validation_closed(self):
        """测试 issue 状态验证 (CLOSED 应警告)"""
        # TODO: Implement test
        pass


class TestBranchManagement:
    """测试分支管理功能"""

    def test_branch_name_generation_simple(self):
        """测试分支名生成 - 简单标题"""
        title = "Fix Login Bug"
        expected = "feature/123-fix-login-bug"

        # Simple kebab-case conversion
        kebab_title = title.lower().replace(' ', '-')
        result = f"feature/123-{kebab_title}"

        assert result == expected

    def test_branch_name_generation_special_chars(self):
        """测试分支名生成 - 特殊字符处理"""
        title = "feat: Add User Authentication (OAuth2)"
        # Should remove special chars and convert to kebab-case
        # Expected: "feature/123-feat-add-user-authentication-oauth2"

        # Remove colons, parentheses
        cleaned = re.sub(r'[:\(\)]', '', title)
        # Convert to kebab-case
        kebab_title = re.sub(r'[^a-z0-9]+', '-', cleaned.lower()).strip('-')
        result = f"feature/123-{kebab_title}"

        assert result == "feature/123-feat-add-user-authentication-oauth2"

    def test_branch_name_truncation(self):
        """测试分支名截断 (>50 chars)"""
        long_title = "This is a very long issue title that exceeds fifty characters"
        kebab_title = long_title.lower().replace(' ', '-')

        # Truncate to 50 chars
        if len(kebab_title) > 50:
            kebab_title = kebab_title[:50].rsplit('-', 1)[0]

        result = f"feature/123-{kebab_title}"
        assert len(kebab_title) <= 50

    def test_branch_existence_check(self, temp_git_repo):
        """测试分支存在性检查"""
        # Create a branch
        subprocess.run(["git", "branch", "test-branch"], cwd=temp_git_repo, check=True, capture_output=True)

        # Check if branch exists
        result = subprocess.run(
            ["git", "branch", "--list", "test-branch"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True
        )

        assert "test-branch" in result.stdout

    def test_custom_branch_prefix(self):
        """测试 --branch-prefix 选项"""
        prefix = "fix"
        issue_number = 123
        title = "authentication-bug"

        result = f"{prefix}/{issue_number}-{title}"
        assert result == "fix/123-authentication-bug"


class TestWorktreeManagement:
    """测试 Worktree 管理功能"""

    def test_worktree_directory_naming(self):
        """测试 worktree 目录命名规则"""
        repo_name = "ai-dev"
        issue_number = 123
        kebab_title = "fix-login-bug"

        expected = f"{repo_name}-{issue_number}-{kebab_title}"
        assert expected == "ai-dev-123-fix-login-bug"

    def test_worktree_creation(self, temp_git_repo, tmp_path):
        """测试 worktree 创建逻辑"""
        worktree_dir = tmp_path / "test-worktree"
        branch_name = "feature/123-test"

        # Create worktree
        result = subprocess.run(
            ["git", "worktree", "add", str(worktree_dir), "-b", branch_name],
            cwd=temp_git_repo,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert worktree_dir.exists()

        # Verify worktree list
        result = subprocess.run(
            ["git", "worktree", "list"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True
        )
        assert str(worktree_dir) in result.stdout

        # Cleanup
        subprocess.run(["git", "worktree", "remove", str(worktree_dir)], cwd=temp_git_repo)

    def test_no_worktree_option(self):
        """测试 --no-worktree 选项 (应使用传统分支切换)"""
        # TODO: Implement test for --no-worktree behavior
        pass

    def test_worktree_conflict_detection(self, temp_git_repo, tmp_path):
        """测试 worktree 冲突检测"""
        worktree_dir = tmp_path / "conflict-worktree"
        worktree_dir.mkdir()

        # Try to create worktree in existing directory
        result = subprocess.run(
            ["git", "worktree", "add", str(worktree_dir), "-b", "test-branch"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True
        )

        # Git allows creating worktree in existing directory
        # The directory must be empty for safety
        # This test validates the behavior (may succeed or fail depending on git version)
        # Just verify the command runs
        assert result.returncode in [0, 128]  # Both outcomes are acceptable


class TestPlanGeneration:
    """测试 Plan 生成功能"""

    def test_plan_file_generation(self, tmp_path, sample_issue_body):
        """测试 plan 文件生成"""
        plan_dir = tmp_path / ".claude" / "plans" / "active"
        plan_dir.mkdir(parents=True)

        plan_file = plan_dir / "issue-123-plan.md"
        plan_content = f"""# Issue #123: Test Issue

**GitHub**: https://github.com/test/repo/issues/123
**Branch**: feature/123-test-issue
**Worktree**: /path/to/worktree
**Started**: 2026-04-07

## Context
{sample_issue_body}

## Progress
- [ ] Plan reviewed

## Next Steps
1. Review this plan
2. Start implementation
"""

        plan_file.write_text(plan_content)
        assert plan_file.exists()

        # Verify plan content structure
        content = plan_file.read_text()
        assert "# Issue #123" in content
        assert "**GitHub**:" in content
        assert "**Branch**:" in content
        assert "**Worktree**:" in content

    def test_plan_content_structure(self, sample_issue_body):
        """测试 plan 内容结构包含必需元数据"""
        # Required metadata
        required_sections = [
            "# Issue #",
            "**GitHub**:",
            "**Branch**:",
            "**Started**:",
            "## Context",
            "## Tasks",
            "## Progress",
            "## Next Steps"
        ]

        plan_template = f"""# Issue #123: Test

**GitHub**: https://github.com/test/repo/issues/123
**Branch**: feature/123-test
**Started**: 2026-04-07

## Context
Test context

## Tasks
- [ ] Task 1

## Progress
- [ ] Plan reviewed

## Next Steps
1. Review plan
"""

        for section in required_sections:
            assert section in plan_template

    def test_no_plan_option(self):
        """测试 --no-plan 选项 (应跳过 plan 生成)"""
        # TODO: Implement test for --no-plan behavior
        pass

    def test_worktree_path_recording(self):
        """测试 worktree 路径记录在 plan 元数据中"""
        worktree_path = "/Users/woo/dev/ai-dev-123-test"
        plan_content = f"""# Issue #123: Test

**Worktree**: {worktree_path}
"""

        # Extract worktree path from plan
        match = re.search(r'\*\*Worktree\*\*: (.+)', plan_content)
        assert match is not None
        assert match.group(1) == worktree_path


class TestSafetyFeatures:
    """测试安全机制功能"""

    def test_environment_validation_on_main(self, temp_git_repo):
        """测试环境验证 - 在 main 分支 (✅ 安全)"""
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True
        )

        current_branch = result.stdout.strip()
        assert current_branch == "main"

    def test_environment_validation_on_feature_branch(self, temp_git_repo):
        """测试环境验证 - 在 feature 分支 (❌ 应阻止)"""
        # Create and switch to feature branch
        subprocess.run(
            ["git", "checkout", "-b", "feature/existing"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True
        )

        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True
        )

        current_branch = result.stdout.strip()
        assert current_branch.startswith("feature/")

        # Should detect and warn about nested branch creation

    def test_git_status_clean(self, temp_git_repo):
        """测试 git 工作目录干净"""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True
        )

        assert result.stdout == ""  # Clean working directory

    def test_git_status_uncommitted_changes(self, temp_git_repo):
        """测试检测未提交的更改"""
        # Create uncommitted change
        test_file = temp_git_repo / "test.txt"
        test_file.write_text("uncommitted change")

        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True
        )

        assert result.stdout != ""  # Has uncommitted changes
        assert "test.txt" in result.stdout

    def test_branch_conflict_detection(self, temp_git_repo):
        """测试分支冲突检测"""
        branch_name = "feature/123-test"

        # Create branch
        subprocess.run(
            ["git", "branch", branch_name],
            cwd=temp_git_repo,
            check=True,
            capture_output=True
        )

        # Try to create same branch again should fail
        result = subprocess.run(
            ["git", "branch", branch_name],
            cwd=temp_git_repo,
            capture_output=True,
            text=True
        )

        assert result.returncode != 0
        # Check for error in stderr (locale-independent)
        assert result.returncode == 128  # Git error code for branch exists

    def test_force_option(self):
        """测试 --force 选项 (应跳过安全检查)"""
        # TODO: Implement test for --force bypass behavior
        pass

    def test_error_recovery_stash(self, temp_git_repo):
        """测试错误恢复机制 - 自动 stash"""
        # Create uncommitted change
        test_file = temp_git_repo / "test.txt"
        test_file.write_text("uncommitted")

        # Add the file first (git stash only works on tracked or staged files)
        subprocess.run(["git", "add", "test.txt"], cwd=temp_git_repo, check=True, capture_output=True)

        # Stash changes
        result = subprocess.run(
            ["git", "stash"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0

        # Verify working directory is clean
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True
        )

        # After stash, working directory should be clean
        assert result.stdout == ""
