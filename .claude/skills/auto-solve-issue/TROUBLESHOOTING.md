# Auto-Solve Issue - Troubleshooting Guide

> Error scenarios, retry logic, and recovery strategies

## Overview

This document covers error handling in `/auto-solve-issue`:

1. **Error Categories** - Different types of failures and how they're handled
2. **Retry Logic** - Automatic retry (up to 3 attempts) for transient errors
3. **Resume Points** - Checkpoint saving for graceful recovery
4. **Common Scenarios** - Real-world error situations and solutions

## Error Handling Architecture

**Integrated into main execution loop** (Step 4 in PHASES.md):

```python
while True:
    next_task = find_next_available_task(task_ids)

    # Execute phase
    try:
        result = execute_phase(next_task, mode)
    except Exception as e:
        # Handle unexpected errors with retry
        handle_error_with_retry(next_task, e)
        continue

    # Handle graceful failures
    if not result.success:
        handle_error_with_retry(next_task, result.error)
        continue

    # Handle checkpoint failures
    if is_checkpoint and not should_continue:
        save_resume_point(next_task, reason)
        break
```

## Error Categories

### 1. Subagent Execution Errors

**What**: Unexpected exceptions during skill execution

**Handling**: Retry up to 3 times with exponential backoff

```python
try:
    result = execute_with_subagent(next_task, mode)
except Exception as e:
    # Unexpected error during subagent execution
    print(f"❌ Unexpected error in Phase {phase}: {e}")

    # Increment retry count
    retry_count = next_task["metadata"].get("retry_count", 0) + 1

    if retry_count >= 3:
        # Max retries exceeded
        save_resume_point(next_task["id"], f"error_max_retries: {str(e)}")
        break
    else:
        # Retry with updated metadata
        TaskUpdate(
            next_task["id"],
            status="pending",
            metadata={"retry_count": retry_count}
        )
        continue
```

**Example:**
```
Phase 2: execute-plan fails with "Connection timeout"

⚠️ Retrying Phase 2 (attempt 2/3)
[retry 1] ❌ Connection timeout
⚠️ Retrying Phase 2 (attempt 3/3)
[retry 2] ❌ Connection timeout
❌ Max retries (3) exceeded for Phase 2

💾 Resume point saved:
   Reason: error_max_retries: Connection timeout
```

---

### 2. Graceful Skill Failures

**What**: Skill reports failure (not exception) with error message

**Handling**: Same retry logic as exceptions

```python
if not result["success"]:
    # Subagent reported failure (not exception)
    error_msg = result["error"]
    print(f"❌ Phase {phase} failed: {error_msg}")

    retry_count = next_task["metadata"].get("retry_count", 0) + 1

    if retry_count >= 3:
        save_resume_point(next_task["id"], f"failed_{skill}: {error_msg}")
        break
    else:
        print(f"⚠️ Retrying (attempt {retry_count + 1}/3)")
        TaskUpdate(
            next_task["id"],
            status="pending",
            metadata={"retry_count": retry_count}
        )
        continue
```

**Example:**
```
Phase 1: start-issue fails

❌ Phase 1 failed: Branch feature/23-auth already exists

⚠️ Retrying (attempt 2/3)
[retry 1] ✅ Deleted existing branch
✅ Phase 1 completed
```

---

### 3. Checkpoint Score Unavailable

**What**: Status file missing or score field is null

**Handling**:
- Auto mode: Stop immediately (requires score)
- Interactive mode: Ask user to decide

```python
if is_checkpoint and score is None:
    print(f"⚠️ {checkpoint_name} score unavailable")

    if mode == "auto":
        save_resume_point(next_task["id"], "score_unavailable")
        print(f"⏸️ Fix {skill} and resume: /auto-solve-issue #{issue_number} --resume")
        break
    else:
        # Interactive mode - ask user
        user_decision = ask_user_to_continue()
        if user_decision != "continue":
            save_resume_point(next_task["id"], "user_stopped")
            break
```

**Example:**
```
Phase 1.5: eval-plan completes but status file corrupted

⏸️ Checkpoint 1
   Score: null
   Threshold: 90

⚠️ Score unavailable

⏸️ Stopping - fix issue and use --resume

Possible causes:
1. Status file not written: .claude/.eval-plan-status.json
2. Corrupted JSON in status file
3. Skill failed before writing status

Fix:
1. Check if file exists: ls .claude/.eval-plan-status.json
2. If missing: /eval-plan #23 --mode=auto
3. If corrupted: rm .claude/.eval-plan-status.json && /eval-plan #23
4. Resume: /auto-solve-issue #23 --resume
```

---

### 4. Checkpoint Score Below Threshold

**What**: Score < 90 in auto mode

**Handling**:
- Auto mode: Stop and save resume point
- Interactive mode: Ask user

```python
if is_checkpoint and score < threshold:
    print(f"⚠️ {checkpoint_name} score {score} < {threshold}")

    if mode == "auto":
        save_resume_point(next_task["id"], "score_below_threshold")
        print(f"⏸️ Fix issues and resume: /auto-solve-issue #{issue_number} --resume")
        break
    else:
        # Interactive mode - ask user
        user_decision = ask_user_to_continue()
        if user_decision != "continue":
            save_resume_point(next_task["id"], "user_stopped")
            break
```

**Example:**
```
Phase 2.5: review completes with low score

⏸️ Checkpoint 2
   Score: 75/100
   Threshold: 90

⚠️ Score 75 < 90 (auto mode)

⏸️ Stopping at Checkpoint 2
   Score 75/100 is below threshold 90
   Fix issues and resume: /auto-solve-issue #23 --resume

Issues Found:
- Missing error handling (5 locations)
- N+1 queries (userLoader.ts:23)
- No input validation (auth.ts:45)

Fix and resume:
1. Address issues above
2. Re-run: /review
3. Verify score ≥ 90
4. Resume: /auto-solve-issue #23 --resume
```

---

### 5. Task System Errors

**What**: Errors in TaskList(), TaskGet(), TaskUpdate()

**Handling**: Stop immediately, save resume point

```python
try:
    next_task = find_next_available_task(task_ids)
except Exception as e:
    print(f"❌ Error finding next task: {e}")
    save_resume_point(task_ids[0], f"task_system_error: {str(e)}")
    break
```

**Example:**
```
Task system error during task lookup

❌ Error finding next task: Task task_140 not found

💾 Resume point saved:
   Reason: task_system_error: Task task_140 not found

This is rare - possible causes:
1. Task was deleted externally
2. Claude Code task system issue
3. Concurrent modification

Fix:
1. Check task list: /tasks
2. Verify task_140 exists
3. If missing, can't resume (restart workflow)
```

---

## Error Categories Summary

| Error Type | Handling | Max Retries | Resume Point | Auto Mode | Interactive Mode |
|------------|----------|-------------|--------------|-----------|------------------|
| **Subagent timeout** | Retry | 3 | After 3 failures | Stop | Stop |
| **Subagent exception** | Retry | 3 | After 3 failures | Stop | Stop |
| **Graceful failure** | Retry | 3 | After 3 failures | Stop | Stop |
| **Checkpoint score < 90** | Stop | N/A | Immediate | Stop | Ask user |
| **Checkpoint score N/A** | Stop | N/A | Immediate | Stop | Ask user |
| **Task system error** | Stop | N/A | Immediate | Stop | Stop |

## Common Scenarios

### Scenario 1: Network Timeout

```
Problem:
   Phase 2 (execute-plan) fails with connection timeout

Symptoms:
   ❌ Phase 2 failed: Connection timeout
   ⚠️ Retrying (attempt 2/3)

Cause:
   Network issue, GitHub API rate limit, or slow connection

Solution:
   1. Wait for retry (automatic)
   2. If 3 retries fail:
      - Check network connection
      - Check GitHub status (status.github.com)
      - Wait 5-10 minutes for rate limits
      - Resume: /auto-solve-issue #23 --resume
```

### Scenario 2: Plan Quality Too Low

```
Problem:
   Checkpoint 1 fails with score 65/100

Symptoms:
   ⏸️ Checkpoint 1
      Score: 65/100 ≤ 90

Cause:
   - Vague task descriptions
   - Missing acceptance criteria
   - Architecture violations
   - Incomplete task breakdown

Solution:
   1. Review eval-plan results:
      cat .claude/.eval-plan-status.json | jq '.issues'
   2. Edit plan to fix issues:
      vim .claude/plans/active/issue-23-plan.md
   3. Re-evaluate:
      /eval-plan #23 --mode=auto
   4. Verify score ≥ 90
   5. Resume:
      /auto-solve-issue #23 --resume
```

### Scenario 3: Code Quality Issues

```
Problem:
   Checkpoint 2 fails with score 80/100

Symptoms:
   ⏸️ Checkpoint 2
      Score: 80/100 ≤ 90

   Issues: 0 blocking, 5 recommendations

Cause:
   - Missing error handling
   - Performance issues (N+1 queries)
   - Security concerns (no input validation)
   - Architecture violations

Solution:
   1. Review issues:
      cat .claude/.review-status.json | jq '.issues'
   2. Fix code issues:
      vim src/auth.ts src/userLoader.ts
   3. Re-review:
      /review
   4. Verify score ≥ 90
   5. Resume:
      /auto-solve-issue #23 --resume
```

### Scenario 4: Status File Expired

```
Problem:
   Checkpoint validation fails due to expired status (>90 minutes old)

Symptoms:
   ⏸️ Checkpoint 1
      Score: 95/100
      Status expired - re-run eval-plan

Cause:
   Too long between checkpoint and validation (>90 minutes)

Solution:
   1. Re-run skill to refresh status:
      /eval-plan #23 --mode=auto
   2. Resume immediately (within 90 minutes):
      /auto-solve-issue #23 --resume
```

### Scenario 5: Resume Point Lost

```
Problem:
   Can't find resume point after manual cleanup

Symptoms:
   /auto-solve-issue #23 --resume
   ⚠️ No resume point found

Cause:
   - State file deleted: .claude/.auto-solve-state.json
   - File corrupted
   - Wrong directory

Solution:
   1. Check if file exists:
      ls -la .claude/.auto-solve-state.json
   2. If missing, restart workflow:
      /auto-solve-issue #23 --auto
   3. Or manually run remaining phases:
      /execute-plan #23    # If plan already validated
      /review              # After implementation
      /finish-issue #23    # After review
```

---

## Retry Metadata

**Tracked per task** to avoid infinite loops:

```python
metadata = {
    "retry_count": 0,  # Increments on each failure
    "last_error": str(e),  # Error message from last failure
    "retry_history": [
        {"attempt": 1, "error": "...", "timestamp": "..."},
        {"attempt": 2, "error": "...", "timestamp": "..."}
    ]
}
```

**Max retries: 3** (hardcoded for safety)

**Why 3?**
- Handles transient errors (network blips)
- Avoids infinite loops
- Provides enough chances for recovery
- Still fails fast on persistent issues

---

## Graceful Degradation

**Priority: Never lose progress**

1. **Retry 3 times** - Give transient errors a chance to resolve
2. **Save resume point** - Preserve all workflow state
3. **Clear error messages** - Tell user exactly what failed and why
4. **Preserve context** - Task IDs, mode, issue number all saved
5. **Easy recovery** - Single `--resume` command to continue

**Philosophy**: Better to pause safely than to lose hours of work.

---

## Debugging Tips

### Enable Verbose Logging

```bash
# Add to coordinator.py for debugging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Task State

```bash
# View all tasks
/tasks

# Or use TaskList() in Python
python3 -c "
import sys
sys.path.insert(0, '.claude/skills/auto-solve-issue/scripts')
from coordinator import *
print(TaskList())
"
```

### Inspect Status Files

```bash
# Check eval-plan status
cat .claude/.eval-plan-status.json | jq '.'

# Check review status
cat .claude/.review-status.json | jq '.'

# Check resume state
cat .claude/.auto-solve-state.json | jq '.'
```

### Manual Recovery

If automatic resume fails, run phases manually:

```bash
# Phase 1: Start issue
/start-issue #23

# Phase 1.5: Evaluate plan
/eval-plan #23

# Phase 2: Execute plan
/execute-plan #23

# Phase 2.5: Review code
/review

# Phase 3: Finish issue
/finish-issue #23
```

---

**See also:**
- [PHASES.md](./PHASES.md) - Normal execution flow
- [CHECKPOINTS.md](./CHECKPOINTS.md) - Checkpoint system
- [EXAMPLES.md](./EXAMPLES.md) - Success scenarios
