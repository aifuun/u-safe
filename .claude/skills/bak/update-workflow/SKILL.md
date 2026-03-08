---
name: update-workflow
description: |
  Sync workflow documentation between projects - CLAUDE.md and .claude/workflow/.
  Detects changes, shows diffs, handles framework updates intelligently.
  Essential for workflow best practices propagation.
disable-model-invocation: true
user-invocable: true
argument-hint: "--from <project> | --to <project> [--dry-run] [--files CLAUDE.md,WORKFLOW.md]"
allowed-tools: Read, Glob, Bash(cp *), Bash(diff *), Bash(find *), Bash(wc *), Write
context: fork
agent: general-purpose
---

# Update Workflow - Project Workflow Synchronization

Sync workflow documentation between ai-dev framework and other projects bidirectionally.

## Purpose

**Why This Skill Exists**:
- ✅ Framework workflow updates (propagate best practices)
- ✅ Cross-project learning (adopt workflow improvements)
- ✅ Maintain workflow consistency across projects
- ✅ Detect new/updated workflow files automatically
- ✅ Preview changes before applying (--dry-run)
- ✅ Smart filtering (exclude project-specific files)

---

## Usage

### Pull workflow from another project

```bash
/update-workflow --from ../ai-dev
/update-workflow --from ../ai-dev --dry-run
/update-workflow --from ../ai-dev --files CLAUDE.md,WORKFLOW.md
```

### Push workflow to another project

```bash
/update-workflow --to ../my-app
/update-workflow --to ../my-app --dry-run
/update-workflow --to ../my-app --files workflow/MAIN.md
```

---

## What Gets Synced

### ✅ Included Files (Framework Files)

```
Project Root:
├── CLAUDE.md                    ✅ Main project instructions

.claude/:
├── README.md                    ✅ Framework documentation
├── WORKFLOW.md                  ✅ Quick start guide
└── workflow/                    ✅ Planning templates
    ├── MAIN.md
    ├── PLANNING.md
    ├── TIER.md
    └── TEMPLATES.md
```

### ❌ Excluded Files (Project-Specific)

```
.claude/:
├── settings.json                ❌ Project-specific config
├── MEMORY.md                    ❌ Project-specific knowledge
├── plans/                       ❌ Project-specific plans
├── skills/                      ❌ Managed by update-skills
└── rules/                       ❌ Managed by update-rules

.prot/:
└── pillars/                     ❌ Managed by update-pillars
```

---

## Commands

### 1. Pull Workflow (--from)

**Command**: `/update-workflow --from <project-path>`

**What It Does**:
1. **Scan source project**: Find workflow files in `<project>/`
2. **Compare with current**: Check which files are new or updated
3. **Detect changes**: Compare file sizes, modification times
4. **Show diff**: Display what will change
5. **Confirm**: Ask user to proceed (unless --dry-run)
6. **Copy**: Update current project with new/updated workflow
7. **Report**: Show what was copied/updated

**Example**:
```bash
User: /update-workflow --from ~/dev/ai-dev

AI Response:
📥 Pulling workflow from ~/dev/ai-dev

Scanning workflow files...
✅ Found 5 workflow files in ~/dev/ai-dev
✅ Found 3 workflow files in current project

📊 Analysis by location:
┌──────────────────────────┬────────┬──────────────────┐
│ File                     │ Status │ Action           │
├──────────────────────────┼────────┼──────────────────┤
│ CLAUDE.md                │ NEWER  │ Update           │
│ .claude/README.md        │ SAME   │ Skip             │
│ .claude/WORKFLOW.md      │ NEWER  │ Update           │
│ .claude/workflow/MAIN.md │ NEW    │ Add              │
│ .claude/workflow/TIER.md │ SAME   │ Skip             │
└──────────────────────────┴────────┴──────────────────┘

Summary:
- New files: 1
- Updated files: 2
- Unchanged: 2
- Total to update: 3 files

Proceed? (y/n)
```

---

### 2. Push Workflow (--to)

**Command**: `/update-workflow --to <project-path>`

**What It Does**:
1. **Scan current workflow**: Find all workflow files in current project
2. **Compare with target**: Check which files are new or updated
3. **Show diff**: Display what will change in target project
4. **Confirm**: Ask user to proceed
5. **Copy**: Update target project with new/updated workflow
6. **Report**: Show what was pushed

**Example**:
```bash
User: /update-workflow --to ../my-app

AI Response:
📤 Pushing workflow to ../my-app

Checking target project...
✅ Target exists: ../my-app/

📊 Analysis:
┌──────────────────────────┬────────┬──────────────────┐
│ File                     │ Status │ Action           │
├──────────────────────────┼────────┼──────────────────┤
│ CLAUDE.md                │ NEWER  │ Update           │
│ .claude/README.md        │ NEW    │ Add              │
│ .claude/WORKFLOW.md      │ NEWER  │ Update           │
│ .claude/workflow/MAIN.md │ SAME   │ Skip             │
└──────────────────────────┴────────┴──────────────────┘

Summary:
- New files: 1
- Updated files: 2
- Total to push: 3 files

⚠️  Warning: This will modify ../my-app/

Proceed? (y/n)
```

---

### 3. Dry Run Mode (--dry-run)

**Flag**: `--dry-run`

**What It Does**:
- Shows what would happen WITHOUT making changes
- Perfect for previewing updates
- No confirmation required
- Safe to run anytime

**Example**:
```bash
User: /update-workflow --from ~/dev/ai-dev --dry-run

AI Response:
📥 DRY RUN: Pulling workflow from ~/dev/ai-dev

[Same analysis as above]

Summary:
- New files: 1
- Updated files: 2
- Total to update: 3 files

🔍 DRY RUN MODE - No changes made
Run without --dry-run to apply changes
```

---

### 4. File Filter (--files)

**Flag**: `--files CLAUDE.md,WORKFLOW.md`

**What It Does**:
- Only sync specified files
- Comma-separated list
- Supports partial paths (e.g., "workflow/" matches all in workflow/)
- Ignores other files

**Available Files**:
- `CLAUDE.md` - Main project instructions
- `README.md` - Framework documentation (.claude/README.md)
- `WORKFLOW.md` - Quick start guide (.claude/WORKFLOW.md)
- `workflow/` - All planning templates (.claude/workflow/*.md)
- `workflow/MAIN.md` - Main workflow guide
- `workflow/PLANNING.md` - Planning template
- `workflow/TIER.md` - Tiering system
- `workflow/TEMPLATES.md` - Template library

**Example**:
```bash
User: /update-workflow --from ~/dev/ai-dev --files CLAUDE.md,workflow/

AI Response:
📥 Pulling workflow from ~/dev/ai-dev

Selected files: CLAUDE.md, workflow/

📊 Analysis:
┌──────────────────────────┬────────┬──────────────────┐
│ File                     │ Status │ Action           │
├──────────────────────────┼────────┼──────────────────┤
│ CLAUDE.md                │ NEWER  │ Update           │
│ .claude/workflow/MAIN.md │ NEW    │ Add              │
│ .claude/workflow/TIER.md │ SAME   │ Skip             │
└──────────────────────────┴────────┴──────────────────┘

Skipped files: README.md, WORKFLOW.md

Summary:
- New files: 1
- Updated files: 1
- Total to update: 2 files

Proceed? (y/n)
```

---

## Common Use Cases

### Use Case 1: Framework Workflow Update

```bash
# In your project
cd ~/projects/my-app

# Pull latest workflow from framework
/update-workflow --from ~/dev/ai-dev

# Preview first
/update-workflow --from ~/dev/ai-dev --dry-run

# Update specific files only
/update-workflow --from ~/dev/ai-dev --files CLAUDE.md
```

### Use Case 2: Selective Updates

```bash
# Only update planning templates
cd ~/projects/my-app

/update-workflow --from ~/dev/ai-dev --files workflow/
# → Only updates .claude/workflow/*.md
```

### Use Case 3: Share Workflow Innovations

```bash
# In framework repo
cd ~/dev/ai-dev

# Pull improved workflow from successful project
/update-workflow --from ~/projects/my-app

# Or push framework workflow to new project
/update-workflow --to ~/projects/new-app
```

---

## File Detection Logic

### Smart Filtering

```
Process:
1. Scan source project for workflow files
2. Apply inclusion/exclusion rules
3. Compare with target project
4. Show only relevant changes

Inclusion Rules:
✅ CLAUDE.md
✅ .claude/README.md
✅ .claude/WORKFLOW.md
✅ .claude/workflow/*.md

Exclusion Rules:
❌ .claude/settings.json (project-specific config)
❌ .claude/MEMORY.md (project-specific knowledge)
❌ .claude/plans/ (project-specific plans)
❌ .claude/skills/ (managed by update-skills)
❌ .claude/rules/ (managed by update-rules)
❌ .prot/pillars/ (managed by update-pillars)
```

### File Structure

```
Workflow Files Managed:
CLAUDE.md                          # Root-level project instructions
.claude/
├── README.md                      # Framework overview
├── WORKFLOW.md                    # Quick start entry point
└── workflow/
    ├── MAIN.md                    # Main workflow guide
    ├── PLANNING.md                # Planning template
    ├── TIER.md                    # Tiering system
    └── TEMPLATES.md               # Template library

Not Managed:
.claude/
├── settings.json                  # ❌ Project-specific
├── MEMORY.md                      # ❌ Project-specific
├── plans/                         # ❌ Project-specific
├── skills/                        # ❌ Use update-skills
└── rules/                         # ❌ Use update-rules
```

---

## Safety Features

**Pre-flight Checks**:
- ✅ Source/target paths exist
- ✅ Source has workflow files
- ✅ User confirmation for changes
- ✅ Dry-run mode available
- ✅ Smart file filtering (exclude settings.json, etc.)

**Smart Defaults**:
- Shows diff before applying
- Backup before overwrite (optional)
- Clean error messages
- File-based filtering

**Backup Strategy**:
```bash
# Before overwrite
CLAUDE.md → CLAUDE.md.backup-20260304-153045
```

---

## Error Handling

### Invalid Source/Target

```
❌ Error: Project not found

Path: ../nonexistent
Expected workflow files in: ../nonexistent/

Please check:
1. Path is correct
2. Project has workflow files
3. You have read permissions
```

### No Files to Update

```
✅ All workflow files are up to date!

No new or updated files found in source.
Current project has all latest versions.
```

### Invalid File Pattern

```
❌ Error: Unknown file pattern: invalid-file.md

Valid patterns:
- CLAUDE.md
- README.md
- WORKFLOW.md
- workflow/ (all workflow templates)
- workflow/MAIN.md
- workflow/PLANNING.md
- workflow/TIER.md
- workflow/TEMPLATES.md
```

---

## Best Practices

1. **Always dry-run first**:
```bash
/update-workflow --from ~/dev/ai-dev --dry-run
/update-workflow --from ~/dev/ai-dev
```

2. **File-specific updates**:
```bash
# Only update main instructions
/update-workflow --from ~/dev/ai-dev --files CLAUDE.md

# Only update planning templates
/update-workflow --from ~/dev/ai-dev --files workflow/
```

3. **Framework as source of truth**:
```bash
# In projects: pull from framework
/update-workflow --from ~/dev/ai-dev

# In framework: pull innovations from projects
/update-workflow --from ~/projects/my-app
```

4. **Regular updates**:
```bash
# Weekly/monthly routine
/update-workflow --from ~/dev/ai-dev
```

---

## Integration with Other Skills

```bash
# Complete framework update workflow
/update-pillars --from ~/dev/ai-dev    # 1. Update Pillars
/update-rules --from ~/dev/ai-dev      # 2. Update Rules
/update-workflow --from ~/dev/ai-dev   # 3. Update Workflow
/update-skills --from ~/dev/ai-dev     # 4. Update Skills
```

---

## Quick Reference

```bash
# Pull all workflow
/update-workflow --from ~/dev/ai-dev

# Push all workflow
/update-workflow --to ~/projects/my-app

# Dry run
/update-workflow --from ~/dev/ai-dev --dry-run

# Specific files
/update-workflow --from ~/dev/ai-dev --files CLAUDE.md

# Multiple files
/update-workflow --from ~/dev/ai-dev --files CLAUDE.md,workflow/MAIN.md

# All workflow templates
/update-workflow --from ~/dev/ai-dev --files workflow/
```

---

**Last Updated**: 2026-03-05
**Version**: 1.0
**Status**: Production Ready
