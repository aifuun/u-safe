---
name: finish-issue
description: |
  Complete issue workflow - commit, PR, merge, close, cleanup.
version: "3.1.0"

  TRIGGER when: User wants to complete/finish an issue ("finish issue #23", "complete issue", "merge and close", "done with issue").

  DO NOT TRIGGER when: User just wants to create issues (use /start-issue), review code (use /review), or manually commit changes.
user-invocable: true
argument-hint: "[issue-number] [--keep-branch] [--no-merge] [--dry-run] [--force]"
context: fork
---

# Finish Issue - Complete Issue Lifecycle

> Automates the final phase: commit, PR, merge, close, and cleanup

## Overview

This skill completes the issue lifecycle by automating 8 final steps:

**What it does:**
1. **Pre-Finish Validation** - Quality gates (tests, linting, review status)
2. **Commit & Push** - Commits all changes with semantic message including issue reference
3. **Create PR** - Generates pull request with issue context
4. **Merge PR** - Merges after checks pass (optional)
5. **Generate Summary** - Creates comprehensive completion summary with commits, stats, review scores
6. **Post Summary Comment** - Adds summary to issue before closing
7. **Close Issue** - Marks issue as done on GitHub
8. **Cleanup** - Deletes branches and temporary files

**Why it's needed:**
Manually finishing an issue requires 10+ commands (git, gh CLI) and takes 5-10 minutes. This skill automates everything in ~2 minutes with built-in safety checks.

**When to use:**
- After completing implementation and code review
- Ready to merge your feature branch
- Want automated PR creation and merging

**Usage:**
- **Primary (Recommended)**: Say "finish issue #97" - Claude orchestrates the complete workflow
- **Alternative**: Run `python .claude/skills/finish-issue/scripts/finish.py 97` for direct script execution
- **Manual**: Execute individual git/gh commands for full control (see Workflow Steps)

## Arguments

```bash
/finish-issue [issue-number] [options]
```

**Common usage:**
```bash
/finish-issue              # Auto-detect from branch
/finish-issue 97           # Specific issue
/finish-issue 97 --dry-run # Preview without executing
```

**Options:**
- `[issue-number]` - Optional, auto-detected from branch if omitted
- `--keep-branch` - Don't delete branch after merge
- `--no-merge` - Create PR but don't auto-merge
- `--dry-run` - Show what would happen without executing
- `--force` - Skip validation checks (use cautiously)

## Safety Features

This skill includes comprehensive safety mechanisms to prevent accidental damage during issue completion:

### 1. Pre-Finish Validation

**What it checks:**
- Review status exists and is valid (score ≥ 90 recommended)
- Not on main branch (must be on feature branch)
- No uncommitted changes (all work committed)
- Tests passing (if test suite exists)
- Branch synced with main (no merge conflicts)

**Why it matters:**
- Prevents merging untested code
- Ensures quality gates passed
- Avoids losing uncommitted work
- Reduces merge conflict risks

**On failure:**
```
❌ Pre-finish validation failed

Issues:
- No review status (run /review first)
- 3 uncommitted files (commit before finishing)
- 2 tests failing (fix tests before merge)

Fix: Address issues above, then retry /finish-issue
```

### 2. Commit Safety

**What it checks:**
- Commit message format (semantic commit with issue reference)
- All changed files staged (no forgotten files)
- Commit includes "Fixes #N" footer (auto-closes issue)
- Co-authored-by attribution present

**Why it matters:**
- Ensures consistent commit history
- Enables automatic issue closing
- Provides proper attribution
- Makes commits searchable

**On failure:**
```
⚠️ Commit validation warning

- Commit message missing "Fixes #511"
- 1 file not staged: .claude/plans/active/issue-511-plan.md

Action: Auto-correcting commit message and staging files
```

### 3. PR Creation Validation

**What it checks:**
- Issue body accessible (for PR description)
- Branch pushed to remote
- No existing PR for this branch
- PR title includes issue reference

**Why it matters:**
- Prevents duplicate PRs
- Ensures PR properly linked to issue
- Provides context in PR description

**On failure:**
```
❌ PR creation failed

Error: PR already exists for this branch
Existing PR: #534

Options:
1. View PR: gh pr view 534
2. Continue with existing PR
3. Close old PR and create new one
```

### 4. Merge Safety

**What it checks:**
- All PR checks passing (CI/CD, required reviews)
- Branch up-to-date with main
- Squash merge strategy (clean history)
- Branch deletion after merge

**Why it matters:**
- Prevents merging broken code
- Ensures linear git history
- Cleans up remote branches

**On failure:**
```
❌ Merge blocked

Checks failing:
- CI build failed (fix build errors)
- 1 required review missing (request review)

Fix: Address check failures, then retry merge
```

### 5. Cleanup Safety

**What it checks:**
- Worktree removed successfully (no orphaned directories)
- Local branch deleted
- Status files cleaned (.eval-plan-status.json, .review-status.json)
- Back on main branch and up-to-date

**Why it matters:**
- Prevents disk accumulation
- Avoids state confusion
- Ensures clean working environment

**On failure:**
```
⚠️ Cleanup incomplete

Issues:
- Worktree has uncommitted files (forcing removal)
- Local branch deletion failed (branch protected)

Action: Manual cleanup may be required
Command: git worktree remove --force {path}
```

### Safety Override

Use `--force` flag to bypass safety checks:

```bash
/finish-issue #511 --force  # Skips validation
```

**Warning:** Only use --force when you understand the risks:
- May merge untested/unreviewed code
- May create duplicate PRs
- May skip quality gates
- May leave cleanup incomplete

**Recommended approach:** Fix the safety issue instead:
```bash
# Instead of --force, fix the issue:
/review                    # Run quality check
git add . && git commit    # Commit uncommitted changes
/finish-issue #511         # Now safe to proceed
```

## AI Execution Instructions

**CRITICAL: Immediate Issue Detection**

When `/finish-issue` is invoked, AI MUST follow this pattern:

### Step 1: Detect Issue Number Immediately

**Before creating any tasks or introducing the skill**, determine which issue to finish:

```python
# Priority 1: Check if issue number provided as argument
if args:
    issue_num = args  # Use explicit argument
else:
    # Priority 2: Check conversation context/memory for active issue
    # Look for recently mentioned issue numbers in conversation
    # Example patterns to detect:
    # - "issue #158"
    # - "working on issue 158"
    # - "just completed #158"
    # - Recent /start-issue, /execute-plan, /review commands with issue number

    if issue_in_context:
        issue_num = detected_issue_from_context
    else:
        # Priority 3: Use issue detector (branch name, active plan, worktree)
        try:
            import sys
            sys.path.insert(0, '.claude/skills/_scripts')
            from framework.issue_detector import detect_issue_number
            issue_num = detect_issue_number(check_github=True, required=False)
        except:
            issue_num = None

        # Priority 4: Ask user if all detection fails
        if not issue_num:
            issue_num = AskUserQuestion(
                questions=[{
                    "question": "Which issue should I finish?",
                    "header": "Issue Number",
                    "options": [
                        {"label": "Enter manually", "description": "Type the issue number"}
                    ],
                    "multiSelect": false
                }]
            )
```

**What NOT to do:**
- ❌ Don't introduce the skill with overview text
- ❌ Don't show "Complete issue workflow - commit, PR, merge..." preamble
- ❌ Don't wait for user to specify issue if context already has it

**Expected behavior:**
1. Skill invoked → Immediately detect issue number
2. If recent context mentions issue (like issue #158 just worked on) → Use it
3. If no context → Try auto-detection from branch/plan
4. If detection fails → Ask user "Which issue should I finish?"
5. Once issue number determined → Create tasks and execute

### Step 2: Create Task List and Execute

**After** issue number is determined, proceed with normal workflow:

## Output Strategy (Mode-Aware)

**Output adapts based on mode:**

### Auto Mode Output (2 lines)

When called by `/auto-solve-issue`:

```
✅ Issue #{issue_number} finished | PR #{pr_number} merged
Cleanup: Branch deleted, worktree removed, status files cleared
```

### Interactive Mode Output (≤20 lines)

When called directly by user:

```markdown
🎉 Issue #{issue_number} Complete!

✅ Committed and pushed
✅ PR #{pr_number} created and merged
✅ Issue closed on GitHub
✅ Branch deleted
✅ Worktree removed
✅ Status files cleaned

Back on: main branch (up to date)
```

## Workflow Steps (AI Orchestration)

Copy this checklist when executing:

```
Task Progress:
- [ ] Step 1: Pre-Finish Validation
- [ ] Step 2: Commit & Push
- [ ] Step 3: Create Pull Request
- [ ] Step 4: Merge Pull Request
- [ ] Step 5: Generate Summary Comment
- [ ] Step 6: Post Summary to Issue
- [ ] Step 7: Close Issue
- [ ] Step 8: Cleanup
```

Execute these steps in sequence using the Python script or manual commands.

### Step 0: Issue Number Detection (Multi-Strategy)

If no issue number was provided as argument, use the shared detector module:

**Using the detector:**
```python
import sys
sys.path.insert(0, '.claude/skills/_scripts')

from framework.issue_detector import detect_issue_number

# Auto-detect with all 4 strategies + validation
issue_num = detect_issue_number(check_github=True, required=True)
# Returns: int (issue number) or raises IssueDetectionError
```

**Detection strategies (automatic, in order):**
1. **Extract from branch name** - `feature/137-python-shared-libs` → `137`
2. **Find single active plan** - If exactly 1 plan in `.claude/plans/active/`
3. **Extract from worktree path** - `ai-dev-137-python-shared-libs` → `137`
4. **Ask user** - Fallback prompt if all auto-detection fails

**Python script integration:**
The `finish.py` script now uses the shared detector instead of its own `extract_issue_number()` function:
```bash
# Auto-detect (recommended)
python .claude/skills/finish-issue/scripts/finish.py

# Explicit issue number (still supported)
python .claude/skills/finish-issue/scripts/finish.py 137
```

**For AI orchestration:**
When the user provides no issue number:
```markdown
1. Call detector: python -c "import sys; sys.path.insert(0, '.claude/skills/_scripts'); from framework.issue_detector import detect_issue_number; print(detect_issue_number())"
2. Capture issue number from output
3. If detection fails and user input needed:
   - Use AskUserQuestion tool to ask for issue number
   - Validate issue exists on GitHub: gh issue view {N}
4. Continue with detected/provided issue number
```

### Step 1: Pre-Finish Validation

Validates quality gates: review status exists (score ≥90 recommended), not on main branch, no uncommitted changes, tests passing (if applicable), branch synced with main. If validation fails, commit changes, run `/review`, or sync branch before proceeding.

### Step 2: Commit & Push

Commits all changes with semantic message including issue reference. The commit message must include `(Issue #N)` in the title and `Fixes #N` in the footer to auto-link and auto-close the issue when merged.

**Format:** `<type>: <description> (Issue #N)\n\n<details>\n\nFixes #N\n\nCo-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`

### Step 3: Create Pull Request

Creates PR with issue number in title, summary section, changes description, and Claude Code attribution. Use `gh pr create` with heredoc for body content.

### Step 4: Merge Pull Request

Merges PR with squash strategy for clean history. Use `gh pr merge --squash --delete-branch`. Branch deletion is automatic unless `--keep-branch` flag is used.

### Step 5: Generate Summary Comment

**Create human-friendly completion summary:**

Uses `formatter.py` to generate standardized, business-focused output with 4 main sections:

```python
from formatter import HumanReadableSummary

def generate_issue_summary(issue_number: int, branch_name: str) -> str:
    """生成人类友好的 issue 完成总结

    Extracts information from multiple sources:
    - Issue body: Why (background/problem)
    - Plan file: What (main changes), Achievements (acceptance criteria)
    - Review data: Notes (recommendations)
    - Git history: Technical metrics

    Returns: Human-readable markdown focused on business value
    """
    # Gather raw data
    issue_data = get_issue_details(issue_number)
    commits = get_commits(branch_name)
    plan_content = read_plan_file(issue_number)
    review_data = load_review_status()

    # Use formatter to generate summary
    summary = HumanReadableSummary.from_issue_data(
        issue_number=issue_number,
        issue_title=issue_data['title'],
        issue_body=issue_data['body'],
        commits=commits,
        plan_content=plan_content,
        review_data=review_data,
        files_changed=count_files_changed(),
        lines_summary=get_lines_summary(),
        duration=calculate_duration(),
        issue_url=issue_data['url'],
        pr_number=get_pr_number(branch_name)
    )

    return summary.format_output()
```

**Output format (4 sections):**

1. **💡 实现原因 (Why)** - Business problem/background from issue body
2. **✨ 主要改动 (What)** - 3-5 core changes from plan/commits
3. **🎯 实现功能 (Achievements)** - Features delivered (acceptance criteria)
4. **⚠️ 注意事项 (Notes)** - Warnings, breaking changes, follow-ups

Plus one-line technical metrics: `📊 质量：92/100 | 3 commits | 8 files (+245/-120)`

**Information extraction:**
- **Why**: Regex extracts `## 背景` or `## 问题` from issue body; fallback to first paragraph
- **What**: Parses `### Part N:` structure from plan; fallback to commit messages
- **Achievements**: Extracts completed items from `## 验收标准` section
- **Notes**: Combines review recommendations (severity >= warning) + plan technical points

**Why this format:**
- Focuses on business value, not technical details
- Easy for stakeholders to understand completion status
- Consistent format across all issues
- Technical metrics condensed to single line

### Step 6: Post Summary to Issue

Posts human-friendly completion summary as issue comment before closing. Uses the standardized 4-section format (Why/What/Achievements/Notes) generated by `formatter.py`.

**Example summary (Issue #558):**
```markdown
🎉 Issue #558 完成：改进 sync skill commit 消息质量和简化实现

## 💡 实现原因

当前 /sync skill 的 commit 消息过于通用，缺乏具体信息：
- Auto-commit 缺少文件列表和原因
- Merge 未指明具体分支
- Conflict 未说明冲突文件和策略

这导致 Git history 可读性差，无法从历史记录了解具体变更，调试困难。
同时 SKILL.md 476 行过于复杂，需要简化。

## ✨ 主要改动

- Part 1: Commit 消息增强 - Auto-commit 现在包含文件列表、分支名、原因说明
- Part 1: Merge 消息包含具体分支名、commit 数量、最近 5 个 commits
- Part 1: Conflict 消息包含冲突文件列表、解决策略
- Part 2: SKILL.md 从 501 行精简到 275 行（减少 45%）
- Part 2: 冲突处理拆分到 CONFLICT-HANDLING.md（162 行）

## 🎯 实现功能

- Git history 现在可以直接看懂每个 commit 做了什么
- Commit 消息自动包含关键上下文信息
- 文档结构清晰，核心流程和详细指南分离
- 新用户快速上手（核心文档 < 300 行）
- 验收标准：11/12 完成（92%）

## ⚠️ 注意事项

- 新的 commit 消息格式需要 bash 变量捕获，确保 shell 环境支持
- 如果生成失败，会降级到简单格式（向后兼容）
- CONFLICT-HANDLING.md 和 SYNC-STRATEGIES.md 是可选文档

---
📊 质量：94/100 | 1 commit | 4 files (+852/-718)
🔗 Issue #558 | PR #559 | 用时：2小时
```

**What changed:**
- Old format: Technical focus (commits, files, test coverage)
- New format: Business focus (why, what, achievements, notes)
- Technical metrics compressed to 1 line
- Easier for stakeholders to understand value delivered

### Step 7: Close Issue

Closes issue with `gh issue close {N}`. Summary was already posted in Step 6, so no additional comment needed.

### Step 8: Cleanup

Cleans up environment: switches to main branch, pulls latest changes, **archives plan file** (moves to `.claude/plans/archive/`, do NOT delete), deletes workflow state files (`.work-issue-state.json`, `.eval-plan-status.json`, `.review-status.json`), removes worktree directory (if used), and deletes all issue-related tasks/todos.

**AI Orchestration cleanup:** Use `shutil.move()` to archive plan file to `.claude/plans/archive/` (do NOT delete). Use `TaskList()` and `TaskUpdate(status="deleted")` to clean up all issue-related tasks/todos.

## Task Management (AI Orchestration)

Create 8 tasks at start (validation, commit, PR, merge, summary gen, post summary, close, cleanup). Use `TaskUpdate()` to mark each `in_progress` before execution and `completed` after. Final verification: all tasks completed, PR merged, issue closed, branches cleaned, state files deleted, todos deleted, on main branch.

## Usage Modes

This skill supports three execution modes, with **AI Orchestration** as the primary recommended approach:

### Primary: AI Orchestration (Recommended)

**Tell Claude to finish:**

```
User: "finish issue #97"

Claude:
1. Creates task list (6 tasks)
2. Calls: python finish.py 97
3. Updates tasks as script executes
4. Reports completion
```

**When to use:**
- Prefer conversational interface
- Want progress tracking
- Claude handles errors

## Error Handling

**Common errors:** Not on feature branch (checkout feature branch first), uncommitted changes (commit before finishing), no review status (run `/review` or use `--force`), PR already exists (check `gh pr list` and merge manually), merge conflicts (sync with main and resolve). Summary generation/posting failures use graceful degradation: skip optional summary, continue to close issue, allow manual summary addition.

## Usage Examples

### Example 1: Basic Finish (Happy Path)

**User says:**
> "finish issue #97"

**What happens:**
1. **Pre-finish validation** - Checks review status, tests passing, no uncommitted changes
2. **Commit changes** - Semantic commit with "Fixes #97" footer
3. **Create PR** - Generates PR with issue context, summary, test results
4. **Merge PR** - Squash merge to main, deletes remote branch
5. **Post summary** - Adds completion summary to issue (commits, files, review score)
6. **Close issue** - Marks issue as closed on GitHub
7. **Cleanup** - Removes worktree, deletes local branch, cleans status files
8. **Return to main** - Switches to main branch, pulls latest

**Output:**
```
✅ Issue #97 finished successfully

Commits: 1 commit
PR: #534 (merged)
Review score: 92/100

Cleanup complete:
- Worktree removed
- Branch deleted
- Status files cleaned

Back on: main branch
```

**Time:** ~2-3 minutes

### Example 2: Dry Run Preview

**User says:**
> "show me what would happen if I finish issue #97, but don't actually do it"

**What happens:**
1. **Load plan and review status**
2. **Preview all 8 steps** without executing:
   ```
   DRY RUN MODE - No changes will be made

   Step 1: Commit changes
     Files: .claude/skills/finish-issue/SKILL.md
     Message: "docs(finish-issue): add Safety Features and Usage Examples"

   Step 2: Create PR
     Title: "docs: finish-issue 文档重构（ADR-020 合规）"
     Body: [Summary of changes...]

   Step 3: Merge PR
     Strategy: Squash merge
     Delete branch: Yes

   Step 4-8: [Summary, Close, Cleanup...]

   To execute: /finish-issue #97 (without --dry-run)
   ```

**Time:** <10 seconds

### Example 3: Error Handling (Validation Failure)

**User says:**
> "finish issue #97"

**What happens:**
```
❌ Pre-finish validation failed

Issues found:
1. No review status found
   - Run: /review
   - Or use: /finish-issue #97 --force (not recommended)

2. Uncommitted changes detected
   - Files: .claude/skills/finish-issue/SKILL.md
   - Action: Commit changes before finishing

3. Tests failing (2/10 passing)
   - Failed: test_validation, test_cleanup
   - Fix tests before merge

Fix these issues, then retry /finish-issue #97
```

**User fixes issues:**
```bash
# Fix tests
npm test  # All passing ✅

# Commit changes
git add .
git commit -m "fix: resolve test failures"

# Run review
/review  # Score: 92/100 ✅

# Retry finish
/finish-issue #97  # Now succeeds ✅
```

**Outcome:** All validation checks pass, issue finishes successfully

**Time:** 5-10 minutes (including fixes)

**Key insight:** Safety checks prevent merging broken code. Fix issues instead of using --force.

## Integration

**Workflow sequence:**
```
/start-issue #97    → Branch + plan
/execute-plan #97   → Implementation
/review             → Quality check
/finish-issue #97   → Merge + close (THIS SKILL)
```

**Or complete lifecycle:**
```
/work-issue #97
  → Calls /start-issue
  → Calls /eval-plan
  → Calls /execute-plan
  → Calls /review
  → Calls /finish-issue (automatic)
```

## Best Practices

1. **Always review first** - Run `/review` before finishing
2. **Check dry-run** - Preview with `--dry-run` if unsure
3. **Sync before finish** - Run `/sync` to avoid conflicts
4. **Trust validation** - Fix issues instead of using `--force`
5. **Use auto-detect** - Let script infer issue from branch

## Performance

- **Validation**: <5 seconds
- **Commit + Push**: ~10 seconds
- **PR creation**: ~5 seconds
- **Merge**: ~30 seconds
- **Cleanup**: ~5 seconds
- **Total**: ~1-2 minutes

Fast because:
- Automated validation (no manual checks)
- Parallel GitHub operations
- Efficient git commands

## Worktree Support

If worktree was created by `/start-issue`, extract worktree path from plan metadata (`**Worktree**: ...`). All git operations must use `-C` flag (e.g., `git -C ${WORKTREE_PATH} status`). After closing issue, remove worktree with `git worktree remove ${WORKTREE_PATH}`, delete local branch, switch to main, and pull latest. Falls back to standard git commands if no worktree path found.

---

## Testing

This skill has comprehensive test coverage following ADR-020 standards.

### Test Suite Overview

**Location**: `.claude/skills/finish-issue/tests/`

**Coverage**: 80%+ (ADR-015 requirement)

**Test Files**:
- `test_detection.py` (8 tests) - Issue number detection strategies
- `test_worktree.py` (7 tests) - Worktree handling and cleanup
- `test_validation.py` (7 tests) - Pre-finish validation checks
- `test_safety.py` (15 tests) - All 5 safety mechanisms
- `test_examples.py` (12 tests) - Usage examples from SKILL.md
- `test_workflow.py` (9 tests) - End-to-end integration tests

**Total**: 58 tests across 6 categories

### Running Tests

```bash
# Navigate to skill directory
cd .claude/skills/finish-issue

# Activate virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r tests/requirements.txt

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov --cov-report=term-missing

# Run specific category
pytest tests/ -m unit          # Unit tests only
pytest tests/ -m integration   # Integration tests only
pytest tests/ -m safety        # Safety mechanism tests
pytest tests/ -m examples      # Usage example tests

# Run specific file
pytest tests/test_detection.py
pytest tests/test_safety.py
```

### Test Categories

Tests are organized with pytest markers:

| Marker | Count | Purpose |
|--------|-------|---------|
| `unit` | 22 | Unit tests for individual functions |
| `integration` | 9 | End-to-end workflow tests |
| `safety` | 15 | Safety mechanism validation |
| `examples` | 12 | Usage examples from docs |

### Coverage Requirements

- **Minimum**: 80% (ADR-015 standard)
- **Target**: 90%+
- **Fails CI if**: Coverage < 80%

Check coverage:
```bash
pytest tests/ --cov --cov-report=html
open htmlcov/index.html
```

### Adding New Tests

When adding new functionality:

1. **Create test file** in `tests/` (follow `test_*.py` naming)
2. **Add marker** from conftest.py (`@pytest.mark.unit`, `@pytest.mark.integration`, etc.)
3. **Use fixtures** from `conftest.py` for setup
4. **Follow ADR-020** - tests should map to SKILL.md sections
5. **Run coverage** - ensure new code is covered

Example test structure:
```python
import pytest

@pytest.mark.unit
class TestNewFeature:
    def test_feature_behavior(self, temp_worktree):
        """Test description matching SKILL.md section."""
        # Arrange
        setup_data = prepare_test_data()

        # Act
        result = execute_feature(setup_data)

        # Assert
        assert result == expected_output
```

### Continuous Integration

Tests run automatically on:
- Every PR to main branch
- Every commit to feature branches
- Manual workflow dispatch

CI configuration: `.github/workflows/test-finish-issue.yml`

---

## Final Verification

**Critical checks before completion:**

```
- [ ] Plan file archived (not deleted) to .claude/plans/archive/
- [ ] All 3 state files deleted (.work-issue-state, .eval-plan-status, .review-status)
- [ ] All todos cleaned up (TaskUpdate status="deleted")
- [ ] Worktree removed (if used)
- [ ] On main branch and up to date
```

Missing items indicate incomplete cleanup.

## Workflow Skills Requirements

This is a **workflow skill** and must follow the standard pattern:

1. **TaskCreate** at start - Create todo list for progress tracking
2. **TaskUpdate** during execution - Mark tasks in_progress → completed
3. **Verification checklist** - Final validation before completion

**See**: [WORKFLOW_PATTERNS.md](../WORKFLOW_PATTERNS.md) for complete implementation guide

---

## Related Skills

- **/start-issue** - Phase 1: Begin issue workflow
- **/eval-plan** - Phase 1.5: Validate plan
- **/execute-plan** - Phase 2: Implementation
- **/review** - Phase 2.5: Quality check
- **/auto-solve-issue** - Complete lifecycle (calls this skill)
- **/sync** - Sync branch with main

---

**Version:** 3.2.0
**Pattern:** Workflow Orchestrator (AI-guided + Script)
**Compliance:** ADR-001 ✅ | ADR-003 ✅ | WORKFLOW_PATTERNS ✅
**Last Updated:** 2026-03-18
**Changelog:**
- v3.1.0: Added mode-aware output (2 lines auto, ≤20 lines interactive) (Issue #263)
- v3.0.0: Complete rewrite with Python script + AI orchestration
- v2.0.0: Added workflow pattern compliance
- v1.0.0: Initial release
