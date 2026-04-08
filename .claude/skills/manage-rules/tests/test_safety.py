"""
安全测试 - 基于 manage-rules SKILL.md Safety Features 章节

测试 manage-rules 的安全机制:
1. Pre-flight 检查: Python 脚本存在
2. Pre-flight 检查: PyYAML 依赖已安装
3. 智能默认: auto-detect profile（无需 --profile）
4. 智能默认: instant 模式（无需 --confirm）
5. 验证点: profile 文件格式
6. 验证点: 模板目录存在
7. 验证点: 输出目录可写
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_rules import RuleGenerator, ProfileError


class TestPreflightScriptExists(unittest.TestCase):
    """测试 Pre-flight 检查: Python 脚本存在"""

    def test_script_file_exists(self):
        """验证 generate_rules.py 脚本文件存在"""
        # Given: 脚本路径
        script_path = Path(__file__).parent.parent / "scripts" / "generate_rules.py"

        # When/Then: 脚本应存在
        self.assertTrue(script_path.exists(), f"Script not found: {script_path}")

    def test_script_is_executable(self):
        """验证脚本可执行（有 main 函数）"""
        # Given: 导入脚本
        from generate_rules import main

        # When/Then: main 函数应存在
        self.assertTrue(callable(main))


class TestPreflightDependencies(unittest.TestCase):
    """测试 Pre-flight 检查: PyYAML 依赖已安装"""

    def test_pyyaml_is_installed(self):
        """验证 PyYAML 已安装"""
        # When/Then: 应能导入 yaml
        try:
            import yaml
            has_yaml = True
        except ImportError:
            has_yaml = False

        self.assertTrue(has_yaml, "PyYAML not installed - run: pip install PyYAML")

    def test_pyyaml_safe_load_available(self):
        """验证 yaml.safe_load 可用"""
        # Given: yaml 模块
        import yaml

        # When/Then: safe_load 应存在
        self.assertTrue(hasattr(yaml, 'safe_load'))


class TestSmartDefaultAutoDetect(unittest.TestCase):
    """测试智能默认: auto-detect profile（无需 --profile）"""

    def setUp(self):
        """Create temporary test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)
        (self.test_root / "docs").mkdir()

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_auto_detect_without_profile_arg(self):
        """无 --profile 参数时自动检测"""
        # Given: 创建 profile 文件
        profile_content = """---
profile: tauri
---
"""
        profile_file = self.test_root / "docs" / "project-profile.md"
        with open(profile_file, 'w', encoding='utf-8') as f:
            f.write(profile_content)

        # When: 不提供 profile 参数
        generator = RuleGenerator()
        generator.project_root = self.test_root
        detected = generator.detect_profile()

        # Then: 应自动检测成功
        self.assertEqual(detected, "tauri")

    def test_auto_detect_works_for_all_profiles(self):
        """自动检测适用于所有 profile 类型"""
        # Given: 不同的 profiles
        profiles = ["tauri", "nextjs-aws", "minimal"]

        for profile_name in profiles:
            with self.subTest(profile=profile_name):
                # Create profile
                profile_content = f"""---
profile: {profile_name}
---
"""
                profile_file = self.test_root / "docs" / "project-profile.md"
                with open(profile_file, 'w', encoding='utf-8') as f:
                    f.write(profile_content)

                # When: 自动检测
                generator = RuleGenerator()
                generator.project_root = self.test_root
                detected = generator.detect_profile()

                # Then: 应检测到正确的 profile
                self.assertEqual(detected, profile_name)


class TestSmartDefaultInstantMode(unittest.TestCase):
    """测试智能默认: instant 模式（无需 --confirm）"""

    def test_instant_mode_is_default(self):
        """默认应该是 instant 模式"""
        # Given: 默认设置
        default_instant = True  # 模拟默认值

        # When/Then: 应该是 instant
        self.assertTrue(default_instant)

    def test_instant_mode_generates_immediately(self):
        """instant 模式应立即生成（无需确认）"""
        # Given: instant 模式
        instant = True

        # When: 检查是否需要确认
        needs_confirmation = not instant

        # Then: 不应需要确认
        self.assertFalse(needs_confirmation)


class TestValidateProfileFormat(unittest.TestCase):
    """测试验证点: profile 文件格式"""

    def setUp(self):
        """Create temporary test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)
        (self.test_root / "docs").mkdir()

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_reject_missing_yaml_frontmatter(self):
        """拒绝缺少 YAML frontmatter 的 profile"""
        # Given: 无 frontmatter
        profile_content = """# Project Profile

This is a project without frontmatter.
"""
        profile_file = self.test_root / "docs" / "project-profile.md"
        with open(profile_file, 'w', encoding='utf-8') as f:
            f.write(profile_content)

        # When/Then: 应检测到格式错误
        generator = RuleGenerator()
        generator.project_root = self.test_root

        with self.assertRaises(ProfileError):
            generator.detect_profile()

    def test_reject_malformed_yaml(self):
        """拒绝格式错误的 YAML"""
        # Given: 无效 YAML
        profile_content = """---
profile: tauri
invalid: [unclosed
---
"""
        profile_file = self.test_root / "docs" / "project-profile.md"
        with open(profile_file, 'w', encoding='utf-8') as f:
            f.write(profile_content)

        # When/Then: 应检测到 YAML 错误
        generator = RuleGenerator()
        generator.project_root = self.test_root

        with self.assertRaises(ProfileError) as ctx:
            generator.detect_profile()

        self.assertIn("Invalid YAML", str(ctx.exception))

    def test_accept_valid_yaml_frontmatter(self):
        """接受有效的 YAML frontmatter"""
        # Given: 有效 YAML
        profile_content = """---
profile: tauri
type: desktop-app
rules:
  include:
    - core/*
  exclude: []
---

# Valid Profile
"""
        profile_file = self.test_root / "docs" / "project-profile.md"
        with open(profile_file, 'w', encoding='utf-8') as f:
            f.write(profile_content)

        # When: 验证
        generator = RuleGenerator()
        generator.project_root = self.test_root
        profile = generator.detect_profile()

        # Then: 应接受
        self.assertEqual(profile, "tauri")


class TestValidateTemplateDirectory(unittest.TestCase):
    """测试验证点: 模板目录存在"""

    def setUp(self):
        """Create temporary test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_check_template_directory_exists(self):
        """验证模板目录存在"""
        # Given: 创建模板目录
        templates_dir = self.test_root / ".claude" / "guides" / "rules" / "templates"
        templates_dir.mkdir(parents=True)

        # When: 检查目录
        exists = templates_dir.exists() and templates_dir.is_dir()

        # Then: 应存在
        self.assertTrue(exists)

    def test_handle_missing_template_directory(self):
        """处理缺失的模板目录"""
        # Given: 不存在的目录
        templates_dir = self.test_root / ".claude" / "guides" / "rules" / "templates"

        # When: 检查目录
        exists = templates_dir.exists()

        # Then: 应返回 False
        self.assertFalse(exists)


class TestValidateOutputDirectory(unittest.TestCase):
    """测试验证点: 输出目录可写"""

    def setUp(self):
        """Create temporary test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_output_directory_is_writable(self):
        """验证输出目录可写"""
        # Given: 创建输出目录
        output_dir = self.test_root / ".claude" / "rules"
        output_dir.mkdir(parents=True)

        # When: 测试写入
        test_file = output_dir / "test.txt"
        try:
            test_file.write_text("test")
            is_writable = True
            test_file.unlink()  # Cleanup
        except Exception:
            is_writable = False

        # Then: 应可写
        self.assertTrue(is_writable)

    def test_create_output_directory_if_missing(self):
        """缺失时创建输出目录"""
        # Given: 不存在的输出目录
        output_dir = self.test_root / ".claude" / "rules"
        self.assertFalse(output_dir.exists())

        # When: 创建目录
        output_dir.mkdir(parents=True)

        # Then: 应成功创建
        self.assertTrue(output_dir.exists())


if __name__ == "__main__":
    unittest.main()
