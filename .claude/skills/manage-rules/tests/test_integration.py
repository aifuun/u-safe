"""
集成测试 - 基于 manage-rules SKILL.md Usage Examples 章节

端到端测试场景:
1. Example 1: 基础使用（auto-detect profile, instant mode）
2. Example 2: 预览模式（--dry-run）
3. Example 3: Profile 覆盖（--profile tauri）
4. Example 4: 项目初始化后（/init-docs → /manage-rules）
5. Example 5: Framework 同步后（/update-framework → /manage-rules）
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_rules import RuleGenerator


class TestExample1BasicUsage(unittest.TestCase):
    """Example 1: 基础使用（auto-detect profile, instant mode）"""

    def setUp(self):
        """Create complete test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

        # 创建完整结构
        (self.test_root / "docs").mkdir()
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core").mkdir(parents=True)
        (self.test_root / ".claude" / "profiles").mkdir(parents=True)

        # 创建 profile
        profile_content = """---
profile: tauri
type: desktop-app
---
"""
        with open(self.test_root / "docs" / "project-profile.md", 'w') as f:
            f.write(profile_content)

        # 创建 profile config
        config = {
            "rules": {
                "include": ["core/*"],
                "exclude": []
            }
        }
        with open(self.test_root / ".claude" / "profiles" / "tauri.json", 'w') as f:
            json.dump(config, f)

        # 创建模板
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core" / "naming.md").write_text("# Naming")

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)

    def test_end_to_end_basic_workflow(self):
        """端到端基础工作流"""
        # Given: 完整的项目结构（setUp 已创建）
        generator = RuleGenerator()
        generator.project_root = self.test_root

        # When: 执行完整流程
        # Step 1: Auto-detect profile
        profile = generator.detect_profile()
        self.assertEqual(profile, "tauri")

        # Step 2: Load config
        config = generator.load_profile_config(profile)
        self.assertIn("rules", config)

        # Step 3: Filter templates
        templates = generator.filter_templates(config)
        self.assertGreater(len(templates), 0)

        # Step 4: Filter framework-only
        filtered = generator.filter_framework_only_skills(templates)
        self.assertGreater(len(filtered), 0)

        # Step 5: Generate rules
        count = generator.generate_rules(filtered, dry_run=False)
        self.assertEqual(count, 1)

        # Then: 验证生成结果
        rules_file = self.test_root / ".claude" / "rules" / "core" / "naming.md"
        self.assertTrue(rules_file.exists())


class TestExample2DryRun(unittest.TestCase):
    """Example 2: 预览模式（--dry-run）"""

    def setUp(self):
        """Create test project"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core").mkdir(parents=True)
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "architecture").mkdir(parents=True)

        # 创建多个模板
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core" / "naming.md").write_text("# Naming")
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "architecture" / "clean.md").write_text("# Clean")

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)

    def test_dry_run_preview_without_changes(self):
        """dry-run 模式预览但不修改"""
        # Given: 模板文件
        templates_dir = self.test_root / ".claude" / "guides" / "rules" / "templates"
        templates = list(templates_dir.rglob("*.md"))

        # When: dry-run 模式
        generator = RuleGenerator()
        generator.project_root = self.test_root
        count = generator.generate_rules(templates, dry_run=True)

        # Then: 返回计数但不生成文件
        self.assertEqual(count, 2)

        rules_dir = self.test_root / ".claude" / "rules"
        if rules_dir.exists():
            generated = list(rules_dir.rglob("*.md"))
            self.assertEqual(len(generated), 0)


class TestExample3ProfileOverride(unittest.TestCase):
    """Example 3: Profile 覆盖（--profile tauri）"""

    def setUp(self):
        """Create test project with different profile"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

        (self.test_root / "docs").mkdir()
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core").mkdir(parents=True)
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "languages").mkdir(parents=True)
        (self.test_root / ".claude" / "profiles").mkdir(parents=True)

        # Profile 是 nextjs-aws
        profile_content = """---
profile: nextjs-aws
---
"""
        with open(self.test_root / "docs" / "project-profile.md", 'w') as f:
            f.write(profile_content)

        # 但我们要用 tauri config 覆盖
        tauri_config = {
            "rules": {
                "include": ["core/*", "languages/typescript.md"],
                "exclude": []
            }
        }
        with open(self.test_root / ".claude" / "profiles" / "tauri.json", 'w') as f:
            json.dump(tauri_config, f)

        # 创建模板
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core" / "naming.md").write_text("# Naming")
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "languages" / "typescript.md").write_text("# TS")

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)

    def test_profile_override_uses_specified_config(self):
        """profile 覆盖使用指定的配置"""
        # Given: 项目 profile 是 nextjs-aws
        generator = RuleGenerator()
        generator.project_root = self.test_root

        detected = generator.detect_profile()
        self.assertEqual(detected, "nextjs-aws")

        # When: 使用 tauri profile 覆盖
        override_profile = "tauri"
        config = generator.load_profile_config(override_profile)

        # Then: 应使用 tauri 配置
        self.assertIn("core/*", config["rules"]["include"])
        self.assertIn("languages/typescript.md", config["rules"]["include"])


class TestExample4AfterInitDocs(unittest.TestCase):
    """Example 4: 项目初始化后（/init-docs → /manage-rules）"""

    def setUp(self):
        """Simulate after /init-docs"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

        # /init-docs 已创建的结构
        (self.test_root / "docs").mkdir()
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core").mkdir(parents=True)
        (self.test_root / ".claude" / "profiles").mkdir(parents=True)

        # Profile 已配置
        profile_content = """---
profile: minimal
---
"""
        with open(self.test_root / "docs" / "project-profile.md", 'w') as f:
            f.write(profile_content)

        # Profile config
        config = {
            "rules": {
                "include": ["core/naming.md"],
                "exclude": []
            }
        }
        with open(self.test_root / ".claude" / "profiles" / "minimal.json", 'w') as f:
            json.dump(config, f)

        # 模板已存在
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core" / "naming.md").write_text("# Naming")

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)

    def test_after_init_docs_workflow(self):
        """init-docs 后的工作流"""
        # Given: /init-docs 已完成（结构已创建）
        generator = RuleGenerator()
        generator.project_root = self.test_root

        # When: /manage-rules 生成规则
        profile = generator.detect_profile()
        config = generator.load_profile_config(profile)
        templates = generator.filter_templates(config)
        filtered = generator.filter_framework_only_skills(templates)
        count = generator.generate_rules(filtered, dry_run=False)

        # Then: 应成功生成
        self.assertGreater(count, 0)
        rules_file = self.test_root / ".claude" / "rules" / "core" / "naming.md"
        self.assertTrue(rules_file.exists())


class TestExample5AfterFrameworkSync(unittest.TestCase):
    """Example 5: Framework 同步后（/update-framework → /manage-rules）"""

    def setUp(self):
        """Simulate after /update-framework"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

        # /update-framework 已同步的结构
        (self.test_root / "docs").mkdir()
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core").mkdir(parents=True)
        (self.test_root / ".claude" / "profiles").mkdir(parents=True)

        # Profile 存在
        profile_content = """---
profile: tauri
---
"""
        with open(self.test_root / "docs" / "project-profile.md", 'w') as f:
            f.write(profile_content)

        # Profile config 已同步
        config = {
            "rules": {
                "include": ["core/*"],
                "exclude": []
            }
        }
        with open(self.test_root / ".claude" / "profiles" / "tauri.json", 'w') as f:
            json.dump(config, f)

        # 模板已同步（可能有新模板）
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core" / "naming.md").write_text("# Naming v2")
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core" / "types.md").write_text("# Types v2")

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)

    def test_after_framework_sync_regeneration(self):
        """framework 同步后重新生成规则"""
        # Given: /update-framework 已完成（新模板已同步）
        generator = RuleGenerator()
        generator.project_root = self.test_root

        # When: /manage-rules 重新生成
        profile = generator.detect_profile()
        config = generator.load_profile_config(profile)
        templates = generator.filter_templates(config)
        filtered = generator.filter_framework_only_skills(templates)
        count = generator.generate_rules(filtered, dry_run=False)

        # Then: 应生成所有新模板
        self.assertEqual(count, 2)

        naming_file = self.test_root / ".claude" / "rules" / "core" / "naming.md"
        types_file = self.test_root / ".claude" / "rules" / "core" / "types.md"
        self.assertTrue(naming_file.exists())
        self.assertTrue(types_file.exists())

        # 验证内容已更新
        self.assertIn("v2", naming_file.read_text())


if __name__ == "__main__":
    unittest.main()
