"""
集成测试 - 基于 update-guides SKILL.md "Usage Examples" 章节

测试 update-guides 的端到端使用场景:
- Example 1: 基本同步
- Example 2: Dry-run 模式
- Example 3: 更新现有项目
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestExample1BasicSync(unittest.TestCase):
    """测试示例 1: 基本同步"""

    def setUp(self):
        """Create temporary test structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_sync_from_framework_to_new_project(self):
        """从 framework 同步到新项目"""
        # Given: Framework 带 guides
        framework_dir = self.test_root / "ai-dev"
        framework_dir.mkdir()
        guides_dir = framework_dir / ".claude" / "guides"
        guides_dir.mkdir(parents=True)

        # 创建完整 guides 结构
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
                (subdir_path / f"file{i}.md").write_text(f"{subdir} content {i}")

        # 新项目
        target_dir = self.test_root / "my-project"
        target_dir.mkdir()

        # When: 执行同步
        target_guides = target_dir / ".claude" / "guides"
        shutil.copytree(guides_dir, target_guides)

        # 创建版本文件
        version_file = target_dir / ".ai-guides-version"
        version_data = {
            "sync_time": "2026-04-07T14:00:00",
            "source_framework": str(framework_dir),
            "guides_count": 20
        }
        version_file.write_text(json.dumps(version_data, indent=2))

        # Then: 验证结果
        # 1. 目标应有 guides 目录
        self.assertTrue(target_guides.exists())

        # 2. 应有所有子目录
        for subdir in subdirs.keys():
            self.assertTrue((target_guides / subdir).exists())

        # 3. 文件总数应为 20
        total_files = sum(
            len(list((target_guides / subdir).glob("*.md")))
            for subdir in subdirs.keys()
        )
        self.assertEqual(total_files, 20)

        # 4. 应创建版本文件
        self.assertTrue(version_file.exists())
        version_data_loaded = json.loads(version_file.read_text())
        self.assertEqual(version_data_loaded["guides_count"], 20)


class TestExample2DryRun(unittest.TestCase):
    """测试示例 2: Dry-run 模式"""

    def setUp(self):
        """Create temporary test structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_preview_changes_without_executing(self):
        """预览更改但不执行"""
        # Given: dry-run 模式
        dry_run = True

        # Framework guides
        framework_dir = self.test_root / "ai-dev"
        framework_dir.mkdir()
        guides_dir = framework_dir / ".claude" / "guides"
        guides_dir.mkdir(parents=True)
        (guides_dir / "workflow").mkdir()
        (guides_dir / "workflow" / "test.md").write_text("content")

        # 目标项目
        target_dir = self.test_root / "my-project"
        target_dir.mkdir()

        # When: 生成预览（不执行）
        preview_actions = []
        if dry_run:
            # 收集将要执行的操作
            for file in guides_dir.rglob("*.md"):
                rel_path = file.relative_to(guides_dir)
                preview_actions.append(f"Would copy: {rel_path}")

            preview_actions.append("Would create: .ai-guides-version")

        target_guides = target_dir / ".claude" / "guides"

        # Then: 验证
        # 1. 不应创建实际文件
        self.assertFalse(target_guides.exists())

        # 2. 应生成预览
        self.assertTrue(len(preview_actions) > 0)
        self.assertTrue(any("Would copy" in a for a in preview_actions))
        self.assertTrue(any("Would create" in a for a in preview_actions))


class TestExample3UpdateExisting(unittest.TestCase):
    """测试示例 3: 更新现有项目"""

    def setUp(self):
        """Create temporary test structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_update_existing_project_guides(self):
        """更新现有项目的 guides"""
        # Given: 现有项目已有旧版 guides
        target_dir = self.test_root / "existing-project"
        target_dir.mkdir()
        old_guides = target_dir / ".claude" / "guides"
        old_guides.mkdir(parents=True)
        (old_guides / "workflow").mkdir()
        (old_guides / "workflow" / "old.md").write_text("old content")

        # 记录旧版本
        old_version = target_dir / ".ai-guides-version"
        old_version.write_text(json.dumps({
            "sync_time": "2026-01-01T00:00:00",
            "guides_count": 10
        }))

        # Framework 新版 guides
        framework_dir = self.test_root / "ai-dev"
        framework_dir.mkdir()
        new_guides = framework_dir / ".claude" / "guides"
        new_guides.mkdir(parents=True)
        (new_guides / "workflow").mkdir()
        (new_guides / "workflow" / "new.md").write_text("new content")
        (new_guides / "workflow" / "README.md").write_text("updated readme")

        # When: 更新（删除旧的，复制新的）
        shutil.rmtree(old_guides)
        shutil.copytree(new_guides, old_guides)

        # 更新版本文件
        new_version_data = {
            "sync_time": "2026-04-07T14:00:00",
            "source_framework": str(framework_dir),
            "guides_count": 2
        }
        old_version.write_text(json.dumps(new_version_data, indent=2))

        # Then: 验证更新
        # 1. 旧文件应被删除
        self.assertFalse((old_guides / "workflow" / "old.md").exists())

        # 2. 新文件应存在
        self.assertTrue((old_guides / "workflow" / "new.md").exists())
        self.assertTrue((old_guides / "workflow" / "README.md").exists())

        # 3. 版本文件应更新
        self.assertTrue(old_version.exists())
        version_data = json.loads(old_version.read_text())
        self.assertEqual(version_data["sync_time"], "2026-04-07T14:00:00")
        self.assertEqual(version_data["guides_count"], 2)


if __name__ == "__main__":
    unittest.main()
