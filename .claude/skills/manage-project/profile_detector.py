#!/usr/bin/env python3
"""
Profile Auto-Detection Module for /manage-project

Implements 4-level detection strategy:
1. Level 1: Check docs/project-profile.md (user's explicit configuration)
2. Level 2: Check .framework-install (installation marker)
3. Level 3: Smart tech stack detection (from project files)
4. Level 4: Interactive selection (fallback)
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ProfileDetector:
    """Intelligent profile detection for project configuration."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.profiles_dir = self.project_root / "framework" / "profiles"

    def detect_profile(self, show_detection: bool = False) -> Tuple[Optional[str], str]:
        """
        主检测入口 - 按优先级尝试 4 个级别

        Args:
            show_detection: 是否显示检测过程

        Returns:
            (profile_name, detection_method)
            profile_name: 检测到的 profile 名称，None 表示未检测到
            detection_method: "level1" | "level2" | "level3" | "level4" | "not_found"
        """
        detection_log = []

        # Level 1: docs/project-profile.md
        profile = self._detect_level1()
        if profile:
            detection_log.append(f"Level 1: ✓ Found docs/project-profile.md (profile: {profile})")
            if show_detection:
                self._print_detection_log(detection_log)
            return profile, "level1"
        else:
            detection_log.append("Level 1: ✗ docs/project-profile.md not found or invalid")

        # Level 2: .framework-install
        profile = self._detect_level2()
        if profile:
            detection_log.append(f"Level 2: ✓ Found .framework-install (profile: {profile})")
            if show_detection:
                self._print_detection_log(detection_log)
            return profile, "level2"
        else:
            detection_log.append("Level 2: ✗ .framework-install not found or invalid")

        # Level 3: Tech stack detection
        profiles = self._detect_level3()
        if len(profiles) == 1:
            profile = profiles[0]
            detection_log.append(f"Level 3: ✓ Detected tech stack (profile: {profile})")
            if show_detection:
                self._print_detection_log(detection_log)
            return profile, "level3"
        elif len(profiles) > 1:
            detection_log.append(f"Level 3: ⚠ Multiple matches: {', '.join(profiles)}")
            if show_detection:
                self._print_detection_log(detection_log)
            # Return first match but indicate multiple matches
            return profiles[0], "level3_multiple"
        else:
            detection_log.append("Level 3: ✗ Could not match tech stack to profiles")

        # Level 4: Fallback to interactive
        detection_log.append("Level 4: → Falling back to interactive selection")
        if show_detection:
            self._print_detection_log(detection_log)

        return None, "level4"

    def _detect_level1(self) -> Optional[str]:
        """Level 1: 读取 docs/project-profile.md 中的 profile 字段"""
        profile_file = self.project_root / "docs" / "project-profile.md"

        if not profile_file.exists():
            return None

        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse frontmatter (YAML between --- lines)
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    # Extract profile field
                    for line in frontmatter.split('\n'):
                        if line.strip().startswith('name:'):
                            profile = line.split(':', 1)[1].strip().strip('"\'')
                            # Validate profile exists
                            if self._validate_profile(profile):
                                return profile

            return None

        except Exception:
            return None

    def _detect_level2(self) -> Optional[str]:
        """Level 2: 读取 .framework-install 标记文件"""
        marker_file = self.project_root / ".framework-install"

        if not marker_file.exists():
            return None

        try:
            with open(marker_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            profile = data.get('profile')
            if profile and self._validate_profile(profile):
                return profile

            return None

        except Exception:
            return None

    def _detect_level3(self) -> List[str]:
        """
        Level 3: 智能技术栈检测

        Returns:
            List of matching profiles (may be empty, single, or multiple)
        """
        tech_stack = self._detect_tech_stack()
        return self._match_profiles(tech_stack)

    def _detect_tech_stack(self) -> Dict[str, bool]:
        """检测项目技术栈特征"""
        return {
            'has_cargo': (self.project_root / "Cargo.toml").exists(),
            'has_tauri': (self.project_root / "src-tauri" / "tauri.conf.json").exists(),
            'has_cdk': (
                (self.project_root / "cdk").exists() or
                (self.project_root / "infra").exists()
            ),
            'has_nextjs': self._check_package_dependency('next'),
            'has_react': self._check_package_dependency('react'),
        }

    def _check_package_dependency(self, package: str) -> bool:
        """检查 package.json 中是否包含特定依赖"""
        package_json = self.project_root / "package.json"

        if not package_json.exists():
            return False

        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)

            dependencies = data.get('dependencies', {})
            dev_dependencies = data.get('devDependencies', {})

            return package in dependencies or package in dev_dependencies

        except Exception:
            return False

    def _match_profiles(self, tech_stack: Dict[str, bool]) -> List[str]:
        """
        根据技术栈匹配 profiles

        Matching rules:
        - Tauri Desktop: has_cargo + has_tauri + !has_cdk
        - Tauri AWS: has_cargo + has_tauri + has_cdk
        - Next.js AWS: has_nextjs + has_cdk
        """
        matches = []

        # Tauri Desktop (without cloud)
        if (tech_stack['has_cargo'] and
            tech_stack['has_tauri'] and
            not tech_stack['has_cdk']):
            matches.append('tauri')

        # Tauri AWS (with cloud backend)
        if (tech_stack['has_cargo'] and
            tech_stack['has_tauri'] and
            tech_stack['has_cdk']):
            matches.append('tauri-aws')

        # Next.js AWS
        if tech_stack['has_nextjs'] and tech_stack['has_cdk']:
            matches.append('nextjs-aws')

        return matches

    def _validate_profile(self, profile: str) -> bool:
        """验证 profile 是否存在于 .claude/profiles/"""
        profile_file = self.profiles_dir / f"{profile}.md"
        return profile_file.exists()

    def _print_detection_log(self, log: List[str]):
        """打印检测日志（用于 --show-detection 模式）"""
        print("\n🔍 Profile Detection Process\n")
        for entry in log:
            print(f"   {entry}")
        print()

    def check_consistency(self) -> Dict[str, Optional[str]]:
        """
        检查 Level 1/2/3 检测结果的一致性

        Returns:
            {
                "level1": profile or None,
                "level2": profile or None,
                "level3": profile or None,
                "consistent": bool,
                "recommendation": profile
            }
        """
        level1 = self._detect_level1()
        level2 = self._detect_level2()
        level3_matches = self._detect_level3()
        level3 = level3_matches[0] if level3_matches else None

        # Determine consistency
        detected = [p for p in [level1, level2, level3] if p]
        consistent = len(set(detected)) <= 1

        # Recommendation priority: Level 1 > Level 3 > Level 2
        recommendation = level1 or level3 or level2

        return {
            "level1": level1,
            "level2": level2,
            "level3": level3,
            "consistent": consistent,
            "recommendation": recommendation
        }


def main():
    """CLI entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Detect project profile")
    parser.add_argument('--show-detection', action='store_true',
                        help='Show detection process')
    parser.add_argument('--check-consistency', action='store_true',
                        help='Check consistency across all levels')

    args = parser.parse_args()

    detector = ProfileDetector()

    if args.check_consistency:
        result = detector.check_consistency()
        print("\n📊 Consistency Check\n")
        print(f"   Level 1: {result['level1'] or '✗ Not found'}")
        print(f"   Level 2: {result['level2'] or '✗ Not found'}")
        print(f"   Level 3: {result['level3'] or '✗ Not found'}")
        print()
        if result['consistent']:
            print("   ✅ All levels consistent")
        else:
            print("   ⚠️ Inconsistent configuration detected")
        print(f"   Recommendation: {result['recommendation']}")
        print()
    else:
        profile, method = detector.detect_profile(show_detection=args.show_detection)

        if profile:
            print(f"✅ Detected profile: {profile} (via {method})")
        else:
            print("❌ Could not auto-detect profile")
            print("   Falling back to interactive selection")


if __name__ == '__main__':
    main()
