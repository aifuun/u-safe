---
name: auto-solve-issue
version: "2.1.0"
description: |
  Complete issue lifecycle with Task dependencies and coordinator script - true zero-pause automation.
  TRIGGER when: user wants fully automated issue resolution ("auto-solve issue #N", "solve issue completely").
  DO NOT TRIGGER when: user wants manual control (use /auto-solve-issue --interactive), or individual phases (use specific skills).
last-updated: "2026-03-30"
---

# Auto-Solve Issue v2.1 - Script-Based Automation

> Complete issue lifecycle using Python coordinator + Task system for truly continuous execution

## Overview

This skill provides **fully automated issue resolution** without manual intervention:

**What it does:**
1. **Creates Task dependency chain** - 5 tasks with blockedBy relationships (via coordinator.py)
2. **Executes phases with direct skill calls** - Maintains worktree context (default)
3. **Validates at checkpoints** - Auto-continues if score ≥ 90
4. **Resumes from failures** - Checkpoint and resume mechanism
5. **Zero manual intervention** - Continuous loop until completion

**Why it's needed:**
Auto-solve-issue v1.0 had execution pauses requiring manual "continue" 3-4 times. The monolithic SKILL.md was 1232 lines and difficult to maintain. This v2.1 uses Python coordinator for workflow logic + focused documentation for maintainability.

**When to use:**
- Need complete automation without checkpoints
- Issue is well-defined with high confidence
- Trust validation scores (eval-plan, review)

**Workflow:**
```
/auto-solve-issue #23 [--auto|--interactive]
  → Coordinator creates 5 tasks with dependencies
  → Phase 1: start-issue (direct skill call)
  → Phase 1.5: eval-plan + checkpoint
  → Phase 2: execute-plan (direct skill call)
  → Phase 2.5: review + checkpoint
  → Phase 3: finish-issue (direct skill call)
  → All complete
```

## Arguments

```bash
/auto-solve-issue [issue-number] [options]
```

**Common usage:**
```bash
/auto-solve-issue #23              # Auto mode (score-based checkpoints)
/auto-solve-issue #23 --interactive # Stop at all checkpoints
/auto-solve-issue #23 --resume     # Resume from saved state
```

**Options:**
- `[issue-number]` - Required, which issue to solve
- `--auto` - Auto mode (default) - continues if score ≥ 90
- `--interactive` - Stop at checkpoints for manual review
- `--resume` - Resume from last checkpoint
- `--no-subagent` - Use direct skill calls instead of subagents (default, recommended)

## Architecture Overview

**Script-Based Pattern (ADR-014 compliant):**

This skill delegates workflow orchestration to `scripts/coordinator.py`, which implements the `IssueSolver` class:

```python
class IssueSolver:
    """Coordinates automated issue resolution workflow"""

    def __init__(self, issue_number: int, mode: str = "auto", use_subagent: bool = False)
    def create_task_chain(self) -> List[str]
    def find_next_available_task(self, all_tasks: List[Dict]) -> Optional[Dict]
    def execute_phase(self, task: Dict) -> Result
    def check_checkpoint(self, task: Dict) -> CheckpointDecision
    def save_resume_point(self, task_id: str, reason: str)
    def load_resume_point(self) -> Optional[Dict]
    def resume_workflow(self, resume_data: Dict) -> Dict
```

**Key Components:**
1. **Task Dependency Chain** (Step 1): Creates 5 tasks (Phases 1, 1.5, 2, 2.5, 3) with blockedBy relationships
2. **Main Execution Loop** (Step 4): `while True` loop that finds next available task, executes, handles checkpoints
3. **Checkpoint System** (Step 5): Reads `.claude/.eval-plan-status.json` and `.claude/.review-status.json`, validates score ≥ 90
4. **Resume Mechanism** (Step 6): Saves state to `.claude/.auto-solve-state.json`, restores on `--resume`
5. **Error Handling** (Step 7): Retry up to 3 times, save resume point on max retries
6. **Skill Execution** (Step 3): Direct `Skill()` calls (default) or Task subagents (legacy)

**Why Python coordinator?**
- ✅ **Maintainability**: Logic in code, not embedded in markdown
- ✅ **Testability**: Unit tests for workflow logic (see `tests/test_integration.py`)
- ✅ **Clarity**: Separation of concerns (coordinator vs AI instructions)
- ✅ **Compliance**: Follows ADR-014 script-based pattern for complex skills

## AI Execution Instructions

**CRITICAL: How AI orchestrates the workflow**

When user invokes `/auto-solve-issue #23 --auto`, AI should:

1. **Import coordinator module**:
   ```python
   import sys
   sys.path.insert(0, '.claude/skills/auto-solve-issue/scripts')
   from coordinator import IssueSolver
   ```

2. **Create workflow instance**:
   ```python
   solver = IssueSolver(issue_number=23, mode="auto", use_subagent=False)
   ```

3. **Create task chain**:
   ```python
   task_definitions = solver.create_task_chain()

   # Create tasks using TaskCreate
   task_ids = []
   for i, task_def in enumerate(task_definitions, 1):
       task = TaskCreate(
           subject=task_def["subject"],
           description=task_def["description"],
           activeForm=task_def["activeForm"],
           metadata=task_def["metadata"]
       )
       task_ids.append(task.id)

       # Add dependencies
       if task_def.get("blockedBy"):
           TaskUpdate(task.id, addBlockedBy=[task_ids[i-2]])  # Previous task
   ```

4. **Execute main loop**:
   ```python
   while True:
       # Find next available task
       all_tasks = TaskList()
       next_task = solver.find_next_available_task(all_tasks)

       if next_task is None:
           break  # All tasks complete

       # Mark in progress
       TaskUpdate(next_task["id"], status="in_progress")

       # Get execution spec
       exec_spec = solver.execute_phase(next_task)

       # Execute skill
       Skill(skill=exec_spec["skill"], args=exec_spec["args"])

       # Handle checkpoint
       if exec_spec["is_checkpoint"]:
           decision = solver.check_checkpoint(next_task)
           if not decision.should_continue:
               solver.save_resume_point(next_task["id"], decision.reason)
               break

       # Mark complete
       TaskUpdate(next_task["id"], status="completed")
   ```

**For detailed workflow steps**, see [PHASES.md](./PHASES.md).

**For checkpoint logic**, see [CHECKPOINTS.md](./CHECKPOINTS.md).

**For error handling**, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).

## Integration

**Comparison with work-issue:**

| Feature | work-issue | auto-solve-issue |
|---------|-----------|------------------|
| **Orchestration** | AI skill calls | Python coordinator + AI |
| **Execution** | Skill tool | Direct calls (default) |
| **Pauses** | After each phase | Checkpoints only |
| **Maturity** | Stable | Production (v2.1) |
| **Use Case** | General | Maximum automation |

**When to use each:**
- work-issue: Default, stable, well-tested
- auto-solve-issue: Need maximum speed, trust automation

## Performance

| Metric | v1.0 (manual) | v2.0 (tasks) | v2.1 (script) | Improvement |
|--------|---------------|--------------|---------------|-------------|
| **Pauses** | 5+ | 0-2 | 0-2 | 60-100% reduction |
| **Total time** | 45-75 min | 35-65 min | 35-65 min | 20-30% faster |
| **Maintainability** | Low | Medium | High | ADR-014 compliance |
| **Context usage** | Variable | < 50k | < 50k | Controlled |

## Documentation Structure

This skill follows ADR-014 script-based pattern with modular documentation:

- **SKILL.md** (this file): Overview, arguments, integration, quick start
- **[PHASES.md](./PHASES.md)**: Detailed 5-phase workflow with code examples (400 lines)
- **[CHECKPOINTS.md](./CHECKPOINTS.md)**: Checkpoint system and resume mechanism (200 lines)
- **[EXAMPLES.md](./EXAMPLES.md)**: Usage examples and best practices (200 lines)
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)**: Error scenarios and solutions (132 lines)
- **[ARCHITECTURE.md](./ARCHITECTURE.md)**: Design document and implementation guide
- **scripts/coordinator.py**: Core workflow orchestration logic (453 lines)
- **tests/test_integration.py**: Integration tests for workflow (TBD)

## Best Practices

1. **Use for well-defined issues** - Complex/vague issues may fail checkpoints
2. **Trust the scores** - Auto mode relies on eval-plan/review scores (≥90)
3. **Have fallback** - If issues occur, use /work-issue as backup
4. **Monitor first run** - Watch the continuous execution to build confidence
5. **Provide feedback** - Report bugs/issues to improve the skill

## Task Management

When executing, the coordinator creates this task structure:

```python
tasks = [
    TaskCreate("Phase 1: start-issue", ...),
    TaskCreate("Phase 1.5: eval-plan", ..., blockedBy=[task1]),
    TaskCreate("Phase 2: execute-plan", ..., blockedBy=[task2]),
    TaskCreate("Phase 2.5: review", ..., blockedBy=[task3]),
    TaskCreate("Phase 3: finish-issue", ..., blockedBy=[task4])
]
```

Updates status as each phase completes, automatically unlocking the next.

## Final Verification

```
- [ ] All 5 phases completed
- [ ] Both checkpoints passed (or manually approved)
- [ ] Issue closed on GitHub
- [ ] PR merged to main
- [ ] State files cleaned up
```

## Related Skills

- **/work-issue** - Stable alternative (AI orchestration)
- **/start-issue** - Phase 1 (called by this skill)
- **/eval-plan** - Phase 1.5 (called by this skill)
- **/execute-plan** - Phase 2 (called by this skill)
- **/review** - Phase 2.5 (called by this skill)
- **/finish-issue** - Phase 3 (called by this skill)

---

**Version:** 2.1.0
**Last Updated:** 2026-03-30
**Changelog:**
- v2.1.0 (2026-03-30): Refactor to script-based pattern (ADR-014) - Split 1232-line SKILL.md into coordinator.py + 5 docs (Issue #409)
- v2.0.0 (2026-03-18): Major redesign - replace solve-issue v1.0 with task dependencies (Issue #258)

**Pattern:** Script-Based Workflow Orchestrator
**Status:** Production
**Compliance:** ADR-001 ✅ | ADR-014 ✅
