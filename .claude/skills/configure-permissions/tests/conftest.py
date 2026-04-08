"""
Shared fixtures for configure-permissions tests.
"""
import json
from pathlib import Path
from typing import Dict, Any

import pytest


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create temporary project structure for testing."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    # Create .claude directory
    claude_dir = project_dir / ".claude"
    claude_dir.mkdir()

    return project_dir


@pytest.fixture
def sample_settings() -> Dict[str, Any]:
    """Sample settings.json structure for testing."""
    return {
        "allowedPrompts": [
            {"tool": "Bash", "prompt": "run tests"},
            {"tool": "Bash", "prompt": "git status"}
        ]
    }


@pytest.fixture
def permission_templates() -> Dict[str, Dict[str, Any]]:
    """Permission template data for testing."""
    return {
        "safe": {
            "allowedPrompts": [
                {"tool": "Bash", "prompt": "git add"},
                {"tool": "Bash", "prompt": "git commit"},
                {"tool": "Bash", "prompt": "git push"},
                {"tool": "Bash", "prompt": "npm test"},
                {"tool": "Bash", "prompt": "npm run build"}
            ]
        },
        "all": {
            "allowedPrompts": [
                {"tool": "Bash", "prompt": ".*"}
            ]
        },
        "minimal": {
            "allowedPrompts": [
                {"tool": "Bash", "prompt": "git status"},
                {"tool": "Bash", "prompt": "npm test"}
            ]
        },
        "read-only": {
            "allowedPrompts": [
                {"tool": "Bash", "prompt": "git status"},
                {"tool": "Bash", "prompt": "git diff"}
            ]
        }
    }


@pytest.fixture
def mock_claude_settings(temp_project: Path, sample_settings: Dict[str, Any]) -> Path:
    """Create mock Claude Code settings.json file."""
    settings_file = temp_project / ".claude" / "settings.json"
    settings_file.write_text(json.dumps(sample_settings, indent=2))
    return settings_file
