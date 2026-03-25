---
name: update-skills
description: |
  Sync skills between projects - complete directory replacement by default, with optional incremental mode.
  TRIGGER when: user wants to sync skills ("update skills from X", "sync skills", "pull skills from framework", "push skills to project").
  DO NOT TRIGGER when: user wants to update pillars/rules/workflow (use respective update-* skills), or just wants to read skill docs.
version: "3.0.0"
allowed-tools: Bash(cp *), Bash(mkdir *), Bash(ls *), Bash(find *), Bash(test *), Bash(cat *), Bash(wc *), Bash(stat *), Bash(git *), Read, Write, Glob, Grep, Edit
disable-model-invocation: false
user-invocable: true
---

# Update Skills - Skills Synchronization

Sync skill files between projects bidirectionally with smart version detection and conflict handling.

## Overview

This skill synchronizes skills (.claude/skills/) between projects with **complete directory replacement** as the default behavior:

**What it does (default mode):**
1. **Deletes** target `.claude/skills/` directory completely
2. **Copies** all skills from source
3. Reports what was synced
4. **No version comparison** - simple, fast, conflict-free

**Alternative: Incremental mode (--incremental):**
1. Scans source and target projects for skills
2. Compares skills to detect new/updated/conflicted versions
3. Shows detailed diff preview with line counts
4. Syncs skills with confirmation
5. Supports selective skill filtering
6. Creates backups before overwriting

**Why complete replacement is default:**
- 99% of use cases need complete sync (framework → project)
- Incremental mode causes CONFLICT issues (Issue #285)
- Git version control provides safety (no need for automatic backups)
- Simpler, faster, more predictable

**When to use incremental mode:**
- Bidirectional development (project ↔ framework)
- Need version comparison and conflict detection
- Selective skill updates with --skills flag

## Arguments

```bash
/update-skills [options]
```

**Direction (required, mutually exclusive):**
- `--from <path>` - Pull skills from source project to current project
- `--to <path>` - Push skills from current project to target project

**Sync Mode:**
- (Default) - Complete directory replacement (fast, conflict-free)
- `--incremental` - Version comparison and selective sync (slower, more control)

**Options (work with both modes):**
- `--dry-run` - Preview changes without applying

**Options (only with --incremental):**
- `--skills <list>` - Sync only specific skills (comma-separated)
- `--filter-config <path>` - Apply smart filter based on tech stack config

**Deprecated:**
- `--clean` - ⚠️ Deprecated in v3.0.0 (complete replacement is now default)

**Common usage:**

```bash
# Most common: complete replacement (default)
/update-skills --from ~/dev/ai-dev

# Preview before syncing
/update-skills --from ~/dev/ai-dev --dry-run

# Incremental with version detection
/update-skills --from ~/dev/ai-dev --incremental

# Selective skills (requires --incremental)
/update-skills --from ~/dev/ai-dev --incremental --skills adr,status,review

# Smart filter (requires --incremental, used by /update-framework)
/update-skills --from ~/dev/ai-dev --incremental --filter-config .claude/framework-config.json

# Deprecated (shows warning, works as default)
/update-skills --from ~/dev/ai-dev --clean
```

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

### 1. Default Mode: Complete Replacement (--from / --to)

**Default behavior** - Complete clean slate with directory replacement:

```bash
# Pull from framework (complete replacement)
/update-skills --from ~/dev/ai-dev

# Push to project (complete replacement)
/update-skills --to ~/projects/my-app

# Preview before replacement
/update-skills --from ~/dev/ai-dev --dry-run
```

**What happens:**
1. **Deletes** target `.claude/skills/` directory completely
2. **Copies** all skills from source
3. Reports results

**Why this is default:**
- ✅ Simple and fast (no version comparison)
- ✅ Conflict-free (no CONFLICT status to resolve)
- ✅ Complete sync guaranteed
- ✅ Git provides safety (git diff, git restore)

**Example output:**
```
🗑️  Deleting .claude/skills (34 skills)
📋 Copying from ~/dev/ai-dev/.claude/skills (22 skills)

✅ Complete sync: 22 skills synced
```

### 2. Incremental Mode (--incremental)

**Optional mode** - Version comparison and selective sync:

```bash
# Incremental sync with version detection
/update-skills --from ~/dev/ai-dev --incremental

# Incremental with selective skills
/update-skills --from ~/dev/ai-dev --incremental --skills adr,status,review
```

**What happens:**
1. Scan source: `<source>/.claude/skills/`
2. Scan current: `.claude/skills/`
3. Compare semantic versions from YAML frontmatter
4. Detect: NEW, NEWER, OLDER, CONFLICT, SAME
5. Show analysis table
6. Confirm and copy only updated skills
7. Create backups before overwriting

**When to use:**
- Bidirectional development (both sides modified)
- Need version conflict detection
- Want selective skill updates (--skills flag)
- Customizing framework skills in project

### 3. Dry Run Mode (--dry-run)

Preview changes without applying:

```bash
# Preview complete replacement (default)
/update-skills --from ~/dev/ai-dev --dry-run

# Preview incremental sync
/update-skills --from ~/dev/ai-dev --incremental --dry-run
```

**Output:**
- Default mode: Shows source and target skill counts
- Incremental mode: Shows analysis table with versions
- Reports what would be synced
- No confirmation required
- No actual changes made

### 4. Selective Sync (--skills)

**Only works with --incremental mode:**

```bash
# Incremental sync with selective skills
/update-skills --from ~/dev/ai-dev --incremental --skills adr,status
/update-skills --to ~/projects/my-app --incremental --skills custom-deploy,custom-test
```

**Skill selection:**
- Comma-separated list
- Only syncs specified skills
- Ignores others

**Mutual exclusion:**
- ❌ `--skills` without `--incremental` → Error
- ✅ `--skills` with `--incremental` → Valid

### 5. Smart Filter (--filter-config)

**Only works with --incremental mode:**

Apply intelligent filtering based on tech stack configuration:

```bash
# Used by /update-framework meta-skill (with --incremental)
/update-skills --from ~/dev/ai-dev --incremental --filter-config <target>/.claude/framework-config.json
```

**What it does:**
1. Reads filter config from `.claude/framework-config.json`
2. Applies exclude list for skills not relevant to tech stack
3. Shows filter summary in analysis

**Filter Configuration Format:**

```json
{
  "filterConfig": {
    "skills": {
      "include": ["*"],  // Usually sync all skills
      "exclude": []      // Rarely exclude skills
    }
  }
}
```

**Filter Logic:**

```
For each skill directory:
1. Check if skill name in exclude list
   → Skip if excluded
2. Apply normal NEW/NEWER/SAME logic
```

**Example - Minimal Project:**

Without filter: 16 skills synced
With filter (exclude deployment skills): ~14 skills synced

```
📋 Smart Filter Active
⏭️  Excluding: deploy-prod (deployment skill)
⏭️  Excluding: hotfix (deployment skill)

Result: 14 skills synced (2 excluded)
```

**Note:**
- Skills are usually synced completely (no filtering)
- Filtering mainly used for specialized deployment skills
- Typically called by `/update-framework` meta-skill
- Requires `--incremental` mode

**Mutual exclusion:**
- ❌ `--filter-config` without `--incremental` → Error
- ✅ `--filter-config` with `--incremental` → Valid

### 6. Deprecated: --clean Flag

**DEPRECATED in v3.0.0** - Complete replacement is now the default behavior.

```bash
# ⚠️ DEPRECATED - This flag is no longer needed
/update-skills --from ~/dev/ai-dev --clean

# ✅ Use this instead (same behavior)
/update-skills --from ~/dev/ai-dev
```

**What happens when you use --clean:**
- Displays deprecation warning
- Continues with normal complete replacement (default)
- Does not block execution

**Deprecation message:**
```
⚠️  Warning: --clean flag is deprecated
   Complete replacement is now the default behavior.
   You can omit this flag.

Continuing with complete sync...
```

**Migration guide:**
- Remove `--clean` from all commands
- Default behavior is now complete replacement
- Use `--incremental` if you need version comparison

## Parameter Combinations

**Mutual exclusion rules:**

| Parameter | Compatible With | Incompatible With |
|-----------|----------------|-------------------|
| `--from` / `--to` | All | None |
| `--incremental` | `--skills`, `--filter-config`, `--dry-run` | None (optional parameter) |
| `--skills` | `--incremental`, `--dry-run` | Default mode (requires `--incremental`) |
| `--filter-config` | `--incremental`, `--dry-run` | Default mode (requires `--incremental`) |
| `--dry-run` | All | None |
| `--clean` (deprecated) | `--from`, `--to`, `--dry-run` | `--skills`, `--filter-config` (but deprecated anyway) |

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
$ /update-skills --from ~/dev/ai-dev --skills adr,status

Error: --skills requires --incremental mode
   Default mode syncs all skills completely
   Use: /update-skills --from ~/dev/ai-dev --incremental --skills adr,status

# ❌ --filter-config without --incremental
$ /update-skills --from ~/dev/ai-dev --filter-config .claude/framework-config.json

Error: --filter-config requires --incremental mode
   Default mode syncs all skills completely
   Use: /update-skills --from ~/dev/ai-dev --incremental --filter-config <path>
```

## Version Detection (v2.0.0+)

**Method**: Semantic version comparison from YAML frontmatter

**Comparison algorithm:**

```python
def parse_yaml_version(file_path):
    """从 SKILL.md 的 YAML frontmatter 提取 version 字段

    Returns:
        str: 版本号 (如 "1.1.0") 或 None
    """
    import re
    with open(file_path, 'r') as f:
        # 读取 YAML frontmatter (---...--- 之间)
        lines = []
        in_yaml = False
        for line in f:
            if line.strip() == '---':
                if not in_yaml:
                    in_yaml = True
                    continue
                else:
                    break  # 结束 YAML 块
            if in_yaml:
                lines.append(line)

        # 查找 version: "x.y.z"
        for line in lines:
            if line.startswith('version:'):
                # 提取引号内的版本号
                match = re.search(r'version:\s*"([^"]+)"', line)
                if match:
                    return match.group(1)
    return None

def compare_semver(v1: str, v2: str) -> int:
    """语义化版本比较

    Args:
        v1: 版本号 1 (如 "2.1.0")
        v2: 版本号 2 (如 "2.0.0")

    Returns:
        int: 1 if v1 > v2, -1 if v1 < v2, 0 if equal
    """
    parts1 = [int(x) for x in v1.split('.')]
    parts2 = [int(x) for x in v2.split('.')]

    for p1, p2 in zip(parts1, parts2):
        if p1 > p2:
            return 1
        elif p1 < p2:
            return -1

    return 0

def content_differs(source_path, target_path):
    """检查两个文件内容是否不同（忽略空白和注释）

    Returns:
        bool: True if content differs
    """
    def normalize(path):
        # 读取文件，移除 YAML frontmatter 和空白行
        with open(path, 'r') as f:
            lines = f.readlines()

        # 跳过 YAML frontmatter
        in_yaml = False
        content_lines = []
        for line in lines:
            if line.strip() == '---':
                if not in_yaml:
                    in_yaml = True
                    continue
                else:
                    in_yaml = False
                    continue
            if not in_yaml and line.strip():
                content_lines.append(line.strip())

        return '\n'.join(content_lines)

    return normalize(source_path) != normalize(target_path)

def compare_skill_versions(source_skill, target_skill):
    """比较两个 skill 的版本

    Returns:
        str: "NEW", "NEWER", "OLDER", "SAME", "CONFLICT"
    """
    import os
    source_path = f"{source_skills_dir}/{source_skill}/SKILL.md"
    target_path = f"{target_skills_dir}/{target_skill}/SKILL.md"

    # 1. Target 不存在 → NEW
    if not os.path.exists(target_path):
        return "NEW"

    # 2. 解析 YAML version 字段
    source_version = parse_yaml_version(source_path)
    target_version = parse_yaml_version(target_path)

    # 3. 向后兼容：任一缺少 version → fallback to legacy
    if not source_version or not target_version:
        return compare_legacy(source_path, target_path)

    # 4. 语义化版本比较
    cmp = compare_semver(source_version, target_version)

    if cmp > 0:
        return "NEWER"    # Source version higher
    elif cmp < 0:
        return "OLDER"    # Source version lower
    else:
        # 5. 版本相同，检查内容
        if content_differs(source_path, target_path):
            return "CONFLICT"  # Same version, different content
        else:
            return "SAME"

def compare_legacy(source_path, target_path):
    """Legacy 比较方法（时间 + 行数）- 向后兼容"""
    import os
    # 原有的 stat -f %m 和 wc -l 逻辑
    source_time = os.path.getmtime(source_path)
    target_time = os.path.getmtime(target_path)

    if source_time > target_time:
        return "NEWER"
    elif source_time < target_time:
        return "OLDER"
    else:
        # 时间相同，比较行数
        source_lines = len(open(source_path).readlines())
        target_lines = len(open(target_path).readlines())

        if source_lines != target_lines:
            return "CONFLICT"
        else:
            return "SAME"
```

**Process**:
1. Parse `version: "x.y.z"` from SKILL.md YAML frontmatter
2. Compare using semantic versioning rules:
   - Major: Breaking changes (2.0.0 > 1.9.0)
   - Minor: New features (1.1.0 > 1.0.0)
   - Patch: Bug fixes (1.0.1 > 1.0.0)
3. Detect conflicts: Same version, different content
4. Fallback: If no version field, use legacy (time + size)

**Status meanings:**
- **NEW** - Skill doesn't exist in target (safe to copy)
- **NEWER** - Source version > target version (2.1.0 > 2.0.0, recommend update)
- **OLDER** - Source version < target version (warn before overwrite)
- **SAME** - Versions and content identical (skip)
- **CONFLICT** - Same version but content differs (manual review needed)

**Legacy fallback** (for skills without `version` field):
- Compare modification time (`stat -f %m`)
- If time same, compare file size (`wc -l`)

## Analysis Output

```
📊 Analysis:
┌─────────────────┬────────┬──────────────────────────────┐
│ Skill           │ Status │ Action                       │
├─────────────────┼────────┼──────────────────────────────┤
│ adr             │ NEWER  │ Update (v1.1.0 → v1.2.0)     │
│ create-issues   │ NEW    │ Add (v1.0.0)                 │
│ start-issue     │ NEWER  │ Update (v2.1.0 → v2.2.0)     │
│ finish-issue    │ NEW    │ Add (v1.0.0)                 │
│ status          │ SAME   │ Skip (both v1.0.0)           │
│ review          │ OLDER  │ Skip (v1.0.0 < v1.1.0)       │
│ work-issue      │ CONFLICT│ Manual review needed         │
│                 │        │ (both v3.0.0, content diff)  │
│ (15 others)     │ SAME   │ Skip                         │
└─────────────────┴────────┴──────────────────────────────┘

Summary:
- New skills: 2 (create-issues, finish-issue)
- Updated skills: 2 (adr, start-issue)
- Unchanged: 15
- Skipped (older): 1 (review)
- Conflicts: 1 (work-issue - requires manual resolution)
- Total to sync: 4 skills
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

### CONFLICT Detection (Version Mismatch)

```
❌ Conflict detected

Skill: work-issue
Source version: v3.0.0
Target version: v3.0.0
Content differs: Yes

⚠️ Issue: Version numbers match but content differs

This usually means:
- Both sides modified same version
- Forgot to bump version after changes
- Divergent development

Recommended action:
1. Review changes: diff source/SKILL.md target/SKILL.md
2. Merge manually or choose one version
3. Update version number after merge (v3.0.1 or v3.1.0)

Options:
1. Skip - Keep current version (no sync)
2. Show diff - Compare line by line
3. Overwrite - Use source version (requires confirmation)
4. Manual merge - Open both files in editor

Choice (1/2/3/4):
```

**Why conflicts occur:**
- Both source and target modified same version
- Version number not bumped after content changes
- Parallel development without coordination

**Resolution steps:**
1. Review both versions (option 2: show diff)
2. Choose merge strategy:
   - Manual merge: Combine both changes
   - Accept source: Use newer implementation
   - Accept target: Keep current version
3. Bump version number (v3.0.0 → v3.0.1 or v3.1.0)
4. Re-run sync to verify

## Backup Strategy

**Default mode (complete replacement):**
- NO automatic backups created
- Relies on git version control for safety
- Use `git diff .claude/skills/` to review changes
- Use `git restore .claude/skills/` to recover if needed

**Why no backups in default mode:**
- Git provides better version control than automatic backups
- Simpler and faster (no backup directory creation)
- Complete replacement means no partial states to backup

**Incremental mode (--incremental):**
- Automatic backup before overwriting each skill
- Timestamped backup directories
- Easy rollback

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
├── README.md                 ✅ Synced (skills system guide)
├── WORKFLOW_PATTERNS.md      ✅ Synced (workflow requirements)
├── PYTHON_GUIDE.md           ✅ Synced (development guide)
├── _shared/                  ✅ Synced (shared utilities)
│   ├── *.py
│   └── tests/
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

**Note:**
- Entire skill directories are synced, not just SKILL.md
- Root-level documentation (README, WORKFLOW_PATTERNS, PYTHON_GUIDE) is synced to preserve framework knowledge
- Shared utilities and tests are synced for cross-skill compatibility

## Usage Examples

### Example 1: Framework Upgrade (Default)

**User says:**
> "update skills from the framework"

**What happens:**
1. `/update-skills --from ~/dev/ai-dev` (complete replacement)
2. Delete target `.claude/skills/` (34 skills)
3. Copy from source (22 skills)
4. Report: "Complete sync: 22 skills synced"

**Time:** ~15 seconds (faster than incremental)

### Example 2: Incremental Update with Version Detection

**User says:**
> "update skills but check versions first"

**What happens:**
1. `/update-skills --from ~/dev/ai-dev --incremental`
2. Scan both projects
3. Compare versions
4. Show: 4 skills to update (NEW or NEWER)
5. Confirm and sync
6. Report: "Updated 4 skills"

**Time:** ~30 seconds

### Example 3: Selective Update

**User says:**
> "pull only the adr and status skills"

**What happens:**
1. `/update-skills --from ~/dev/ai-dev --incremental --skills adr,status`
2. Compare only those 2 skills
3. Show: 1 updated (adr), 1 same (status)
4. Sync adr only
5. Report: "Updated adr skill"

**Time:** ~20 seconds

### Example 4: Promote to Framework

**User says:**
> "push my custom skills to the framework"

**What happens:**
1. `/update-skills --to ~/dev/ai-dev --incremental --skills custom-deploy,custom-test`
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

1. **Always dry-run first:** Test with `--dry-run` before applying changes
2. **Selective updates:** Use `--skills` flag to update only specific skills
3. **Framework as source of truth:** Projects pull from framework, framework pulls innovations from projects
4. **Document custom skills:** Ensure complete YAML frontmatter, 200+ lines docs, examples, no hardcoded paths, LICENSE.txt

## Integration

**With other update-* skills:**
```bash
# Complete framework update (default: complete replacement)
/update-pillars --from ~/dev/ai-dev   # 1. Pillars
/update-rules --from ~/dev/ai-dev     # 2. Rules
/update-workflow --from ~/dev/ai-dev  # 3. Workflow
/update-skills --from ~/dev/ai-dev    # 4. Skills (complete replacement)

# Or use meta-skill
/update-framework --from ~/dev/ai-dev # All-in-one
```

**Common workflows:**
```
# 1. Framework upgrade (most common)
Framework upgrade → Pull Skills (complete) → Test → Commit

# 2. Bidirectional development
Skill development → Polish → Push to framework (incremental) → Share

# 3. Monthly sync
Monthly maintenance → Pull skills (complete) → Verify → Commit
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

## Workflow Skills Requirements

This is a **workflow skill** and must follow the standard pattern:

1. **TaskCreate** at start - Create todo list for progress tracking
2. **TaskUpdate** during execution - Mark tasks in_progress → completed
3. **Verification checklist** - Final validation before completion

**See**: [WORKFLOW_PATTERNS.md](../WORKFLOW_PATTERNS.md) for complete implementation guide

## Migration from v2.x

**BREAKING CHANGE in v3.0.0**: Default behavior changed from incremental to complete replacement.

### What Changed

| Aspect | v2.x (Old) | v3.0.0 (New) |
|--------|------------|--------------|
| **Default mode** | Incremental sync (version detection) | Complete replacement (delete + copy) |
| **Default flag** | (none - incremental) | (none - complete) |
| **Incremental mode** | Default | `--incremental` flag required |
| **Clean mode** | `--clean` flag | Default behavior (--clean deprecated) |
| **Selective sync (--skills)** | Works with default | Requires `--incremental` |
| **Smart filter (--filter-config)** | Works with default | Requires `--incremental` |

### Migration Guide

**1. Most common use case (framework sync):**

```bash
# v2.x - Need --clean for complete replacement
/update-skills --from ~/dev/ai-dev --clean

# v3.0.0 - Default is complete replacement
/update-skills --from ~/dev/ai-dev
```

**Action**: Remove `--clean` flag from all commands.

**2. Version detection and selective sync:**

```bash
# v2.x - Default is incremental
/update-skills --from ~/dev/ai-dev --skills adr,status

# v3.0.0 - Must add --incremental
/update-skills --from ~/dev/ai-dev --incremental --skills adr,status
```

**Action**: Add `--incremental` flag when using `--skills` or `--filter-config`.

**3. Dry run preview:**

```bash
# v2.x
/update-skills --from ~/dev/ai-dev --dry-run

# v3.0.0 - Same command, different default output
/update-skills --from ~/dev/ai-dev --dry-run  # Shows complete replacement preview
/update-skills --from ~/dev/ai-dev --incremental --dry-run  # Shows incremental preview
```

**Action**: No change needed, but output format will differ.

### Why This Change?

**Data from Issue #285:**
- 99% of use cases need complete sync (framework → project)
- Incremental mode caused CONFLICT issues frequently
- Users had to remember to use `--clean` flag
- Git version control provides better safety than automatic backups

**Benefits:**
- ✅ Simpler default (no version comparison)
- ✅ Faster execution (no scanning)
- ✅ Conflict-free (complete replacement)
- ✅ More intuitive (sync = replace)

### Compatibility

**Backward compatibility:**
- `--clean` flag still works (shows deprecation warning, then proceeds as default)
- All other flags work as before (but `--skills` and `--filter-config` require `--incremental`)
- No data loss (git provides recovery via `git restore .claude/skills/`)

### Rollback

If you need v2.x behavior permanently:

```bash
# Always use --incremental flag
alias update-skills='/update-skills --incremental'

# Or update your documentation to include --incremental
```

## Related Skills

- **/update-framework** - Sync entire framework (calls this skill)
- **/update-pillars** - Sync Pillars
- **/update-rules** - Sync rules
- **/update-workflow** - Sync workflow docs

---

**Version:** 3.0.0
**Last Updated:** 2026-03-23
**Changelog:**
- v3.0.0 (2026-03-23): BREAKING: Make --clean the default behavior, add --incremental for old mode (Issue #290)
- v2.4.0 (2026-03-14): Simplify --clean mode documentation (Issue #256)
- v2.3.0 (2026-03-13): Add --clean parameter for complete directory replacement (Issue #210)
- v2.0.0 (2026-03-10): Upgrade to semantic version comparison (Issue #214)
- v1.0.0 (Initial): Created update-skills skill (Issue #70)

**Pattern:** Tool-Reference (guides sync process)
**Compliance:** ADR-001 Section 4 ✅
