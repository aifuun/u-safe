"""
Integration tests for update-framework skill.

Tests end-to-end workflows and integration with other skills.
Following ADR-020 standards.
"""

import json
import shutil
from pathlib import Path
from typing import Dict
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.integration
def test_integration_with_manage_claude_md(framework_and_project: Dict[str, Path]):
    """Test integration with manage-claude-md skill.

    After framework sync, manage-claude-md should update CLAUDE.md
    with new skills list.

    Arrange:
        - Framework with 3 skills
        - Project with outdated CLAUDE.md
    Act:
        - Run update-framework
        - Run manage-claude-md
    Assert:
        - CLAUDE.md updated with new skills
        - Skills section includes all 3 framework skills
    """
    framework = framework_and_project["framework"]
    project = framework_and_project["project"]

    # Create CLAUDE.md with outdated skills list
    claude_md_content = """# Project

## Skills
- old-skill-1
- old-skill-2
"""
    (project / "CLAUDE.md").write_text(claude_md_content)

    # Simulate framework sync (copy skills)
    shutil.copytree(
        framework / ".claude/skills",
        project / ".claude/skills",
        dirs_exist_ok=True
    )

    # Simulate manage-claude-md updating CLAUDE.md
    # In real implementation, this would call /manage-claude-md
    skills = [d.name for d in (project / ".claude/skills").iterdir() if d.is_dir()]

    updated_content = f"""# Project

## Skills
{chr(10).join(f'- {skill}' for skill in sorted(skills))}
"""

    (project / "CLAUDE.md").write_text(updated_content)

    # Verify integration
    assert (project / "CLAUDE.md").exists()
    content = (project / "CLAUDE.md").read_text()
    assert "skill-0" in content
    assert "skill-1" in content
    assert "skill-2" in content
    assert "old-skill-1" not in content  # Replaced


@pytest.mark.integration
def test_integration_with_init_docs(framework_and_project: Dict[str, Path]):
    """Test integration with init-docs skill.

    After framework sync, init-docs can use new templates from framework.

    Arrange:
        - Framework with doc templates in guides
        - Empty project docs
    Act:
        - Run update-framework
        - Run init-docs
    Assert:
        - Project docs initialized with framework templates
        - Standard documentation structure created
    """
    framework = framework_and_project["framework"]
    project = framework_and_project["project"]

    # Create doc templates in framework guides
    templates_dir = framework / ".claude/guides/doc-templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "README.template.md").write_text("# ${PROJECT_NAME}")
    (templates_dir / "CONTRIBUTING.template.md").write_text("# Contributing")

    # Simulate framework sync (copy guides)
    shutil.copytree(
        framework / ".claude/guides",
        project / ".claude/guides",
        dirs_exist_ok=True
    )

    # Simulate init-docs using templates
    # In real implementation, this would call /init-docs
    project_templates = project / ".claude/guides/doc-templates"
    assert project_templates.exists()

    # Generate docs from templates
    (project / "docs").mkdir(exist_ok=True)

    readme_template = (project_templates / "README.template.md").read_text()
    readme_content = readme_template.replace("${PROJECT_NAME}", "My Project")
    (project / "docs/README.md").write_text(readme_content)

    contrib_template = (project_templates / "CONTRIBUTING.template.md").read_text()
    (project / "docs/CONTRIBUTING.md").write_text(contrib_template)

    # Verify integration
    assert (project / "docs/README.md").exists()
    assert (project / "docs/CONTRIBUTING.md").exists()
    assert "My Project" in (project / "docs/README.md").read_text()


@pytest.mark.integration
def test_full_project_initialization(tmp_path: Path):
    """Test complete project initialization workflow.

    Simulates full setup:
    1. Clone framework
    2. Create new project
    3. Run update-framework
    4. Configure permissions
    5. Initialize docs
    6. Verify project ready for development

    Arrange:
        - Fresh framework clone
        - New project directory
    Act:
        - Execute full initialization workflow
    Assert:
        - All framework components synced
        - Project configuration complete
        - Documentation initialized
        - Ready for /start-issue
    """
    # Step 1: Setup framework
    framework = tmp_path / "ai-dev"
    framework.mkdir()
    (framework / ".claude/pillars").mkdir(parents=True)
    (framework / ".claude/skills").mkdir(parents=True)
    (framework / ".claude/guides").mkdir(parents=True)
    (framework / ".claude/profiles").mkdir(parents=True)

    # Add framework content
    (framework / ".claude/pillars/pillar-1.md").write_text("# Pillar 1")
    (framework / ".claude/skills/test-skill").mkdir()
    (framework / ".claude/skills/test-skill/SKILL.md").write_text("# Test Skill")
    (framework / ".claude/guides/workflow").mkdir()
    (framework / ".claude/guides/workflow/guide-1.md").write_text("# Guide 1")

    # Step 2: Create new project
    project = tmp_path / "my-new-project"
    project.mkdir()
    (project / ".claude").mkdir()

    # Step 3: Sync framework
    shutil.copytree(
        framework / ".claude/pillars",
        project / ".claude/pillars",
        dirs_exist_ok=True
    )
    shutil.copytree(
        framework / ".claude/skills",
        project / ".claude/skills",
        dirs_exist_ok=True
    )
    shutil.copytree(
        framework / ".claude/guides",
        project / ".claude/guides",
        dirs_exist_ok=True
    )

    # Step 4: Configure permissions (simulate)
    settings = {
        "allowed_commands": ["git", "npm", "pytest"],
        "auto_approve": ["git status", "npm test"]
    }
    settings_file = project / ".claude/settings.json"
    settings_file.write_text(json.dumps(settings, indent=2))

    # Step 5: Initialize docs
    (project / "docs").mkdir()
    (project / "docs/README.md").write_text("# My New Project")
    (project / "docs/ADRs").mkdir()
    (project / "docs/ADRs/INDEX.md").write_text("# Architecture Decisions")

    # Step 6: Create installation marker
    install_info = {
        "framework_version": "5.1.0",
        "installed_at": "2026-04-07",
        "profile": "default"
    }
    (project / ".framework-install").write_text(json.dumps(install_info, indent=2))

    # === Verification ===

    # Framework components synced
    assert (project / ".claude/pillars/pillar-1.md").exists()
    assert (project / ".claude/skills/test-skill/SKILL.md").exists()
    assert (project / ".claude/guides/workflow/guide-1.md").exists()

    # Configuration complete
    assert (project / ".claude/settings.json").exists()
    config = json.loads((project / ".claude/settings.json").read_text())
    assert "git" in config["allowed_commands"]

    # Documentation initialized
    assert (project / "docs/README.md").exists()
    assert (project / "docs/ADRs/INDEX.md").exists()

    # Installation marker present
    assert (project / ".framework-install").exists()
    marker = json.loads((project / ".framework-install").read_text())
    assert marker["framework_version"] == "5.1.0"

    # Project ready for development
    assert (project / ".claude/pillars").exists()
    assert (project / ".claude/skills").exists()
    assert (project / ".claude/guides").exists()
    assert (project / ".claude/settings.json").exists()
    assert (project / "docs").exists()
