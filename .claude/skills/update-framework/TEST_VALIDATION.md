# Update Framework - Test Validation Checklist

**Issue**: #154 - Fix update-framework to follow Workflow Skills pattern
**Created**: 2026-03-12

## Test Scenarios

### Test 1: Verify 7 Tasks Created

**Command**:
```bash
cd ~/dev/ai-dev
/update-framework ../u-safe
```

**Expected Behavior**:
- Creates exactly 7 subtasks using TaskCreate
- Task names match AI Execution Instructions:
  1. "Detect tech stack profile"
  2. "Validate source and target paths"
  3. "Sync Pillars via update-pillars"
  4. "Sync Rules via update-rules"
  5. "Sync Workflow via update-workflow"
  6. "Sync Skills via update-skills"
  7. "Report comprehensive summary"

**Verification**:
```bash
# Check Claude Code UI shows 7 tasks
# OR count tasks in task list output
```

**Pass Criteria**: ✅ 7 tasks visible, not 1 top-level task

---

### Test 2: Verify Sub-Skills Called

**Command**:
```bash
cd ~/dev/ai-dev
/update-framework ../u-safe --dry-run
```

**Expected Behavior**:
- Calls `Skill("update-pillars", args="...")` NOT direct rsync
- Calls `Skill("update-rules", args="...")` NOT direct rsync
- Calls `Skill("update-workflow", args="...")` NOT direct rsync
- Calls `Skill("update-skills", args="...")` NOT direct rsync

**Verification**:
```bash
# Check execution log shows:
# "Launching skill: update-pillars"
# "Launching skill: update-rules"
# "Launching skill: update-workflow"
# "Launching skill: update-skills"

# Should NOT see:
# "rsync -av .claude/pillars/pillars/"
```

**Pass Criteria**: ✅ 4 sub-skills invoked, no direct rsync

---

### Test 3: Verify Task Status Updates

**Command**:
```bash
cd ~/dev/ai-dev
/update-framework ../u-safe
```

**Expected Behavior**:
- Each task status changes: pending → in_progress → completed
- Real-time updates visible in Claude Code UI
- activeForm shows current operation (e.g., "Syncing Pillars...")

**Verification**:
- Watch task list during execution
- Verify each task shows "in_progress" then "completed"

**Pass Criteria**: ✅ All 7 tasks transition through statuses correctly

---

### Test 4: Verify Filtering Works

**Command**:
```bash
cd ~/dev/ai-dev
/update-framework ../u-safe
```

**Given**: u-safe has profile "tauri-react" (excludes backend/**)

**Expected Behavior**:
- Backend rules NOT copied to ../u-safe/.claude/rules/
- Only categories from profile synced: core, architecture, languages, frontend, desktop
- No manual `rm -rf ../u-safe/.claude/rules/backend` needed

**Verification**:
```bash
# After sync completes
ls ../u-safe/.claude/rules/backend 2>/dev/null && echo "FAIL: backend exists" || echo "PASS: backend excluded"
```

**Pass Criteria**: ✅ Backend rules not present (filtered by sub-skill)

---

### Test 5: Verify Pillar Sync

**Command**:
```bash
cd ~/dev/ai-dev
/update-framework ../u-safe
```

**Given**: u-safe profile specifies pillars: A, B, K, L

**Expected Behavior**:
- Pillars A, B, K, L synced to ../u-safe/.prot/pillars/
- Directory structure preserved (q1-data-integrity/pillar-a/, etc.)
- No "Pillar A not found" errors

**Verification**:
```bash
# Check Pillar directories exist
ls ../u-safe/.prot/pillars/q1-data-integrity/pillar-a/
ls ../u-safe/.prot/pillars/q1-data-integrity/pillar-b/
ls ../u-safe/.prot/pillars/q2-flow-concurrency/pillar-k/
ls ../u-safe/.prot/pillars/q3-structure-boundaries/pillar-l/
```

**Pass Criteria**: ✅ All 4 Pillar directories exist, no errors

---

### Test 6: Verify Resume Capability

**Command**:
```bash
cd ~/dev/ai-dev
/update-framework ../u-safe
# Interrupt during execution (Ctrl+C during Task 3)
/update-framework ../u-safe --resume
```

**Expected Behavior**:
- Detects incomplete execution
- Resumes from last completed task
- Skips already-completed tasks (Tasks 1-2)
- Continues from Task 3 onward

**Verification**:
- Check that Tasks 1-2 not re-executed
- Task 3 starts immediately

**Pass Criteria**: ✅ Resume works, no duplicate execution

---

## Compliance Checklist

After running all 6 tests, verify compliance:

- [ ] Creates 7 subtasks at start of execution (Test 1)
- [ ] Updates each task status (pending → in_progress → completed) (Test 3)
- [ ] Calls 4 sub-skills using Skill() tool (not direct rsync) (Test 2)
- [ ] Sub-skills receive profile filters as arguments (Test 2, 4)
- [ ] No manual rsync or cleanup code executed (Test 2, 4)
- [ ] Complies with WORKFLOW_PATTERNS.md requirements (Test 1, 3)
- [ ] Progress visible to user in real-time (Test 3)
- [ ] Test with `/update-framework ../u-safe` shows all 7 tasks (Test 1)

**Overall Pass Criteria**: All 8 compliance items ✅

---

## Test Execution Log

**Date**: _________
**Tester**: _________

### Test Results

| Test | Status | Notes |
|------|--------|-------|
| Test 1: 7 Tasks Created | ⬜ Pass / ⬜ Fail | |
| Test 2: Sub-Skills Called | ⬜ Pass / ⬜ Fail | |
| Test 3: Task Status Updates | ⬜ Pass / ⬜ Fail | |
| Test 4: Filtering Works | ⬜ Pass / ⬜ Fail | |
| Test 5: Pillar Sync | ⬜ Pass / ⬜ Fail | |
| Test 6: Resume Capability | ⬜ Pass / ⬜ Fail | |

### Issues Found

_Document any failures or unexpected behavior here_

---

**Note**: These tests should be run AFTER merging issue #154 to main branch and before releasing the updated skill.
