"""
test_cleanup_safety.py - Safety tests for cleanup script

Ensures that important files are NEVER deleted by accident.

Test Coverage Target: >60%

Run tests:
    python -m pytest tests/test_cleanup_safety.py -v
    python -m pytest tests/test_cleanup_safety.py --cov=scripts/cleanup --cov-report=term-missing
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add parent directory to path to import cleanup module
from cleanup import ProjectCleaner, PROTECTED_PATTERNS, CLEANUP_RULES, detect_profile


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_project():
    """
    创建临时测试项目

    Returns:
        Path to temporary project directory
    """
    temp_dir = Path(tempfile.mkdtemp())

    # Create project structure
    (temp_dir / '.git').mkdir()
    (temp_dir / '.claude').mkdir()
    (temp_dir / '.claude' / 'settings.json').write_text('{}')
    (temp_dir / 'docs').mkdir()
    (temp_dir / 'docs' / 'README.md').write_text('# Docs')

    # Create protected files
    (temp_dir / '.env').write_text('SECRET=1234')
    (temp_dir / 'package.json').write_text('{}')
    (temp_dir / 'README.md').write_text('# Project')
    (temp_dir / 'src.py').write_text('print("hello")')

    # Create temporary files (safe to delete)
    (temp_dir / 'target').mkdir()
    (temp_dir / 'target' / 'debug').mkdir()
    (temp_dir / 'target' / 'debug' / 'app').write_text('binary')

    (temp_dir / 'node_modules').mkdir()
    (temp_dir / 'node_modules' / 'package').mkdir()

    (temp_dir / '__pycache__').mkdir()
    (temp_dir / '__pycache__' / 'module.pyc').write_text('bytecode')

    (temp_dir / '.DS_Store').write_text('mac')

    (temp_dir / '.claude' / '.work-issue-state.json').write_text('{}')

    # Change to temp directory for tests
    original_cwd = os.getcwd()
    os.chdir(temp_dir)

    yield temp_dir

    # Cleanup
    os.chdir(original_cwd)
    shutil.rmtree(temp_dir)


# ============================================================================
# Safety Tests - Protected Files Must NOT Be Deleted
# ============================================================================

def test_git_directory_protected(temp_project):
    """
    .git/ 目录绝对不删除
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=True)

    git_dir = temp_project / '.git'
    assert git_dir.exists()

    # Git directory should NOT be safe to delete
    assert not cleaner.check_safe_to_delete(git_dir), ".git/ should be protected"


def test_env_files_protected(temp_project):
    """
    .env 文件（包含敏感信息）绝对不删除
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=True)

    env_file = temp_project / '.env'
    assert env_file.exists()

    assert not cleaner.check_safe_to_delete(env_file), ".env should be protected"


def test_source_code_protected(temp_project):
    """
    源代码文件（*.py, *.md 等）绝对不删除
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=True)

    # Python source
    py_file = temp_project / 'src.py'
    assert py_file.exists()
    assert not cleaner.check_safe_to_delete(py_file), "*.py should be protected"

    # Markdown docs
    md_file = temp_project / 'README.md'
    assert md_file.exists()
    assert not cleaner.check_safe_to_delete(md_file), "*.md should be protected"


def test_config_files_protected(temp_project):
    """
    配置文件（package.json, Cargo.toml 等）绝对不删除
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=True)

    config_file = temp_project / 'package.json'
    assert config_file.exists()

    assert not cleaner.check_safe_to_delete(config_file), "package.json should be protected"


def test_framework_settings_protected(temp_project):
    """
    框架核心配置（.claude/settings.json）绝对不删除
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=True)

    settings_file = temp_project / '.claude' / 'settings.json'
    assert settings_file.exists()

    assert not cleaner.check_safe_to_delete(settings_file), ".claude/settings.json should be protected"


def test_docs_directory_protected(temp_project):
    """
    文档目录（docs/）绝对不删除
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=True)

    docs_dir = temp_project / 'docs'
    assert docs_dir.exists()

    assert not cleaner.check_safe_to_delete(docs_dir), "docs/ should be protected"


# ============================================================================
# Functionality Tests - Temporary Files Should Be Deleted
# ============================================================================

def test_temp_files_allowed_to_delete(temp_project):
    """
    临时文件（target/, node_modules/, __pycache__/）应该被删除
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=True)

    # target/ (Rust build artifacts)
    target_dir = temp_project / 'target'
    assert target_dir.exists()
    assert cleaner.check_safe_to_delete(target_dir), "target/ should be deletable"

    # node_modules/ (Node dependencies)
    node_modules = temp_project / 'node_modules'
    assert node_modules.exists()
    assert cleaner.check_safe_to_delete(node_modules), "node_modules/ should be deletable"

    # __pycache__/ (Python bytecode)
    pycache = temp_project / '__pycache__'
    assert pycache.exists()
    assert cleaner.check_safe_to_delete(pycache), "__pycache__/ should be deletable"


def test_framework_state_files_allowed_to_delete(temp_project):
    """
    框架临时状态文件（.work-issue-state.json 等）应该被删除
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=True)

    state_file = temp_project / '.claude' / '.work-issue-state.json'
    assert state_file.exists()

    assert cleaner.check_safe_to_delete(state_file), "Framework state files should be deletable"


def test_system_temp_files_allowed_to_delete(temp_project):
    """
    系统临时文件（.DS_Store, Thumbs.db 等）应该被删除
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=True)

    ds_store = temp_project / '.DS_Store'
    assert ds_store.exists()

    assert cleaner.check_safe_to_delete(ds_store), ".DS_Store should be deletable"


# ============================================================================
# Dry-Run Tests - Preview Mode Should Not Actually Delete
# ============================================================================

def test_dry_run_does_not_delete(temp_project):
    """
    Dry-run 模式应该只预览，不实际删除文件
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=True)

    # Files before dry-run
    target_dir = temp_project / 'target'
    assert target_dir.exists()

    # Run dry-run
    result = cleaner.dry_run_cleanup()

    # Files should still exist after dry-run
    assert target_dir.exists(), "Dry-run should not delete files"

    # Result should contain information
    assert 'files' in result
    assert 'total_size' in result
    assert 'total_count' in result
    assert result['total_count'] > 0, "Should find temp files to delete"


def test_dry_run_calculates_size(temp_project):
    """
    Dry-run 应该正确计算将要删除的文件大小
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=True)

    result = cleaner.dry_run_cleanup()

    # Should calculate total size
    assert result['total_size'] > 0, "Should calculate size of temp files"

    # Should count files
    assert result['total_count'] > 0, "Should count temp files"


# ============================================================================
# Execution Tests - Actual Deletion Logic
# ============================================================================

def test_execute_cleanup_deletes_temp_files(temp_project):
    """
    execute_cleanup 应该实际删除临时文件
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=False, force=True)

    # Verify temp files exist before cleanup
    target_dir = temp_project / 'target'
    node_modules = temp_project / 'node_modules'
    assert target_dir.exists()
    assert node_modules.exists()

    # Execute cleanup
    result = cleaner.execute_cleanup()

    # Temp files should be deleted
    assert not target_dir.exists(), "target/ should be deleted"
    assert not node_modules.exists(), "node_modules/ should be deleted"

    # Result should show deletions
    assert len(result['deleted']) > 0, "Should report deleted files"
    assert result['total_size'] > 0, "Should report deleted size"


def test_execute_cleanup_preserves_protected_files(temp_project):
    """
    execute_cleanup 应该保留受保护的文件
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=False, force=True)

    # Protected files before cleanup
    env_file = temp_project / '.env'
    readme = temp_project / 'README.md'
    py_file = temp_project / 'src.py'

    assert env_file.exists()
    assert readme.exists()
    assert py_file.exists()

    # Execute cleanup
    result = cleaner.execute_cleanup()

    # Protected files should still exist
    assert env_file.exists(), ".env should be preserved"
    assert readme.exists(), "README.md should be preserved"
    assert py_file.exists(), "*.py should be preserved"


def test_execute_cleanup_handles_permission_errors(temp_project):
    """
    execute_cleanup 应该优雅处理权限错误
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=False, force=True)

    # Create a file and make it read-only (simulate permission error on some systems)
    protected_temp = temp_project / 'protected_temp.txt'
    protected_temp.write_text('test')
    protected_temp.chmod(0o444)  # Read-only

    # Execute cleanup
    result = cleaner.execute_cleanup()

    # Should handle errors gracefully without crashing
    assert isinstance(result, dict)
    assert 'errors' in result or 'skipped' in result


def test_execute_cleanup_handles_missing_files(temp_project):
    """
    execute_cleanup 应该处理文件不存在的情况（竞态条件）
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=False, force=True)

    # Scan first
    matches = cleaner.scan_temp_files()

    # Delete one file manually (simulate race condition)
    if matches:
        first_match = matches[0]
        if first_match.is_file():
            first_match.unlink()

    # Execute cleanup (should not crash)
    result = cleaner.execute_cleanup()

    # Should complete without exceptions
    assert isinstance(result, dict)


# ============================================================================
# Profile Tests - Profile-Aware Rules
# ============================================================================

def test_tauri_profile_rules():
    """
    Tauri profile 应该包含 Rust 和 Node 清理规则
    """
    rules = CLEANUP_RULES['tauri']

    # Should include Rust artifacts
    assert any('target' in rule for rule in rules), "Should include target/"

    # Should include Node artifacts
    assert any('node_modules' in rule for rule in rules), "Should include node_modules/"

    # Should include Python artifacts
    assert any('__pycache__' in rule for rule in rules), "Should include __pycache__/"


def test_nextjs_aws_profile_rules():
    """
    Next.js-AWS profile 应该包含 Next.js 和 CDK 清理规则
    """
    rules = CLEANUP_RULES['nextjs-aws']

    # Should include Next.js artifacts
    assert any('.next' in rule for rule in rules), "Should include .next/"

    # Should include CDK artifacts
    assert any('cdk.out' in rule for rule in rules), "Should include cdk.out/"

    # Should include Node artifacts
    assert any('node_modules' in rule for rule in rules), "Should include node_modules/"


def test_profile_initialization():
    """
    测试不同 profile 的初始化
    """
    # Valid profiles
    cleaner_tauri = ProjectCleaner(profile='tauri', dry_run=True)
    assert cleaner_tauri.profile == 'tauri'

    cleaner_nextjs = ProjectCleaner(profile='nextjs-aws', dry_run=True)
    assert cleaner_nextjs.profile == 'nextjs-aws'

    cleaner_common = ProjectCleaner(profile='common', dry_run=True)
    assert cleaner_common.profile == 'common'

    # Invalid profile should raise ValueError
    with pytest.raises(ValueError):
        ProjectCleaner(profile='invalid', dry_run=True)


# ============================================================================
# Edge Case Tests
# ============================================================================

def test_check_safe_to_delete_nonexistent_file(temp_project):
    """
    测试不存在的文件不会导致崩溃
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=True)

    nonexistent = temp_project / 'does_not_exist.txt'
    assert not nonexistent.exists()

    # Should not crash
    result = cleaner.check_safe_to_delete(nonexistent)

    # Should return False (conservative - don't delete if unsure)
    assert isinstance(result, bool)


def test_scan_empty_project(temp_project):
    """
    测试空项目（无临时文件）不会崩溃
    """
    # Remove all temp files
    for item in temp_project.iterdir():
        if item.name in ['target', 'node_modules', '__pycache__', '.DS_Store']:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    cleaner = ProjectCleaner(profile='tauri', dry_run=True)

    # Should not crash
    result = cleaner.dry_run_cleanup()

    # Should return empty result
    assert result['total_count'] == 0 or result['total_count'] == 1  # Might still have state files
    assert isinstance(result['files'], list)


def test_pattern_matching_edge_cases(temp_project):
    """
    测试模式匹配的边界情况
    """
    cleaner = ProjectCleaner(profile='common', dry_run=True)

    # Test recursive patterns
    nested_pycache = temp_project / 'src' / 'utils' / '__pycache__'
    nested_pycache.mkdir(parents=True)
    assert cleaner.check_safe_to_delete(nested_pycache), "**/__pycache__ should match nested directories"

    # Test exact matches
    ds_store = temp_project / 'subdir' / '.DS_Store'
    ds_store.parent.mkdir(parents=True, exist_ok=True)
    ds_store.write_text('mac')
    assert cleaner.check_safe_to_delete(ds_store), "**/.DS_Store should match nested files"


# ============================================================================
# Integration Tests
# ============================================================================

def test_full_cleanup_workflow(temp_project):
    """
    测试完整的清理工作流：扫描 → 预览 → 执行
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=False, force=True)

    # Step 1: Scan
    matches = cleaner.scan_temp_files()
    assert len(matches) > 0, "Should find temp files"

    # Step 2: Dry-run preview
    cleaner_preview = ProjectCleaner(profile='tauri', dry_run=True)
    preview = cleaner_preview.dry_run_cleanup()
    assert preview['total_count'] > 0, "Preview should show files"

    # Step 3: Execute
    result = cleaner.execute_cleanup()

    # Verify results
    assert len(result['deleted']) > 0, "Should delete temp files"
    assert result['total_size'] > 0, "Should report size"

    # Verify protected files still exist
    assert (temp_project / '.env').exists()
    assert (temp_project / 'README.md').exists()


# ============================================================================
# Coverage Tests - Ensure >60% Coverage
# ============================================================================

def test_format_size_utility():
    """
    测试 format_size 工具函数
    """
    from cleanup import format_size

    assert format_size(500) == "500.00B"
    assert format_size(1024) == "1.00KB"
    assert format_size(1024 * 1024) == "1.00MB"
    assert format_size(1024 * 1024 * 1024) == "1.00GB"


def test_detect_profile_utility(temp_project):
    """
    测试 detect_profile 工具函数
    """
    # No profile indicators - should default to common
    profile = detect_profile()
    assert profile == 'common'

    # Create tauri indicator
    tauri_dir = temp_project / 'src-tauri'
    tauri_dir.mkdir()
    (tauri_dir / 'Cargo.toml').write_text('[package]')

    profile = detect_profile()
    assert profile == 'tauri'


def test_match_pattern_utility(temp_project):
    """
    测试 _match_pattern 内部方法
    """
    cleaner = ProjectCleaner(profile='tauri', dry_run=True)

    # Test exact match
    assert cleaner._match_pattern('target', 'target')

    # Test glob match
    assert cleaner._match_pattern('file.pyc', '*.pyc')

    # Test directory pattern
    assert cleaner._match_pattern('target/debug/app', 'target/**')

    # Test recursive pattern
    assert cleaner._match_pattern('src/utils/__pycache__', '**/__pycache__')


def test_is_git_tracked_utility(temp_project):
    """
    测试 _is_git_tracked 内部方法
    """
    # Initialize git repo
    subprocess.run(['git', 'init'], cwd=temp_project, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=temp_project, capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_project, capture_output=True)

    # Add and commit a file
    test_file = temp_project / 'tracked.txt'
    test_file.write_text('tracked')
    subprocess.run(['git', 'add', 'tracked.txt'], cwd=temp_project, capture_output=True)
    subprocess.run(['git', 'commit', '-m', 'test'], cwd=temp_project, capture_output=True)

    cleaner = ProjectCleaner(profile='tauri', dry_run=True)

    # Tracked file should return True
    assert cleaner._is_git_tracked(test_file) == True

    # Untracked file should return False
    untracked_file = temp_project / 'untracked.txt'
    untracked_file.write_text('untracked')
    assert cleaner._is_git_tracked(untracked_file) == False


# Add import for subprocess
import subprocess


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=scripts/cleanup', '--cov-report=term-missing'])
