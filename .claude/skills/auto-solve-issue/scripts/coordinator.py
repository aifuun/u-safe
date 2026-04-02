#!/usr/bin/env python3
"""
auto-solve-issue workflow coordinator

Orchestrates the 5-phase issue resolution workflow with checkpoints,
task dependencies, and resume capability.

Usage:
    python coordinator.py 409 --auto
    python coordinator.py 409 --interactive
    python coordinator.py 409 --resume
"""

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Result:
    """Result of phase execution"""
    success: bool
    score: Optional[int] = None
    error: Optional[str] = None


@dataclass
class CheckpointDecision:
    """Decision from checkpoint evaluation"""
    should_continue: bool
    score: Optional[int]
    reason: str


class IssueSolver:
    """Coordinates automated issue resolution workflow"""

    def __init__(self, issue_number: int, mode: str = "auto", use_subagent: bool = False):
        """Initialize issue solver

        Args:
            issue_number: GitHub issue number
            mode: "auto" (score-based checkpoints) or "interactive" (always ask)
            use_subagent: Use subagents instead of direct skill calls (legacy)
        """
        self.issue_number = issue_number
        self.mode = mode
        self.use_subagent = use_subagent
        self.task_ids: List[str] = []

    def create_task_chain(self) -> List[str]:
        """Create 5-phase task dependency chain

        Returns:
            List of task IDs in creation order

        Note:
            This method provides the task structure. The actual TaskCreate
            calls should be made by the AI orchestrator using Claude Code's
            Task tools.
        """
        task_definitions = [
            {
                "subject": f"Phase 1: start-issue #{self.issue_number}",
                "description": "Create branch, generate plan, sync with main",
                "activeForm": "Creating branch and plan",
                "metadata": {
                    "phase": "1",
                    "skill": "start-issue",
                    "checkpoint": False,
                    "issue_number": self.issue_number
                }
            },
            {
                "subject": f"Phase 1.5: eval-plan #{self.issue_number}",
                "description": "Validate implementation plan (score must be ≥ 90 for auto-continue)",
                "activeForm": "Evaluating plan",
                "metadata": {
                    "phase": "1.5",
                    "skill": "eval-plan",
                    "checkpoint": True,
                    "checkpoint_name": "Checkpoint 1",
                    "score_threshold": 90,
                    "issue_number": self.issue_number
                },
                "blockedBy": ["task_1"]  # Placeholder, actual IDs from TaskCreate
            },
            {
                "subject": f"Phase 2: execute-plan #{self.issue_number}",
                "description": "Implement all tasks from plan",
                "activeForm": "Executing implementation plan",
                "metadata": {
                    "phase": "2",
                    "skill": "execute-plan",
                    "checkpoint": False,
                    "issue_number": self.issue_number
                },
                "blockedBy": ["task_2"]
            },
            {
                "subject": f"Phase 2.5: review #{self.issue_number}",
                "description": "Validate code quality (score must be ≥ 90 for auto-continue)",
                "activeForm": "Reviewing code quality",
                "metadata": {
                    "phase": "2.5",
                    "skill": "review",
                    "checkpoint": True,
                    "checkpoint_name": "Checkpoint 2",
                    "score_threshold": 90,
                    "issue_number": self.issue_number
                },
                "blockedBy": ["task_3"]
            },
            {
                "subject": f"Phase 3: finish-issue #{self.issue_number}",
                "description": "Commit, create PR, merge, close issue",
                "activeForm": "Finishing issue",
                "metadata": {
                    "phase": "3",
                    "skill": "finish-issue",
                    "checkpoint": False,
                    "issue_number": self.issue_number
                },
                "blockedBy": ["task_4"]
            }
        ]

        return task_definitions

    def find_next_available_task(self, all_tasks: List[Dict]) -> Optional[Dict]:
        """Find next pending task with no blockers

        Args:
            all_tasks: List of all workflow tasks (from TaskList())

        Returns:
            Task dict with keys: id, subject, status, metadata, blockedBy
            None if all tasks complete or all remaining tasks blocked
        """
        workflow_tasks = [t for t in all_tasks if t["id"] in self.task_ids]

        for task in workflow_tasks:
            # Skip completed tasks
            if task["status"] == "completed":
                continue

            # Check if blocked
            if task.get("blockedBy"):
                # Check if all blockers are completed
                all_blockers_done = True
                for blocker_id in task["blockedBy"]:
                    blocker = next((t for t in workflow_tasks if t["id"] == blocker_id), None)
                    if blocker and blocker["status"] != "completed":
                        all_blockers_done = False
                        break

                if not all_blockers_done:
                    continue  # Still blocked

            # Found available task
            return task

        # No tasks available
        return None

    def execute_phase(self, task: Dict) -> Result:
        """Execute single workflow phase

        Args:
            task: Task metadata dict with keys: id, metadata.skill, metadata.checkpoint

        Returns:
            Result with success flag, score (if checkpoint), error message

        Note:
            This method prepares arguments for skill execution.
            The actual Skill() or Task() call should be made by AI orchestrator.
        """
        skill_name = task["metadata"]["skill"]
        is_checkpoint = task["metadata"].get("checkpoint", False)

        # Build skill arguments
        if skill_name == "eval-plan":
            skill_args = f"{self.issue_number} --mode={self.mode}"
        elif skill_name == "review":
            skill_args = ""  # Auto-detects current branch
        elif skill_name in ["start-issue", "execute-plan", "finish-issue"]:
            skill_args = str(self.issue_number)
        else:
            skill_args = str(self.issue_number)

        # Return execution spec for AI to invoke
        return {
            "skill": skill_name,
            "args": skill_args,
            "is_checkpoint": is_checkpoint,
            "use_subagent": self.use_subagent
        }

    def check_checkpoint(self, task: Dict) -> CheckpointDecision:
        """Evaluate checkpoint score and decide continuation

        Args:
            task: Checkpoint task metadata with skill name

        Returns:
            CheckpointDecision with should_continue flag, score, and reason
        """
        skill_name = task["metadata"]["skill"]
        threshold = task["metadata"]["score_threshold"]

        # Read appropriate status file
        if skill_name == "eval-plan":
            status_file = ".claude/.eval-plan-status.json"
        elif skill_name == "review":
            status_file = ".claude/.review-status.json"
        else:
            return CheckpointDecision(
                should_continue=False,
                score=None,
                reason=f"Unknown checkpoint skill: {skill_name}"
            )

        # Read status file
        try:
            with open(status_file, "r") as f:
                data = json.load(f)

            score = data.get("score")

            # Check validity (90 minutes)
            valid_until = data.get("valid_until")
            if valid_until:
                valid_time = datetime.fromisoformat(valid_until)
                now = datetime.now()
                if now > valid_time:
                    return CheckpointDecision(
                        should_continue=False,
                        score=score,
                        reason=f"{skill_name} status expired - re-run {skill_name}"
                    )

        except FileNotFoundError:
            return CheckpointDecision(
                should_continue=False,
                score=None,
                reason=f"Status file not found: {status_file}"
            )
        except json.JSONDecodeError:
            return CheckpointDecision(
                should_continue=False,
                score=None,
                reason=f"Invalid JSON in {status_file}"
            )

        # Evaluate score
        if score is None:
            if self.mode == "auto":
                return CheckpointDecision(
                    should_continue=False,
                    score=None,
                    reason="Score unavailable in auto mode"
                )
            else:
                # Interactive mode - decision from user
                return CheckpointDecision(
                    should_continue=None,  # Requires user input
                    score=None,
                    reason="User decision required (score unavailable)"
                )

        elif score < threshold:
            if self.mode == "auto":
                return CheckpointDecision(
                    should_continue=False,
                    score=score,
                    reason=f"Score {score} < {threshold} (auto mode)"
                )
            else:
                # Interactive mode - ask user
                return CheckpointDecision(
                    should_continue=None,  # Requires user input
                    score=score,
                    reason=f"User decision required (score {score} < {threshold})"
                )

        else:
            # Score >= threshold
            return CheckpointDecision(
                should_continue=True,
                score=score,
                reason=f"Score {score} ≥ {threshold}"
            )

    def save_resume_point(self, task_id: str, reason: str):
        """Save workflow state for resuming

        Args:
            task_id: ID of task where execution stopped
            reason: Why execution stopped (e.g., "score_below_threshold")
        """
        # Get task details - would need TaskGet() from AI orchestrator
        # For now, store essential data
        resume_data = {
            "timestamp": datetime.now().isoformat(),
            "issue_number": self.issue_number,
            "stopped_at_task_id": task_id,
            "reason": reason,
            "task_ids": self.task_ids,
            "mode": self.mode
        }

        state_file = ".claude/.auto-solve-state.json"
        with open(state_file, "w") as f:
            json.dump(resume_data, f, indent=2)

        print(f"\n💾 Resume point saved:")
        print(f"   State file: {state_file}")
        print(f"   Reason: {reason}")
        print(f"\n   Resume with: /auto-solve-issue #{self.issue_number} --resume")

    def load_resume_point(self) -> Optional[Dict]:
        """Load saved workflow state

        Returns:
            Resume data dict or None if no save exists
        """
        state_file = ".claude/.auto-solve-state.json"

        try:
            with open(state_file, "r") as f:
                data = json.load(f)

            print(f"\n💾 Resume point found:")
            print(f"   Saved at: {data['timestamp']}")
            print(f"   Reason: {data['reason']}")

            return data

        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            print(f"⚠️ Invalid resume state file: {state_file}")
            return None

    def resume_workflow(self, resume_data: Dict) -> Dict:
        """Restore workflow from saved state

        Args:
            resume_data: State loaded from file

        Returns:
            Context dict with task_ids, mode, issue_number for continuation
        """
        stopped_task_id = resume_data["stopped_at_task_id"]
        self.task_ids = resume_data["task_ids"]
        self.mode = resume_data["mode"]
        self.issue_number = resume_data["issue_number"]

        print(f"\n🔄 Resuming workflow...")
        print(f"   Issue: #{self.issue_number}")
        print(f"   Mode: {self.mode}")
        print(f"   Reset task {stopped_task_id} to pending")

        return {
            "task_ids": self.task_ids,
            "mode": self.mode,
            "issue_number": self.issue_number,
            "stopped_task_id": stopped_task_id,
            "resumed": True
        }


def read_eval_plan_score() -> Optional[int]:
    """Read score from .claude/.eval-plan-status.json

    Returns:
        Score (0-100) or None if unavailable
    """
    try:
        with open(".claude/.eval-plan-status.json", "r") as f:
            data = json.load(f)
            return data.get("score")
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None


def read_review_score() -> Optional[int]:
    """Read score from .claude/.review-status.json

    Returns:
        Score (0-100) or None if unavailable
    """
    try:
        with open(".claude/.review-status.json", "r") as f:
            data = json.load(f)
            return data.get("score")
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None


def cleanup_state_files():
    """Delete status files after workflow completion"""
    state_files = [
        ".claude/.auto-solve-state.json",
        ".claude/.eval-plan-status.json",
        ".claude/.review-status.json"
    ]

    for file_path in state_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"   Cleaned: {file_path}")
        except Exception as e:
            print(f"   Warning: Failed to clean {file_path}: {e}")


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python coordinator.py <issue-number> [--auto|--interactive] [--resume]")
        sys.exit(1)

    issue_number = int(sys.argv[1])
    mode = "interactive" if "--interactive" in sys.argv else "auto"
    resume_flag = "--resume" in sys.argv

    solver = IssueSolver(issue_number, mode)

    if resume_flag:
        resume_data = solver.load_resume_point()
        if resume_data:
            context = solver.resume_workflow(resume_data)
            print(f"   Task IDs: {context['task_ids']}")
        else:
            print("⚠️ No resume point found")
            sys.exit(1)
    else:
        print(f"🚀 Starting auto-solve for issue #{issue_number}")
        print(f"   Mode: {mode}")

        # Would create task chain here
        task_definitions = solver.create_task_chain()
        print(f"   Created {len(task_definitions)} phase definitions")


if __name__ == "__main__":
    main()
