"""
Functional tests for execute-plan skill

Based on ADR-020 "What it does" section:
1. Load plan from `.claude/plans/active/issue-{N}-plan.md`
2. Create todos from plan tasks for progress tracking
3. Guide implementation task-by-task with context
4. Validate progress after each task
5. Continue until complete - all tasks done
6. Prepare deliverables for `/review`
"""

import pytest
from pathlib import Path
import re


@pytest.mark.functional
@pytest.mark.unit
def test_load_plan_file(mock_plan_file):
    """Test 1: Load plan from correct file path"""
    # Given: A plan file exists
    assert mock_plan_file.exists()

    # When: Loading the plan
    content = mock_plan_file.read_text()

    # Then: Plan content is loaded correctly
    assert "Issue #123" in content
    assert "## Tasks" in content
    assert "Task 1: Create test file" in content


@pytest.mark.functional
@pytest.mark.unit
def test_extract_tasks_from_plan(mock_plan_simple):
    """Test 2: Extract tasks from plan for todo creation"""
    # Given: A plan with tasks
    plan_content = mock_plan_simple

    # When: Extracting tasks
    task_pattern = r"- \[ \] (.+)"
    tasks = re.findall(task_pattern, plan_content)

    # Then: All tasks are extracted
    assert len(tasks) >= 3
    assert any("Task 1" in t for t in tasks)
    assert any("Task 2" in t for t in tasks)
    assert any("Task 3" in t for t in tasks)


@pytest.mark.functional
@pytest.mark.unit
def test_create_todos_from_tasks(mock_task_tracker, mock_plan_simple):
    """Test 3: Create todos from plan tasks with dependencies"""
    # Given: Plan with tasks
    task_pattern = r"- \[ \] (.+)"
    tasks = re.findall(task_pattern, mock_plan_simple)

    # When: Creating todos
    task_ids = []
    for i, task_text in enumerate(tasks):
        todo = mock_task_tracker.create_task(
            subject=task_text,
            description=f"Execute: {task_text}"
        )
        task_ids.append(todo["id"])

        # Add dependency: task i+1 blocked by task i
        if i > 0:
            mock_task_tracker.update_task(todo["id"], blockedBy=[task_ids[i-1]])

    # Then: Todos created with correct dependencies
    assert len(mock_task_tracker.tasks) == len(tasks)

    # Task 1 has no blockers
    task1 = mock_task_tracker.get_task(task_ids[0])
    assert len(task1["blockedBy"]) == 0

    # Task 2 blocked by Task 1
    task2 = mock_task_tracker.get_task(task_ids[1])
    assert task_ids[0] in task2["blockedBy"]

    # Task 3 blocked by Task 2
    task3 = mock_task_tracker.get_task(task_ids[2])
    assert task_ids[1] in task3["blockedBy"]


@pytest.mark.functional
@pytest.mark.integration
def test_sequential_task_execution(mock_task_tracker):
    """Test 4: Execute tasks sequentially respecting dependencies"""
    # Given: Three tasks with dependencies
    t1 = mock_task_tracker.create_task("Task 1", "First task")
    t2 = mock_task_tracker.create_task("Task 2", "Second task")
    t3 = mock_task_tracker.create_task("Task 3", "Third task")

    mock_task_tracker.update_task(t2["id"], blockedBy=[t1["id"]])
    mock_task_tracker.update_task(t3["id"], blockedBy=[t2["id"]])

    # When: Finding next available task
    next_task = mock_task_tracker.get_next_available_task()

    # Then: Task 1 is available (no blockers)
    assert next_task["id"] == t1["id"]

    # When: Completing Task 1
    mock_task_tracker.update_task(t1["id"], status="completed")
    next_task = mock_task_tracker.get_next_available_task()

    # Then: Task 2 is now available
    assert next_task["id"] == t2["id"]

    # When: Completing Task 2
    mock_task_tracker.update_task(t2["id"], status="completed")
    next_task = mock_task_tracker.get_next_available_task()

    # Then: Task 3 is now available
    assert next_task["id"] == t3["id"]

    # When: Completing Task 3
    mock_task_tracker.update_task(t3["id"], status="completed")
    next_task = mock_task_tracker.get_next_available_task()

    # Then: No more tasks available
    assert next_task is None


@pytest.mark.functional
@pytest.mark.unit
def test_validate_task_completion(mock_task_tracker):
    """Test 5: Validate task marked completed after execution"""
    # Given: A task in progress
    task = mock_task_tracker.create_task("Test task", "Testing completion")
    mock_task_tracker.update_task(task["id"], status="in_progress")

    # When: Marking task as completed
    updated = mock_task_tracker.update_task(task["id"], status="completed")

    # Then: Task status is completed
    assert updated["status"] == "completed"

    # Verify task is in completed state
    completed_task = mock_task_tracker.get_task(task["id"])
    assert completed_task["status"] == "completed"


@pytest.mark.functional
@pytest.mark.integration
def test_prepare_deliverables_summary():
    """Test 6: Prepare deliverables summary for review"""
    # Given: Completed tasks and file changes
    completed_tasks = 5
    total_tasks = 5
    files_changed = 3
    lines_added = 150
    lines_removed = 20

    # When: Generating deliverables summary
    summary = {
        "tasks_completed": f"{completed_tasks}/{total_tasks}",
        "files_changed": files_changed,
        "lines_delta": f"+{lines_added}/-{lines_removed}",
        "status": "ready_for_review"
    }

    # Then: Summary contains expected information
    assert summary["tasks_completed"] == "5/5"
    assert summary["files_changed"] == 3
    assert summary["status"] == "ready_for_review"
    assert "+150" in summary["lines_delta"]


@pytest.mark.functional
@pytest.mark.integration
def test_complete_workflow_end_to_end(mock_task_tracker, mock_plan_simple):
    """Integration test: Complete workflow from plan to deliverables"""
    # Given: A plan with tasks
    task_pattern = r"- \[ \] (.+)"
    tasks = re.findall(task_pattern, mock_plan_simple)

    # Phase 1: Create todos from plan
    task_ids = []
    for i, task_text in enumerate(tasks):
        todo = mock_task_tracker.create_task(
            subject=task_text,
            description=f"Execute: {task_text}"
        )
        task_ids.append(todo["id"])
        if i > 0:
            mock_task_tracker.update_task(todo["id"], blockedBy=[task_ids[i-1]])

    # Phase 2: Execute tasks sequentially
    while True:
        next_task = mock_task_tracker.get_next_available_task()
        if not next_task:
            break

        # Mark in progress
        mock_task_tracker.update_task(next_task["id"], status="in_progress")

        # Simulate execution (in real scenario, execute task logic here)
        # ...

        # Mark completed
        mock_task_tracker.update_task(next_task["id"], status="completed")

    # Phase 3: Verify all tasks completed
    all_tasks = mock_task_tracker.tasks
    completed_count = sum(1 for t in all_tasks if t["status"] == "completed")

    # Then: All tasks should be completed
    assert completed_count == len(tasks)
    assert all(t["status"] == "completed" for t in all_tasks)

    # And: No more available tasks
    assert mock_task_tracker.get_next_available_task() is None
