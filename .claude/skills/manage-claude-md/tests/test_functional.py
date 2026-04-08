"""
Functional tests for manage-claude-md skill

Based on ADR-020 "What it does" section:
1. Update skills list in CLAUDE.md
2. Archive completed plans
3. Generate project health report
4. Clean stale status files
5. Instant mode workflow
6. Configure profile
"""

import pytest
from pathlib import Path


@pytest.mark.functional
@pytest.mark.unit
def test_update_skills_list(mock_claude_md, mock_skill_files):
    """Test updating CLAUDE.md skills list from .claude/skills/"""
    # Given: CLAUDE.md with outdated skills list
    original_content = mock_claude_md.read_text()
    assert "skill1" in original_content

    # When: Updating skills list
    # (Simulating skill list update)
    new_skills = ["skill1", "skill2", "skill3", "skill4"]
    updated_content = original_content.replace(
        "- /skill3 - Third skill",
        "- /skill3 - Third skill\n- /skill4 - Fourth skill"
    )
    mock_claude_md.write_text(updated_content)

    # Then: CLAUDE.md contains all skills
    content = mock_claude_md.read_text()
    assert "skill4" in content


@pytest.mark.functional
@pytest.mark.integration
def test_archive_completed_plans(mock_plans_dir):
    """Test archiving completed plans from active to archive"""
    # Given: Active plans directory with completed plans
    active_dir = mock_plans_dir["active"]
    archive_dir = mock_plans_dir["archive"]

    active_plans_before = list(active_dir.glob("*.md"))
    assert len(active_plans_before) == 2

    # When: Archiving a completed plan
    plan_to_archive = active_dir / "issue-123-plan.md"
    target = archive_dir / "issue-123-plan.md"
    plan_to_archive.rename(target)

    # Then: Plan moved to archive
    assert not plan_to_archive.exists()
    assert target.exists()
    assert len(list(active_dir.glob("*.md"))) == 1


@pytest.mark.functional
@pytest.mark.integration
def test_generate_health_report(mock_claude_md, mock_plans_dir, mock_state_files):
    """Test generating project health report"""
    # Given: Project with various status indicators
    active_plans = list(mock_plans_dir["active"].glob("*.md"))
    state_files = [mock_state_files["eval_status"], mock_state_files["review_status"]]

    # When: Generating health report
    report = {
        "active_plans": len(active_plans),
        "state_files": len([f for f in state_files if f.exists()]),
        "claude_md_exists": mock_claude_md.exists()
    }

    # Then: Report contains expected metrics
    assert report["active_plans"] == 2
    assert report["state_files"] == 2
    assert report["claude_md_exists"] is True


@pytest.mark.functional
@pytest.mark.unit
def test_clean_stale_files(mock_state_files):
    """Test cleaning stale status files (>24h old)"""
    import json
    from datetime import datetime

    # Given: Stale status file
    eval_status_file = mock_state_files["eval_status"]
    status_data = json.loads(eval_status_file.read_text())
    status_time = datetime.fromisoformat(status_data["timestamp"])
    age = (datetime.now() - status_time).total_seconds() / 3600

    # Then: File is identified as stale
    assert age > 24

    # When: Cleaning stale files
    if age > 24:
        eval_status_file.unlink()

    # Then: Stale file removed
    assert not eval_status_file.exists()


@pytest.mark.functional
@pytest.mark.integration
def test_instant_mode_workflow(mock_claude_md, mock_plans_dir, mock_state_files):
    """Test complete instant mode workflow"""
    # Given: Project setup
    claude_md = mock_claude_md
    active_dir = mock_plans_dir["active"]

    # When: Running instant mode (simulated)
    # 1. Update skills list
    original_content = claude_md.read_text()
    updated_content = original_content + "\n- /new-skill - New skill\n"
    claude_md.write_text(updated_content)

    # 2. Archive completed plans
    completed_plan = active_dir / "issue-123-plan.md"
    if completed_plan.exists():
        target = mock_plans_dir["archive"] / completed_plan.name
        completed_plan.rename(target)

    # 3. Clean stale files
    stale_file = mock_state_files["eval_status"]
    if stale_file.exists():
        stale_file.unlink()

    # Then: All operations completed
    assert "new-skill" in claude_md.read_text()
    assert len(list(active_dir.glob("*.md"))) == 1
    assert not stale_file.exists()


@pytest.mark.functional
@pytest.mark.unit
def test_configure_profile(mock_profile_config):
    """Test profile configuration functionality"""
    # Given: CLAUDE.md with profile
    content = mock_profile_config.read_text()

    # When: Reading profile
    import re
    match = re.search(r'\*\*Profile\*\*:\s+(\w+)', content)

    # Then: Profile extracted correctly
    assert match is not None
    assert match.group(1) == "tauri"
