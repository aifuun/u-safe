# Update Framework - Advanced Topics

Detailed orchestration logic, execution patterns, and output examples for the update-framework meta-skill.

## Table of Contents

- [Orchestration Logic](#orchestration-logic)
- [Analysis Output](#analysis-output)
- [Execution Output](#execution-output)
- [Partial Failure Recovery](#partial-failure-recovery)

---

## Orchestration Logic

**How the meta-skill delegates to component skills:**

### Step-by-Step Delegation Flow

```
For each enabled component:

1. Call respective update-* skill with flags
   - update-pillars <target> --dry-run
   - update-guides <target> --dry-run
   - update-skills <target> --dry-run

2. Capture analysis output from each skill
   - Parse component-specific change counts
   - Extract new, updated, and unchanged items
   - Collect any warnings or errors

3. Aggregate into unified summary table:
   ┌────────────┬─────┬─────┬──────┬──────────┐
   │ Component  │ New │ Upd │ Same │ Action   │
   ├────────────┼─────┼─────┼──────┼──────────┤
   │ Pillars    │  0  │  2  │   3  │ Update 2 │
   │ Guides     │  1  │  3  │  16  │ Update 4 │
   │ Skills     │  2  │  1  │  10  │ Update 3 │
   └────────────┴─────┴─────┴──────┴──────────┘

4. If NOT dry-run, confirm once
   - Show unified summary to user
   - Single y/n confirmation for all components
   - No per-component confirmations

5. If confirmed, execute actual sync:
   - update-pillars <target>
   - update-guides <target>
   - update-skills <target>

6. Collect results and report comprehensive summary
   - Count total items synced
   - Report sync time
   - Show any warnings or errors
```

### Dependency-Aware Sync Order

Components are synced in this order to respect dependencies:

```
1. Pillars (Foundation)
   ↓ (Rules reference Pillars)
2. Rules (Reference layer)
   ↓ (Workflow uses Rules)
3. Workflow (Process documentation)
   ↓ (Skills implement Workflow)
4. Skills (Automation layer)
```

**Why this matters:**
- Rules may reference Pillar concepts
- Workflow documentation may cite specific rules
- Skills implement workflows and may reference rules

### Smart Filtering Pass-Through

When tech stack configuration exists:

```
1. Load .claude/framework-config.json from target
2. Extract filterConfig section
3. Pass filterConfig to each update-* skill:
   - update-rules receives rules.include_categories, rules.exclude_patterns
   - update-skills receives skills.exclude list
   - Pillars and Workflow: no filtering (all synced)
4. Each skill applies its own filtering logic
5. Meta-skill aggregates filtered results
```

---

## Analysis Output

**Complete analysis example showing all components:**

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

### Analysis with Smart Filtering

**When tech stack filtering is active:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 Framework Sync: Pulling from ~/dev/ai-dev
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Smart Filtering Active (Tauri + React + No Cloud)

┌────────────┬─────┬─────┬──────┬──────────┬──────────┐
│ Component  │ New │ Upd │ Same │ Filtered │ Action   │
├────────────┼─────┼─────┼──────┼──────────┼──────────┤
│ Pillars    │  0  │  2  │   3  │    0     │ Update 2 │
│ Rules      │  1  │  3  │  21  │   18     │ Update 4 │
│ Workflow   │  1  │  1  │   3  │    0     │ Update 2 │
│ Skills     │  0  │  1  │  15  │    0     │ Update 1 │
└────────────┴─────┴─────┴──────┴──────────┴──────────┘

📊 Overall Summary:
- New items: 2
- Updated items: 7
- Unchanged: 42
- Filtered out: 18 (AWS/Lambda rules not needed)
- Total to sync: 9 items

⏱️  Estimated time: 25 seconds

Proceed with framework sync? (y/n)
```

---

## Execution Output

**Complete execution example showing all 4 component syncs:**

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

### Execution with Filtering

**When smart filtering excludes items:**

```
[User confirms with 'y']

━━━ Step 1/4: Syncing Pillars ━━━
✅ Updated Pillar A (Nominal Types)
✅ Updated Pillar K (Testing)

━━━ Step 2/4: Syncing Rules ━━━
✅ Updated core/workflow.md
✅ Updated frontend/react.md
⏭️  Skipped backend/lambda-*.md (3 files, not in tech stack)
⏭️  Skipped infrastructure/aws-*.md (5 files, not in tech stack)
⏭️  Skipped infrastructure/cdk-*.md (3 files, not in tech stack)

━━━ Step 3/4: Syncing Workflow ━━━
✅ Updated CLAUDE.md

━━━ Step 4/4: Syncing Skills ━━━
✅ Updated review skill

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Framework sync complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Updated:
- 2 Pillars
- 2 Rules (11 filtered out based on tech stack)
- 1 Workflow file
- 1 Skill

Total: 6 items synced (18 filtered) in 18 seconds
```

---

## Partial Failure Recovery

**When one or more components fail:**

```
⚠️  Framework sync completed with warnings

✅ Pillars: Updated 2 items
✅ Rules: Updated 4 items
❌ Workflow: Failed (permission denied on CLAUDE.md)
✅ Skills: Updated 3 items

Summary:
- Successful: 3/4 components
- Failed: 1 component (workflow)

Would you like to retry failed components? (y/n)
```

**If user confirms retry:**

```
Retrying failed components...

━━━ Retrying Workflow Sync ━━━
❌ Still failing: Permission denied

Please fix the permission issue and run:
  cd ~/dev/ai-dev
  /update-guides ../my-app

Or retry entire framework sync:
  cd ~/dev/ai-dev
  /update-framework ../my-app --only guides
```

### Graceful Degradation

**The meta-skill continues even if one component fails:**

1. **Detect failure** during component sync
2. **Log error** with component name
3. **Continue** with remaining components
4. **Report** partial success at end
5. **Offer retry** for failed components only

**Why this matters:**
- One component failure doesn't block others
- User gets partial updates immediately
- Can retry failed components separately
- Clear error messages for debugging

---

**See also:**
- [SKILL.md](SKILL.md) - Main skill documentation
- [FILTERING.md](FILTERING.md) - Tech stack questionnaire and filtering logic

---

**Version:** 1.0.0
**Last Updated:** 2026-03-10
