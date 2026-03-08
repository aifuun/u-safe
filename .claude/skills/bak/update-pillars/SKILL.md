---
name: update-pillars
description: |
  Sync Pillars between projects - copy from or push to other projects.
  Detects new/updated Pillars, shows diffs, handles conflicts intelligently.
  Essential for framework upgrades and cross-project learning.
disable-model-invocation: true
user-invocable: true
argument-hint: "--from <project> | --to <project> [--dry-run] [--pillars A,B,K]"
allowed-tools: Read, Glob, Bash(cp *), Bash(diff *), Bash(find *), Bash(wc *), Write
context: fork
agent: general-purpose
---

# Update Pillars - Project Pillar Synchronization

Sync Pillars between ai-dev framework and other projects bidirectionally.

## Purpose

**Why This Skill Exists**:
- ✅ Framework upgrades (update Pillar documentation)
- ✅ Cross-project learning (adopt Pillar practices from other projects)
- ✅ Maintain Pillar consistency across projects
- ✅ Detect new/updated Pillars automatically
- ✅ Preview changes before applying (--dry-run)
- ✅ Profile-aware (only update Pillars enabled in profile)

---

## Usage

### Pull Pillars from another project

```bash
/update-pillars --from ../ai-dev
/update-pillars --from ../ai-dev --dry-run
/update-pillars --from ../ai-dev --pillars A,B,K
```

### Push Pillars to another project

```bash
/update-pillars --to ../my-app
/update-pillars --to ../my-app --dry-run
/update-pillars --to ../my-app --pillars M,Q,R
```

---

## Commands

### 1. Pull Pillars (--from)

**Command**: `/update-pillars --from <project-path>`

**What It Does**:
1. **Scan source project**: Find all Pillars in `<project>/.prot/pillars/`
2. **Compare with current**: Check which Pillars are new or updated
3. **Detect changes**: Compare file sizes, modification times
4. **Show diff**: Display what will change
5. **Confirm**: Ask user to proceed (unless --dry-run)
6. **Copy**: Update current project with new/updated Pillars
7. **Report**: Show what was copied/updated

**Example**:
```bash
User: /update-pillars --from ~/dev/ai-dev

AI Response:
📥 Pulling Pillars from ~/dev/ai-dev

Scanning Pillars...
✅ Found 18 Pillars in ~/dev/ai-dev/.prot/pillars/
✅ Found 3 Pillars in current project (profile: minimal)

📊 Analysis:
┌─────────────┬────────┬──────────────────┐
│ Pillar      │ Status │ Action           │
├─────────────┼────────┼──────────────────┤
│ pillar-a    │ NEWER  │ Update (250 vs 245 lines) │
│ pillar-b    │ SAME   │ Skip             │
│ pillar-k    │ NEWER  │ Update (180 vs 175 lines) │
└─────────────┴────────┴──────────────────┘

Summary:
- New Pillars: 0
- Updated Pillars: 2 (A, K)
- Unchanged: 1 (B)
- Total to update: 2 Pillars

Proceed? (y/n)
```

**Profile Integration**:
```bash
# If project has .framework-install
Detected profile: minimal (Pillars A, B, K)
→ Only update A, B, K (skip other Pillars)

# If no profile detected
→ Update all Pillars found
```

---

### 2. Push Pillars (--to)

**Command**: `/update-pillars --to <project-path>`

**What It Does**:
1. **Scan current Pillars**: Find all Pillars in current project
2. **Compare with target**: Check which Pillars are new or updated
3. **Show diff**: Display what will change in target project
4. **Confirm**: Ask user to proceed
5. **Copy**: Update target project with new/updated Pillars
6. **Report**: Show what was pushed

**Example**:
```bash
User: /update-pillars --to ../my-app --pillars M,Q

AI Response:
📤 Pushing Pillars to ../my-app

Selected Pillars: M, Q

Checking target project...
✅ Target exists: ../my-app/.prot/pillars/

📊 Analysis:
┌─────────────┬────────┬──────────────────┐
│ Pillar      │ Status │ Action           │
├─────────────┼────────┼──────────────────┤
│ pillar-m    │ NEW    │ Add (320 lines)  │
│ pillar-q    │ NEWER  │ Update (215 vs 200) │
└─────────────┴────────┴──────────────────┘

Summary:
- New Pillars: 1 (M)
- Updated Pillars: 1 (Q)
- Total to push: 2 Pillars

⚠️  Warning: This will modify ../my-app/.prot/pillars/

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
User: /update-pillars --from ~/dev/ai-dev --dry-run

AI Response:
📥 DRY RUN: Pulling Pillars from ~/dev/ai-dev

[Same analysis as above]

Summary:
- New Pillars: 0
- Updated Pillars: 2
- Total to update: 2 Pillars

🔍 DRY RUN MODE - No changes made
Run without --dry-run to apply changes
```

---

### 4. Selective Update (--pillars)

**Flag**: `--pillars A,B,K`

**What It Does**:
- Only sync specified Pillars
- Comma-separated list (A-R)
- Ignores other Pillars

**Example**:
```bash
User: /update-pillars --from ~/dev/ai-dev --pillars A,M,Q

AI Response:
📥 Pulling Pillars from ~/dev/ai-dev

Selected Pillars: A, M, Q

📊 Analysis:
┌─────────────┬────────┬──────────────────┐
│ Pillar      │ Status │ Action           │
├─────────────┼────────┼──────────────────┤
│ pillar-a    │ NEWER  │ Update           │
│ pillar-m    │ NEW    │ Add              │
│ pillar-q    │ SAME   │ Skip             │
└─────────────┴────────┴──────────────────┘

Summary:
- New Pillars: 1 (M)
- Updated Pillars: 1 (A)
- Skipped: 1 (Q - unchanged)

Proceed? (y/n)
```

---

## Common Use Cases

### Use Case 1: Framework Upgrade

```bash
# In your project
cd ~/projects/my-app

# Pull latest Pillars from framework
/update-pillars --from ~/dev/ai-dev

# Preview first
/update-pillars --from ~/dev/ai-dev --dry-run

# Update only enabled Pillars (profile-aware)
# → Automatically filters based on .framework-install
```

### Use Case 2: Cross-Project Learning

```bash
# Learn Saga and Idempotency from another project
cd ~/projects/project-a

/update-pillars --from ~/projects/project-b --pillars M,Q
# → Adopt Pillar M (Saga) and Q (Idempotency) practices
```

### Use Case 3: Promote Innovation to Framework

```bash
# In framework repo
cd ~/dev/ai-dev

# Pull improved Pillar documentation from project
/update-pillars --from ~/projects/my-app --pillars X

# Or push framework updates to project
/update-pillars --to ~/projects/my-app
```

---

## What Gets Synced

```
.prot/pillars/
├── pillar-a/
│   └── *.md              ✅ Synced
├── pillar-b/
│   └── *.md              ✅ Synced
├── pillar-k/
│   └── *.md              ✅ Synced
└── README.md             ✅ Synced (if exists)

.prot/
├── checklists/           ❌ Not synced (project-specific)
└── other files           ❌ Not synced
```

---

## Profile Integration

### Profile Detection

```bash
# Method 1: Read .framework-install
cat .framework-install
# → profile: minimal

# Method 2: Scan .prot/pillars/
ls .prot/pillars/
# → pillar-a, pillar-b, pillar-k (3 Pillars)
```

### Profile-Based Filtering

```
┌─────────────────┬────────────────────────────────┐
│ Profile         │ Pillars Updated                │
├─────────────────┼────────────────────────────────┤
│ minimal         │ A, B, K only                   │
│ node-lambda     │ A, B, K, M, Q, R only          │
│ react-aws       │ All 7 (A, B, K, L, M, Q, R)    │
│ custom/none     │ All Pillars in .prot/pillars/  │
└─────────────────┴────────────────────────────────┘

Example:
Profile: minimal
Source has: 18 Pillars (A-R)
→ Only update: A, B, K (3 Pillars)
→ Skip: Other 15 Pillars (not in profile)
```

---

## Safety Features

**Pre-flight Checks**:
- ✅ Source/target paths exist
- ✅ Source has .prot/pillars/ directory
- ✅ User confirmation for changes
- ✅ Dry-run mode available

**Smart Defaults**:
- Profile-aware (respects .framework-install)
- Shows diff before applying
- Backup before overwrite (optional)
- Clean error messages

---

## Error Handling

### Invalid Source/Target

```
❌ Error: Project not found

Path: ../nonexistent
Expected: ../nonexistent/.prot/pillars/

Please check:
1. Path is correct
2. Project has .prot/pillars/ directory
3. You have read permissions
```

### No Pillars to Update

```
✅ All Pillars are up to date!

No new or updated Pillars found in source.
Current project has all latest versions.
```

---

## Best Practices

1. **Always dry-run first**:
```bash
/update-pillars --from ~/dev/ai-dev --dry-run
/update-pillars --from ~/dev/ai-dev
```

2. **Selective updates for safety**:
```bash
# Update only specific Pillars you understand
/update-pillars --from ~/dev/ai-dev --pillars A,B,K
```

3. **Framework as source of truth**:
```bash
# In projects: pull from framework
/update-pillars --from ~/dev/ai-dev

# In framework: pull innovations from projects
/update-pillars --from ~/projects/my-app --pillars X
```

---

## Quick Reference

```bash
# Pull from framework
/update-pillars --from ~/dev/ai-dev

# Push to project
/update-pillars --to ~/projects/my-app

# Dry run
/update-pillars --from ~/dev/ai-dev --dry-run

# Specific Pillars
/update-pillars --from ~/dev/ai-dev --pillars A,B,K
```

---

**Last Updated**: 2026-03-04
**Version**: 1.0
**Status**: Production Ready
