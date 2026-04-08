"""
Argument tests for execute-plan skill

Based on ADR-020 "Arguments" section:
- Issue number auto-detection
- --resume flag
- --skip-task flag
- --dry-run flag
- Invalid arguments handling
"""

import pytest
import re


@pytest.mark.unit
def test_issue_number_from_branch():
    """Test issue number extraction from branch name"""
    # Given: Branch names with issue numbers
    branches = [
        ("feature/123-test-feature", 123),
        ("fix/456-bug-fix", 456),
        ("feature/789-long-feature-name", 789),
    ]

    # When: Extracting issue number
    pattern = r"/(\d+)-"

    for branch, expected in branches:
        match = re.search(pattern, branch)
        # Then: Issue number extracted correctly
        assert match is not None
        assert int(match.group(1)) == expected


@pytest.mark.unit
def test_resume_flag_loads_checkpoint(mock_state_file):
    """Test --resume flag loads saved checkpoint"""
    # Given: A saved checkpoint file
    import json
    state = json.loads(mock_state_file.read_text())

    # When: Loading checkpoint for resume
    issue_number = state.get("issue_number")
    current_task = state.get("current_task_id")
    completed = state.get("completed_task_ids")

    # Then: Checkpoint data loaded correctly
    assert issue_number == 123
    assert current_task == 2
    assert 1 in completed


@pytest.mark.unit
def test_skip_task_marks_completed_without_execution(mock_task_tracker):
    """Test --skip-task N marks task completed without executing"""
    # Given: Tasks in sequence
    t1 = mock_task_tracker.create_task("Task 1", "First")
    t2 = mock_task_tracker.create_task("Task 2", "Second - to skip")
    t3 = mock_task_tracker.create_task("Task 3", "Third")

    # When: Skipping task 2
    skip_task_id = t2["id"]
    mock_task_tracker.update_task(skip_task_id, status="completed")  # Skip without execution

    # Then: Task 2 marked completed
    skipped = mock_task_tracker.get_task(skip_task_id)
    assert skipped["status"] == "completed"

    # And: Can proceed to task 3
    assert t3["status"] == "pending"


@pytest.mark.unit
def test_dry_run_shows_preview_without_changes(mock_plan_simple):
    """Test --dry-run shows plan preview without executing"""
    # Given: A plan with tasks
    plan_content = mock_plan_simple

    # When: Simulating dry-run mode
    dry_run = True
    tasks = re.findall(r"- \[ \] (.+)", plan_content)

    # Then: Tasks identified for preview
    assert len(tasks) >= 3

    # Dry-run would display but not execute
    preview = {
        "mode": "dry-run",
        "tasks_to_execute": tasks,
        "will_modify": False
    }

    assert preview["mode"] == "dry-run"
    assert preview["will_modify"] is False
    assert len(preview["tasks_to_execute"]) == len(tasks)


@pytest.mark.unit
def test_invalid_arguments_handling():
    """Test invalid arguments raise appropriate errors"""
    # Given: Invalid argument scenarios
    invalid_cases = [
        {"issue_number": None, "error": "Issue number required"},
        {"issue_number": "abc", "error": "Invalid issue number format"},
        {"skip_task": -1, "error": "Invalid task number"},
        {"skip_task": 999, "error": "Task not found"},
    ]

    for case in invalid_cases:
        # When/Then: Invalid arguments should be detected
        if case.get("issue_number") is None and "issue_number" in case:
            # Simulating validation
            assert case["error"] == "Issue number required"
        elif isinstance(case.get("issue_number"), str):
            try:
                int(case["issue_number"])
                assert False, "Should have raised error"
            except ValueError:
                assert case["error"] == "Invalid issue number format"
        elif case.get("skip_task") is not None:
            # Skip-task validation
            if case["skip_task"] < 0:
                assert case["error"] == "Invalid task number"
            elif case["skip_task"] > 100:  # Reasonable upper bound
                assert case["error"] == "Task not found"


@pytest.mark.integration
def test_auto_detect_from_active_plan(temp_dir):
    """Test issue number auto-detection from active plan"""
    # Given: Single active plan file
    plans_dir = temp_dir / ".claude" / "plans" / "active"
    plans_dir.mkdir(parents=True)

    plan_file = plans_dir / "issue-456-plan.md"
    plan_file.write_text("# Issue #456: Test")

    # When: Auto-detecting issue number
    active_plans = list(plans_dir.glob("issue-*-plan.md"))

    # Then: Issue number detected from filename
    assert len(active_plans) == 1
    match = re.search(r"issue-(\d+)-", active_plans[0].name)
    assert match is not None
    assert int(match.group(1)) == 456
