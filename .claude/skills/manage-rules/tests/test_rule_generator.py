"""
Unit tests for RuleGenerator class

Tests profile detection, template filtering, framework-only filtering, and rule generation.
Target: >60% coverage focusing on core logic.
"""

import unittest
import tempfile
import shutil
import json
import yaml
from pathlib import Path
import sys

# Add scripts directory to path

from generate_rules import RuleGenerator, ProfileError


class TestRuleGenerator(unittest.TestCase):
    """Test suite for RuleGenerator class"""

    def setUp(self):
        """Create temporary test project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_root = Path(self.test_dir)

        # 创建测试项目结构
        (self.test_root / "docs").mkdir()
        (self.test_root / ".claude" / "profiles").mkdir(parents=True)
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "core").mkdir(parents=True)
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "architecture").mkdir(parents=True)
        (self.test_root / ".claude" / "guides" / "rules" / "templates" / "languages").mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary test directory"""
        shutil.rmtree(self.test_dir)

    def _create_profile_file(self, profile: str, content: str):
        """Helper: create profile markdown file"""
        profile_file = self.test_root / "docs" / "project-profile.md"
        with open(profile_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def _create_profile_config(self, profile: str, config: dict):
        """Helper: create profile JSON config"""
        config_file = self.test_root / ".claude" / "profiles" / f"{profile}.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

    def _create_template(self, rel_path: str, content: str):
        """Helper: create template file"""
        template_file = self.test_root / ".claude" / "guides" / "rules" / "templates" / rel_path
        template_file.parent.mkdir(parents=True, exist_ok=True)
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(content)

    # ===== Profile Detection Tests =====

    def test_detect_profile_from_file(self):
        """Test profile detection from docs/project-profile.md"""
        # 创建 profile 文件
        profile_content = """---
profile: tauri
type: desktop-app
---

# Project Profile

This is a Tauri desktop application.
"""
        self._create_profile_file("tauri", profile_content)

        # 测试检测
        generator = RuleGenerator()
        generator.project_root = self.test_root
        profile = generator.detect_profile()

        self.assertEqual(profile, "tauri")

    def test_detect_profile_missing_file(self):
        """Test error when profile file missing"""
        generator = RuleGenerator()
        generator.project_root = self.test_root

        with self.assertRaises(ProfileError) as ctx:
            generator.detect_profile()

        self.assertIn("not found", str(ctx.exception))

    def test_detect_profile_invalid_yaml(self):
        """Test error when YAML syntax invalid"""
        # 创建无效的 YAML
        profile_content = """---
profile: tauri
invalid yaml: [unclosed bracket
---
"""
        self._create_profile_file("tauri", profile_content)

        generator = RuleGenerator()
        generator.project_root = self.test_root

        with self.assertRaises(ProfileError) as ctx:
            generator.detect_profile()

        self.assertIn("Invalid YAML", str(ctx.exception))

    # ===== Template Filtering Tests =====

    def test_filter_by_whitelist(self):
        """Test filtering templates by include whitelist"""
        # 创建测试模板
        self._create_template("core/naming.md", "# Naming conventions")
        self._create_template("core/types.md", "# Type safety")
        self._create_template("architecture/clean.md", "# Clean architecture")
        self._create_template("languages/typescript.md", "# TypeScript rules")

        # 创建 profile config（只包含 core/*）
        config = {
            "rules": {
                "include": ["core/*"],
                "exclude": []
            }
        }

        generator = RuleGenerator()
        generator.project_root = self.test_root
        filtered = generator.filter_templates(config)

        # 应该只有 core/* 的模板
        rel_paths = [str(t.relative_to(self.test_root / ".claude" / "guides" / "rules" / "templates")) for t in filtered]
        self.assertEqual(len(filtered), 2)
        self.assertIn("core/naming.md", rel_paths)
        self.assertIn("core/types.md", rel_paths)
        self.assertNotIn("architecture/clean.md", rel_paths)
        self.assertNotIn("languages/typescript.md", rel_paths)

    def test_filter_by_exclude(self):
        """Test filtering templates by exclude patterns"""
        # 创建测试模板
        self._create_template("core/naming.md", "# Naming")
        self._create_template("core/deprecated-old.md", "# Old rule")
        self._create_template("architecture/clean.md", "# Clean")

        # 创建 config（包含所有，排除 deprecated-*）
        config = {
            "rules": {
                "include": ["*"],
                "exclude": ["**/deprecated-*.md"]
            }
        }

        generator = RuleGenerator()
        generator.project_root = self.test_root
        filtered = generator.filter_templates(config)

        # 应该排除 deprecated 文件
        rel_paths = [str(t.relative_to(self.test_root / ".claude" / "guides" / "rules" / "templates")) for t in filtered]
        self.assertNotIn("core/deprecated-old.md", rel_paths)
        self.assertIn("core/naming.md", rel_paths)
        self.assertIn("architecture/clean.md", rel_paths)

    def test_filter_combined(self):
        """Test combined include + exclude filtering"""
        # 创建测试模板
        self._create_template("core/naming.md", "# Naming")
        self._create_template("core/types.md", "# Types")
        self._create_template("core/deprecated.md", "# Deprecated")
        self._create_template("architecture/clean.md", "# Clean")

        # 创建 config（包含 core/*，排除 deprecated）
        config = {
            "rules": {
                "include": ["core/*"],
                "exclude": ["**/deprecated.md"]
            }
        }

        generator = RuleGenerator()
        generator.project_root = self.test_root
        filtered = generator.filter_templates(config)

        # 应该只有 core 且非 deprecated
        rel_paths = [str(t.relative_to(self.test_root / ".claude" / "guides" / "rules" / "templates")) for t in filtered]
        self.assertEqual(len(filtered), 2)
        self.assertIn("core/naming.md", rel_paths)
        self.assertIn("core/types.md", rel_paths)
        self.assertNotIn("core/deprecated.md", rel_paths)
        self.assertNotIn("architecture/clean.md", rel_paths)

    # ===== Framework-Only Filtering Tests (Issue #401) =====

    def test_filter_framework_only(self):
        """Test detection and exclusion of framework-only templates"""
        # 创建普通模板
        self._create_template("core/naming.md", "# Naming conventions")

        # 创建 framework-only 模板
        framework_only_content = """---
framework-only: true
---

# Update Framework Skill

This skill is only for framework maintenance.
"""
        self._create_template("core/update-framework.md", framework_only_content)

        # 获取所有模板
        templates = [
            self.test_root / ".claude" / "guides" / "rules" / "templates" / "core" / "naming.md",
            self.test_root / ".claude" / "guides" / "rules" / "templates" / "core" / "update-framework.md"
        ]

        # 测试过滤
        generator = RuleGenerator()
        generator.project_root = self.test_root
        filtered = generator.filter_framework_only_skills(templates)

        # 应该排除 framework-only 模板
        rel_paths = [str(t.relative_to(self.test_root / ".claude" / "guides" / "rules" / "templates")) for t in filtered]
        self.assertEqual(len(filtered), 1)
        self.assertIn("core/naming.md", rel_paths)
        self.assertNotIn("core/update-framework.md", rel_paths)

    def test_filter_no_marker(self):
        """Test templates without framework-only marker are kept"""
        # 创建无 marker 的模板
        self._create_template("core/naming.md", "# Naming (no frontmatter)")

        templates = [
            self.test_root / ".claude" / "guides" / "rules" / "templates" / "core" / "naming.md"
        ]

        generator = RuleGenerator()
        generator.project_root = self.test_root
        filtered = generator.filter_framework_only_skills(templates)

        # 应该保留（默认不是 framework-only）
        self.assertEqual(len(filtered), 1)

    def test_filter_invalid_yaml(self):
        """Test graceful handling of invalid YAML in frontmatter"""
        # 创建无效 YAML 的模板
        invalid_yaml = """---
framework-only: [unclosed
---

# Invalid YAML
"""
        self._create_template("core/invalid.md", invalid_yaml)

        templates = [
            self.test_root / ".claude" / "guides" / "rules" / "templates" / "core" / "invalid.md"
        ]

        generator = RuleGenerator()
        generator.project_root = self.test_root
        filtered = generator.filter_framework_only_skills(templates)

        # 应该保留（优雅降级）
        self.assertEqual(len(filtered), 1)

    # ===== Rule Generation Tests =====

    def test_generate_rules(self):
        """Test rule file generation"""
        # 创建测试模板
        self._create_template("core/naming.md", "# Naming conventions")
        self._create_template("architecture/clean.md", "# Clean architecture")

        templates = [
            self.test_root / ".claude" / "guides" / "rules" / "templates" / "core" / "naming.md",
            self.test_root / ".claude" / "guides" / "rules" / "templates" / "architecture" / "clean.md"
        ]

        generator = RuleGenerator()
        generator.project_root = self.test_root
        count = generator.generate_rules(templates, dry_run=False)

        # 验证生成数量
        self.assertEqual(count, 2)

        # 验证文件存在
        rules_dir = self.test_root / ".claude" / "rules"
        self.assertTrue((rules_dir / "core" / "naming.md").exists())
        self.assertTrue((rules_dir / "architecture" / "clean.md").exists())

    def test_generate_with_subdirs(self):
        """Test rule generation preserves category structure"""
        # 创建多层模板
        self._create_template("core/naming.md", "# Naming")
        self._create_template("architecture/patterns/clean.md", "# Clean")

        templates = [
            self.test_root / ".claude" / "guides" / "rules" / "templates" / "core" / "naming.md",
            self.test_root / ".claude" / "guides" / "rules" / "templates" / "architecture" / "patterns" / "clean.md"
        ]

        generator = RuleGenerator()
        generator.project_root = self.test_root
        generator.generate_rules(templates, dry_run=False)

        # 验证目录结构
        rules_dir = self.test_root / ".claude" / "rules"
        self.assertTrue((rules_dir / "core").is_dir())
        self.assertTrue((rules_dir / "architecture" / "patterns").is_dir())

    def test_generate_dry_run(self):
        """Test dry run mode shows plan without executing"""
        # 创建测试模板
        self._create_template("core/naming.md", "# Naming")

        templates = [
            self.test_root / ".claude" / "guides" / "rules" / "templates" / "core" / "naming.md"
        ]

        generator = RuleGenerator()
        generator.project_root = self.test_root
        count = generator.generate_rules(templates, dry_run=True)

        # 应该返回计数但不生成文件
        self.assertEqual(count, 1)

        rules_dir = self.test_root / ".claude" / "rules"
        if rules_dir.exists():
            # 如果目录存在，应该是空的
            self.assertEqual(len(list(rules_dir.rglob("*.md"))), 0)


    # ===== Template Extension Tests (Issue #475) =====

    def test_template_extension_handling(self):
        """Test handling of .md.template extension"""
        # 创建 .md.template 模板
        self._create_template("core/naming.md.template", "# Naming conventions")

        templates = [
            self.test_root / ".claude" / "guides" / "rules" / "templates" / "core" / "naming.md.template"
        ]

        generator = RuleGenerator()
        generator.project_root = self.test_root
        count = generator.generate_rules(templates, dry_run=False)

        # 验证文件数量
        self.assertEqual(count, 1)

        # 验证生成的文件名是 naming.md 而不是 naming.md.md
        rules_dir = self.test_root / ".claude" / "rules"
        self.assertTrue((rules_dir / "core" / "naming.md").exists())
        self.assertFalse((rules_dir / "core" / "naming.md.md").exists())

    def test_simple_rule_name_pattern_matching(self):
        """Test pattern matching for simple names like 'workflow'"""
        # 创建模板
        self._create_template("core/workflow.md.template", "# Workflow guidelines")

        # Profile 使用简单名称 "workflow" 而不是 "core/workflow.md"
        config = {
            "rules": {
                "include": ["workflow"],  # 简单名称
                "exclude": []
            }
        }

        generator = RuleGenerator()
        generator.project_root = self.test_root
        filtered = generator.filter_templates(config)

        # 应该匹配成功
        rel_paths = [str(t.relative_to(self.test_root / ".claude" / "guides" / "rules" / "templates")) for t in filtered]
        self.assertEqual(len(filtered), 1)
        self.assertIn("core/workflow.md.template", rel_paths)


if __name__ == "__main__":
    unittest.main()
