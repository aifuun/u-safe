"""
功能测试 - 基于 manage-rules SKILL.md "What it does" 章节

测试 manage-rules 的核心功能:
1. 加载项目 profile（从 docs/project-profile.md）
2. 验证 profile（YAML 语法和必需字段）
3. 扫描规则模板（.claude/guides/rules/templates/）
4. 按 profile 过滤（rules.include 白名单）
5. 过滤 framework-only 模板（Issue #401）
6. 生成规则文件（复制到 .claude/rules/）
7. 报告结果（生成数量和位置）
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


class TestLoadProjectProfile(unittest.TestCase):
    """测试功能 1: 加载项目 profile（从 docs/project-profile.md）"""

    def setUp(self):
        """Create temporary test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)
        (self.test_root / "docs").mkdir()

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_load_profile_from_docs_directory(self):
        """从 docs/project-profile.md 加载 profile"""
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

        # When: 加载 profile
        generator = RuleGenerator()
        generator.project_root = self.test_root
        profile = generator.detect_profile()

        # Then: 应成功加载
        self.assertEqual(profile, "tauri")

    def test_load_profile_with_rules_config(self):
        """加载包含 rules 配置的 profile"""
        # Given: Profile 包含 rules 配置
        profile_content = """---
profile: tauri
rules:
  include:
    - core/*
    - languages/typescript.md
    - languages/rust.md
---
"""
        profile_file = self.test_root / "docs" / "project-profile.md"
        with open(profile_file, 'w', encoding='utf-8') as f:
            f.write(profile_content)

        # When: 加载 profile
        generator = RuleGenerator()
        generator.project_root = self.test_root
        profile = generator.detect_profile()

        # Then: 应成功加载
        self.assertEqual(profile, "tauri")


class TestValidateProfile(unittest.TestCase):
    """测试功能 2: 验证 profile（YAML 语法和必需字段）"""

    def setUp(self):
        """Create temporary test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)
        (self.test_root / "docs").mkdir()

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_validate_yaml_syntax(self):
        """验证 YAML 语法正确性"""
        # Given: 无效的 YAML 语法
        invalid_yaml = """---
profile: tauri
invalid: [unclosed bracket
---
"""
        profile_file = self.test_root / "docs" / "project-profile.md"
        with open(profile_file, 'w', encoding='utf-8') as f:
            f.write(invalid_yaml)

        # When/Then: 应抛出 ProfileError
        generator = RuleGenerator()
        generator.project_root = self.test_root

        with self.assertRaises(ProfileError) as ctx:
            generator.detect_profile()

        self.assertIn("Invalid YAML", str(ctx.exception))

    def test_validate_required_profile_field(self):
        """验证必需字段 'profile' 存在"""
        # Given: 缺少 profile 字段
        missing_profile = """---
type: desktop-app
---
"""
        profile_file = self.test_root / "docs" / "project-profile.md"
        with open(profile_file, 'w', encoding='utf-8') as f:
            f.write(missing_profile)

        # When/Then: 应检测到缺失
        generator = RuleGenerator()
        generator.project_root = self.test_root

        with self.assertRaises(ProfileError):
            generator.detect_profile()


class TestScanRuleTemplates(unittest.TestCase):
    """测试功能 3: 扫描规则模板（.claude/guides/rules/templates/）"""

    def setUp(self):
        """Create temporary test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core").mkdir(parents=True)
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "architecture").mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_scan_templates_directory(self):
        """扫描模板目录"""
        # Given: 创建多个模板文件
        templates_dir = self.test_root / ".claude" / "guides" / "rules" / "templates"
        (templates_dir / "core" / "naming.md").write_text("# Naming")
        (templates_dir / "core" / "types.md").write_text("# Types")
        (templates_dir / "architecture" / "clean.md").write_text("# Clean")

        # When: 扫描模板
        templates = list(templates_dir.rglob("*.md"))

        # Then: 应找到所有模板
        self.assertEqual(len(templates), 3)

    def test_scan_finds_nested_templates(self):
        """扫描应找到嵌套目录中的模板"""
        # Given: 嵌套目录结构
        templates_dir = self.test_root / ".claude" / "guides" / "rules" / "templates"
        (templates_dir / "architecture" / "patterns").mkdir(parents=True)
        (templates_dir / "architecture" / "patterns" / "mvvm.md").write_text("# MVVM")

        # When: 扫描
        templates = list(templates_dir.rglob("*.md"))

        # Then: 应找到嵌套模板
        self.assertGreaterEqual(len(templates), 1)
        self.assertTrue(any("mvvm.md" in str(t) for t in templates))


class TestFilterByProfile(unittest.TestCase):
    """测试功能 4: 按 profile 过滤（rules.include 白名单）"""

    def setUp(self):
        """Create temporary test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core").mkdir(parents=True)
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "languages").mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_filter_by_include_whitelist(self):
        """按 include 白名单过滤"""
        # Given: 创建多个模板
        templates_dir = self.test_root / ".claude" / "guides" / "rules" / "templates"
        (templates_dir / "core" / "naming.md").write_text("# Naming")
        (templates_dir / "core" / "types.md").write_text("# Types")
        (templates_dir / "languages" / "typescript.md").write_text("# TypeScript")

        # Profile 只包含 core/*
        config = {
            "rules": {
                "include": ["core/*"],
                "exclude": []
            }
        }

        # When: 过滤
        generator = RuleGenerator()
        generator.project_root = self.test_root
        filtered = generator.filter_templates(config)

        # Then: 应只有 core/* 模板
        rel_paths = [str(t.relative_to(templates_dir)) for t in filtered]
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all("core/" in p for p in rel_paths))

    def test_filter_by_exclude_pattern(self):
        """按 exclude 模式排除"""
        # Given: 创建模板
        templates_dir = self.test_root / ".claude" / "guides" / "rules" / "templates"
        (templates_dir / "core" / "naming.md").write_text("# Naming")
        (templates_dir / "core" / "deprecated.md").write_text("# Deprecated")

        config = {
            "rules": {
                "include": ["*"],
                "exclude": ["**/deprecated.md"]
            }
        }

        # When: 过滤
        generator = RuleGenerator()
        generator.project_root = self.test_root
        filtered = generator.filter_templates(config)

        # Then: 应排除 deprecated
        rel_paths = [str(t.relative_to(templates_dir)) for t in filtered]
        self.assertNotIn("core/deprecated.md", rel_paths)


class TestFilterFrameworkOnly(unittest.TestCase):
    """测试功能 5: 过滤 framework-only 模板（Issue #401）"""

    def setUp(self):
        """Create temporary test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core").mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_exclude_framework_only_templates(self):
        """排除 framework-only 模板"""
        # Given: 创建普通和 framework-only 模板
        templates_dir = self.test_root / ".claude" / "guides" / "rules" / "templates"
        (templates_dir / "core" / "naming.md").write_text("# Naming")

        framework_only = """---
framework-only: true
---

# Update Framework
"""
        (templates_dir / "core" / "update-framework.md").write_text(framework_only)

        templates = list(templates_dir.rglob("*.md"))

        # When: 过滤 framework-only
        generator = RuleGenerator()
        generator.project_root = self.test_root
        filtered = generator.filter_framework_only_skills(templates)

        # Then: 应排除 framework-only
        rel_paths = [str(t.relative_to(templates_dir)) for t in filtered]
        self.assertEqual(len(filtered), 1)
        self.assertIn("core/naming.md", rel_paths)
        self.assertNotIn("core/update-framework.md", rel_paths)


class TestGenerateRuleFiles(unittest.TestCase):
    """测试功能 6: 生成规则文件（复制到 .claude/rules/）"""

    def setUp(self):
        """Create temporary test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core").mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_generate_copies_to_rules_directory(self):
        """生成规则文件到 .claude/rules/"""
        # Given: 创建模板
        templates_dir = self.test_root / ".claude" / "guides" / "rules" / "templates"
        (templates_dir / "core" / "naming.md").write_text("# Naming")

        templates = [templates_dir / "core" / "naming.md"]

        # When: 生成
        generator = RuleGenerator()
        generator.project_root = self.test_root
        count = generator.generate_rules(templates, dry_run=False)

        # Then: 应生成到 .claude/rules/
        rules_file = self.test_root / ".claude" / "rules" / "core" / "naming.md"
        self.assertTrue(rules_file.exists())
        self.assertEqual(count, 1)

    def test_generate_preserves_directory_structure(self):
        """生成保留目录结构"""
        # Given: 多层目录模板
        templates_dir = self.test_root / ".claude" / "guides" / "rules" / "templates"
        (templates_dir / "architecture" / "patterns").mkdir(parents=True)
        (templates_dir / "architecture" / "patterns" / "clean.md").write_text("# Clean")

        templates = [templates_dir / "architecture" / "patterns" / "clean.md"]

        # When: 生成
        generator = RuleGenerator()
        generator.project_root = self.test_root
        generator.generate_rules(templates, dry_run=False)

        # Then: 应保留目录结构
        rules_file = self.test_root / ".claude" / "rules" / "architecture" / "patterns" / "clean.md"
        self.assertTrue(rules_file.exists())


class TestReportResults(unittest.TestCase):
    """测试功能 7: 报告结果（生成数量和位置）"""

    def setUp(self):
        """Create temporary test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core").mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def test_report_generated_count(self):
        """报告生成的文件数量"""
        # Given: 多个模板
        templates_dir = self.test_root / ".claude" / "guides" / "rules" / "templates"
        for name in ["naming.md", "types.md", "error.md"]:
            (templates_dir / "core" / name).write_text(f"# {name}")

        templates = list(templates_dir.glob("core/*.md"))

        # When: 生成
        generator = RuleGenerator()
        generator.project_root = self.test_root
        count = generator.generate_rules(templates, dry_run=False)

        # Then: 应报告正确数量
        self.assertEqual(count, 3)

    def test_report_file_locations(self):
        """报告文件位置"""
        # Given: 生成规则文件
        templates_dir = self.test_root / ".claude" / "guides" / "rules" / "templates"
        (templates_dir / "core" / "naming.md").write_text("# Naming")

        templates = [templates_dir / "core" / "naming.md"]

        generator = RuleGenerator()
        generator.project_root = self.test_root
        generator.generate_rules(templates, dry_run=False)

        # When: 检查位置
        rules_dir = self.test_root / ".claude" / "rules"
        generated_files = list(rules_dir.rglob("*.md"))

        # Then: 应报告正确位置
        self.assertEqual(len(generated_files), 1)
        self.assertTrue(any("naming.md" in str(f) for f in generated_files))


if __name__ == "__main__":
    unittest.main()
