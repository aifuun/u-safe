---
name: start-issue
description: |
  Start working on a GitHub issue - fetch details, create branch, generate plan.
  Can create new issues on-the-fly with --create flag.
  Pairs with /finish-issue for complete issue lifecycle management.
disable-model-invocation: true
user-invocable: true
argument-hint: "[issue-number] [--create \"title\"] [--no-plan] [--dry-run]"
allowed-tools: Bash(gh *), Bash(git *), Read, Write
context: fork
agent: general-purpose
---

# Issue Starter

Start working on a GitHub issue with automated setup and planning.

## Task

Start issue workflow (with live status):
1. **Create Issue** - (Optional) Create new issue with --create flag (LIVE)
2. **Fetch Issue** - Get details from GitHub (LIVE)
3. **Create Branch** - Smart branch naming from issue (LIVE)
4. **Generate Plan** - Optional task breakdown (LIVE)
5. **Setup Environment** - Check dependencies and sync (LIVE)
6. **Display Next Steps** - Ready to code (LIVE)

## Live Pre-Start Status

### Current State
- **Current Branch**: !`git rev-parse --abbrev-ref HEAD`
- **Uncommitted Changes**: !`git status --short | wc -l | tr -d ' '` files
- **Behind Main**: !`git fetch origin &>/dev/null && git rev-list --count HEAD..origin/main 2>/dev/null || echo "0"` commits
- **Dependency Status**: !`if [ -f package.json ]; then npm list &>/dev/null && echo "✅ Ready" || echo "⚠️ Run npm install"; else echo "No package.json"; fi`

### GitHub Connection
- **Auth Status**: !`gh auth status &>/dev/null && echo "✅ Authenticated" || echo "❌ Not authenticated"`
- **API Rate Limit**: !`gh api rate_limit --jq '.rate | "\\(.remaining)/\\(.limit)"' 2>/dev/null || echo "unknown"`

## Commands

**Basic usage**:
```bash
/start-issue #23              # Start working on issue #23
/start-issue #23 --no-plan    # Skip plan generation
/start-issue #23 --dry-run    # Preview actions only
/start-issue --create "Fix login button" --label bug,P0  # Create + start ⭐
```

**With arguments** (using $ARGUMENTS):
```bash
/start-issue #23                    # Full setup with plan
/start-issue --create "Title" --label bug,P0  # Create issue + start
/start-issue #23 --no-plan          # Branch only, no plan
/start-issue #23 --branch-prefix fix # Use fix/ instead of feature/
/start-issue #23 --dry-run          # Test mode
```

Argument format: `[issue-number] [options]`

Options:
- `--no-plan` - Skip implementation plan generation
- `--dry-run` - Show what would happen without executing
- `--branch-prefix <prefix>` - Use custom branch prefix (default: feature)
- `--force` - Override safety checks

## Workflow

Execute: `bash scripts/start-issue.sh $ARGUMENTS`

### Standard Flow (5 steps)

**Step 1: Fetch Issue Details**
```bash
gh issue view #23 --json number,title,body,labels,state
# → Issue: "Task List & Completion Flow"
# → Labels: P0, frontend, enhancement
# → State: OPEN
```

**Step 2: Create Feature Branch**
```bash
# Smart naming from issue title
# "Task List & Completion Flow" → feature/23-task-list-completion-flow
git checkout -b feature/23-task-list-completion-flow
git push -u origin feature/23-task-list-completion-flow
```

**Step 3: Generate Implementation Plan** (optional)
```bash
# Create plan file from issue description
cat > .claude/plans/active/issue-23-implementation.md << EOF
# Issue #23: Task List & Completion Flow

## Tasks
- [ ] Design task list component
- [ ] Implement completion logic
- [ ] Add tests
- [ ] Update documentation
EOF
```

**Step 4: Environment Setup**
```bash
# Sync with main
git fetch origin
git merge origin/main

# Install dependencies (if needed)
[ -f package.json ] && npm install

# Run health check
npm test &>/dev/null && echo "✅ Tests passing"
```

**Step 5: Display Next Steps**
```bash
echo "✅ Ready to work on Issue #23!"
echo ""
echo "Next steps:"
echo "  1. Read plan: cat .claude/plans/active/issue-23-implementation.md"
echo "  2. Get first task: /next"
echo "  3. Start coding!"
echo "  4. When done: /finish-issue #23"
```

### Fast Path (30 seconds)

```
Start: on main branch
  ↓ (5 sec)
Fetch issue #23 from GitHub
  ↓ (10 sec)
Create branch: feature/23-task-list-completion-flow
  ↓ (10 sec)
Generate plan with 5 tasks
  ↓ (5 sec)
Sync with main + install deps
  ↓
End: Ready to code! ✅

Total time: ~30 seconds
```

## Safety Features

**Pre-flight Checks**:
- ✅ Issue exists and is open on GitHub
- ✅ Not already on a feature branch
- ✅ No uncommitted changes (or confirm stash)
- ✅ Dependencies installed
- ✅ Tests passing (if present)

**Smart Defaults**:
- Branch naming: `feature/{number}-{kebab-case-title}`
- Syncs with main automatically
- Generates plan from issue description
- Links issue to plan file

**Rollback Protection**:
- Creates backup before major changes
- Can cancel at any step
- Preserves existing work

## Integration with Framework

### Paired with /finish-issue

```bash
# Complete workflow
/start-issue #23    # ← Start working (30 sec)
# ... implement ...
/finish-issue #23   # ← Complete & close (2-3 min)

# Total lifecycle: Managed from start to finish
```

### Workflow Integration

```
/issue list         → See all open issues
/start-issue #23    → Begin work on #23
/next               → Get first task from plan
# ... code ...
/review             → Self-review code
/finish-issue #23   → Complete and close
```

### Plan Integration

**Auto-generated plan structure**:
```markdown
# Issue #23: {Title}

## Context
{Issue description}

## Tasks
{Auto-extracted from issue body}

## Acceptance Criteria
{From issue body or labels}

## Related
- GitHub: #{number}
- Branch: feature/{number}-{title}
```

## Examples

### Example 1: Standard Start

```bash
/start-issue #23

# Output:
# 🔍 Fetching Issue #23...
# ✅ Issue: "Task List & Completion Flow"
# 📝 Labels: P0, frontend, enhancement
#
# 🌿 Creating branch: feature/23-task-list-completion-flow
# ✅ Branch created and pushed
#
# 📋 Generating implementation plan...
# ✅ Plan saved: .claude/plans/active/issue-23-implementation.md
#
# 🔄 Syncing with main...
# ✅ Up to date with origin/main
#
# 🎉 Ready to work on Issue #23!
#
# Next steps:
#   1. Read plan: /next
#   2. Start coding!
#   3. When done: /finish-issue #23
```

### Example 2: Skip Plan Generation

```bash
/start-issue #23 --no-plan

# Same as above but skips plan generation
# Useful when you already have a clear implementation in mind
```

### Example 3: Custom Branch Prefix

```bash
/start-issue #23 --branch-prefix fix

# Creates: fix/23-task-list-completion-flow
# Useful for bug fixes or hotfixes
```

### Example 4: Dry Run (Test Mode)

```bash
/start-issue #23 --dry-run

# Output:
# Would fetch issue #23 from GitHub
# Would create branch: feature/23-task-list-completion-flow
# Would generate plan: .claude/plans/active/issue-23-implementation.md
# Would sync with origin/main
# Would install dependencies (if needed)
```

### Example 5: Create and Start (One Command) ⭐

```bash
/start-issue --create "Fix login button alignment" --label bug,P0

# Output:
# 📝 Creating new issue...
# ✅ Issue #24 created: "Fix login button alignment"
# 🏷️  Labels: bug, P0
#
# 🌿 Creating branch: feature/24-fix-login-button-alignment
# ✅ Branch created and pushed
#
# 📋 Generating implementation plan...
# ✅ Plan saved: .claude/plans/active/issue-24-implementation.md
#
# 🔄 Syncing with main...
# ✅ Up to date with origin/main
#
# 🎉 Ready to work on Issue #24!
#
# Next steps:
#   1. Read plan: /next
#   2. Start coding!
#   3. When done: /finish-issue #24
```

**Use cases for --create:**
- Quick bug fixes that don't need detailed planning
- Small features discovered during development
- Technical debt items identified on-the-fly
- Emergent work not captured in MVP plans

**Compared to /create-issues:**
- `/create-issues`: Batch creation from MVP plans (10+ issues)
- `/start-issue --create`: Single ad-hoc issue + immediate work

## Error Handling

### Scenario 1: Already on Feature Branch

```
⚠️ Error: Already on a feature branch: feature/11-task-list

Options:
1. Finish current work: /finish-issue #11
2. Switch to main: git checkout main && /start-issue #23
3. Force new branch: /start-issue #23 --force (not recommended)
```

### Scenario 2: Uncommitted Changes

```
⚠️ Error: Uncommitted changes detected

Files:
- src/components/TaskList.tsx (modified)
- src/types/task.ts (new)

Options:
1. Commit now: git add . && git commit -m "WIP"
2. Stash: git stash && /start-issue #23
3. Force anyway: /start-issue #23 --force
```

### Scenario 3: Issue Doesn't Exist

```
❌ Error: Issue #999 not found on GitHub

Check:
1. Issue number correct?
2. Repository correct? (gh repo view)
3. Authentication valid? (gh auth status)
```

### Scenario 4: Issue Already Closed

```
⚠️ Warning: Issue #23 is already CLOSED

Status: Closed on 2026-03-04 by @user

Options:
1. Reopen issue: gh issue reopen #23
2. Pick different issue: /issue list
3. Continue anyway: /start-issue #23 --force
```

### Scenario 5: Branch Already Exists

```
⚠️ Warning: Branch feature/23-task-list exists

Options:
1. Checkout existing: git checkout feature/23-task-list
2. Delete and recreate: git branch -D feature/23-task-list && /start-issue #23
3. Use different name: /start-issue #23 --branch-prefix feature-v2
```

## Advanced Usage

### Plan Generation from Issue

The skill auto-extracts tasks from issue descriptions:

**Issue body format** (GitHub markdown):
```markdown
## Tasks
- [ ] Design UI mockups
- [ ] Implement TaskList component
- [ ] Add unit tests
- [ ] Update documentation

## Acceptance Criteria
- Task list displays correctly
- Completion flow works
- Tests pass
```

**Generated plan** (`.claude/plans/active/issue-23-implementation.md`):
```markdown
# Issue #23: Task List & Completion Flow

## Context
From issue description...

## Tasks
- [ ] Design UI mockups
- [ ] Implement TaskList component
- [ ] Add unit tests
- [ ] Update documentation

## Acceptance Criteria
- Task list displays correctly
- Completion flow works
- Tests pass

## Related
- GitHub: #23
- Branch: feature/23-task-list-completion-flow
- Created: 2026-03-04
```

### Custom Branch Naming

```bash
# Default (feature/)
/start-issue #23
→ feature/23-task-list-completion-flow

# Bug fix
/start-issue #23 --branch-prefix fix
→ fix/23-task-list-completion-flow

# Hotfix
/start-issue #23 --branch-prefix hotfix
→ hotfix/23-task-list-completion-flow

# Experiment
/start-issue #23 --branch-prefix experiment
→ experiment/23-task-list-completion-flow
```

### Integration with /plan

```bash
# If you want custom planning instead of auto-generated
/start-issue #23 --no-plan
/plan "Implement task list with drag-drop and real-time sync"
# Creates more detailed plan than auto-extraction
```

## Troubleshooting

### Issue: GitHub CLI Not Authenticated

```bash
gh auth login
/start-issue #23
```

### Issue: Can't Push Branch

```bash
# Check remote
git remote -v

# Add remote if missing
git remote add origin https://github.com/user/repo.git

# Try again
/start-issue #23
```

### Issue: Merge Conflicts with Main

```bash
# Will be detected automatically
# Follow prompts to resolve conflicts
git status
git add <resolved-files>
git commit
```

### Issue: Plan File Already Exists

```bash
⚠️ Plan file exists: .claude/plans/active/issue-23-implementation.md

Options:
1. View existing: cat .claude/plans/active/issue-23-implementation.md
2. Overwrite: /start-issue #23 --force
3. Rename old: mv .claude/plans/active/issue-23-implementation.md \
               .claude/plans/archive/issue-23-old.md
```

## Best Practices

1. **Always start from main**: Ensure you're on main before starting new issues
2. **Review issue before starting**: Read the issue description carefully
3. **Use /issue list first**: Pick the right issue to work on
4. **Let it generate plans**: Auto-generated plans save time
5. **Follow the workflow**: start-issue → next → finish-issue

## Performance

- **Average time**: 30 seconds (with plan generation)
- **Without plan**: 15 seconds
- **With slow network**: 1-2 minutes

**Optimization Tips**:
- Keep dependencies up to date (faster npm install)
- Use fast internet for GitHub API calls
- Cache GitHub credentials (gh auth login)

## Comparison with Manual Setup

| Step | Manual | /start-issue | Time Saved |
|------|--------|--------------|------------|
| Fetch issue | gh issue view #23 | Automated | 15 sec |
| Create branch | git checkout -b ... | Automated | 30 sec |
| Push branch | git push -u origin ... | Automated | 10 sec |
| Create plan | Manual writing | Automated | 5 min |
| Sync with main | git fetch && merge | Automated | 30 sec |
| Install deps | npm install | Automated | 1 min |
| **Total** | **~7-10 min** | **~30 sec** | **6-9 min** |

## Lifecycle Management

```
┌─────────────────────────────────────────────┐
│          Complete Issue Lifecycle           │
├─────────────────────────────────────────────┤
│                                             │
│  /start-issue #23                          │
│  ↓ (30 sec)                                │
│  Branch created + Plan generated           │
│  ↓                                         │
│  /next → Get first task                    │
│  ↓                                         │
│  Code implementation                       │
│  ↓                                         │
│  /review → Self-review                     │
│  ↓                                         │
│  /finish-issue #23                         │
│  ↓ (2-3 min)                               │
│  PR created + Merged + Issue closed        │
│                                             │
│  Total managed time: 3-4 minutes           │
│  Total workflow time: Clear & structured   │
└─────────────────────────────────────────────┘
```

---

**Related**:
- [finish-issue](../finish-issue/SKILL.md) - Complete issue workflow (pairs with this)
- [issue](../issue/SKILL.md) - General issue management
- [plan](../plan/SKILL.md) - Strategic planning
- [next](../next/SKILL.md) - Get next task from plan

**Version**: 1.0.0
**Created**: 2026-03-04
**Status**: Production Ready
