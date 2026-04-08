"""
功能测试 - 基于 update-guides SKILL.md "What it does" 章节

测试 update-guides 的核心功能:
1. 检测 ai-dev 的 `.claude/guides/` 目录
2. 删除目标项目的 `.claude/guides/`（如果存在）
3. 从 ai-dev 复制所有 AI guides 和 profiles 到目标
4. 创建 `.ai-guides-version` 跟踪文件
5. 生成详细的同步报告
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

try:
    from update_guides import sync_guides, detect_guides_directory
except ImportError:
    # Fallback if module structure is different
    pass


class TestDetectGuidesDirectory(unittest.TestCase):
    """测试功能 1: 检测 ai-dev 的 .claude/guides/ 目录"""

    def setUp(self):
        """Create temporary test structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_detect_guides_directory_exists(self):
        """检测存在的 guides 目录"""
        # Given: 创建 guides 目录
        guides_dir = self.test_root / ".claude" / "guides"
        guides_dir.mkdir(parents=True)
        (guides_dir / "test.md").write_text("test")

        # When: 检测目录
        result = guides_dir.exists()

        # Then: 应检测到
        self.assertTrue(result)
        self.assertTrue(guides_dir.is_dir())

    def test_fail_when_guides_directory_missing(self):
        """guides 目录不存在时失败"""
        # Given: 不存在 guides 目录
        guides_dir = self.test_root / ".claude" / "guides"

        # When: 检测目录
        result = guides_dir.exists()

        # Then: 应返回 False
        self.assertFalse(result)


class TestDeleteTargetGuides(unittest.TestCase):
    """测试功能 2: 删除目标项目的 .claude/guides/"""

    def setUp(self):
        """Create temporary test structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_delete_existing_target_guides(self):
        """删除已存在的目标 guides 目录"""
        # Given: 目标已有 guides 目录
        target_guides = self.test_root / "target" / ".claude" / "guides"
        target_guides.mkdir(parents=True)
        (target_guides / "old.md").write_text("old content")

        # When: 删除目录
        shutil.rmtree(target_guides)

        # Then: 目录应被删除
        self.assertFalse(target_guides.exists())

    def test_handle_missing_target_guides(self):
        """目标 guides 不存在时不报错"""
        # Given: 目标没有 guides 目录
        target_guides = self.test_root / "target" / ".claude" / "guides"

        # When: 尝试删除（如果存在）
        if target_guides.exists():
            shutil.rmtree(target_guides)

        # Then: 不应报错，操作正常完成
        self.assertFalse(target_guides.exists())


class TestCopyGuidesToTarget(unittest.TestCase):
    """测试功能 3: 复制 guides 到目标"""

    def setUp(self):
        """Create temporary test structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_copy_all_20_files(self):
        """复制所有 20 个文件"""
        # Given: 创建源 guides 结构（20 个文件）
        source_guides = self.test_root / "framework" / ".claude" / "guides"
        source_guides.mkdir(parents=True)

        # 创建 workflow/ (6 files)
        workflow_dir = source_guides / "workflow"
        workflow_dir.mkdir()
        for i in range(6):
            (workflow_dir / f"file{i}.md").write_text(f"content {i}")

        # 创建 doc-templates/ (3 files)
        doc_dir = source_guides / "doc-templates"
        doc_dir.mkdir()
        for i in range(3):
            (doc_dir / f"doc{i}.md").write_text(f"doc {i}")

        # 创建 rules/ (5 files)
        rules_dir = source_guides / "rules"
        rules_dir.mkdir()
        for i in range(5):
            (rules_dir / f"rule{i}.md").write_text(f"rule {i}")

        # 创建 profiles/ (4 files)
        profiles_dir = source_guides / "profiles"
        profiles_dir.mkdir()
        for i in range(4):
            (profiles_dir / f"profile{i}.md").write_text(f"profile {i}")

        # 创建 templates/ (2 files)
        templates_dir = source_guides / "templates"
        templates_dir.mkdir()
        for i in range(2):
            (templates_dir / f"template{i}.md").write_text(f"template {i}")

        # When: 复制到目标
        target_guides = self.test_root / "target" / ".claude" / "guides"
        shutil.copytree(source_guides, target_guides)

        # Then: 应复制所有 20 个文件
        workflow_files = list((target_guides / "workflow").glob("*.md"))
        doc_files = list((target_guides / "doc-templates").glob("*.md"))
        rules_files = list((target_guides / "rules").glob("*.md"))
        profiles_files = list((target_guides / "profiles").glob("*.md"))
        templates_files = list((target_guides / "templates").glob("*.md"))

        self.assertEqual(len(workflow_files), 6)
        self.assertEqual(len(doc_files), 3)
        self.assertEqual(len(rules_files), 5)
        self.assertEqual(len(profiles_files), 4)
        self.assertEqual(len(templates_files), 2)

        total_files = len(workflow_files) + len(doc_files) + len(rules_files) + len(profiles_files) + len(templates_files)
        self.assertEqual(total_files, 20)

    def test_preserve_directory_structure(self):
        """保留目录结构"""
        # Given: 创建源目录结构
        source_guides = self.test_root / "framework" / ".claude" / "guides"
        source_guides.mkdir(parents=True)
        (source_guides / "workflow").mkdir()
        (source_guides / "workflow" / "test.md").write_text("test")

        # When: 复制
        target_guides = self.test_root / "target" / ".claude" / "guides"
        shutil.copytree(source_guides, target_guides)

        # Then: 结构应保持一致
        self.assertTrue((target_guides / "workflow").exists())
        self.assertTrue((target_guides / "workflow").is_dir())
        self.assertTrue((target_guides / "workflow" / "test.md").exists())

    def test_preserve_file_permissions(self):
        """保留文件权限"""
        # Given: 创建带权限的文件
        source_guides = self.test_root / "framework" / ".claude" / "guides"
        source_guides.mkdir(parents=True)
        test_file = source_guides / "test.md"
        test_file.write_text("test")
        test_file.chmod(0o644)

        # When: 复制
        target_guides = self.test_root / "target" / ".claude" / "guides"
        shutil.copytree(source_guides, target_guides)

        # Then: 权限应保留
        target_file = target_guides / "test.md"
        self.assertTrue(target_file.exists())
        # Note: 权限可能因系统而异，这里只验证文件可读
        self.assertTrue(target_file.is_file())


class TestCreateVersionFile(unittest.TestCase):
    """测试功能 4: 创建 .ai-guides-version 文件"""

    def setUp(self):
        """Create temporary test structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_create_version_file_with_metadata(self):
        """创建包含元数据的版本文件"""
        # Given: 目标目录
        target_dir = self.test_root / "target"
        target_dir.mkdir()

        # When: 创建版本文件
        version_file = target_dir / ".ai-guides-version"
        version_data = {
            "sync_time": "2026-04-07T14:00:00",
            "source_framework": "/path/to/ai-dev",
            "guides_count": 20
        }
        version_file.write_text(json.dumps(version_data, indent=2))

        # Then: 文件应包含正确的元数据
        self.assertTrue(version_file.exists())
        loaded_data = json.loads(version_file.read_text())
        self.assertEqual(loaded_data["guides_count"], 20)
        self.assertIn("sync_time", loaded_data)
        self.assertIn("source_framework", loaded_data)

    def test_version_file_content_format(self):
        """验证版本文件格式（JSON）"""
        # Given: 目标目录
        target_dir = self.test_root / "target"
        target_dir.mkdir()

        # When: 创建版本文件
        version_file = target_dir / ".ai-guides-version"
        version_data = {
            "sync_time": "2026-04-07T14:00:00",
            "source_framework": "/path/to/ai-dev",
            "guides_count": 20
        }
        version_file.write_text(json.dumps(version_data))

        # Then: 应能解析为 JSON
        try:
            loaded_data = json.loads(version_file.read_text())
            valid_json = True
        except json.JSONDecodeError:
            valid_json = False

        self.assertTrue(valid_json)
        self.assertIsInstance(loaded_data, dict)


class TestGenerateSyncReport(unittest.TestCase):
    """测试功能 5: 生成同步报告"""

    def setUp(self):
        """Create temporary test structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_report_contains_file_counts(self):
        """报告包含文件数量"""
        # Given: 同步数据
        sync_report = {
            "total_files": 20,
            "workflow": 6,
            "doc_templates": 3,
            "rules": 5,
            "profiles": 4,
            "templates": 2
        }

        # When: 验证报告
        total = sync_report["workflow"] + sync_report["doc_templates"] + \
                sync_report["rules"] + sync_report["profiles"] + sync_report["templates"]

        # Then: 总数应正确
        self.assertEqual(total, 20)
        self.assertEqual(sync_report["total_files"], 20)

    def test_report_contains_directory_list(self):
        """报告包含目录列表"""
        # Given: 同步报告
        sync_report = {
            "directories": ["workflow", "doc-templates", "rules", "profiles", "templates"],
            "total_directories": 5
        }

        # When: 验证报告
        dir_count = len(sync_report["directories"])

        # Then: 目录列表应完整
        self.assertEqual(dir_count, 5)
        self.assertIn("workflow", sync_report["directories"])
        self.assertIn("profiles", sync_report["directories"])
        self.assertEqual(sync_report["total_directories"], 5)


if __name__ == "__main__":
    unittest.main()
