# Auto-Solve Issue - Usage Examples

> Practical examples and best practices for automated issue resolution

## Overview

This document provides real-world usage examples of `/auto-solve-issue` in different scenarios:

1. **Auto Mode** (score-based checkpoints) - Default behavior
2. **Interactive Mode** (manual checkpoint approval)
3. **Resume Workflow** (continue after interruption)

## Example 1: Auto Mode (Score ≥ 90)

### Scenario

User wants to automatically solve Issue #23 with minimal intervention.

### Command

```bash
/auto-solve-issue #23
# OR explicitly:
/auto-solve-issue #23 --auto
```

### Workflow

```
🚀 Starting auto-solve for issue #23
   Mode: auto

📋 Creating 5-phase task chain...
   ✅ Task 1: Phase 1 - start-issue
   ✅ Task 2: Phase 1.5 - eval-plan (Checkpoint 1)
   ✅ Task 3: Phase 2 - execute-plan
   ✅ Task 4: Phase 2.5 - review (Checkpoint 2)
   ✅ Task 5: Phase 3 - finish-issue

📋 Executing Phase 1: start-issue
   Creating branch: feature/23-fix-authentication
   Generating plan: .claude/plans/active/issue-23-plan.md
   ✅ Phase 1 completed

📋 Executing Phase 1.5: eval-plan
   Validating plan quality...
   ✅ Plan evaluation: 95/100 (approved)

⏸️ Checkpoint 1
   Score: 95/100
   Threshold: 90
   ✅ Score 95 ≥ 90 - auto-continuing

📋 Executing Phase 2: execute-plan
   Implementing tasks from plan...
   ✅ Phase 2 completed

📋 Executing Phase 2.5: review
   Validating code quality...
   ✅ Code review: 92/100 (approved)

⏸️ Checkpoint 2
   Score: 92/100
   Threshold: 90
   ✅ Score 92 ≥ 90 - auto-continuing

📋 Executing Phase 3: finish-issue
   Committing changes...
   Creating pull request...
   Merging to main...
   Closing issue #23...
   ✅ Phase 3 completed

✅ All phases completed!
   Issue #23 resolved
   All phases executed successfully

   Cleaned: .claude/.auto-solve-state.json
   Cleaned: .claude/.eval-plan-status.json
   Cleaned: .claude/.review-status.json
```

### Time

**35-65 minutes** (no manual pauses)

### Key Points

- ✅ Zero manual intervention (scores ≥ 90)
- ✅ All checkpoints passed automatically
- ✅ Complete lifecycle in one command
- ✅ State files cleaned up automatically

---

## Example 2: Interactive Mode

### Scenario

User wants manual control at checkpoints to review plan and code before proceeding.

### Command

```bash
/auto-solve-issue #23 --interactive
```

### Workflow

```
🚀 Starting auto-solve for issue #23
   Mode: interactive

[... Phases 1 and 1.5 execute ...]

⏸️ Checkpoint 1
   Score: 95/100
   Threshold: 90
   ✅ Score 95 ≥ 90

📊 Plan Evaluation Summary:
   Architecture: 40/40
   Coverage: 28/30
   Dependencies: 15/15
   Practices: 9/10
   Clarity: 5/5

   Issues: 0 blocking, 2 recommendations

   Top Recommendations:
   1. Add error handling for network failures
   2. Include performance test for large datasets

? Continue to next phase?
  [1] Continue - Proceed to implementation
  [2] Stop - Pause to address recommendations

User selects: [1]

✅ Continuing to Phase 2...

[... Phase 2 executes ...]

⏸️ Checkpoint 2
   Score: 82/100
   Threshold: 90
   ⚠️ Score 82 < 90

📊 Code Review Summary:
   Quality: 85/100
   Architecture: 90/100
   Security: 80/100
   Performance: 75/100

   Issues: 0 blocking, 3 recommendations

   Top Issues:
   1. N+1 query in userLoader.ts:23
   2. Missing input validation in auth.ts:45
   3. No error handling for API calls

? Continue to next phase?
  [1] Continue - Merge despite issues
  [2] Stop - Fix issues first

User selects: [2]

💾 Resume point saved:
   State file: .claude/.auto-solve-state.json
   Stopped at: Phase 2.5
   Reason: user_stopped

   Resume with: /auto-solve-issue #23 --resume
```

### Time

**40-70 minutes** + review time (~5-10 min per checkpoint)

### Key Points

- ✅ Manual approval at both checkpoints
- ✅ User sees detailed evaluation results
- ✅ Can stop to fix issues before merging
- ✅ Resume capability preserved

---

## Example 3: Resume from Checkpoint

### Scenario

User stopped at Checkpoint 2 to fix code issues, now wants to resume.

### Before Resume

```bash
# User fixes issues manually
git add src/auth.ts src/userLoader.ts
git commit -m "fix: add error handling and optimize queries"

# User re-runs review to verify fixes
/review
# Output: Score: 93/100 ✅
```

### Command

```bash
/auto-solve-issue #23 --resume
```

### Workflow

```
💾 Resume point found:
   Saved at: 2026-03-30T10:45:00Z
   Stopped at: Phase 2.5
   Reason: user_stopped

🔄 Resuming workflow...
   Issue: #23
   Mode: interactive
   Reset task task_140 to pending
   Continuing execution loop...

📋 Executing Phase 2.5: review (retry)
   Validating code quality...
   ✅ Code review: 93/100 (approved)

⏸️ Checkpoint 2
   Score: 93/100
   Threshold: 90
   ✅ Score 93 ≥ 90 - auto-continuing

📋 Executing Phase 3: finish-issue
   [... completes successfully ...]

🎉 Issue lifecycle complete!
```

### Time

**Depends on checkpoint location** (in this case ~5 minutes to finish)

### Key Points

- ✅ Seamless resume from exact stopping point
- ✅ State preserved (task IDs, mode, issue number)
- ✅ Re-runs stopped phase (in case fixes changed score)
- ✅ Continues normally after checkpoint passes

---

## Example 4: Checkpoint Failed (Auto Mode)

### Scenario

Plan quality is too low (score < 90), auto mode stops immediately.

### Command

```bash
/auto-solve-issue #23 --auto
```

### Workflow

```
[... Phase 1 executes ...]

📋 Executing Phase 1.5: eval-plan
   Validating plan quality...
   ⚠️ Plan evaluation: 75/100 (needs_improvement)

⏸️ Checkpoint 1
   Score: 75/100
   Threshold: 90

⚠️ Score 75 < 90

⏸️ Stopping at Checkpoint 1
   Score 75/100 is below threshold 90
   Fix issues and resume: /auto-solve-issue #23 --resume

📊 Issues Found:
   Blocking: 2
   Recommendations: 5

   Critical Issues:
   1. Task 5: Architecture violation (UI logic in service layer)
   2. Missing acceptance criteria coverage (only 60%)

💾 Resume point saved:
   State file: .claude/.auto-solve-state.json
   Stopped at: Phase 1.5
   Reason: score_below_threshold
```

### Fix and Resume

```bash
# User edits plan to fix issues
vim .claude/plans/active/issue-23-plan.md

# User re-runs eval-plan
/eval-plan #23
# Output: Score: 95/100 ✅

# Resume workflow
/auto-solve-issue #23 --resume
# ✅ Continues from Phase 2
```

### Key Points

- ❌ Auto mode enforces quality gates strictly
- ✅ Clear feedback on what's wrong
- ✅ Can fix and resume without starting over
- ✅ Ensures high-quality plans before implementation

---

## Best Practices

### 1. Use for Well-Defined Issues

**Good candidates:**
- Clear acceptance criteria
- Well-understood scope
- No ambiguous requirements
- Estimated 2-8 hours of work

**Poor candidates:**
- Vague issue descriptions
- Scope creep likely
- Requires discovery/research
- Multiple unknown dependencies

### 2. Trust the Scores

**Checkpoint thresholds (≥ 90) are carefully calibrated:**
- eval-plan: 90/100 → Plan is solid, ready to implement
- review: 90/100 → Code quality acceptable for production

**Don't override without understanding why score is low.**

### 3. Have a Fallback

If auto-solve-issue encounters issues:
- Use `/work-issue #23` (stable alternative)
- Manual phase execution: `/start-issue` → `/execute-plan` → `/finish-issue`
- Resume capability minimizes lost work

### 4. Monitor First Run

**For new projects/teams:**
- Use `--interactive` first to build confidence
- Review checkpoint results carefully
- Understand evaluation criteria
- Switch to `--auto` once comfortable

### 5. Provide Feedback

Report issues to improve the skill:
- Unexpected stops
- Incorrect checkpoint scores
- Resume failures
- Performance problems

## Performance Comparison

| Scenario | Manual | work-issue | auto-solve-issue |
|----------|--------|------------|------------------|
| **Simple issue (2-3 hours)** | 15-20 min overhead | 10-15 min overhead | 5-10 min overhead |
| **Complex issue (6-8 hours)** | 30-40 min overhead | 20-25 min overhead | 10-15 min overhead |
| **User pauses** | Variable | After each phase (5x) | Only at checkpoints (2x) |
| **Context switching** | High | Medium | Low |
| **Cognitive load** | High (track state manually) | Medium (phases visible) | Low (fully automated) |

**Overhead = Time spent on workflow coordination (not coding)**

---

**See also:**
- [PHASES.md](./PHASES.md) - Detailed workflow steps
- [CHECKPOINTS.md](./CHECKPOINTS.md) - Checkpoint system
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Error scenarios
