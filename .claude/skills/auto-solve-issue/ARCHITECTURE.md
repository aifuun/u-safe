# auto-solve-issue Architecture Design

> Design document for scripts/coordinator.py refactoring (Issue #409)

## Current State Analysis

**File**: `.claude/skills/auto-solve-issue/SKILL.md`
**Lines**: 1232 (largest skill in framework)
**Problem**: All logic embedded in documentation, no code separation, difficult to test

## Core Components Identified

### 1. Task Dependency Chain (Step 1)
**Purpose**: Create 5-phase workflow with dependency relationships

**Logic**:
- Phase 1: start-issue (no dependencies)
- Phase 1.5: eval-plan (blocked by Phase 1) - CHECKPOINT
- Phase 2: execute-plan (blocked by Phase 1.5)
- Phase 2.5: review (blocked by Phase 2) - CHECKPOINT
- Phase 3: finish-issue (blocked by Phase 2.5)

**Key Data**:
```python
task_metadata = {
    "phase": "1.5",
    "skill": "eval-plan",
    "checkpoint": True,
    "checkpoint_name": "Checkpoint 1",
    "score_threshold": 90,
    "issue_number": 409
}
```

### 2. Main Execution Loop (Step 4)
**Purpose**: Continuously find and execute next available task until complete

**State Machine**:
```
while True:
    next_task = find_next_available_task(task_ids)
    if next_task is None:
        break  # All complete

    TaskUpdate(next_task, "in_progress")
    result = execute_phase(next_task, mode)

    if not result.success:
        handle_error_and_retry(next_task, result)
        continue

    if next_task.is_checkpoint:
        decision = check_checkpoint(result.score, mode)
        if not decision.should_continue:
            save_resume_point(next_task)
            break

    TaskUpdate(next_task, "completed")
```

### 3. Checkpoint System (Step 5)
**Purpose**: Validate plan quality (Phase 1.5) and code quality (Phase 2.5)

**Logic**:
- Read status file: `.claude/.eval-plan-status.json` or `.claude/.review-status.json`
- Extract score (0-100)
- Compare to threshold (90)
- Decision tree:
  - Auto mode + score ≥ 90 → continue
  - Auto mode + score < 90 → stop and save resume point
  - Interactive mode → ask user

### 4. Resume Mechanism (Step 6)
**Purpose**: Save workflow state for resuming after interruptions

**State File**: `.claude/.auto-solve-state.json`

**Data Structure**:
```json
{
  "timestamp": "2026-03-30T...",
  "issue_number": 409,
  "stopped_at_task_id": "task_139",
  "stopped_at_phase": "1.5",
  "stopped_at_skill": "eval-plan",
  "reason": "score_below_threshold",
  "task_ids": ["task_138", "task_139", ...],
  "mode": "auto"
}
```

**Recovery**:
- Load state file
- Reset stopped task to "pending"
- Continue execution loop

### 5. Error Handling (Step 7)
**Purpose**: Retry transient failures, save state on persistent failures

**Retry Logic**:
- Max retries: 3
- Increment `retry_count` in task metadata
- After 3 failures: save resume point with reason

**Error Types**:
- Skill execution exception → retry
- Checkpoint score unavailable → stop
- Checkpoint score < threshold → stop (auto mode)
- Task system error → stop

### 6. Skill Execution (Step 3)
**Purpose**: Execute individual phase skills

**Two modes**:
1. **Direct calls** (default): `Skill(skill=skill_name, args=...)`
   - Maintains worktree context
   - Faster, no subagent overhead

2. **Subagent** (legacy): `Task(subagent_type="general-purpose", ...)`
   - Context isolation
   - Known worktree path issues

## Proposed Python Architecture

### Class: IssueSolver

```python
class IssueSolver:
    """Coordinates automated issue resolution workflow"""

    def __init__(self, issue_number: int, mode: str = "auto"):
        self.issue_number = issue_number
        self.mode = mode  # "auto" or "interactive"
        self.task_ids: List[str] = []
        self.use_subagent = False  # Default to direct calls

    def create_task_chain(self) -> List[str]:
        """Create 5-phase task dependency chain

        Returns:
            List of task IDs in execution order
        """

    def find_next_available_task(self) -> Optional[Dict]:
        """Find next pending task with no blockers

        Returns:
            Task dict or None if workflow complete
        """

    def execute_phase(self, task: Dict) -> Result:
        """Execute single workflow phase

        Args:
            task: Task metadata dict

        Returns:
            Result with success flag, score (if checkpoint), error
        """

    def check_checkpoint(self, task: Dict, score: int) -> CheckpointDecision:
        """Evaluate checkpoint score and decide continuation

        Args:
            task: Checkpoint task metadata
            score: Score from status file (0-100)

        Returns:
            Decision with should_continue flag and reason
        """

    def save_resume_point(self, task_id: str, reason: str):
        """Save workflow state for resuming

        Args:
            task_id: ID of task where execution stopped
            reason: Why execution stopped
        """

    def load_resume_point(self) -> Optional[Dict]:
        """Load saved workflow state

        Returns:
            Resume data dict or None if no save exists
        """

    def resume_workflow(self, resume_data: Dict):
        """Restore workflow from saved state

        Args:
            resume_data: State loaded from file
        """

    def run(self):
        """Main execution loop - run until complete or stopped"""
```

### Supporting Functions

```python
def read_eval_plan_score() -> Optional[int]:
    """Read score from .claude/.eval-plan-status.json"""

def read_review_score() -> Optional[int]:
    """Read score from .claude/.review-status.json"""

def cleanup_state_files():
    """Delete status files after completion"""
```

## File Structure After Refactoring

```
.claude/skills/auto-solve-issue/
├── SKILL.md (300 lines)          # Usage guide + skill invocation
├── PHASES.md (400 lines)         # 5-phase workflow details
├── CHECKPOINTS.md (200 lines)   # Checkpoint system explained
├── EXAMPLES.md (200 lines)       # Usage examples
├── TROUBLESHOOTING.md (132 lines) # Error scenarios
├── ARCHITECTURE.md (this file)  # Design documentation
├── scripts/
│   └── coordinator.py           # IssueSolver class (new)
└── tests/
    └── test_integration.py      # Integration tests (new)
```

## Key Design Decisions

1. **Use direct Skill() calls by default** - Maintains worktree context, avoids subagent complexity
2. **Store task IDs, not task objects** - Use TaskList() to refresh state each iteration
3. **Checkpoint scores from status files** - Decouple from skill execution
4. **Resume state in .claude/** - Consistent with other status files
5. **Retry up to 3 times** - Balance resilience vs infinite loops

## Testing Strategy

1. **Unit tests**: Individual methods (create_task_chain, find_next_available_task)
2. **Integration tests**: Full workflow with mock skills
3. **Checkpoint tests**: Save/resume at different points
4. **Error tests**: Retry logic, max retries, graceful degradation

## Migration Path

1. Create coordinator.py with IssueSolver class
2. Update SKILL.md to call Python script
3. Run integration tests
4. Validate with real issue (dogfooding)
5. Compare behavior before/after

## Acceptance Criteria

- [ ] coordinator.py implements all 7 core functions
- [ ] SKILL.md reduced to < 500 lines
- [ ] Integration tests cover main scenarios
- [ ] Test coverage > 60%
- [ ] Behavior matches original (no regression)
- [ ] Marked "Compliance: ADR-014 ✅"
