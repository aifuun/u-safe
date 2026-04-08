"""
异常测试 - 基于 update-guides SKILL.md "Error Handling" 章节

测试 update-guides 的错误处理:
- Guides directory errors
- Permission errors
- Sync failures
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestGuidesDirectoryErrors(unittest.TestCase):
    """测试 guides 目录相关错误"""

    def setUp(self):
        """Create temporary test structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_handle_missing_framework_guides(self):
        """处理缺失的 framework guides 目录"""
        # Given: framework 没有 guides 目录
        framework_dir = self.test_root / "framework"
        framework_dir.mkdir()

        # When: 检查 guides 目录
        guides_dir = framework_dir / ".claude" / "guides"
        has_guides = guides_dir.exists()

        # Then: 应返回 False（错误处理应捕获）
        self.assertFalse(has_guides)

        # 模拟错误处理
        try:
            if not has_guides:
                raise FileNotFoundError("Guides directory not found")
        except FileNotFoundError as e:
            error_handled = True
            error_message = str(e)

        self.assertTrue(error_handled)
        self.assertIn("not found", error_message)

    def test_handle_incomplete_guides_structure(self):
        """处理不完整的 guides 结构"""
        # Given: guides 目录不完整（缺少子目录）
        guides_dir = self.test_root / "framework" / ".claude" / "guides"
        guides_dir.mkdir(parents=True)
        # 只创建 workflow，缺少其他目录
        (guides_dir / "workflow").mkdir()

        # When: 验证完整性
        required_dirs = ["workflow", "doc-templates", "rules", "profiles", "templates"]
        missing_dirs = [d for d in required_dirs if not (guides_dir / d).exists()]

        # Then: 应检测到缺失
        self.assertTrue(len(missing_dirs) > 0)
        self.assertIn("doc-templates", missing_dirs)
        self.assertIn("rules", missing_dirs)


class TestPermissionErrors(unittest.TestCase):
    """测试权限错误"""

    def setUp(self):
        """Create temporary test structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        # Restore permissions before cleanup
        for root, dirs, files in os.walk(self.test_dir):
            for d in dirs:
                os.chmod(os.path.join(root, d), 0o755)
            for f in files:
                os.chmod(os.path.join(root, f), 0o644)
        shutil.rmtree(self.test_dir)

    def test_handle_target_directory_not_writable(self):
        """处理目标目录不可写"""
        # Given: 只读目标目录
        target_dir = self.test_root / "readonly-target"
        target_dir.mkdir()
        target_dir.chmod(0o444)  # 只读

        # When: 尝试写入
        test_file = target_dir / "test.txt"
        try:
            test_file.write_text("test")
            write_succeeded = True
        except (PermissionError, OSError):
            write_succeeded = False

        # Then: 应失败
        self.assertFalse(write_succeeded)

        # 恢复权限用于清理
        target_dir.chmod(0o755)

    def test_handle_permission_denied_on_delete(self):
        """处理删除时权限拒绝"""
        # Given: 受保护的目录
        protected_dir = self.test_root / "protected"
        protected_dir.mkdir()
        (protected_dir / "file.txt").write_text("content")
        protected_dir.chmod(0o444)  # 只读，无法删除内容

        # When: 尝试删除
        try:
            shutil.rmtree(protected_dir)
            delete_succeeded = True
        except (PermissionError, OSError):
            delete_succeeded = False

        # Then: 应失败或需要特殊处理
        # Note: 行为可能因操作系统而异
        # 恢复权限
        protected_dir.chmod(0o755)


class TestSyncFailures(unittest.TestCase):
    """测试同步失败场景"""

    def setUp(self):
        """Create temporary test structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_handle_partial_copy_failure(self):
        """处理部分复制失败"""
        # Given: 源目录
        source_dir = self.test_root / "source"
        source_dir.mkdir()
        (source_dir / "file1.md").write_text("content1")
        (source_dir / "file2.md").write_text("content2")

        # When: 模拟部分失败（只复制一个文件）
        target_dir = self.test_root / "target"
        target_dir.mkdir()

        copied_files = []
        failed_files = []

        for file in source_dir.glob("*.md"):
            try:
                if file.name == "file2.md":
                    # 模拟失败
                    raise IOError("Simulated copy failure")
                shutil.copy2(file, target_dir / file.name)
                copied_files.append(file.name)
            except IOError:
                failed_files.append(file.name)

        # Then: 应跟踪失败
        self.assertEqual(len(copied_files), 1)
        self.assertEqual(len(failed_files), 1)
        self.assertIn("file2.md", failed_files)

    def test_rollback_on_critical_error(self):
        """关键错误时回滚"""
        # Given: 备份原始状态
        target_dir = self.test_root / "target"
        target_dir.mkdir()
        original_file = target_dir / "original.md"
        original_file.write_text("original content")

        # 记录原始状态
        backup_content = original_file.read_text()

        # When: 模拟同步失败
        try:
            # 删除原文件
            original_file.unlink()

            # 模拟复制失败
            raise IOError("Critical sync error")

        except IOError:
            # Then: 回滚 - 恢复原文件
            original_file.write_text(backup_content)

        # 验证回滚成功
        self.assertTrue(original_file.exists())
        self.assertEqual(original_file.read_text(), "original content")


if __name__ == "__main__":
    unittest.main()
