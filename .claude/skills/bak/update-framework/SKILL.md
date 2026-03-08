---
name: update-framework
description: |
  Sync entire framework (Pillars, Rules, Workflow, Skills) between projects in one command.
  Orchestrates all 4 update-* skills for complete framework synchronization.
  Essential for framework upgrades and cross-project consistency.
disable-model-invocation: true
user-invocable: true
argument-hint: "--from <project> | --to <project> [--dry-run] [--skip pillars,rules]"
allowed-tools: Read, Glob, Bash(*), Write
context: fork
agent: general-purpose
---

# Update Framework - Complete Framework Synchronization

Sync all framework components (Pillars, Rules, Workflow, Skills) between projects in one command.

## Purpose

**Why This Skill Exists**:
- ✅ One command for complete framework sync (instead of 4 separate commands)
- ✅ Framework upgrades made easy (pull all updates at once)
- ✅ Initial project setup (push framework to new project)
- ✅ Cross-project learning (share improvements bidirectionally)
- ✅ Consistent sync experience across all components
- ✅ Preview all changes with single --dry-run

---

## Usage

### Pull entire framework from source

```bash
/update-framework --from ~/dev/ai-dev
/update-framework --from ~/dev/ai-dev --dry-run
/update-framework --from ~/dev/ai-dev --skip skills
```

### Push entire framework to target

```bash
/update-framework --to ~/projects/my-app
/update-framework --to ~/projects/my-app --dry-run
/update-framework --to ~/projects/my-app --only pillars,rules
```

---

## What Gets Synced

### Complete Framework (Default)

```
Sync Order (optimized for dependencies):
1. 📚 Pillars    → .prot/pillars/         (Coding standards)
2. 📋 Rules      → .claude/rules/         (Quick reference)
3. 📖 Workflow   → CLAUDE.md + .claude/workflow/  (Process docs)
4. ⚡ Skills     → .claude/skills/        (Command tools)
```

### Component Details

| Component | What It Syncs | Command |
|-----------|---------------|---------|
| **Pillars** | 18 coding standards (.prot/pillars/) | update-pillars |
| **Rules** | 40+ technical rules (.claude/rules/) | update-rules |
| **Workflow** | CLAUDE.md + workflow templates | update-workflow |
| **Skills** | All skills (.claude/skills/) | update-skills |

---

## Commands

### 1. Pull Framework (--from)

**Command**: `/update-framework --from <project-path>`

**What It Does**:
1. **Pulls Pillars** from source project
2. **Pulls Rules** from source project
3. **Pulls Workflow** from source project
4. **Pulls Skills** from source project
5. **Shows aggregated summary** of all changes
6. **Confirms once** before applying all updates

**Example**:
```bash
User: /update-framework --from ~/dev/ai-dev

AI Response:
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

[User types 'y']

━━━ Step 1/4: Syncing Pillars ━━━
✅ Synced Pillar A (Nominal Types)
✅ Synced Pillar K (Testing)

━━━ Step 2/4: Syncing Rules ━━━
✅ Synced core/workflow.md
✅ Synced architecture/clean-architecture.md
✅ Synced backend/lambda.md
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

---

### 2. Push Framework (--to)

**Command**: `/update-framework --to <project-path>`

**What It Does**:
1. **Pushes Pillars** to target project
2. **Pushes Rules** to target project
3. **Pushes Workflow** to target project
4. **Pushes Skills** to target project
5. **Shows aggregated summary** of all changes
6. **Confirms once** before applying all updates

**Example**:
```bash
User: /update-framework --to ~/projects/my-app

AI Response:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📤 Framework Sync: Pushing to ~/projects/my-app
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Analyzing components...

┌────────────┬─────┬─────┬──────┬──────────┐
│ Component  │ New │ Upd │ Same │ Action   │
├────────────┼─────┼─────┼──────┼──────────┤
│ Pillars    │  3  │  0  │   0  │ Add 3    │
│ Rules      │ 15  │  5  │  20  │ Update 20│
│ Workflow   │  4  │  1  │   0  │ Update 5 │
│ Skills     │  8  │  2  │   3  │ Update 10│
└────────────┴─────┴─────┴──────┴──────────┘

📊 Overall Summary:
- New items: 30
- Updated items: 8
- Total to sync: 38 items

⚠️  Warning: This will modify ~/projects/my-app/

Proceed with framework sync? (y/n)
```

---

### 3. Dry Run Mode (--dry-run)

**Flag**: `--dry-run`

**What It Does**:
- Preview all changes across all 4 components
- No confirmation required
- No actual changes made
- Perfect for checking what would happen

**Example**:
```bash
User: /update-framework --from ~/dev/ai-dev --dry-run

AI Response:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 DRY RUN: Framework Sync from ~/dev/ai-dev
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Same analysis as above]

📊 Overall Summary:
- Total to sync: 11 items

🔍 DRY RUN MODE - No changes made
Run without --dry-run to apply changes
```

---

### 4. Selective Sync (--skip / --only)

**Flag**: `--skip pillars,rules` or `--only skills,workflow`

**What It Does**:
- Skip specific components: `--skip pillars,rules`
- Only sync specific components: `--only skills`
- Cannot use both --skip and --only together

**Available Components**:
- `pillars` - Pillar documentation
- `rules` - Technical rules
- `workflow` - Workflow documentation
- `skills` - Skills (commands)

**Examples**:

```bash
# Only update rules and workflow (skip pillars and skills)
User: /update-framework --from ~/dev/ai-dev --only rules,workflow

AI Response:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 Framework Sync: Pulling from ~/dev/ai-dev
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ️  Only syncing: rules, workflow
ℹ️  Skipping: pillars, skills

[Analysis of only rules and workflow]

┌────────────┬─────┬─────┬──────┬──────────┐
│ Component  │ New │ Upd │ Same │ Action   │
├────────────┼─────┼─────┼──────┼──────────┤
│ Rules      │  1  │  3  │  36  │ Update 4 │
│ Workflow   │  1  │  1  │   3  │ Update 2 │
└────────────┴─────┴─────┴──────┴──────────┘

Proceed with partial sync? (y/n)
```

```bash
# Skip skills (update everything except skills)
User: /update-framework --from ~/dev/ai-dev --skip skills

AI Response:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 Framework Sync: Pulling from ~/dev/ai-dev
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ️  Skipping: skills
ℹ️  Syncing: pillars, rules, workflow

[Analysis of pillars, rules, workflow]

Proceed with partial sync? (y/n)
```

---

## Common Use Cases

### Use Case 1: Framework Upgrade (Recommended Monthly)

```bash
# In your project
cd ~/projects/my-app

# Preview what will change
/update-framework --from ~/dev/ai-dev --dry-run

# Apply all updates
/update-framework --from ~/dev/ai-dev

# Result:
# - Latest Pillars (coding standards)
# - Latest Rules (best practices)
# - Latest Workflow (process improvements)
# - Latest Skills (new commands)
```

### Use Case 2: Initial Project Setup

```bash
# In framework repo
cd ~/dev/ai-dev

# Push entire framework to new project
/update-framework --to ~/projects/new-app

# Result: New project has complete framework setup
```

### Use Case 3: Selective Updates

```bash
# Only update documentation (not code tools)
cd ~/projects/my-app

/update-framework --from ~/dev/ai-dev --only pillars,rules,workflow
# → Skip skills, only update documentation

# Only update tools (not documentation)
/update-framework --from ~/dev/ai-dev --only skills
# → Skip pillars/rules/workflow, only update commands
```

### Use Case 4: Cross-Project Learning

```bash
# Share improvements from project back to framework
cd ~/dev/ai-dev

# Preview what's new in project
/update-framework --from ~/projects/my-app --dry-run

# Pull specific improvements
/update-framework --from ~/projects/my-app --only skills
# → Only pull new skills from project
```

---

## Component Sync Order

**Why this order?**

```
1. Pillars     (Foundation - coding standards)
   ↓
2. Rules       (Reference Pillars in examples)
   ↓
3. Workflow    (Uses both Pillars and Rules)
   ↓
4. Skills      (Implements the workflow)
```

**Dependency chain**:
- Rules reference Pillars
- Workflow references Rules and Pillars
- Skills implement Workflow

**Benefit**: Updates flow naturally from foundation to implementation.

---

## Safety Features

**Pre-flight Checks**:
- ✅ Source/target paths exist
- ✅ Source has framework components
- ✅ User confirmation for changes
- ✅ Dry-run mode available
- ✅ Component-by-component status

**Smart Defaults**:
- Aggregated summary before applying
- Single confirmation for all updates
- Progress shown for each step
- Clean error messages
- Backup strategy (inherited from individual update-* skills)

**Error Handling**:
- If one component fails, others continue
- Clear error messages for each component
- Option to retry failed components

---

## Error Handling

### Invalid Source/Target

```
❌ Error: Project not found

Path: ../nonexistent
Expected framework components in: ../nonexistent/

Please check:
1. Path is correct
2. Project has framework components
3. You have read permissions
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

---

## Best Practices

1. **Always dry-run first for major updates**:
```bash
/update-framework --from ~/dev/ai-dev --dry-run
/update-framework --from ~/dev/ai-dev
```

2. **Regular framework upgrades**:
```bash
# Weekly/monthly routine
/update-framework --from ~/dev/ai-dev
```

3. **Selective updates for safety**:
```bash
# Only update documentation first
/update-framework --from ~/dev/ai-dev --only pillars,rules

# Then update tools after testing
/update-framework --from ~/dev/ai-dev --only skills
```

4. **Framework as source of truth**:
```bash
# In projects: pull from framework
/update-framework --from ~/dev/ai-dev

# In framework: pull innovations from projects
/update-framework --from ~/projects/my-app --only skills
```

---

## Integration with Individual Update Skills

**You can still use individual update-* skills**:

```bash
# Fine-grained control
/update-pillars --from ~/dev/ai-dev --pillars A,B,K
/update-rules --from ~/dev/ai-dev --categories core,architecture
/update-workflow --from ~/dev/ai-dev --files CLAUDE.md
/update-skills --from ~/dev/ai-dev --skills adr,review

# Coarse-grained control (this skill)
/update-framework --from ~/dev/ai-dev
```

**When to use update-framework**:
- ✅ Monthly framework upgrades
- ✅ Initial project setup
- ✅ Complete sync needed
- ✅ Want simplicity (one command)

**When to use individual update-* skills**:
- ✅ Only need specific component
- ✅ Need fine-grained filtering (--pillars, --categories, etc.)
- ✅ Testing updates incrementally
- ✅ Debugging sync issues

---

## Quick Reference

```bash
# Pull all framework
/update-framework --from ~/dev/ai-dev

# Push all framework
/update-framework --to ~/projects/my-app

# Dry run
/update-framework --from ~/dev/ai-dev --dry-run

# Only specific components
/update-framework --from ~/dev/ai-dev --only skills,workflow

# Skip specific components
/update-framework --from ~/dev/ai-dev --skip pillars
```

---

## Comparison with Individual Skills

| Task | Individual Skills | update-framework |
|------|-------------------|------------------|
| **Commands needed** | 4 separate commands | 1 command |
| **Confirmations** | 4 prompts | 1 prompt |
| **Time** | ~2 minutes | ~30 seconds |
| **Complexity** | Must remember 4 commands | Simple, memorable |
| **Use case** | Fine-grained control | Complete sync |

---

**Last Updated**: 2026-03-05
**Version**: 1.0
**Status**: Production Ready
