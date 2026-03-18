# Preflight Check Integration with work-issue

## Integration Point

**Phase 0** (NEW): Preflight check runs BEFORE Phase 1 (/start-issue)

## Updated work-issue Workflow

```
Phase 0: /preflight-check (NEW)
  ├─ If ✅ READY → Continue to Phase 1
  ├─ If ❌ BLOCKED → Stop, show fix commands
  └─ If ⚠️ WARNINGS → Warn user, optionally continue

Phase 1: /start-issue
Phase 1.5: /eval-plan
Phase 2: /execute-plan
Phase 2.5: /review
Phase 3: /finish-issue
```

## Implementation in work-issue SKILL.md

Add the following section to work-issue SKILL.md after "AI Execution Instructions":

```markdown
### Step 0: Preflight Check (NEW)

**Before starting Phase 1**, AI MUST run preflight check:

\`\`\`python
# Run preflight check
preflight_result = Skill("preflight-check")

# Parse result
if "BLOCKED" in preflight_result:
    print("❌ Preflight check failed. Fix issues before proceeding:")
    print(preflight_result)
    return  # Stop workflow

if "WARNINGS" in preflight_result:
    print("⚠️ Preflight check completed with warnings:")
    print(preflight_result)
    # Continue but warn user

# If READY, proceed to Phase 1
print("✅ Preflight check passed")
\`\`\`

**Checks performed:**
- Permissions configured (.claude/settings.json)
- Framework directories exist (.claude/, .prot/)
- Git environment clean (on main, no uncommitted changes)
- GitHub CLI authenticated
- Dependencies installed (node_modules/)

**Auto-fixes applied:**
- Configure permissions (if missing)
- Create framework directories
- Stash uncommitted changes
- Install dependencies (if confirmed)

**Time**: 2-5 seconds (parallel execution)

**If blocked**: Fix issues manually and re-run /work-issue
```

## work-issue SKILL.md Modifications

### 1. Update Overview Section

Add Phase 0 to the workflow diagram:

```markdown
**Workflow:**
0. **Phase 0**: `/preflight-check` - Environment validation (NEW)
1. **Phase 1**: `/start-issue` - Branch + plan
2. **Phase 1.5**: `/eval-plan` - Validate plan (automated)
3. **Checkpoint 1**: Review eval results, edit plan if needed
4. **Phase 2**: `/execute-plan` - Implementation
5. **Phase 2.5**: `/review` - Validate code (automated)
6. **Checkpoint 2**: Review quality results, fix if needed
7. **Phase 3**: `/finish-issue` - Commit + PR + merge
```

### 2. Update Continuous Execution Pattern

Add Phase 0 to the execution loop:

```python
# Step 0: Display Startup Message
display_startup_message(mode, issue_number)

# Phase 0: Preflight Check (NEW)
Skill("preflight-check")
# ✅ Phase 0 complete → Check for blockers

# Phase 1: Start Issue
Skill("start-issue", args=str(issue_number))
# ...rest of workflow...
```

### 3. Update Examples

Add Phase 0 to all workflow examples:

```markdown
### Example 1: Default Mode (Auto)

\`\`\`bash
/work-issue #23

→ Phase 0: /preflight-check... ✅ (3.2s)
→ Phase 1: /start-issue... ✅
→ Phase 1.5: /eval-plan... ✅ (Score: 92/100)
→ Phase 2: /execute-plan... ✅
→ Phase 2.5: /review... ✅ (Score: 98/100)
→ Phase 3: /finish-issue... ✅

✅ Issue #23 complete! (35 min total)
\`\`\`
```

## Error Handling

### Preflight Blocked

```
❌ Preflight Check Failed

Issues:
- GitHub CLI not authenticated (Fix: gh auth login)
- Working directory dirty (Fix: git stash)

Cannot proceed with work-issue until fixed.

Re-run after fixing: /work-issue #23
```

### Preflight Warnings

```
⚠️ Preflight Check Warnings

Warnings:
- npm test script not found (recommended)
- src/ directory not found (project structure)

Proceeding anyway (non-blocking)...

→ Phase 1: /start-issue... ✅
```

## Batch Processing Integration

**Batch mode behavior:**

```python
for issue in [128, 184, 33]:
    # Run preflight once before batch (not per issue)
    if first_issue:
        preflight_result = Skill("preflight-check")
        if "BLOCKED" in preflight_result:
            print(f"❌ Batch stopped: Preflight check failed")
            break

    # Proceed with issue
    Skill("work-issue", args=str(issue))
```

**Optimization**: Preflight runs once for batch, not per issue.

## Testing

### Test 1: Clean Environment

```bash
/work-issue #23

→ Phase 0: /preflight-check... ✅ All checks passed (2.8s)
→ Phase 1: /start-issue... ✅
# ... workflow continues normally ...
```

### Test 2: First-Time Setup

```bash
/work-issue #23

→ Phase 0: /preflight-check...
   🔧 Auto-fixing:
      🔧 Permissions not configured → /configure-permissions --safe (2s)
      🔧 .claude/plans/ missing → Created directories (0.1s)
      🔧 node_modules missing → npm install (45s)
   ✅ Preflight ready (49s)

→ Phase 1: /start-issue... ✅
# ... workflow continues ...
```

### Test 3: Blocked State

```bash
/work-issue #23

→ Phase 0: /preflight-check... ❌ BLOCKED

Issues:
  ❌ GitHub CLI not authenticated
     Fix: gh auth login

Cannot proceed. Fix issues and re-run: /work-issue #23
```

## Performance Impact

| Phase | Before | After (with preflight) | Difference |
|-------|--------|----------------------|------------|
| **Startup** | 0s | 3-5s | +3-5s |
| **Total (clean)** | 35 min | 35 min 5s | +0.2% |
| **Total (first-time)** | 35 min + manual fixes | 35 min 50s | Automated |

**Impact**: Minimal overhead (2-5s) for significant reliability improvement.

## Related Documentation

- **Preflight Check SKILL.md**: `/Users/woo/dev/ai-dev-246-implement-preflight-check-system-for-work-issue/.claude/skills/preflight-check/SKILL.md`
- **work-issue SKILL.md**: `.claude/skills/work-issue/SKILL.md`
- **configure-permissions**: `.claude/skills/configure-permissions/SKILL.md`
