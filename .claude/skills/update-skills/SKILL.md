---
name: update-skills
description: |
  Sync skills between projects - complete directory replacement by default, with optional incremental mode.
  TRIGGER when: user wants to sync skills ("update skills from X", "sync skills", "pull skills from framework", "push skills to project").
  DO NOT TRIGGER when: user wants to update pillars/rules/workflow (use respective update-* skills), or just wants to read skill docs.
version: "3.2.0"
framework-only: true
allowed-tools: Bash(cp *), Bash(mkdir *), Bash(ls *), Bash(find *), Bash(test *), Bash(cat *), Bash(wc *), Bash(stat *), Bash(git *), Read, Write, Glob, Grep, Edit
disable-model-invocation: false
user-invocable: true
---

# Update Skills - Skills Synchronization

> Sync skill files between projects bidirectionally with smart version detection and conflict handling

**Quick Links:**
- **[Sync Modes Guide](./MODES.md)** - Complete vs Incremental synchronization
- **[Framework-Only Filtering](./FRAMEWORK_ONLY.md)** - Issue #401: Auto-exclude framework tools
- **[Usage Examples](./EXAMPLES.md)** - Common scenarios and best practices

## Overview

This skill synchronizes skills (`.claude/skills/`) between projects with **complete directory replacement** as the default behavior:

### Default Mode: Complete Replacement

**Simple, fast, conflict-free** - Recommended for 99% of use cases.

```
1. Delete target .claude/skills/ directory completely
2. Complete copy of entire .claude/skills/ directory
   - Includes all skills
   - Includes _scripts/ (shared utilities)
   - Includes _shared/ (shared resources)
   - Includes _templates/ (skill templates)
3. Report sync completion
```

**Why it's default:**
- ✅ **Fast**: ~1.5 seconds for complete sync
- ✅ **Simple**: Two commands (rm + cp)
- ✅ **Complete**: No missing dependencies
- ✅ **Predictable**: Exact mirror of source
- ✅ **Safe**: Git provides rollback if needed

### Alternative: Incremental Mode

For complex scenarios requiring version-aware synchronization:

```
1. Scan source and target skills
2. Compare semantic versions from YAML frontmatter
3. Detect: NEW, NEWER, OLDER, CONFLICT, SAME
4. Show analysis table with version details
5. Sync only changed skills with confirmation
```

**When to use incremental:**
- Bidirectional development (both sides modified)
- Need version conflict detection
- Want selective skill updates (--skills flag)

**See**: [MODES.md](./MODES.md) for complete mode comparison

## Arguments

```bash
/update-skills [options]
```

### Direction (required, mutually exclusive)

- `--from <path>` - Pull skills from source project to current project
- `--to <path>` - Push skills from current project to target project

### Sync Mode

- **(Default)** - Complete directory replacement (fast, conflict-free)
- `--incremental` - Version comparison and selective sync (slower, more control)

### Options (work with both modes)

- `--dry-run` - Preview changes without applying
- `--skip-validation` - Skip path validation (used when called by update-framework)

### Options (only with --incremental)

- `--skills <list>` - Sync only specific skills (comma-separated)
- `--filter-config <path>` - Apply smart filter based on tech stack config

### Deprecated

- `--clean` - ⚠️ Deprecated in v3.0.0 (complete replacement is now default)

## Quick Start

### Most Common: Pull from Framework

```bash
# Pull latest skills from ai-dev framework
/update-skills --from ~/dev/ai-dev

# Preview changes first
/update-skills --from ~/dev/ai-dev --dry-run

# Push skills to target project
/update-skills --to ~/projects/my-app
```

**What happens:**
```
🔄 Syncing skills (complete replacement mode)

Source: ~/dev/ai-dev/.claude/skills/
Target: ./.claude/skills/

Removing target directory...
✅ Removed: .claude/skills/

Copying entire skills directory...
✅ Skills directory synced completely
   Source: ~/dev/ai-dev/.claude/skills/
   Target: ./.claude/skills/

Time: 1.5s
```

### Incremental Sync with Version Detection

```bash
# Compare versions before syncing
/update-skills --from ~/dev/ai-dev --incremental

# Selective skills only
/update-skills --from ~/dev/ai-dev --incremental --skills adr,status,review
```

**What happens:**
```
🔍 Scanning skills...

┌──────────────┬─────────┬─────────┬──────────┬──────────┐
│ Skill        │ Source  │ Target  │ Status   │ Decision │
├──────────────┼─────────┼─────────┼──────────┼──────────┤
│ adr          │ 1.5.0   │ 1.4.0   │ NEWER    │ Sync     │
│ status       │ 2.1.0   │ 2.1.0   │ SAME     │ Skip     │
│ review       │ 2.3.0   │ 2.4.0   │ OLDER    │ Skip     │
│ new-skill    │ 1.0.0   │ -       │ NEW      │ Sync     │
└──────────────┴─────────┴─────────┴──────────┴──────────┘

Total to sync: 2 skills

Continue? [Y/n]: Y
✅ Skills synced successfully!
```

**See**: [EXAMPLES.md](./EXAMPLES.md) for more scenarios

## AI Execution Instructions

### Step 1: Parse Arguments

```python
# Parse direction
if '--from' in args:
    source_path = args['--from']
    target_path = '.'
    direction = 'pull'
elif '--to' in args:
    source_path = '.'
    target_path = args['--to']
    direction = 'push'

# Parse mode
use_incremental = '--incremental' in args
dry_run = '--dry-run' in args
skills_filter = args.get('--skills', '').split(',') if '--skills' in args else None
filter_config = args.get('--filter-config')
```

### Step 2: Execute Complete Sync

**Simple two-step process:**

```bash
# AI-EXECUTABLE
# Step 1: Delete target directory
rm -rf {target_path}/.claude/skills/

# Step 2: Complete copy (includes everything: skills, _scripts, _shared, _templates)
cp -r {source_path}/.claude/skills/ {target_path}/.claude/skills/

# Report results
echo "✅ Skills directory synced completely"
echo "   Source: {source_path}/.claude/skills/"
echo "   Target: {target_path}/.claude/skills/"
```

**Incremental Mode:**

**Note**: Incremental mode is deprecated in v4.0.0. Use default complete replacement mode for all use cases.

If you still need version-aware syncing, see [MODES.md](./MODES.md) for legacy documentation.
```

### Step 4: Handle Errors

```python
# Validate paths exist
if not Path(f"{source_path}/.claude/skills").exists():
    raise Error(f"Source path not found: {source_path}/.claude/skills/")

# Validate parameter combinations
if skills_filter and not use_incremental:
    raise Error("--skills requires --incremental mode")

if filter_config and not use_incremental:
    raise Error("--filter-config requires --incremental mode")
```

## Safety Features

### Git Version Control

Complete replacement doesn't need automatic backups because:

1. **Git tracks all changes**: `git diff` shows what changed
2. **Easy rollback**: `git restore .claude/skills/` undoes sync
3. **Commit before sync**: Standard practice for safety
4. **No silent overwrites**: All changes visible in git status

**Best practice workflow:**

```bash
# 1. Commit current state
git add .claude/skills/
git commit -m "chore: before skills sync"

# 2. Preview changes
/update-skills --from ~/dev/ai-dev --dry-run

# 3. Sync
/update-skills --from ~/dev/ai-dev

# 4. Review changes
git diff HEAD .claude/skills/

# 5. Rollback if needed (or commit)
git restore .claude/skills/  # Undo
# OR
git commit -m "chore: update skills from framework"
```

### Validation Checks

Before syncing:
- ✅ Source path exists
- ✅ Target path writable
- ✅ Not on main branch (if using git)
- ✅ Valid parameter combinations

During sync:
- ✅ Complete directory copy executed
- ✅ Version format validation (incremental mode)
- ✅ Conflict detection (incremental mode)

After sync:
- ✅ File count verification
- ✅ Permission preservation
- ✅ Summary report

## Error Handling

### Common Errors

**Source path not found:**
```
❌ Error: Source path does not exist

Path: ~/dev/nonexistent-project/.claude/skills/
Expected: Valid project with .claude/skills/ directory

Fix: Check path spelling and ensure project exists
```

**Invalid parameter combination:**
```
❌ Error: --skills requires --incremental mode

Default mode syncs all skills completely.
Use: /update-skills --from ~/dev/ai-dev --incremental --skills adr,status
```

**Version conflict (incremental mode):**
```
⚠️  CONFLICT: custom-tool

Source version: 3.0.0
Target version: 2.5.0

Reason: Major version mismatch indicates breaking changes

Options:
1. Keep target version (no action)
2. Force update (review breaking changes first)
3. Manual merge (recommended for customizations)
```

## Best Practices

1. **Use complete replacement for framework updates** (99% of cases)
2. **Preview with --dry-run** before syncing
3. **Commit before major sync** for easy rollback
4. **Use incremental for bidirectional development**
5. **Review conflicts manually** when they occur

## Integration

### Part of /update-framework

```bash
/update-framework ~/dev/ai-dev

# Internally calls:
# 1. update-pillars --from ~/dev/ai-dev
# 2. update-skills --from ~/dev/ai-dev --incremental --filter-config ...
# 3. update-guides --from ~/dev/ai-dev
```

### Workflow Integration

```bash
# Monthly framework update routine
/update-skills --from ~/dev/ai-dev --dry-run  # Preview
/update-skills --from ~/dev/ai-dev            # Sync
/status                                       # Verify
```

## Task Management

When executing via AI orchestration, use TaskCreate/TaskUpdate:

```
Task #1: Validate source and target paths
Task #2: Scan and filter skills (blocked by #1)
Task #3: Execute sync (blocked by #2)
Task #4: Verify and report (blocked by #3)
```

## Final Verification

```
- [ ] All tasks completed
- [ ] Source and target paths validated
- [ ] Complete directory copy executed
- [ ] Skills directory synced successfully (includes _scripts, _shared, _templates)
- [ ] Summary report displayed
```

## Performance

- **Default mode**: ~1-2 seconds (complete directory copy)
- **Incremental mode**: ~5-10 seconds (version scanning)
- **Fast because**:
  - Simple two-step process (rm + cp)
  - Single directory copy operation
  - No filtering or processing overhead

## Output Mode Detection

**When called by update-framework:**
- Check environment variable: `CALLED_BY_UPDATE_FRAMEWORK`
- If set: Output simplified 1-2 line summary (e.g., "✅ Skills 同步完成: 28 个技能")
- If not set: Output full detailed report (current behavior)

This reduces total output length when update-framework orchestrates multiple sync operations.

## Related Skills

- **/update-framework** - Complete framework sync (calls this skill)
- **/update-pillars** - Sync Pillars between projects
- **/update-guides** - Sync AI guides between projects

## Documentation

- **[MODES.md](./MODES.md)** - Complete guide to sync modes
  - Complete replacement vs incremental comparison
  - Version detection logic (for incremental mode)
  - Conflict handling
  - Parameter combinations

- **[EXAMPLES.md](./EXAMPLES.md)** - Usage examples
  - Common scenarios
  - Advanced use cases
  - Workflow integration
  - Error scenarios
  - Best practices

**Note**: FRAMEWORK_ONLY.md is deprecated as of v4.0.0 (no longer filtering framework-only skills)

---

**Version:** 4.0.0
**Pattern:** Tool-Reference (guides AI through sync workflow)
**Compliance:** ADR-001 ✅ | ADR-014 ✅ (modular documentation)
**Last Updated:** 2026-04-05
**Changelog:**
- v4.0.0 (2026-04-05): **BREAKING** - Removed framework-only filtering, simplified to pure directory copy (rm + cp)
- v3.2.0 (2026-03-30): Refactor to modular docs - extracted MODES.md, FRAMEWORK_ONLY.md, EXAMPLES.md (Issue #418)
- v3.1.0 (2026-03-18): Added framework-only filtering (Issue #401)
- v3.0.0 (2026-03-01): Made complete replacement default, deprecated --clean
