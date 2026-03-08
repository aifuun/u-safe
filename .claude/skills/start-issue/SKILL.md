---
name: start-issue
description: |
  Start working on a GitHub issue with automated branch creation and planning.
  TRIGGER when: user wants to begin work on an issue (e.g., "start issue #23", "begin working on #45", "work on that bug", "let's tackle the auth issue").
  Also trigger when user mentions starting, picking up, or beginning any GitHub issue by number or description.
  DO NOT TRIGGER when: user just wants to view/list issues (use /issue instead), or close/finish issues (use /finish-issue).
---

# Start Issue - Begin Work on GitHub Issue

Automate the setup for working on a GitHub issue: fetch details, create branch, generate plan, and prepare environment.

## Overview

This skill handles the complete workflow to start working on a GitHub issue:

**What it does:**
1. Fetches issue details from GitHub (or creates new issue with `--create`)
2. Creates a feature branch with smart naming: `feature/{number}-{kebab-case-title}`
3. Generates an implementation plan from the issue body
4. Syncs with main branch and sets up dependencies
5. Shows clear next steps to begin coding

**Why it's needed:**
Starting work on an issue involves many manual steps (fetch issue, create branch, push, write plan, sync). This skill automates the entire flow in ~30 seconds, ensuring consistency and saving 5-10 minutes of manual work.

**When to use:**
- User says "start issue #N" or similar phrasing
- User wants to "work on", "begin", "pick up" an issue
- User wants to create and immediately start work on a new issue

Pairs with `/finish-issue` for complete issue lifecycle management.

## Arguments

```
$ARGUMENTS = "[issue-number] [options]" or "--create \"title\" [options]"
```

**Common usage:**
```bash
/start-issue #23
/start-issue #23 --no-plan
/start-issue --create "Fix login button" --label bug,P0
/start-issue #23 --branch-prefix fix
```

**Options:**
- `--create "title"` - Create new issue and start work
- `--label bug,P0` - Add labels when creating (use with --create)
- `--no-plan` - Skip plan generation
- `--branch-prefix fix` - Use custom prefix instead of "feature"
- `--dry-run` - Preview actions without executing
- `--force` - Override safety checks

## Workflow Steps

Execute these steps in sequence:

### 1. Validate Environment

Check that it's safe to start:
- Not already on a feature branch (must be on main or similar)
- No uncommitted changes (or user confirms stash/commit)
- GitHub CLI is authenticated

If validation fails, show clear error with options to resolve.

### 2. Fetch or Create Issue

**For existing issue:**
```bash
gh issue view $ISSUE_NUMBER --json number,title,body,state
```

Extract issue title, body, and verify it's open (warn if closed).

**For --create flag:**
```bash
gh issue create --title "$TITLE" --label "$LABELS" --body "$BODY"
```

Parse the `--create "title"` and optional `--label`, `--body` from arguments.

### 3. Create Feature Branch

Generate branch name from issue title:
- Convert to kebab-case: "Fix Login Bug" → "fix-login-bug"
- Truncate to 50 chars if needed
- Construct: `{prefix}/{number}-{kebab-title}` (default prefix: "feature")

Check if branch exists remotely; if yes, show options (checkout existing, delete and recreate, use different prefix).

Create and push branch:
```bash
git checkout -b "$BRANCH_NAME"
git push -u origin "$BRANCH_NAME"
```

### 4. Generate Implementation Plan (unless --no-plan)

Create `.claude/plans/active/issue-{number}-plan.md` with:

**Structure:**
```markdown
# Issue #{number}: {title}

**GitHub**: [link]
**Branch**: {branch-name}
**Started**: {date}

## Context
{issue body}

## Tasks
{extracted from issue body - look for checkboxes, numbered lists}

## Acceptance Criteria
{extracted from issue body - look for "Acceptance Criteria" section}

## Progress
- [ ] Plan reviewed
- [ ] Implementation started
- [ ] Tests added
- [ ] Ready for review

## Next Steps
1. Review this plan
2. Get first task: /next
3. Start implementation
4. When done: /finish-issue #{number}
```

**Why generate plans:** Plans create a single source of truth, make progress trackable, and give Claude context about the full scope of work.

### 5. Create Todo List from Plan

Parse the plan's `## Tasks` section and create Claude Code todos:

```
For each task in plan:
1. Use TaskCreate with subject, description, activeForm
2. Add blockedBy dependencies for sequential tasks
3. Enables visual progress tracking in Claude Code UI
```

**Example:** Plan with "Read legacy skill", "Create SKILL.md", "Add LICENSE.txt" becomes 3 linked todos.

### 6. Sync and Setup

Ensure working directory is ready:
```bash
git fetch origin
git merge origin/main
```

If `package.json` exists and `node_modules` is stale, run `npm install`.

Optionally run quick health check (don't block on failure).

### 7. Report Success

Show clear next steps:
```
🎉 Ready to work on Issue #{number}!

Next steps:
  1. Review plan: cat {plan-file}
  2. Get first task: /next
  3. Start coding!
  4. When done: /finish-issue #{number}

Current status:
  Branch: {branch-name}
  Plan: {plan-file}
```

## Error Handling

Handle common failure scenarios gracefully:

**Already on feature branch:**
```
❌ Already on feature branch: feature/11-other-task

Options:
  1. Finish current work: /finish-issue #11
  2. Switch to main: git checkout main && /start-issue #23
  3. Force: /start-issue #23 --force
```

**Uncommitted changes:**
```
⚠️ Uncommitted changes detected

Options:
  1. Commit: git add . && git commit -m "WIP"
  2. Stash: git stash && /start-issue #23
  3. Force: /start-issue #23 --force
```

**Issue not found:**
```
❌ Issue #999 not found

Check:
  1. Issue number correct?
  2. Repository correct? Run: gh repo view
  3. Authentication valid? Run: gh auth status
```

**Branch already exists:**
```
⚠️ Branch feature/23-fix-bug already exists

Options:
  1. Checkout existing: git checkout feature/23-fix-bug
  2. Delete and recreate: git branch -D feature/23-fix-bug && /start-issue #23
  3. Use different prefix: /start-issue #23 --branch-prefix v2
```

## Examples

### Example 1: Start Existing Issue

**User says:**
> "hey can you start working on issue #37? i think it's about project cleanup"

**What happens:**
1. Fetch issue #37 details
2. Create branch: `feature/37-project-cleanup`
3. Generate plan at `.claude/plans/active/issue-37-plan.md`
4. Sync with main
5. Show ready message

**Time:** ~30 seconds

### Example 2: Create and Start New Issue

**User says:**
> "i found a bug - the login button is misaligned on mobile. create an issue and start work on it, label it bug and P1"

**What happens:**
1. Create issue: "Login button misaligned on mobile" with labels bug,P1
2. Get new issue number (e.g., #42)
3. Create branch: `feature/42-login-button-misaligned-mobile`
4. Generate plan
5. Ready to code

**Time:** ~45 seconds

### Example 3: Bugfix with Custom Prefix

**User says:**
> "start issue #48 but use 'fix' as the branch prefix since it's a bugfix"

**What happens:**
1. Fetch issue #48
2. Create branch: `fix/48-{title}` (not feature/)
3. Generate plan
4. Ready to code

**Time:** ~30 seconds

### Example 4: Skip Plan Generation

**User says:**
> "start issue #23 but skip the plan, I already know what to do"

**What happens:**
1. Fetch issue #23
2. Create branch
3. Skip plan generation
4. Ready to code (use /plan later if needed)

**Time:** ~15 seconds

## Integration

**Pairs with /finish-issue:**
```
/start-issue #23    # ← Start (30 sec)
# ... implement ...
/finish-issue #23   # ← Finish and close (2-3 min)
```

**Workflow integration:**
```
/issue list         # Browse open issues
/start-issue #23    # Begin work
/next               # Get first task from plan
# ... code ...
/review             # Self-review
/finish-issue #23   # Complete
```

**Plan file location:**
- Created: `.claude/plans/active/issue-{number}-plan.md`
- Used by: `/next` (get current task)
- Archived by: `/finish-issue` (moved to `.claude/plans/archive/`)

## Performance

- **Average time:** 30 seconds (with plan)
- **Without plan:** 15 seconds
- **With --create:** 45 seconds

Fast because:
- Minimal GitHub API calls
- Parallel operations where possible
- Skip npm install if node_modules is fresh

## Best Practices

1. **Start from main** - Ensures clean branch point
2. **Review issue first** - Understand scope before starting
3. **Let plan generate** - Auto-extraction saves time
4. **Use descriptive issue titles** - Branch names come from titles
5. **Follow workflow** - start → next → code → finish

## Task Management

**After each step completion**, update progress:

```
Step 1 done (Environment validated) → Use TaskUpdate if created
Step 2 done (Issue fetched) → Update task status
Step 3 done (Branch created) → Update task status
Step 4 done (Plan generated) → Update task status
Step 5 done (Todos created) → Update task status
Step 6 done (Environment synced) → Update task status
Step 7 done (Success reported) → Mark workflow complete
```

This provides real-time visibility of progress.

## Final Verification

**Quick checklist before completion:**

```
- [ ] Branch created and pushed
- [ ] Plan file exists (unless --no-plan)
- [ ] Todo list created from plan
- [ ] Synced with origin/main
- [ ] Ready message displayed
- [ ] User knows next steps
```

If any critical item missing, troubleshoot before declaring success.

## Related Skills

- **/finish-issue** - Complete issue workflow (pairs with this)
- **/issue** - Issue management (list, view, close)
- **/plan** - Custom planning (if auto-plan isn't enough)
- **/next** - Get next task from plan

---

**Version:** 2.1.0
**Pattern:** Tool-Reference (guides Claude through workflow)
**Compliance:** ADR-001 Section 4 ✅
