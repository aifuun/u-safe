---
name: update-skills
description: |
  Sync skills between projects - bidirectional copy with version detection.
  TRIGGER when: user wants to sync skills ("update skills from X", "sync skills", "pull skills from framework", "push skills to project").
  DO NOT TRIGGER when: user wants to update pillars/rules/workflow (use respective update-* skills), or just wants to read skill docs.
---

# Update Skills - Skills Synchronization

Sync skill files between projects bidirectionally with smart version detection and conflict handling.

## Overview

This skill synchronizes skills (.claude/skills/) between projects:

**What it does:**
1. Scans source and target projects for skills
2. Compares skills to detect new/updated/conflicted versions
3. Shows detailed diff preview with line counts
4. Syncs skills with confirmation
5. Supports selective skill filtering
6. Creates backups before overwriting
7. Reports what was synced

**Why it's needed:**
Skills evolve across projects. Framework updates need to propagate, and project innovations should flow back. This skill automates bidirectional skill sync with version conflict detection and backup protection.

**When to use:**
- Monthly framework upgrades
- Promoting project skills to framework
- Cross-project skill sharing
- Initial project setup

## Workflow

### Step 1: Create Todo List

**Initialize sync tracking** using TaskCreate:

```
Task #1: Validate source and target paths
Task #2: Scan skills in both projects (blocked by #1)
Task #3: Compare and detect versions (blocked by #2)
Task #4: Show diff preview (blocked by #3)
Task #5: Execute sync with confirmation (blocked by #4)
Task #6: Report sync results (blocked by #5)
```

After creating tasks, proceed with sync execution.

## Sync Modes

### 1. Pull Skills (--from)

Pull skills from source project to current project:

```bash
/update-skills --from ~/dev/ai-dev
/update-skills --from ~/dev/ai-dev --dry-run
/update-skills --from ~/dev/ai-dev --skills adr,status,review
```

**What happens:**
1. Scan source: `<source>/.claude/skills/`
2. Scan current: `.claude/skills/`
3. Compare modification times and sizes
4. Detect: NEW, NEWER, OLDER, CONFLICT, SAME
5. Show analysis table
6. Confirm and copy updated skills

### 2. Push Skills (--to)

Push skills from current project to target project:

```bash
/update-skills --to ~/projects/my-app
/update-skills --to ~/projects/my-app --dry-run
/update-skills --to ~/projects/my-app --skills create-issues,start-issue,finish-issue
```

**What happens:**
1. Scan current project skills
2. Scan target project skills
3. Compare versions
4. Show what will be pushed
5. Confirm and copy to target

### 3. Dry Run Mode (--dry-run)

Preview changes without applying:

```bash
/update-skills --from ~/dev/ai-dev --dry-run
```

**Output:**
- Shows analysis table with versions
- Reports what would be synced
- No confirmation required
- No actual changes made

### 4. Selective Sync (--skills)

Sync only specific skills:

```bash
/update-skills --from ~/dev/ai-dev --skills adr,status
/update-skills --to ~/projects/my-app --skills custom-deploy,custom-test
```

**Skill selection:**
- Comma-separated list
- Only syncs specified skills
- Ignores others

## Version Detection

**Comparison algorithm:**

```
For each skill directory with SKILL.md:
1. Check if exists in target
   → NEW if not found
2. Compare modification time (stat -f %m)
   → NEWER if source newer
   → OLDER if source older
3. Compare file size (wc -l)
   → CONFLICT if same time, different size
   → SAME if identical time and size
```

**Status meanings:**
- **NEW** - Skill doesn't exist in target (safe to copy)
- **NEWER** - Source modified more recently (recommend update)
- **OLDER** - Target modified more recently (warn before overwrite)
- **CONFLICT** - Same modification time but different content (manual review needed)
- **SAME** - Identical (skip)

## Analysis Output

```
📊 Analysis:
┌─────────────────┬────────┬──────────────────┐
│ Skill           │ Status │ Action           │
├─────────────────┼────────┼──────────────────┤
│ adr             │ NEWER  │ Update (443 vs 408 lines) │
│ create-issues   │ NEW    │ Copy (617 lines) │
│ start-issue     │ NEW    │ Copy (554 lines) │
│ finish-issue    │ NEW    │ Copy (557 lines) │
│ status          │ SAME   │ Skip             │
│ review          │ OLDER  │ Skip (warn)      │
│ (15 others)     │ SAME   │ Skip             │
└─────────────────┴────────┴──────────────────┘

Summary:
- New skills: 3
- Updated skills: 1
- Unchanged: 18
- Skipped (older): 1
- Total to sync: 4 skills (2,171 lines)
```

## Conflict Handling

### OLDER Source (Warning)

```
⚠️ Warning: Source skill is OLDER than target

Skill: status
Source: 2026-03-01 (220 lines)
Target: 2026-03-04 (223 lines)

Options:
1. Skip (recommended) - Keep newer version
2. Overwrite - Replace with older version
3. Diff - Show differences

Choice (1/2/3):
```

### CONFLICT Detection

```
❌ Conflict detected

Skill: adr
Source: modified 2026-03-04 14:59 (443 lines)
Target: modified 2026-03-04 14:59 (408 lines)

Same modification time but different content.

Options:
1. Skip - Keep current version
2. Show diff - Compare line by line
3. Overwrite - Use source version
4. Manual merge - Open both files

Choice (1/2/3/4):
```

## Backup Strategy

**Automatic backup before overwrite:**

```bash
Before updating any skill:

✅ Creating backup: .claude/skills/adr.backup-2026-03-06/
✅ Backed up: adr/SKILL.md
✅ Backed up: adr/LICENSE.txt

Now updating adr...
✅ Updated: adr (408 → 443 lines)

Rollback available: .claude/skills/adr.backup-2026-03-06/
```

**Backup cleanup:**
- Automatic after 7 days
- Or manual: `rm -rf .claude/skills/*.backup-*`

## What Gets Synced

```
.claude/skills/
├── skill-name/
│   ├── SKILL.md              ✅ Synced (entire directory)
│   ├── LICENSE.txt           ✅ Synced
│   ├── scripts/              ✅ Synced (if exists)
│   ├── references/           ✅ Synced (if exists)
│   └── assets/               ✅ Synced (if exists)
└── another-skill/
    └── ...                   ✅ Synced

.claude/
├── settings.json             ❌ Not synced (project-specific)
├── MEMORY.md                 ❌ Not synced (project-specific)
└── plans/                    ❌ Not synced (project-specific)
```

**Note:** Entire skill directories are synced, not just SKILL.md.

## Usage Examples

### Example 1: Framework Upgrade

**User says:**
> "update skills from the framework"

**What happens:**
1. Pull from ~/dev/ai-dev
2. Scan both projects
3. Show: 4 skills to update
4. Confirm and sync
5. Report: "Updated 4 skills"

**Time:** ~30 seconds

### Example 2: Selective Update

**User says:**
> "pull only the adr and status skills"

**What happens:**
1. `/update-skills --from ~/dev/ai-dev --skills adr,status`
2. Compare only those 2 skills
3. Show: 1 updated (adr), 1 same (status)
4. Sync adr only
5. Report: "Updated adr skill"

**Time:** ~20 seconds

### Example 3: Promote to Framework

**User says:**
> "push my custom skills to the framework"

**What happens:**
1. `/update-skills --to ~/dev/ai-dev --skills custom-deploy,custom-test`
2. Compare custom skills
3. Show: 2 NEW skills
4. Confirm and push
5. Report: "Pushed 2 skills to framework"

**Time:** ~25 seconds

## Safety Features

**Pre-flight checks:**
- ✅ Source/target paths exist
- ✅ Source has .claude/skills/ directory
- ✅ User confirmation before changes
- ✅ Dry-run preview available

**Version protection:**
- Warns when overwriting newer target
- Detects conflicts (same time, different content)
- Shows line count differences
- Provides diff option

**Backup protection:**
- Automatic backup before overwrite
- Timestamped backup directories
- Easy rollback

## Error Handling

### Invalid Source/Target

```
❌ Error: Project not found

Path: ../nonexistent
Expected: ../nonexistent/.claude/skills/

Please check:
1. Path is correct
2. Project has .claude/skills/ directory
3. You have read permissions
```

### No Skills to Update

```
✅ All skills are up to date!

No new or updated skills found in source.
Current project has all latest versions.
```

### Permission Issues

```
❌ Error: Permission denied

Cannot write to: ../buffer/.claude/skills/

Please check:
1. You have write permissions
2. Directory is not read-only
3. No other process is locking the directory
```

## Best Practices

1. **Always dry-run first:**
```bash
/update-skills --from ~/dev/ai-dev --dry-run
/update-skills --from ~/dev/ai-dev
```

2. **Selective updates for safety:**
```bash
# Update only specific skills you trust
/update-skills --from ~/dev/ai-dev --skills adr,status
```

3. **Framework as source of truth:**
```bash
# In projects: pull from framework
/update-skills --from ~/dev/ai-dev

# In framework: pull innovations from projects
/update-skills --from ~/projects/my-app --skills custom-skill
```

4. **Document custom skills:**
Before pushing to framework, ensure:
- [ ] Complete YAML frontmatter
- [ ] Detailed documentation (200+ lines)
- [ ] Comprehensive examples
- [ ] No project-specific hardcoded paths
- [ ] LICENSE.txt included

## Integration

**With other update-* skills:**
```bash
# Complete framework update
/update-pillars --from ~/dev/ai-dev   # 1. Pillars
/update-rules --from ~/dev/ai-dev     # 2. Rules
/update-workflow --from ~/dev/ai-dev  # 3. Workflow
/update-skills --from ~/dev/ai-dev    # 4. Skills

# Or use meta-skill
/update-framework --from ~/dev/ai-dev # All-in-one
```

**Common workflow:**
```
Framework upgrade → Pull Skills → Test locally → Commit
Skill development → Polish → Push to framework → Share
```

## Task Management

**After each sync step**, update progress:

```
Paths validated → Update Task #1
Skills scanned → Update Task #2
Versions compared → Update Task #3
Diff shown → Update Task #4
Sync executed → Update Task #5
Results reported → Update Task #6
```

Provides real-time visibility of sync progress.

## Final Verification

**Before declaring sync complete**, verify:

```
- [ ] All 6 sync tasks completed
- [ ] Source and target paths valid
- [ ] Skills compared successfully
- [ ] User confirmed changes
- [ ] Directories copied correctly
- [ ] Backups created (if overwritten)
- [ ] Sync summary displayed
```

Missing items indicate incomplete sync.

## Related Skills

- **/update-framework** - Sync entire framework (calls this skill)
- **/update-pillars** - Sync Pillars
- **/update-rules** - Sync rules
- **/update-workflow** - Sync workflow docs

---

**Version:** 2.1.0
**Pattern:** Tool-Reference (guides sync process)
**Compliance:** ADR-001 Section 4 ✅
