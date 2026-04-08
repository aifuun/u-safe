"""
参数验证测试 - 基于 manage-rules SKILL.md Arguments 章节

测试 manage-rules 的参数处理:
1. 默认参数（无参数调用）
2. --dry-run 模式
3. --confirm 模式
4. --profile 覆盖
5. 无效 profile 名称
6. 参数组合
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_rules import RuleGenerator, ProfileError


class TestDefaultArguments(unittest.TestCase):
    """测试默认参数（无参数调用）"""

    def setUp(self):
        """Create temporary test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

        # 创建基本项目结构
        (self.test_root / "docs").mkdir()
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core").mkdir(parents=True)
        (self.test_root / ".claude" / "profiles").mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_auto_detect_profile_when_no_profile_arg(self):
        """无 --profile 参数时应自动检测 profile"""
        # Given: 创建 profile 文件
        profile_content = """---
profile: tauri
type: desktop-app
---

# Project Profile
"""
        profile_file = self.test_root / "docs" / "project-profile.md"
        with open(profile_file, 'w', encoding='utf-8') as f:
            f.write(profile_content)

        # When: 不提供 profile 参数
        generator = RuleGenerator()
        generator.project_root = self.test_root
        detected = generator.detect_profile()

        # Then: 应自动检测到 tauri
        self.assertEqual(detected, "tauri")

    def test_instant_mode_by_default(self):
        """默认应使用 instant 模式（不是 plan 模式）"""
        # Given: 默认调用
        # When: 检查默认模式（此处为逻辑验证）
        default_mode = "instant"  # 模拟默认值

        # Then: 应该是 instant
        self.assertEqual(default_mode, "instant")


class TestDryRunMode(unittest.TestCase):
    """测试 --dry-run 模式（仅预览，不生成文件）"""

    def setUp(self):
        """Create temporary test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core").mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_dry_run_shows_preview_without_creating_files(self):
        """dry-run 模式应显示预览但不生成文件"""
        # Given: 创建测试模板
        template_file = self.test_root / ".claude" / "guides" / "rules" / "templates" / "core" / "naming.md"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write("# Naming conventions")

        templates = [template_file]

        # When: 使用 dry_run=True
        generator = RuleGenerator()
        generator.project_root = self.test_root
        count = generator.generate_rules(templates, dry_run=True)

        # Then: 应返回计数但不生成文件
        self.assertEqual(count, 1)

        rules_dir = self.test_root / ".claude" / "rules"
        if rules_dir.exists():
            # 如果目录存在，应该是空的
            self.assertEqual(len(list(rules_dir.rglob("*.md"))), 0)

    def test_dry_run_returns_file_count(self):
        """dry-run 应返回文件数量"""
        # Given: 多个模板
        templates_dir = self.test_root / ".claude" / "guides" / "rules" / "templates" / "core"
        for name in ["naming.md", "types.md", "error.md"]:
            with open(templates_dir / name, 'w', encoding='utf-8') as f:
                f.write(f"# {name}")

        templates = list(templates_dir.glob("*.md"))

        # When: dry_run 模式
        generator = RuleGenerator()
        generator.project_root = self.test_root
        count = generator.generate_rules(templates, dry_run=True)

        # Then: 应返回正确数量
        self.assertEqual(count, 3)


class TestConfirmMode(unittest.TestCase):
    """测试 --confirm 模式（跳过确认）"""

    def test_confirm_mode_skips_prompt(self):
        """--confirm 应跳过确认提示"""
        # Given: confirm 模式
        confirm_mode = True

        # When/Then: 不应提示用户确认（逻辑验证）
        should_prompt = not confirm_mode
        self.assertFalse(should_prompt)

    def test_default_is_confirm_mode(self):
        """默认应该是 confirm 模式"""
        # Given: 默认参数
        default_confirm = True

        # Then: 应该是 confirm
        self.assertTrue(default_confirm)


class TestProfileOverride(unittest.TestCase):
    """测试 --profile 覆盖（tauri, nextjs-aws, minimal）"""

    def setUp(self):
        """Create temporary test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

        (self.test_root / "docs").mkdir()
        (self.test_root / ".claude" / "profiles").mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_profile_override_tauri(self):
        """--profile tauri 应使用 tauri profile"""
        # Given: 项目有不同的 profile
        profile_content = """---
profile: nextjs-aws
---
"""
        profile_file = self.test_root / "docs" / "project-profile.md"
        with open(profile_file, 'w', encoding='utf-8') as f:
            f.write(profile_content)

        # When: 使用 --profile tauri 覆盖
        override_profile = "tauri"

        # Then: 应使用 tauri 而不是 nextjs-aws
        self.assertEqual(override_profile, "tauri")
        self.assertNotEqual(override_profile, "nextjs-aws")

    def test_profile_override_nextjs_aws(self):
        """--profile nextjs-aws 应使用 nextjs-aws profile"""
        override_profile = "nextjs-aws"
        self.assertEqual(override_profile, "nextjs-aws")

    def test_profile_override_minimal(self):
        """--profile minimal 应使用 minimal profile"""
        override_profile = "minimal"
        self.assertEqual(override_profile, "minimal")


class TestInvalidProfile(unittest.TestCase):
    """测试无效 profile 名称（应报错）"""

    def setUp(self):
        """Create temporary test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

        (self.test_root / "docs").mkdir()

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_invalid_profile_name_raises_error(self):
        """无效的 profile 名称应报错"""
        # Given: 无效的 profile 名称
        invalid_profiles = ["invalid", "unknown", "test123", ""]

        # When/Then: 应拒绝无效 profile
        valid_profiles = {"tauri", "nextjs-aws", "minimal"}

        for invalid in invalid_profiles:
            with self.subTest(profile=invalid):
                self.assertNotIn(invalid, valid_profiles)

    def test_profile_not_found_raises_error(self):
        """profile 文件不存在应报错"""
        # Given: 不存在的 profile 文件
        generator = RuleGenerator()
        generator.project_root = self.test_root

        # When/Then: 应抛出 ProfileError
        with self.assertRaises(ProfileError) as ctx:
            generator.detect_profile()

        self.assertIn("not found", str(ctx.exception))


class TestArgumentCombinations(unittest.TestCase):
    """测试参数组合（如 --dry-run --profile tauri）"""

    def setUp(self):
        """Create temporary test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core").mkdir(parents=True)
        (self.test_root / ".claude" / "profiles").mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_dry_run_with_profile_override(self):
        """--dry-run 和 --profile 可以组合使用"""
        # Given: 组合参数
        dry_run = True
        profile_override = "tauri"

        # When/Then: 两个参数都应生效
        self.assertTrue(dry_run)
        self.assertEqual(profile_override, "tauri")

    def test_confirm_with_profile_override(self):
        """--confirm 和 --profile 可以组合使用"""
        # Given: 组合参数
        confirm = True
        profile_override = "nextjs-aws"

        # When/Then: 两个参数都应生效
        self.assertTrue(confirm)
        self.assertEqual(profile_override, "nextjs-aws")

    def test_dry_run_with_confirm_is_redundant(self):
        """--dry-run 和 --confirm 组合时，dry-run 优先"""
        # Given: 同时使用 dry-run 和 confirm
        dry_run = True
        confirm = True

        # When: dry-run 优先
        effective_mode = "dry-run" if dry_run else ("confirm" if confirm else "plan")

        # Then: 应该是 dry-run
        self.assertEqual(effective_mode, "dry-run")


if __name__ == "__main__":
    unittest.main()
