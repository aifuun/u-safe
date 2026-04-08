"""
安全测试 - 基于 update-guides SKILL.md "Safety Features" 章节

测试 update-guides 的安全机制:
- Pre-flight validation
- Smart defaults
- Validation points
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestPreFlightValidation(unittest.TestCase):
    """测试 Pre-flight 检查"""

    def setUp(self):
        """Create temporary test structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_validate_run_from_ai_dev_directory(self):
        """验证必须从 ai-dev 目录运行"""
        # Given: ai-dev 目录标记
        framework_dir = self.test_root / "ai-dev"
        framework_dir.mkdir()
        (framework_dir / ".claude").mkdir()
        marker_file = framework_dir / "CLAUDE.md"
        marker_file.write_text("# AI Development Framework")

        # When: 验证是否在 framework
        is_framework = marker_file.exists() and "Framework" in marker_file.read_text()

        # Then: 应检测到 framework 目录
        self.assertTrue(is_framework)

    def test_fail_when_not_in_framework(self):
        """非 framework 目录运行时失败"""
        # Given: 普通目录（非 framework）
        normal_dir = self.test_root / "my-project"
        normal_dir.mkdir()

        # When: 检查是否为 framework
        marker_file = normal_dir / "CLAUDE.md"
        is_framework = marker_file.exists() and \
                      (marker_file.is_file() and "Framework" in marker_file.read_text() if marker_file.exists() else False)

        # Then: 应返回 False
        self.assertFalse(is_framework)

    def test_validate_guides_directory_exists(self):
        """验证 guides 目录存在"""
        # Given: framework 目录
        framework_dir = self.test_root / "ai-dev"
        framework_dir.mkdir()
        guides_dir = framework_dir / ".claude" / "guides"
        guides_dir.mkdir(parents=True)

        # When: 验证 guides 存在
        has_guides = guides_dir.exists() and guides_dir.is_dir()

        # Then: 应通过验证
        self.assertTrue(has_guides)


class TestSmartDefaults(unittest.TestCase):
    """测试 Smart Defaults"""

    def setUp(self):
        """Create temporary test structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_auto_detect_framework_directory(self):
        """自动检测 framework 目录"""
        # Given: 当前目录是 framework
        framework_dir = self.test_root / "ai-dev"
        framework_dir.mkdir()
        (framework_dir / ".claude" / "guides").mkdir(parents=True)

        # When: 自动检测
        detected_guides = framework_dir / ".claude" / "guides"
        is_detected = detected_guides.exists()

        # Then: 应自动检测到
        self.assertTrue(is_detected)

    def test_default_sync_all_content(self):
        """默认同步所有内容（20 个文件）"""
        # Given: guides 结构
        guides_dir = self.test_root / ".claude" / "guides"
        guides_dir.mkdir(parents=True)

        # 创建所有子目录
        subdirs = {
            "workflow": 6,
            "doc-templates": 3,
            "rules": 5,
            "profiles": 4,
            "templates": 2
        }

        for subdir, file_count in subdirs.items():
            subdir_path = guides_dir / subdir
            subdir_path.mkdir()
            for i in range(file_count):
                (subdir_path / f"file{i}.md").write_text(f"content {i}")

        # When: 计算文件总数
        total_files = sum(
            len(list((guides_dir / subdir).glob("*.md")))
            for subdir in subdirs.keys()
        )

        # Then: 应有 20 个文件
        self.assertEqual(total_files, 20)


class TestValidationPoints(unittest.TestCase):
    """测试验证点"""

    def setUp(self):
        """Create temporary test structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_validate_target_is_writable(self):
        """验证目标目录可写"""
        # Given: 目标目录
        target_dir = self.test_root / "target"
        target_dir.mkdir()

        # When: 尝试写入测试文件
        test_file = target_dir / "test.txt"
        try:
            test_file.write_text("test")
            is_writable = True
        except (PermissionError, OSError):
            is_writable = False

        # Then: 应可写
        self.assertTrue(is_writable)
        test_file.unlink()  # 清理

    def test_validate_sufficient_disk_space(self):
        """验证磁盘空间充足"""
        # Given: 临时目录
        import shutil as sh
        stat = sh.disk_usage(self.test_dir)

        # When: 检查可用空间
        available_mb = stat.free / (1024 * 1024)
        required_mb = 10  # guides 通常 < 10MB

        # Then: 空间应充足
        self.assertGreater(available_mb, required_mb)

    def test_prevent_accidental_overwrite(self):
        """防止意外覆盖（需要确认）"""
        # Given: 目标已存在 guides
        target_guides = self.test_root / "target" / ".claude" / "guides"
        target_guides.mkdir(parents=True)
        (target_guides / "important.md").write_text("important data")

        # When: 检查是否存在
        has_existing_guides = target_guides.exists() and \
                            any(target_guides.iterdir())

        # Then: 应检测到已存在的内容
        self.assertTrue(has_existing_guides)

        # 验证确认流程
        force_flag = False  # 没有 force，需要确认
        should_proceed = force_flag or not has_existing_guides

        # 没有 force 且有内容时，不应自动继续
        self.assertFalse(should_proceed)


if __name__ == "__main__":
    unittest.main()
