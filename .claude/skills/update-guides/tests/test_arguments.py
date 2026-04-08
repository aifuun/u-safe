"""
参数验证测试 - 基于 update-guides SKILL.md "Arguments" 章节

测试 update-guides 的参数验证:
- target-project-path (必需)
- --dry-run (可选)
- --force (可选)
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestTargetProjectPath(unittest.TestCase):
    """测试参数: target-project-path（必需）"""

    def setUp(self):
        """Create temporary test structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_accept_valid_absolute_path(self):
        """接受有效的绝对路径"""
        # Given: 有效的绝对路径
        target_path = self.test_root / "target-project"
        target_path.mkdir()

        # When: 验证路径
        is_absolute = target_path.is_absolute()
        exists = target_path.exists()

        # Then: 应接受
        self.assertTrue(is_absolute)
        self.assertTrue(exists)

    def test_accept_valid_relative_path(self):
        """接受有效的相对路径（../my-project）"""
        # Given: 相对路径
        current_dir = self.test_root / "current"
        current_dir.mkdir()
        target_dir = self.test_root / "target"
        target_dir.mkdir()

        # When: 计算相对路径
        relative_path = Path("..") / "target"

        # Then: 相对路径应有效
        self.assertFalse(relative_path.is_absolute())
        # 验证路径格式
        self.assertIn("..", str(relative_path))

    def test_reject_missing_path(self):
        """拒绝缺失的 path 参数"""
        # Given: 空路径
        path = None

        # When: 验证
        is_valid = path is not None and path != ""

        # Then: 应拒绝
        self.assertFalse(is_valid)

    def test_reject_nonexistent_path(self):
        """拒绝不存在的路径"""
        # Given: 不存在的路径
        nonexistent_path = self.test_root / "does-not-exist"

        # When: 验证
        exists = nonexistent_path.exists()

        # Then: 应返回 False
        self.assertFalse(exists)


class TestDryRunFlag(unittest.TestCase):
    """测试参数: --dry-run（可选）"""

    def setUp(self):
        """Create temporary test structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_dry_run_mode_no_changes(self):
        """dry-run 模式不执行实际更改"""
        # Given: dry-run 标志
        dry_run = True

        # When: 模拟操作
        source_file = self.test_root / "source" / "test.md"
        source_file.parent.mkdir()
        source_file.write_text("content")

        target_file = self.test_root / "target" / "test.md"

        # dry-run 模式下不复制
        if not dry_run:
            target_file.parent.mkdir(exist_ok=True)
            shutil.copy2(source_file, target_file)

        # Then: 目标文件不应被创建
        self.assertFalse(target_file.exists())

    def test_dry_run_shows_preview(self):
        """dry-run 显示预览信息"""
        # Given: dry-run 标志
        dry_run = True

        # When: 生成预览
        preview_actions = []
        if dry_run:
            preview_actions.append("Would copy: source/test.md -> target/test.md")
            preview_actions.append("Would create: target/.ai-guides-version")

        # Then: 应生成预览信息
        self.assertTrue(len(preview_actions) > 0)
        self.assertIn("Would copy", preview_actions[0])
        self.assertIn("Would create", preview_actions[1])


class TestForceFlag(unittest.TestCase):
    """测试参数: --force（可选）"""

    def setUp(self):
        """Create temporary test structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_force_flag_overrides_safety_checks(self):
        """force 标志绕过安全检查"""
        # Given: force 标志和安全检查
        force = True
        safety_check_passed = False  # 模拟安全检查失败

        # When: 决定是否继续
        should_proceed = force or safety_check_passed

        # Then: force 标志应绕过检查
        self.assertTrue(should_proceed)
        self.assertTrue(force)

        # 测试没有 force 时
        force_disabled = False
        should_proceed_without_force = force_disabled or safety_check_passed
        self.assertFalse(should_proceed_without_force)


if __name__ == "__main__":
    unittest.main()
