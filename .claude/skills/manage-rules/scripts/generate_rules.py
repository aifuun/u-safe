#!/usr/bin/env python3
# /// script
# dependencies = [
#   "PyYAML>=6.0"
# ]
# ///
"""
Rule Generator Script for manage-rules v3.0.0 (UV-enabled)

Generates project-specific rules from templates based on profile configuration.
Implements ADR-014 compliant script-based pattern.

Now uses PEP 723 inline dependencies for automatic dependency management via uv.

Usage:
    uv run scripts/generate_rules.py [--profile PROFILE] [--instant] [--dry-run]
    # Or with python (if dependencies already installed):
    python scripts/generate_rules.py [--profile PROFILE] [--instant] [--dry-run]
"""

import sys
import json
import yaml
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import fnmatch
import argparse


class ProfileError(Exception):
    """Profile-related errors"""
    pass


class RuleGenerator:
    """
    Orchestrates rule generation workflow

    Workflow:
    1. Detect profile from docs/project-profile.md
    2. Load profile configuration with rules whitelist
    3. Filter templates by profile whitelist and exclude patterns
    4. Filter out framework-only templates (Issue #401)
    5. Generate .claude/rules/ files from filtered templates
    """

    def __init__(self, profile: Optional[str] = None, instant: bool = True):
        """
        Initialize with optional profile override and execution mode

        Args:
            profile: Optional profile override (default: auto-detect)
            instant: Execute immediately without confirmation (default: True)
        """
        self.profile = profile
        self.instant = instant
        self.project_root = self._find_project_root()

    def _find_project_root(self) -> Path:
        """
        查找项目根目录（包含 docs/project-profile.md 的目录）

        Returns:
            Path: 项目根目录路径

        Raises:
            ProfileError: 如果找不到项目根目录
        """
        current = Path.cwd()

        # 向上查找直到找到 docs/project-profile.md
        while current != current.parent:
            profile_file = current / "docs" / "project-profile.md"
            if profile_file.exists():
                return current
            current = current.parent

        raise ProfileError("无法找到项目根目录（需要 docs/project-profile.md）")

    def detect_profile(self) -> str:
        """
        Detect project profile from docs/project-profile.md

        Returns:
            str: Profile name (tauri, nextjs-aws, minimal, etc.)

        Raises:
            ProfileError: If profile file missing or invalid
        """
        profile_file = self.project_root / "docs" / "project-profile.md"

        if not profile_file.exists():
            raise ProfileError(f"Profile file not found: {profile_file}")

        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析 YAML frontmatter
            if not content.startswith('---'):
                raise ProfileError("Profile file missing YAML frontmatter")

            yaml_end = content.find('---', 3)
            if yaml_end == -1:
                raise ProfileError("Invalid YAML frontmatter format")

            frontmatter = content[3:yaml_end].strip()
            metadata = yaml.safe_load(frontmatter)

            # 提取 profile 字段
            profile = metadata.get('profile')
            if not profile:
                raise ProfileError("Profile field not found in YAML frontmatter")

            return profile

        except yaml.YAMLError as e:
            raise ProfileError(f"Invalid YAML syntax: {e}")
        except Exception as e:
            raise ProfileError(f"Error reading profile file: {e}")

    def load_profile_config(self, profile: str) -> Dict:
        """
        Load profile configuration with rules whitelist

        Args:
            profile: Profile name

        Returns:
            dict: Profile config with 'rules': {'include': [...], 'exclude': [...]}

        Raises:
            ProfileError: If profile config invalid
        """
        # 查找 profile 配置文件
        # 优先级: 1. .claude/profiles/{profile}.json
        #        2. framework/profiles/{profile}.json (如果是 framework 项目)

        profile_paths = [
            self.project_root / ".claude" / "profiles" / f"{profile}.json",
            self.project_root / "framework" / "profiles" / f"{profile}.json"
        ]

        profile_file = None
        for path in profile_paths:
            if path.exists():
                profile_file = path
                break

        if not profile_file:
            raise ProfileError(f"Profile config not found: {profile}")

        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 验证 rules 字段
            if 'rules' not in config:
                raise ProfileError(f"Profile config missing 'rules' field: {profile}")

            rules_config = config['rules']

            # 验证 include 字段
            if 'include' not in rules_config:
                raise ProfileError(f"Profile config missing 'rules.include' field: {profile}")

            # exclude 字段可选
            if 'exclude' not in rules_config:
                rules_config['exclude'] = []

            return config

        except json.JSONDecodeError as e:
            raise ProfileError(f"Invalid JSON in profile config: {e}")
        except Exception as e:
            raise ProfileError(f"Error loading profile config: {e}")

    def filter_templates(self, config: Dict) -> List[Path]:
        """
        Filter templates by profile whitelist and exclude patterns

        Args:
            config: Profile configuration dict

        Returns:
            List[Path]: Filtered template paths

        Logic:
            1. Scan .claude/guides/rules/templates/
            2. Apply include whitelist
            3. Apply exclude patterns (fnmatch)
            4. Return filtered list
        """
        # 查找模板目录
        template_paths = [
            self.project_root / ".claude" / "guides" / "rules" / "templates",
            self.project_root / "docs" / "ai-guides" / "rules" / "templates"
        ]

        template_dir = None
        for path in template_paths:
            if path.exists():
                template_dir = path
                break

        if not template_dir:
            raise ProfileError("Template directory not found")

        # 扫描所有模板文件（支持 .md 和 .md.template 两种扩展名）
        all_templates = list(template_dir.glob("**/*.md")) + list(template_dir.glob("**/*.md.template"))

        # 提取 include 和 exclude 规则
        include_rules = config['rules']['include']
        exclude_patterns = config['rules'].get('exclude', [])

        # 应用 include whitelist
        # include_rules 格式示例: ["core/*", "architecture/*", "languages/typescript.md"]
        filtered = []
        for template in all_templates:
            # 计算相对于 template_dir 的路径
            rel_path = template.relative_to(template_dir)
            rel_path_str = str(rel_path)

            # 检查是否匹配任何 include 规则
            # 对于简单规则名（如 "workflow"），转换为通配符模式 "*/workflow.md*"
            matched = False
            for rule in include_rules:
                # 如果规则不包含路径分隔符和通配符，视为简单文件名
                if '/' not in rule and '*' not in rule:
                    # 将 "workflow" 转换为 "*/workflow.md*" 以匹配 core/workflow.md 或 core/workflow.md.template
                    pattern = f"*/{rule}.md*"
                else:
                    pattern = rule

                if fnmatch.fnmatch(rel_path_str, pattern):
                    matched = True
                    break

            if matched:
                filtered.append(template)

        # 应用 exclude patterns
        # exclude_patterns 格式示例: ["**/deprecated-*.md", "languages/python.md"]
        final_filtered = []
        for template in filtered:
            rel_path = template.relative_to(template_dir)
            rel_path_str = str(rel_path)

            # 检查是否匹配任何 exclude pattern
            excluded = False
            for pattern in exclude_patterns:
                if fnmatch.fnmatch(rel_path_str, pattern):
                    excluded = True
                    break

            if not excluded:
                final_filtered.append(template)

        return final_filtered

    def filter_framework_only_skills(self, templates: List[Path]) -> List[Path]:
        """
        Filter out framework-only templates (Issue #401)

        Args:
            templates: List of template paths

        Returns:
            List[Path]: Templates without framework-only items

        Logic:
            1. For each template, read YAML frontmatter
            2. Check for 'framework-only: true' field
            3. Exclude templates with framework-only=true
            4. Return filtered list

        Note: This preserves Issue #401 functionality
        """
        filtered = []

        for template in templates:
            try:
                with open(template, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 检查是否有 YAML frontmatter
                if not content.startswith('---'):
                    # 没有 frontmatter，默认包含
                    filtered.append(template)
                    continue

                # 解析 YAML frontmatter
                yaml_end = content.find('---', 3)
                if yaml_end == -1:
                    # 无效的 frontmatter，默认包含
                    filtered.append(template)
                    continue

                frontmatter = content[3:yaml_end].strip()
                metadata = yaml.safe_load(frontmatter)

                # 检查 framework-only 字段
                framework_only = metadata.get('framework-only', False)

                if not framework_only:
                    filtered.append(template)

            except yaml.YAMLError:
                # YAML 解析错误，默认包含（优雅降级）
                filtered.append(template)
            except Exception:
                # 其他错误，默认包含（优雅降级）
                filtered.append(template)

        return filtered

    def generate_rules(self, templates: List[Path], dry_run: bool = False) -> int:
        """
        Generate .claude/rules/ files from filtered templates

        Args:
            templates: Filtered template paths
            dry_run: Show plan without executing (default: False)

        Returns:
            int: Count of generated rule files

        Logic:
            1. Create .claude/rules/ structure
            2. Copy each template to appropriate category subdirectory
            3. Remove .template suffix from filenames
            4. Return count
        """
        rules_dir = self.project_root / ".claude" / "rules"

        if dry_run:
            print(f"📋 Dry Run - Would generate {len(templates)} rules:")
            for template in templates:
                # 计算目标路径
                template_dir = template.parent
                category = template_dir.name

                # 移除 .template 后缀（如果有）
                if template.name.endswith('.md.template'):
                    rule_name = template.stem  # workflow.md from workflow.md.template
                else:
                    rule_name = template.name  # workflow.md from workflow.md

                target_path = rules_dir / category / rule_name
                print(f"  - {template.relative_to(self.project_root)} → {target_path.relative_to(self.project_root)}")

            return len(templates)

        # 清空现有 rules 目录（保留 .gitkeep）
        if rules_dir.exists():
            for item in rules_dir.iterdir():
                if item.name == '.gitkeep':
                    continue
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        else:
            rules_dir.mkdir(parents=True, exist_ok=True)

        # 复制模板到 rules 目录
        count = 0
        for template in templates:
            # 计算目标路径
            template_dir = template.parent
            category = template_dir.name

            # 创建类别目录
            category_dir = rules_dir / category
            category_dir.mkdir(exist_ok=True)

            # 移除 .template 后缀（如果有）
            if template.name.endswith('.md.template'):
                rule_name = template.stem  # workflow.md from workflow.md.template
            else:
                rule_name = template.name  # workflow.md from workflow.md

            target_path = category_dir / rule_name

            # 复制文件
            shutil.copy2(template, target_path)
            count += 1

        return count


def main():
    """Main entry point for rule generation"""
    parser = argparse.ArgumentParser(
        description='Generate project-specific rules from templates'
    )
    parser.add_argument(
        '--profile',
        type=str,
        help='Override profile (default: auto-detect from docs/project-profile.md)'
    )
    parser.add_argument(
        '--instant',
        action='store_true',
        help='Execute immediately without confirmation (default: False)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show plan without executing (default: False)'
    )

    args = parser.parse_args()

    try:
        # 创建 RuleGenerator 实例
        generator = RuleGenerator(profile=args.profile, instant=args.instant)

        # Step 1: Detect profile
        print("🔍 Detecting profile...")
        detected_profile = generator.detect_profile() if not args.profile else args.profile
        print(f"✅ Profile: {detected_profile}")

        # Step 2: Load config
        print("\n📖 Loading profile configuration...")
        config = generator.load_profile_config(detected_profile)
        include_count = len(config['rules']['include'])
        exclude_count = len(config['rules'].get('exclude', []))
        print(f"✅ Config loaded: {include_count} include rules, {exclude_count} exclude patterns")

        # Step 3: Filter templates
        print("\n🔍 Filtering templates...")
        templates = generator.filter_templates(config)
        print(f"✅ Filtered: {len(templates)} templates matched")

        # Step 4: Filter framework-only (Issue #401)
        print("\n🔍 Filtering framework-only templates...")
        before_count = len(templates)
        filtered = generator.filter_framework_only_skills(templates)
        excluded_count = before_count - len(filtered)
        print(f"✅ Filtered: {len(filtered)} templates (excluded {excluded_count} framework-only)")

        # Step 5: Generate or show plan
        if args.dry_run or not args.instant:
            print("\n📋 Dry Run:")
            generator.generate_rules(filtered, dry_run=True)

            if not args.instant and not args.dry_run:
                response = input("\nProceed with generation? [y/N]: ")
                if response.lower() != 'y':
                    print("❌ Cancelled")
                    return 0

        if not args.dry_run:
            print("\n📝 Generating rules...")
            count = generator.generate_rules(filtered, dry_run=False)
            print(f"✅ Generated {count} rules for profile '{detected_profile}'")

        return 0

    except ProfileError as e:
        print(f"❌ Profile Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
