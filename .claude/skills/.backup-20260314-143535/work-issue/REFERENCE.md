# Work Issue - Advanced Reference

**See**: [SKILL.md](SKILL.md) for main documentation

This document contains detailed examples, error scenarios, and advanced usage patterns.

## Detailed Examples

### Example 1: Interactive Workflow (Complete)

**User says:** "work on issue #23"

**Full execution trace:**
```
Phase 1: /start-issue #23
→ Validating environment... ✅
→ Fetching issue from GitHub... ✅
→ Creating branch: feature/23-add-user-auth ✅
→ Generating plan with 8 tasks... ✅
→ Creating todos... ✅
→ Branch pushed to origin ✅

Checkpoint 1: Review plan?
📋 Plan Preview:
  Task 1: Add User schema with Zod validation
  Task 2: Create authentication service
  Task 3: Implement login endpoint
  ... (5 more tasks)

Options: [C]ontinue / [E]dit / [S]top / [Q]uit
→ User enters: C

Phase 2: /execute-plan #23
→ Loading plan... ✅
→ Task 1/8: Add User schema... ✅ (5 min)
→ Task 2/8: Create auth service... ✅ (8 min)
→ Task 3/8: Implement login... ✅ (10 min)
→ Task 4/8: Add tests... ✅ (12 min)
→ Task 5/8: Update docs... ✅ (3 min)
→ Task 6/8: Error handling... ✅ (5 min)
→ Task 7/8: Integration test... ✅ (7 min)
→ Task 8/8: Final cleanup... ✅ (2 min)
→ All tasks complete!

Checkpoint 2: Review code?
📦 Implementation Status:
  Files changed: 12 files
  Lines: +450/-120
  Quick checks:
    ✅ TypeScript compiles
    ⚠️ 2 lint warnings (non-blocking)
    ✅ All tests passing (32/32)

Options: [C]ontinue / [F]ix / [S]top / [Q]uit
→ User enters: C

Phase 3: /review
→ Running quality gates... ✅
→ Checking architecture... ✅
→ Validating Pillars... ✅
→ Security scan... ✅
→ Performance check... ✅
→ Writing review status... ✅

Checkpoint 3: Review results
📊 Code Review Report:
  Status: approved_with_recommendations
  Score: 92/100

  Issues:
    Non-blocking:
    - Consider adding rate limiting (low priority)
    - Minor: Use const instead of let in 2 places

Options: [C]ontinue / [F]ix / [S]top / [Q]uit
→ User enters: C

Phase 4: /finish-issue #23
→ Pre-finish validation... ✅
→ Committing changes... ✅
→ Pushing to origin... ✅
→ Creating PR #107... ✅
→ Waiting for checks... ✅
→ Merging PR... ✅
→ Closing issue #23... ✅
→ Cleaning up branches... ✅
→ Switched to main branch ✅

✅ Workflow complete!
Total time: 52 minutes
```

### Example 2: Auto Mode (No Checkpoints)

**User says:** "work on issue #24 --auto, it's a simple bug fix"

**Execution:**
```bash
/work-issue #24 --auto

→ Phase 1: Starting issue...
  ✅ Branch: feature/24-fix-typo
  ✅ Plan: 3 simple tasks

→ Phase 2: Executing plan...
  ✅ Task 1/3: Fix typo in README (1 min)
  ✅ Task 2/3: Update test fixture (1 min)
  ✅ Task 3/3: Verify tests pass (30 sec)

→ Phase 3: Running review...
  ✅ Score: 100/100 (approved)

→ Phase 4: Finishing issue...
  ✅ PR #108 created and merged
  ✅ Issue #24 closed

✅ Complete in 3 minutes!
```

### Example 3: Stop After Plan

**User says:** "work on issue #25 but stop after planning"

**Execution:**
```bash
/work-issue #25 --stop-after=plan

→ Phase 1: Starting issue...
  ✅ Branch: feature/25-complex-refactor
  ✅ Plan: 15 detailed tasks
  ✅ Plan saved to: .claude/plans/active/issue-25-plan.md

✅ Stopped as requested

Next steps:
  1. Review plan: cat .claude/plans/active/issue-25-plan.md
  2. Edit if needed: vim .claude/plans/active/issue-25-plan.md
  3. When ready: /work-issue #25 --resume

  Or use individual skills:
    /execute-plan #25
    /review
    /finish-issue #25
```

### Example 4: Resume After Interruption

**Context:** User ran `/work-issue #26`, completed Phase 1 and 2, then had to stop.

**User says:** "resume work on issue #26"

**Execution:**
```bash
/work-issue #26 --resume

→ Detecting workflow state...
  ✅ State file found: .claude/.work-issue-state.json
  ✅ Issue #26: Add logging middleware
  ✅ Current phase: execute (complete)
  ✅ Next phase: review

→ Resuming from Checkpoint 2

Checkpoint 2: Review code?
📦 Implementation Status:
  (shows status from earlier session)

Options: [C]ontinue / [F]ix / [S]top / [Q]uit
→ User enters: C

→ Phase 3: Running review... ✅
→ Phase 4: Finishing issue... ✅

✅ Issue #26 complete!
```

## All Error Scenarios

### 1. Already on Feature Branch

**Scenario:** User runs `/work-issue #23` while on `feature/11-other-task`

**Error:**
```
❌ Cannot start workflow

Current state:
  Branch: feature/11-other-task
  Issue: #11 (in progress)

Requested:
  Issue: #23

Problem: Already working on a different issue

Solutions:
  1. Finish current work:
     /finish-issue #11

  2. Switch to main and start fresh:
     git checkout main
     /work-issue #23

  3. Force start (not recommended):
     /work-issue #23 --force
     Warning: This will abandon work on Issue #11

Which solution? (1/2/3):
```

### 2. Issue Not Found

**Scenario:** User runs `/work-issue #999` (non-existent issue)

**Error:**
```
❌ Phase 1 failed: Issue not found

Attempted: /start-issue #999
Error: Issue #999 does not exist

Troubleshooting:
  1. Check issue number:
     gh issue list

  2. Verify repository:
     gh repo view

  3. Check authentication:
     gh auth status

Workflow aborted.
```

### 3. Task Execution Failed

**Scenario:** During Phase 2, a task fails validation

**Error:**
```
❌ Phase 2 failed: Task execution error

Task 5/12: "Add integration tests"
Error: Test framework not installed

Workflow paused.

Options:
  1. Fix issue and resume:
     npm install --save-dev jest
     /work-issue #23 --resume

  2. Skip this task (use with caution):
     /execute-plan #23 --skip-task 5
     /work-issue #23 --resume

  3. Cancel workflow:
     rm .claude/.work-issue-state.json

Which option? (1/2/3):
```

### 4. Review Found Blocking Issues

**Scenario:** Phase 3 review finds critical issues

**Error:**
```
❌ Phase 3 completed with blocking issues

Review Status: issues_found
Score: 65/100

Blocking Issues:
  1. Security: SQL injection vulnerability in login.ts:45
  2. Architecture: Violates layer boundaries (ADR-003)

Workflow cannot continue to Phase 4.

Required actions:
  1. Fix blocking issues:
     - Use parameterized queries in login.ts:45
     - Move data access to repository layer

  2. Re-run review:
     /review

  3. Resume workflow when approved:
     /work-issue #23 --resume

Workflow paused. Fix issues before continuing.
```

### 5. PR Merge Failed

**Scenario:** Phase 4 attempts to merge but CI is failing

**Error:**
```
❌ Phase 4 failed: PR merge blocked

PR #109 created successfully
Status: checks failing

Failed Checks:
  ❌ CI: Unit tests (2 failing)
  ❌ CI: Lint check (12 warnings)
  ✅ CI: Build

Cannot merge until checks pass.

Options:
  1. Wait for checks (if transient failure):
     Wait 5-10 minutes, then:
     /work-issue #23 --resume

  2. Fix failing checks:
     - Fix tests locally
     - Push fixes: git push
     - Resume: /work-issue #23 --resume

  3. Manual merge via GitHub:
     - Override checks on GitHub (if permitted)
     - Mark workflow complete manually

Which option? (1/2/3):
```

### 6. Uncommitted Changes

**Scenario:** User runs `/work-issue #23` with uncommitted changes

**Error:**
```
⚠️ Uncommitted changes detected

Modified files:
  M  src/auth.ts
  M  src/types.ts
  ?? temp.txt

Cannot start workflow with uncommitted changes.

Options:
  1. Commit changes:
     git add .
     git commit -m "WIP: auth work"
     /work-issue #23

  2. Stash changes:
     git stash
     /work-issue #23
     (restore later: git stash pop)

  3. Discard changes (careful!):
     git checkout .
     /work-issue #23

Which option? (1/2/3):
```

## State Management Details

### State File Location

`.claude/.work-issue-state.json`

### State Schema

```json
{
  "version": "1.0.0",
  "issue_number": 23,
  "issue_title": "Add user authentication",
  "branch": "feature/23-add-user-authentication",
  "current_phase": "execute",
  "last_checkpoint": "plan_reviewed",
  "started_at": "2026-03-11T10:00:00Z",
  "updated_at": "2026-03-11T10:25:00Z",
  "phases_completed": ["start"],
  "phases_in_progress": ["execute"],
  "checkpoints_passed": {
    "review_plan": true,
    "review_code": false,
    "review_quality": false
  },
  "mode": "interactive",
  "can_resume": true,
  "errors": [],
  "metadata": {
    "tasks_total": 8,
    "tasks_completed": 5,
    "files_changed": 12
  }
}
```

### State Transitions

```
State: null (no state file)
  → /work-issue #23
  → State: phase=start, can_resume=false

State: phase=start, complete
  → Checkpoint 1 passed
  → State: phase=execute, checkpoint=plan_reviewed, can_resume=true

State: phase=execute, in_progress
  → User interrupts (Ctrl+C)
  → State: phase=execute, can_resume=true

State: phase=execute, complete
  → Checkpoint 2 passed
  → State: phase=review, checkpoint=code_reviewed, can_resume=true

State: phase=review, complete
  → Checkpoint 3 passed
  → State: phase=finish, checkpoint=quality_reviewed, can_resume=true

State: phase=finish, complete
  → Workflow done
  → State: deleted
```

### Resume Logic

```python
def detect_resume_point(state):
    if not state.exists():
        return None

    completed = state.phases_completed
    current = state.current_phase

    if current == "start" and "start" not in completed:
        return "start"  # Restart Phase 1

    if current == "execute" and "execute" not in completed:
        return "execute"  # Continue Phase 2

    if current == "review" and "review" not in completed:
        return "review"  # Continue Phase 3

    if current == "finish" and "finish" not in completed:
        return "finish"  # Continue Phase 4

    # Determine next phase based on last completed
    if "review" in completed:
        return "finish"  # Move to Phase 4

    if "execute" in completed:
        return "review"  # Move to Phase 3

    if "start" in completed:
        return "execute"  # Move to Phase 2

    return "start"  # Default: start from beginning
```

## Performance Benchmarks

### Timing Breakdown by Issue Complexity

**Simple Issue** (1-3 tasks, bug fix):
- Phase 1: 30 seconds
- Checkpoint 1: 10 seconds (user decision)
- Phase 2: 2-5 minutes
- Checkpoint 2: 10 seconds
- Phase 3: 30 seconds
- Checkpoint 3: 10 seconds
- Phase 4: 1 minute
- **Total: 5-8 minutes**

**Medium Issue** (4-8 tasks, feature):
- Phase 1: 30 seconds
- Checkpoint 1: 30 seconds (review plan)
- Phase 2: 20-40 minutes
- Checkpoint 2: 30 seconds
- Phase 3: 1 minute
- Checkpoint 3: 1 minute
- Phase 4: 2 minutes
- **Total: 25-45 minutes**

**Complex Issue** (9-15 tasks, architecture):
- Phase 1: 45 seconds
- Checkpoint 1: 2 minutes (careful review)
- Phase 2: 60-120 minutes
- Checkpoint 2: 1 minute
- Phase 3: 2 minutes
- Checkpoint 3: 2 minutes (review findings)
- Phase 4: 3 minutes
- **Total: 70-130 minutes**

### Mode Comparison

| Mode | Simple | Medium | Complex |
|------|--------|--------|---------|
| Interactive | 8 min | 45 min | 130 min |
| Auto | 5 min | 30 min | 90 min |
| Savings | 3 min | 15 min | 40 min |

Auto mode saves checkpoint time but sacrifices review opportunities.

## Integration Patterns

### Pattern 1: Standard Flow

```
/work-issue #23
→ Complete end-to-end
→ Use when: straightforward issue
```

### Pattern 2: Plan → Manual → Finish

```
/work-issue #23 --stop-after=plan
→ Review plan
→ Implement manually
/finish-issue #23
→ Use when: want custom implementation
```

### Pattern 3: Resume Pattern

```
/work-issue #23
→ (interrupted)
... (do other work)
/work-issue #23 --resume
→ Use when: context switch needed
```

### Pattern 4: Individual Skills

```
/start-issue #23
/execute-plan #23
/review
/finish-issue #23
→ Use when: need fine control
```

## Advanced Configuration

### Custom Checkpoint Behavior

Future enhancement: Allow configuration of checkpoint behavior via `.claude/work-issue.config.json`:

```json
{
  "checkpoints": {
    "review_plan": {
      "enabled": true,
      "auto_continue_if": ["simple_issue", "bug_fix"]
    },
    "review_code": {
      "enabled": true,
      "auto_continue_if": ["all_tests_pass", "no_lint_errors"]
    },
    "review_quality": {
      "enabled": true,
      "auto_continue_if": ["score_above_90"]
    }
  },
  "auto_mode": {
    "max_tasks": 5,
    "max_files": 10,
    "require_tests": true
  }
}
```

---

## Batch Processing Examples

### Example: Daily Issue Batch (Full Trace)

**User says:** "/work-issue [128, 184, 33]"

**Full execution trace:**
```
🚀 Batch Processing: 3 issues queued
Mode: Stop on error (default)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #128 (1/3): Update documentation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 1: /start-issue #128
→ Validating environment... ✅
→ Fetching issue... ✅
→ Creating branch: feature/128-update-documentation ✅
→ Generating plan with 5 tasks... ✅
→ Branch pushed to origin ✅

Phase 1.5: /eval-plan #128
→ Architecture alignment: 40/40 ✅
→ Acceptance criteria: 30/30 ✅
→ Task dependencies: 15/15 ✅
→ Best practices: 10/10 ✅
→ Task clarity: 5/5 ✅
→ Score: 100/100 ✅
→ Auto mode: Skipping Checkpoint 1 (score > 90)

Phase 2: /execute-plan #128
→ Loading plan... ✅
→ Task 1/5: Update README... ✅ (3 min)
→ Task 2/5: Update CHANGELOG... ✅ (2 min)
→ Task 3/5: Update API docs... ✅ (5 min)
→ Task 4/5: Add examples... ✅ (4 min)
→ Task 5/5: Final review... ✅ (1 min)
→ All tasks complete!

Phase 2.5: /review
→ Quality gates: ✅
→ Architecture: ✅
→ Documentation: ✅
→ Score: 95/100 ✅
→ Auto mode: Skipping Checkpoint 2 (score > 90)

Phase 3: /finish-issue #128
→ Committing changes... ✅
→ Creating PR... ✅
→ Merging PR... ✅
→ Closing issue... ✅
→ Cleaning up branch... ✅

✅ Issue #128 complete (20 min)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #184 (2/3): Fix login bug
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 1: /start-issue #184
→ Validating environment... ✅
→ Fetching issue... ✅
→ Creating branch: feature/184-fix-login-bug ✅
→ Generating plan with 7 tasks... ✅
→ Branch pushed to origin ✅

Phase 1.5: /eval-plan #184
→ Architecture alignment: 38/40 ✅
→ Acceptance criteria: 28/30 ✅
→ Task dependencies: 14/15 ⚠️
→ Best practices: 9/10 ✅
→ Task clarity: 5/5 ✅
→ Score: 94/100 ✅
→ Auto mode: Skipping Checkpoint 1 (score > 90)

Phase 2: /execute-plan #184
→ Loading plan... ✅
→ Task 1/7: Reproduce bug... ✅ (8 min)
→ Task 2/7: Identify root cause... ✅ (10 min)
→ Task 3/7: Fix auth service... ✅ (12 min)
→ Task 4/7: Add regression test... ✅ (8 min)
→ Task 5/7: Update error handling... ✅ (5 min)
→ Task 6/7: Update docs... ✅ (2 min)
→ Task 7/7: Manual testing... ✅ (5 min)
→ All tasks complete!

Phase 2.5: /review
→ Quality gates: ✅
→ Architecture: ✅
→ Tests: ✅ (coverage 92%)
→ Score: 96/100 ✅
→ Auto mode: Skipping Checkpoint 2 (score > 90)

Phase 3: /finish-issue #184
→ Committing changes... ✅
→ Creating PR... ✅
→ Merging PR... ✅
→ Closing issue... ✅
→ Cleaning up branch... ✅

✅ Issue #184 complete (50 min)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #33 (3/3): Add error handling
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 1: /start-issue #33
→ Validating environment... ✅
→ Fetching issue... ✅
→ Creating branch: feature/33-add-error-handling ✅
→ Generating plan with 6 tasks... ✅
→ Branch pushed to origin ✅

Phase 1.5: /eval-plan #33
→ Architecture alignment: 40/40 ✅
→ Acceptance criteria: 30/30 ✅
→ Task dependencies: 15/15 ✅
→ Best practices: 10/10 ✅
→ Task clarity: 5/5 ✅
→ Score: 100/100 ✅
→ Auto mode: Skipping Checkpoint 1 (score > 90)

Phase 2: /execute-plan #33
→ Loading plan... ✅
→ Task 1/6: Define error types... ✅ (6 min)
→ Task 2/6: Add error boundary... ✅ (8 min)
→ Task 3/6: Implement logging... ✅ (7 min)
→ Task 4/6: Add retry logic... ✅ (10 min)
→ Task 5/6: Update tests... ✅ (6 min)
→ Task 6/6: Update docs... ✅ (3 min)
→ All tasks complete!

Phase 2.5: /review
→ Quality gates: ✅
→ Architecture: ✅
→ Error handling: ✅
→ Tests: ✅ (coverage 94%)
→ Score: 98/100 ✅
→ Auto mode: Skipping Checkpoint 2 (score > 90)

Phase 3: /finish-issue #33
→ Committing changes... ✅
→ Creating PR... ✅
→ Merging PR... ✅
→ Closing issue... ✅
→ Cleaning up branch... ✅

✅ Issue #33 complete (40 min)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Batch Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 3/3 issues completed successfully
Total time: 110 minutes

Batch summary:
- Issue #128: ✅ 20 min (documentation update)
- Issue #184: ✅ 50 min (bug fix)
- Issue #33: ✅ 40 min (error handling)

Batch state file cleaned up (successful completion)
```

### Example: Batch with Failure (Stop on Error)

**User says:** "/work-issue [45, 67, 89] --stop-on-error"

**Execution trace:**
```
🚀 Batch Processing: 3 issues queued
Mode: Stop on error

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #45 (1/3): Refactor authentication
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[... full workflow ...]
✅ Issue #45 complete (50 min)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #67 (2/3): Update API endpoints
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 1: /start-issue #67 ✅
Phase 1.5: /eval-plan #67

→ Architecture alignment: 28/40 ⚠️
→ Acceptance criteria: 25/30 ⚠️
→ Task dependencies: 10/15 ⚠️
→ Best practices: 6/10 ⚠️
→ Task clarity: 3/5 ⚠️
→ Score: 72/100 ⚠️

Issues found:
🔴 Task 3: Architecture violation (API call in UI component)
🔴 Missing: Error handling task
🔴 Task 5 depends on Task 8 (circular dependency)

⚠️ Issue #67 failed at eval-plan checkpoint
   Error: Plan score 72/100 (< 90 threshold)
   Recommendations need fixing before proceeding

Batch stopped (--stop-on-error mode)

Issues processed:
  ✅ 1/3 completed (Issue #45)
  ❌ 1/3 failed (Issue #67 - eval-plan score 72)
  ⏸️  1/3 skipped (Issue #89)

Batch state saved for resume:
  File: .claude/.work-issue-batch-state.json
  Resume with: /work-issue --resume-batch

Next steps:
1. Fix Issue #67 plan manually
2. Re-run: /work-issue #67 (single mode to validate fix)
3. Resume batch: /work-issue --resume-batch
```

### Example: Batch Resume After Fix

**User says:** "/work-issue --resume-batch"

**Execution trace:**
```
🔄 Resuming batch processing...
Batch ID: batch-2026-03-12-14-30

Previous results:
  ✅ Issue #45 completed (50 min)
  ❌ Issue #67 failed (eval-plan score 72)

Resuming from: Issue #67

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #67 (2/3): Update API endpoints [RETRY]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 1: /start-issue #67
→ Plan was manually fixed
→ Using existing branch: feature/67-update-api-endpoints

Phase 1.5: /eval-plan #67
→ Score: 95/100 ✅
→ Issues fixed!

[... continues with Phase 2-3 ...]
✅ Issue #67 complete (55 min)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #89 (3/3): Add comprehensive logging
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[... full workflow ...]
✅ Issue #89 complete (35 min)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Batch Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 3/3 issues completed successfully
Total time: 140 minutes (including retry)

Batch state file cleaned up
```

### Batch State File Structure

**File:** `.claude/.work-issue-batch-state.json`

**Example content:**
```json
{
  "batch_id": "batch-2026-03-12-14-30",
  "timestamp": "2026-03-12T14:30:00Z",
  "issues": [128, 184, 33],
  "current_index": 2,
  "mode": "stop_on_error",
  "results": {
    "128": {
      "status": "completed",
      "duration_minutes": 20,
      "plan_score": 100,
      "review_score": 95,
      "completed_at": "2026-03-12T14:50:00Z"
    },
    "184": {
      "status": "completed",
      "duration_minutes": 50,
      "plan_score": 94,
      "review_score": 96,
      "completed_at": "2026-03-12T15:40:00Z"
    },
    "33": {
      "status": "pending"
    }
  },
  "can_resume": true
}
```

**State transitions:**
- `pending` → Issue queued, not started
- `in_progress` → Currently executing
- `completed` → Successfully finished
- `failed` → Workflow failed at some phase
- `skipped` → Not processed (previous failure in stop-on-error mode)

---

**For main documentation**, see [SKILL.md](SKILL.md)
