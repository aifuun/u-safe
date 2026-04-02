# Eval Plan - Scoring & Status

Scoring algorithm, approval thresholds, status file format, and auto-fix mode.

## Overview

This document describes how evaluation scores are calculated, how approval decisions are made, the status file format for integration with other skills, and the auto-fix mode for minor issues.

**Related**: See [SKILL.md](SKILL.md) for overview | [CHECKLIST.md](CHECKLIST.md) for evaluation criteria

---

## Scoring Algorithm

### Score Calculation

**Total Score** = Sum of 5 dimension scores (max 100 points)

```python
# AI-EXECUTABLE
scores = {
    "architecture": evaluate_architecture(plan, max=40),
    "coverage": evaluate_coverage(plan, issue, max=30),
    "dependencies": evaluate_dependencies(plan, max=15),
    "practices": evaluate_practices(plan, max=10),
    "clarity": evaluate_clarity(plan, max=5)
}

total_score = sum(scores.values())  # 0-100
```

**Dimension Weights**:
- Architecture: 40% (most critical - prevents costly rework)
- Coverage: 30% (ensures all requirements met)
- Dependencies: 15% (enables smooth execution)
- Practices: 10% (quality and maintainability)
- Clarity: 5% (execution ease)

### Score Interpretation

| Range | Status | Meaning |
|-------|--------|---------|
| **90-100** | ✅ Approved | Excellent plan, ready for implementation |
| **70-89** | ⚠️ Needs Improvement | Acceptable plan with recommendations |
| **<70** | ❌ Rejected | Critical issues, must fix before proceeding |

---

## Approval Thresholds

### ✅ Approved (Score > 90)

**Characteristics**:
- All dimensions strong (>80% of max)
- No blocking issues
- Minor suggestions only
- Ready for immediate implementation

**Auto Mode Behavior**: Proceed automatically to execute-plan

**Interactive Mode Behavior**: Show results, offer options:
- [C] Continue to execute-plan
- [E] Edit plan (optional improvements)
- [S] Stop here

**Example Output**:
```markdown
✅ Plan Approved: 95/100

Breakdown:
- Architecture: 40/40 ✅
- Coverage: 30/30 ✅
- Dependencies: 13/15 ⚠️ (minor: one task slightly out of order)
- Practices: 9/10 ✅
- Clarity: 3/5 ⚠️ (suggestion: clarify Task 3)

Next: /execute-plan #23
```

### ⚠️ Needs Improvement (Score 70-90)

**Characteristics**:
- Good foundation, some gaps
- Recommendations present (not blocking)
- Can proceed with awareness of issues
- May cause minor rework if not addressed

**Auto Mode Behavior**:
- If score ≥ 90: Proceed (with auto-fix if applicable)
- If score < 90: Stop at checkpoint, require manual decision

**Interactive Mode Behavior**: Always stop, show recommendations

**Example Output**:
```markdown
⚠️ Plan Needs Improvement: 82/100

Issues:
1. Task 5 - Architecture concern: API call in UI component
2. Missing - Best practice: No error handling task
3. Task 3 - Dependency issue: Test before implementation

Recommendations:
- Move API logic to service layer
- Add error handling strategy task
- Reorder: implement first, then test

Options:
[C] Continue anyway (may cause rework later)
[E] Edit plan (recommended)
[S] Stop here
```

### ❌ Rejected (Score < 70)

**Characteristics**:
- Critical issues present
- Multiple blocking problems
- High rework risk if proceeding
- Plan needs significant revision

**Both Modes Behavior**: Stop, require fixes before proceeding

**Example Output**:
```markdown
❌ Plan Rejected: 58/100

Critical Issues:
- Architecture: 15/40 ❌ Multiple layer violations
- Coverage: 12/30 ❌ 3 acceptance criteria unaddressed
- Dependencies: 3/15 ❌ Circular dependencies detected

This plan has critical issues that will cause significant rework.
Please revise the plan before implementation.

Next: Edit plan and re-evaluate
```

---

## Status File Format

### Purpose

`.claude/.eval-plan-status.json` enables integration with other skills (work-issue, auto-solve-issue) by providing machine-readable evaluation results.

### File Location

```
.claude/.eval-plan-status.json
```

**Note**: Written to main repo directory, not worktree (for cross-workflow access).

### Basic Format

```json
{
  "timestamp": "2026-03-30T10:30:00Z",
  "issue_number": 419,
  "issue_title": "Skill 2: eval-plan optimization",
  "plan_file": "/path/to/worktree/.claude/plans/active/issue-419-plan.md",
  "status": "approved",
  "score": 95,
  "breakdown": {
    "architecture": {
      "score": 40,
      "max": 40,
      "status": "pass"
    },
    "coverage": {
      "score": 30,
      "max": 30,
      "status": "pass"
    },
    "dependencies": {
      "score": 13,
      "max": 15,
      "status": "pass"
    },
    "practices": {
      "score": 8,
      "max": 10,
      "status": "pass"
    },
    "clarity": {
      "score": 4,
      "max": 5,
      "status": "pass"
    }
  },
  "issues_count": {
    "blocking": 0,
    "recommendations": 2,
    "suggestions": 3
  },
  "valid_until": "2026-03-30T12:00:00Z"
}
```

### Extended Format (with Auto-Fix)

When auto-fix is applied:

```json
{
  "timestamp": "2026-03-30T10:30:00Z",
  "issue_number": 419,
  "status": "approved",
  "score": 95,
  "score_before_autofix": 92,
  "auto_fixes_applied": [
    {
      "type": "format_issue",
      "task": "Task numbering",
      "description": "Renumbered tasks 1,2,4,5 → 1,2,3,4",
      "before": "Gap in task numbering",
      "after": "Sequential numbering"
    },
    {
      "type": "version_missing",
      "description": "Added version: \"2.0\" to plan frontmatter"
    }
  ],
  "breakdown": { "..." },
  "issues_count": {
    "blocking": 0,
    "recommendations": 0,
    "suggestions": 1
  }
}
```

### Validity

Status files are valid for **90 minutes** from evaluation timestamp.

**Rationale**: Plans can become stale if code/requirements change. Re-evaluation recommended after 90 minutes.

**Check validity**:
```python
# AI-EXECUTABLE
from datetime import datetime

def is_status_valid(status_file):
    with open(status_file) as f:
        status = json.load(f)

    valid_until = datetime.fromisoformat(status["valid_until"])
    return datetime.now() < valid_until
```

---

## Auto-Fix Mode

**Purpose**: Automatically fix minor issues when score ≥90 in `--mode=auto`, enabling seamless continuation to execute-plan.

### When Auto-Fix Triggers

Conditions (ALL must be true):
1. Mode is `--mode=auto` (set by work-issue --auto or auto-solve-issue)
2. Score ≥ 90 (passing threshold)
3. Issues are classified as "minor" (auto-fixable)

### Auto-Fixable Issue Types

| Issue Type | Description | Example Fix |
|------------|-------------|-------------|
| **missing_todo** | Task mentions TODO but no TODO comment | Add `<!-- TODO: ... -->` comment |
| **incomplete_test** | "Add tests" without specifics | Expand: "Add unit tests (80% coverage): normal case, error case, edge cases" |
| **format_issue** | Task numbering gaps, inconsistent formatting | Renumber tasks 1→2→4→5 to 1→2→3→4 |
| **missing_file_ref** | "Update SKILL.md" without path | Add full path: `.claude/skills/eval-plan/SKILL.md` |
| **logic_gap** | Missing obvious steps between tasks | Insert missing intermediate task |
| **version_missing** | Plan frontmatter missing version field | Add `version: "2.0"` to YAML frontmatter |

### Non-Auto-Fixable Issues

These require manual review (stop at checkpoint):

- **architecture_violation** - Requires redesign
- **missing_acceptance_criteria** - Requires PO/user input
- **circular_dependency** - Requires re-planning
- **security_issue** - Requires expert review
- **performance_concern** - Requires benchmarking

### Auto-Fix Workflow

```
1. eval-plan runs → Score = 92/100
2. Detect mode = auto (from --mode=auto argument)
3. Score ≥ 90 → Trigger auto-fix
4. Classify issues:
   - 2 × missing_todo → AUTO-FIX
   - 1 × format_issue → AUTO-FIX
   - 1 × suggestion (non-blocking) → SKIP
5. Apply fixes to plan file
6. Re-evaluate → New score = 95/100
7. Write status file with fix log
8. Report auto-fixes to user
9. Continue to execute-plan (seamless)
```

### Implementation

```python
# AI-EXECUTABLE
def auto_fix_if_applicable(mode, score, issues, plan_content, plan_file):
    """
    自动修复微小问题（仅在 auto 模式且分数 ≥90 时）
    """
    # 检查是否启用自动修复
    if mode != "auto" or score < 90:
        return plan_content, [], score  # 不修复

    # 分类问题
    minor_issues = [i for i in issues if i.category in AUTO_FIXABLE]

    if not minor_issues:
        return plan_content, [], score  # 无需修复

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

        # 重新评估
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
    "version_missing"
}

FIXERS = {
    "missing_todo": lambda content, issue: add_todo_comment(content, issue),
    "incomplete_test": lambda content, issue: expand_test_description(content, issue),
    "format_issue": lambda content, issue: fix_task_numbering(content),
    "missing_file_ref": lambda content, issue: add_file_path(content, issue),
    "logic_gap": lambda content, issue: insert_missing_step(content, issue),
    "version_missing": lambda content, issue: add_version_field(content)
}
```

### Graceful Degradation

If auto-fix fails:
```python
# AI-EXECUTABLE
try:
    fixed_content, fixes = auto_fix_plan(content, issues)
    write_plan(fixed_content)
except AutoFixError as e:
    log.error(f"Auto-fix failed: {e}")
    # Fall back to interactive mode
    return prompt_user_checkpoint()
```

Fallback behavior:
- Show original evaluation results
- Prompt user for action (continue/edit/stop)
- Preserve original plan file
- Log failure reason

### Performance Impact

- **Auto-fix time**: < 10 seconds
- **Total eval-plan time**: 40-70 seconds (was 30-60 seconds)
- **Value**: +10 seconds overhead, saves 5-60 minutes of manual editing

---

## Output Formats

### Auto Mode Output (2 lines)

When called by `/auto-solve-issue` or with `--mode=auto`:

```
✅ Plan evaluation: 95/100 (approved)
Status: .claude/.eval-plan-status.json
```

### Interactive Mode Output (≤20 lines)

When called directly by user:

```markdown
# Plan Evaluation: Issue #419

Score: 95/100 (approved)
Issues: 0 blocking, 2 recommendations

Breakdown:
- Architecture: 40/40 ✅
- Coverage: 30/30 ✅
- Dependencies: 13/15 ⚠️
- Practices: 8/10 ✅
- Clarity: 4/5 ✅

Recommendations:
1. Task 3 - Add file path for clarity
2. Consider splitting Task 5 into subtasks

Status file: .claude/.eval-plan-status.json
Next: /execute-plan #419
```

### JSON Output (for automation)

With `--json` flag:

```json
{
  "timestamp": "2026-03-30T10:30:00Z",
  "issue_number": 419,
  "status": "approved",
  "score": 95,
  "breakdown": { "..." },
  "issues": {
    "blocking": [],
    "recommendations": [
      {
        "task": "Task 3",
        "category": "clarity",
        "description": "Missing file path",
        "fix": "Add `.claude/skills/eval-plan/SKILL.md`",
        "impact": "low"
      }
    ],
    "suggestions": []
  },
  "strengths": [
    "Perfect architecture alignment",
    "100% acceptance criteria coverage",
    "Clear task breakdown"
  ],
  "metrics": {
    "total_tasks": 3,
    "acceptance_criteria": 5,
    "coverage_percentage": 100,
    "estimated_complexity": "low"
  }
}
```

---

## Integration Points

### /work-issue Integration

```
Phase 1: /start-issue → Creates plan
Phase 1.5: /eval-plan → Validation (THIS SKILL)
Checkpoint 1:
  - Auto mode: Continue if score ≥ 90, stop if < 90
  - Interactive mode: Always stop, show results
Phase 2: /execute-plan → Implementation
```

### /auto-solve-issue Integration

```
Task 2 (Phase 1.5): eval-plan
- Runs with --mode=auto
- Auto-fixes minor issues if score ≥ 90
- Continues seamlessly to Phase 2 if approved
- Stops at checkpoint if score < 90
```

### Status File Usage

Other skills read `.claude/.eval-plan-status.json`:

```python
# AI-EXECUTABLE
def check_plan_approved(issue_num):
    status_file = ".claude/.eval-plan-status.json"

    with open(status_file) as f:
        status = json.load(f)

    # Verify it's for the correct issue
    if status["issue_number"] != issue_num:
        return False, "Status file is for different issue"

    # Check validity
    if not is_status_valid(status):
        return False, "Status file expired (>90 min old)"

    # Check approval
    if status["status"] != "approved":
        return False, f"Plan status: {status['status']} (score: {status['score']})"

    return True, f"Plan approved (score: {status['score']})"
```

---

## Summary

**Scoring**: 5 dimensions, 100 points total, weighted by importance

**Approval Thresholds**:
- ≥90: ✅ Approved (proceed automatically in auto mode)
- 70-89: ⚠️ Needs Improvement (stop at checkpoint)
- <70: ❌ Rejected (must fix)

**Status File**: `.claude/.eval-plan-status.json` (valid for 90 minutes)

**Auto-Fix**: Fixes minor issues when score ≥90 in auto mode

**Output Modes**:
- Auto: 2 lines
- Interactive: ≤20 lines
- JSON: Full detail

**See Also**:
- [SKILL.md](SKILL.md) - Skill overview and usage
- [CHECKLIST.md](CHECKLIST.md) - Detailed evaluation criteria
- [VERSION_CHECK.md](VERSION_CHECK.md) - Version field validation

---

**Version:** 1.0.0
**Last Updated:** 2026-03-30
**Part of**: eval-plan skill (v1.4.0)
**Compliance:** ADR-016 ✅ (modular documentation)
