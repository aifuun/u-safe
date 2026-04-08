"""
Shared fixtures for manage-docs tests.
"""
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

import pytest


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create temporary project structure for testing."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    # Create basic project structure
    (project_dir / ".claude").mkdir()
    (project_dir / ".claude" / "profiles").mkdir()
    (project_dir / "docs").mkdir()
    (project_dir / "docs" / "ADRs").mkdir()

    # Create CLAUDE.md
    claude_md = project_dir / "CLAUDE.md"
    claude_md.write_text("# Test Project\n\nTest documentation.\n")

    # Create profile
    profile = project_dir / ".claude" / "profiles" / "active-profile.json"
    profile.write_text('{"name": "tauri", "type": "desktop"}')

    return project_dir


@pytest.fixture
def sample_doc_structure() -> Dict[str, Any]:
    """Sample documentation structure for testing."""
    return {
        "required_docs": [
            "CLAUDE.md",
            "README.md",
            "docs/ADRs/INDEX.md"
        ],
        "optional_docs": [
            "CONTRIBUTING.md",
            "CHANGELOG.md"
        ],
        "profiles": {
            "tauri": {
                "required": ["docs/TAURI_SETUP.md"],
                "optional": ["docs/PACKAGING.md"]
            },
            "nextjs-aws": {
                "required": ["docs/DEPLOYMENT.md"],
                "optional": ["docs/AWS_CONFIG.md"]
            }
        }
    }


@pytest.fixture
def mock_git_repo(tmp_path: Path) -> Path:
    """Create mock git repository for testing."""
    repo_dir = tmp_path / "git-repo"
    repo_dir.mkdir()

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True, capture_output=True)

    # Create initial commit
    readme = repo_dir / "README.md"
    readme.write_text("# Test Repo\n")
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True, capture_output=True)

    return repo_dir


@pytest.fixture
def sample_health_report() -> Dict[str, Any]:
    """Sample health report data for testing."""
    return {
        "status": "healthy",
        "missing_docs": [],
        "invalid_docs": [],
        "total_docs": 5,
        "coverage": 100,
        "recommendations": []
    }


@pytest.fixture
def profile_config() -> Dict[str, Any]:
    """Sample profile configuration."""
    return {
        "tauri": {
            "name": "Tauri Desktop",
            "required_docs": ["docs/TAURI_SETUP.md"],
            "optional_docs": ["docs/PACKAGING.md"]
        },
        "nextjs-aws": {
            "name": "Next.js + AWS",
            "required_docs": ["docs/DEPLOYMENT.md"],
            "optional_docs": ["docs/AWS_CONFIG.md"]
        },
        "python-lib": {
            "name": "Python Library",
            "required_docs": ["docs/API.md"],
            "optional_docs": ["docs/EXAMPLES.md"]
        }
    }
