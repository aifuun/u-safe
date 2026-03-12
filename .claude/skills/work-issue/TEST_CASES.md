# /work-issue Workflow - Test Case Library

**Created**: 2026-03-11
**Purpose**: Reusable test cases for regression testing
**Issue**: #122 - Phase 3 validation
**Version**: work-issue v2.0.0+

---

## How to Use This Library

1. **Select test case** based on scenario (simple/medium/complex/error/resume)
2. **Follow steps** exactly as documented
3. **Validate results** using provided checklist
4. **Document outcomes** for comparison with baseline
5. **Report issues** if behavior differs from expected

---

## Test Case 1: Simple Issue Workflow (Auto Mode)

**Scenario**: Straightforward 3-5 task issue with high-quality plan
**Mode**: `--auto`
**Expected Behavior**: Completes all 7 phases automatically without human intervention
**Duration**: 7-10 minutes

### Steps

1. **Create test issue** (or use existing simple issue):
   ```bash
   gh issue create --title "Add unit tests for utility functions" \
     --label "test,P2" \
     --body "## Tasks
   - Add tests for string helpers
   - Add tests for date helpers
   - Update test documentation

   ## Acceptance Criteria
   - 80%+ test coverage
   - All tests passing
   - Docs updated"
   ```

2. **Run workflow**:
   ```bash
   /work-issue #<N> --auto
   ```

3. **Observe automatic progression**:
   - Phase 1: Branch + plan created (30 sec)
   - Phase 1.5: Plan evaluated automatically
   - Checkpoint 1: SKIPPED (score > 90)
   - Phase 2: Tasks executed (5-7 min)
   - Phase 2.5: Code reviewed automatically
   - Checkpoint 2: SKIPPED (score > 90)
   - Phase 3: PR merged, issue closed (2 min)

### Validation

- [ ] All 7 phases completed without stopping
- [ ] Both checkpoints skipped (scores > 90)
- [ ] Worktree created with correct naming
- [ ] Plan file generated in worktree
- [ ] All tasks marked completed
- [ ] Status files created then cleaned up
- [ ] PR merged to main
- [ ] Issue closed on GitHub
- [ ] Worktree removed after finish
- [ ] Total time: 7-10 minutes

### Expected Output

```
✅ Issue #<N> complete! (8 min total)
- Plan eval: 95/100 (approved)
- Code review: 98/100 (approved)
```

---

## Test Case 2: Medium Complexity (Interactive Mode)

**Scenario**: 8-12 task issue requiring human checkpoints
**Mode**: Interactive (default)
**Expected Behavior**: Stops at Checkpoint 1 and Checkpoint 2 for review
**Duration**: 50-60 minutes

### Steps

1. **Create test issue** with moderate complexity:
   ```bash
   gh issue create --title "Refactor authentication system" \
     --label "refactor,P1" \
     --body "## Tasks
   - Review current auth implementation
   - Extract auth logic to service layer
   - Add schema validation with Airlock
   - Implement error handling
   - Add unit tests for auth service
   - Add integration tests
   - Update documentation
   - Review security implications

   ## Acceptance Criteria
   - Auth logic in service layer (not UI)
   - Schema validation at boundaries
   - 90%+ test coverage
   - Security review passed"
   ```

2. **Run workflow** (interactive mode):
   ```bash
   /work-issue #<N>
   ```

3. **At Checkpoint 1** (after eval-plan):
   - Review plan evaluation (score ~85/100)
   - Note recommendations (e.g., "Add error handling task")
   - Choose: **[E]dit plan**
   - Add missing task
   - Re-evaluate plan (score improves to 92/100)
   - Choose: **[C]ontinue**

4. **During Phase 2**:
   - Watch task-by-task execution
   - Verify worktree path used correctly
   - Observe progress tracking

5. **At Checkpoint 2** (after review):
   - Review code quality (score ~88/100)
   - Note recommendations (e.g., "Add rate limiting")
   - Choose: **[C]ontinue** (recommendations non-blocking)

6. **Phase 3 completion**:
   - PR created and merged
   - Issue closed
   - Cleanup performed

### Validation

- [ ] Checkpoint 1 stopped for human review
- [ ] Plan evaluation showed recommendations
- [ ] Edit plan workflow worked correctly
- [ ] Re-evaluation showed improved score
- [ ] Phase 2 executed all 9 tasks (8 original + 1 added)
- [ ] Checkpoint 2 stopped for human review
- [ ] Code review identified minor improvements
- [ ] Able to continue despite recommendations
- [ ] All files modified in worktree (not main repo)
- [ ] Total time: 50-60 minutes

### Expected Output

```
📊 Checkpoint 1:
  Issues: Missing error handling task
  [E]dit plan

→ Plan edited, added Task 9: Error handling
→ Phase 2: /execute-plan... ✅ (9/9 tasks)

📊 Checkpoint 2:
  Status: Approved with recommendations
  [C]ontinue

✅ Issue #<N> complete! (52 min total)
```

---

## Test Case 3: Complex Issue (Step-by-Step)

**Scenario**: Large 15+ task issue with dependencies
**Mode**: Interactive with careful review
**Expected Behavior**: All tasks tracked, dependencies enforced, thorough review
**Duration**: 2-3 hours

### Steps

1. **Create complex test issue**:
   ```bash
   gh issue create --title "Implement complete user management system" \
     --label "feature,P0" \
     --body "## Tasks
   - Design user schema (Pillar A - nominal types)
   - Create user repository layer
   - Implement user service layer
   - Add schema validation (Pillar B - Airlock)
   - Add authentication middleware
   - Implement authorization checks
   - Create user API endpoints
   - Add unit tests for repository
   - Add unit tests for service
   - Add unit tests for API
   - Add integration tests
   - Implement error handling
   - Add logging (Pillar R)
   - Update API documentation
   - Security review checklist
   - Performance testing

   ## Acceptance Criteria
   - Clean architecture (UI → Service → Repository)
   - Branded types for UserId
   - Schema validation at boundaries
   - 95%+ test coverage
   - Security review passed
   - Performance acceptable (< 100ms per request)"
   ```

2. **Run workflow**:
   ```bash
   /work-issue #<N>
   ```

3. **Monitor all 7 phases**:
   - Phase 1: Note 16 tasks in plan
   - Phase 1.5: Review eval score (expect ~92/100)
   - Checkpoint 1: Review, approve plan
   - Phase 2: Execute 16 tasks one by one (2 hours)
   - Phase 2.5: Review generated code
   - Checkpoint 2: Review quality score
   - Phase 3: Merge and close

4. **Verify task dependencies**:
   - Repository layer before service layer
   - Service layer before API endpoints
   - Implementation before tests
   - Tests before documentation

### Validation

- [ ] All 16 tasks created as todos
- [ ] Tasks executed in correct dependency order
- [ ] Repository → Service → API layer separation maintained
- [ ] Tests added after implementation (not before)
- [ ] Documentation updated last
- [ ] Plan score high (90+)
- [ ] Code review score high (90+)
- [ ] All acceptance criteria met
- [ ] Total time: 2-3 hours

### Expected Output

```
→ Phase 2: /execute-plan... ✅ (16/16 tasks)
→ Phase 2.5: /review... ✅ (Score: 96/100)

✅ Issue #<N> complete! (140 min total)
- Plan eval: 92/100 (approved)
- Code review: 96/100 (approved)
```

---

## Test Case 4: Low Plan Score (< 90)

**Scenario**: Plan with architecture violations or missing requirements
**Mode**: `--auto` (should stop at checkpoint despite auto mode)
**Expected Behavior**: Checkpoint 1 forces stop, requires human decision
**Duration**: Variable (depends on plan fixes)

### Steps

1. **Create issue with intentionally poor plan**:
   ```bash
   gh issue create --title "Add user profile page" \
     --label "feature" \
     --body "## Tasks
   - Add profile component
   - Fetch user data
   - Display user info

   ## Acceptance Criteria
   - Profile page shows user data"
   ```

   (This plan will score low because:
   - No error handling
   - No tests mentioned
   - Vague tasks
   - Missing architecture guidance
   - Incomplete acceptance criteria)

2. **Run workflow in auto mode**:
   ```bash
   /work-issue #<N> --auto
   ```

3. **Observe Checkpoint 1 behavior**:
   - Eval-plan runs automatically
   - Score comes back ~75/100
   - **Checkpoint 1 STOPS** (even in auto mode)
   - Shows recommendations:
     - Missing: Error handling task
     - Task 1: Too vague ("Add profile component")
     - Architecture: No layer separation specified
     - Tests: Not mentioned

4. **Make decision**:
   ```
   [C]ontinue anyway - proceed to implementation
   [E]dit plan - fix issues and re-evaluate
   [S]top here - pause workflow
   [Q]uit - cancel workflow
   ```

5. **Choose [E]dit plan**:
   - Edit plan file manually
   - Add error handling task
   - Clarify architecture (service → component)
   - Add test tasks
   - Expand acceptance criteria

6. **Re-evaluate**:
   - Score improves to 92/100
   - Checkpoint 1 approves automatically
   - Continue to Phase 2

### Validation

- [ ] Auto mode correctly stopped at Checkpoint 1
- [ ] Score < 90 triggered the stop
- [ ] Recommendations were clear and actionable
- [ ] Edit plan workflow worked
- [ ] Re-evaluation showed improved score
- [ ] Workflow continued after fixes
- [ ] Safety net prevented poor implementation

### Expected Output

```
→ Phase 1.5: /eval-plan... ⚠️ (Score: 75/100)

📊 Checkpoint 1 (AUTO MODE STOPPED):
  Score: 75/100 (below 90 threshold)
  Issues:
  - Missing: Error handling task
  - Task 1: Too vague
  - Architecture: Layer separation unclear

  [E]dit plan

→ Plan edited... re-evaluating...
→ New score: 92/100 ✅
→ Checkpoint 1 approved, continuing...
```

---

## Test Case 5: Low Code Quality Score (< 90)

**Scenario**: Implementation with quality issues
**Mode**: `--auto` (should stop at Checkpoint 2)
**Expected Behavior**: Checkpoint 2 forces stop for fixes
**Duration**: Variable (depends on fixes needed)

### Steps

1. **Create issue and complete Phase 1 + Phase 1.5**:
   ```bash
   /work-issue #<N> --auto
   ```

2. **During Phase 2** (execute-plan):
   - Intentionally introduce quality issues:
     - Skip some tests
     - Use `any` types in TypeScript
     - Add console.log instead of proper logging
     - Miss error handling in one function

3. **Observe Checkpoint 2 behavior**:
   - Review runs automatically
   - Score comes back ~82/100
   - **Checkpoint 2 STOPS** (even in auto mode)
   - Shows issues:
     - Tests: Coverage only 65% (need 80%+)
     - TypeScript: Using `any` in 3 places
     - Logging: console.log found (use semantic logging)
     - Error handling: Missing in submitForm()

4. **Make decision**:
   ```
   [C]ontinue - merge with known issues (not recommended)
   [F]ix issues - resolve problems and re-review
   [S]top - pause to investigate
   [Q]uit - cancel workflow
   ```

5. **Choose [F]ix issues**:
   - Add missing tests
   - Replace `any` with proper types
   - Replace console.log with structured logging
   - Add error handling

6. **Re-review**:
   - Run `/review` again
   - Score improves to 94/100
   - Checkpoint 2 approves
   - Continue to Phase 3

### Validation

- [ ] Auto mode stopped at Checkpoint 2
- [ ] Score < 90 triggered the stop
- [ ] Quality issues identified accurately
- [ ] Fix workflow worked
- [ ] Re-review showed improvements
- [ ] Prevented merging low-quality code

### Expected Output

```
→ Phase 2.5: /review... ⚠️ (Score: 82/100)

📊 Checkpoint 2 (AUTO MODE STOPPED):
  Score: 82/100 (below 90 threshold)
  Issues:
  - Test coverage: 65% (need 80%+)
  - TypeScript: 3 uses of 'any'
  - Logging: console.log found
  - Error handling: Missing in submitForm()

  [F]ix issues

→ Issues fixed... re-reviewing...
→ New score: 94/100 ✅
→ Checkpoint 2 approved, proceeding to merge...
```

---

## Test Case 6: Interruption and Resume

**Scenario**: Workflow interrupted, resume from last checkpoint
**Mode**: Interactive with `--resume`
**Expected Behavior**: State recovery, resume from interruption point
**Duration**: Variable

### Steps

1. **Start workflow**:
   ```bash
   /work-issue #<N>
   ```

2. **Complete Phase 1 + Phase 1.5**:
   - Branch + plan created
   - Plan evaluated
   - Checkpoint 1 passed

3. **Start Phase 2** (execute-plan):
   - Begin task execution
   - Complete 5 of 10 tasks

4. **Interrupt workflow**:
   - Ctrl+C or close Claude Code
   - Simulate interruption

5. **Resume workflow**:
   ```bash
   /work-issue #<N> --resume
   ```

6. **Observe resume behavior**:
   - Reads `.claude/.work-issue-state.json`
   - Detects: Phase 2 in progress, 5/10 tasks done
   - Shows: "Resuming from task 6/10..."
   - Continues execution from task 6

7. **Complete workflow**:
   - Finish remaining 5 tasks
   - Continue through Phase 2.5, Checkpoint 2, Phase 3

### Validation

- [ ] State file saved after interruption
- [ ] Resume detected previous state correctly
- [ ] Showed "You are here" indicator
- [ ] Continued from correct task
- [ ] No duplicate work performed
- [ ] All state preserved (worktree path, issue number, etc.)
- [ ] Workflow completed successfully

### Expected Output

```
📊 Resuming workflow for Issue #<N>

Last state:
- Phase: 2 (Execute plan)
- Progress: 5/10 tasks completed
- Last task: "Add unit tests for service"

→ Resuming from task 6/10...
→ Task 6: Add integration tests...
→ Task 7: Update documentation...
...
```

---

## Test Case 7: Error Handling (GitHub API Failure)

**Scenario**: GitHub API is unreachable or rate-limited
**Mode**: Any
**Expected Behavior**: Clear error message, recovery instructions
**Duration**: <1 minute (fails fast)

### Steps

1. **Simulate GitHub API failure**:
   - Disconnect network temporarily, OR
   - Revoke GitHub CLI authentication: `gh auth logout`

2. **Run workflow**:
   ```bash
   /work-issue #<N>
   ```

3. **Observe error handling**:
   - Phase 1 attempts to fetch issue
   - GitHub API call fails
   - Error message displayed
   - Recovery options shown

### Validation

- [ ] Error detected quickly (< 5 seconds)
- [ ] Error message is clear and actionable
- [ ] Recovery instructions provided
- [ ] No partial state created (branch not created if issue fetch fails)
- [ ] Workflow fails gracefully (no corruption)

### Expected Output

```
❌ GitHub API Error

Failed to fetch issue #<N>

Possible causes:
1. Network connectivity issue
2. GitHub authentication expired
3. Issue not found
4. Rate limit exceeded

Recovery options:
1. Check network: ping github.com
2. Re-authenticate: gh auth login
3. Verify issue exists: gh issue view <N>
4. Wait if rate-limited (check: gh api rate_limit)
```

---

## Test Case 8: Error Handling (Git Operation Failure)

**Scenario**: Git operation fails (e.g., branch already exists)
**Mode**: Any
**Expected Behavior**: Clear error, options to resolve
**Duration**: <1 minute

### Steps

1. **Create pre-existing branch**:
   ```bash
   git checkout -b feature/123-test-branch
   git push -u origin feature/123-test-branch
   git checkout main
   ```

2. **Run workflow** for same issue:
   ```bash
   /work-issue #123
   ```

3. **Observe error handling**:
   - Phase 1 attempts to create branch
   - Detects branch already exists
   - Shows error with options

### Validation

- [ ] Error detected before any state created
- [ ] Clear explanation of conflict
- [ ] Multiple resolution options shown
- [ ] Each option has clear instructions
- [ ] No corrupted state

### Expected Output

```
⚠️ Branch Already Exists

Branch 'feature/123-test-branch' already exists locally and remotely.

Options:
1. Use existing branch:
   git checkout feature/123-test-branch
   /work-issue #123 --resume

2. Delete and recreate:
   git branch -D feature/123-test-branch
   git push origin --delete feature/123-test-branch
   /work-issue #123

3. Use different prefix:
   /work-issue #123 --branch-prefix v2
```

---

## Test Execution Checklist

When running regression tests, use this checklist:

### Pre-Test Setup
- [ ] Main branch up to date: `git pull origin main`
- [ ] GitHub CLI authenticated: `gh auth status`
- [ ] Clean working directory: `git status`
- [ ] No active worktrees: `git worktree list`

### During Testing
- [ ] Record start time
- [ ] Document actual behavior vs expected
- [ ] Note any deviations or errors
- [ ] Capture relevant output/logs
- [ ] Track performance metrics

### Post-Test Validation
- [ ] All validation checkboxes marked
- [ ] Compare actual vs expected output
- [ ] Document any issues found
- [ ] Clean up test artifacts:
  - Delete test branches
  - Remove worktrees
  - Close test issues
  - Delete test PRs

### Test Report Template

```markdown
## Test Execution Report

**Date**: YYYY-MM-DD
**Test Case**: #N - [Name]
**Executor**: [Name/System]
**Result**: ✅ PASS / ⚠️ PARTIAL / ❌ FAIL

### Actual vs Expected

| Aspect | Expected | Actual | Match |
|--------|----------|--------|-------|
| Duration | X min | Y min | ✅/❌ |
| Checkpoints | Stopped at 1, 2 | Stopped at 1, 2 | ✅ |
| Score Phase 1.5 | 92/100 | 95/100 | ✅ |
| Score Phase 2.5 | 88/100 | 91/100 | ✅ |
| Tasks completed | 10/10 | 10/10 | ✅ |

### Issues Found

1. [None / Issue description]

### Notes

- [Any observations]
```

---

## Maintenance

**Update Frequency**: After each workflow change
**Owner**: Development team
**Last Updated**: 2026-03-11

### When to Update

- ✅ New skill added to workflow
- ✅ Workflow logic changed
- ✅ New error scenarios discovered
- ✅ Performance characteristics change
- ✅ New validation added

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-11 | Initial test case library (8 cases) |

---

**Total Test Cases**: 8
**Coverage**: Simple, Medium, Complex, Error Handling, State Recovery
**Status**: Ready for use in future regression testing
