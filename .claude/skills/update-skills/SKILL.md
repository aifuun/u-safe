---
name: update-skills
description: |
  Sync skills between projects - complete directory replacement by default, with optional incremental mode.
  TRIGGER when: user wants to sync skills ("update skills from X", "sync skills", "pull skills from framework", "push skills to project").
  DO NOT TRIGGER when: user wants to update pillars/rules/workflow (use respective update-* skills), or just wants to read skill docs.
version: "6.0.0"
framework-only: true
allowed-tools: Bash(cp *), Bash(mkdir *), Bash(ls *), Bash(find *), Bash(test *), Bash(cat *), Bash(wc *), Bash(stat *), Bash(git *), Read, Write, Glob, Grep, Edit
disable-model-invocation: false
user-invocable: true
---

# Update Skills - Skills Synchronization

> Sync skill files from ai-dev framework to target projects with complete directory replacement

## Overview

This skill synchronizes skills (`.claude/skills/`) between projects with **complete directory replacement** as the default behavior.

**What it does:**
1. Deletes target .claude/skills/ directory completely
2. Performs complete copy of entire .claude/skills/ directory (includes all skills, _scripts/, _shared/, _templates/)
3. Reports sync completion
4. Optionally supports incremental mode for version-aware synchronization

**Why it's needed:**
Framework upgrades require updating skills across projects. Manual copying is error-prone and time-consuming. This skill automates the sync with safety checks.

**When to use:**
- Monthly framework upgrades
- Initial project setup
- Cross-project consistency
- Part of /update-framework meta-skill

## Arguments

```bash
/update-skills [options]
```

## AI Execution Instructions

### Step 1: Parse Arguments

```python
# Parse target path (required)
positional_args = [arg for arg in args if not arg.startswith('--')]
if not positional_args:
    raise Error("Missing required argument: <target-path>")

source_path = '.'  # Always current directory (ai-dev)
target_path = positional_args[0]

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

If you still need version-aware syncing, see git history of MODES.md (archived in v5.0.0).

### Step 3: Handle Errors

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

## Quick Start

### Basic Usage

```bash
# Must be in ai-dev framework directory
cd ~/dev/ai-dev

# Sync skills to target project
/update-skills ../my-app

# Preview first
/update-skills ../my-app --dry-run
```

## Sync Modes

### Default Mode: Complete Replacement

**Simple, fast, conflict-free** - Recommended for 99% of use cases.

**Process:**
```
1. Delete target .claude/skills/ directory
2. Complete copy of source .claude/skills/
3. Report completion
```

**Advantages:**
- ✅ **Fast**: ~1.5 seconds
- ✅ **Simple**: Two commands (rm + cp)
- ✅ **Complete**: No missing dependencies
- ✅ **Predictable**: Exact mirror
- ✅ **Safe**: Git provides rollback

### Alternative: Incremental Mode

For complex scenarios requiring version-aware synchronization.

**Process:**
```
1. Scan source and target skills
2. Compare semantic versions from YAML frontmatter
3. Detect status: NEW, NEWER, OLDER, CONFLICT, SAME
4. Show analysis table with version details
5. Sync only changed skills with confirmation
```

**When to use incremental:**
- Bidirectional development (both sides modified)
- Need version conflict detection
- Want selective skill updates (--skills flag)

**Usage:**
```bash
/update-skills ../my-app --incremental
/update-skills ../my-app --incremental --skills adr,review
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

## Safety Features

**Pre-flight checks:**
- ✅ Source/target paths exist
- ✅ Source has .claude/skills/ directory
- ✅ User confirmation before changes (if not --skip-validation)
- ✅ Dry-run preview available

**Smart defaults:**
- Complete replacement by default (simple, fast)
- Automatic backup via git (no manual backups needed)

**Error handling:**
- Invalid paths: Clear error message with fix suggestions
- Permission issues: Helpful guidance

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
Use: /update-skills ../my-app --incremental --skills adr,status
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

## Usage Examples

### Example 1: Pull Skills from Framework (Most Common)

**Scenario**: You have a project that needs the latest skills from ai-dev framework.

**Command**:
```bash
cd ~/dev/ai-dev && /update-skills ../my-app
```

**What happens**:
1. Deletes `.claude/skills/` in current project
2. Copies all skills from framework (excludes 7 framework-only skills)
3. Reports 28 skills synced

**Output**:
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


### Example 2: Preview Before Syncing

**Scenario**: Want to see what will change before actually syncing.

**Command**:
```bash
cd ~/dev/ai-dev && /update-skills ../my-app --dry-run
```

**Output**:
```
🔍 DRY RUN - Preview Mode

Source: ~/dev/ai-dev/.claude/skills/ (35 skills)
Target: ./.claude/skills/ (30 skills)

Would remove: .claude/skills/

Would sync: 28 skills (7 framework-only excluded)

Framework-only skills (excluded):
- update-framework
- update-skills
- update-pillars
- update-guides
- update-permissions
- update-doc-refs
- update-rules

No changes made (dry run mode).
```


### Example 3: Push Skills to Target Project

**Scenario**: You developed new skills in current project and want to push them to another project.

**Command**:
```bash
cd ~/dev/ai-dev && /update-skills ~/projects/my-app
```

**What happens**:
1. Deletes `.claude/skills/` in target project
2. Copies all skills from current project
3. Framework-only filtering applies


### Example 4: Incremental Sync with Version Detection

**Scenario**: Both projects have been modified, need version-aware sync.

**Command**:
```bash
cd ~/dev/ai-dev && /update-skills ../my-app --incremental
```

**Output**:
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
│ new-feature      │ 1.0.0   │ -       │ NEW      │ Sync     │
└──────────────────┴─────────┴─────────┴──────────┴──────────┘

Summary:
- NEW: 1 skill
- NEWER: 1 skill
- OLDER: 1 skill (target is newer, skipping)
- SAME: 25 skills

Total to sync: 2 skills

Continue? [Y/n]: Y

Syncing 2 skills...
✅ adr (1.4.0 → 1.5.0)
✅ new-feature (new)

✅ Skills synced successfully!
```

## Best Practices

1. **Use complete replacement for framework updates** (99% of cases)
2. **Preview with --dry-run** before syncing
3. **Commit before major sync** for easy rollback
4. **Use incremental for bidirectional development**
5. **Review conflicts manually** when they occur

## Integration

### Task Management

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

This skill follows ADR-020 test-driven documentation standard:
- All testing baseline chapters are self-contained in SKILL.md
- No external documentation required for core functionality

For detailed mode comparison and extended examples, see git history of MODES.md and EXAMPLES.md (archived in v5.0.0).


---

**Version:** 6.0.0
**Pattern:** Tool-Reference (guides AI through sync workflow)
**Compliance:** ADR-001 ✅ | ADR-014 ✅ | ADR-020 ✅ (test-driven documentation)
**Last Updated:** 2026-04-06
**Changelog:**
- v6.0.0 (2026-04-06): **BREAKING** - Refactor to ADR-020 test-driven documentation standard (Issue #488)
  - Merged MODES.md and EXAMPLES.md into SKILL.md
  - All testing baseline chapters now self-contained
  - Removed external documentation dependencies
- v5.0.0 (2026-04-06): **BREAKING** - Removed --from/--to parameters, now only supports ai-dev → target (one direction)
- v4.1.0 (2026-04-06): **FEATURE** - Default to --to (push) when only path provided, improving UX for framework → project sync
- v4.0.0 (2026-04-05): **BREAKING** - Removed framework-only filtering, simplified to pure directory copy (rm + cp)
- v3.2.0 (2026-03-30): Refactor to modular docs - extracted MODES.md, FRAMEWORK_ONLY.md, EXAMPLES.md (Issue #418)
- v3.1.0 (2026-03-18): Added framework-only filtering (Issue #401)
- v3.0.0 (2026-03-01): Made complete replacement default, deprecated --clean
