---
name: finish-issue
description: |
  Complete issue workflow - commit, PR, merge, close, cleanup.
  Automates the entire issue completion lifecycle with quality gates.
disable-model-invocation: true
user-invocable: true
argument-hint: "[issue-number] [--keep-branch] [--no-pr] [--force]"
allowed-tools: Bash(git *), Bash(gh *), Read
context: fork
agent: general-purpose
---

# Issue Finisher

Complete the entire workflow for closing an issue with automated quality gates and safety checks.

## Task

Finish issue workflow in 6 automated steps:
1. **Pre-Finish Validation** - Quality gates (linting, tests, review status)
2. **Commit & Push** - Commit changes and push to remote
3. **Create PR** - Generate pull request with context
4. **Merge PR** - Merge after checks pass
5. **Close Issue** - Mark issue as done on GitHub
6. **Cleanup** - Delete branches and review status

## Live Status Checks

### Current State
- **Branch**: !`git rev-parse --abbrev-ref HEAD`
- **Issue Number**: !`git rev-parse --abbrev-ref HEAD | grep -oE '[0-9]+' | head -1 || echo "none"`
- **Uncommitted Changes**: !`git status --short | wc -l | tr -d ' '` files
- **Branch Ahead**: !`git rev-list --count @{u}..HEAD 2>/dev/null || echo "not pushed"`

### Quality Status
- **Tests**: !`if [ -f package.json ]; then npm test &>/dev/null && echo "✅ Passing" || echo "⚠️ Failing"; else echo "No tests"; fi`
- **Main Sync**: !`git fetch origin &>/dev/null && git merge-base --is-ancestor origin/main HEAD && echo "✅ Synced" || echo "⚠️ Need sync"`

## Commands

**Basic usage**:
```bash
/finish-issue              # Complete current issue (infer from branch)
/finish-issue #23          # Complete specific issue
```

**With options**:
```bash
/finish-issue --keep-branch    # Keep branch after merge
/finish-issue --no-pr          # Close issue without PR
/finish-issue --force          # Skip validation (use with caution)
```

Arguments:
- `[issue-number]` - Optional, inferred from branch name if omitted
- `--keep-branch` - Don't delete branches after merge
- `--no-pr` - Close issue without creating PR
- `--force` - Skip all pre-finish validation checks

## Workflow

Execute: `bash scripts/finish-issue.sh $ARGUMENTS`

### Step 1: Create Todo List

**Initialize progress tracking** using TaskCreate for all workflow steps:

```
Task #1: Pre-finish validation (quality gates)
Task #2: Commit and push changes (blocked by #1)
Task #3: Create pull request (blocked by #2)
Task #4: Merge PR to main (blocked by #3)
Task #5: Close GitHub issue (blocked by #4)
Task #6: Cleanup branches (blocked by #5)
```

After creating tasks, proceed with workflow execution.

### Step 2: Pre-Finish Validation ⭐

**Automated Checks**:
```bash
# Run linting and tests
npm run lint  # Must pass
npm test      # Must pass
```

**Review Status Check**:
```bash
# Check if /review was run recently
if [ -f .claude/.review-status.json ]; then
  REVIEW_STATUS=$(jq -r '.status' .claude/.review-status.json)
  REVIEW_TIME=$(jq -r '.timestamp' .claude/.review-status.json)
  VALID_UNTIL=$(jq -r '.valid_until' .claude/.review-status.json)

  # Check if review expired (90 minutes)
  if [[ "$CURRENT_TIME" > "$VALID_UNTIL" ]]; then
    ⚠️  Previous review expired
    ℹ️  Recommended: Run /review again
    ❓ Proceed anyway? (Y/n)
  else
    ✅ Code review completed
    - Status: $REVIEW_STATUS
    - Score: $REVIEW_SCORE/100

    if [ "$REVIEW_STATUS" = "issues_found" ]; then
      ❌ Blocking issues detected - cannot proceed
      exit 1
    fi
  fi
else
  ℹ️  Recommended: Run /review for quality check
  ❓ Proceed without review? (Y/n)
fi
```

**Acceptance Criteria**:
```bash
# Extract from issue body
gh issue view #23 --json body --jq .body | grep -A 20 "Acceptance Criteria"

❓ All acceptance criteria met? (Y/n)
```

**Documentation Check**:
```bash
ℹ️  Documentation updated if needed? (README, ADRs, API docs)
❓ Confirm (Y/n)
```

**Skip validation**: Use `--force` flag

### Step 1: Commit & Push
```bash
git add .
git commit -m "$(cat <<EOF
feat: implement Issue #23

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
git push -u origin <branch>
```

### Step 2: Create PR
```bash
gh pr create \
  --title "feat: implement Issue #23" \
  --body "<generated-pr-body>" \
  --base main
```

### Step 3: Merge PR
```bash
# Wait for checks or auto-merge
gh pr merge --squash --delete-branch
```

### Step 4: Close Issue
```bash
gh issue close #23 --comment "✅ Completed in PR #<pr-number>"
```

### Step 5: Cleanup
```bash
git checkout main
git pull origin main
git branch -d <feature-branch>
git push origin --delete <branch>

# Remove review status file
rm -f .claude/.review-status.json
```

### Execution Time
```
Pre-Finish Validation: 1 min
Commit & Push: 30 sec
Create PR: 20 sec
Merge PR: 30 sec (with auto-merge)
Close Issue: 10 sec
Cleanup: 10 sec

Total: ~3-4 minutes
Manual equivalent: ~15-20 minutes
```

## Examples

### Example 1: Standard Completion

```bash
# On branch: feature/23-task-list
# All work done, tests passing

/finish-issue

# Output:
# ━━━ Pre-Finish Validation ━━━
# ✅ Linting passes
# ✅ Tests passing (24 passed)
# ✅ Code review completed (Score: 92/100)
# ✅ Acceptance criteria confirmed
# ✅ Documentation confirmed
#
# ━━━ Step 1: Commit & Push ━━━
# ✅ Committed 3 files
# ✅ Pushed to origin/feature/23-task-list
#
# ━━━ Step 2: Create PR ━━━
# ✅ Created PR #45: "feat: implement Issue #23"
#
# ━━━ Step 3: Merge PR ━━━
# ✅ PR #45 merged (squash)
#
# ━━━ Step 4: Close Issue ━━━
# ✅ Closed Issue #23
#
# ━━━ Step 5: Cleanup ━━━
# ✅ Deleted branches
# ✅ Back on main branch
#
# 🎉 Issue #23 completed!
```

### Example 2: Skip Validation

```bash
# Quick finish without validation checks
/finish-issue --force

# Skips:
# - Linting/test checks
# - Review status check
# - Acceptance criteria confirmation
# - Documentation confirmation
#
# Use when: Urgent hotfix, documentation-only changes
```

### Example 3: Keep Branch for Reference

```bash
# Keep branch after merge
/finish-issue --keep-branch

# Same flow but skips branch deletion
# Useful for: Reference, backporting, experiments
```

## Integration

### Paired with /start-issue

```bash
# Complete workflow
/start-issue #23    # Start (30 sec)
# ... implement ...
/review             # Quality check (2 min)
/finish-issue #23   # Finish (3 min)

# Total managed: ~6 minutes
# Total manual: ~25-30 minutes
```

### Review Integration

```bash
# Recommended workflow
/review              # Run code review first
/finish-issue        # Checks review status automatically

# Review status tracked in .claude/.review-status.json
# Valid for 90 minutes after review completion
```

### Workflow Chain

```
/start-issue → Implementation → /review → /finish-issue
    ↓              ↓               ↓           ↓
  Branch         Code           Quality     Complete
  + Plan         Changes        Check       & Close
```

## Safety Features

**Pre-flight Checks**:
- ✅ All changes committed
- ✅ Branch synced with main
- ✅ Issue exists and is open
- ✅ Automated tests passing
- ✅ Review status checked

**Quality Gates**:
- ✅ Linting passes
- ✅ Tests passing
- ✅ Code review (recommended)
- ✅ Acceptance criteria met
- ✅ Documentation updated

**Rollback Protection**:
- Creates backup before deletion
- Can restore: `git checkout -b <branch> backup/<branch>`
- Backup cleanup: 7 days (automated)

## Error Handling

### Tests Failing
```
❌ Error: Tests failing

Failed: 2 tests in src/components/TaskList.test.tsx

Options:
1. Fix tests and retry
2. Skip with --force (not recommended)
3. Cancel (Ctrl+C)
```

### Review Status Issues
```
⚠️ Warning: Review status expired

Last review: 2 hours ago (90 min limit)

Recommended: Run /review again
Or proceed with: /finish-issue --force
```

### Already on Main Branch
```
⚠️ Error: Not on a feature branch

Current: main
Expected: feature/* or fix/*

Options:
1. Specify issue: /finish-issue #23
2. Checkout branch: git checkout feature/23-*
```

### PR Already Exists
```
ℹ️ PR #45 already exists

Status: Open, passing checks

Will merge existing PR and continue.
```

## Commit Message Format

Follows conventional commits:
```
feat: implement Issue #23 - Task list component

- Add TaskList component with drag-drop
- Implement completion flow
- Add comprehensive tests

Closes #23

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

## Advanced Options

### Dry Run
```bash
# Preview actions without executing
/finish-issue --dry-run

# Shows what would happen
```

### Custom Commit Message
```bash
# Override default message
/finish-issue --message "feat: complete task list

Added drag-drop and real-time sync"
```

### Skip Specific Steps
```bash
/finish-issue --no-commit   # Already committed
/finish-issue --no-push     # Testing locally
/finish-issue --no-pr       # Direct merge (dangerous)
```

## Task Management

**After each step completion**, update task status:

```
Use TaskUpdate to mark task as completed:
- Step 2 done → Update Task #1
- Step 3 done → Update Task #2
- Step 4 done → Update Task #3
- Step 5 done → Update Task #4
- Step 6 done → Update Task #5
- Step 7 done → Update Task #6
```

This provides real-time progress visibility in Claude Code UI.

## Final Verification

**Before declaring success**, verify all critical items:

```
Quick checklist:
- [ ] All 6 tasks completed
- [ ] PR merged to main
- [ ] Issue closed on GitHub
- [ ] Branches deleted (unless --keep-branch)
- [ ] Review status cleaned up
- [ ] No errors during workflow
```

If any item fails, troubleshoot and retry before completion.

---

**Related**:
- [start-issue](../start-issue/SKILL.md) - Start issue workflow
- [review](../review/SKILL.md) - Code quality review
- [sync](../sync/SKILL.md) - Sync with main branch

**Version**: 2.1.0
**Status**: ADR-001 Section 4 Compliant
**Last Updated**: 2026-03-05
