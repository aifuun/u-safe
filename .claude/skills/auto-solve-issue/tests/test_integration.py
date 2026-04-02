#!/usr/bin/env python3
"""
Integration tests for auto-solve-issue coordinator

Tests the IssueSolver class and workflow orchestration logic.
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path to import coordinator

from coordinator import (
    IssueSolver,
    Result,
    CheckpointDecision,
)


class TestIssueSolver(unittest.TestCase):
    """Test IssueSolver class initialization and methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.solver = IssueSolver(issue_number=409, mode="auto", use_subagent=False)

    def test_initialization(self):
        """Test IssueSolver initializes correctly"""
        self.assertEqual(self.solver.issue_number, 409)
        self.assertEqual(self.solver.mode, "auto")
        self.assertEqual(self.solver.use_subagent, False)
        self.assertEqual(self.solver.task_ids, [])

    def test_initialization_with_subagent(self):
        """Test IssueSolver with subagent enabled"""
        solver = IssueSolver(issue_number=23, mode="interactive", use_subagent=True)
        self.assertEqual(solver.issue_number, 23)
        self.assertEqual(solver.mode, "interactive")
        self.assertEqual(solver.use_subagent, True)


class TestTaskChainCreation(unittest.TestCase):
    """Test task dependency chain creation"""

    def setUp(self):
        """Set up test fixtures"""
        self.solver = IssueSolver(issue_number=409, mode="auto")

    def test_create_task_chain(self):
        """Test task chain returns 5 phase definitions"""
        task_definitions = self.solver.create_task_chain()

        # Should return 5 tasks
        self.assertEqual(len(task_definitions), 5)

        # Verify phase numbers
        phases = [task["metadata"]["phase"] for task in task_definitions]
        self.assertEqual(phases, ["1", "1.5", "2", "2.5", "3"])

    def test_task_metadata(self):
        """Test task metadata contains required fields"""
        task_definitions = self.solver.create_task_chain()

        for task in task_definitions:
            # Check required metadata fields
            self.assertIn("phase", task["metadata"])
            self.assertIn("skill", task["metadata"])
            self.assertIn("checkpoint", task["metadata"])
            self.assertIn("issue_number", task["metadata"])
            self.assertEqual(task["metadata"]["issue_number"], 409)

    def test_checkpoint_tasks(self):
        """Test checkpoint tasks have correct metadata"""
        task_definitions = self.solver.create_task_chain()

        # Phase 1.5 should be checkpoint
        task_1_5 = task_definitions[1]
        self.assertTrue(task_1_5["metadata"]["checkpoint"])
        self.assertEqual(task_1_5["metadata"]["checkpoint_name"], "Checkpoint 1")
        self.assertEqual(task_1_5["metadata"]["score_threshold"], 90)

        # Phase 2.5 should be checkpoint
        task_2_5 = task_definitions[3]
        self.assertTrue(task_2_5["metadata"]["checkpoint"])
        self.assertEqual(task_2_5["metadata"]["checkpoint_name"], "Checkpoint 2")
        self.assertEqual(task_2_5["metadata"]["score_threshold"], 90)

    def test_non_checkpoint_tasks(self):
        """Test non-checkpoint tasks don't have checkpoint metadata"""
        task_definitions = self.solver.create_task_chain()

        # Phase 1, 2, 3 should not be checkpoints
        for idx in [0, 2, 4]:  # Phases 1, 2, 3
            task = task_definitions[idx]
            self.assertFalse(task["metadata"]["checkpoint"])
            self.assertNotIn("checkpoint_name", task["metadata"])


class TestFindNextAvailableTask(unittest.TestCase):
    """Test finding next available task"""

    def setUp(self):
        """Set up test fixtures"""
        self.solver = IssueSolver(issue_number=409, mode="auto")
        self.solver.task_ids = ["task_1", "task_2", "task_3", "task_4", "task_5"]

    def test_find_first_task(self):
        """Test finding first task when all are pending"""
        all_tasks = [
            {"id": "task_1", "status": "pending", "blockedBy": []},
            {"id": "task_2", "status": "pending", "blockedBy": ["task_1"]},
            {"id": "task_3", "status": "pending", "blockedBy": ["task_2"]},
        ]

        next_task = self.solver.find_next_available_task(all_tasks)

        self.assertIsNotNone(next_task)
        self.assertEqual(next_task["id"], "task_1")

    def test_find_second_task_after_first_complete(self):
        """Test finding second task after first completes"""
        all_tasks = [
            {"id": "task_1", "status": "completed", "blockedBy": []},
            {"id": "task_2", "status": "pending", "blockedBy": ["task_1"]},
            {"id": "task_3", "status": "pending", "blockedBy": ["task_2"]},
        ]

        next_task = self.solver.find_next_available_task(all_tasks)

        self.assertIsNotNone(next_task)
        self.assertEqual(next_task["id"], "task_2")

    def test_no_available_task_when_all_complete(self):
        """Test returns None when all tasks complete"""
        all_tasks = [
            {"id": "task_1", "status": "completed", "blockedBy": []},
            {"id": "task_2", "status": "completed", "blockedBy": ["task_1"]},
            {"id": "task_3", "status": "completed", "blockedBy": ["task_2"]},
        ]

        next_task = self.solver.find_next_available_task(all_tasks)

        self.assertIsNone(next_task)

    def test_skip_completed_and_find_next(self):
        """Test skips completed tasks and finds next available"""
        all_tasks = [
            {"id": "task_1", "status": "completed", "blockedBy": []},
            {"id": "task_2", "status": "completed", "blockedBy": ["task_1"]},
            {"id": "task_3", "status": "pending", "blockedBy": ["task_2"]},
            {"id": "task_4", "status": "pending", "blockedBy": ["task_3"]},
        ]

        next_task = self.solver.find_next_available_task(all_tasks)

        self.assertIsNotNone(next_task)
        self.assertEqual(next_task["id"], "task_3")

    def test_task_still_blocked(self):
        """Test returns None when remaining tasks are blocked"""
        all_tasks = [
            {"id": "task_1", "status": "completed", "blockedBy": []},
            {"id": "task_2", "status": "pending", "blockedBy": ["task_1"]},  # Available
            {"id": "task_3", "status": "pending", "blockedBy": ["task_2"]},  # Blocked
        ]

        # Should return task_2, not None
        next_task = self.solver.find_next_available_task(all_tasks)
        self.assertIsNotNone(next_task)
        self.assertEqual(next_task["id"], "task_2")


class TestExecutePhase(unittest.TestCase):
    """Test phase execution preparation"""

    def setUp(self):
        """Set up test fixtures"""
        self.solver = IssueSolver(issue_number=409, mode="auto")

    def test_execute_phase_returns_spec(self):
        """Test execute_phase returns execution spec"""
        task = {
            "id": "task_1",
            "metadata": {
                "skill": "start-issue",
                "checkpoint": False,
                "issue_number": 409,
            },
        }

        result = self.solver.execute_phase(task)

        self.assertEqual(result["skill"], "start-issue")
        self.assertEqual(result["args"], "409")
        self.assertFalse(result["is_checkpoint"])
        self.assertFalse(result["use_subagent"])

    def test_execute_phase_eval_plan(self):
        """Test execute_phase for eval-plan skill"""
        task = {
            "id": "task_2",
            "metadata": {
                "skill": "eval-plan",
                "checkpoint": True,
                "issue_number": 409,
            },
        }

        result = self.solver.execute_phase(task)

        self.assertEqual(result["skill"], "eval-plan")
        self.assertEqual(result["args"], "409 --mode=auto")
        self.assertTrue(result["is_checkpoint"])

    def test_execute_phase_review(self):
        """Test execute_phase for review skill"""
        task = {
            "id": "task_4",
            "metadata": {"skill": "review", "checkpoint": True, "issue_number": 409},
        }

        result = self.solver.execute_phase(task)

        self.assertEqual(result["skill"], "review")
        self.assertEqual(result["args"], "")  # Review auto-detects branch
        self.assertTrue(result["is_checkpoint"])


class TestCheckpointLogicBasic(unittest.TestCase):
    """Test basic checkpoint validation logic"""

    def setUp(self):
        """Set up test fixtures"""
        self.solver = IssueSolver(issue_number=409, mode="auto")
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files"""
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def test_checkpoint_status_file_not_found(self):
        """Test checkpoint fails when status file missing"""
        task = {
            "metadata": {
                "skill": "eval-plan",
                "score_threshold": 90,
                "checkpoint_name": "Checkpoint 1",
            }
        }

        # Status file doesn't exist
        decision = self.solver.check_checkpoint(task)

        self.assertFalse(decision.should_continue)
        self.assertIsNone(decision.score)
        self.assertIn("not found", decision.reason)


class TestResumeManagement(unittest.TestCase):
    """Test resume point save and load"""

    def setUp(self):
        """Set up test fixtures"""
        self.solver = IssueSolver(issue_number=409, mode="auto")
        self.solver.task_ids = ["task_1", "task_2", "task_3", "task_4", "task_5"]
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, ".auto-solve-state.json")
        # Change working directory for state file access
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test files"""
        os.chdir(self.original_dir)
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
        os.rmdir(self.temp_dir)

    def test_load_resume_point_not_found(self):
        """Test load_resume_point returns None when file missing"""
        loaded_data = self.solver.load_resume_point()
        self.assertIsNone(loaded_data)

    def test_resume_workflow(self):
        """Test resume_workflow restores context"""
        resume_data = {
            "timestamp": datetime.now().isoformat(),
            "issue_number": 409,
            "stopped_at_task_id": "task_2",
            "stopped_at_phase": "1.5",
            "stopped_at_skill": "eval-plan",
            "reason": "score_below_threshold",
            "task_ids": ["task_1", "task_2", "task_3", "task_4", "task_5"],
            "mode": "auto",
        }

        context = self.solver.resume_workflow(resume_data)

        self.assertEqual(context["issue_number"], 409)
        self.assertEqual(context["mode"], "auto")
        self.assertTrue(context["resumed"])
        self.assertEqual(self.solver.issue_number, 409)
        self.assertEqual(self.solver.mode, "auto")


class TestDataClasses(unittest.TestCase):
    """Test Result and CheckpointDecision dataclasses"""

    def test_result_creation(self):
        """Test Result dataclass"""
        result = Result(success=True, score=95, error=None)
        self.assertTrue(result.success)
        self.assertEqual(result.score, 95)
        self.assertIsNone(result.error)

    def test_checkpoint_decision_creation(self):
        """Test CheckpointDecision dataclass"""
        decision = CheckpointDecision(
            should_continue=True, score=92, reason="Score 92 ≥ 90"
        )
        self.assertTrue(decision.should_continue)
        self.assertEqual(decision.score, 92)
        self.assertIn("≥", decision.reason)


if __name__ == "__main__":
    # Run tests with verbosity
    unittest.main(verbosity=2)
