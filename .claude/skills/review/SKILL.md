---
name: review
description: |
  Conduct code review with quality checks, architecture validation, and framework compliance.
  TRIGGER when: user wants code reviewed ("review my code", "check this PR", "review these changes", "quality check").
  Dynamically detects project configuration (Pillars, architecture rules, ADRs) and adapts checks accordingly.
  DO NOT TRIGGER when: user wants to create/write code (not reviewing), or just wants explanations without quality assessment.
version: "2.2.0"
argument-hint: "[options]"
---

# Code Review - Quality and Architecture Validation

Automated code review that adapts to your project's configuration, checking quality, architecture, Pillars, ADRs, security, and performance.

## Overview

This skill provides comprehensive code review by:

**What it does:**
1. Runs quality gates (types, tests, linting)
2. Validates architecture patterns (dynamically detected)
3. Checks Pillar compliance (based on project profile)
4. Verifies ADR compliance (scans docs/adr/)
5. Identifies security vulnerabilities
6. Detects performance issues
7. Writes review status for /finish-issue integration

**Why it's needed:**
Manual code review is time-consuming and inconsistent. This skill automates quality checks while adapting to each project's specific configuration (minimal vs full-stack, different architecture patterns, custom ADRs).

**Key feature - Dynamic Detection:**
- No hardcoded assumptions
- Reads project profile to determine which Pillars to check
- Scans architecture rules from .claude/rules/architecture/
- Discovers ADRs from docs/adr/
- Different projects → different checks

## Workflow Steps

Copy this checklist to track progress:

```
Task Progress:
- [ ] Step 1: Create todo list
- [ ] Step 2: Run quality gates
- [ ] Step 3: Check architecture patterns
- [ ] Step 4: Verify Pillar compliance
- [ ] Step 5: Check ADR compliance
- [ ] Step 6: Security scan
- [ ] Step 7: Performance check
- [ ] Step 8: Write review status file
```

Execute these steps in sequence:

### Step 1: Create Todo List

**Initialize review tracking** using TaskCreate:

```
Task #1: Run quality gates (types, tests, linting)
Task #2: Check architecture patterns (blocked by #1)
Task #3: Verify Pillar compliance (blocked by #1)
Task #4: Check ADR compliance (blocked by #1)
Task #5: Security scan (blocked by #1)
Task #6: Performance check (blocked by #1)
Task #7: Write review status file (blocked by #2-6)
```

After creating tasks, proceed with review execution.

## Review Dimensions

### 1. Quality Gates

Basic quality checks that every project needs:

```
✅ Types valid (TypeScript compiles)
✅ Tests passing
✅ Linting passes
✅ No obvious bugs
```

**How to check:**
```bash
# TypeScript
npx tsc --noEmit

# Tests
npm test

# Linting
npm run lint
```

### 2. Architecture Validation

**Dynamic detection** - scans `.claude/rules/architecture/` to find which rules are enabled:

```
Process:
1. List files in .claude/rules/architecture/
2. For each rule file found, check compliance
3. Common rules to look for:
   - clean-architecture.md → Check module boundaries
   - dependency-rules.md → Check dependency direction
   - layer-boundaries.md → Check layer separation
   - naming-conventions.md → Check naming patterns
   - error-handling.md → Check error patterns

If no architecture rules found:
  ℹ️ Skip architecture checks (not configured for this project)
```

### 3. Pillar Compliance

**Dynamic detection** - determines which Pillars to check based on project profile:

```
Detection Method:
1. Read .framework-install file for profile
   OR scan .prot/pillars/ for installed Pillars
2. Map profile to Pillars:
   - minimal: A, B, K (3 Pillars)
   - node-lambda: A, B, K, M, Q, R (6 Pillars)
   - react-aws: A, B, K, L, M, Q, R (7 Pillars)
   - custom: Whatever exists in .prot/pillars/

3. Only check enabled Pillars

Example checks (if enabled):
✅ Pillar A (Nominal Types) - Branded types for IDs
✅ Pillar B (Airlock) - Schema validation at boundaries
✅ Pillar K (Testing) - Test pyramid structure
✅ Pillar M (Saga) - Transaction compensation
✅ Pillar Q (Idempotency) - Idempotent operations
✅ Pillar R (Logging) - Semantic logging with traceId
```

**Important:** Only check Pillars enabled in THIS project. Don't assume all Pillars exist.

### 4. ADR Compliance

**Dynamic scanning** - discovers and checks ADRs specific to this project:

```
Process:
1. Scan docs/adr/ (or docs/ADRs/) for all *.md files
2. Extract ADR number, title, and requirements
3. Identify which ADRs are relevant to changed code
4. Check compliance for each relevant ADR
5. Report violations with file:line references

Example (project-specific):
✅ ADR-001 (Official Skill Patterns)
   Check: SKILL.md has YAML frontmatter
   Check: Description has TRIGGER conditions

⚠️ ADR-009 (Zustand Vanilla Store)
   Violation: src/stores/taskStore.ts:5
   Issue: Using create() instead of createStore()
   Fix: import { createStore } from 'zustand/vanilla'

When no ADRs found:
  ℹ️ No ADRs in docs/adr/ - skip ADR checks
```

**Key point:** ADR checks are 100% project-specific. Different projects have different ADRs.

### 5. Security

Common security checks:

```
✅ Input validation present
✅ No hardcoded secrets or API keys
✅ SQL injection prevention (parameterized queries)
✅ CSRF protection (if web app)
✅ XSS prevention (escaped output)
```

### 6. Performance

Basic performance checks:

```
✅ No N+1 queries
✅ Proper caching strategy
✅ Reasonable algorithm complexity (no O(n²) in hot paths)
✅ Lazy loading where appropriate
```

## Review Output

**Output adapts based on mode:**

### Auto Mode Output (2 lines)

When called by `/work-issue --auto`:

```
✅ Code review: 92/100 (approved)
Status: .claude/.review-status.json
```

### Interactive Mode Output (≤20 lines)

When called directly by user:

```markdown
# Code Review: Issue #{issue_number}

Score: 85/100 (approved_with_recommendations)
Files: 8 changed (+150/-50)
Issues: 0 blocking, 2 recommendations

Quality Gates: ✅ All passed
Pillars: 7/7 compliant
ADRs: 2/3 compliant

Top Issues:
1. ADR-009 violation: taskStore.ts:5 - Use createStore()
2. Performance: N+1 query in userLoader.ts:23

Status: .claude/.review-status.json
Next: Fix issues or /finish-issue
```

### Full Report Format (status file only)

Complete review stored in `.claude/.review-status.json`:

```json
{
  "timestamp": "2026-03-11T14:30:00Z",
  "issue_number": 23,
  "status": "approved_with_recommendations",
  "score": 85,
  "breakdown": {
    "quality_gates": 90,
    "architecture": 88,
    "security": 90,
    "performance": 75
  },
  "issues_count": {
    "blocking": 0,
    "recommendations": 2
  },
  "issues": [
    {
      "file": "src/stores/taskStore.ts",
      "line": 5,
      "category": "adr_compliance",
      "description": "ADR-009 violation: Using create() instead of createStore()",
      "fix": "Import from 'zustand/vanilla'"
    }
  ]
}
```

## Approval Levels

**✅ Green (Approved)**
- All quality checks pass
- Architecture sound
- Pillars correctly implemented
- ADRs complied with
- No security issues
- Ready to merge

**⚠️ Yellow (Approved with recommendations)**
- Minor issues that don't block merge
- Non-critical ADR deviations (with justification)
- Can be addressed in follow-up
- Merge allowed with observations

**❌ Red (Changes required)**
- Must fix before merge
- Security vulnerabilities
- Breaking changes
- Architecture violations
- Critical ADR violations

## Integration with /finish-issue

After review, `/finish-issue` can read the status file to skip re-review if results are still valid (within 90 minutes).

**Workflow:**
```
/review              # Review code, write status
/finish-issue #N     # Reads status, skips re-review if valid
```

## Status File for Integration

After review, write `.claude/.review-status.json`:

```json
{
  "timestamp": "2026-03-11T14:30:00Z",
  "issue_number": 23,
  "status": "approved",
  "score": 92,
  "breakdown": {
    "quality_gates": 90,
    "architecture": 95,
    "security": 90,
    "performance": 92
  },
  "issues_count": {
    "blocking": 0,
    "recommendations": 2
  },
  "valid_until": "2026-03-11T16:00:00Z"
}
```

**Status values:**
- `"approved"` - Score > 90, no blocking issues
- `"approved_with_recommendations"` - Score 70-90, minor issues
- `"issues_found"` - Score < 70, must fix before proceeding

**Validity:** 90 minutes from review completion

**Used by:**
- `/work-issue` - Checkpoint 2 logic (auto-skip if score > 90)
- `/finish-issue` - Skips re-review if status valid

## Usage Examples

### Example 1: Review Current Changes

**User says:**
> "review my code changes"

**What happens:**
1. Detect project config (profile, rules, ADRs)
2. Run quality gates
3. Check architecture, Pillars, ADRs
4. Generate report
5. Write .review-status.json
6. Show approval status

### Example 2: Review Specific Files

**User says:**
> "review src/auth/ for security issues"

**What happens:**
1. Focus on src/auth/ directory
2. Run security checks
3. Check relevant Pillars (B for validation)
4. Check relevant ADRs
5. Report findings

### Example 3: Pre-PR Review

**User says:**
> "check if this is ready for PR"

**What happens:**
1. Full review all dimensions
2. Check quality gates
3. Validate all applicable patterns
4. Provide go/no-go recommendation
5. Write status for /finish-issue

## Best Practices

1. **Run before /finish-issue** - Catches issues early
2. **Trust dynamic detection** - Skill adapts to your project
3. **Fix blocking issues** - Don't merge with red flags
4. **Learn from reviews** - Improves code quality over time
5. **Re-review after fixes** - Status expires in 90 minutes

## Task Management

**After completing each review dimension**, update progress:

```
Quality gates done → Update Task #1
Architecture validated → Update Task #2
Pillars checked → Update Task #3
ADRs verified → Update Task #4
Security scanned → Update Task #5
Performance checked → Update Task #6
Status file written → Update Task #7
```

Provides real-time visibility of review progress.

## Final Verification

**Before completing review**, verify:

```
- [ ] All 7 review tasks completed
- [ ] Status file written (.claude/.review-status.json)
- [ ] Approval level determined (✅/⚠️/❌)
- [ ] All blocking issues documented
- [ ] Score calculated (0-100)
- [ ] Valid until timestamp set (90 min)
```

Missing items indicate incomplete review.

## Worktree Support

If the issue was started with `/start-issue` and a worktree was created, review operations MUST use the worktree path.

### Auto-Detection

**Extract worktree path from plan**:
```bash
PLAN_FILE=".claude/plans/active/issue-${ISSUE_NUM}-plan.md"
WORKTREE_PATH=$(grep "^**Worktree**:" "$PLAN_FILE" | cut -d' ' -f2)
```

### File Operations with Worktree

**All file reads must use absolute worktree paths**:

```bash
# ✅ CORRECT - Review files in worktree
Read ${WORKTREE_PATH}/.claude/skills/start-issue/SKILL.md
Read ${WORKTREE_PATH}/src/components/Button.tsx
Read ${WORKTREE_PATH}/tests/button.test.ts

# Check git diff in worktree
git -C ${WORKTREE_PATH} diff main...HEAD

# Get changed files in worktree
git -C ${WORKTREE_PATH} diff --name-only main...HEAD

# ❌ WRONG - Reviews main repo instead of worktree
Read .claude/skills/start-issue/SKILL.md
git diff main...HEAD
```

### Review Workflow with Worktree

**Step-by-step**:

1. **Read plan from worktree** to identify issue and scope
2. **Get changed files** from worktree git diff
3. **Review each file** using absolute worktree paths
4. **Check tests** in worktree test directory
5. **Verify builds** in worktree (if applicable)
6. **Write status file** to main repo (for /work-issue integration)

### Fallback Behavior

If no worktree path found:
- ✅ Use current working directory
- ✅ Standard relative paths work
- ✅ Backward compatible

---

## Related Skills

- **/eval-plan** - Validates plans (Phase 1.5 - symmetric validation for planning)
- **/work-issue** - Calls this skill in Phase 2.5 (quality check after implementation)
- **/finish-issue** - Uses review status to skip re-review
- **/pillar** - Deep dive into specific Pillar
- **/adr** - Create or check Architecture Decision Records

---

**Version:** 2.2.0
**Pattern:** Tool-Reference (guides review process)
**Compliance:** ADR-001 ✅ | WORKFLOW_PATTERNS.md ✅
**Last Updated:** 2026-03-18
**Changelog:**
- v2.2.0: Added mode-aware output (2 lines auto, ≤20 lines interactive) (Issue #263)
- v2.1.0: Dynamic configuration detection
- v2.0.0: Added Pillar and ADR compliance checks
