---
name: update-rules
description: |
  Sync technical rules between projects - copy from or push to other projects.
  Detects new/updated rules, shows diffs, handles conflicts intelligently.
  Essential for framework rule updates and best practices propagation.
disable-model-invocation: true
user-invocable: true
argument-hint: "--from <project> | --to <project> [--dry-run] [--categories core,architecture]"
allowed-tools: Read, Glob, Bash(cp *), Bash(diff *), Bash(find *), Bash(wc *), Write
context: fork
agent: general-purpose
---

# Update Rules - Project Technical Rules Synchronization

Sync technical rules between ai-dev framework and other projects bidirectionally.

## Purpose

**Why This Skill Exists**:
- ✅ Framework rule updates (propagate best practices)
- ✅ Cross-project learning (adopt rule improvements)
- ✅ Maintain rule consistency across projects
- ✅ Detect new/updated rules automatically
- ✅ Preview changes before applying (--dry-run)
- ✅ Category-based filtering (core, architecture, etc.)

---

## Usage

### Pull rules from another project

```bash
/update-rules --from ../ai-dev
/update-rules --from ../ai-dev --dry-run
/update-rules --from ../ai-dev --categories core,architecture
```

### Push rules to another project

```bash
/update-rules --to ../my-app
/update-rules --to ../my-app --dry-run
/update-rules --to ../my-app --categories languages,frontend
```

---

## Rule Categories

```
.claude/rules/
├── core/                    # Workflow, naming, debugging
├── architecture/            # Clean architecture, layers
├── languages/               # TypeScript, Python, Go
├── frontend/                # React, state management
├── backend/                 # Lambda, API design
├── infrastructure/          # AWS CDK, secrets
└── development/             # Performance, security
```

---

## Commands

### 1. Pull Rules (--from)

**Command**: `/update-rules --from <project-path>`

**What It Does**:
1. **Scan source project**: Find all rules in `<project>/.claude/rules/`
2. **Compare with current**: Check which rules are new or updated
3. **Detect changes**: Compare file sizes, modification times
4. **Show diff**: Display what will change
5. **Confirm**: Ask user to proceed (unless --dry-run)
6. **Copy**: Update current project with new/updated rules
7. **Report**: Show what was copied/updated

**Example**:
```bash
User: /update-rules --from ~/dev/ai-dev

AI Response:
📥 Pulling rules from ~/dev/ai-dev

Scanning rules...
✅ Found 42 rules in ~/dev/ai-dev/.claude/rules/
✅ Found 38 rules in current project

📊 Analysis by category:
┌────────────────┬─────┬─────┬──────┐
│ Category       │ New │ Upd │ Same │
├────────────────┼─────┼─────┼──────┤
│ core           │  0  │  1  │   6  │
│ architecture   │  0  │  2  │   5  │
│ languages      │  1  │  0  │   2  │
│ frontend       │  1  │  1  │   4  │
│ backend        │  2  │  0  │   3  │
│ infrastructure │  0  │  1  │   9  │
│ development    │  0  │  0  │   2  │
└────────────────┴─────┴─────┴──────┘

Summary:
- New rules: 4
- Updated rules: 5
- Unchanged: 33
- Total to update: 9 rules

Proceed? (y/n)
```

---

### 2. Push Rules (--to)

**Command**: `/update-rules --to <project-path>`

**What It Does**:
1. **Scan current rules**: Find all rules in current project
2. **Compare with target**: Check which rules are new or updated
3. **Show diff**: Display what will change in target project
4. **Confirm**: Ask user to proceed
5. **Copy**: Update target project with new/updated rules
6. **Report**: Show what was pushed

**Example**:
```bash
User: /update-rules --to ../my-app --categories backend

AI Response:
📤 Pushing rules to ../my-app

Selected categories: backend

Checking target project...
✅ Target exists: ../my-app/.claude/rules/

📊 Analysis (backend category):
┌─────────────────────┬────────┬──────────────┐
│ Rule                │ Status │ Action       │
├─────────────────────┼────────┼──────────────┤
│ lambda.md           │ NEWER  │ Update       │
│ api-design.md       │ SAME   │ Skip         │
│ saga.md             │ NEW    │ Add          │
│ error-handling.md   │ NEWER  │ Update       │
└─────────────────────┴────────┴──────────────┘

Summary:
- New rules: 1
- Updated rules: 2
- Total to push: 3 rules

⚠️  Warning: This will modify ../my-app/.claude/rules/

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
User: /update-rules --from ~/dev/ai-dev --dry-run

AI Response:
📥 DRY RUN: Pulling rules from ~/dev/ai-dev

[Same analysis as above]

Summary:
- New rules: 4
- Updated rules: 5
- Total to update: 9 rules

🔍 DRY RUN MODE - No changes made
Run without --dry-run to apply changes
```

---

### 4. Category Filter (--categories)

**Flag**: `--categories core,architecture,languages`

**What It Does**:
- Only sync specified categories
- Comma-separated list
- Ignores other categories

**Available Categories**:
- `core` - Workflow, naming, debugging, docs
- `architecture` - Clean architecture, layers, dependencies
- `languages` - TypeScript, Python, Go
- `frontend` - React, state, design system
- `backend` - Lambda, saga, API design
- `infrastructure` - AWS CDK, secrets, monitoring
- `development` - Performance, security

**Example**:
```bash
User: /update-rules --from ~/dev/ai-dev --categories core,architecture

AI Response:
📥 Pulling rules from ~/dev/ai-dev

Selected categories: core, architecture

📊 Analysis:
┌────────────────┬─────┬─────┬──────┐
│ Category       │ New │ Upd │ Same │
├────────────────┼─────┼─────┼──────┤
│ core           │  0  │  1  │   6  │
│ architecture   │  0  │  2  │   5  │
└────────────────┴─────┴─────┴──────┘

Skipped categories: languages, frontend, backend, infrastructure, development

Summary:
- New rules: 0
- Updated rules: 3
- Total to update: 3 rules

Proceed? (y/n)
```

---

## Common Use Cases

### Use Case 1: Framework Rule Update

```bash
# In your project
cd ~/projects/my-app

# Pull latest rules from framework
/update-rules --from ~/dev/ai-dev

# Preview first
/update-rules --from ~/dev/ai-dev --dry-run

# Update specific categories only
/update-rules --from ~/dev/ai-dev --categories core,architecture
```

### Use Case 2: Project-Specific Rules

```bash
# Only update rules relevant to your stack
cd ~/projects/react-app

# Only pull frontend + React rules
/update-rules --from ~/dev/ai-dev --categories frontend,languages
```

### Use Case 3: Share Project Innovations

```bash
# In framework repo
cd ~/dev/ai-dev

# Pull improved rules from successful project
/update-rules --from ~/projects/my-app --categories backend

# Or push framework rules to new project
/update-rules --to ~/projects/new-app
```

---

## What Gets Synced

```
.claude/rules/
├── core/
│   ├── workflow.md           ✅ Synced
│   ├── naming.md             ✅ Synced
│   └── ...                   ✅ Synced
├── architecture/
│   ├── clean-architecture.md ✅ Synced
│   └── ...                   ✅ Synced
├── languages/
│   └── ...                   ✅ Synced
├── frontend/
│   └── ...                   ✅ Synced
├── backend/
│   └── ...                   ✅ Synced
├── infrastructure/
│   └── ...                   ✅ Synced
└── development/
    └── ...                   ✅ Synced

.claude/
├── settings.json             ❌ Not synced (project-specific)
├── MEMORY.md                 ❌ Not synced (project-specific)
└── plans/                    ❌ Not synced (project-specific)
```

---

## Safety Features

**Pre-flight Checks**:
- ✅ Source/target paths exist
- ✅ Source has .claude/rules/ directory
- ✅ User confirmation for changes
- ✅ Dry-run mode available

**Smart Defaults**:
- Category-based filtering
- Shows diff before applying
- Backup before overwrite (optional)
- Clean error messages

**Backup Strategy**:
```bash
# Before overwrite
.claude/rules/core/workflow.md
→ .claude/rules/core/workflow.md.backup-20260304-153045
```

---

## Error Handling

### Invalid Source/Target

```
❌ Error: Project not found

Path: ../nonexistent
Expected: ../nonexistent/.claude/rules/

Please check:
1. Path is correct
2. Project has .claude/rules/ directory
3. You have read permissions
```

### No Rules to Update

```
✅ All rules are up to date!

No new or updated rules found in source.
Current project has all latest versions.
```

### Invalid Category

```
❌ Error: Unknown category: unknown-category

Valid categories:
- core
- architecture
- languages
- frontend
- backend
- infrastructure
- development
```

---

## Best Practices

1. **Always dry-run first**:
```bash
/update-rules --from ~/dev/ai-dev --dry-run
/update-rules --from ~/dev/ai-dev
```

2. **Category-specific updates**:
```bash
# Only update relevant categories
/update-rules --from ~/dev/ai-dev --categories frontend,languages
```

3. **Framework as source of truth**:
```bash
# In projects: pull from framework
/update-rules --from ~/dev/ai-dev

# In framework: pull innovations from projects
/update-rules --from ~/projects/my-app --categories backend
```

4. **Regular updates**:
```bash
# Weekly/monthly routine
/update-rules --from ~/dev/ai-dev
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
# Pull all rules
/update-rules --from ~/dev/ai-dev

# Push all rules
/update-rules --to ~/projects/my-app

# Dry run
/update-rules --from ~/dev/ai-dev --dry-run

# Specific categories
/update-rules --from ~/dev/ai-dev --categories core,architecture

# Multiple categories
/update-rules --from ~/dev/ai-dev --categories frontend,backend,languages
```

---

**Last Updated**: 2026-03-04
**Version**: 1.0
**Status**: Production Ready
