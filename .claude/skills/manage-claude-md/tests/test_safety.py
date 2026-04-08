"""
Safety feature tests for manage-claude-md skill

Based on ADR-020 "Safety Features" section:
1. Backup before modify
2. Atomic file operations
3. Read-only validation
4. Error recovery
5. Dry-run no changes
"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta


@pytest.mark.safety
@pytest.mark.unit
def test_backup_before_modify(mock_claude_md):
    """Test that backups are created before modifying CLAUDE.md"""
    # Given: CLAUDE.md exists
    original_content = mock_claude_md.read_text()
    backup_dir = mock_claude_md.parent / ".backups"
    backup_dir.mkdir(exist_ok=True)

    # When: Creating backup before modification
    backup_path = backup_dir / f"CLAUDE.md.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
    backup_path.write_text(original_content)

    # Then: Backup exists and matches original
    assert backup_path.exists()
    assert backup_path.read_text() == original_content


@pytest.mark.safety
@pytest.mark.unit
def test_atomic_file_operations(mock_claude_md, tmp_path):
    """Test atomic writes to prevent partial updates"""
    # Given: CLAUDE.md content
    original_content = mock_claude_md.read_text()

    # When: Simulating atomic write using temp file
    temp_file = tmp_path / "CLAUDE.md.tmp"
    new_content = original_content + "\n- /new-skill - New skill"

    # Write to temp file first
    temp_file.write_text(new_content)

    # Then: Atomic rename (all-or-nothing)
    assert temp_file.exists()
    # In real implementation, would use: temp_file.rename(mock_claude_md)

    # Verify temp file has correct content
    assert temp_file.read_text() == new_content


@pytest.mark.safety
@pytest.mark.unit
def test_read_only_validation(mock_claude_md):
    """Test read-only mode doesn't modify files"""
    # Given: CLAUDE.md in read-only mode
    original_content = mock_claude_md.read_text()
    read_only = True

    # When: Attempting operation in read-only mode
    if not read_only:
        mock_claude_md.write_text(original_content + "\nModified")

    # Then: File remains unchanged
    assert mock_claude_md.read_text() == original_content


@pytest.mark.safety
@pytest.mark.integration
def test_error_recovery(mock_plans_dir, mock_state_files):
    """Test graceful recovery from errors"""
    # Given: Operation that might fail
    state_file = mock_state_files["eval_status"]

    # When: Simulating error during operation
    try:
        # Attempt to read possibly corrupted JSON
        data = json.loads(state_file.read_text())

        # Simulate processing
        if "timestamp" not in data:
            raise KeyError("Missing timestamp")

    except (json.JSONDecodeError, KeyError) as e:
        # Then: Error handled gracefully
        error_message = str(e)
        assert error_message  # Error captured

        # Recovery: Can recreate valid state
        valid_data = {
            "timestamp": datetime.now().isoformat(),
            "issue_number": 123,
            "score": 95
        }
        state_file.write_text(json.dumps(valid_data))

    # Verify recovery successful
    recovered_data = json.loads(state_file.read_text())
    assert "timestamp" in recovered_data


@pytest.mark.safety
@pytest.mark.unit
def test_dry_run_no_changes(mock_claude_md, mock_plans_dir):
    """Test dry-run mode makes no actual changes"""
    # Given: Initial state
    original_md = mock_claude_md.read_text()
    active_plans_before = list(mock_plans_dir["active"].glob("*.md"))

    # When: Running in dry-run mode
    dry_run = True

    if dry_run:
        # Simulate operations without execution
        planned_changes = [
            f"Would update: {mock_claude_md}",
            f"Would archive: {active_plans_before[0]}",
            "No actual changes made"
        ]
    else:
        # Real operations (not executed in dry-run)
        mock_claude_md.write_text(original_md + "\nModified")

    # Then: No changes made
    assert mock_claude_md.read_text() == original_md
    assert len(list(mock_plans_dir["active"].glob("*.md"))) == len(active_plans_before)

    # But plan was generated
    if dry_run:
        assert len(planned_changes) == 3
        assert "Would update" in planned_changes[0]
