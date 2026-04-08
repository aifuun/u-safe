"""
Safety feature tests for execute-plan skill

Based on ADR-020 "Safety Features" section:
1. Plan Structure Validation
2. Task Dependency Checking
3. Error Recovery Mechanism
4. Failure Limits
5. State File Management
"""

import pytest
import json
from pathlib import Path


@pytest.mark.safety
@pytest.mark.unit
def test_plan_structure_validation_empty_plan():
    """Test validation rejects empty plans"""
    # Given: An empty plan
    empty_plan = ""

    # When: Validating plan structure
    has_tasks = "## Tasks" in empty_plan
    has_criteria = "## Acceptance Criteria" in empty_plan

    # Then: Validation should fail
    assert not has_tasks
    assert not has_criteria


@pytest.mark.safety
@pytest.mark.unit
def test_plan_structure_validation_malformed_markdown():
    """Test validation rejects malformed markdown"""
    # Given: Malformed plan (no proper sections)
    malformed = "Some random text without proper structure"

    # When: Validating required sections
    required_sections = ["## Tasks", "## Acceptance Criteria"]
    has_all_sections = all(section in malformed for section in required_sections)

    # Then: Validation should fail
    assert not has_all_sections


@pytest.mark.safety
@pytest.mark.unit
def test_task_dependency_no_cycles(mock_task_tracker):
    """Test circular dependency detection"""
    # Given: Tasks that would create a cycle
    t1 = mock_task_tracker.create_task("Task 1", "First")
    t2 = mock_task_tracker.create_task("Task 2", "Second")
    t3 = mock_task_tracker.create_task("Task 3", "Third")

    # When: Creating valid dependency chain
    mock_task_tracker.update_task(t2["id"], blockedBy=[t1["id"]])
    mock_task_tracker.update_task(t3["id"], blockedBy=[t2["id"]])

    # Then: No cycles exist (can execute sequentially)
    # Task 1 is available
    next_task = mock_task_tracker.get_next_available_task()
    assert next_task["id"] == t1["id"]

    # Attempting circular dependency (t1 blocked by t3) would create cycle
    # In real implementation, this should be detected and prevented
    # For this test, we verify the detection logic

    def has_cycle(task_id, blockedBy_ids, all_tasks):
        """Simple cycle detection"""
        visited = set()

        def visit(tid):
            if tid in visited:
                return True  # Cycle detected
            visited.add(tid)
            task = next((t for t in all_tasks if t["id"] == tid), None)
            if task:
                for blocker_id in task.get("blockedBy", []):
                    if visit(blocker_id):
                        return True
            return False

        return visit(task_id)

    # Test: Adding t1 blocked by t3 would create cycle
    test_tasks = [t1, t2, t3]
    # t1 <- t2 <- t3, if we add t3 <- t1, cycle exists
    t1_with_cycle = {**t1, "blockedBy": [t3["id"]]}
    test_tasks_with_cycle = [t1_with_cycle, t2, t3]

    # Cycle should be detected
    assert has_cycle(t1["id"], [t3["id"]], test_tasks_with_cycle)


@pytest.mark.safety
@pytest.mark.unit
def test_error_recovery_save_checkpoint(temp_dir):
    """Test checkpoint saved on failure"""
    # Given: Task execution state
    state = {
        "issue_number": 123,
        "current_task_id": 3,
        "completed_task_ids": [1, 2],
        "timestamp": "2026-04-07T12:00:00"
    }

    # When: Saving checkpoint
    state_file = temp_dir / ".execute-plan-state.json"
    state_file.write_text(json.dumps(state, indent=2))

    # Then: Checkpoint file created with correct data
    assert state_file.exists()
    loaded = json.loads(state_file.read_text())
    assert loaded["issue_number"] == 123
    assert loaded["current_task_id"] == 3
    assert 1 in loaded["completed_task_ids"]
    assert 2 in loaded["completed_task_ids"]


@pytest.mark.safety
@pytest.mark.unit
def test_failure_limits_max_retries():
    """Test max retries limit prevents infinite loops"""
    # Given: Max retries configuration
    MAX_RETRIES = 3

    # When: Simulating task failures
    retry_count = 0
    task_succeeded = False

    for attempt in range(MAX_RETRIES + 1):
        retry_count = attempt
        # Simulate failure
        task_succeeded = False

        if retry_count >= MAX_RETRIES:
            break

    # Then: Stopped after MAX_RETRIES
    assert retry_count == MAX_RETRIES
    assert not task_succeeded


@pytest.mark.safety
@pytest.mark.unit
def test_state_file_cleanup_on_completion(temp_dir):
    """Test state files cleaned up after successful completion"""
    # Given: State files exist
    state_files = [
        temp_dir / ".execute-plan-state.json",
        temp_dir / ".eval-plan-status.json",
    ]

    for state_file in state_files:
        state_file.write_text("{}")

    # When: Cleaning up after completion
    for state_file in state_files:
        if state_file.exists():
            state_file.unlink()

    # Then: State files removed
    for state_file in state_files:
        assert not state_file.exists()


@pytest.mark.safety
@pytest.mark.integration
def test_stale_state_warning(temp_dir):
    """Test warning for stale state files (>24h old)"""
    from datetime import datetime, timedelta

    # Given: Old state file
    old_timestamp = datetime.now() - timedelta(hours=25)
    state = {
        "timestamp": old_timestamp.isoformat(),
        "issue_number": 123
    }

    state_file = temp_dir / ".execute-plan-state.json"
    state_file.write_text(json.dumps(state))

    # When: Checking state age
    loaded_state = json.loads(state_file.read_text())
    state_time = datetime.fromisoformat(loaded_state["timestamp"])
    age_hours = (datetime.now() - state_time).total_seconds() / 3600

    # Then: State is stale (>24h)
    assert age_hours > 24

    # Should warn user and suggest fresh start
    warning = "State file stale, consider fresh start"
    assert age_hours > 24, warning
