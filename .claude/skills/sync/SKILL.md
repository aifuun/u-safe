---
name: sync
description: |
  Sync branch with main - fetch, merge, resolve conflicts, test, push. Works on both feature branches and main branch.
  TRIGGER when: user wants to sync with main ("sync with main", "merge main into my branch", "update from main", "pull latest changes", "sync").
  DO NOT TRIGGER when: user wants to create branches (use /start-issue), or finish work (use /finish-issue).
---

# Sync - Branch Synchronization with Main

Safe synchronization of your branch with main, including conflict resolution and safety checks. Works on both feature branches and main branch.

## Overview

This skill automates the complete workflow to sync your branch:

**On Feature Branch:**
1. Auto-commits any uncommitted changes (WIP commit)
2. Fetches latest changes from remote
3. Merges main into your feature branch
4. Detects and guides conflict resolution
5. Runs tests to verify nothing broke
6. Pushes synced changes to remote
7. Provides live status throughout the process

**On Main Branch:**
1. Auto-commits any uncommitted changes (WIP commit)
2. Fetches latest changes from remote
3. Pulls and merges remote main into local main
4. Detects and guides conflict resolution (if any)
5. Pushes changes to remote
6. Provides live status throughout the process

**Why it's needed:**
Keeping branches in sync with main prevents merge conflicts, ensures compatibility with latest changes, and makes final PRs smoother. Manual syncing involves multiple git commands and safety checks that are easy to forget.

**When to use:**
- Before starting new work on a long-running branch
- Daily sync for active feature branches
- Before creating a PR (with /finish-issue)
- After main branch receives important updates
- When you see "branch is X commits behind main"
- To update local main with latest remote changes

## Workflow

### Step 1: Create Todo List

**Initialize sync tracking** using TaskCreate:

**For Feature Branches:**
```
Task #1: Auto-commit uncommitted changes
Task #2: Fetch latest from remote (blocked by #1)
Task #3: Check for potential conflicts (blocked by #2)
Task #4: Merge main into feature branch (blocked by #3)
Task #5: Resolve conflicts if any (blocked by #4)
Task #6: Run tests to verify (blocked by #5)
Task #7: Push synced branch (blocked by #6)
```

**For Main Branch:**
```
Task #1: Auto-commit uncommitted changes
Task #2: Fetch latest from remote (blocked by #1)
Task #3: Pull and merge origin/main (blocked by #2)
Task #4: Resolve conflicts if any (blocked by #3)
Task #5: Push to remote (blocked by #4)
```

After creating tasks, proceed with sync execution.

## Sync Dimensions

### 1. Pre-Sync Status Check

Verify current state before syncing:

```bash
# Current branch
git rev-parse --abbrev-ref HEAD

# Latest commit on your branch
git rev-parse --short HEAD

# Latest commit on main
git rev-parse --short origin/main

# How many commits behind/ahead
git rev-list --left-right --count origin/main...HEAD
```

**Safety checks:**
- Auto-commit uncommitted changes (WIP commit if present)
- Confirm tests are passing (for feature branches)
- Verify branch exists on remote (for pushing)

### 2. Fetch Latest Changes

Get latest from remote without modifying local branches:

```bash
git fetch origin
git fetch origin main
```

**Why fetch first:**
- See what changes are coming
- Preview potential conflicts
- Don't modify working tree yet

### 3. Conflict Detection

Before merging, preview what might conflict:

```bash
# Files modified on both branches
git diff --name-only origin/main...HEAD

# Detailed change preview
git diff origin/main...HEAD --stat

# Show commits on main not in your branch
git log HEAD..origin/main --oneline
```

**Common conflict scenarios:**
- Same file modified in both branches
- File deleted in main but modified in your branch
- Package.json/lock file differences
- Formatting changes (prettier, linting)

### 4. Merge Execution

Merge main into your feature branch:

```bash
# Standard merge
git merge origin/main

# Or with message
git merge origin/main -m "sync: merge main into feature branch"
```

**Possible outcomes:**
- ✅ **Fast-forward** - No conflicts, auto-merged
- ✅ **Auto-merge** - Git resolved conflicts automatically
- ⚠️ **Conflicts** - Manual resolution required (see Conflict Resolution)

### 5. Conflict Resolution

If conflicts detected, guide the user:

```markdown
⚠️ Merge conflicts found in:
- src/auth.ts (2 conflicts)
- src/types.ts (1 conflict)
- package-lock.json (auto-resolve recommended)

## Resolution Steps

1. **Review conflicts:**
   ```bash
   git status  # See conflicted files
   git diff    # See conflict markers
   ```

2. **Edit conflicted files:**
   - Look for `<<<<<<<`, `=======`, `>>>>>>>` markers
   - Choose which changes to keep
   - Remove conflict markers
   - Combine changes if needed

3. **Stage resolved files:**
   ```bash
   git add src/auth.ts
   git add src/types.ts
   ```

4. **Complete merge:**
   ```bash
   git commit -m "resolve: merge conflicts from main"
   ```

5. **Verify resolution:**
   ```bash
   npm run lint    # Check syntax
   npm test        # Run tests
   ```

## Special Cases

**package-lock.json conflicts:**
```bash
# Usually safe to regenerate
git checkout --theirs package-lock.json
npm install
git add package-lock.json
```

**Binary file conflicts:**
```bash
# Choose one version
git checkout --ours path/to/file   # Keep your version
# OR
git checkout --theirs path/to/file # Take main's version
git add path/to/file
```
```

### 6. Post-Merge Testing

Verify nothing broke after merge:

```bash
# TypeScript compilation
npx tsc --noEmit

# Linting
npm run lint

# Unit tests
npm test

# Build verification
npm run build
```

**If tests fail:**
1. Review merge-related changes
2. Fix failing tests or broken code
3. Commit fixes: `git commit -m "fix: resolve test failures after sync"`
4. Re-run tests until passing

### 7. Push Synced Branch

Push merged changes to remote:

```bash
# Push to remote
git push origin <branch-name>

# If remote was force-updated (rare)
git push --force-with-lease origin <branch-name>
```

**Safety:**
- Only push after tests pass
- Use `--force-with-lease` instead of `--force` (safer)
- Confirm branch name is correct

## Safety Features

**Pre-flight checks:**
- ✅ Auto-commit uncommitted changes (WIP commit)
- ✅ Confirm tests passing before sync (feature branches)
- ✅ Preview conflicts before merge
- ✅ Detect branch type (main vs feature) and use appropriate workflow

**Backup protection:**
```bash
# Create backup before risky operations
git branch backup/<branch-name>

# Restore if needed
git reset --hard backup/<branch-name>
```

**Abort mechanisms:**
```bash
# Abort merge if conflicts too complex
git merge --abort

# Reset to pre-sync state
git reset --hard HEAD@{1}
```

## Integration

**With /start-issue:**
```
/start-issue #23    # Creates feature branch from main
# ... work for a while ...
/sync               # Sync with main mid-development
# ... more work ...
/finish-issue #23   # Final sync happens automatically
```

**With /finish-issue:**
```
# finish-issue includes sync step automatically
/finish-issue #23   # Syncs, then creates PR
```

**Daily workflow:**
```
# Morning routine
/sync               # Get latest changes
/next               # Continue work

# Before lunch
/sync               # Stay up-to-date

# End of day
/sync               # Prepare for tomorrow
```

## Special Workflows

### Syncing Main Branch

When already on main branch, the workflow is simpler:

**Steps:**
1. **Fetch latest changes**
   ```bash
   git fetch origin main
   ```

2. **Pull and merge**
   ```bash
   git pull origin main
   # Or equivalently
   git merge origin/main
   ```

3. **Resolve conflicts if any** (rare on main, but possible)
   ```bash
   git status  # Check for conflicts
   # Edit files to resolve
   git add .
   git commit -m "resolve: merge conflicts from remote main"
   ```

4. **Push changes** (if you had local commits)
   ```bash
   git push origin main
   ```

**Why this is simpler:**
- No need for extensive testing (main should already be tested)
- Usually fast-forward merge (no conflicts)
- No need to preview conflicts in advance
- Direct push to origin/main

**When to use:**
- After making commits directly on main (not recommended workflow, but happens)
- To update local main with latest remote changes
- When you need to sync main before creating a new feature branch

## Error Handling

### Auto-Commit Behavior
```
ℹ️ Auto-committing uncommitted changes

Modified: 3 files
Untracked: 1 file

Action: Creating WIP commit
  git add .
  git commit -m "wip: auto-commit before sync"
```

**Note:** Uncommitted changes are automatically committed with a "wip:" prefix before syncing. This ensures a clean working tree and allows you to continue the sync safely.

### Remote Branch Doesn't Exist
```
⚠️ Warning: Branch not pushed to remote yet

Current: feature/23-task
Remote: Not found

Action: Push first
  git push -u origin feature/23-task
Then: /sync
```

### Tests Failing After Merge
```
❌ Error: Tests failing after merge

Failed: 2 tests in src/auth.test.ts

Next steps:
  1. Review changes: git log origin/main..HEAD
  2. Fix failing tests
  3. Commit: git commit -m "fix: resolve test failures"
  4. Continue: /sync --skip-tests (not recommended)
```

## Usage Examples

### Example 1: Daily Sync

**User says:**
> "sync my branch with main"

**What happens:**
1. Check current branch (e.g., feature/23-auth)
2. Fetch latest from origin/main
3. Preview conflicts (none)
4. Merge origin/main → feature/23-auth
5. Run tests (pass)
6. Push to origin/feature/23-auth
7. ✅ Branch synced successfully

**Time:** ~1 minute

### Example 2: Sync with Conflicts

**User says:**
> "pull latest changes from main"

**What happens:**
1. Fetch origin/main
2. Preview shows conflicts in src/auth.ts
3. Merge origin/main → feature/23-auth
4. ⚠️ Conflicts detected
5. Guide user through resolution
6. User edits, stages, commits
7. Run tests (pass)
8. Push to remote
9. ✅ Conflicts resolved, synced

**Time:** ~5-10 minutes

### Example 3: Sync Before PR

**User says:**
> "make sure my branch is up to date before creating the PR"

**What happens:**
1. Fetch latest
2. Check commits: branch 5 behind, 8 ahead
3. Merge main
4. Auto-merge successful
5. Run full test suite
6. Push synced branch
7. ✅ Ready for PR

**Time:** ~2 minutes

### Example 4: Sync Main Branch

**User says:**
> "sync" (while on main branch)

**What happens:**
1. Detect current branch: main
2. Fetch origin/main
3. Pull and merge origin/main
4. Fast-forward merge (no conflicts)
5. Push to origin/main (if there were local commits)
6. ✅ Main branch synced

**Time:** ~30 seconds

## Best Practices

1. **Sync frequently** - Daily or before starting new work
2. **Auto-commits WIP** - Uncommitted changes automatically committed with "wip:" prefix
3. **Test after merge** - Always verify tests pass
4. **Resolve conflicts carefully** - Don't blindly choose "theirs" or "ours"
5. **Communicate** - Tell team if resolving complex conflicts

## Task Management

**After each sync step**, update progress:

**For Feature Branches:**
```
Auto-commit completed → Update Task #1
Fetch completed → Update Task #2
Conflicts checked → Update Task #3
Merge executed → Update Task #4
Conflicts resolved → Update Task #5
Tests passed → Update Task #6
Branch pushed → Update Task #7
```

**For Main Branch:**
```
Auto-commit completed → Update Task #1
Fetch completed → Update Task #2
Pull/merge completed → Update Task #3
Conflicts resolved → Update Task #4
Branch pushed → Update Task #5
```

Provides real-time visibility of sync progress.

## Final Verification

**Before declaring sync complete**, verify:

**For Feature Branches:**
```
- [ ] All 7 sync tasks completed
- [ ] Uncommitted changes auto-committed
- [ ] Main branch merged into feature branch
- [ ] No remaining conflicts
- [ ] Tests passing
- [ ] Changes pushed to remote
- [ ] Working tree clean
```

**For Main Branch:**
```
- [ ] All 5 sync tasks completed
- [ ] Uncommitted changes auto-committed
- [ ] Remote main merged into local main
- [ ] No remaining conflicts
- [ ] Changes pushed to remote (if applicable)
- [ ] Working tree clean
```

Missing items indicate incomplete sync.

## Related Skills

- **/start-issue** - Creates feature branch from main
- **/finish-issue** - Includes final sync before PR
- **/review** - Review code after syncing

---

**Version:** 2.3.0
**Pattern:** Tool-Reference (guides sync process)
**Compliance:** ADR-001 Section 4 ✅
**Changelog:**
- v2.3.0: Auto-commit uncommitted changes before sync (no user prompt needed)
- v2.2.0: Added main branch sync support - pull and push when already on main
- v2.1.0: Initial stable version with feature branch sync
