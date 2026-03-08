---
name: update-framework
description: |
  Sync entire framework (Pillars, Rules, Workflow, Skills) in one command - meta-skill orchestrating all update-* skills.
  TRIGGER when: user wants complete framework sync ("update framework from X", "sync entire framework", "pull all from framework", "upgrade framework").
  DO NOT TRIGGER when: user wants specific components only (use /update-pillars, /update-rules, /update-workflow, /update-skills), or just wants to read framework docs.
---

# Update Framework - Complete Framework Synchronization Meta-Skill

Sync all framework components (Pillars, Rules, Workflow, Skills) between projects in one command.

## Overview

This meta-skill orchestrates all 4 update-* skills for complete framework synchronization:

**What it does:**
1. Calls update-pillars, update-rules, update-workflow, update-skills in sequence
2. Aggregates analysis from all 4 components
3. Shows unified diff preview
4. Confirms once before syncing everything
5. Executes all 4 syncs with progress updates
6. Reports comprehensive summary

**Why it's needed:**
Monthly framework upgrades require syncing 4 components. Running 4 separate commands with 4 confirmations takes ~2 minutes. This meta-skill does it in one command with one confirmation in ~30 seconds.

**When to use:**
- Monthly framework upgrades (pull all updates)
- Initial project setup (push framework to new project)
- Complete framework sync needed
- Cross-project consistency enforcement

## Workflow

### Step 1: Create Todo List

**Initialize sync tracking** using TaskCreate:

```
Task #1: Validate source and target paths
Task #2: Aggregate component analysis (blocked by #1)
Task #3: Show unified diff preview (blocked by #2)
Task #4: Execute all component syncs (blocked by #3)
Task #5: Collect results from all components (blocked by #4)
Task #6: Report comprehensive summary (blocked by #5)
```

After creating tasks, proceed with meta-sync execution.

## What Gets Synced

### Complete Framework (Default)

```
Sync Order (dependency-optimized):
1. 📚 Pillars    → .prot/pillars/              (Foundation)
2. 📋 Rules      → .claude/rules/              (Reference Pillars)
3. 📖 Workflow   → CLAUDE.md + .claude/workflow/ (Uses Rules)
4. ⚡ Skills     → .claude/skills/             (Implements Workflow)
```

### Component Details

| Component | What Syncs | Delegated Skill |
|-----------|------------|-----------------|
| **Pillars** | 18 coding standards (.prot/pillars/) | /update-pillars |
| **Rules** | 40+ technical rules (.claude/rules/) | /update-rules |
| **Workflow** | CLAUDE.md + workflow templates | /update-workflow |
| **Skills** | All skills (.claude/skills/) | /update-skills |

## Sync Modes

### 1. Pull Framework (--from)

Pull entire framework from source project to current project:

```bash
/update-framework --from ~/dev/ai-dev
/update-framework --from ~/dev/ai-dev --dry-run
/update-framework --from ~/dev/ai-dev --skip skills
```

**What happens:**
1. Validate source path has framework components
2. Call all 4 update-* skills with --from flag
3. Aggregate analysis results
4. Show unified summary table
5. Confirm once
6. Execute all 4 syncs with progress updates

### 2. Push Framework (--to)

Push entire framework from current project to target project:

```bash
/update-framework --to ~/projects/my-app
/update-framework --to ~/projects/my-app --dry-run
/update-framework --to ~/projects/my-app --only pillars,rules
```

**What happens:**
1. Validate target path exists
2. Call all 4 update-* skills with --to flag
3. Aggregate analysis results
4. Show what will be pushed
5. Confirm once
6. Execute all 4 syncs

### 3. Dry Run Mode (--dry-run)

Preview all changes without applying:

```bash
/update-framework --from ~/dev/ai-dev --dry-run
```

**Output:**
- Aggregated analysis from all 4 components
- Shows what would be synced
- No confirmation required
- No actual changes made

### 4. Selective Sync (--skip / --only)

Sync only specific components:

```bash
/update-framework --from ~/dev/ai-dev --only skills,workflow
/update-framework --from ~/dev/ai-dev --skip pillars
```

**Available components:**
- `pillars` - Pillar documentation
- `rules` - Technical rules
- `workflow` - Workflow documentation
- `skills` - Skills (commands)

**Note:** Cannot use both --skip and --only together.

## Orchestration Logic

**How meta-skill delegates to component skills:**

```
For each enabled component:
1. Call respective update-* skill with flags
   - update-pillars --from <source> --dry-run
   - update-rules --from <source> --dry-run
   - update-workflow --from <source> --dry-run
   - update-skills --from <source> --dry-run

2. Capture analysis output from each skill

3. Aggregate into unified summary:
   ┌────────────┬─────┬─────┬──────┬──────────┐
   │ Component  │ New │ Upd │ Same │ Action   │
   ├────────────┼─────┼─────┼──────┼──────────┤
   │ Pillars    │  0  │  2  │   3  │ Update 2 │
   │ Rules      │  1  │  3  │  36  │ Update 4 │
   │ Workflow   │  1  │  1  │   3  │ Update 2 │
   │ Skills     │  2  │  1  │  10  │ Update 3 │
   └────────────┴─────┴─────┴──────┴──────────┘

4. If NOT dry-run, confirm once

5. If confirmed, execute actual sync:
   - update-pillars --from <source>
   - update-rules --from <source>
   - update-workflow --from <source>
   - update-skills --from <source>

6. Collect results and report summary
```

## Analysis Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 Framework Sync: Pulling from ~/dev/ai-dev
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Analyzing components...

┌────────────┬─────┬─────┬──────┬──────────┐
│ Component  │ New │ Upd │ Same │ Action   │
├────────────┼─────┼─────┼──────┼──────────┤
│ Pillars    │  0  │  2  │   3  │ Update 2 │
│ Rules      │  1  │  3  │  36  │ Update 4 │
│ Workflow   │  1  │  1  │   3  │ Update 2 │
│ Skills     │  2  │  1  │  10  │ Update 3 │
└────────────┴─────┴─────┴──────┴──────────┘

📊 Overall Summary:
- New items: 4
- Updated items: 7
- Unchanged: 52
- Total to sync: 11 items

⏱️  Estimated time: 30 seconds

Proceed with framework sync? (y/n)
```

## Execution Output

```
[User confirms with 'y']

━━━ Step 1/4: Syncing Pillars ━━━
✅ Updated Pillar A (Nominal Types)
✅ Updated Pillar K (Testing)

━━━ Step 2/4: Syncing Rules ━━━
✅ Updated core/workflow.md
✅ Updated architecture/clean-architecture.md
✅ Updated backend/lambda.md
✅ Added languages/go.md

━━━ Step 3/4: Syncing Workflow ━━━
✅ Updated CLAUDE.md
✅ Added .claude/workflow/TIER.md

━━━ Step 4/4: Syncing Skills ━━━
✅ Added create-issues skill
✅ Added start-issue skill
✅ Updated review skill

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Framework sync complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Updated:
- 2 Pillars
- 4 Rules
- 2 Workflow files
- 3 Skills

Total: 11 items synced in 28 seconds
```

## Usage Examples

### Example 1: Framework Upgrade (Recommended Monthly)

**User says:**
> "update framework from ai-dev"

**What happens:**
1. Call all 4 update-* skills with --from ~/dev/ai-dev --dry-run
2. Aggregate: 11 items to sync (2 Pillars, 4 Rules, 2 Workflow, 3 Skills)
3. Confirm once
4. Execute all 4 syncs
5. Report: "Updated 11 items in 28 seconds"

**Time:** ~30 seconds

### Example 2: Initial Project Setup

**User says:**
> "push entire framework to my new project at ~/projects/new-app"

**What happens:**
1. `/update-framework --to ~/projects/new-app`
2. Aggregate: 38 NEW items to push
3. Confirm once
4. Execute all 4 pushes
5. Report: "Pushed 38 items"

**Time:** ~45 seconds

### Example 3: Selective Update (Documentation Only)

**User says:**
> "update framework from ai-dev but skip skills"

**What happens:**
1. `/update-framework --from ~/dev/ai-dev --skip skills`
2. Only call update-pillars, update-rules, update-workflow
3. Aggregate: 8 items to sync (skip skills)
4. Confirm and sync
5. Report: "Updated 8 items (skipped skills)"

**Time:** ~20 seconds

### Example 4: Dry Run Preview

**User says:**
> "show me what would change if I pulled framework from ai-dev"

**What happens:**
1. `/update-framework --from ~/dev/ai-dev --dry-run`
2. Call all 4 skills with --dry-run
3. Show aggregated analysis
4. No confirmation, no changes
5. Report: "11 items would be synced (dry run)"

**Time:** ~15 seconds

## Safety Features

**Pre-flight checks:**
- ✅ Source/target paths exist
- ✅ Source has framework components
- ✅ All 4 component skills exist
- ✅ Single confirmation for all updates
- ✅ Dry-run preview available

**Smart defaults:**
- Dependency-aware sync order (Pillars → Rules → Workflow → Skills)
- Aggregated summary before confirmation
- Progress shown for each component
- Clean error messages per component
- Partial failure handling (continue other components)

**Backup protection:**
- Inherited from individual update-* skills
- Each skill creates backups before overwrite
- Timestamped backup directories

## Error Handling

### Invalid Source/Target

```
❌ Error: Project not found

Path: ../nonexistent
Expected framework components in: ../nonexistent/

Please check:
1. Path is correct
2. Project has framework components (.prot/, .claude/)
3. You have read permissions
```

### Missing Component Skills

```
❌ Error: Required skill not found

Missing: update-pillars

This meta-skill requires all 4 component skills:
- update-pillars
- update-rules
- update-workflow
- update-skills

Please ensure all skills are installed.
```

### No Updates Needed

```
✅ All framework components are up to date!

No new or updated items found in source.
Current project has all latest versions.

┌────────────┬─────┬─────┬──────┐
│ Component  │ New │ Upd │ Same │
├────────────┼─────┼─────┼──────┤
│ Pillars    │  0  │  0  │   3  │
│ Rules      │  0  │  0  │  40  │
│ Workflow   │  0  │  0  │   5  │
│ Skills     │  0  │  0  │  12  │
└────────────┴─────┴─────┴──────┘
```

### Partial Failure

```
⚠️  Framework sync completed with warnings

✅ Pillars: Updated 2 items
✅ Rules: Updated 4 items
❌ Workflow: Failed (permission denied)
✅ Skills: Updated 3 items

Summary:
- Successful: 3/4 components
- Failed: 1 component (workflow)

Would you like to retry failed components? (y/n)
```

## Best Practices

1. **Always dry-run first for major updates:**
```bash
/update-framework --from ~/dev/ai-dev --dry-run
/update-framework --from ~/dev/ai-dev
```

2. **Regular framework upgrades:**
```bash
# Weekly/monthly routine
/update-framework --from ~/dev/ai-dev
```

3. **Selective updates for safety:**
```bash
# Only update documentation first
/update-framework --from ~/dev/ai-dev --only pillars,rules,workflow

# Then update tools after testing
/update-framework --from ~/dev/ai-dev --only skills
```

4. **Framework as source of truth:**
```bash
# In projects: pull from framework
/update-framework --from ~/dev/ai-dev

# In framework: pull innovations from projects
/update-framework --from ~/projects/my-app --only skills
```

## Integration with Component Skills

**You can still use individual update-* skills:**

```bash
# Fine-grained control
/update-pillars --from ~/dev/ai-dev --pillars A,B,K
/update-rules --from ~/dev/ai-dev --categories core,architecture
/update-workflow --from ~/dev/ai-dev --files CLAUDE.md
/update-skills --from ~/dev/ai-dev --skills adr,review

# Coarse-grained control (this meta-skill)
/update-framework --from ~/dev/ai-dev
```

**When to use update-framework:**
- ✅ Monthly framework upgrades
- ✅ Initial project setup
- ✅ Complete sync needed
- ✅ Want simplicity (one command)

**When to use individual update-* skills:**
- ✅ Only need specific component
- ✅ Need fine-grained filtering (--pillars, --categories, etc.)
- ✅ Testing updates incrementally
- ✅ Debugging sync issues

## Task Management

**After each meta-sync step**, update progress:

```
Paths validated → Update Task #1
Component analysis aggregated → Update Task #2
Unified diff shown → Update Task #3
All component syncs executed → Update Task #4
Results collected → Update Task #5
Summary reported → Update Task #6
```

Provides real-time visibility of meta-sync progress.

## Final Verification

**Before declaring sync complete**, verify:

```
- [ ] All 6 meta-sync tasks completed
- [ ] Source and target paths valid
- [ ] All 4 component skills called successfully
- [ ] User confirmed unified changes
- [ ] All components synced (or partial failure reported)
- [ ] Comprehensive summary displayed
```

Missing items indicate incomplete meta-sync.

## Comparison with Individual Skills

| Aspect | Individual Skills | update-framework |
|--------|-------------------|------------------|
| **Commands** | 4 separate | 1 command |
| **Confirmations** | 4 prompts | 1 prompt |
| **Time** | ~2 minutes | ~30 seconds |
| **Complexity** | Must remember 4 | Simple, memorable |
| **Use case** | Fine-grained | Complete sync |

## Related Skills

- **/update-pillars** - Sync Pillars (called by this meta-skill)
- **/update-rules** - Sync rules (called by this meta-skill)
- **/update-workflow** - Sync workflow docs (called by this meta-skill)
- **/update-skills** - Sync skills (called by this meta-skill)

---

**Version:** 2.1.0
**Pattern:** Meta-Skill (orchestrates other skills)
**Compliance:** ADR-001 Section 4 ✅
