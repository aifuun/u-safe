# Sync - Conflict Resolution Guide

Detailed guide for resolving merge conflicts during branch synchronization.

## Table of Contents

- [When Conflicts Occur](#when-conflicts-occur)
- [Resolution Steps](#resolution-steps)
- [Special Cases](#special-cases)
- [Common Conflict Patterns](#common-conflict-patterns)
- [Prevention Tips](#prevention-tips)

---

## When Conflicts Occur

Conflicts happen when:
- **Same file modified** in both main and feature branch
- **File deleted** in main but modified in feature branch (or vice versa)
- **Dependencies changed** (package.json, package-lock.json differences)
- **Formatting conflicts** (prettier, linting auto-fixes applied differently)

**Expected frequency:**
- Daily syncs: Low (5-10% of syncs)
- Weekly syncs: Medium (20-30% of syncs)
- Monthly syncs: High (50-70% of syncs)

---

## Resolution Steps

### Step 1: Review Conflicts

Identify all conflicted files:

```bash
# See list of conflicted files
git status

# See conflict markers in detail
git diff
```

**Output example:**
```
Unmerged paths:
  (use "git add <file>..." to mark resolution)
	both modified:   src/auth.ts
	both modified:   src/types.ts
	both modified:   package-lock.json
```

### Step 2: Understand Conflict Markers

**Standard conflict format:**

```typescript
<<<<<<< HEAD (your branch)
// Your changes
function login(user: User) {
  return authenticateWithJWT(user);
}
=======
// Changes from main
function login(user: User) {
  return authenticateWithOAuth(user);
}
>>>>>>> origin/main
```

**What each marker means:**
- `<<<<<<< HEAD` - Start of your changes (feature branch)
- `=======` - Separator between versions
- `>>>>>>> origin/main` - End of changes from main branch

### Step 3: Choose Resolution Strategy

**Option A: Keep your changes (ours)**
```bash
git checkout --ours src/auth.ts
git add src/auth.ts
```

**Option B: Take main's changes (theirs)**
```bash
git checkout --theirs src/auth.ts
git add src/auth.ts
```

**Option C: Combine both changes (manual)**
```typescript
// Edit file to combine both:
function login(user: User) {
  // Keep JWT auth but add OAuth fallback
  try {
    return authenticateWithJWT(user);
  } catch {
    return authenticateWithOAuth(user);
  }
}
```

**Option D: Complete rewrite**
```typescript
// Sometimes best to rewrite from scratch:
function login(user: User) {
  // New unified approach
  return authenticateWithProvider(user, 'jwt');
}
```

### Step 4: Edit Conflicted Files

**For each conflicted file:**

1. **Open in editor**
2. **Find conflict markers** (`<<<<<<<`, `=======`, `>>>>>>>`)
3. **Decide which version** to keep (or combine)
4. **Remove all conflict markers**
5. **Test that code is valid** (no syntax errors)

**Example resolution:**

Before:
```typescript
<<<<<<< HEAD
const API_URL = 'http://localhost:3000';
=======
const API_URL = 'https://api.production.com';
>>>>>>> origin/main
```

After:
```typescript
const API_URL = process.env.API_URL || 'http://localhost:3000';
```

### Step 5: Stage Resolved Files

After editing, mark each file as resolved:

```bash
git add src/auth.ts
git add src/types.ts
```

**Verify all resolved:**
```bash
git status
# Should show:
# All conflicts fixed but you are still merging.
#   (use "git commit" to conclude merge)
```

### Step 6: Complete Merge

After all conflicts resolved and staged:

```bash
git commit -m "resolve: merge conflicts from main"
```

**Commit message format:**
- Start with `resolve:` prefix
- Briefly describe what was conflicted
- Example: `resolve: merge conflicts in auth system and types`

### Step 7: Verify Resolution

Test that everything still works:

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
1. Review merged changes carefully
2. Fix failing tests or broken code
3. Commit fixes: `git commit -m "fix: resolve test failures after merge"`
4. Re-run tests until passing

---

## Special Cases

### Package-lock.json Conflicts

**Problem**: Package-lock.json conflicts are common and complex to resolve manually.

**Solution**: Usually safe to regenerate

```bash
# Take their version (main's lock file)
git checkout --theirs package-lock.json

# Regenerate based on package.json
npm install

# Stage regenerated file
git add package-lock.json
```

**Why this works:**
- package-lock.json is derived from package.json
- npm install regenerates it correctly
- No need to manually merge thousands of lines

**When NOT to use:**
- If package.json also has conflicts (resolve that first)
- If specific package versions must be preserved (manually verify)

### Binary File Conflicts

**Problem**: Cannot manually merge binary files (images, PDFs, etc.)

**Solution**: Choose one version

```bash
# Keep your version
git checkout --ours path/to/image.png
git add path/to/image.png

# OR take main's version
git checkout --theirs path/to/image.png
git add path/to/image.png
```

**Common binary files:**
- Images: `.png`, `.jpg`, `.gif`, `.svg`
- Documents: `.pdf`, `.doc`, `.xls`
- Compiled assets: `.wasm`, `.so`, `.dll`

**Best practice:**
- Prefer keeping source files (SVG over PNG)
- Re-export binary from source after merge
- Use version control for source, not generated assets

### Deleted File Conflicts

**Problem**: File deleted in main but modified in your branch

**Git output:**
```
deleted by them: src/old-api.ts
```

**Options:**

**Option A: Keep the file (it's still needed)**
```bash
git add src/old-api.ts
```

**Option B: Confirm deletion (file is obsolete)**
```bash
git rm src/old-api.ts
```

**Decision criteria:**
- If your changes are important: Keep the file, communicate with team
- If file is being removed in main: Accept deletion, migrate your changes elsewhere

### Formatting-Only Conflicts

**Problem**: Same logic, different formatting (prettier, linting)

**Example:**
```typescript
<<<<<<< HEAD
function foo(){return 42;}
=======
function foo() {
  return 42;
}
>>>>>>> origin/main
```

**Solution**: Take main's formatting, re-apply any logic changes

```bash
# Take theirs (formatted version)
git checkout --theirs src/file.ts

# If you had logic changes, manually re-add them
# Then re-format
npm run format

git add src/file.ts
```

---

## Common Conflict Patterns

### Pattern 1: Parallel Feature Development

**Scenario**: Two features modify same function

**Resolution strategy:**
1. Understand both features
2. Combine functionality if compatible
3. Refactor to support both use cases
4. Add tests for combined behavior

### Pattern 2: Refactoring vs Feature

**Scenario**: Main refactored code structure, you added features to old structure

**Resolution strategy:**
1. Accept refactoring from main
2. Re-implement your features in new structure
3. Update imports and dependencies
4. Verify feature still works

### Pattern 3: Dependency Updates

**Scenario**: Different dependency versions in main vs your branch

**Resolution strategy:**
1. Take main's package.json (latest versions)
2. Regenerate package-lock.json
3. Test that your features work with new versions
4. Update code if breaking changes

### Pattern 4: Configuration Changes

**Scenario**: Different config values (tsconfig.json, .env, etc.)

**Resolution strategy:**
1. Review why configs differ
2. Take main's "standard" config
3. Preserve any feature-specific settings
4. Document why custom config is needed

---

## Prevention Tips

### Sync Frequently

```bash
# Daily routine (before starting work)
/sync

# Before lunch
/sync

# End of day
/sync
```

**Why it helps:**
- Smaller diffs = fewer conflicts
- Easier to remember context
- Less time spent resolving

### Communicate with Team

**Before major refactoring:**
1. Announce in team chat
2. Ask others to sync and push WIP
3. Do refactoring
4. Notify when done

**Why it helps:**
- Reduces concurrent modifications
- Team is aware of structural changes
- Conflicts are expected and understood

### Use Feature Flags

**Instead of long-running branches:**

```typescript
// In main branch
if (featureFlags.newAuthFlow) {
  return newAuthenticate(user);
} else {
  return oldAuthenticate(user);
}
```

**Why it helps:**
- No branch divergence
- Gradual rollout
- Easy to revert
- No merge conflicts

### Keep Changes Focused

**One branch = one feature:**
- Don't mix unrelated changes
- Don't refactor while adding features
- Smaller PRs = easier merges

---

**See also:**
- [SKILL.md](SKILL.md) - Main sync workflow
- [Git conflict resolution docs](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging)

---

**Version:** 1.0.0
**Last Updated:** 2026-03-10
