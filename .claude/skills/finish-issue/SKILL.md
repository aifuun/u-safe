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

**Create comprehensive completion summary:**

```python
def generate_issue_summary(issue_number: int, branch_name: str) -> str:
    """
    生成 issue 完成总结内容

    Returns: Formatted markdown string
    """
    # 1. 提取 commits 列表 (from origin/main to current branch)
    commits = Bash(f'git log origin/main..HEAD --oneline')
    commit_count = len(commits.split('\n'))

    # 2. 提取变更文件统计
    diff_stat = Bash(f'git diff origin/main..HEAD --stat')

    # 3. 读取 review 分数（如果存在）
    review_score = None
    try:
        with open('.claude/.review-status.json', 'r') as f:
            review_data = json.load(f)
            review_score = review_data.get('score')
    except:
        pass

    # 4. 提取 PR 编号 (from gh pr list or recent PR)
    pr_number = extract_pr_number_from_branch(branch_name)

    # 5. 格式化 markdown
    return f"""## ✅ Issue 完成总结

**分支**: {branch_name}
**PR**: #{pr_number}
**完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

### Commits 列表

{commits}

**总计**: {commit_count} commits

### 变更文件

{diff_stat}

### 代码质量

{format_review_score(review_score) if review_score else 'No review data'}

---

🤖 Generated by [Claude Code](https://claude.com/claude-code) via `/finish-issue`
"""
```

**Summary includes:**
- Branch name and PR number
- Complete commits list with hashes and messages
- File change statistics (additions/deletions)
- Code review score (if /review was run)
- Timestamp of completion

**Why this step:**
- Provides permanent record of what was done
- Easy to reference later (no need to check PR/commits)
- Shows testing and quality metrics
- Documents completion context

### Step 6: Post Summary to Issue

Posts comprehensive completion summary as issue comment before closing. Use `gh issue comment` with heredoc to avoid special character issues. Summary includes branch name, PR number, commits list, file changes, and review score.

**Example summary:**
```markdown
## ✅ Issue 完成总结

**分支**: feature/97-implement-auth
**PR**: #109
**完成时间**: 2026-03-23 15:30

### Commits 列表

a1b2c3d feat: add OAuth2 login flow
e4f5g6h feat: implement logout endpoint
i7j8k9l docs: update authentication guide

**总计**: 3 commits

### 变更文件

 src/auth/login.ts     | 45 +++++++++++++++++++++++++
 src/auth/logout.ts    | 28 +++++++++++++++
 docs/AUTH.md          | 15 +++++++++
 3 files changed, 88 insertions(+)

### 代码质量

✅ Review Score: 92/100
- Architecture: 38/40
- Best Practices: 28/30
- Testing: 25/30

---

🤖 Generated by [Claude Code](https://claude.com/claude-code) via `/finish-issue`
```

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

## Examples

**Basic finish:** User says "finish issue #97" → Claude creates 8-step task list, commits changes with issue reference, creates and merges PR, posts summary comment to issue (commits, file changes, review score), closes issue, cleanups (archives plan, removes state files, deletes branch/worktree). Time: ~2-3 minutes.

**Dry run:** Use `--dry-run` to preview steps without executing. Time: <10 seconds.

**No merge:** Use `--no-merge` to create PR but skip merging for manual review.

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

**Version:** 3.1.0
**Pattern:** Workflow Orchestrator (AI-guided + Script)
**Compliance:** ADR-001 ✅ | ADR-003 ✅ | WORKFLOW_PATTERNS ✅
**Last Updated:** 2026-03-18
**Changelog:**
- v3.1.0: Added mode-aware output (2 lines auto, ≤20 lines interactive) (Issue #263)
- v3.0.0: Complete rewrite with Python script + AI orchestration
- v2.0.0: Added workflow pattern compliance
- v1.0.0: Initial release
