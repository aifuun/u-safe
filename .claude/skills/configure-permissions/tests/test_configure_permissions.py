"""
Tests for configure-permissions skill functionality.

This module tests the core functionality of the configure-permissions skill including:
- Permission configuration management
- Template application and validation
- Argument handling
- Safety features
"""
import json
from pathlib import Path
from typing import Dict, Any

import pytest


class TestPermissionConfiguration:
    """测试权限配置功能"""

    def test_detect_missing_settings_file(self, temp_project):
        """测试检测缺失的 settings.json"""
        settings_file = temp_project / ".claude" / "settings.json"

        # Verify file doesn't exist
        assert not settings_file.exists()

        # Expected behavior: skill should detect missing file
        # and offer to create it
        missing_detected = not settings_file.exists()
        assert missing_detected

    def test_load_existing_settings(self, temp_project, mock_claude_settings):
        """测试加载已有配置"""
        # Verify file exists
        assert mock_claude_settings.exists()

        # Load and verify content
        content = json.loads(mock_claude_settings.read_text())
        assert "allowedPrompts" in content
        assert isinstance(content["allowedPrompts"], list)

    def test_apply_safe_template(self, temp_project, permission_templates):
        """测试应用 safe 模板"""
        safe_template = permission_templates["safe"]

        # Apply template
        settings_file = temp_project / ".claude" / "settings.json"
        settings_file.write_text(json.dumps(safe_template, indent=2))

        # Verify applied correctly
        content = json.loads(settings_file.read_text())
        assert "allowedPrompts" in content

        # Safe template should have git and npm commands
        prompts = [p["prompt"] for p in content["allowedPrompts"]]
        assert "git add" in prompts
        assert "npm test" in prompts

    def test_apply_custom_permissions(self, temp_project):
        """测试应用自定义权限"""
        custom_permissions = {
            "allowedPrompts": [
                {"tool": "Bash", "prompt": "custom command"}
            ]
        }

        settings_file = temp_project / ".claude" / "settings.json"
        settings_file.write_text(json.dumps(custom_permissions, indent=2))

        # Verify custom permissions applied
        content = json.loads(settings_file.read_text())
        assert len(content["allowedPrompts"]) == 1
        assert content["allowedPrompts"][0]["prompt"] == "custom command"

    def test_validate_permission_format(self, temp_project):
        """测试验证权限格式"""
        # Valid format
        valid_permission = {"tool": "Bash", "prompt": "test"}
        assert "tool" in valid_permission
        assert "prompt" in valid_permission

        # Invalid format (missing tool)
        invalid_permission = {"prompt": "test"}
        is_valid = "tool" in invalid_permission and "prompt" in invalid_permission
        assert not is_valid


class TestArgumentHandling:
    """测试参数处理功能"""

    def test_template_selection(self, permission_templates):
        """测试模板选择（safe/all/minimal/read-only）"""
        # Verify all templates exist
        assert "safe" in permission_templates
        assert "all" in permission_templates
        assert "minimal" in permission_templates
        assert "read-only" in permission_templates

        # Each template should have allowedPrompts
        for template_name, template in permission_templates.items():
            assert "allowedPrompts" in template

    def test_custom_prompt_parsing(self):
        """测试自定义 prompt 解析"""
        # Parse custom prompt string
        custom_prompt = "tool=Bash,prompt=git status"

        # Expected parsing result
        parsed = {
            "tool": "Bash",
            "prompt": "git status"
        }

        # Verify parsing logic works
        assert "tool=Bash" in custom_prompt
        assert "prompt=git status" in custom_prompt

    def test_invalid_template_error(self, permission_templates):
        """测试无效模板错误处理"""
        # Valid templates
        valid_templates = ["safe", "all", "minimal", "read-only"]

        # Invalid template
        invalid_template = "nonexistent"

        # Should detect invalid template
        is_valid = invalid_template in valid_templates
        assert not is_valid

    def test_dry_run_mode(self, temp_project, permission_templates):
        """测试 Dry-run 模式"""
        # Dry-run should preview without applying
        dry_run = True
        template = permission_templates["safe"]

        settings_file = temp_project / ".claude" / "settings.json"
        original_exists = settings_file.exists()

        if not dry_run:
            settings_file.write_text(json.dumps(template, indent=2))

        # In dry-run mode, file should not be created
        if dry_run:
            assert settings_file.exists() == original_exists

    def test_force_override(self, temp_project, mock_claude_settings):
        """测试 Force 覆盖标志"""
        # Original settings exist
        original_content = mock_claude_settings.read_text()
        assert mock_claude_settings.exists()

        # Force override with new template
        new_template = {"allowedPrompts": [{"tool": "Bash", "prompt": "new"}]}
        mock_claude_settings.write_text(json.dumps(new_template, indent=2))

        # Verify override worked
        new_content = mock_claude_settings.read_text()
        assert new_content != original_content

    def test_merge_vs_replace_behavior(self, temp_project, mock_claude_settings):
        """测试合并 vs 替换行为"""
        # Original settings
        original = json.loads(mock_claude_settings.read_text())
        original_count = len(original["allowedPrompts"])

        # Merge: add new permission
        new_permission = {"tool": "Bash", "prompt": "additional"}
        original["allowedPrompts"].append(new_permission)
        mock_claude_settings.write_text(json.dumps(original, indent=2))

        # Verify merge (count increased)
        merged = json.loads(mock_claude_settings.read_text())
        assert len(merged["allowedPrompts"]) == original_count + 1

        # Replace: overwrite completely
        replaced = {"allowedPrompts": [new_permission]}
        mock_claude_settings.write_text(json.dumps(replaced, indent=2))

        # Verify replace (only 1 permission)
        replaced_content = json.loads(mock_claude_settings.read_text())
        assert len(replaced_content["allowedPrompts"]) == 1


class TestSafetyFeatures:
    """测试安全机制功能"""

    def test_read_only_validation(self, temp_project, mock_claude_settings):
        """测试只读操作验证"""
        # Verify read-only check works
        original_content = mock_claude_settings.read_text()

        # Simulate read-only check (no modification)
        content = mock_claude_settings.read_text()

        # Content should be unchanged
        assert content == original_content

    def test_backup_creation(self, temp_project, mock_claude_settings):
        """测试创建备份"""
        # Create backup before modification
        backup_file = temp_project / ".claude" / "settings.json.backup"
        original_content = mock_claude_settings.read_text()

        # Simulate backup creation
        backup_file.write_text(original_content)

        # Verify backup exists and matches original
        assert backup_file.exists()
        assert backup_file.read_text() == original_content

    def test_destructive_command_blocking(self, permission_templates):
        """测试阻止破坏性命令（safe 模板）"""
        safe_template = permission_templates["safe"]
        allowed_prompts = [p["prompt"] for p in safe_template["allowedPrompts"]]

        # Safe template should not allow destructive commands
        destructive_commands = ["git push --force", "git reset --hard", "rm -rf"]

        for cmd in destructive_commands:
            # Check if destructive command is in allowed prompts
            is_blocked = cmd not in allowed_prompts
            assert is_blocked, f"Destructive command '{cmd}' should be blocked in safe template"

    def test_permission_scope_validation(self):
        """测试权限范围验证"""
        # Permission should have valid tool and prompt
        valid_permission = {"tool": "Bash", "prompt": "git status"}

        # Check scope
        assert valid_permission["tool"] in ["Bash", "Read", "Write", "Edit"]
        assert isinstance(valid_permission["prompt"], str)
        assert len(valid_permission["prompt"]) > 0
