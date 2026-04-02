---
name: eval-plan
description: |
  Evaluate implementation plan before execution - validates architecture, coverage, dependencies, and best practices.
  TRIGGER when: user wants plan validated ("evaluate plan", "check plan", "validate plan", "review the plan before starting").
  DO NOT TRIGGER when: user wants to execute plan (use /execute-plan), create plan (use /start-issue or /plan), or review code (use /review).
version: "1.4.1"
argument-hint: "[issue-number] [--strict] [--json] [--mode=auto]"
allowed-tools: Bash(gh *), Read, Glob, Grep
disable-model-invocation: false
user-invocable: true
---

# Eval Plan - Implementation Plan Validator

Validate implementation plans before execution to catch issues early and prevent costly rework.

## Overview

This skill provides automated plan validation by checking:

**What it does:**
1. **Architecture alignment** - Validates against .claude/rules/architecture/
2. **Acceptance criteria coverage** - Ensures all issue requirements addressed
3. **Task dependencies** - Validates correct ordering and relationships
4. **Best practices** - Checks for error handling, docs, logging, tests
5. **Task clarity** - Ensures tasks are specific and actionable
6. **Generates scored evaluation** - 0-100 score with actionable feedback
7. **Writes status file** - For /work-issue integration
8. **Version field validation** - Checks YAML frontmatter has version field (see [VERSION_CHECK.md](VERSION_CHECK.md))

**Why it's needed:**
Manual plan review misses systematic issues like architecture violations, missing requirements, and dependency problems. These surface during implementation (Phase 2) causing 60+ minutes of rework. This skill catches issues before coding starts.

**When to use:**
- After /start-issue creates a plan
- Before /execute-plan begins implementation
- Automatically in /work-issue as Phase 1.5
- Anytime you want plan validation

**Value proposition:**
- Catches architecture violations before implementation
- Ensures requirement coverage (prevents incomplete PRs)
- Validates task ordering (prevents implementation stalls)
- Reminds of best practices (error handling, docs, logging)
- Fast (30-60 seconds) vs high impact (prevents hours of rework)

## Arguments

```bash
/eval-plan [issue-number] [options]
```

**Common usage:**
```bash
/eval-plan              # Evaluate plan for current branch
/eval-plan #23          # Evaluate specific issue's plan
/eval-plan --strict     # Fail on recommendations (not just blocking)
/eval-plan --json       # Output JSON only (for automation)
/eval-plan --mode=auto  # Auto-fix minor issues when score ≥90 (used by work-issue --auto)
```

**Options:**
- `[issue-number]` - Optional, inferred from branch if omitted
- `--strict` - Treat recommendations as blocking issues
- `--json` - Output JSON format only (no human-readable summary)
- `--mode=auto` - Enable auto-fix mode for minor issues (requires score ≥90)

## AI Execution Instructions

**CRITICAL: Evaluation scoring and status file**

When executing `/eval-plan`, AI MUST follow this pattern:

### Step 1: Create 9 Evaluation Tasks

```python
# AI-EXECUTABLE
tasks = [
    TaskCreate(subject="Load plan file", ...),
    TaskCreate(subject="Evaluate architecture alignment", ...),
    TaskCreate(subject="Check acceptance criteria coverage", ...),
    TaskCreate(subject="Validate task dependencies", ...),
    TaskCreate(subject="Assess best practices", ...),
    TaskCreate(subject="Check task clarity", ...),
    TaskCreate(subject="Check version field", ...),  # NEW - Step 6.5
    TaskCreate(subject="Generate scored report", ...),
    TaskCreate(subject="Write status file", ...)
]
```

### Step 2: Load Plan from Worktree

```python
# AI-EXECUTABLE
# Check plan metadata for worktree path
plan_file = f".claude/plans/active/issue-{issue_number}-plan.md"
worktree_path = extract_worktree_from_plan(plan_file)

if worktree_path:
    # CRITICAL: Read plan from worktree
    plan_file = f"{worktree_path}/.claude/plans/active/issue-{issue_number}-plan.md"

plan_content = Read(plan_file)
```

### Step 3: Evaluate 5 Dimensions

```python
# AI-EXECUTABLE
scores = {
    "architecture": evaluate_architecture(plan, max=40),
    "coverage": evaluate_coverage(plan, issue, max=30),
    "dependencies": evaluate_dependencies(plan, max=15),
    "practices": evaluate_practices(plan, max=10),
    "clarity": evaluate_clarity(plan, max=5)
}

total_score = sum(scores.values())  # Max 100
```

**Detailed evaluation criteria**: See [CHECKLIST.md](CHECKLIST.md) for complete scoring guidelines.

### Step 4: Check Version Field (NEW)

```python
# AI-EXECUTABLE
import sys
sys.path.insert(0, '.claude/skills/_scripts')

from utils.version import get_version_from_frontmatter, validate_version_format

# Check if plan YAML frontmatter has version field
version = get_version_from_frontmatter(plan_content)

if not version:
    # Warning (not blocking) - version field missing
    issues.append({
        "category": "version_missing",
        "severity": "warning",
        "message": "Plan frontmatter missing version field"
    })
elif not validate_version_format(version):
    # Warning - invalid version format
    issues.append({
        "category": "version_invalid",
        "severity": "warning",
        "message": f"Invalid version format: '{version}'"
    })
```

**Detailed version checking logic**: See [VERSION_CHECK.md](VERSION_CHECK.md) for implementation.
**Shared module**: Uses `.claude/skills/_scripts/utils/version.py` (Issue #406)

### Step 5: Write Status File

**CRITICAL**: Always write `.claude/.eval-plan-status.json`:

```python
# AI-EXECUTABLE
import json
from datetime import datetime, timedelta

status = {
    "timestamp": datetime.now().isoformat(),
    "issue_number": issue_number,
    "status": "approved" if total_score > 90 else "needs_improvement" if total_score >= 70 else "rejected",
    "score": total_score,
    "breakdown": scores,
    "issues_count": {
        "blocking": len(blocking_issues),
        "recommendations": len(recommendations),
        "suggestions": len(suggestions)
    },
    "valid_until": (datetime.now() + timedelta(minutes=90)).isoformat(),
    "plan_file": plan_file
}

with open(".claude/.eval-plan-status.json", "w") as f:
    json.dump(status, f, indent=2)
```

**Detailed scoring logic**: See [SCORING.md](SCORING.md) for algorithm and status file format.

### Step 6: Auto-Fix (if --mode=auto and score ≥90)

**CRITICAL**: Apply auto-fixes when in auto mode with passing score:

```python
# AI-EXECUTABLE
def auto_fix_if_applicable(mode, score, issues, plan_content, plan_file):
    """
    自动修复微小问题（仅在 auto 模式且分数 ≥90 时）
    """
    # 检查是否启用自动修复
    if mode != "auto" or score < 90:
        return plan_content, []  # 不修复

    # 分类问题：微小 vs 重大
    minor_issues = [i for i in issues if i.category in AUTO_FIXABLE]
    major_issues = [i for i in issues if i.category not in AUTO_FIXABLE]

    if not minor_issues:
        return plan_content, []  # 无需修复

    # 应用修复
    fixes_applied = []
    content = plan_content

    try:
        for issue in minor_issues:
            fixer = FIXERS[issue.category]
            content, fix_log = fixer(content, issue)
            fixes_applied.append(fix_log)

        # 写入修复后的计划
        Write(plan_file, content)

        # 重新评估（可选，验证修复效果）
        new_score = evaluate_plan(content)

        return content, fixes_applied, new_score

    except Exception as e:
        # 优雅降级：修复失败，返回原内容
        log.error(f"Auto-fix failed: {e}")
        return plan_content, [], score

# 修复器定义
AUTO_FIXABLE = {
    "missing_todo",
    "incomplete_test",
    "format_issue",
    "missing_file_ref",
    "logic_gap",
    "version_missing"  # NEW - Auto-fixable
}

FIXERS = {
    "missing_todo": lambda content, issue: add_todo_comment(content, issue),
    "incomplete_test": lambda content, issue: expand_test_description(content, issue),
    "format_issue": lambda content, issue: fix_task_numbering(content),
    "missing_file_ref": lambda content, issue: add_file_path(content, issue),
    "logic_gap": lambda content, issue: insert_missing_step(content, issue),
    "version_missing": lambda content, issue: add_version_field(content)  # NEW
}
```

**Auto-fix details**: See [SCORING.md](SCORING.md#auto-fix-mode) for complete workflow.

### Step 7: Generate Output (Mode-Aware)

**Output mode detection**:
- **Auto mode** (--mode=auto or called by /work-issue): Minimal 2-line output
- **Interactive mode** (direct invocation): Concise summary ≤20 lines

```python
# AI-EXECUTABLE
is_auto_mode = args.get('mode') == 'auto' or os.path.exists('.claude/.work-issue-state.json')

if is_auto_mode:
    print(f"✅ Plan evaluation: {total_score}/100 ({status})")
    print(f"Status: .claude/.eval-plan-status.json")
else:
    # Interactive mode - show concise summary
    print_concise_summary(scores, issues)
```

**Output formats**: See [SCORING.md](SCORING.md#output-formats) for detailed examples.

### Step 8: Task Updates

```python
# AI-EXECUTABLE
for task_id in task_ids:
    TaskUpdate(task_id, status="in_progress")
    # ... execute evaluation dimension ...
    TaskUpdate(task_id, status="completed")
```

## Workflow Steps

Copy this checklist when executing:

```
Task Progress:
- [ ] Step 1: Load plan file
- [ ] Step 2: Evaluate architecture alignment
- [ ] Step 3: Check acceptance criteria coverage
- [ ] Step 4: Validate task dependencies
- [ ] Step 5: Assess best practices
- [ ] Step 6: Check task clarity
- [ ] Step 6.5: Check version field (NEW)
- [ ] Step 7: Generate scored report
- [ ] Step 8: Write status file
- [ ] Step 9: Auto-fix minor issues (if --mode=auto and score ≥90)
- [ ] Step 10: Report results
```

Execute these steps in sequence using TaskCreate/TaskUpdate for progress tracking.

### Issue Number Detection (Multi-Strategy)

If no issue number was provided as argument, use the shared detector module:

```python
# AI-EXECUTABLE
import sys
sys.path.insert(0, '.claude/skills/_scripts')

from framework.issue_detector import detect_issue_number

# Auto-detect with all 4 strategies + validation
issue_num = detect_issue_number(check_github=True, required=True)
# Returns: int (issue number) or raises IssueDetectionError
```

**Detection strategies**: Branch name → Active plan → Worktree path → Ask user

## Integration with /work-issue

**Workflow:**
```
Phase 1: /start-issue #23 → Creates plan
Phase 1.5: /eval-plan → Automatic validation (THIS SKILL)
Checkpoint 1: Review eval results
  - Interactive mode: Always stop
  - Auto mode: Stop if score ≤ 90
Phase 2: /execute-plan #23 → Implementation
Phase 2.5: /review → Code validation
Checkpoint 2: Review quality
Phase 3: /finish-issue #23 → Ship
```

**Checkpoint behavior**: See [SCORING.md](SCORING.md#approval-thresholds) for approval criteria.

## Usage Examples

### Example 1: Excellent Plan (Score 95)
- All tasks specific and actionable
- Perfect layer separation (service → repository → tests)
- 100% acceptance criteria coverage
- Version field present in frontmatter
- **Result:** ✅ Approved immediately

### Example 2: Good Plan (Score 82)
- Good structure, minor gaps
- Task 2 unclear about service layer
- Missing error handling task
- Version field missing (auto-fixed in auto mode)
- **Result:** ⚠️ Approved with recommendations

### Example 3: Needs Work (Score 58)
- Vague tasks ("Fix authentication", "Add tests")
- No architecture guidance
- Can't verify criteria coverage
- **Result:** ❌ Rejected - needs revision

## Best Practices

1. **Run after /start-issue** - Validate auto-generated plans
2. **Fix recommendations** - Prevents rework during implementation
3. **Re-evaluate after edits** - Verify fixes improved score
4. **Trust the evaluation** - AI catches systematic issues humans miss
5. **Use in /work-issue** - Automatic integration recommended
6. **Ensure version fields** - All plans should have version in frontmatter

## Worktree Support

If the issue was started with `/start-issue` and a worktree was created, all operations MUST use the worktree path.

**Auto-Detection**: Read plan file to extract worktree path from metadata
**File Operations**: Always use absolute paths when worktree is detected
**Fallback**: Use current directory if no worktree path found

**See**: [WORKFLOW_PATTERNS.md](../WORKFLOW_PATTERNS.md) for complete worktree usage.

## Final Verification

**Critical checks before completion:**

```
- [ ] All 9 evaluation tasks completed (including version check)
- [ ] Score calculated (0-100)
- [ ] Status file written (.claude/.eval-plan-status.json)
- [ ] Status file has valid_until timestamp (90 min)
- [ ] Approval level determined (approved/needs_improvement/rejected)
- [ ] Version field checked
```

Missing items indicate incomplete evaluation.

## Related Documentation

- **[CHECKLIST.md](CHECKLIST.md)** - Detailed 5-dimension evaluation criteria and scoring rubrics
- **[SCORING.md](SCORING.md)** - Scoring algorithm, approval thresholds, status file format, and auto-fix mode
- **[VERSION_CHECK.md](VERSION_CHECK.md)** - Version field checking logic and implementation (Issue #401 feature)

## Related Skills

- **/start-issue** - Creates plan (run before this)
- **/auto-solve-issue** - Calls this skill automatically in Phase 1.5
- **/execute-plan** - Executes plan (run after this)
- **/review** - Validates code (Phase 2.5 - symmetric validation)

## Workflow Skills Requirements

This is a **workflow skill** and must follow the standard pattern:

1. **TaskCreate** at start - Create todo list for progress tracking
2. **TaskUpdate** during execution - Mark tasks in_progress → completed
3. **Verification checklist** - Final validation before completion

**See**: [WORKFLOW_PATTERNS.md](../WORKFLOW_PATTERNS.md) for complete implementation guide

---

**Version:** 1.4.1
**Pattern:** Analysis skill (validates before execution)
**Compliance:** ADR-001 ✅ | ADR-014 ✅ | ADR-016 ✅ | WORKFLOW_PATTERNS.md ✅
**Last Updated:** 2026-03-30
**Changelog:**
- v1.4.1: Use shared version.py module for version checking (Issue #406)
- v1.4.0: Split into modular docs (SKILL.md <500L, CHECKLIST.md, SCORING.md, VERSION_CHECK.md) - ADR-016 compliance (Issue #419)
- v1.3.0: Added mode-aware output (2 lines auto, ≤20 lines interactive) (Issue #263)
- v1.2.0: Added auto-fix mode for minor issues when score ≥90 (Issue #177)
- v1.0.0: Initial release with 5-dimension evaluation
