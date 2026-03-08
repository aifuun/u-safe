---
name: sync
description: |
  Sync with remote - merge main, handle conflicts, push changes.
  Complex git workflow automation with safety checks.
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash(git *), Read
context: fork
agent: general-purpose
---

# Git Synchronizer

Safe synchronization with remote repository.

## Task

Sync your branch with main (with live status):
1. **Fetch** - Get latest from remote (LIVE)
2. **Merge** - Merge main into your branch (LIVE)
3. **Resolve** - Handle any conflicts (LIVE)
4. **Test** - Verify nothing broke
5. **Push** - Push to remote

## Live Sync Status

### Current State
- **Your Branch**: !`git rev-parse --abbrev-ref HEAD`
- **Your Commit**: !`git rev-parse --short HEAD`
- **Main Latest**: !`git rev-parse --short origin/main 2>/dev/null || echo "unknown"`

### Merge Preview
Changes between main and your branch:
!`git diff origin/main...HEAD --stat 2>/dev/null || echo "Cannot fetch main for comparison"`

### Potential Conflicts
Files that might conflict:
!`git diff --name-only origin/main...HEAD 2>/dev/null | head -10 || echo "No merge data available"`

### Tests Status
!`if [ -f package.json ]; then if npm list &>/dev/null; then echo "✅ Dependencies ready"; else echo "⚠️ npm install may be needed"; fi; else echo "No package.json found"; fi`

## Workflow

Execute: `bash scripts/sync.sh`

### Steps
1. `git fetch origin` - Get latest
2. `git merge origin/main` - Merge main into your branch
3. If conflicts appear:
   - List conflicted files
   - Show merge helper commands
   - Wait for manual resolution
4. Run tests to verify
5. `git push origin <branch>` - Push changes

## Conflict Handling

If conflicts detected:
```
⚠️ Merge conflicts found in:
- src/auth.ts (2 conflicts)
- src/types.ts (1 conflict)

Resolve with:
1. Edit files to fix conflicts
2. Run: git add <resolved-files>
3. Run: git commit -m "resolve conflicts"
4. Then: sync --continue
```

## Safety Features

- Won't push if tests failing
- Asks confirmation before force operations
- Creates backup branch before major changes
- Detects untracked files that might conflict

---

Ensures:
- Safe merging with main
- No lost work
- Team sync
- Ready to push
