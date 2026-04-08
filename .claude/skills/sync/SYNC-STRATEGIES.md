# Sync Strategies - Advanced Scenarios

Advanced synchronization strategies and edge case handling.

## Overview

This document covers advanced sync scenarios and detailed pre/post-sync checks for the `/sync` skill. For basic sync workflow, see [SKILL.md](SKILL.md).

## Pre-Sync Checks

### 1. Branch State Validation

**Check current branch:**
\`\`\`bash
CURRENT_BRANCH=\$(git rev-parse --abbrev-ref HEAD)

if [ "\$CURRENT_BRANCH" = "main" ]; then
  echo "ℹ️  On main branch - will sync with origin/main"
else
  echo "ℹ️  On feature branch \$CURRENT_BRANCH - will merge main into this branch"
fi
\`\`\`

**Verify remote tracking:**
\`\`\`bash
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null

# If no output, branch not pushed yet
if [ \$? -ne 0 ]; then
  echo "⚠️  Branch not pushed to remote"
  echo "Action: Push first with git push -u origin \$CURRENT_BRANCH"
  exit 1
fi
\`\`\`

### 2. Uncommitted Changes Check

**Detect uncommitted work:**
\`\`\`bash
if ! git diff-index --quiet HEAD --; then
  echo "ℹ️  Uncommitted changes detected"
  echo "Files modified: \$(git diff --name-only | wc -l)"
  echo "Files untracked: \$(git ls-files --others --exclude-standard | wc -l)"
  echo "Action: Auto-committing with WIP message"
fi
\`\`\`

### 3. Behind/Ahead Status

**Check sync status:**
\`\`\`bash
git fetch origin

LOCAL=\$(git rev-parse HEAD)
REMOTE=\$(git rev-parse origin/main)
BASE=\$(git merge-base HEAD origin/main)

if [ "\$LOCAL" = "\$REMOTE" ]; then
  echo "✅ Already up to date"
  exit 0
elif [ "\$LOCAL" = "\$BASE" ]; then
  echo "ℹ️  Behind main by \$(git rev-list --count HEAD..origin/main) commits"
  echo "Fast-forward merge possible"
elif [ "\$REMOTE" = "\$BASE" ]; then
  echo "ℹ️  Ahead of main by \$(git rev-list --count origin/main..HEAD) commits"
  echo "No sync needed (you're ahead)"
else
  echo "ℹ️  Diverged from main"
  echo "Behind: \$(git rev-list --count HEAD..origin/main) commits"
  echo "Ahead: \$(git rev-list --count origin/main..HEAD) commits"
  echo "Merge required"
fi
\`\`\`

## Post-Merge Testing

### 1. Quick Validation Tests

**Run immediately after merge:**
\`\`\`bash
# Check if tests exist
if [ -f "package.json" ] && grep -q "\"test\"" package.json; then
  echo "ℹ️  Running tests..."
  npm test
elif [ -f "pytest.ini" ]; then
  echo "ℹ️  Running Python tests..."
  pytest
elif [ -f "Cargo.toml" ]; then
  echo "ℹ️  Running Rust tests..."
  cargo test
else
  echo "⚠️  No test command found, skipping"
fi
\`\`\`

### 2. Build Verification

**Verify build still works:**
\`\`\`bash
# Check if build command exists
if grep -q "\"build\"" package.json 2>/dev/null; then
  echo "ℹ️  Running build check..."
  npm run build
fi
\`\`\`

### 3. Linting Check

**Run linter to catch issues:**
\`\`\`bash
if grep -q "\"lint\"" package.json 2>/dev/null; then
  echo "ℹ️  Running linter..."
  npm run lint
fi
\`\`\`

## Advanced Scenarios

### Scenario 1: Long-Running Feature Branch

**Problem:** Branch 100+ commits behind main, high conflict risk

**Strategy: Incremental sync**
\`\`\`bash
# Instead of merging all at once, sync in chunks
git fetch origin

# Find midpoint commit between your branch and main
COMMITS_BEHIND=\$(git rev-list --count HEAD..origin/main)
MIDPOINT=\$((COMMITS_BEHIND / 2))

# Merge up to midpoint first
MIDPOINT_COMMIT=\$(git log origin/main --skip=\$MIDPOINT --max-count=1 --format="%H")
git merge \$MIDPOINT_COMMIT

# Resolve conflicts if any
# Then merge the rest
git merge origin/main
\`\`\`

### Scenario 2: Conflicting package.json

**Problem:** Both added different dependencies

**Strategy: Merge dependencies manually**
\`\`\`bash
# 1. Accept main's package.json first
git checkout --theirs package.json

# 2. Manually add your dependencies back
npm install your-package-1 your-package-2

# 3. Regenerate lock file
rm package-lock.json
npm install

# 4. Commit
git add package.json package-lock.json
git commit -m "resolve: merge package.json dependencies"
\`\`\`

### Scenario 3: Main Broke Your Feature

**Problem:** After sync, your feature no longer works due to main's changes

**Strategy: Adapt to breaking changes**
\`\`\`bash
# 1. Identify what changed in main
git log origin/main --since="1 week ago" --oneline

# 2. Check for breaking changes
git diff origin/main~10..origin/main -- src/api/

# 3. Update your code to match new API
# Edit files to adapt

# 4. Run tests to verify
npm test

# 5. Commit fixes
git commit -m "fix: adapt feature to main's API changes"
\`\`\`

### Scenario 4: Emergency Hotfix During Sync

**Problem:** Sync in progress but urgent hotfix needed

**Strategy: Stash and switch**
\`\`\`bash
# If in middle of conflict resolution
git stash --include-untracked

# Switch to main
git checkout main

# Apply hotfix
# ... make changes ...
git commit -m "hotfix: critical bug"
git push origin main

# Return to feature branch
git checkout feature/your-branch

# Resume sync
git stash pop
# Continue resolving conflicts
\`\`\`

### Scenario 5: Sync Failed Midway

**Problem:** Merge started but encountered errors, now in broken state

**Strategy: Abort and retry**
\`\`\`bash
# Check current state
git status

# If in middle of merge
if git merge HEAD >/dev/null 2>&1; then
  # Merge in progress, abort
  git merge --abort
  echo "✅ Merge aborted, working tree restored"
fi

# Alternative: Reset to before sync
git reset --hard origin/\$(git rev-parse --abbrev-ref HEAD)

# Retry sync with different strategy
/sync
\`\`\`

## Performance Optimization

### Large Repositories

**Problem:** Fetch takes very long (10+ minutes)

**Optimization:**
\`\`\`bash
# Use shallow fetch for sync
git fetch --depth=100 origin main

# Or fetch only specific branch
git fetch origin main:refs/remotes/origin/main
\`\`\`

### Many Untracked Files

**Problem:** git status slow due to thousands of untracked files

**Optimization:**
\`\`\`bash
# Update .gitignore first
echo "node_modules/" >> .gitignore
echo "*.log" >> .gitignore
git add .gitignore
git commit -m "chore: update gitignore"

# Then sync
/sync
\`\`\`

## Troubleshooting

### "Not a git repository"

**Cause:** Running sync outside git repo

**Fix:**
\`\`\`bash
cd /path/to/your/repo
/sync
\`\`\`

### "fatal: refusing to merge unrelated histories"

**Cause:** Branch has different history than main

**Fix:**
\`\`\`bash
git merge origin/main --allow-unrelated-histories
\`\`\`

### "error: Your local changes would be overwritten"

**Cause:** Uncommitted changes conflict with merge

**Fix:**
\`\`\`bash
# Auto-commit will handle this, but if manual:
git add .
git commit -m "wip: save work before sync"
/sync
\`\`\`

## Best Practices

1. **Sync before starting work** - Reduces conflicts
2. **Sync after main updates** - Stay current
3. **Test after every sync** - Catch breaking changes early
4. **Communicate large syncs** - Warn team if pushing big merge
5. **Use incremental sync** - For very old branches

## Related Documentation

- **[SKILL.md](SKILL.md)** - Main sync workflow
- **[CONFLICT-HANDLING.md](CONFLICT-HANDLING.md)** - Conflict resolution guide

---

**Version:** 1.0.0
**Last Updated:** 2026-04-07
**Pattern:** Advanced Reference
