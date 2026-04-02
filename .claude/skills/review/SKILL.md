---
name: review
description: |
  Conduct code review with quality checks, architecture validation, and framework compliance.
  TRIGGER when: user wants code reviewed ("review my code", "check this PR", "review these changes", "quality check").
  Dynamically detects project configuration (Pillars, architecture rules, ADRs) and adapts checks accordingly.
  DO NOT TRIGGER when: user wants to create/write code (not reviewing), or just wants explanations without quality assessment.
version: "2.4.1"
last-updated: "2026-03-30"
argument-hint: "[options]"
---

# Code Review - Quality and Architecture Validation

Automated code review that adapts to your project's configuration, checking quality, architecture, Pillars, ADRs, security, and performance.

## Overview

This skill provides comprehensive code review by:

**What it does:**
1. Runs quality gates (types, tests, linting)
2. Validates architecture patterns (dynamically detected)
3. **Checks skill version updates** (prevents version conflicts - Issue #401)
4. Checks Pillar compliance (based on project profile)
5. Verifies ADR compliance (scans docs/ADRs/)
6. Identifies security vulnerabilities
7. Detects performance issues
8. Writes review status for `/finish-issue` integration

**Why it's needed:**
Manual code review is time-consuming and inconsistent. This skill automates quality checks while adapting to each project's specific configuration.

**Key feature - Dynamic Detection:**
- No hardcoded assumptions
- Reads project profile to determine which Pillars to check
- Scans architecture rules from `.claude/rules/architecture/`
- Discovers ADRs from `docs/ADRs/`
- Different projects → different checks

**When to use:**
- After `/execute-plan` completes implementation
- Before `/finish-issue` creates PR
- Anytime you want code quality validation

## Arguments

```bash
/review [options]
```

**Common usage:**
```bash
/review                   # Review current branch changes
/review --strict          # Treat warnings as errors
/review --mode=auto       # Minimal output (for automation)
```

**Options:**
- `--strict` - Treat recommendations as blocking issues
- `--mode=auto` - Auto mode output (2 lines, used by /auto-solve-issue)
- `--files="pattern"` - Review specific files only

## AI Execution Instructions

**CRITICAL: Adaptive strategy and worktree support**

When executing `/review`, AI MUST follow this pattern:

### Step 0: Smart Decision (Adaptive Strategy)

**BEFORE running checks**, analyze changes and select strategy:

```bash
# Get change statistics
LINES_CHANGED=$(git diff --stat main...HEAD | tail -1 | grep -oE '[0-9]+ insertions' | cut -d' ' -f1)

if [ "$LINES_CHANGED" -lt 50 ]; then
  STRATEGY="SMALL"  # Focus on quality gates
elif [ "$LINES_CHANGED" -lt 200 ]; then
  STRATEGY="MEDIUM"  # Balanced review
else
  STRATEGY="LARGE"  # Deep review with full dimensions
fi
```

### Step 1: Create Todo List

```python
tasks = [
    TaskCreate("Smart decision - select strategy"),
    TaskCreate("Check goal coverage"),
    TaskCreate("Check skill version updates"),
    TaskCreate("Run quality gates"),
    TaskCreate("Check architecture patterns"),
    TaskCreate("Verify Pillar compliance"),
    TaskCreate("Check ADR compliance"),
    TaskCreate("Security scan"),
    TaskCreate("Performance check"),
    TaskCreate("Write review status file")
]
```

### Step 2: Check Goal Coverage (Phase 1)

**CRITICAL FIRST CHECK**: Verify implementation solves Issue requirements.

```bash
# Get issue number and load issue body
ISSUE_NUM=$(git branch --show-current | grep -oE '[0-9]+')
gh issue view $ISSUE_NUM --json body --jq '.body' > /tmp/issue-body.md

# Extract acceptance criteria
grep -E '- \[ \]|^- |^[0-9]+\.' /tmp/issue-body.md > /tmp/acceptance-criteria.txt

# Check if all criteria are addressed in code changes
# Score: requirements_coverage * 100
# If score < 80, auto-reject
```

**See**: [QUALITY.md](./QUALITY.md) for scoring details

### Step 3: Check Skill Version Updates

**Triggered when**: `.claude/skills/*/SKILL.md` files are modified.

```python
# AI-EXECUTABLE
import sys
from pathlib import Path
sys.path.insert(0, '.claude/skills/_scripts')

from utils.version import check_version_field, compare_versions

# Detect modified SKILL.md files
modified_skills = Bash("git diff --name-only HEAD | grep '.claude/skills/.*/SKILL.md'")

for skill_file in modified_skills.strip().split('\n'):
    if not skill_file:
        continue

    skill_path = Path(skill_file)

    # Check current version
    current_result = check_version_field(skill_path)

    # Get old version from git
    old_content = Bash(f"git show HEAD:{skill_file}")
    old_version = get_version_from_frontmatter(old_content)

    if current_result['has_version'] and old_version:
        if current_result['version'] == old_version:
            issues.append({
                "file": skill_file,
                "category": "version_unchanged",
                "severity": "warning",
                "message": f"Version not updated: {old_version}"
            })
```

**Shared module**: Uses `.claude/skills/_scripts/utils/version.py` (Issue #406)
**See**: [VERSION_CHECK.md](./VERSION_CHECK.md) for complete logic

### Step 4-9: Run Review Dimensions

Execute checks based on strategy selected in Step 0:

| Strategy | Dimensions | Focus |
|----------|------------|-------|
| SMALL | Quality gates, quick architecture | Fast validation |
| MEDIUM | All dimensions (standard weights) | Balanced |
| LARGE | Deep architecture, full Pillars | Comprehensive |

**Dimensions:**
1. **Quality Gates** (30 pts) - Types, tests, linting, build
2. **Architecture** (25 pts) - Layer separation, dependencies
3. **Pillars** (20 pts) - Error handling, logging, validation
4. **ADRs** (10 pts) - Compliance with decisions
5. **Security** (10 pts) - Vulnerabilities, input validation
6. **Performance** (5 pts) - Algorithm efficiency

**See**: [CHECKLIST.md](./CHECKLIST.md) for complete checklist

### Step 10: Write Status File

**CRITICAL**: Always write `.claude/.review-status.json`:

```python
import json
from datetime import datetime, timedelta

status = {
    "timestamp": datetime.now().isoformat(),
    "issue_number": issue_number,
    "status": "approved" if score > 90 else "needs_improvement" if score >= 70 else "rejected",
    "score": score,
    "breakdown": {
        "quality_gates": quality_score,
        "architecture": arch_score,
        "pillar_compliance": pillar_score,
        "adr_compliance": adr_score,
        "security": security_score,
        "performance": perf_score
    },
    "issues_count": {
        "blocking": len(blocking_issues),
        "recommendations": len(recommendations)
    },
    "valid_until": (datetime.now() + timedelta(minutes=90)).isoformat()
}

with open(".claude/.review-status.json", "w") as f:
    json.dump(status, f, indent=2)
```

### Step 11: Output Results (Mode-Aware)

**Auto mode** (--mode=auto or called by /auto-solve-issue):
```text
✅ Review complete: 92/100 (approved)
Status: .claude/.review-status.json
```

**Interactive mode** (direct invocation):
```markdown
# Code Review: Issue #421

Score: 92/100 (approved)
Issues: 0 blocking, 2 recommendations

Top Recommendations:
1. Architecture - Move API call to service layer (-2 pts)
2. Performance - Use Set for faster lookup (-2 pts)

Full details: .claude/.review-status.json
Next: /finish-issue #421
```

## Workflow Steps

Copy this checklist to track progress:

```markdown
Task Progress:
- [ ] Step 0: Smart decision (adaptive strategy)
- [ ] Step 1: Create todo list
- [ ] Step 2: Check goal coverage
- [ ] Step 3: Check skill version updates
- [ ] Step 4: Run quality gates
- [ ] Step 5: Check architecture patterns
- [ ] Step 6: Verify Pillar compliance
- [ ] Step 7: Check ADR compliance
- [ ] Step 8: Security scan
- [ ] Step 9: Performance check
- [ ] Step 10: Write review status file
```

Execute these steps in sequence with TaskCreate/TaskUpdate for progress tracking.

## Review Dimensions

### 1. Quality Gates (30 points)

Basic quality checks:
- TypeScript compilation (types valid)
- Test execution (all passing)
- Linting (no errors)
- Build success

### 2. Architecture Validation (25 points)

Check architecture patterns:
- Layer separation (UI → Domain → Data)
- Dependency direction (inward only)
- Module boundaries (no circular deps)

### 3. Pillar Compliance (20 points)

Based on project profile:
- Error handling present
- Logging at appropriate levels
- Input validation at boundaries
- Documentation for public APIs
- Test coverage for changes

### 4. ADR Compliance (10 points)

Adherence to Architecture Decision Records:
- Scan `docs/ADRs/` directory
- Check code follows applicable ADRs
- Flag deviations with justification needed

### 5. Security (10 points)

Identify vulnerabilities:
- Input validation
- SQL injection prevention
- XSS prevention
- No secrets in code
- Dependency vulnerabilities

### 6. Performance (5 points)

Detect performance issues:
- Algorithmic complexity (avoid O(n²) where O(n) possible)
- Efficient data structures
- No memory leaks
- Database queries optimized

**See**: [QUALITY.md](./QUALITY.md) for scoring details

## Approval Levels

### ✅ Approved (Score > 90)
- All critical gates pass
- No blocking issues
- Ready to merge

### ⚠️ Needs Improvement (Score 70-90)
- Some gates fail or recommendations present
- No blocking issues
- Can merge with awareness

### ❌ Rejected (Score < 70)
- Critical gates fail
- Blocking issues present
- Must fix before merge

**See**: [QUALITY.md](./QUALITY.md) for threshold details

## Integration with /finish-issue

After review, `/finish-issue` reads the status file to skip re-review if valid (within 90 minutes).

**Workflow:**
```bash
/review              # Review code, write status
/finish-issue #N     # Reads status, skips re-review if valid
```

## Status File for Integration

After review, write `.claude/.review-status.json`:

```json
{
  "timestamp": "2026-03-30T14:30:00Z",
  "issue_number": 421,
  "status": "approved",
  "score": 92,
  "breakdown": {
    "quality_gates": 30,
    "architecture": 23,
    "pillar_compliance": 18,
    "adr_compliance": 10,
    "security": 10,
    "performance": 1
  },
  "issues_count": {
    "blocking": 0,
    "recommendations": 2
  },
  "valid_until": "2026-03-30T16:00:00Z"
}
```

**Status values:**
- `"approved"` - Score > 90, no blocking issues
- `"needs_improvement"` - Score 70-90, minor issues
- `"rejected"` - Score < 70, must fix before proceeding

**Validity:** 90 minutes from review completion

**Used by:**
- `/auto-solve-issue` - Checkpoint 2 logic (auto-continue if score ≥ 90)
- `/finish-issue` - Skips re-review if status valid

## Usage Examples

### Example 1: Review Current Changes

**User says:**
> "review my code"

**What happens:**
1. Detect issue number from branch
2. Run smart decision (analyze change size)
3. Execute adaptive review strategy
4. Generate report with score
5. Write status file

**See**: [EXAMPLES.md](./EXAMPLES.md) for more examples

### Example 2: Goal Coverage Failure

**Scenario:** Issue requires 5 acceptance criteria, only 3 implemented.

**Output:**
```markdown
## 1. Goal Coverage Check ❌

**Issue Requirements**: 3/5 (60%) ← Below 80% threshold
Missing: AC3, AC5

**Status**: REJECTED (blocking)
```

### Example 3: Skill Version Not Updated

**Scenario:** Modified SKILL.md but forgot version bump.

**Output:**
```markdown
## 3. Skill Version Check ⚠️

⚠️ `.claude/skills/eval-plan/SKILL.md`
   Version: 1.1.0 (unchanged)
   Suggested: 1.2.0 (minor bump)

**Status**: NEEDS_IMPROVEMENT (blocking)
```

**See**: [VERSION_CHECK.md](./VERSION_CHECK.md) for details

## Best Practices

1. **Run before /finish-issue** - Catches issues early
2. **Trust dynamic detection** - Skill adapts to your project
3. **Fix blocking issues** - Don't merge with critical failures
4. **Learn from reviews** - Improves code quality over time
5. **Re-review after fixes** - Status expires in 90 minutes

## Worktree Support

If the issue was started with `/start-issue` and a worktree was created, review operations MUST use the worktree path.

### Auto-Detection

```bash
PLAN_FILE=".claude/plans/active/issue-${ISSUE_NUM}-plan.md"
WORKTREE_PATH=$(grep "^**Worktree**:" "$PLAN_FILE" | cut -d' ' -f2)
```

### File Operations

**All file reads must use absolute worktree paths**:

```bash
# ✅ CORRECT - Review files in worktree
Read ${WORKTREE_PATH}/src/components/Button.tsx
git -C ${WORKTREE_PATH} diff main...HEAD

# ❌ WRONG - Reviews main repo instead
Read src/components/Button.tsx
git diff main...HEAD
```

## Task Management

After each step completion, update progress using TaskUpdate:

```python
# Mark task in progress
TaskUpdate(task_id, status="in_progress")

# Execute review dimension
execute_dimension()

# Mark complete
TaskUpdate(task_id, status="completed")
```

## Final Verification

Before completing review, verify:

```markdown
- [ ] All review tasks completed
- [ ] Status file written (.claude/.review-status.json)
- [ ] Approval level determined (✅/⚠️/❌)
- [ ] All blocking issues documented
- [ ] Score calculated (0-100)
- [ ] Valid until timestamp set (90 min)
```

## Related Skills

- **/eval-plan** - Validates plans (Phase 1.5 - symmetric validation for planning)
- **/auto-solve-issue** - Calls this skill in Phase 2.5 (quality check after implementation)
- **/finish-issue** - Uses review status to skip re-review
- **/execute-plan** - Implementation phase (run before this)

## Documentation

- **[CHECKLIST.md](./CHECKLIST.md)** - Complete review checklist for all dimensions
- **[QUALITY.md](./QUALITY.md)** - Scoring methodology and approval thresholds
- **[VERSION_CHECK.md](./VERSION_CHECK.md)** - Skill version validation logic (Issue #401)
- **[EXAMPLES.md](./EXAMPLES.md)** - Real-world usage examples

---

**Version:** 2.4.1
**Last Updated:** 2026-03-30
**Pattern:** Tool-Reference (guides review process)
**Compliance:** ADR-001 ✅ | ADR-014 ✅ | WORKFLOW_PATTERNS.md ✅
**Changelog:**
- v2.4.1: Use shared version.py module for version checking (Issue #406)
- v2.4.0: Split into 5 documents for ADR-014 compliance (Issue #421)
- v2.3.0: Added skill version check to prevent version conflicts (Issue #401)
- v2.2.0: Added mode-aware output (2 lines auto, ≤20 lines interactive)
- v2.1.0: Dynamic configuration detection
- v2.0.0: Added Pillar and ADR compliance checks
