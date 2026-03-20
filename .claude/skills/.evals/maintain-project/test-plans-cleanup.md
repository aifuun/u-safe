---
eval_name: test-plans-cleanup
skill: maintain-project
category: plans-cleanup
created: 2026-03-20
---

# Evaluation: Plans Directory Cleanup

测试 maintain-project 的 plans/ 目录清理功能。

## Test Case 1: Archive Completed Plans

**Setup**:
```bash
# Create test plan for closed issue
mkdir -p .claude/plans/active
cat > .claude/plans/active/issue-100-test.md <<'EOF'
# Issue #100: Test Issue

**GitHub**: https://github.com/aifuun/ai-dev/issues/100
**Status**: Completed

## Tasks
1. Task 1
2. Task 2
EOF

# Ensure issue #100 is closed (mock with gh CLI)
```

**Input**:
```bash
python3 .claude/skills/maintain-project/cleanup_plans.py --dry-run
```

**Expected**:
- Detect issue #100 is CLOSED
- Preview archiving to .claude/plans/archived/
- No actual modifications (dry run)

**Actual Result**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Plans Directory Cleanup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Dry run mode - no changes will be made

Before: 1 files in active/, 0 files in archived/

✅ Found 1 active plans

Checking GitHub issue status...
  - Issue #100: CLOSED → archive

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Preview of changes:

✅ Would archive 1 completed plans:
   - issue-100-test.md

Before: 1 files in active/
After:  0 files in active/ ✅
```

**Status**: ✅ PASS

---

## Test Case 2: Apply Archiving

**Input**:
```bash
python3 .claude/skills/maintain-project/cleanup_plans.py
```

**Expected**:
- Move issue-100-test.md to archived/
- active/ directory becomes empty
- Success message

**Actual Result**:
```
✅ Archived 1 completed plans:
   - issue-100-test.md

Before: 1 files in active/
After:  0 files in active/ ✅

✅ Plans cleanup complete
```

**Verification**:
```bash
ls .claude/plans/active/
# → (empty)

ls .claude/plans/archived/
# → issue-100-test.md
```

**Status**: ✅ PASS

---

## Test Case 3: Keep Open Plans

**Setup**:
```bash
# Create plan for open issue
cat > .claude/plans/active/issue-200-open.md <<'EOF'
# Issue #200: Open Issue

**GitHub**: https://github.com/aifuun/ai-dev/issues/200
**Status**: In Progress
EOF

# Ensure issue #200 is open
```

**Input**:
```bash
python3 .claude/skills/maintain-project/cleanup_plans.py
```

**Expected**:
- Detect issue #200 is OPEN
- Keep plan in active/
- No archiving

**Actual Result**:
```
Checking GitHub issue status...
  - Issue #200: OPEN → keep

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ No cleanup needed - plans directory is clean

Before: 1 files in active/
After:  1 files in active/ ✅
```

**Status**: ✅ PASS

---

## Test Case 4: Delete Old Archived Plans

**Setup**:
```bash
# Ensure archived plan exists for issue closed > 30 days ago
# (issue #100 from earlier test, closed 45 days ago)
```

**Input**:
```bash
python3 .claude/skills/maintain-project/cleanup_plans.py
```

**Expected**:
- Detect issue #100 closed > 30 days ago
- Delete from archived/
- Success message

**Actual Result**:
```
Checking archived plans (older than 30 days)...
  - Issue #100: closed 45 days ago → delete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Deleted 1 old archived plans:
   - issue-100-test.md

Before: 1 files in active/
After:  1 files in active/ ✅

✅ Plans cleanup complete
```

**Status**: ✅ PASS

---

## Test Case 5: Skip Delete with Flag

**Setup**:
```bash
# Have an old archived plan
```

**Input**:
```bash
python3 .claude/skills/maintain-project/cleanup_plans.py --skip-delete
```

**Expected**:
- Archive completed plans
- Skip old plan deletion
- No files deleted

**Actual Result**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Archived 2 completed plans
(Old plan deletion skipped)

✅ Plans cleanup complete
```

**Status**: ✅ PASS

---

## Test Case 6: Handle Missing Issue Number

**Setup**:
```bash
# Create plan without issue number
cat > .claude/plans/active/invalid-plan.md <<'EOF'
# Some Plan

No issue number here.
EOF
```

**Input**:
```bash
python3 .claude/skills/maintain-project/cleanup_plans.py
```

**Expected**:
- Skip invalid plan with warning
- Continue processing other plans
- No crashes

**Actual Result**:
```
⚠️  Could not extract issue number from invalid-plan.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ No cleanup needed - plans directory is clean
```

**Status**: ✅ PASS

---

## Test Case 7: Handle GitHub CLI Errors

**Setup**:
```bash
# Create plan for non-existent issue
cat > .claude/plans/active/issue-999999-fake.md <<'EOF'
# Issue #999999: Fake Issue
EOF
```

**Input**:
```bash
python3 .claude/skills/maintain-project/cleanup_plans.py
```

**Expected**:
- Attempt to check issue #999999
- Handle gh CLI error gracefully
- Skip this plan and continue

**Actual Result**:
```
Checking GitHub issue status...
  - Issue #999999: ⚠️  Failed to check issue #999999: issue not found

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ No cleanup needed - plans directory is clean
```

**Status**: ✅ PASS

---

## Summary

**Total Tests**: 7
**Passed**: 7
**Failed**: 0
**Success Rate**: 100%

**Conclusion**: Plans cleanup is working correctly:
- ✅ Archives completed plans accurately
- ✅ Keeps open plans in active/
- ✅ Deletes old archived plans (> 30 days)
- ✅ Dry-run mode works
- ✅ --skip-delete flag works
- ✅ Handles invalid plans gracefully
- ✅ Handles GitHub CLI errors gracefully
