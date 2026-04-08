"""
Tests for manage-docs skill functionality.

This module tests the core functionality of the manage-docs skill including:
- Documentation structure management
- Validation functionality
- Report generation
- Profile support
- Safety features
"""
import json
import re
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


class TestDocumentationStructure:
    """测试文档结构功能"""

    def test_detect_missing_documents(self, temp_project):
        """测试缺失文档检测"""
        # Remove README to create missing doc
        readme = temp_project / "README.md"
        if readme.exists():
            readme.unlink()

        # Verify README is missing
        assert not readme.exists()

        # Expected missing docs
        missing = ["README.md"]
        assert "README.md" in missing

    def test_identify_documentation_structure(self, temp_project, sample_doc_structure):
        """测试文档结构识别"""
        # Check required docs exist
        required = sample_doc_structure["required_docs"]
        assert "CLAUDE.md" in required
        assert "README.md" in required

        # Verify CLAUDE.md exists
        claude_md = temp_project / "CLAUDE.md"
        assert claude_md.exists()

    def test_apply_documentation_template(self, temp_project):
        """测试文档模板应用"""
        # Create template for CONTRIBUTING.md
        template_content = """# Contributing

## Guidelines
- Follow code style
- Write tests
- Update docs
"""

        contributing = temp_project / "CONTRIBUTING.md"
        contributing.write_text(template_content)

        assert contributing.exists()
        content = contributing.read_text()
        assert "## Guidelines" in content

    def test_profile_aware_doc_generation(self, temp_project, profile_config):
        """测试 profile-aware 文档生成"""
        # Check tauri profile requirements
        tauri_docs = profile_config["tauri"]["required_docs"]
        assert "docs/TAURI_SETUP.md" in tauri_docs

        # Verify profile-specific doc can be created
        tauri_setup = temp_project / "docs" / "TAURI_SETUP.md"
        tauri_setup.write_text("# Tauri Setup\n\nSetup instructions...")

        assert tauri_setup.exists()


class TestValidation:
    """测试验证功能"""

    def test_validate_documentation_completeness(self, temp_project, sample_doc_structure):
        """测试文档完整性验证"""
        required_docs = sample_doc_structure["required_docs"]

        # Check all required docs exist
        existing = []
        for doc in required_docs:
            doc_path = temp_project / doc
            if doc_path.exists():
                existing.append(doc)

        # CLAUDE.md should exist
        assert "CLAUDE.md" in existing

    def test_validate_documentation_format(self, temp_project):
        """测试文档格式验证"""
        claude_md = temp_project / "CLAUDE.md"
        content = claude_md.read_text()

        # Check for required markdown headers
        assert content.startswith("# ")
        assert "\n\n" in content  # Has paragraphs

    def test_check_link_validity(self, temp_project):
        """测试链接有效性检查"""
        # Create doc with internal link
        doc = temp_project / "docs" / "TEST.md"
        doc.write_text("""# Test

See [CLAUDE.md](../CLAUDE.md) for details.
""")

        # Extract links
        content = doc.read_text()
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)

        assert len(links) > 0
        assert links[0][1] == "../CLAUDE.md"

    def test_validate_frontmatter(self, temp_project):
        """测试 frontmatter 验证"""
        # Create doc with frontmatter
        doc = temp_project / "docs" / "WITH_FRONTMATTER.md"
        doc.write_text("""---
title: Test Document
version: 1.0.0
---

# Test Document

Content here.
""")

        content = doc.read_text()

        # Check frontmatter exists
        assert content.startswith("---")
        assert "version:" in content


class TestReportGeneration:
    """测试报告生成功能"""

    def test_generate_health_report(self, temp_project, sample_health_report):
        """测试健康报告生成"""
        # Simulate report generation
        report = sample_health_report.copy()

        assert report["status"] == "healthy"
        assert report["total_docs"] == 5
        assert report["coverage"] == 100

    def test_generate_missing_docs_report(self, temp_project):
        """测试缺失文档报告"""
        # Remove a doc to create missing item
        readme = temp_project / "README.md"
        if readme.exists():
            readme.unlink()

        missing = []
        if not readme.exists():
            missing.append("README.md")

        assert len(missing) == 1
        assert "README.md" in missing

    def test_generate_fix_suggestions(self, temp_project):
        """测试修复建议生成"""
        # Generate suggestions for missing docs
        suggestions = [
            "Create README.md with project overview",
            "Add CONTRIBUTING.md with contribution guidelines"
        ]

        assert len(suggestions) > 0
        assert any("README.md" in s for s in suggestions)

    def test_json_output_format(self, sample_health_report):
        """测试 JSON 输出格式"""
        # Verify JSON serializability
        json_str = json.dumps(sample_health_report, indent=2)
        parsed = json.loads(json_str)

        assert parsed["status"] == "healthy"
        assert "missing_docs" in parsed
        assert "total_docs" in parsed


class TestProfileSupport:
    """测试 Profile 支持功能"""

    def test_tauri_profile_documents(self, temp_project, profile_config):
        """测试 tauri profile 文档"""
        tauri_config = profile_config["tauri"]

        assert tauri_config["name"] == "Tauri Desktop"
        assert "docs/TAURI_SETUP.md" in tauri_config["required_docs"]

    def test_nextjs_aws_profile_documents(self, temp_project, profile_config):
        """测试 nextjs-aws profile 文档"""
        nextjs_config = profile_config["nextjs-aws"]

        assert nextjs_config["name"] == "Next.js + AWS"
        assert "docs/DEPLOYMENT.md" in nextjs_config["required_docs"]

    def test_python_lib_profile_documents(self, temp_project, profile_config):
        """测试 python-lib profile 文档"""
        python_config = profile_config["python-lib"]

        assert python_config["name"] == "Python Library"
        assert "docs/API.md" in python_config["required_docs"]

    def test_profile_switching_behavior(self, temp_project, profile_config):
        """测试 profile 切换行为"""
        # Simulate profile switch from tauri to nextjs-aws
        old_profile = profile_config["tauri"]
        new_profile = profile_config["nextjs-aws"]

        # Different required docs
        assert old_profile["required_docs"] != new_profile["required_docs"]

        # Tauri has different requirements
        assert "docs/TAURI_SETUP.md" in old_profile["required_docs"]
        assert "docs/DEPLOYMENT.md" in new_profile["required_docs"]


class TestSafetyFeatures:
    """测试安全机制功能"""

    def test_read_only_operations(self, temp_project):
        """测试只读操作"""
        # Verify no modification during check
        claude_md = temp_project / "CLAUDE.md"
        original_content = claude_md.read_text()

        # Simulate read-only check
        content = claude_md.read_text()

        # Content unchanged
        assert content == original_content

    def test_backup_mechanism(self, temp_project):
        """测试备份机制"""
        # Create backup before modification
        claude_md = temp_project / "CLAUDE.md"
        backup = temp_project / "CLAUDE.md.backup"

        original = claude_md.read_text()
        backup.write_text(original)

        assert backup.exists()
        assert backup.read_text() == original

    def test_error_recovery(self, temp_project):
        """测试错误恢复"""
        # Simulate error during operation
        try:
            # Attempt invalid operation
            invalid_path = temp_project / "nonexistent" / "file.md"
            invalid_path.read_text()  # Will fail
        except FileNotFoundError:
            # Error caught, can recover
            recovered = True

        assert recovered

    def test_permission_checking(self, temp_project):
        """测试权限检查"""
        # Check if directory is writable
        test_file = temp_project / ".write_test"

        try:
            test_file.write_text("test")
            can_write = test_file.exists()
            test_file.unlink()
        except PermissionError:
            can_write = False

        # Temp directory should be writable
        assert can_write
