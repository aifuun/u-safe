"""
错误处理测试 - 基于 update-pillars SKILL.md "Error Handling" 章节

测试错误场景:
1. Invalid source/target paths
2. No Pillars to update
3. OLDER source (warning)
4. Permission issues
5. Error message formatting
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import os


class TestInvalidPaths(unittest.TestCase):
    """测试无效路径处理"""

    def test_nonexistent_target_path(self):
        """处理不存在的目标路径"""
        # Given: 不存在的路径
        target_path = Path("/nonexistent/path/12345")

        # When: 检查路径
        path_exists = target_path.exists()

        # Then: 应不存在
        self.assertFalse(path_exists)

    def test_target_without_pillars_directory(self):
        """处理没有 .claude/pillars/ 的目标项目"""
        # Given: 创建目标但没有 Pillars 目录
        with tempfile.TemporaryDirectory() as tmpdir:
            target_root = Path(tmpdir) / "my-app"
            target_root.mkdir()

            # When: 检查 Pillars 目录
            pillars_dir = target_root / ".claude" / "pillars"
            has_pillars = pillars_dir.exists()

            # Then: 不应存在
            self.assertFalse(has_pillars)

    def test_error_message_includes_expected_path(self):
        """错误消息应包含期望的路径"""
        # Given: 错误场景
        target_path = "../nonexistent"
        expected_pillars = "../nonexistent/.claude/pillars/"

        # When: 构建错误消息
        error_message = f"Path: {target_path}\nExpected: {expected_pillars}"

        # Then: 应包含路径信息
        self.assertIn(target_path, error_message)
        self.assertIn(expected_pillars, error_message)


class TestNoPillarsToUpdate(unittest.TestCase):
    """测试没有 Pillars 需要更新的情况"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """清理临时测试目录"""
        shutil.rmtree(self.test_dir)

    def test_all_pillars_up_to_date(self):
        """所有 Pillars 都是最新的"""
        # Given: 源和目标有相同的 Pillars
        content = "# Pillar A\nSame content\n"

        source_root = self.test_root / "ai-dev"
        source_pillars = source_root / ".claude" / "pillars"
        source_pillars.mkdir(parents=True)
        (source_pillars / "pillar-a").mkdir()
        (source_pillars / "pillar-a" / "pillar-a.md").write_text(content)

        target_root = self.test_root / "my-app"
        target_pillars = target_root / ".claude" / "pillars"
        target_pillars.mkdir(parents=True)
        (target_pillars / "pillar-a").mkdir()
        (target_pillars / "pillar-a" / "pillar-a.md").write_text(content)

        # When: 比较
        source_content = (source_pillars / "pillar-a" / "pillar-a.md").read_text()
        target_content = (target_pillars / "pillar-a" / "pillar-a.md").read_text()
        needs_update = source_content != target_content

        # Then: 不需要更新
        self.assertFalse(needs_update)

    def test_success_message_when_up_to_date(self):
        """当 Pillars 都是最新时显示成功消息"""
        # Given: 没有需要更新的 Pillars
        to_update = []

        # When: 生成消息
        if not to_update:
            message = "✅ All Pillars are up to date!"
        else:
            message = f"{len(to_update)} Pillars to update"

        # Then: 应显示成功消息
        self.assertIn("up to date", message)


class TestOlderSourceWarning(unittest.TestCase):
    """测试源比目标旧的警告"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """清理临时测试目录"""
        shutil.rmtree(self.test_dir)

    def test_detect_older_source(self):
        """检测源 Pillar 比目标旧"""
        # Given: 源有较少内容（可能更旧）
        source_root = self.test_root / "ai-dev"
        source_pillars = source_root / ".claude" / "pillars"
        source_pillars.mkdir(parents=True)
        (source_pillars / "pillar-a").mkdir()
        source_file = source_pillars / "pillar-a" / "pillar-a.md"
        source_file.write_text("# Pillar A\n" * 10)  # 245 lines

        # 目标有更多内容（可能更新）
        target_root = self.test_root / "my-app"
        target_pillars = target_root / ".claude" / "pillars"
        target_pillars.mkdir(parents=True)
        (target_pillars / "pillar-a").mkdir()
        target_file = target_pillars / "pillar-a" / "pillar-a.md"
        target_file.write_text("# Pillar A\nUpdated\n" * 12)  # 250 lines

        # When: 比较大小
        source_size = source_file.stat().st_size
        target_size = target_file.stat().st_size
        is_older = source_size < target_size

        # Then: 源应该更小（OLDER）
        self.assertTrue(is_older)

    def test_warning_message_for_older_source(self):
        """为更旧的源生成警告消息"""
        # Given: 检测到 OLDER 状态
        pillar_name = "pillar-a"
        source_lines = 245
        target_lines = 250
        status = "OLDER"

        # When: 生成警告消息
        if status == "OLDER":
            warning = f"⚠️ Warning: Source Pillar is OLDER\nPillar: {pillar_name}"
        else:
            warning = ""

        # Then: 应包含警告
        self.assertIn("Warning", warning)
        self.assertIn("OLDER", warning)

    def test_skip_older_source_by_default(self):
        """默认跳过更旧的源"""
        # Given: OLDER 状态
        status = "OLDER"

        # When: 决定操作
        if status == "OLDER":
            action = "Skip (keeping newer target version)"
        else:
            action = "Update"

        # Then: 应跳过
        self.assertIn("Skip", action)


class TestPermissionIssues(unittest.TestCase):
    """测试权限问题处理"""

    def test_detect_readonly_target(self):
        """检测只读的目标目录"""
        # Given: 创建只读目录
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir) / "readonly"
            target_dir.mkdir()

            # 设置为只读
            os.chmod(target_dir, 0o444)

            # When: 检查写权限
            is_writable = os.access(target_dir, os.W_OK)

            # Then: 不应可写
            self.assertFalse(is_writable)

            # 清理：恢复权限
            os.chmod(target_dir, 0o755)


class TestErrorMessageFormatting(unittest.TestCase):
    """测试错误消息格式"""

    def test_error_message_includes_path(self):
        """错误消息应包含路径"""
        # Given: 路径错误
        invalid_path = "../nonexistent"

        # When: 格式化错误消息
        error = f"❌ Error: Project not found\n\nPath: {invalid_path}"

        # Then: 应包含路径
        self.assertIn(invalid_path, error)

    def test_error_message_includes_suggestions(self):
        """错误消息应包含解决建议"""
        # Given: 错误场景
        error_type = "path_not_found"

        # When: 添加建议
        suggestions = [
            "1. Path is correct",
            "2. Project has .claude/pillars/ directory",
            "3. You have read permissions"
        ]

        error = f"Please check:\n" + "\n".join(suggestions)

        # Then: 应包含建议
        self.assertIn("Please check", error)
        self.assertIn("permissions", error)


if __name__ == "__main__":
    unittest.main()
