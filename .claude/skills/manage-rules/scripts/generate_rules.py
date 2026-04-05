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
from functools import lru_cache
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

        # 验证 profile schema（Issue #475）
        self.validate_profile_schema(profile_file)

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
                # 检查是否使用了错误的字段名
                if 'name' in metadata:
                    raise ProfileError(
                        f"Profile field not found in YAML frontmatter.\n"
                        f"Found 'name: {metadata['name']}' instead.\n"
                        f"Did you mean to use 'profile: {metadata['name']}'?\n"
                        f"Location: {profile_file}"
                    )
                else:
                    raise ProfileError(
                        f"Profile field not found in YAML frontmatter.\n"
                        f"Expected format:\n"
                        f"  ---\n"
                        f"  profile: tauri\n"
                        f"  ---\n"
                        f"Location: {profile_file}"
                    )

            return profile

        except yaml.YAMLError as e:
            raise ProfileError(f"Invalid YAML syntax: {e}")
        except Exception as e:
            raise ProfileError(f"Error reading profile file: {e}")

    def validate_profile_schema(self, profile_file: Path) -> None:
        """
        验证 profile frontmatter 符合 schema 要求

        Args:
            profile_file: Profile 文件路径

        Raises:
            ProfileError: 如果缺少必填字段

        Schema: docs/schemas/project-profile.schema.md

        Required fields:
          - profile: Unique identifier (e.g., "tauri")
          - type: Project type (e.g., "desktop-app")
          - category: Broad category (e.g., "desktop")
        """
        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取 YAML frontmatter
            if not content.startswith('---'):
                raise ProfileError(f"No YAML frontmatter found in {profile_file}")

            yaml_end = content.find('\n---', 3)
            if yaml_end == -1:
                raise ProfileError(f"Invalid YAML frontmatter format in {profile_file}")

            frontmatter = content[3:yaml_end].strip()
            metadata = yaml.safe_load(frontmatter)

            # 验证必填字段
            required_fields = ['profile', 'type', 'category']
            missing = [f for f in required_fields if f not in metadata]

            if missing:
                raise ProfileError(
                    f"Missing required fields in {profile_file}: {', '.join(missing)}\n"
                    f"See docs/schemas/project-profile.schema.md for format"
                )

        except yaml.YAMLError as e:
            raise ProfileError(f"Invalid YAML syntax in {profile_file}: {e}")
        except FileNotFoundError:
            raise ProfileError(f"Profile file not found: {profile_file}")
        except Exception as e:
            if isinstance(e, ProfileError):
                raise
            raise ProfileError(f"Error validating profile schema: {e}")

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

        # 扫描所有模板文件（使用缓存优化 - Issue #475 Task 6）
        all_templates = list(self._scan_all_templates(template_dir))

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
            matched = False
            for rule in include_rules:
                if fnmatch.fnmatch(rel_path_str, rule):
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

    @lru_cache(maxsize=1)
    def _scan_all_templates(self, template_dir: Path) -> tuple:
        """
        扫描所有模板文件（带缓存优化）

        使用 @lru_cache 避免重复扫描相同目录。
        返回 tuple 使其可以被缓存（list 不可哈希）。

        Args:
            template_dir: 模板目录路径

        Returns:
            tuple: 所有模板文件路径的元组

        Performance:
            - 首次调用: 扫描文件系统
            - 后续调用: 返回缓存结果（几乎零开销）
        """
        templates = list(template_dir.glob("**/*.md")) + list(template_dir.glob("**/*.md.template"))
        return tuple(templates)  # Convert to tuple for caching

    def _normalize_rule_filename(self, template_path: Path) -> str:
        """
        将模板文件名转换为规则文件名

        处理 .md.template 扩展名，移除 .template 后缀。

        Args:
            template_path: 模板文件路径

        Returns:
            str: 规则文件名（带 .md 扩展名）

        Examples:
            workflow.md.template → workflow.md
            naming.md → naming.md
        """
        if template_path.name.endswith('.md.template'):
            return template_path.stem  # workflow.md (stem 已包含 .md)
        else:
            return template_path.name  # naming.md

    def generate_rules(self, templates: List[Path], dry_run: bool = False) -> int:
        """
        Generate .claude/rules/ files from filtered templates

        Args:
            templates: Filtered template paths
            dry_run: Show plan without executing (default: False)

        Returns:
            int: Count of generated rule files

        Logic:
            1. Backup existing rules (if any)
            2. Create .claude/rules/ structure
            3. Copy each template to appropriate category subdirectory
            4. Remove .template suffix from filenames
            5. Remove backup on success
            6. Restore from backup on failure
        """
        rules_dir = self.project_root / ".claude" / "rules"
        backup_dir = self.project_root / ".claude" / "rules.backup"

        if dry_run:
            print(f"📋 Dry Run - Would generate {len(templates)} rules:")
            for template in templates:
                # 计算目标路径
                template_dir = template.parent
                category = template_dir.name

                # 使用统一的文件名规范化方法
                rule_name = self._normalize_rule_filename(template)

                target_path = rules_dir / category / rule_name
                print(f"  - {template.relative_to(self.project_root)} → {target_path.relative_to(self.project_root)}")

            return len(templates)

        # 备份现有规则（Issue #475 - Task 5）
        if rules_dir.exists() and any(rules_dir.iterdir()):
            # 删除旧备份（如果存在）
            if backup_dir.exists():
                shutil.rmtree(backup_dir)

            # 创建新备份
            shutil.copytree(rules_dir, backup_dir)
            print(f"📦 Backed up existing rules to {backup_dir.relative_to(self.project_root)}")

        try:
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

                # 使用统一的文件名规范化方法
                rule_name = self._normalize_rule_filename(template)

                target_path = category_dir / rule_name

                # 复制文件
                shutil.copy2(template, target_path)
                count += 1

            # 成功后删除备份
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
                print(f"✅ Backup removed (generation successful)")

            return count

        except Exception as e:
            # 失败时从备份恢复
            if backup_dir.exists():
                if rules_dir.exists():
                    shutil.rmtree(rules_dir)
                shutil.move(str(backup_dir), str(rules_dir))
                print(f"⚠️  Generation failed, restored from backup")
            raise


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
