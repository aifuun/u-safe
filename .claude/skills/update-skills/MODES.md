# Sync Modes - Complete vs Incremental

> Detailed guide to update-skills synchronization strategies

## Overview

update-skills supports two synchronization modes:

| Mode | When to Use | Speed | Complexity | Conflicts |
|------|-------------|-------|------------|-----------|
| **Complete Replacement** (default) | Framework → Project (99% use cases) | Fast | Simple | None |
| **Incremental** (--incremental) | Bidirectional development | Slower | Complex | Possible |

## Complete Replacement Mode (Default)

**Simple, fast, conflict-free** - Recommended for most use cases.

### How It Works

```
1. Delete target .claude/skills/ directory completely
2. Copy all skills from source (filtered by framework-only)
3. Report what was synced
4. No version comparison needed
```

### Usage

```bash
# Most common: pull from framework
/update-skills --from ~/dev/ai-dev

# Push to target project
/update-skills --to ~/projects/my-app

# Preview changes
/update-skills --from ~/dev/ai-dev --dry-run
```

### Output Example

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
```

### When to Use

- ✅ Framework → Project synchronization (primary use case)
- ✅ Fresh project setup
- ✅ After framework updates
- ✅ Clean synchronization without conflicts
- ✅ Don't need version comparison

### Advantages

- **Fast**: No version scanning or comparison
- **Simple**: Single operation (delete + copy)
- **Predictable**: No conflicts or version issues
- **Safe**: Git provides rollback if needed

### Git Safety

Complete replacement doesn't need automatic backups because:

1. **Git tracks all changes**: `git diff` shows what changed
2. **Easy rollback**: `git restore .claude/skills/` undoes sync
3. **Commit before sync**: Standard practice for safety
4. **No silent overwrites**: All changes visible in git status

## Incremental Mode (--incremental)

**Version-aware synchronization** with conflict detection.

### How It Works

```
1. Scan source skills (with framework-only filtering)
2. Scan target skills
3. Compare semantic versions from YAML frontmatter
4. Detect status: NEW, NEWER, OLDER, CONFLICT, SAME
5. Show analysis table
6. Confirm and sync only updated skills
```

### Usage

```bash
# Basic incremental sync
/update-skills --from ~/dev/ai-dev --incremental

# Preview incremental changes
/update-skills --from ~/dev/ai-dev --incremental --dry-run

# Selective skills only
/update-skills --from ~/dev/ai-dev --incremental --skills adr,status,review

# With smart filter (used by /update-framework)
/update-skills --from ~/dev/ai-dev --incremental --filter-config .claude/framework-config.json
```

### Version Detection Logic

```python
def compare_versions(source_version: str, target_version: str) -> Status:
    """
    Compare semantic versions

    Returns:
        NEW: Skill exists only in source
        NEWER: Source version > target version
        OLDER: Source version < target version
        SAME: Versions are identical
        CONFLICT: Versions differ in major (breaking changes)
    """
    if not target_version:
        return Status.NEW

    s_major, s_minor, s_patch = parse_semver(source_version)
    t_major, t_minor, t_patch = parse_semver(target_version)

    if s_major != t_major:
        return Status.CONFLICT  # Major version mismatch

    if (s_major, s_minor, s_patch) > (t_major, t_minor, t_patch):
        return Status.NEWER
    elif (s_major, s_minor, s_patch) < (t_major, t_minor, t_patch):
        return Status.OLDER
    else:
        return Status.SAME
```

### Output Example

```
🔍 Scanning skills...

Source: ~/dev/ai-dev/.claude/skills/ (35 skills)
Target: ./.claude/skills/ (30 skills)

📊 Skills Analysis:
- Total source skills: 35
- Framework-only (excluded): 7
- Comparing: 28 skills

┌──────────────────┬─────────┬─────────┬──────────┬──────────┐
│ Skill            │ Source  │ Target  │ Status   │ Decision │
├──────────────────┼─────────┼─────────┼──────────┼──────────┤
│ adr              │ 1.5.0   │ 1.4.0   │ NEWER    │ Sync     │
│ status           │ 2.1.0   │ 2.1.0   │ SAME     │ Skip     │
│ review           │ 2.3.0   │ 2.4.0   │ OLDER    │ Skip     │
│ new-skill        │ 1.0.0   │ -       │ NEW      │ Sync     │
│ custom-tool      │ 3.0.0   │ 2.5.0   │ CONFLICT │ Manual   │
└──────────────────┴─────────┴─────────┴──────────┴──────────┘

Summary:
- NEW: 1 skill (will sync)
- NEWER: 1 skill (will sync)
- OLDER: 1 skill (will skip - target is newer)
- SAME: 24 skills (will skip)
- CONFLICT: 1 skill (manual resolution required)

Total to sync: 2 skills
```

### Status Definitions

| Status | Meaning | Action |
|--------|---------|--------|
| **NEW** | Skill only in source | ✅ Copy to target |
| **NEWER** | Source version > target | ✅ Update target |
| **OLDER** | Source version < target | ⏭️ Skip (keep target) |
| **SAME** | Versions identical | ⏭️ Skip (no change) |
| **CONFLICT** | Major version mismatch | ⚠️ Manual review |

### Conflict Handling

**When conflicts occur:**

```
⚠️  CONFLICT: custom-tool

Source version: 3.0.0
Target version: 2.5.0

Reason: Major version mismatch indicates breaking changes

Options:
1. Keep target version (2.5.0) - No action needed
2. Force update to source (3.0.0) - Review breaking changes first
3. Manually merge changes - Best for customizations

Recommended: Review changelog and decide manually
```

**Resolution steps:**

1. **Review changelog**: Check what changed in major version bump
2. **Check customizations**: Identify target project customizations
3. **Test in isolation**: Create backup branch, test update
4. **Manual merge**: Merge changes if needed
5. **Update version**: Bump version after merge

### When to Use Incremental

- ✅ Bidirectional development (both sides modified)
- ✅ Need version conflict detection
- ✅ Want selective skill updates
- ✅ Customizing framework skills in project
- ✅ Complex synchronization scenarios

### Advantages

- **Version-aware**: Detects conflicts before sync
- **Selective**: Only sync changed skills
- **Safe**: Preserves newer target versions
- **Flexible**: Supports --skills filter

### Disadvantages

- **Slower**: Requires version scanning
- **Complex**: More logic, more edge cases
- **Conflict-prone**: Major version mismatches need manual resolution

## Selective Sync (--skills)

**Only works with --incremental mode.**

### Usage

```bash
# Sync specific skills only
/update-skills --from ~/dev/ai-dev --incremental --skills adr,status

# Multiple skills
/update-skills --from ~/dev/ai-dev --incremental --skills adr,review,finish-issue,start-issue
```

### How It Works

```
1. Parse --skills argument (comma-separated list)
2. Filter source skills to only include specified names
3. Run normal incremental comparison
4. Sync only the filtered skills
```

### Example

```bash
$ /update-skills --from ~/dev/ai-dev --incremental --skills adr,status

🔍 Filtering skills: adr, status

Source skills (filtered): 2
Target skills: 30

┌──────────┬─────────┬─────────┬──────────┬──────────┐
│ Skill    │ Source  │ Target  │ Status   │ Decision │
├──────────┼─────────┼─────────┼──────────┼──────────┤
│ adr      │ 1.5.0   │ 1.4.0   │ NEWER    │ Sync     │
│ status   │ 2.1.0   │ 2.1.0   │ SAME     │ Skip     │
└──────────┴─────────┴─────────┴──────────┴──────────┘

Total to sync: 1 skill (adr)
```

### Error: --skills without --incremental

```bash
$ /update-skills --from ~/dev/ai-dev --skills adr,status

❌ Error: --skills requires --incremental mode

Default mode syncs all skills completely. For selective sync:
/update-skills --from ~/dev/ai-dev --incremental --skills adr,status
```

## Smart Filter (--filter-config)

**Only works with --incremental mode.** Used by /update-framework meta-skill.

### Configuration Format

```json
{
  "filterConfig": {
    "skills": {
      "include": ["*"],
      "exclude": ["deploy-prod", "hotfix"]
    }
  }
}
```

### Usage

```bash
# Used by /update-framework
/update-skills --from ~/dev/ai-dev --incremental --filter-config .claude/framework-config.json
```

### How It Works

```
1. Read filter config from specified path
2. Parse include/exclude lists
3. For each skill:
   - Skip if in exclude list
   - Apply normal version comparison
4. Show filter summary in output
```

### Example Output

```
📋 Smart Filter Active (from .claude/framework-config.json)

Exclude list: deploy-prod, hotfix

⏭️  Excluding: deploy-prod (deployment skill)
⏭️  Excluding: hotfix (deployment skill)

Comparing: 26 skills (2 excluded)

Result: 14 skills synced, 12 skipped, 2 filtered
```

## Dry Run Mode (--dry-run)

Preview changes without applying them. Works with both modes.

### Complete Replacement Preview

```bash
$ /update-skills --from ~/dev/ai-dev --dry-run

🔍 DRY RUN - Preview Mode

Source: ~/dev/ai-dev/.claude/skills/ (35 skills)
Target: ./.claude/skills/ (30 skills)

Would remove: .claude/skills/

Would sync: 28 skills (7 framework-only excluded)

No changes made (dry run mode).
```

### Incremental Preview

```bash
$ /update-skills --from ~/dev/ai-dev --incremental --dry-run

🔍 DRY RUN - Preview Mode

[... normal incremental analysis table ...]

Would sync: 5 skills
Would skip: 23 skills

No changes made (dry run mode).
```

## Parameter Combinations

**Valid combinations:**

```bash
# ✅ Default complete replacement
/update-skills --from ~/dev/ai-dev
/update-skills --to ~/projects/my-app
/update-skills --from ~/dev/ai-dev --dry-run

# ✅ Incremental with version detection
/update-skills --from ~/dev/ai-dev --incremental
/update-skills --from ~/dev/ai-dev --incremental --dry-run

# ✅ Incremental with selective skills
/update-skills --from ~/dev/ai-dev --incremental --skills adr,status

# ✅ Incremental with smart filter
/update-skills --from ~/dev/ai-dev --incremental --filter-config .claude/framework-config.json
```

**Invalid combinations:**

```bash
# ❌ --skills without --incremental
/update-skills --from ~/dev/ai-dev --skills adr,status
Error: --skills requires --incremental mode

# ❌ --filter-config without --incremental
/update-skills --from ~/dev/ai-dev --filter-config .claude/framework-config.json
Error: --filter-config requires --incremental mode
```

## Deprecated: --clean Flag

**DEPRECATED in v3.0.0** - Complete replacement is now the default.

```bash
# ⚠️ DEPRECATED
/update-skills --from ~/dev/ai-dev --clean

# ✅ Use this instead (same behavior)
/update-skills --from ~/dev/ai-dev
```

**Deprecation message:**
```
⚠️  Warning: --clean flag is deprecated
   Complete replacement is now the default behavior.
   You can omit this flag.

Continuing with complete sync...
```

---

**See also:**
- [SKILL.md](./SKILL.md): Core usage documentation
- [FRAMEWORK_ONLY.md](./FRAMEWORK_ONLY.md): Framework-only filtering (Issue #401)
- [EXAMPLES.md](./EXAMPLES.md): Usage examples and scenarios
