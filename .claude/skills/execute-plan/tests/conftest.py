"""
pytest configuration and fixtures for execute-plan tests

Provides test fixtures for:
- Mock plan files
- Git environment simulation
- Task tracking
- File system mocking
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List
import json


@pytest.fixture
def temp_dir():
    """Create temporary directory for test isolation"""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)


@pytest.fixture
def mock_plan_simple():
    """Simple plan with 3 sequential tasks"""
    return """# Issue #123: Test Issue

**GitHub**: https://github.com/test/repo/issues/123
**Branch**: feature/123-test
**Worktree**: /tmp/test-worktree
**Started**: 2026-04-07

## Tasks

- [ ] Task 1: Create test file
- [ ] Task 2: Add test logic
- [ ] Task 3: Run tests

## Acceptance Criteria

- [ ] All tests pass
- [ ] Coverage >= 80%
"""


@pytest.fixture
def mock_plan_complex():
    """Complex plan with phases and sub-tasks"""
    return """# Issue #456: Complex Test Issue

**GitHub**: https://github.com/test/repo/issues/456
**Branch**: feature/456-complex
**Worktree**: /tmp/complex-worktree
**Started**: 2026-04-07

## Tasks

### Phase 1: Setup
- [ ] Initialize test environment
- [ ] Configure dependencies

### Phase 2: Implementation
- [ ] Implement feature A
- [ ] Implement feature B
- [ ] Add error handling

### Phase 3: Testing
- [ ] Unit tests
- [ ] Integration tests

## Acceptance Criteria

- [ ] All features implemented
- [ ] Test coverage >= 90%
- [ ] Documentation complete
"""


@pytest.fixture
def mock_plan_with_dependencies():
    """Plan with explicit task dependencies"""
    return """# Issue #789: Dependency Test

**GitHub**: https://github.com/test/repo/issues/789
**Branch**: feature/789-deps
**Started**: 2026-04-07

## Tasks

- [ ] Task A: Foundation (no dependencies)
- [ ] Task B: Build on A (depends on Task A)
- [ ] Task C: Build on B (depends on Task B)
- [ ] Task D: Independent task

## Acceptance Criteria

- [ ] Tasks execute in correct order
- [ ] Dependencies respected
"""


@pytest.fixture
def mock_git_env(temp_dir, monkeypatch):
    """Mock git environment for testing"""
    # Create .git directory
    git_dir = temp_dir / ".git"
    git_dir.mkdir()

    # Mock git commands
    def mock_git_status(*args, **kwargs):
        return "On branch feature/123-test\nnothing to commit"

    def mock_git_branch(*args, **kwargs):
        return "feature/123-test"

    monkeypatch.setattr("subprocess.run", lambda *a, **k: type('obj', (), {
        'returncode': 0,
        'stdout': 'feature/123-test',
        'stderr': ''
    })())

    return temp_dir


@pytest.fixture
def mock_task_tracker():
    """Mock task tracking system"""
    class TaskTracker:
        def __init__(self):
            self.tasks: List[Dict] = []
            self.current_id = 1

        def create_task(self, subject: str, description: str, activeForm: str = None):
            task = {
                "id": self.current_id,
                "subject": subject,
                "description": description,
                "activeForm": activeForm or f"{subject}...",
                "status": "pending",
                "blockedBy": []
            }
            self.tasks.append(task)
            self.current_id += 1
            return task

        def update_task(self, task_id: int, status: str = None, blockedBy: List[int] = None):
            task = self.get_task(task_id)
            if task:
                if status:
                    task["status"] = status
                if blockedBy is not None:
                    task["blockedBy"] = blockedBy
            return task

        def get_task(self, task_id: int):
            for task in self.tasks:
                if task["id"] == task_id:
                    return task
            return None

        def get_next_available_task(self):
            """Find next task with no blockers"""
            for task in self.tasks:
                if task["status"] == "pending":
                    # Check if all blockers are completed
                    all_clear = True
                    for blocker_id in task["blockedBy"]:
                        blocker = self.get_task(blocker_id)
                        if blocker and blocker["status"] != "completed":
                            all_clear = False
                            break
                    if all_clear:
                        return task
            return None

    return TaskTracker()


@pytest.fixture
def mock_plan_file(temp_dir, mock_plan_simple):
    """Create mock plan file in temp directory"""
    plans_dir = temp_dir / ".claude" / "plans" / "active"
    plans_dir.mkdir(parents=True)

    plan_file = plans_dir / "issue-123-plan.md"
    plan_file.write_text(mock_plan_simple)

    return plan_file


@pytest.fixture
def mock_state_file(temp_dir):
    """Create mock state file for resume testing"""
    state_dir = temp_dir / ".claude"
    state_dir.mkdir(parents=True)

    state_file = state_dir / ".execute-plan-state.json"
    state = {
        "issue_number": 123,
        "current_task_id": 2,
        "completed_task_ids": [1],
        "timestamp": "2026-04-07T10:00:00"
    }
    state_file.write_text(json.dumps(state, indent=2))

    return state_file
