# Sync with Remote Reference Guide

Complete guide for the `/sync` skill covering merge workflows, conflict resolution, and best practices.

## When to Use `/sync`

- **Regular team updates** - Daily sync with main
- **Before deployment** - Ensure up-to-date with main
- **Multi-day features** - Keep branch fresh
- **Team collaboration** - Integrate changes frequently
- **Release preparation** - Final merge before release

## Command Usage

```bash
/sync              # Safe merge of main into current branch
```

The skill:
1. Shows merge preview (what will change)
2. Detects potential conflicts
3. Checks test status
4. Merges and handles conflicts
5. Pushes to remote

## Merge Workflow

### Before Sync

**Check current state:**
```bash
git status                           # What you've changed
git log origin/main..HEAD            # Your commits vs main
git diff origin/main...HEAD --stat   # Impact preview
```

### During Sync

The `/sync` skill:
1. **Fetches** - Gets latest from remote
2. **Merges** - Merges main into your branch
3. **Handles Conflicts** - Lists conflicted files
4. **Tests** - Runs tests to verify merge
5. **Pushes** - Pushes updated branch to remote

### After Sync

**Verify success:**
```bash
git log --oneline -5               # See merge commit
git branch -vv                     # Check tracking
```

## Conflict Resolution

### Understanding Conflicts

When `/sync` encounters conflicts, it shows:

```
⚠️ Merge conflicts found in:
- src/auth.ts (2 conflicts)
- src/types.ts (1 conflict)

Conflicted sections marked with:
<<<<<<< HEAD        (your changes)
=======             (conflict separator)
>>>>>>> origin/main (main's changes)
```

### Resolving Conflicts

**Step 1: Open conflicted files**
```typescript
// src/auth.ts (with conflicts)

<<<<<<< HEAD
export const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret';
=======
export const JWT_SECRET = process.env.JWT_SECRET!;
>>>>>>> origin/main
```

**Step 2: Choose the correct version**
```typescript
// ✅ Resolved: Keep main's stricter version
export const JWT_SECRET = process.env.JWT_SECRET!;
```

**Step 3: Mark as resolved and commit**
```bash
git add src/auth.ts
git commit -m "resolve conflicts: keep stricter JWT_SECRET"
```

### Common Conflict Patterns

#### Pattern 1: Dependency Conflicts
```json
// package.json
<<<<<<< HEAD
"react": "^18.2.0"
=======
"react": "^19.0.0"
>>>>>>> origin/main
```

**Resolution:** Usually take main's version
```json
"react": "^19.0.0"
```

#### Pattern 2: Feature Conflicts
```typescript
// User model
<<<<<<< HEAD
interface User {
  id: string;
  name: string;
  email: string;
  premium: boolean;  // Your addition
}
=======
interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';  // Main's addition
}
>>>>>>> origin/main
```

**Resolution:** Combine both changes
```typescript
interface User {
  id: string;
  name: string;
  email: string;
  premium: boolean;
  role: 'admin' | 'user';
}
```

#### Pattern 3: Migration/Schema Conflicts
```typescript
// Database migrations
<<<<<<< HEAD
migration_005_add_premium_field.sql
=======
migration_005_add_role_field.sql
>>>>>>> origin/main
```

**Resolution:** Rename and reorder
```
migration_005_add_premium_field.sql
migration_006_add_role_field.sql
```

## Preventing Conflicts

### Best Practices

1. **Sync Daily** - Small, frequent syncs are easier
2. **Small Branches** - Keep feature branches focused
3. **Communicate** - Tell team about big changes
4. **Code Review** - Review changes before main
5. **Test Early** - Run tests after sync

### Git Workflow

```
1. Create branch from main
   git checkout -b feature/auth

2. Work on feature (1-3 days max)
   git add .
   git commit -m "feat: add OAuth"

3. Keep fresh with /sync
   /sync              # Daily or every 2 days

4. Merge back when ready
   Create PR, get review, merge to main
```

## Troubleshooting

### Issue: Merge Conflicts Won't Resolve

**Symptom:** Conflicts keep appearing even after fixing
**Cause:** Files are still marked as conflicted
**Solution:** 
```bash
git add <resolved-files>
git commit -m "resolve conflicts"
# Then sync again
```

### Issue: Tests Fail After Merge

**Symptom:** Tests passing before sync, failing after
**Cause:** Compatibility issues between branches
**Solution:**
```bash
# Debug the specific test
npm test -- --testNamePattern="failing test"

# Fix compatibility issues
# Usually dependency version mismatch or API changes

# Commit fix
git add .
git commit -m "fix test compatibility with main"
```

### Issue: Push Rejected

**Symptom:** `git push` says "rejected (non-fast-forward)"
**Cause:** Someone pushed to main while you were syncing
**Solution:**
```bash
# Fetch latest and sync again
/sync
```

### Issue: Lost Work After Merge

**Symptom:** Your changes disappeared
**Cause:** Chose wrong conflict resolution
**Solution:**
```bash
git reflog                    # Find your previous state
git reset --hard <commit>     # Go back to before merge
# Manually re-do the merge, being more careful

# Or use git merge --abort to restart
git merge --abort
# Then try again more carefully
```

## Advanced Sync Scenarios

### Scenario 1: Many Commits Piled Up

**Situation:** Main has 20+ commits since your branch

**Approach:**
```bash
/sync                         # Let it handle the merge
# If too complex, consider squashing

# Or interactive rebase
git rebase -i origin/main
# Pick first commit, squash others
```

### Scenario 2: Rebasing vs Merging

**Merge** (default with `/sync`):
```
* (main) Latest commit
|\ 
| * (your-branch) Your work
| * Previous commit
* | Main commit
|/
* Base commit
```

**Rebase** (alternative):
```
* (main) Latest commit
* (your-branch) Your work
* Previous commit
* Main commit
* Base commit
```

Choose merge if you want history; rebase for cleaner timeline.

### Scenario 3: Recovering from Bad Merge

**If merge went wrong:**
```bash
git reset --hard HEAD~1       # Undo merge commit
# Fix the issue
/sync                         # Try again
```

## Live Merge Preview

When you run `/sync`, it shows:
```
### Merge Preview
Changes between main and your branch:
- src/auth.ts (45 lines added)
- src/types.ts (12 lines modified)
- package.json (2 lines modified)

### Potential Conflicts
- src/auth.ts (modified on both sides)
- src/types.ts (modified on both sides)
```

This helps you prepare mentally before the merge.

## Pro Tips

1. **Merge Often** - 1-2 times per day keeps branches fresh
2. **Small PRs** - Fewer conflicts if changes are scoped
3. **Communicate** - Let team know about big changes
4. **Keep Main Stable** - Don't merge breaking changes to main
5. **Test After Merge** - Always run tests post-sync

## Integration with Workflow

```
1. Check status: /status
   ↓
2. Get next task: /next
   ↓
3. Work on feature
   ↓
4. Keep fresh: /sync (daily)
   ↓
5. When done: Create PR
   ↓
6. Review & merge
```

## Git Commands Reference

```bash
# View merge status
git status

# See what would merge
git diff origin/main...HEAD

# View commits in your branch
git log origin/main..HEAD

# Clean up after bad merge
git merge --abort
git reset --hard origin/your-branch

# Check for conflicts before sync
git merge --no-commit --no-ff origin/main
git merge --abort
```
