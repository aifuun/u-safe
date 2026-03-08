---
name: resume
description: |
  Resume work after interruption - pull latest changes, resolve conflicts, load context.
  Quickly get back up to speed.
disable-model-invocation: true
user-invocable: true
allowed-tools: Read, Bash(git *), Bash(npm *)
context: fork
agent: Explore
---

# Work Resumer

Resume your work after stepping away from the project.

## Task

Get back to work safely with live environment check:
1. **Fetch latest** - Pull changes from remote (LIVE)
2. **Detect conflicts** - Warn if merging needed (LIVE)
3. **Reload context** - Load previous plans and memory (LIVE)
4. **Verify environment** - Deps installed, tests passing (LIVE)
5. **Summary** - What changed while you were away? (LIVE)

## Live Environment Status

### Git State
- **Current Branch**: !`git rev-parse --abbrev-ref HEAD`
- **Latest Remote**: !`git ls-remote origin HEAD | awk '{print $2}' | sed 's|refs/heads/||'`
- **Commits Behind**: !`git rev-list --count HEAD..origin/main 2>/dev/null || echo "0"`

### Conflict Detection
Branch comparison with main:
!`if git merge-base --is-ancestor origin/main HEAD 2>/dev/null; then echo "✅ Branch is up to date"; else echo "⚠️ Main has new commits - merge needed"; fi`

### Context Files
- **MEMORY.md**: !`if [ -f .claude/MEMORY.md ]; then echo "✅ Found ($(wc -l < .claude/MEMORY.md) lines)"; else echo "❌ Not found"; fi`
- **Active Plans**: !`if [ -d .claude/plans/active ]; then echo "✅ Found ($(ls -1 .claude/plans/active/*.md 2>/dev/null | wc -l) plans)"; else echo "❌ No plans directory"; fi`

### Environment Check
- **Dependencies**: !`if [ -f package.json ] && npm list &>/dev/null; then echo "✅ Dependencies OK"; else echo "⚠️ May need npm install"; fi`
- **Git Status**: !`if [ -z "$(git status --porcelain)" ]; then echo "✅ Working directory clean"; else echo "⚠️ Uncommitted changes"; fi`

## Output

```markdown
# 🚀 Resuming Work

## Git Status
✅ Pulled latest changes
- main: 3 new commits from team
- Your branch: feature/auth
- No conflicts detected

## Context Loaded
- Active plan: User Authentication (4/8 done)
- Previous task: Implement JWT tokens
- MEMORY updated: 5 new notes from team

## Environment
✅ Dependencies up to date
✅ Tests passing (24/24)
✅ Dev server ready

## Summary
While you were away:
- 3 commits merged to main (auth, database, docs)
- 2 new issues created
- Team reviewed your PR #15

## Next Steps
1. Continue task #4: JWT Token Generation
2. Or sync with team on changes

Run: /next
```

---

Safe resume workflow to:
- Avoid merge conflicts
- Get context back
- Verify everything works
- Know what changed
