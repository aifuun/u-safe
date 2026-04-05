#!/usr/bin/env python3
"""
check_docs.py - Documentation Structure Validator

脚本化模式实现 (ADR-014合规)
提取自check-docs/SKILL.md的验证逻辑

功能:
1. 文档结构验证 (required directories)
2. 文件存在性验证 (required files)
3. 命名规范验证 (kebab-case, UPPERCASE.md)
4. ADR编号验证 (sequential numbering)
5. 评分系统 (0-100)
6. 修复建议生成

使用:
  python check_docs.py                    # 基础验证
  python check_docs.py --verbose          # 详细输出
  python check_docs.py --profile tauri    # 指定profile
  python check_docs.py --json             # JSON输出
  python check_docs.py --fix              # 自动修复
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Import shared config reader (Issue #481)
# Path: .claude/skills/ (where _scripts is located)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from _scripts.utils.config import read_profile, ProfileError
from typing import Dict, List, Optional, Tuple


@dataclass
class ValidationResult:
    """验证结果数据类"""
    score: int
    max_score: int
    passed: bool
    issues: List[str]
    fixes: List[Dict[str, str]]


@dataclass
class Fix:
    """修复建议数据类"""
    type: str  # mkdir, rename, init-docs, renumber
    command: str
    description: str
    path: Optional[str] = None


class DocsChecker:
    """文档结构检查器"""

    # Profile-specific directory requirements
    PROFILE_DIRS = {
        'tauri': ['docs/desktop/'],
        'tauri-aws': ['docs/desktop/', 'docs/aws/'],
        'nextjs-aws': ['docs/aws/']
    }

    # Base required directories (all profiles)
    BASE_DIRS = [
        'docs/',
        'docs/ADRs/',
        'docs/architecture/',
        'docs/api/',
        'docs/guides/',
        'docs/diagrams/'
    ]

    # Profile-specific required files
    PROFILE_FILES = {
        'tauri': [
            'docs/README.md',
            'docs/PRD.md',
            'docs/ARCHITECTURE.md',
            'docs/API.md',
            'docs/SETUP.md',
            'docs/TEST_PLAN.md',
        ],
        'nextjs-aws': [
            'docs/README.md',
            'docs/PRD.md',
            'docs/ARCHITECTURE.md',
            'docs/API.md',
            'docs/SETUP.md',
            'docs/TEST_PLAN.md',
            'docs/DEPLOYMENT.md',
        ]
    }

    def __init__(self, profile: str = 'minimal', root_path: str = '.'):
        """初始化检查器

        Args:
            profile: 项目profile (tauri, tauri-aws, nextjs-aws, minimal)
            root_path: 项目根目录路径
        """
        self.profile = profile
        self.root = Path(root_path).resolve()
        self.required_dirs = self._get_required_dirs()
        self.required_files = self._get_required_files()

    def _get_required_dirs(self) -> List[str]:
        """获取profile对应的必需目录列表"""
        dirs = self.BASE_DIRS.copy()
        if self.profile in self.PROFILE_DIRS:
            dirs.extend(self.PROFILE_DIRS[self.profile])
        return dirs

    def _get_required_files(self) -> List[str]:
        """获取profile对应的必需文件列表"""
        return self.PROFILE_FILES.get(self.profile, [])

    def validate_structure(self) -> ValidationResult:
        """验证目录结构 (30分)

        Returns:
            ValidationResult with score 0-30
        """
        max_score = 30
        issues = []
        fixes = []

        missing_dirs = []
        for req_dir in self.required_dirs:
            dir_path = self.root / req_dir
            if not dir_path.exists():
                missing_dirs.append(req_dir)
                issues.append(f"Missing directory: {req_dir}")
                fixes.append({
                    'type': 'mkdir',
                    'command': f'mkdir -p {req_dir}',
                    'description': f'Create missing directory: {req_dir}'
                })

        # Scoring: -5分 per missing directory
        score = max(0, max_score - len(missing_dirs) * 5)
        passed = score >= max_score * 0.8  # 80% threshold

        return ValidationResult(
            score=score,
            max_score=max_score,
            passed=passed,
            issues=issues,
            fixes=fixes
        )

    def validate_files(self) -> ValidationResult:
        """验证必需文件存在性 (40分)

        Returns:
            ValidationResult with score 0-40
        """
        max_score = 40
        issues = []
        fixes = []

        missing_files = []
        for req_file in self.required_files:
            file_path = self.root / req_file
            if not file_path.exists():
                missing_files.append(req_file)
                issues.append(f"Missing file: {req_file}")

        if missing_files:
            fixes.append({
                'type': 'init-docs',
                'command': '/init-docs --force',
                'description': f'Generate {len(missing_files)} missing documentation files'
            })

        # Scoring: -8分 per missing file
        score = max(0, max_score - len(missing_files) * 8)
        passed = score >= max_score * 0.8

        return ValidationResult(
            score=score,
            max_score=max_score,
            passed=passed,
            issues=issues,
            fixes=fixes
        )

    def validate_naming(self) -> ValidationResult:
        """验证文件命名规范 (15分)

        规则:
        - 核心文档: UPPERCASE.md (README, PRD, ARCHITECTURE, etc.)
        - 辅助文档: kebab-case.md (user-stories, decision-log, etc.)

        Returns:
            ValidationResult with score 0-15
        """
        max_score = 15
        issues = []
        fixes = []
        violations = []

        # 核心文档应为UPPERCASE
        core_docs = ['README', 'PRD', 'ARCHITECTURE', 'API', 'SETUP', 'TEST_PLAN', 'DEPLOYMENT', 'SCHEMA']

        docs_dir = self.root / 'docs'
        if docs_dir.exists():
            for md_file in docs_dir.rglob('*.md'):
                relative_path = md_file.relative_to(self.root)
                file_stem = md_file.stem

                # 跳过子目录中的文件 (ADRs/, etc.)
                if len(md_file.parts) > 2:
                    continue

                # 检查核心文档命名
                if file_stem in core_docs:
                    if not file_stem.isupper():
                        violations.append((str(relative_path), file_stem))
                        issues.append(f"Core doc should be UPPERCASE: {relative_path}")
                        correct_name = file_stem.upper() + '.md'
                        fixes.append({
                            'type': 'rename',
                            'command': f'mv {relative_path} docs/{correct_name}',
                            'description': f'Fix naming: {file_stem} → {file_stem.upper()}'
                        })

        # Scoring: -5分 per violation
        score = max(0, max_score - len(violations) * 5)
        passed = score >= max_score * 0.8

        return ValidationResult(
            score=score,
            max_score=max_score,
            passed=passed,
            issues=issues,
            fixes=fixes
        )

    def validate_adrs(self) -> ValidationResult:
        """验证ADR编号连续性 (15分)

        Returns:
            ValidationResult with score 0-15
        """
        max_score = 15
        issues = []
        fixes = []

        adrs_dir = self.root / 'docs/ADRs'
        if not adrs_dir.exists():
            return ValidationResult(
                score=0,
                max_score=max_score,
                passed=False,
                issues=['ADRs directory not found'],
                fixes=[]
            )

        # 提取ADR编号
        adr_pattern = re.compile(r'^(\d{3})-.*\.md$')
        adr_numbers = []

        for adr_file in adrs_dir.glob('*.md'):
            match = adr_pattern.match(adr_file.name)
            if match:
                adr_numbers.append(int(match.group(1)))

        if not adr_numbers:
            return ValidationResult(
                score=max_score,
                max_score=max_score,
                passed=True,
                issues=[],
                fixes=[]
            )

        # 检查连续性
        adr_numbers.sort()
        gaps = []
        for i in range(1, len(adr_numbers)):
            if adr_numbers[i] != adr_numbers[i-1] + 1:
                gap = adr_numbers[i] - adr_numbers[i-1] - 1
                gaps.append((adr_numbers[i-1], adr_numbers[i], gap))
                issues.append(f"ADR numbering gap: {adr_numbers[i-1]} → {adr_numbers[i]} (missing {gap})")

        # Scoring: -5分 per gap
        score = max(0, max_score - len(gaps) * 5)
        passed = score >= max_score * 0.8

        return ValidationResult(
            score=score,
            max_score=max_score,
            passed=passed,
            issues=issues,
            fixes=fixes
        )

    def run_full_validation(self) -> Dict:
        """运行完整验证

        Returns:
            完整验证结果字典
        """
        results = {
            'structure': self.validate_structure(),
            'files': self.validate_files(),
            'naming': self.validate_naming(),
            'adrs': self.validate_adrs()
        }

        total_score = sum(r.score for r in results.values())
        max_total = sum(r.max_score for r in results.values())

        # 收集所有issues和fixes
        all_issues = []
        all_fixes = []
        for dimension, result in results.items():
            all_issues.extend(result.issues)
            all_fixes.extend(result.fixes)

        return {
            'profile': self.profile,
            'total_score': total_score,
            'max_score': max_total,
            'percentage': round(total_score / max_total * 100, 1),
            'passed': total_score >= max_total * 0.8,
            'breakdown': {
                dim: {
                    'score': res.score,
                    'max': res.max_score,
                    'passed': res.passed
                } for dim, res in results.items()
            },
            'issues_count': len(all_issues),
            'fixes_count': len(all_fixes),
            'issues': all_issues,
            'fixes': all_fixes
        }


def detect_profile(root_path: str = '.') -> str:
    """自动检测项目profile (Issue #481: Use shared config reader)

    Uses shared config reader (CLAUDE.md → project-profile.md)

    Args:
        root_path: 项目根目录

    Returns:
        检测到的profile名称
    """
    try:
        profile_obj = read_profile(Path(root_path))
        return profile_obj.name
    except ProfileError:
        # Fallback: No profile config found
        return 'minimal'


def output_human_readable(result: Dict, verbose: bool = False):
    """输出人类可读的报告

    Args:
        result: 验证结果字典
        verbose: 是否显示详细信息
    """
    # Header
    print("\n" + "="*60)
    print(f"📋 Documentation Structure Validation Report")
    print("="*60)

    # Summary
    status_emoji = "✅" if result['passed'] else "❌"
    print(f"\n{status_emoji} Overall Score: {result['total_score']}/{result['max_score']} ({result['percentage']}%)")
    print(f"Profile: {result['profile']}")
    print(f"Issues: {result['issues_count']} | Fixes available: {result['fixes_count']}")

    # Breakdown
    print("\n📊 Dimension Breakdown:")
    for dim, data in result['breakdown'].items():
        status = "✅" if data['passed'] else "⚠️"
        print(f"  {status} {dim.capitalize():12} {data['score']:2}/{data['max']:2}")

    # Issues
    if result['issues']:
        print(f"\n⚠️  Issues Found ({len(result['issues'])}):")
        for issue in result['issues'][:10 if not verbose else None]:
            print(f"  - {issue}")
        if not verbose and len(result['issues']) > 10:
            print(f"  ... and {len(result['issues']) - 10} more (use --verbose)")

    # Fixes
    if result['fixes']:
        print(f"\n🔧 Suggested Fixes ({len(result['fixes'])}):")
        for fix in result['fixes'][:5 if not verbose else None]:
            print(f"  {fix['command']}")
            if verbose:
                print(f"    → {fix['description']}")
        if not verbose and len(result['fixes']) > 5:
            print(f"  ... and {len(result['fixes']) - 5} more (use --verbose)")
        print(f"\n💡 Auto-fix: python check_docs.py --fix")

    print("\n" + "="*60 + "\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Validate documentation structure compliance'
    )
    parser.add_argument(
        '--profile',
        choices=['tauri', 'tauri-aws', 'nextjs-aws', 'minimal'],
        help='Project profile (auto-detected if not specified)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output JSON format'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Automatically fix issues (NOT IMPLEMENTED YET)'
    )
    parser.add_argument(
        '--root',
        default='.',
        help='Project root directory (default: current directory)'
    )

    args = parser.parse_args()

    # Detect or use provided profile
    profile = args.profile or detect_profile(args.root)

    # Run validation
    checker = DocsChecker(profile=profile, root_path=args.root)
    result = checker.run_full_validation()

    # Output results
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        output_human_readable(result, verbose=args.verbose)

    # Exit code: 0 if passed, 1 if failed
    sys.exit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
