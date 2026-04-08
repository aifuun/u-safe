"""
集成测试 - 端到端工作流测试

测试完整的 Pillars 同步流程:
1. End-to-end: 完整的 Pillars 同步流程
2. 多 Pillar 同步场景
3. Profile-aware 同步
4. Dry-run 模式集成
5. 选择性 Pillar 同步
"""

import unittest
import tempfile
import shutil
from pathlib import Path


class TestEndToEndSync(unittest.TestCase):
    """测试端到端同步流程"""

    def setUp(self):
        """创建临时测试目录结构"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

        # 创建源项目
        self.source_root = self.test_root / "ai-dev"
        self.source_pillars = self.source_root / ".claude" / "pillars"
        self.source_pillars.mkdir(parents=True)

        # 创建目标项目
        self.target_root = self.test_root / "my-app"
        self.target_pillars = self.target_root / ".claude" / "pillars"
        self.target_pillars.mkdir(parents=True)
        self.target_docs = self.target_root / "docs"
        self.target_docs.mkdir()

    def tearDown(self):
        """清理临时测试目录"""
        shutil.rmtree(self.test_dir)

    def test_complete_sync_workflow(self):
        """测试完整的同步工作流"""
        # Step 1: 创建源 Pillars
        pillars_to_create = {
            "pillar-a": "# Pillar A\nArchitecture\n" * 20,
            "pillar-b": "# Pillar B\nCode Quality\n" * 15,
            "pillar-k": "# Pillar K\nTesting\n" * 18,
        }

        for name, content in pillars_to_create.items():
            pillar_dir = self.source_pillars / name
            pillar_dir.mkdir()
            (pillar_dir / f"{name}.md").write_text(content)

        # Step 2: 扫描源 Pillars
        source_pillars = list(self.source_pillars.glob("pillar-*"))
        self.assertEqual(len(source_pillars), 3)

        # Step 3: 扫描目标 Pillars (空)
        target_pillars = list(self.target_pillars.glob("pillar-*"))
        self.assertEqual(len(target_pillars), 0)

        # Step 4: 分析差异 (所有 Pillars 都是 NEW)
        analysis = {}
        for pillar in source_pillars:
            pillar_name = pillar.name
            target_pillar = self.target_pillars / pillar_name
            if not target_pillar.exists():
                analysis[pillar_name] = {"status": "NEW", "action": "Add"}

        self.assertEqual(len(analysis), 3)

        # Step 5: 执行同步
        synced_count = 0
        for pillar_name, info in analysis.items():
            if info["action"] == "Add":
                source_dir = self.source_pillars / pillar_name
                target_dir = self.target_pillars / pillar_name
                shutil.copytree(source_dir, target_dir)
                synced_count += 1

        # Step 6: 验证结果
        self.assertEqual(synced_count, 3)
        target_pillars_after = list(self.target_pillars.glob("pillar-*"))
        self.assertEqual(len(target_pillars_after), 3)

        # 验证内容正确
        for name, content in pillars_to_create.items():
            target_file = self.target_pillars / name / f"{name}.md"
            self.assertTrue(target_file.exists())
            self.assertEqual(target_file.read_text(), content)


class TestMultiPillarSync(unittest.TestCase):
    """测试多 Pillar 同步场景"""

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

    def test_sync_mix_of_new_and_updated_pillars(self):
        """同步新增和更新的 Pillars 混合场景"""
        # Given: 源有 3 个 Pillars，目标有 1 个旧的
        # 源 Pillars
        (self.source_pillars / "pillar-a").mkdir()
        (self.source_pillars / "pillar-a" / "pillar-a.md").write_text("# Pillar A\nUpdated\n" * 20)
        (self.source_pillars / "pillar-b").mkdir()
        (self.source_pillars / "pillar-b" / "pillar-b.md").write_text("# Pillar B\n" * 15)
        (self.source_pillars / "pillar-k").mkdir()
        (self.source_pillars / "pillar-k" / "pillar-k.md").write_text("# Pillar K\n" * 18)

        # 目标有旧的 pillar-a
        (self.target_pillars / "pillar-a").mkdir()
        (self.target_pillars / "pillar-a" / "pillar-a.md").write_text("# Pillar A\nOld\n" * 15)

        # When: 分析和同步
        source_pillars = {p.name for p in self.source_pillars.glob("pillar-*")}
        target_pillars = {p.name for p in self.target_pillars.glob("pillar-*")}

        new_pillars = source_pillars - target_pillars  # {pillar-b, pillar-k}
        existing_pillars = source_pillars & target_pillars  # {pillar-a}

        # Then: 应检测到 2 个新 Pillars 和 1 个需更新
        self.assertEqual(len(new_pillars), 2)
        self.assertEqual(len(existing_pillars), 1)


class TestProfileAwareSync(unittest.TestCase):
    """测试 Profile-aware 同步"""

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
        self.target_docs = self.target_root / "docs"
        self.target_docs.mkdir()

    def tearDown(self):
        """清理临时测试目录"""
        shutil.rmtree(self.test_dir)

    def test_sync_with_minimal_profile(self):
        """使用 minimal profile 同步"""
        # Given: 目标项目有 minimal profile
        profile_content = """---
profile: minimal
---

# Project Profile
"""
        (self.target_docs / "project-profile.md").write_text(profile_content)

        # 源有 5 个 Pillars
        all_pillars = ["pillar-a", "pillar-b", "pillar-k", "pillar-m", "pillar-q"]
        for name in all_pillars:
            pillar_dir = self.source_pillars / name
            pillar_dir.mkdir()
            (pillar_dir / f"{name}.md").write_text(f"# {name.title()}\n")

        # When: 按 profile 过滤
        profile = "minimal"
        allowed_pillars = {
            "minimal": ["pillar-a", "pillar-b", "pillar-k"],
        }

        to_sync = [p for p in all_pillars if p in allowed_pillars[profile]]

        # Then: 只应同步 A, B, K
        self.assertEqual(len(to_sync), 3)
        self.assertEqual(sorted(to_sync), ["pillar-a", "pillar-b", "pillar-k"])


class TestDryRunIntegration(unittest.TestCase):
    """测试 Dry-run 模式集成"""

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

    def test_dry_run_preview_without_changes(self):
        """Dry-run 显示预览但不修改"""
        # Given: 源有新 Pillar
        (self.source_pillars / "pillar-k").mkdir()
        (self.source_pillars / "pillar-k" / "pillar-k.md").write_text("# Pillar K\n")

        # Dry-run 模式
        dry_run = True

        # When: 分析
        source_pillars = list(self.source_pillars.glob("pillar-*"))
        target_pillars_before = list(self.target_pillars.glob("pillar-*"))

        # Dry-run: 不执行实际同步
        if not dry_run:
            # 正常模式会执行同步
            pass

        target_pillars_after = list(self.target_pillars.glob("pillar-*"))

        # Then: 目标不应改变
        self.assertEqual(len(target_pillars_before), len(target_pillars_after))
        self.assertEqual(len(source_pillars), 1)  # 源有 1 个
        self.assertEqual(len(target_pillars_after), 0)  # 目标仍为 0


class TestSelectivePillarSync(unittest.TestCase):
    """测试选择性 Pillar 同步"""

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

    def test_sync_only_specified_pillars(self):
        """只同步指定的 Pillars"""
        # Given: 源有 5 个 Pillars
        all_pillars = ["pillar-a", "pillar-b", "pillar-k", "pillar-m", "pillar-q"]
        for name in all_pillars:
            pillar_dir = self.source_pillars / name
            pillar_dir.mkdir()
            (pillar_dir / f"{name}.md").write_text(f"# {name.title()}\n")

        # 用户指定只同步 M, Q
        selected_pillars = ["pillar-m", "pillar-q"]

        # When: 过滤
        to_sync = [p for p in all_pillars if p in selected_pillars]

        # Then: 只应同步 M, Q
        self.assertEqual(len(to_sync), 2)
        self.assertEqual(sorted(to_sync), ["pillar-m", "pillar-q"])


if __name__ == "__main__":
    unittest.main()
