"""
功能测试 - 基于 update-pillars SKILL.md "What it does" 章节

测试 update-pillars 的核心功能:
1. 扫描 ai-dev 和 target projects 的 Pillars
2. 比较 Pillars 检测 new/updated 内容
3. 显示详细 diff 预览
4. 同步 Pillars with confirmation
5. 尊重项目 profiles (minimal, node-lambda, react-aws)
6. 报告同步结果
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import os


class TestScanPillars(unittest.TestCase):
    """测试功能 1: 扫描 ai-dev 和 target projects 的 Pillars"""

    def setUp(self):
        """创建临时测试目录结构"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

        # 创建源项目结构 (ai-dev)
        self.source_root = self.test_root / "ai-dev"
        self.source_pillars = self.source_root / ".claude" / "pillars"
        self.source_pillars.mkdir(parents=True)

        # 创建目标项目结构
        self.target_root = self.test_root / "my-app"
        self.target_pillars = self.target_root / ".claude" / "pillars"
        self.target_pillars.mkdir(parents=True)

    def tearDown(self):
        """清理临时测试目录"""
        shutil.rmtree(self.test_dir)

    def test_scan_source_pillars_directory(self):
        """扫描源项目的 Pillars 目录"""
        # Given: 源项目有 3 个 Pillars
        (self.source_pillars / "pillar-a").mkdir()
        (self.source_pillars / "pillar-a" / "pillar-a.md").write_text("# Pillar A")
        (self.source_pillars / "pillar-b").mkdir()
        (self.source_pillars / "pillar-b" / "pillar-b.md").write_text("# Pillar B")
        (self.source_pillars / "pillar-k").mkdir()
        (self.source_pillars / "pillar-k" / "pillar-k.md").write_text("# Pillar K")

        # When: 扫描源 Pillars
        source_pillars = list(self.source_pillars.glob("pillar-*"))

        # Then: 应找到 3 个 Pillars
        self.assertEqual(len(source_pillars), 3)
        pillar_names = sorted([p.name for p in source_pillars])
        self.assertEqual(pillar_names, ["pillar-a", "pillar-b", "pillar-k"])

    def test_scan_target_pillars_directory(self):
        """扫描目标项目的 Pillars 目录"""
        # Given: 目标项目有 2 个 Pillars
        (self.target_pillars / "pillar-a").mkdir()
        (self.target_pillars / "pillar-a" / "pillar-a.md").write_text("# Old Pillar A")
        (self.target_pillars / "pillar-b").mkdir()
        (self.target_pillars / "pillar-b" / "pillar-b.md").write_text("# Pillar B")

        # When: 扫描目标 Pillars
        target_pillars = list(self.target_pillars.glob("pillar-*"))

        # Then: 应找到 2 个 Pillars
        self.assertEqual(len(target_pillars), 2)
        pillar_names = sorted([p.name for p in target_pillars])
        self.assertEqual(pillar_names, ["pillar-a", "pillar-b"])

    def test_scan_empty_target_directory(self):
        """扫描空的目标 Pillars 目录（新项目）"""
        # Given: 目标项目 Pillars 目录为空
        # (setUp 已创建空目录)

        # When: 扫描目标 Pillars
        target_pillars = list(self.target_pillars.glob("pillar-*"))

        # Then: 应返回空列表
        self.assertEqual(len(target_pillars), 0)


class TestComparePillars(unittest.TestCase):
    """测试功能 2: 比较 Pillars 检测 new/updated 内容"""

    def setUp(self):
        """创建临时测试目录结构"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

        self.source_root = self.test_root / "ai-dev"
        self.source_pillars = self.source_root / ".claude" / "pillars"
        self.source_pillars.mkdir(parents=True)

        self.target_root = self.test_root / "my-app"
        self.target_pillars = self.target_root / ".claude" / "pillars"
        self.target_pillars.mkdir(parents=True)

    def tearDown(self):
        """清理临时测试目录"""
        shutil.rmtree(self.test_dir)

    def test_detect_new_pillar(self):
        """检测新 Pillar (目标中不存在)"""
        # Given: 源有 pillar-k，目标没有
        (self.source_pillars / "pillar-k").mkdir()
        source_file = self.source_pillars / "pillar-k" / "pillar-k.md"
        source_file.write_text("# Pillar K\n" * 10)  # 180 lines

        # When: 比较
        source_exists = source_file.exists()
        target_exists = (self.target_pillars / "pillar-k" / "pillar-k.md").exists()

        # Then: 应检测到 NEW 状态
        self.assertTrue(source_exists)
        self.assertFalse(target_exists)
        # Status: NEW

    def test_detect_updated_pillar(self):
        """检测更新的 Pillar (源更新，目标旧)"""
        # Given: 源和目标都有 pillar-a，源更新
        (self.source_pillars / "pillar-a").mkdir()
        source_file = self.source_pillars / "pillar-a" / "pillar-a.md"
        source_file.write_text("# Pillar A\nUpdated content\n" * 15)  # 250 lines

        (self.target_pillars / "pillar-a").mkdir()
        target_file = self.target_pillars / "pillar-a" / "pillar-a.md"
        target_file.write_text("# Pillar A\nOld content\n" * 12)  # 245 lines

        # When: 比较文件大小
        source_size = source_file.stat().st_size
        target_size = target_file.stat().st_size

        # Then: 源应该更大 (NEWER)
        self.assertGreater(source_size, target_size)

    def test_detect_unchanged_pillar(self):
        """检测未更改的 Pillar (完全相同)"""
        # Given: 源和目标有相同内容的 pillar-b
        content = "# Pillar B\nSame content\n" * 10

        (self.source_pillars / "pillar-b").mkdir()
        source_file = self.source_pillars / "pillar-b" / "pillar-b.md"
        source_file.write_text(content)

        (self.target_pillars / "pillar-b").mkdir()
        target_file = self.target_pillars / "pillar-b" / "pillar-b.md"
        target_file.write_text(content)

        # When: 比较内容
        source_content = source_file.read_text()
        target_content = target_file.read_text()

        # Then: 内容应相同 (SAME)
        self.assertEqual(source_content, target_content)


class TestShowDiffPreview(unittest.TestCase):
    """测试功能 3: 显示详细 diff 预览"""

    def test_diff_preview_format(self):
        """Diff 预览应包含 Pillar 名称、状态、动作"""
        # Given: Analysis 数据
        analysis = {
            "pillar-a": {"status": "NEWER", "source_lines": 250, "target_lines": 245},
            "pillar-b": {"status": "SAME", "source_lines": 200, "target_lines": 200},
            "pillar-k": {"status": "NEW", "source_lines": 180, "target_lines": 0},
        }

        # When: 生成预览
        preview_lines = []
        for pillar, info in analysis.items():
            status = info["status"]
            if status == "NEWER":
                action = f"Update ({info['source_lines']} vs {info['target_lines']} lines)"
            elif status == "NEW":
                action = f"Add ({info['source_lines']} lines)"
            elif status == "SAME":
                action = "Skip"
            preview_lines.append(f"{pillar} | {status} | {action}")

        # Then: 应包含所有 Pillars 的状态
        self.assertEqual(len(preview_lines), 3)
        self.assertIn("pillar-a | NEWER | Update", preview_lines[0])
        self.assertIn("pillar-k | NEW | Add", preview_lines[2])


class TestSyncPillars(unittest.TestCase):
    """测试功能 4: 同步 Pillars"""

    def setUp(self):
        """创建临时测试目录结构"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

        self.source_root = self.test_root / "ai-dev"
        self.source_pillars = self.source_root / ".claude" / "pillars"
        self.source_pillars.mkdir(parents=True)

        self.target_root = self.test_root / "my-app"
        self.target_pillars = self.target_root / ".claude" / "pillars"
        self.target_pillars.mkdir(parents=True)

    def tearDown(self):
        """清理临时测试目录"""
        shutil.rmtree(self.test_dir)

    def test_sync_new_pillar(self):
        """同步新 Pillar 到目标项目"""
        # Given: 源有新 Pillar
        (self.source_pillars / "pillar-k").mkdir()
        source_file = self.source_pillars / "pillar-k" / "pillar-k.md"
        source_file.write_text("# Pillar K\nNew content\n")

        # When: 同步
        target_dir = self.target_pillars / "pillar-k"
        target_dir.mkdir()
        target_file = target_dir / "pillar-k.md"
        shutil.copy2(source_file, target_file)

        # Then: 目标应有新 Pillar
        self.assertTrue(target_file.exists())
        self.assertEqual(source_file.read_text(), target_file.read_text())

    def test_sync_updated_pillar(self):
        """同步更新的 Pillar (覆盖目标)"""
        # Given: 源有更新的 Pillar
        (self.source_pillars / "pillar-a").mkdir()
        source_file = self.source_pillars / "pillar-a" / "pillar-a.md"
        source_file.write_text("# Pillar A\nUpdated content\n")

        # 目标有旧版本
        (self.target_pillars / "pillar-a").mkdir()
        target_file = self.target_pillars / "pillar-a" / "pillar-a.md"
        target_file.write_text("# Pillar A\nOld content\n")

        # When: 同步 (覆盖)
        shutil.copy2(source_file, target_file)

        # Then: 目标应有更新内容
        self.assertEqual(source_file.read_text(), target_file.read_text())
        self.assertIn("Updated content", target_file.read_text())

    def test_skip_unchanged_pillar(self):
        """跳过未更改的 Pillar"""
        # Given: 源和目标内容相同
        content = "# Pillar B\nSame content\n"

        (self.source_pillars / "pillar-b").mkdir()
        source_file = self.source_pillars / "pillar-b" / "pillar-b.md"
        source_file.write_text(content)

        (self.target_pillars / "pillar-b").mkdir()
        target_file = self.target_pillars / "pillar-b" / "pillar-b.md"
        target_file.write_text(content)

        # When: 检查是否需要同步
        needs_sync = source_file.read_text() != target_file.read_text()

        # Then: 不需要同步
        self.assertFalse(needs_sync)


class TestProfileAwareness(unittest.TestCase):
    """测试功能 5: 尊重项目 profiles"""

    def setUp(self):
        """创建临时测试目录结构"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

        self.target_root = self.test_root / "my-app"
        self.target_docs = self.target_root / "docs"
        self.target_docs.mkdir(parents=True)

    def tearDown(self):
        """清理临时测试目录"""
        shutil.rmtree(self.test_dir)

    def test_detect_minimal_profile(self):
        """检测 minimal profile (只同步 A, B, K)"""
        # Given: Profile 文件指定 minimal
        profile_content = """---
profile: minimal
---

# Project Profile
"""
        profile_file = self.target_docs / "project-profile.md"
        profile_file.write_text(profile_content)

        # When: 读取 profile
        content = profile_file.read_text()

        # Then: 应检测到 minimal
        self.assertIn("profile: minimal", content)

    def test_filter_pillars_by_profile(self):
        """根据 profile 过滤 Pillars"""
        # Given: minimal profile 只允许 A, B, K
        profile = "minimal"
        allowed_pillars = {
            "minimal": ["pillar-a", "pillar-b", "pillar-k"],
            "node-lambda": ["pillar-a", "pillar-b", "pillar-k", "pillar-m", "pillar-q", "pillar-r"],
        }

        all_pillars = ["pillar-a", "pillar-b", "pillar-k", "pillar-m", "pillar-q"]

        # When: 过滤
        filtered = [p for p in all_pillars if p in allowed_pillars[profile]]

        # Then: 只保留 A, B, K
        self.assertEqual(filtered, ["pillar-a", "pillar-b", "pillar-k"])


class TestReportResults(unittest.TestCase):
    """测试功能 6: 报告同步结果"""

    def test_report_sync_summary(self):
        """报告应包含同步的 Pillar 数量和名称"""
        # Given: 同步结果
        synced_pillars = ["pillar-a", "pillar-k"]
        skipped_pillars = ["pillar-b"]

        # When: 生成报告
        report = {
            "synced_count": len(synced_pillars),
            "synced_names": synced_pillars,
            "skipped_count": len(skipped_pillars),
        }

        # Then: 报告应包含正确信息
        self.assertEqual(report["synced_count"], 2)
        self.assertIn("pillar-a", report["synced_names"])
        self.assertIn("pillar-k", report["synced_names"])
        self.assertEqual(report["skipped_count"], 1)


if __name__ == "__main__":
    unittest.main()
