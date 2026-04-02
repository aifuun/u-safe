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
2. Copy all skills from source (filtered by framework-only)
3. Report what was synced
4. No version comparison needed
```

**Why it's default:**
- ✅ **Fast**: No version scanning or comparison
- ✅ **Simple**: Single operation (delete + copy)
- ✅ **Predictable**: No conflicts or version issues
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

### Framework-Only Filtering (Issue #401)

Skills marked with `framework-only: true` are automatically excluded during sync:

```yaml
---
name: update-framework
framework-only: true  # Auto-excluded from target projects
---
```

**Result**: Target projects receive 28 skills instead of 35 (↓20% footprint).

**See**: [FRAMEWORK_ONLY.md](./FRAMEWORK_ONLY.md) for complete documentation

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

Source: ~/dev/ai-dev/.claude/skills/ (35 skills)
Target: ./.claude/skills/ (30 skills)

Removing target directory...
✅ Removed: .claude/skills/

Copying skills...
📊 Skills Analysis:
- Total source skills: 35
- Framework-only (excluded): 7
- Synced to target: 28

✅ Skills synced successfully!

Time: 2.3s
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

### Step 2: Import Shared Utilities

```python
import sys
sys.path.insert(0, '.claude/skills/_scripts')

from utils.sync import (
    parse_skill_metadata,
    filter_framework_only_skills,
    sync_skill,
    SyncMode,
    SyncResult
)
```

### Step 3: Execute Sync

**Default Mode (Complete Replacement):**

```python
# AI-EXECUTABLE
# List source skills
source_skills = list_directory(f"{source_path}/.claude/skills/")

# Filter framework-only skills
skills_to_sync, excluded = filter_framework_only_skills(source_skills)

if not dry_run:
    # Remove target directory
    Bash(f'rm -rf {target_path}/.claude/skills/')

    # Copy filtered skills
    for skill in skills_to_sync:
        Bash(f'cp -r {source_path}/.claude/skills/{skill} {target_path}/.claude/skills/{skill}')

# Report results
print(f"✅ Synced {len(skills_to_sync)} skills")
print(f"⏭️  Excluded {len(excluded)} framework-only skills")
```

**Incremental Mode:**

```python
# AI-EXECUTABLE
# List and filter source skills
source_skills = list_directory(f"{source_path}/.claude/skills/")
skills_to_compare, excluded = filter_framework_only_skills(source_skills)

# Compare versions
analysis = []
for skill in skills_to_compare:
    source_meta = parse_skill_metadata(f"{source_path}/.claude/skills/{skill}/SKILL.md")
    target_meta = parse_skill_metadata(f"{target_path}/.claude/skills/{skill}/SKILL.md")

    status = compare_versions(source_meta.version, target_meta.version)
    analysis.append({
        'skill': skill,
        'source_version': source_meta.version,
        'target_version': target_meta.version,
        'status': status
    })

# Show analysis table
display_analysis_table(analysis)

# Sync based on status
for item in analysis:
    if item['status'] in ['NEW', 'NEWER']:
        sync_skill(source_path, target_path, item['skill'])
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
- ✅ Framework-only filtering applied
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
- [ ] Framework-only skills filtered (7 excluded)
- [ ] Skills synced successfully
- [ ] Summary report displayed
```

## Performance

- **Default mode**: ~2-3 seconds (complete replacement)
- **Incremental mode**: ~5-10 seconds (version scanning)
- **Fast because**:
  - Minimal filesystem operations
  - Parallel copy operations
  - Efficient framework-only filtering

## Related Skills

- **/update-framework** - Complete framework sync (calls this skill)
- **/update-pillars** - Sync Pillars between projects
- **/update-guides** - Sync AI guides between projects

## Documentation

- **[MODES.md](./MODES.md)** - Complete guide to sync modes (437 lines)
  - Complete replacement vs incremental comparison
  - Version detection logic
  - Conflict handling
  - Parameter combinations

- **[FRAMEWORK_ONLY.md](./FRAMEWORK_ONLY.md)** - Framework-only filtering (207 lines)
  - Issue #401: Auto-exclude framework management tools
  - YAML metadata marking
  - Filtering logic implementation
  - Backward compatibility

- **[EXAMPLES.md](./EXAMPLES.md)** - Usage examples (461 lines)
  - Common scenarios
  - Advanced use cases
  - Workflow integration
  - Error scenarios
  - Best practices

## Shared Modules

- **`_scripts/utils/sync.py`** (282 lines) - Core synchronization logic
  - `parse_skill_metadata()`: YAML frontmatter parser
  - `filter_framework_only_skills()`: Framework-only filtering (Issue #401)
  - `sync_skill()`: Skill synchronization
  - Support for 3 sync modes: REPLACE, INCREMENTAL, SELECTIVE

- **`_scripts/tests/test_sync_utils.py`** (246 lines) - Unit tests

---

**Version:** 3.2.0
**Pattern:** Tool-Reference (guides AI through sync workflow)
**Compliance:** ADR-001 ✅ | ADR-014 ✅ (modular documentation)
**Last Updated:** 2026-03-30
**Changelog:**
- v3.2.0 (2026-03-30): Refactor to modular docs - extracted MODES.md, FRAMEWORK_ONLY.md, EXAMPLES.md (Issue #418)
- v3.1.0 (2026-03-18): Added framework-only filtering (Issue #401)
- v3.0.0 (2026-03-01): Made complete replacement default, deprecated --clean
