#!/usr/bin/env python3
"""
cleanup.py - Project cleanup script with safety mechanisms

ADR-014 compliant script for cleaning temporary files with
whitelist/blacklist protection to prevent accidental deletion.

Usage:
    python cleanup.py --profile tauri --dry-run
    python cleanup.py --profile nextjs-aws
    python cleanup.py --health-check
"""

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Tuple
import fnmatch

# Import shared config reader (Issue #481)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from _scripts.utils.config import read_profile, ProfileError


# ============================================================================
# Safety Protection: Whitelist (MUST NOT DELETE)
# ============================================================================

PROTECTED_PATTERNS = [
    # Git repository
    '.git',
    '.git/**',

    # Framework settings
    '.claude/settings.json',

    # Environment secrets
    '.env',
    '.env.*',

    # Source code (all languages)
    '*.py',
    '*.md',
    '*.ts',
    '*.tsx',
    '*.rs',
    '*.js',
    '*.jsx',

    # Configuration files
    'package.json',
    'Cargo.toml',
    'pyproject.toml',
    'tsconfig.json',

    # Documentation
    'docs',
    'docs/**',
    'README.md',
    'CLAUDE.md',

    # Skills and rules (framework core)
    '.claude/skills',
    '.claude/skills/**',
    '.claude/rules',
    '.claude/rules/**',
]


# ============================================================================
# Cleanup Rules: Blacklist (ALLOWED TO DELETE) - Profile-Aware
# ============================================================================

CLEANUP_RULES = {
    'tauri': [
        'target',
        'target/**',
        'src-tauri/target',
        'src-tauri/target/**',
        'node_modules',
        'node_modules/**',
        '**/.DS_Store',
        '**/__pycache__',
        '**/__pycache__/**',
        '**/*.pyc',
        '**/.pytest_cache',
        '**/.pytest_cache/**',
        'logs/*.log',
        '.claude/.work-issue-state.json',
        '.claude/.review-status.json',
        '.claude/.eval-plan-status.json',
    ],
    'nextjs-aws': [
        '.next',
        '.next/**',
        'out',
        'out/**',
        'cdk.out',
        'cdk.out/**',
        'node_modules',
        'node_modules/**',
        '.cache',
        '.cache/**',
        '**/.DS_Store',
        'logs/*.log',
        '.claude/.work-issue-state.json',
        '.claude/.review-status.json',
        '.claude/.eval-plan-status.json',
    ],
    'common': [
        '**/.DS_Store',
        '**/Thumbs.db',
        '**/desktop.ini',
        '**/__pycache__',
        '**/__pycache__/**',
        '**/*.pyc',
        '**/.pytest_cache',
        '**/.pytest_cache/**',
        '.claude/.work-issue-state.json',
        '.claude/.review-status.json',
        '.claude/.eval-plan-status.json',
    ]
}


# ============================================================================
# ProjectCleaner Class
# ============================================================================

class ProjectCleaner:
    """
    核心清理类 - 扫描、检查、删除临时文件

    ADR-014 compliant: Script-based pattern with safety mechanisms
    """

    def __init__(self, profile: str, dry_run: bool = False, force: bool = False):
        """
        初始化 ProjectCleaner

        Args:
            profile: "tauri" | "nextjs-aws" | "common"
            dry_run: 仅预览，不实际删除
            force: 跳过确认提示
        """
        if profile not in CLEANUP_RULES:
            raise ValueError(f"Invalid profile: {profile}. Must be one of: {list(CLEANUP_RULES.keys())}")

        self.profile = profile
        self.dry_run = dry_run
        self.force = force
        self.root = Path.cwd()

    def scan_temp_files(self) -> List[Path]:
        """
        扫描临时文件（基于 profile 规则）

        Returns:
            匹配的文件/目录路径列表
        """
        patterns = CLEANUP_RULES[self.profile]
        matches = []

        for pattern in patterns:
            # 使用 glob 查找匹配文件
            if '**' in pattern:
                # 递归匹配
                found = list(self.root.glob(pattern))
            else:
                # 单层匹配
                found = list(self.root.glob(pattern))

            # 过滤：跳过已被保护的文件
            for file_path in found:
                if self.check_safe_to_delete(file_path):
                    matches.append(file_path)

        # 去重并排序
        matches = sorted(set(matches))

        return matches

    def check_safe_to_delete(self, file: Path) -> bool:
        """
        安全检查 - 防止误删重要文件

        Args:
            file: 待检查的文件路径

        Returns:
            True 如果安全（可以删除）
            False 如果不安全（应跳过）
        """
        # Convert to relative path for pattern matching
        try:
            rel_path = file.relative_to(self.root)
        except ValueError:
            # File is outside project root
            return False

        rel_path_str = str(rel_path)

        # Step 1: Whitelist check (highest priority)
        for protected in PROTECTED_PATTERNS:
            if self._match_pattern(rel_path_str, protected):
                return False  # 绝对不删除

        # Step 2: Check if file is git-tracked
        if self._is_git_tracked(file):
            return False  # Git tracked files are protected

        # Step 3: Blacklist check (allowed to delete)
        cleanup_patterns = CLEANUP_RULES[self.profile]
        for pattern in cleanup_patterns:
            if self._match_pattern(rel_path_str, pattern):
                return True  # 可以删除

        # Step 4: 未匹配任何规则 - 默认不删除（保守策略）
        return False

    def _match_pattern(self, path_str: str, pattern: str) -> bool:
        """
        匹配 glob 模式

        Args:
            path_str: 文件路径字符串
            pattern: Glob 模式

        Returns:
            True 如果匹配
        """
        # Handle exact matches first
        if path_str == pattern or str(Path(path_str)) == str(Path(pattern)):
            return True

        # Handle glob patterns
        if fnmatch.fnmatch(path_str, pattern):
            return True

        # Handle directory patterns (e.g., "target/**")
        if pattern.endswith('/**'):
            dir_pattern = pattern[:-3]  # Remove '/**'
            if path_str.startswith(dir_pattern + '/') or path_str == dir_pattern:
                return True

        # Handle recursive patterns (e.g., "**/.DS_Store")
        if pattern.startswith('**/'):
            file_pattern = pattern[3:]  # Remove '**/'
            if fnmatch.fnmatch(Path(path_str).name, file_pattern):
                return True
            # Also check full path match
            if fnmatch.fnmatch(path_str, f'*/{file_pattern}'):
                return True

        return False

    def _is_git_tracked(self, file: Path) -> bool:
        """
        检查文件是否被 git 追踪

        Args:
            file: 文件路径

        Returns:
            True 如果被 git 追踪
        """
        try:
            result = subprocess.run(
                ['git', 'ls-files', '--error-unmatch', str(file)],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Git not available or timeout - assume not tracked
            return False

    def dry_run_cleanup(self) -> Dict:
        """
        预览模式 - 显示将要删除的文件

        Returns:
            {
                "files": List[str],
                "total_size": int (bytes),
                "total_count": int
            }
        """
        matches = self.scan_temp_files()

        total_size = 0
        files_info = []

        for file_path in matches:
            try:
                if file_path.is_dir():
                    # 目录：计算总大小
                    size = sum(f.stat().st_size for f in file_path.rglob('*') if f.is_file())
                elif file_path.is_file():
                    size = file_path.stat().st_size
                else:
                    size = 0

                total_size += size
                files_info.append(str(file_path))
            except (OSError, PermissionError):
                # 无法访问，跳过
                continue

        return {
            "files": files_info,
            "total_size": total_size,
            "total_count": len(files_info)
        }

    def execute_cleanup(self) -> Dict:
        """
        执行清理 - 实际删除文件

        Returns:
            {
                "deleted": List[str],
                "skipped": List[str],
                "errors": List[str],
                "total_size": int (bytes)
            }
        """
        if self.dry_run:
            raise RuntimeError("Cannot execute_cleanup in dry_run mode. Use dry_run_cleanup() instead.")

        matches = self.scan_temp_files()

        # Confirmation prompt (unless --force)
        if not self.force and matches:
            print(f"\n⚠️  About to delete {len(matches)} items.")
            response = input("Confirm deletion? [y/N] ")
            if response.lower() != 'y':
                return {
                    "deleted": [],
                    "skipped": [str(f) for f in matches],
                    "errors": [],
                    "total_size": 0
                }

        deleted = []
        skipped = []
        errors = []
        total_size = 0

        for file_path in matches:
            try:
                # Calculate size before deletion
                if file_path.is_dir():
                    size = sum(f.stat().st_size for f in file_path.rglob('*') if f.is_file())
                elif file_path.is_file():
                    size = file_path.stat().st_size
                else:
                    size = 0

                # Delete
                if file_path.is_dir():
                    shutil.rmtree(file_path)
                elif file_path.is_file():
                    file_path.unlink()
                else:
                    # Broken symlink or special file
                    file_path.unlink(missing_ok=True)

                deleted.append(str(file_path))
                total_size += size

            except PermissionError as e:
                errors.append(f"{file_path}: Permission denied")
            except FileNotFoundError:
                # File already deleted (race condition)
                skipped.append(str(file_path))
            except Exception as e:
                errors.append(f"{file_path}: {str(e)}")

        return {
            "deleted": deleted,
            "skipped": skipped,
            "errors": errors,
            "total_size": total_size
        }


# ============================================================================
# Utility Functions
# ============================================================================

def detect_profile() -> str:
    """
    自动检测项目 profile (Issue #481: Use shared config reader)

    Uses shared config reader with fallback detection.

    Returns:
        "tauri" | "nextjs-aws" | "common"
    """
    # Method 1: Use shared config reader (CLAUDE.md → project-profile.md)
    try:
        profile_obj = read_profile()
        return profile_obj.name
    except ProfileError:
        # Fallback: No profile config found, detect from project structure
        pass

    # Method 2: Detect feature files
    if Path('src-tauri/Cargo.toml').exists():
        return 'tauri'
    elif Path('.next').exists() or Path('cdk.json').exists():
        return 'nextjs-aws'

    # Fallback: common
    return 'common'


def format_size(bytes_size: int) -> str:
    """
    格式化文件大小

    Args:
        bytes_size: 字节数

    Returns:
        人类可读的大小字符串（如 "1.5GB"）
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(bytes_size)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{size:.2f}{units[unit_index]}"


def health_check():
    """
    健康检查 - 查找大文件是否被 ignore
    """
    print("\n🔍 Health Check - Large Files\n")

    # Find large files (>10MB)
    try:
        result = subprocess.run(
            ["find", ".", "-type", "f", "-size", "+10M"],
            capture_output=True,
            text=True,
            timeout=30
        )
        large_files = [f for f in result.stdout.strip().split('\n') if f]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  find command not available or timed out")
        return

    issues = []
    for file in large_files:
        # Check if ignored by git
        try:
            result = subprocess.run(
                ['git', 'check-ignore', '-q', file],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                # Not ignored
                size = os.path.getsize(file)
                issues.append((file, size))
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue

    if issues:
        print(f"⚠️  Found {len(issues)} large unignored files:\n")
        for file, size in issues[:10]:  # Show first 10
            print(f"  - {file} ({format_size(size)})")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
        print("\nRecommendation: Add these to .gitignore if they're build artifacts")
    else:
        print("✅ All large files are properly ignored")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Clean temporary files with safety mechanisms (ADR-014)'
    )
    parser.add_argument(
        '--profile',
        choices=['tauri', 'nextjs-aws', 'common'],
        help='Project profile (auto-detected if not specified)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be deleted without actually deleting'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompts'
    )
    parser.add_argument(
        '--health-check',
        action='store_true',
        help='Check for large unignored files'
    )

    args = parser.parse_args()

    # Health check mode
    if args.health_check:
        health_check()
        return 0

    # Detect or use specified profile
    profile = args.profile or detect_profile()
    print(f"\n🧹 Project Cleanup\n")
    print(f"📋 Profile: {profile}")

    # Initialize cleaner
    cleaner = ProjectCleaner(profile=profile, dry_run=args.dry_run, force=args.force)

    # Execute cleanup
    if args.dry_run:
        print(f"\n🔍 Scanning for temporary files (DRY RUN)...\n")
        result = cleaner.dry_run_cleanup()

        if result['files']:
            print(f"Would delete {result['total_count']} items ({format_size(result['total_size'])}):\n")
            for file in result['files'][:20]:  # Show first 20
                print(f"  - {file}")
            if len(result['files']) > 20:
                print(f"  ... and {len(result['files']) - 20} more")
            print(f"\nRun without --dry-run to actually delete these files")
        else:
            print("✅ No temporary files found")

    else:
        print(f"\n🗑️  Cleaning temporary files...\n")
        result = cleaner.execute_cleanup()

        if result['deleted']:
            print(f"✅ Deleted {len(result['deleted'])} items ({format_size(result['total_size'])})")
        else:
            print("✅ No files to delete")

        if result['skipped']:
            print(f"\n⚠️  Skipped {len(result['skipped'])} items")

        if result['errors']:
            print(f"\n❌ Errors ({len(result['errors'])}):")
            for error in result['errors'][:5]:
                print(f"  - {error}")
            if len(result['errors']) > 5:
                print(f"  ... and {len(result['errors']) - 5} more")

    return 0


if __name__ == '__main__':
    sys.exit(main())
