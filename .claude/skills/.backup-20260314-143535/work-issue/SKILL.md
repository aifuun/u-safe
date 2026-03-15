---
name: work-issue
description: |
  Complete issue lifecycle with automated validation - orchestrates /start-issue, /eval-plan, /execute-plan, /review, and /finish-issue.
  Supports batch processing for multiple issues sequentially.
  TRIGGER when: user wants end-to-end automation ("work on issue #23", "handle issue", "complete issue #45", "work issue", "work on issues 128, 184, 33").
  DO NOT TRIGGER when: user wants individual steps (use skills separately for fine control).
argument-hint: "[issue-number|[issue1,issue2,...]| [--interactive] [--stop-after=phase] [--resume] [--stop-on-error|--continue-on-error]"
allowed-tools: Skill(*), Bash(git *), Bash(gh *), Read
disable-model-invocation: false
user-invocable: true
---

# Work Issue - Complete Issue Lifecycle Orchestrator

Automate the entire issue lifecycle with symmetric validation.

## Overview

Orchestrates 5 workflow skills with 2 validation checkpoints:

**Workflow:**
1. **Phase 1**: `/start-issue` - Branch + plan
2. **Phase 1.5**: `/eval-plan` - Validate plan (automated)
3. **Checkpoint 1**: Review eval results, edit plan if needed
4. **Phase 2**: `/execute-plan` - Implementation
5. **Phase 2.5**: `/review` - Validate code (automated)
6. **Checkpoint 2**: Review quality results, fix if needed
7. **Phase 3**: `/finish-issue` - Commit + PR + merge

**Symmetric validation:**
- Phase 1 → Automated `/eval-plan` validates plan → Checkpoint 1
- Phase 2 → Automated `/review` validates code → Checkpoint 2

**Why needed:**
Users must remember 5 separate commands. This automates the sequence with validation gates.

**When to use:**
- Want complete automation with validation
- Working on any issue (simple or complex)
- Prefer guided workflow over manual steps

**When NOT to use:**
- Need fine control → use individual skills
- Already mid-workflow → use --resume or individual skills

## Arguments

### Single Issue Mode

```bash
/work-issue [issue-number] [options]
```

**Options:**
- `[issue-number]` - Issue to work on (inferred from branch if omitted)
- `--auto` - Auto mode with score-based checkpoints (DEFAULT - used when no mode specified)
- `--interactive` - Stop at both checkpoints for manual review
- `--stop-after=phase` - Stop after: plan, eval, execute, or review
- `--resume` - Resume from last checkpoint

**Mode Selection:**
- **No flag** → Auto mode (default behavior)
- **`--auto`** → Auto mode (explicit)
- **`--interactive`** → Interactive mode

### Batch Processing Mode

```bash
/work-issue [issue1, issue2, issue3] [options]
/work-issue issue1,issue2,issue3 [options]
/work-issue issue1 issue2 issue3 [options]
```

**Batch-specific options:**
- `--stop-on-error` - (Default) Stop batch if any issue fails
- `--continue-on-error` - Process all issues even if some fail
- `--resume-batch` - Resume interrupted batch from last incomplete issue

**Batch behavior:**
- Auto mode applied by default (no checkpoints)
- Issues processed sequentially in order
- State saved after each issue for resume capability
- Final summary shows success/failure for all issues

## AI Execution Instructions

**CRITICAL: Mode detection and default behavior**

When executing `/work-issue`, AI MUST follow this logic:

```python
# Step 1: Parse arguments
issue_number = parse_issue_number(arguments)
mode = "auto"  # DEFAULT MODE

# Step 2: Check for mode flags
if "--interactive" in arguments:
    mode = "interactive"
elif "--auto" in arguments:
    mode = "auto"
# else: mode remains "auto" (default)

# Step 3: Execute workflow based on mode
if mode == "auto":
    # Score-based automatic approval
    # - Score > 90: Skip checkpoint, proceed automatically
    # - Score ≤ 90: Stop at checkpoint for human review
    # - Blocking issues: Always stop
    execute_auto_mode(issue_number)
elif mode == "interactive":
    # Always stop at both checkpoints
    execute_interactive_mode(issue_number)
```

**Default behavior (no mode flag):**
```bash
/work-issue #23        # ← Uses --auto mode by default
/work-issue #23 --auto # ← Explicitly specifies auto mode (same result)
```

**Key principle:** If user does NOT specify `--interactive`, always use auto mode.

### Continuous Execution Pattern (CRITICAL)

**DO NOT STOP between phases** - When executing work-issue, AI must complete the entire workflow in a continuous loop without pausing between sub-skills.

**Execution loop:**
```python
# CONTINUOUS EXECUTION - DO NOT STOP until workflow complete

# Phase 1: Start Issue
Skill("start-issue", args=str(issue_number))
# ✅ Phase 1 complete → IMMEDIATELY proceed to Phase 1.5 (DO NOT WAIT)

# Phase 1.5: Evaluate Plan
Skill("eval-plan", args=str(issue_number))
# ✅ Phase 1.5 complete → Check score and checkpoint logic

# Checkpoint 1: Auto mode decision
eval_score = read_eval_status()["score"]
if mode == "auto" and eval_score > 90:
    # ✅ Score > 90 → IMMEDIATELY proceed to Phase 2 (DO NOT STOP)
    pass
elif mode == "auto" and eval_score <= 90:
    # ⚠️ Score ≤ 90 → STOP for user review
    prompt_checkpoint_1()
    return  # Wait for user decision
elif mode == "interactive":
    # ⚠️ Interactive mode → ALWAYS STOP
    prompt_checkpoint_1()
    return  # Wait for user decision

# Phase 2: Execute Plan
Skill("execute-plan", args=str(issue_number))
# ✅ Phase 2 complete → IMMEDIATELY proceed to Phase 2.5 (DO NOT WAIT)

# Phase 2.5: Review Code
Skill("review")
# ✅ Phase 2.5 complete → Check score and checkpoint logic

# Checkpoint 2: Auto mode decision
review_score = read_review_status()["score"]
if mode == "auto" and review_score > 90:
    # ✅ Score > 90 → IMMEDIATELY proceed to Phase 3 (DO NOT STOP)
    pass
elif mode == "auto" and review_score <= 90:
    # ⚠️ Score ≤ 90 → STOP for user review
    prompt_checkpoint_2()
    return  # Wait for user decision
elif mode == "interactive":
    # ⚠️ Interactive mode → ALWAYS STOP
    prompt_checkpoint_2()
    return  # Wait for user decision

# Phase 3: Finish Issue
Skill("finish-issue", args=str(issue_number))
# ✅ Phase 3 complete → Workflow FINISHED

print("✅ Issue complete!")
```

**CRITICAL RULES:**

1. **Never pause between phases** - Each Skill() call must be immediately followed by the next phase (unless checkpoint logic requires stopping)

2. **Only stop at checkpoints** - In auto mode, ONLY stop when:
   - eval_score ≤ 90 (Checkpoint 1)
   - review_score ≤ 90 (Checkpoint 2)
   - blocking issues found
   - In interactive mode, ALWAYS stop at both checkpoints

3. **Complete sub-skill before proceeding** - Wait for Skill() tool result before moving to next phase, but DO NOT add unnecessary delays

4. **Auto mode = continuous by default** - Unless score triggers checkpoint, proceed immediately

5. **Phase transition is automatic** - No user confirmation needed between phases (only at checkpoints)

**Common mistake to avoid:**
```python
# ❌ WRONG - Stopping after every skill
Skill("start-issue", args=str(issue_number))
# [Stops here waiting for user input] ← BUG

# ✅ CORRECT - Continuous execution
Skill("start-issue", args=str(issue_number))
Skill("eval-plan", args=str(issue_number))  # Immediate transition
```

**Checkpoint detection:**
```python
# Read status files to determine if checkpoint should trigger
eval_status = read_json(".claude/.eval-plan-status.json")
review_status = read_json(".claude/.review-status.json")

# Auto mode checkpoint logic
if mode == "auto":
    if eval_status["score"] <= 90:
        stop_at_checkpoint_1()  # User must review
    # Otherwise continue automatically

    if review_status["score"] <= 90:
        stop_at_checkpoint_2()  # User must review
    # Otherwise continue automatically
```

## Workflow Steps

Copy this checklist to track progress:

```
Task Progress:
- [ ] Phase 1: Start issue (branch + plan)
- [ ] Phase 1.5: Evaluate plan (validate)
- [ ] Checkpoint 1: Review eval → edit if needed
- [ ] Phase 2: Execute plan (implementation)
- [ ] Phase 2.5: Review code (validate)
- [ ] Checkpoint 2: Review quality → fix if needed
- [ ] Phase 3: Finish issue (commit + PR + merge)
```

### Phase 1: Start Issue

**Execute**: `/start-issue #N`

**Output**: Branch + plan file + todos

**Time**: ~30 seconds

### Phase 1.5: Evaluate Plan

**Execute**: `/eval-plan #N` (automatic, issue number passed from Phase 1)

**Validates:**
- Architecture alignment (catches violations)
- Acceptance criteria coverage (ensures completeness)
- Task dependencies (correct ordering)
- Best practices (error handling, docs, logging)
- Task clarity (no vague tasks)

**Output**: Evaluation report with score and recommendations

**Time**: 30-60 seconds

### Checkpoint 1: Review Evaluation

**When triggered:**
- Interactive mode: Always stops
- Auto mode: Only if score ≤ 90

**Prompt:**
```
📊 Plan Evaluation

Issue #23: {title}
Status: ⚠️ Needs minor improvements
Score: 82/100

Issues Found:
🔴 Blocking: None

⚠️ Recommendations:
- Task 5: Violates clean architecture (move to service)
- Missing: Error handling task
- Task order: Task 3 depends on Task 7

💡 Suggestions:
- Consider documentation update task

[C]ontinue / [E]dit plan / [S]top / [Q]uit: _
```

**Auto mode behavior:**
- Score > 90: Skip checkpoint, proceed to Phase 2
- Score ≤ 90: Stop here, require human decision
- Blocking issues: Always stop (any mode)

### Phase 2: Execute Plan

**Execute**: `/execute-plan #N`

**Output**: Implemented code (uncommitted)

**Time**: 30 min - 2 hours (varies)

### Phase 2.5: Review Code

**Execute**: `/review` (automatic)

**Validates:**
- Quality gates (types, tests, linting)
- Architecture patterns
- Pillar compliance (if applicable)
- ADR compliance (if applicable)
- Security scan
- Performance check

**Output**: Review report with score and issues

**Time**: 1-2 minutes

### Checkpoint 2: Review Quality

**When triggered:**
- Interactive mode: Always stops
- Auto mode: Only if score ≤ 90

**Prompt:**
```
📊 Code Review

Status: ✅ Approved with recommendations
Score: 92/100

Issues Found:
🔴 Blocking: None

⚠️ Recommendations:
- Consider adding rate limiting
- Use const instead of let (2 places)

[C]ontinue / [F]ix issues / [S]top / [Q]uit: _
```

**Auto mode behavior:**
- Score > 90: Skip checkpoint, proceed to Phase 3
- Score ≤ 90: Stop here, require human decision
- Blocking issues: Always stop (any mode)

### Phase 3: Finish Issue

**Execute**: `/finish-issue #N`

**Output**: Merged PR + closed issue

**Time**: 2-3 minutes

## Modes

### Auto Mode (Default)

Score-based automatic approval with quality gates. **This is the default mode when no mode flag is specified.**

```bash
/work-issue #23              # Auto mode (default - no flag needed)
/work-issue #23 --auto       # Auto mode (explicit flag)
```

**Behavior:**
- Runs validation automatically (/eval-plan, /review)
- **Score > 90**: Skip checkpoint, proceed automatically
- **Score ≤ 90**: Stop at checkpoint for human review
- Fastest execution for high-quality plans/code
- Safety net for quality issues

**Checkpoint logic:**
- Eval-plan score > 90 → Skip Checkpoint 1
- Eval-plan score ≤ 90 → Stop at Checkpoint 1
- Review score > 90 → Skip Checkpoint 2
- Review score ≤ 90 → Stop at Checkpoint 2

**Use when:**
- Most use cases (default)
- Well-defined issues
- Trust validation scores
- Want speed with safety nets

### Interactive Mode

Stops at 2 validation checkpoints for manual approval.

```bash
/work-issue #23 --interactive
```

**Behavior:**
- Runs Phase 1 → Phase 1.5 → **STOP at Checkpoint 1**
- User reviews eval, decides: Continue / Edit / Stop
- Runs Phase 2 → Phase 2.5 → **STOP at Checkpoint 2**
- User reviews quality, decides: Continue / Fix / Stop
- Runs Phase 3

**Use when:**
- Want to review plan before implementation
- Want to review code before shipping
- Learning workflow
- Complex or risky issues
- Don't trust automation yet

### Partial Mode

Stops after specified phase.

```bash
/work-issue #23 --stop-after=eval      # Stop after plan eval
/work-issue #23 --stop-after=execute   # Stop after implementation
/work-issue #23 --stop-after=review    # Stop after code review
```

**Use when:**
- Want plan validation but manual implementation
- Want to implement and review later
- Need control at specific points

### Resume Mode

Continues from last checkpoint.

```bash
/work-issue #23 --resume
```

**Behavior:**
- Detects last completed phase
- Resumes from next checkpoint
- Maintains workflow state

**Use when:**
- Workflow interrupted
- Context switch needed
- Fixing issues found at checkpoint

## Batch Processing

Process multiple issues sequentially with a single command.

### Syntax

**All valid formats:**
```bash
/work-issue [128, 184, 33]           # JSON array syntax
/work-issue 128,184,33               # Comma-separated
/work-issue 128 184 33               # Space-separated
```

### Execution Model

**Sequential processing:**
```
For each issue in batch:
1. Execute: /work-issue {issue} --auto
2. Wait for complete workflow (all 7 phases)
3. If success: Continue to next issue
4. If failure: Handle based on error strategy
```

**Auto mode default:**
- Batch mode implies `--auto` flag
- No manual checkpoints (score > 90 continues, score ≤ 90 stops workflow)
- Can override: `/work-issue [128, 184, 33] --interactive`

### AI Orchestration (Implementation)

**CRITICAL: For AI executing batch processing**

When user requests batch processing (e.g., `/work-issue [128, 184, 33]`), the AI MUST orchestrate manually:

**Step-by-step execution:**
```python
# Parse issue list
issues = [128, 184, 33]
stop_on_error = True  # Default

# Initialize results tracking
results = {}

# Process each issue sequentially
for i, issue_num in enumerate(issues):
    print(f"\n{'━' * 60}")
    print(f"Issue #{issue_num} ({i+1}/{len(issues)})")
    print(f"{'━' * 60}\n")

    try:
        # Execute full work-issue workflow
        # MUST use Skill tool to invoke work-issue for each issue
        Skill("work-issue", args=str(issue_num))

        # If successful, record result
        results[issue_num] = {"status": "completed"}
        print(f"\n✅ Issue #{issue_num} complete\n")

    except Exception as e:
        # Record failure
        results[issue_num] = {"status": "failed", "error": str(e)}
        print(f"\n❌ Issue #{issue_num} failed: {e}\n")

        # Check if should stop
        if stop_on_error:
            print(f"⚠️ Batch stopped (--stop-on-error)")
            print(f"Issues processed: {i+1}/{len(issues)}")

            # Show summary
            completed = sum(1 for r in results.values() if r["status"] == "completed")
            failed = sum(1 for r in results.values() if r["status"] == "failed")
            skipped = len(issues) - (i+1)

            print(f"  ✅ {completed}/{len(issues)} completed")
            print(f"  ❌ {failed}/{len(issues)} failed")
            print(f"  ⏸️  {skipped}/{len(issues)} skipped")
            break

# Final summary
print(f"\n{'━' * 60}")
print("Batch Complete")
print(f"{'━' * 60}")

completed = sum(1 for r in results.values() if r["status"] == "completed")
failed = sum(1 for r in results.values() if r["status"] == "failed")

print(f"✅ {completed}/{len(issues)} issues completed")
if failed > 0:
    print(f"❌ {failed}/{len(issues)} issues failed")
```

**Important notes:**
- **MUST** use `Skill("work-issue", args=str(issue_num))` for each issue
- **MUST** wait for each Skill call to complete before proceeding
- **DO NOT** use Python subprocess or batch_processor.py directly
- batch_processor.py is only for state management, not execution

### Error Handling Strategies

**Conservative (Default) - `--stop-on-error`:**
```bash
/work-issue [128, 184, 33] --stop-on-error

Issue #128: ✅ Success
Issue #184: ❌ Failed (eval-plan score 65)
Issue #33:  ⏸️  Skipped (previous failure)

Result: Stopped after issue #184
```

**Aggressive - `--continue-on-error`:**
```bash
/work-issue [128, 184, 33] --continue-on-error

Issue #128: ✅ Success
Issue #184: ❌ Failed (eval-plan score 65)
Issue #33:  ✅ Success

Result: Completed 2/3 issues
```

### Progress Reporting

**Real-time status display:**
```
🚀 Batch Processing: 3 issues queued

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #128 (1/3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Phase 1: /start-issue #128... ✅
  Phase 1.5: /eval-plan... ✅ (Score: 95/100)
  Phase 2: /execute-plan... ✅
  Phase 2.5: /review... ✅ (Score: 92/100)
  Phase 3: /finish-issue... ✅
✅ Issue #128 complete (45 min)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #184 (2/3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Phase 1: /start-issue #184... ✅
  Phase 1.5: /eval-plan... ⚠️ (Score: 75/100)

⚠️ Issue #184 failed at eval-plan checkpoint
   Recommendations need fixing before proceeding
```

### State Management

**Batch state file:** `.claude/.work-issue-batch-state.json`

```json
{
  "batch_id": "batch-2026-03-12-14-30",
  "issues": [128, 184, 33],
  "current_index": 1,
  "results": {
    "128": {"status": "completed", "duration_minutes": 45},
    "184": {"status": "failed", "failed_at": "eval-plan"},
    "33": {"status": "pending"}
  },
  "can_resume": true
}
```

**Resume capability:**
```bash
/work-issue --resume-batch
# Continues from last incomplete issue
```

### Use Cases

**Daily Issue Batch:**
```bash
/work-issue [128, 184, 33, 205]
# Processes 4 issues sequentially
```

**Sprint Cleanup:**
```bash
/work-issue [45, 67, 89] --continue-on-error
# Processes all even if some fail
```

**Resume After Interruption:**
```bash
/work-issue --resume-batch
# Continues from where it stopped
```

### Performance

**Expected execution time:**
- 3 issues × 35 min/issue = ~105 min total (for medium complexity)
- Actual time varies by issue complexity
- No parallel execution (sequential only for safety)

### Limitations

- **Sequential only** - No parallel processing (maintains clean git state)
- **Auto mode enforced** - Interactive mode not recommended for batch
- **Same repository** - All issues must be from current repository

## Validation Symmetry

**Before implementation:**
```
Phase 1: /start-issue #N → Plan created
Phase 1.5: /eval-plan #N → Validates plan ✅
Checkpoint 1: Human approval
```

**After implementation:**
```
Phase 2: /execute-plan #N → Code created
Phase 2.5: /review → Validates code ✅
Checkpoint 2: Human approval
```

**Note**: Issue number (#N) is passed explicitly to sub-skills to avoid redundant detection overhead.

**Symmetry = Automated validation before human approval in BOTH phases**

## State Management

**State file**: `.claude/.work-issue-state.json`

**Tracks:**
- Current phase and checkpoint
- Phases completed
- Validation results
- Can resume flag

**Lifecycle:**
- Created: When workflow starts
- Updated: After each phase
- Deleted: When workflow completes

## Error Handling

**Plan eval fails:** Fix blocking issues, resume with `/work-issue #23 --resume`

**Code review fails:** Fix issues, re-run `/review`, resume workflow

**Already on branch:** Finish current work or force start with `--force`

## Examples

### Example 1: Default Mode (Auto)

```bash
/work-issue #23

→ All phases automatic...

✅ Issue #23 complete! (35 min total)
- Plan eval: 92/100 (approved)
- Code review: 98/100 (approved)
```

### Example 2: Interactive Mode

```bash
/work-issue #24 --interactive

→ Phase 1: /start-issue... ✅
→ Phase 1.5: /eval-plan... ✅ (Score: 85/100)

📊 Checkpoint 1:
  Issues: Missing error handling task
  [E]dit plan

→ Plan edited, added Task 9: Error handling
→ Phase 2: /execute-plan... ✅ (9/9 tasks)
→ Phase 2.5: /review... ✅ (Score: 95/100)

📊 Checkpoint 2:
  Status: Approved with recommendations
  [C]ontinue

→ Phase 3: /finish-issue... ✅

✅ Issue #24 complete! (52 min total)
```

### Example 3: Stop After Eval

```bash
/work-issue #25 --stop-after=eval

→ Phase 1: /start-issue... ✅
→ Phase 1.5: /eval-plan... ⚠️ (Score: 65/100)

Blocking issues found - plan needs work.
Stopped for manual revision.

Resume: /work-issue #25 --resume
```

### Example 4: Resume After Fix

```bash
# Earlier: stopped at Checkpoint 2 to fix issues
/work-issue #26 --resume

→ Resuming from Phase 3...
→ /finish-issue... ✅

✅ Issue #26 complete!
```

### Example 5: Batch Processing - Daily Issues

```bash
/work-issue [128, 184, 33]

🚀 Batch Processing: 3 issues queued

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #128 (1/3): Update documentation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
→ Phase 1-3 complete...
✅ Issue #128 complete (20 min)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #184 (2/3): Fix login bug
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
→ Phase 1-3 complete...
✅ Issue #184 complete (45 min)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #33 (3/3): Add error handling
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
→ Phase 1-3 complete...
✅ Issue #33 complete (35 min)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Batch Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 3/3 issues completed successfully
Total time: 100 minutes
```

### Example 6: Batch with Failure - Stop on Error

```bash
/work-issue [45, 67, 89] --stop-on-error

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #45 (1/3): Refactor auth
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
→ Phase 1-3 complete...
✅ Issue #45 complete (50 min)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #67 (2/3): Update API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Phase 1: /start-issue... ✅
  Phase 1.5: /eval-plan... ❌ (Score: 65/100)

⚠️ Issue #67 failed at eval-plan
   Error: Plan has blocking issues

Batch stopped (--stop-on-error)
Issues processed: 1/3 ✅, 1/3 ❌, 1/3 ⏸️

Resume with: /work-issue --resume-batch
```

### Example 7: Batch with Failure - Continue on Error

```bash
/work-issue [45, 67, 89] --continue-on-error

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #45 (1/3): Refactor auth
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Issue #45 complete (50 min)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #67 (2/3): Update API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ Issue #67 failed (eval-plan score 65)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #89 (3/3): Add logging
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Issue #89 complete (30 min)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Batch Complete (with failures)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 2/3 issues completed
❌ 1/3 issues failed: #67

Failed issues need manual attention:
- Issue #67: Plan has blocking issues (eval-plan score 65)
```

### Example 8: Resume Batch After Interruption

```bash
# Earlier: Batch interrupted after issue #184
/work-issue --resume-batch

🔄 Resuming batch processing...

Previous results:
✅ Issue #128 completed
✅ Issue #184 completed

Resuming from:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue #33 (3/3): Add error handling
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
→ Phase 1-3 complete...
✅ Issue #33 complete (35 min)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Batch Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 3/3 issues completed successfully
```

## Integration

**Complete workflow:**
```
/work-issue #23
  ├─ /start-issue #23
  ├─ /eval-plan #23        ← Issue number passed explicitly
  ├─ /execute-plan #23
  ├─ /review
  └─ /finish-issue #23
```

**Alternative (manual control):**
```
/start-issue #23
/eval-plan #23            ← Pass issue number to avoid re-detection
/execute-plan #23
/review
/finish-issue #23
```

**Decision tree:**
- Need speed with safety → /work-issue (default auto mode)
- Need manual control → /work-issue --interactive
- Need fine control → individual skills
- Mid-workflow → /work-issue --resume
- **Multiple issues** → /work-issue [128, 184, 33] (batch mode)
- **Batch interrupted** → /work-issue --resume-batch

## Best Practices

1. **Trust the default (auto mode)** - Validation scores are reliable, auto mode provides speed with safety
2. **Use --interactive for learning** - When getting familiar with the workflow
3. **Fix issues when flagged** - If auto mode stops (score ≤ 90), address the recommendations
4. **Resume when interrupted** - Don't restart from beginning
5. **Edit plans when recommended** - Prevents rework during implementation
6. **Pass issue number to sub-skills** - When orchestrating, always pass `#N` to `/start-issue`, `/eval-plan`, `/execute-plan`, and `/finish-issue` to avoid redundant issue detection (4 strategies × 4 skills = significant overhead)

## Performance

| Mode | Simple | Medium | Complex |
|------|--------|--------|---------|
| Interactive | 10 min | 50 min | 140 min |
| Auto | 7 min | 35 min | 100 min |

**Overhead:**
- Plan eval: 60 sec
- Code review: 90 sec
- Checkpoints: 30 sec each (interactive only)

**Savings:**
- Prevents 60+ min rework per architectural issue
- Catches missing requirements early
- Systematic validation reduces errors

## Task Management

**After each phase**, update progress:

```
Phase 1 done → Update Phase 1 task
Phase 1.5 done → Update Phase 1.5 task
Checkpoint 1 passed → Update Checkpoint 1 task
Phase 2 done → Update Phase 2 task
Phase 2.5 done → Update Phase 2.5 task
Checkpoint 2 passed → Update Checkpoint 2 task
Phase 3 done → Mark complete
```

Provides real-time visibility.

## Final Verification

**Before declaring success:**

```
- [ ] All 7 phases completed
- [ ] Both validations passed (/eval-plan, /review)
- [ ] PR merged to main
- [ ] Issue closed on GitHub
- [ ] Branches cleaned up
- [ ] State file deleted
```

## Workflow Skills Requirements

This is a **workflow skill**:

1. **TaskCreate** at start - Progress tracking
2. **TaskUpdate** during execution - Phase completion
3. **Verification checklist** - Final validation

**See**: [WORKFLOW_PATTERNS.md](../WORKFLOW_PATTERNS.md)

## Advanced Topics

For detailed examples, error scenarios, and state management:

**See**: [REFERENCE.md](REFERENCE.md)

## Related Skills

- **/start-issue** - Phase 1 (called by this skill)
- **/eval-plan** - Phase 1.5 (called by this skill)
- **/execute-plan** - Phase 2 (called by this skill)
- **/review** - Phase 2.5 (called by this skill)
- **/finish-issue** - Phase 3 (called by this skill)

## Implementation Notes

### Batch Mode Integration

**Batch detection:**
When the skill is invoked with array/comma/space-separated issue numbers, batch mode is automatically activated:

```python
# Pseudo-code for batch detection in skill orchestration
if detect_batch_mode(arguments):
    # Delegate to batch processor
    exec("python .claude/skills/work-issue/scripts/batch_processor.py", arguments)
else:
    # Execute single-issue workflow
    execute_single_issue_workflow(issue_number)
```

**Delegation to batch_processor.py:**
- Arguments are passed through to Python script
- Script handles parsing, execution, state management
- Each issue in batch executes full single-issue workflow
- Returns aggregate results

**Script location:**
`.claude/skills/work-issue/scripts/batch_processor.py`

**State file:**
`.claude/.work-issue-batch-state.json` (created during batch execution)

---

**Version:** 3.0.0
**Pattern:** Meta-Workflow Orchestrator with Symmetric Validation + Batch Processing
**Compliance:** ADR-001 ✅ | ADR-003 ✅ | WORKFLOW_PATTERNS.md ✅
**Last Updated:** 2026-03-12
**Changelog:**
- v3.0.0: Added batch processing support for multiple issues (Issue #141)
- v2.0.0: Integrated /eval-plan with symmetric validation checkpoints
- v1.0.0: Initial release with 4-skill orchestration
