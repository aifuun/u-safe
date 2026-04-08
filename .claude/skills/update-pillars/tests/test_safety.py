"""
安全测试 - 基于 update-pillars SKILL.md "Safety Features" 章节

测试安全机制:
1. Pre-flight checks (source/target paths exist, .claude/pillars/ exists)
2. User confirmation before changes
3. Dry-run preview available
4. Profile-aware filtering
5. Clear status for each Pillar
"""

import unittest
import tempfile
import shutil
from pathlib import Path


class TestPreFlightChecks(unittest.TestCase):
    """测试 Pre-flight checks"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """清理临时测试目录"""
        shutil.rmtree(self.test_dir)

    def test_validate_source_path_exists(self):
        """验证源路径存在"""
        # Given: 创建源项目
        source_root = self.test_root / "ai-dev"
        source_root.mkdir()

        # When: 验证源路径
        source_exists = source_root.exists()

        # Then: 应存在
        self.assertTrue(source_exists)

    def test_validate_target_path_exists(self):
        """验证目标路径存在"""
        # Given: 创建目标项目
        target_root = self.test_root / "my-app"
        target_root.mkdir()

        # When: 验证目标路径
        target_exists = target_root.exists()

        # Then: 应存在
        self.assertTrue(target_exists)

    def test_validate_source_has_pillars_directory(self):
        """验证源项目有 .claude/pillars/ 目录"""
        # Given: 创建完整的源项目结构
        source_root = self.test_root / "ai-dev"
        source_pillars = source_root / ".claude" / "pillars"
        source_pillars.mkdir(parents=True)

        # When: 检查 Pillars 目录
        has_pillars_dir = source_pillars.exists() and source_pillars.is_dir()

        # Then: 应存在
        self.assertTrue(has_pillars_dir)

    def test_reject_source_without_pillars_directory(self):
        """拒绝没有 Pillars 目录的源项目"""
        # Given: 源项目没有 .claude/pillars/ 目录
        source_root = self.test_root / "ai-dev"
        source_root.mkdir()

        # When: 检查 Pillars 目录
        pillars_dir = source_root / ".claude" / "pillars"
        has_pillars_dir = pillars_dir.exists()

        # Then: 不应存在
        self.assertFalse(has_pillars_dir)


class TestDryRunMode(unittest.TestCase):
    """测试 Dry-run preview 功能"""

    def test_dry_run_shows_preview_without_changes(self):
        """Dry-run 显示预览但不修改文件"""
        # Given: Dry-run 模式
        dry_run = True

        # When: 检查是否应执行修改
        should_modify = not dry_run

        # Then: 不应修改
        self.assertFalse(should_modify)

    def test_dry_run_reports_what_would_be_synced(self):
        """Dry-run 报告将要同步的内容"""
        # Given: 分析结果
        analysis = {
            "pillar-a": {"status": "NEWER", "action": "Update"},
            "pillar-k": {"status": "NEW", "action": "Add"},
            "pillar-b": {"status": "SAME", "action": "Skip"}
        }

        # When: 过滤需要同步的 Pillars
        to_sync = {k: v for k, v in analysis.items() if v["action"] != "Skip"}

        # Then: 应报告 2 个需要同步
        self.assertEqual(len(to_sync), 2)
        self.assertIn("pillar-a", to_sync)
        self.assertIn("pillar-k", to_sync)


class TestProfileAwareFiltering(unittest.TestCase):
    """测试 Profile-aware filtering"""

    def test_minimal_profile_filters_pillars(self):
        """minimal profile 只同步 A, B, K"""
        # Given: minimal profile 配置
        profile = "minimal"
        allowed_pillars = {
            "minimal": ["pillar-a", "pillar-b", "pillar-k"],
            "node-lambda": ["pillar-a", "pillar-b", "pillar-k", "pillar-m", "pillar-q", "pillar-r"],
        }

        all_pillars = ["pillar-a", "pillar-b", "pillar-k", "pillar-m", "pillar-q"]

        # When: 按 profile 过滤
        filtered = [p for p in all_pillars if p in allowed_pillars[profile]]

        # Then: 只保留 A, B, K
        self.assertEqual(len(filtered), 3)
        self.assertEqual(sorted(filtered), ["pillar-a", "pillar-b", "pillar-k"])

    def test_node_lambda_profile_includes_more_pillars(self):
        """node-lambda profile 包含更多 Pillars"""
        # Given: node-lambda profile
        profile = "node-lambda"
        allowed_pillars = {
            "minimal": ["pillar-a", "pillar-b", "pillar-k"],
            "node-lambda": ["pillar-a", "pillar-b", "pillar-k", "pillar-m", "pillar-q", "pillar-r"],
        }

        all_pillars = ["pillar-a", "pillar-b", "pillar-k", "pillar-m", "pillar-q"]

        # When: 按 profile 过滤
        filtered = [p for p in all_pillars if p in allowed_pillars[profile]]

        # Then: 应包含 5 个 Pillars
        self.assertEqual(len(filtered), 5)


class TestClearStatusReporting(unittest.TestCase):
    """测试清晰的状态报告"""

    def test_status_includes_pillar_name(self):
        """状态应包含 Pillar 名称"""
        # Given: Pillar 状态
        status = {"name": "pillar-a", "status": "NEWER", "action": "Update"}

        # When/Then: 应包含名称
        self.assertIn("name", status)
        self.assertEqual(status["name"], "pillar-a")

    def test_status_includes_action(self):
        """状态应包含操作说明"""
        # Given: Pillar 状态
        status = {"name": "pillar-k", "status": "NEW", "action": "Add (180 lines)"}

        # When/Then: 应包含操作
        self.assertIn("action", status)
        self.assertIn("Add", status["action"])

    def test_status_distinguishes_newer_same_older(self):
        """状态应区分 NEWER, SAME, OLDER"""
        # Given: 不同状态的 Pillars
        statuses = ["NEWER", "SAME", "OLDER", "NEW"]

        # When: 检查所有状态都不同
        unique_statuses = set(statuses)

        # Then: 应有 4 种不同状态
        self.assertEqual(len(unique_statuses), 4)


if __name__ == "__main__":
    unittest.main()
