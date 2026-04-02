#!/usr/bin/env python3
"""
test_check_docs.py - Unit tests for check_docs.py

测试覆盖:
1. validate_structure() - 目录验证
2. validate_files() - 文件验证
3. validate_naming() - 命名规范验证
4. validate_adrs() - ADR编号验证
5. run_full_validation() - 完整workflow
6. detect_profile() - Profile检测

目标覆盖率: ≥80%
"""

import json
import pytest
import tempfile
from pathlib import Path
import sys
import os

# Add scripts to path

from check_docs import DocsChecker, detect_profile, ValidationResult


@pytest.fixture
def temp_project():
    """创建临时项目目录用于测试"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def complete_project(temp_project):
    """创建完整的文档结构 (用于正向测试)"""
    # 创建必需目录
    dirs = [
        'docs',
        'docs/ADRs',
        'docs/architecture',
        'docs/api',
        'docs/guides',
        'docs/diagrams'
    ]
    for dir_path in dirs:
        (temp_project / dir_path).mkdir(parents=True, exist_ok=True)

    # 创建必需文件
    files = [
        'docs/README.md',
        'docs/PRD.md',
        'docs/ARCHITECTURE.md',
        'docs/API.md',
        'docs/SETUP.md',
        'docs/TEST_PLAN.md',
    ]
    for file_path in files:
        (temp_project / file_path).write_text('# Placeholder\n')

    # 创建连续的ADRs
    adr_files = [
        'docs/ADRs/001-first-decision.md',
        'docs/ADRs/002-second-decision.md',
        'docs/ADRs/003-third-decision.md',
    ]
    for adr_path in adr_files:
        (temp_project / adr_path).write_text('# ADR\n')

    return temp_project


class TestDocsChecker:
    """DocsChecker类的单元测试"""

    def test_init_default_profile(self, temp_project):
        """测试默认profile初始化"""
        checker = DocsChecker(profile='minimal', root_path=str(temp_project))
        assert checker.profile == 'minimal'
        assert len(checker.required_dirs) == 6  # BASE_DIRS

    def test_init_tauri_profile(self, temp_project):
        """测试tauri profile初始化"""
        checker = DocsChecker(profile='tauri', root_path=str(temp_project))
        assert checker.profile == 'tauri'
        assert 'docs/desktop/' in checker.required_dirs
        assert len(checker.required_files) == 6  # tauri files

    def test_validate_structure_all_present(self, complete_project):
        """测试结构验证 - 所有目录存在"""
        checker = DocsChecker(profile='minimal', root_path=str(complete_project))
        result = checker.validate_structure()

        assert result.score == 30  # Full score
        assert result.max_score == 30
        assert result.passed is True
        assert len(result.issues) == 0
        assert len(result.fixes) == 0

    def test_validate_structure_missing_dirs(self, temp_project):
        """测试结构验证 - 缺失目录"""
        # 只创建部分目录
        (temp_project / 'docs').mkdir()

        checker = DocsChecker(profile='minimal', root_path=str(temp_project))
        result = checker.validate_structure()

        assert result.score < 30  # Deduction for missing dirs
        assert result.passed is False
        assert len(result.issues) == 5  # 5个缺失目录
        assert len(result.fixes) == 5  # 5个修复建议
        assert result.fixes[0]['type'] == 'mkdir'

    def test_validate_files_all_present(self, complete_project):
        """测试文件验证 - 所有文件存在"""
        checker = DocsChecker(profile='tauri', root_path=str(complete_project))
        result = checker.validate_files()

        assert result.score == 40  # Full score
        assert result.passed is True
        assert len(result.issues) == 0

    def test_validate_files_missing(self, temp_project):
        """测试文件验证 - 缺失文件"""
        # 创建目录但不创建文件
        (temp_project / 'docs').mkdir()

        checker = DocsChecker(profile='tauri', root_path=str(temp_project))
        result = checker.validate_files()

        assert result.score == 0  # No files present
        assert result.passed is False
        assert len(result.issues) == 6  # 6个缺失文件
        assert len(result.fixes) == 1  # 1个init-docs修复建议
        assert result.fixes[0]['type'] == 'init-docs'

    def test_validate_naming_correct(self, complete_project):
        """测试命名验证 - 正确命名"""
        checker = DocsChecker(profile='tauri', root_path=str(complete_project))
        result = checker.validate_naming()

        assert result.score == 15  # Full score
        assert result.passed is True
        assert len(result.issues) == 0

    def test_validate_naming_incorrect(self, temp_project):
        """测试命名验证 - 错误命名"""
        docs_dir = temp_project / 'docs'
        docs_dir.mkdir()

        # 创建错误命名的核心文档 (应为UPPERCASE)
        (docs_dir / 'readme.md').write_text('# README\n')
        (docs_dir / 'Prd.md').write_text('# PRD\n')

        checker = DocsChecker(profile='minimal', root_path=str(temp_project))
        result = checker.validate_naming()

        assert result.score < 15  # Deduction for violations
        assert result.passed is False
        assert len(result.issues) == 2  # 2个命名违规
        assert len(result.fixes) == 2  # 2个重命名建议
        assert result.fixes[0]['type'] == 'rename'

    def test_validate_adrs_sequential(self, complete_project):
        """测试ADR验证 - 连续编号"""
        checker = DocsChecker(profile='minimal', root_path=str(complete_project))
        result = checker.validate_adrs()

        assert result.score == 15  # Full score
        assert result.passed is True
        assert len(result.issues) == 0

    def test_validate_adrs_gaps(self, temp_project):
        """测试ADR验证 - 编号断档"""
        adrs_dir = temp_project / 'docs/ADRs'
        adrs_dir.mkdir(parents=True)

        # 创建有断档的ADR编号
        (adrs_dir / '001-first.md').write_text('# ADR 1\n')
        (adrs_dir / '003-third.md').write_text('# ADR 3\n')  # 缺002
        (adrs_dir / '005-fifth.md').write_text('# ADR 5\n')  # 缺004

        checker = DocsChecker(profile='minimal', root_path=str(temp_project))
        result = checker.validate_adrs()

        assert result.score < 15  # Deduction for gaps
        assert result.passed is False
        assert len(result.issues) == 2  # 2个断档
        assert '001 → 003' in result.issues[0]

    def test_validate_adrs_no_adrs(self, temp_project):
        """测试ADR验证 - 无ADR (边界情况)"""
        adrs_dir = temp_project / 'docs/ADRs'
        adrs_dir.mkdir(parents=True)

        checker = DocsChecker(profile='minimal', root_path=str(temp_project))
        result = checker.validate_adrs()

        # 无ADR时应通过 (空集合无断档)
        assert result.score == 15
        assert result.passed is True

    def test_run_full_validation_complete(self, complete_project):
        """测试完整验证 - 完整项目"""
        checker = DocsChecker(profile='tauri', root_path=str(complete_project))
        result = checker.run_full_validation()

        assert result['total_score'] == 100  # Perfect score
        assert result['percentage'] == 100.0
        assert result['passed'] is True
        assert result['issues_count'] == 0
        assert result['fixes_count'] == 0

    def test_run_full_validation_partial(self, temp_project):
        """测试完整验证 - 部分缺失"""
        # 创建部分结构
        docs_dir = temp_project / 'docs'
        docs_dir.mkdir()
        (docs_dir / 'README.md').write_text('# README\n')

        checker = DocsChecker(profile='minimal', root_path=str(temp_project))
        result = checker.run_full_validation()

        assert result['total_score'] < 100  # Deductions
        assert result['percentage'] < 100.0
        assert result['passed'] is False  # <80%
        assert result['issues_count'] > 0
        assert result['fixes_count'] > 0

    def test_breakdown_structure(self, complete_project):
        """测试结果breakdown结构"""
        checker = DocsChecker(profile='minimal', root_path=str(complete_project))
        result = checker.run_full_validation()

        assert 'breakdown' in result
        assert 'structure' in result['breakdown']
        assert 'files' in result['breakdown']
        assert 'naming' in result['breakdown']
        assert 'adrs' in result['breakdown']

        # 检查breakdown内容
        for dim in result['breakdown'].values():
            assert 'score' in dim
            assert 'max' in dim
            assert 'passed' in dim


class TestDetectProfile:
    """detect_profile函数的单元测试"""

    def test_detect_profile_from_file(self, temp_project):
        """测试从project-profile.md检测"""
        profile_file = temp_project / 'docs/project-profile.md'
        profile_file.parent.mkdir(parents=True, exist_ok=True)

        profile_data = {'profile': 'tauri', 'version': '1.0'}
        profile_file.write_text(json.dumps(profile_data))

        profile = detect_profile(str(temp_project))
        assert profile == 'tauri'

    def test_detect_profile_fallback(self, temp_project):
        """测试检测失败fallback"""
        # 无project-profile.md
        profile = detect_profile(str(temp_project))
        assert profile == 'minimal'  # Fallback

    def test_detect_profile_invalid_json(self, temp_project):
        """测试损坏的profile文件"""
        profile_file = temp_project / 'docs/project-profile.md'
        profile_file.parent.mkdir(parents=True, exist_ok=True)
        profile_file.write_text('invalid json {')

        profile = detect_profile(str(temp_project))
        assert profile == 'minimal'  # Fallback


class TestValidationResult:
    """ValidationResult数据类的测试"""

    def test_validation_result_creation(self):
        """测试ValidationResult创建"""
        result = ValidationResult(
            score=25,
            max_score=30,
            passed=True,
            issues=['Issue 1'],
            fixes=[{'type': 'mkdir', 'command': 'mkdir -p docs/'}]
        )

        assert result.score == 25
        assert result.max_score == 30
        assert result.passed is True
        assert len(result.issues) == 1
        assert len(result.fixes) == 1


class TestEdgeCases:
    """边界情况和错误处理测试"""

    def test_empty_project(self, temp_project):
        """测试完全空的项目"""
        checker = DocsChecker(profile='minimal', root_path=str(temp_project))
        result = checker.run_full_validation()

        assert result['total_score'] == 0  # Nothing exists
        assert result['passed'] is False

    def test_nonexistent_root(self):
        """测试不存在的根目录"""
        checker = DocsChecker(profile='minimal', root_path='/nonexistent/path')

        # 应该不抛异常，而是返回0分
        result = checker.validate_structure()
        assert result.score == 0

    def test_special_characters_in_filenames(self, temp_project):
        """测试文件名中的特殊字符"""
        docs_dir = temp_project / 'docs'
        docs_dir.mkdir()

        # 创建带特殊字符的文件
        (docs_dir / 'file-with-special_chars.md').write_text('# Test\n')

        checker = DocsChecker(profile='minimal', root_path=str(temp_project))
        result = checker.validate_naming()

        # 应能正常处理
        assert isinstance(result, ValidationResult)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=check_docs', '--cov-report=term-missing'])
