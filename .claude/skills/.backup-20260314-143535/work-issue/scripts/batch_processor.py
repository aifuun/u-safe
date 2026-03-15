#!/usr/bin/env python3
"""
Batch processor for /work-issue skill.

Processes multiple issues sequentially with error handling and state management.
"""

import sys
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class BatchProcessor:
    """Orchestrates batch processing of multiple issues."""

    def __init__(self, issues: List[int], stop_on_error: bool = True):
        """
        Initialize batch processor.

        Args:
            issues: List of issue numbers to process
            stop_on_error: Stop batch on first failure (default: True)
        """
        self.issues = issues
        self.stop_on_error = stop_on_error
        self.state_file = Path.home() / "dev" / "ai-dev" / ".claude" / ".work-issue-batch-state.json"
        self.batch_id = f"batch-{datetime.now().strftime('%Y-%m-%d-%H-%M')}"
        self.results: Dict[int, Dict] = {}

    def parse_arguments(self, args: List[str]) -> Tuple[List[int], bool]:
        """
        Parse batch mode arguments.

        Supports:
        - [128, 184, 33] (JSON array)
        - 128,184,33 (comma-separated)
        - 128 184 33 (space-separated)

        Returns:
            (issue_numbers, stop_on_error)
        """
        issues = []
        stop_on_error = True

        for arg in args:
            # Check for error handling flags
            if arg == "--stop-on-error":
                stop_on_error = True
                continue
            elif arg == "--continue-on-error":
                stop_on_error = False
                continue

            # Parse issue numbers
            # JSON array: [128, 184, 33]
            if arg.startswith("[") and arg.endswith("]"):
                arg = arg[1:-1]  # Remove brackets
                issues.extend([int(x.strip()) for x in arg.split(",")])
            # Comma-separated: 128,184,33
            elif "," in arg:
                issues.extend([int(x.strip()) for x in arg.split(",")])
            # Space-separated or single number
            else:
                try:
                    issues.append(int(arg))
                except ValueError:
                    pass  # Skip non-numeric arguments

        return issues, stop_on_error

    def load_state(self) -> Optional[Dict]:
        """Load batch state from file."""
        if not self.state_file.exists():
            return None

        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def save_state(self, current_index: int, can_resume: bool = True):
        """Save batch state to file."""
        state = {
            "batch_id": self.batch_id,
            "issues": self.issues,
            "current_index": current_index,
            "results": self.results,
            "can_resume": can_resume,
            "timestamp": datetime.now().isoformat()
        }

        # Ensure directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def cleanup_state(self):
        """Remove state file after successful completion."""
        if self.state_file.exists():
            self.state_file.unlink()

    def execute_issue(self, issue_num: int) -> Dict:
        """
        Execute /work-issue for a single issue in auto mode.

        NOTE: This method is called by AI orchestration, not by the Python script directly.
        The Python script only manages state and progress tracking.

        AI orchestration should:
        1. Call Skill("work-issue", args=str(issue_num))
        2. Capture the result (success/failure)
        3. Call this method to record the result
        4. Continue to next issue or stop based on result

        Returns:
            Result dict with status, duration, failed_at, etc.
        """
        print(f"\n{'━' * 60}")
        print(f"Issue #{issue_num} ({self.issues.index(issue_num) + 1}/{len(self.issues)})")
        print(f"{'━' * 60}")

        start_time = datetime.now()

        # IMPORTANT: This is a placeholder for AI orchestration
        # When AI executes batch processing, it should:
        # 1. Launch: Skill("work-issue", args=str(issue_num))
        # 2. Wait for completion
        # 3. Record actual result here

        # Return pending status - AI orchestration will update this
        result = {
            "status": "pending",
            "duration_minutes": 0,
            "failed_at": None,
            "start_time": start_time.isoformat()
        }

        print(f"⏳ Issue #{issue_num} queued for AI orchestration")
        print(f"   AI should execute: Skill('work-issue', args='{issue_num}')")

        return result

    def run_batch(self) -> Dict:
        """
        Execute batch processing.

        Returns:
            Summary dict with total, completed, failed counts
        """
        print(f"\n🚀 Batch Processing: {len(self.issues)} issues queued")
        print(f"Mode: {'Stop on error' if self.stop_on_error else 'Continue on error'}\n")

        for index, issue_num in enumerate(self.issues):
            # Execute issue
            result = self.execute_issue(issue_num)
            self.results[issue_num] = result

            # Save state after each issue
            self.save_state(index + 1)

            # Check if we should stop
            if result["status"] == "failed" and self.stop_on_error:
                print(f"\n⚠️ Batch stopped (--stop-on-error)")
                print(f"Issues processed: {index + 1}/{len(self.issues)}")

                # Count results
                completed = sum(1 for r in self.results.values() if r["status"] == "completed")
                failed = sum(1 for r in self.results.values() if r["status"] == "failed")
                skipped = len(self.issues) - (index + 1)

                print(f"  ✅ {completed}/{len(self.issues)} completed")
                print(f"  ❌ {failed}/{len(self.issues)} failed")
                print(f"  ⏸️  {skipped}/{len(self.issues)} skipped")
                print(f"\nResume with: /work-issue --resume-batch")

                return {
                    "total": len(self.issues),
                    "completed": completed,
                    "failed": failed,
                    "skipped": skipped
                }

        # All issues processed
        completed = sum(1 for r in self.results.values() if r["status"] == "completed")
        failed = sum(1 for r in self.results.values() if r["status"] == "failed")

        print(f"\n{'━' * 60}")
        print(f"Batch Complete")
        print(f"{'━' * 60}")
        print(f"✅ {completed}/{len(self.issues)} issues completed")
        if failed > 0:
            print(f"❌ {failed}/{len(self.issues)} issues failed")
            print(f"\nFailed issues need manual attention:")
            for issue_num, result in self.results.items():
                if result["status"] == "failed":
                    print(f"  - Issue #{issue_num}: {result.get('error', 'Unknown error')}")

        total_duration = sum(r.get("duration_minutes", 0) for r in self.results.values())
        print(f"Total time: {total_duration} minutes")

        # Cleanup state on successful completion
        if failed == 0:
            self.cleanup_state()

        return {
            "total": len(self.issues),
            "completed": completed,
            "failed": failed,
            "skipped": 0
        }

    def resume_batch(self) -> Dict:
        """Resume interrupted batch from saved state."""
        state = self.load_state()
        if not state or not state.get("can_resume"):
            raise ValueError("No resumable batch found")

        print(f"\n🔄 Resuming batch processing...")
        print(f"Batch ID: {state['batch_id']}\n")

        # Restore state
        self.issues = state["issues"]
        self.results = {int(k): v for k, v in state["results"].items()}
        current_index = state["current_index"]

        # Show previous results
        print("Previous results:")
        for issue_num in self.issues[:current_index]:
            result = self.results.get(issue_num, {})
            status = result.get("status", "unknown")
            if status == "completed":
                print(f"  ✅ Issue #{issue_num} completed")
            elif status == "failed":
                print(f"  ❌ Issue #{issue_num} failed")

        # Continue from current_index
        remaining_issues = self.issues[current_index:]
        print(f"\nResuming from: {len(remaining_issues)} remaining issues\n")

        self.issues = remaining_issues
        return self.run_batch()


def main():
    """Main entry point for batch processor."""
    if "--resume-batch" in sys.argv:
        processor = BatchProcessor([], stop_on_error=True)
        try:
            summary = processor.resume_batch()
            sys.exit(0 if summary["failed"] == 0 else 1)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        # Parse arguments
        args = sys.argv[1:]
        if not args:
            print("Usage: batch_processor.py [issue1, issue2, ...] [--stop-on-error|--continue-on-error]")
            sys.exit(1)

        issues, stop_on_error = BatchProcessor([], stop_on_error=True).parse_arguments(args)

        if not issues:
            print("Error: No valid issue numbers provided")
            sys.exit(1)

        processor = BatchProcessor(issues, stop_on_error)
        summary = processor.run_batch()

        # Exit with error code if any failures
        sys.exit(0 if summary["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
