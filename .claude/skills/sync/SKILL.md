---
name: sync
description: |
  Sync branch with main - fetch, merge, resolve conflicts, test, push. Works on both feature branches and main branch.
  TRIGGER when: user wants to sync with main ("sync with main", "merge main into my branch", "update from main", "pull latest changes", "sync").
version: "2.4.0"
  DO NOT TRIGGER when: user wants to create branches (use /start-issue), or finish work (use /finish-issue).
---

# Sync - Branch Synchronization with Main

Safe synchronization of your branch with main, including conflict resolution and safety checks.

## Overview

This skill automates the complete workflow to sync your branch:

**On Feature Branch:**
1. Auto-commits uncommitted changes (with enhanced message including file list)
2. Fetches latest changes from remote
3. Merges main into branch (with detailed merge commit message)
4. Detects and guides conflict resolution (with enhanced conflict messages)
5. Runs tests to verify nothing broke
6. Pushes synced changes

**On Main Branch:**
1. Auto-commits uncommitted changes
2. Fetches and pulls from origin/main
3. Pushes changes

**When to use:** Before new work, daily sync, before PR, updating local main

## Workflow

**Feature Branches (7 steps):**
\`\`\`
- [ ] Step 1: Auto-commit uncommitted changes
- [ ] Step 2: Fetch latest from remote
- [ ] Step 3: Check for potential conflicts
- [ ] Step 4: Merge main into feature branch
- [ ] Step 5: Resolve conflicts if any
- [ ] Step 6: Run tests
- [ ] Step 7: Push synced branch
\`\`\`

**Main Branch (5 steps):**
\`\`\`
- [ ] Step 1: Auto-commit uncommitted changes
- [ ] Step 2: Fetch latest from remote
- [ ] Step 3: Pull and merge origin/main
- [ ] Step 4: Resolve conflicts if any
- [ ] Step 5: Push to remote
\`\`\`

## Core Sync Steps

### 1. Auto-Commit Uncommitted Changes

Enhanced commit message with file list and branch:

\`\`\`bash
git add .
MODIFIED=\$(git diff --name-only --cached | tr '\\n' ', ' | sed 's/,\$//')
BRANCH=\$(git rev-parse --abbrev-ref HEAD)

git commit -m "wip: auto-commit before sync on \${BRANCH}

Modified: \${MODIFIED}
Reason: Preparing for main branch sync"
\`\`\`

### 2. Fetch Latest

\`\`\`bash
git fetch origin
\`\`\`

### 3. Merge Main

Enhanced merge message with commit count and list:

\`\`\`bash
BRANCH=\$(git rev-parse --abbrev-ref HEAD)
COMMITS=\$(git log HEAD..origin/main --oneline | head -5)
COUNT=\$(git rev-list --count HEAD..origin/main)

git merge origin/main -m "sync: merge main into \${BRANCH}

Merged \${COUNT} commits:
\${COMMITS}"
\`\`\`

**Outcomes:**
- ✅ Fast-forward - No conflicts
- ✅ Auto-merge - Git resolved automatically
- ⚠️ Conflicts - Manual resolution required

### 4. Conflict Resolution

Enhanced conflict resolution message:

\`\`\`bash
# 1. View conflicts
git status

# 2. Edit files, remove markers (<<<<<<<, =======, >>>>>>>)

# 3. Stage and commit with enhanced message
git add <files>
CONFLICTS=\$(git diff --name-only --diff-filter=U | tr '\\n' ', ' | sed 's/,\$//')
git commit -m "resolve: merge conflicts in \${CONFLICTS}

Strategy: Manual resolution
Files: \${CONFLICTS}"

# 4. Verify
npm test
\`\`\`

**For detailed conflict resolution:**
- Step-by-step guides
- Special cases (package-lock.json, binaries)
- Common patterns
- Prevention tips

See **[CONFLICT-HANDLING.md](CONFLICT-HANDLING.md)**

### 5. Post-Merge Testing

\`\`\`bash
# Run tests if they exist
if [ -f "package.json" ] && grep -q "test" package.json; then
  npm test
fi
\`\`\`

### 6. Push Synced Branch

\`\`\`bash
git push origin \$(git rev-parse --abbrev-ref HEAD)
\`\`\`

## Syncing Main Branch

Simpler workflow when on main:

\`\`\`bash
# 1. Auto-commit if needed
git add .
git commit -m "wip: auto-commit before sync"

# 2. Pull latest
git pull origin main

# 3. Push if you had local commits
git push origin main
\`\`\`

## Error Handling

### Auto-Commit Behavior

\`\`\`
ℹ️ Auto-committing uncommitted changes
Modified: 3 files
Action: Creating enhanced WIP commit with file list
\`\`\`

### Remote Branch Missing

\`\`\`
⚠️ Branch not pushed to remote yet
Action: git push -u origin <branch>
\`\`\`

### Tests Failing After Merge

Enhanced fix commit message:

\`\`\`bash
BRANCH=\$(git rev-parse --abbrev-ref HEAD)
git commit -m "fix: resolve test failures after sync

Branch: \${BRANCH}
Cause: API changes from main merge
Resolution: Updated test expectations"
\`\`\`

## Advanced Scenarios

For complex scenarios:
- Long-running branches (100+ commits behind)
- Conflicting package.json dependencies
- Emergency hotfix during sync
- Large repository optimization
- Performance tuning

See **[SYNC-STRATEGIES.md](SYNC-STRATEGIES.md)**

## Usage Examples

**Example 1: Daily Sync**
- Command: "sync my branch"
- Flow: Fetch → Merge → Test → Push
- Time: ~1 min

**Example 2: With Conflicts**
- Command: "pull latest changes"
- Flow: Fetch → Merge → Conflicts → Resolve → Test → Push
- Time: ~5-10 min

**Example 3: Main Branch**
- Command: "sync" (on main)
- Flow: Fetch → Pull → Push
- Time: ~30 sec

## Best Practices

1. **Sync frequently** - Daily or before new work
2. **Enhanced messages** - File lists, branch names, commit counts included
3. **Test after merge** - Always verify
4. **Careful resolution** - Don't blindly accept changes
5. **Communicate** - Notify team of complex merges

## Task Management

Track progress with TaskCreate/TaskUpdate:

\`\`\`
Task #1: Auto-commit → completed
Task #2: Fetch → completed
...
Task #7: Push → completed
\`\`\`

## Final Verification

\`\`\`
- [ ] All tasks completed
- [ ] Enhanced commit messages used
- [ ] No remaining conflicts
- [ ] Tests passing
- [ ] Changes pushed
- [ ] Working tree clean
\`\`\`

## Workflow Skills Requirements

Follows standard pattern:
1. **TaskCreate** - Todo list
2. **TaskUpdate** - Progress tracking
3. **Verification** - Final checks

See: [WORKFLOW_PATTERNS.md](../WORKFLOW_PATTERNS.md)

## Related Skills

- **/start-issue** - Create feature branch
- **/finish-issue** - Final sync before PR
- **/review** - Code review after sync

## Documentation

- **[CONFLICT-HANDLING.md](CONFLICT-HANDLING.md)** - Detailed conflict resolution
- **[SYNC-STRATEGIES.md](SYNC-STRATEGIES.md)** - Advanced scenarios

---

**Version:** 2.4.0
**Pattern:** Tool-Reference
**Compliance:** ADR-001 ✅
**Changelog:**
- v2.4.0: Enhanced commit messages + split documentation (Issue #558)
- v2.3.0: Auto-commit before sync
- v2.2.0: Main branch sync support
