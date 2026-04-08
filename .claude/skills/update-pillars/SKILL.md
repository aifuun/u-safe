---
name: update-pillars
description: |
  Sync Pillars between projects - bidirectional copy with smart filtering.
  TRIGGER when: user wants to sync Pillars ("update pillars from X", "sync pillars", "pull pillars from framework", "push pillars to project").
  DO NOT TRIGGER when: user wants to update rules/skills/workflow (use respective update-* skills), or just wants to read Pillar docs.
version: "3.0.0"
framework-only: true
allowed-tools: Bash(cp *), Bash(mkdir *), Bash(ls *), Bash(find *), Bash(test *), Bash(cat *), Bash(git *), Read, Write, Glob, Grep, Edit
disable-model-invocation: false
user-invocable: true
---

# Update Pillars - Project Pillar Synchronization

Sync Pillar documentation from ai-dev framework to target projects with profile-aware filtering.

## Overview

This skill synchronizes Pillar documentation (.claude/pillars/) from ai-dev framework to target projects:

**Behavior:** Always syncs FROM current directory (ai-dev) TO target project path.

**What it does:**
1. Scans ai-dev and target projects for Pillars
2. Compares Pillars to detect new/updated content
3. Shows detailed diff preview
4. Syncs Pillars with confirmation
5. Respects project profiles (minimal, node-lambda, react-aws)
6. Reports what was synced

**Note**: Must be run from ai-dev framework directory.

**Why it's needed:**
Framework upgrades require updating Pillar documentation across projects. Manual copying is error-prone and time-consuming. This skill automates the sync with safety checks and profile awareness.

**When to use:**
- Monthly framework upgrades
- Initial project setup
- Cross-project learning (adopting Pillar practices)
- Promoting innovations back to framework

## Directory Structure

**AI-dev framework has two Pillars directories:**

| Directory | Purpose | Used By |
|-----------|---------|---------|
| `.claude/pillars/` | **Source of Truth** (18 Pillars) | Claude Code, sync operations |
| `docs/pillars/` | Legacy human-readable docs | Documentation reference only |

**Key points:**
- ✅ **Sync source**: This skill syncs FROM/TO `.claude/pillars/` (not `docs/pillars/`)
- ✅ **Claude Code**: Reads Pillars from `.claude/pillars/` during development
- ℹ️ **docs/pillars/**: Legacy location, kept for historical reference

**Sync operations:**
```bash
# Must be in ai-dev directory
cd ~/dev/ai-dev

# Sync to target project (uses .claude/pillars/)
/update-pillars ~/projects/my-app
```

**File count:** 18 Pillars (A-R) in `.claude/pillars/` subdirectories

## Workflow

### Step 1: Create Todo List

**Initialize sync tracking** using TaskCreate:

```
Task #1: Validate source and target paths
Task #2: Scan Pillars in both projects (blocked by #1)
Task #3: Compare and detect changes (blocked by #2)
Task #4: Show diff preview (blocked by #3)
Task #5: Execute sync with confirmation (blocked by #4)
Task #6: Report sync results (blocked by #5)
```

After creating tasks, proceed with sync execution.

## Arguments

```bash
/update-pillars <target-path> [options]
```

**Required:**
- `<target-path>` - Target project path

**Options:**
- `--dry-run` - Preview changes without applying
- `--pillars <list>` - Sync only specific Pillars (comma-separated)
- `--skip-validation` - Skip path validation (used by update-framework)

**Usage:**
```bash
# Must be in ai-dev directory
cd ~/dev/ai-dev

# Sync to target project
/update-pillars ../my-app

# Preview first
/update-pillars ../my-app --dry-run

# Selective Pillars
/update-pillars ../my-app --pillars A,B,K
```

## Sync Modes

### 1. Dry Run Mode (--dry-run)

Preview changes without applying:

```bash
/update-pillars ../my-app --dry-run
```

**Output:**
- Shows analysis table
- Reports what would be synced
- No confirmation required
- No actual changes made

### 2. Selective Sync (--pillars)

Sync only specific Pillars:

```bash
/update-pillars ../my-app --pillars A,M,Q
/update-pillars ~/projects/my-app --pillars K,L,R
```

**Pillar selection:**
- Comma-separated list (A-R)
- Only syncs specified Pillars
- Ignores others

### 3. Skip Validation Mode (--skip-validation)

Skip path validation when called by meta-skill (update-framework):

```bash
# Called by update-framework (validation already done)
/update-pillars ../my-app --skip-validation
```

**When to use:**
- ✅ When update-framework calls this skill (paths already validated)
- ✅ Reduces redundant validation (saves ~0.5 seconds)
- ❌ NOT for direct user invocation (safety check needed)

**Behavior:**
- Skips source/target path existence checks
- Skips .claude/pillars/ directory validation
- Assumes caller has validated paths
- Still performs Pillar-level validation

## Comparison Logic

**File status detection:**

```
For each Pillar:
1. Check if exists in target
   → NEW if not found
2. Compare modification time
   → NEWER if source newer
   → OLDER if source older
3. Compare file size
   → CONFLICT if same time, different size
   → SAME if identical
```

**Analysis output:**

```
📊 Analysis:
┌─────────────┬────────┬──────────────────┐
│ Pillar      │ Status │ Action           │
├─────────────┼────────┼──────────────────┤
│ pillar-a    │ NEWER  │ Update (250 vs 245 lines) │
│ pillar-b    │ SAME   │ Skip             │
│ pillar-k    │ NEW    │ Add (180 lines)  │
│ pillar-m    │ OLDER  │ Skip (warn)      │
└─────────────┴────────┴──────────────────┘

Summary:
- New Pillars: 1 (K)
- Updated Pillars: 1 (A)
- Unchanged: 1 (B)
- Total to sync: 2 Pillars
```

## Profile Integration

**Profile detection:**

```bash
# Method 1: Read docs/project-profile.md
cat docs/project-profile.md
# → profile: minimal

# Method 2: Scan installed Pillars
ls .claude/pillars/
# → pillar-a, pillar-b, pillar-k
```

**Profile-based filtering:**

| Profile | Pillars Synced |
|---------|----------------|
| minimal | A, B, K only (3 Pillars) |
| node-lambda | A, B, K, M, Q, R (6 Pillars) |
| react-aws | A, B, K, L, M, Q, R (7 Pillars) |
| custom/none | All Pillars in .claude/pillars/ |

**Example:**
```
Source has: 18 Pillars (A-R)
Current profile: minimal (A, B, K)
→ Only sync: A, B, K
→ Skip: 15 other Pillars
```

## What Gets Synced

```
.claude/pillars/
├── pillar-a/
│   └── *.md              ✅ Synced
├── pillar-b/
│   └── *.md              ✅ Synced
├── pillar-k/
│   └── *.md              ✅ Synced
└── README.md             ✅ Synced (if exists)

.claude/pillars/
├── checklists/           ❌ Not synced (project-specific)
└── other files           ❌ Not synced
```

## Usage Examples

### Example 1: Framework Upgrade

**User says:**
> "update pillars from the framework"

**What happens:**
1. Pull from ~/dev/ai-dev (detected from context)
2. Scan both projects
3. Show analysis: 2 Pillars updated
4. Confirm and sync
5. Report: "Updated Pillar A, K"

**Time:** ~30 seconds

### Example 2: Initial Setup

**User says:**
> "push pillars to my new project at ~/projects/new-app"

**What happens:**
1. Scan current project Pillars (7 Pillars)
2. Scan target (empty)
3. Show: 7 NEW Pillars to add
4. Confirm and copy all
5. Report: "Added 7 Pillars"

**Time:** ~45 seconds

### Example 3: Selective Pillar Sync

**User says:**
> "sync only Pillar M and Q to my project"

**What happens:**
1. `cd ~/dev/ai-dev`
2. `/update-pillars ~/projects/my-app --pillars M,Q`
3. Compare only Saga and Idempotency Pillars
4. Show diff for selected Pillars
5. Sync if needed
6. Skip all other Pillars

**Time:** ~15 seconds

## Safety Features

**Pre-flight checks:**
- ✅ Source/target paths exist
- ✅ Source has .claude/pillars/ directory
- ✅ User confirmation before changes
- ✅ Dry-run preview available

**Smart filtering:**
- Profile-aware (respects project configuration)
- Only syncs enabled Pillars
- Clear status for each Pillar

**Error handling:**
- Invalid paths: Clear error message
- No updates needed: Skip gracefully
- Permission issues: Helpful guidance

## Error Handling

### Invalid Source/Target

```
❌ Error: Project not found

Path: ../nonexistent
Expected: ../nonexistent/.claude/pillars/

Please check:
1. Path is correct
2. Project has .claude/pillars/ directory
3. You have read permissions
```

### No Pillars to Update

```
✅ All Pillars are up to date!

No new or updated Pillars found in source.
Current project has all latest versions.
```

### OLDER Source (Warning)

```
⚠️ Warning: Source Pillar is OLDER

Pillar: A
Source: 2026-03-01 (245 lines)
Target: 2026-03-04 (250 lines)

Action: Skip (keeping newer target version)
```

## Best Practices

1. **Always dry-run first for major updates:**
```bash
cd ~/dev/ai-dev
/update-pillars ../my-app --dry-run
/update-pillars ../my-app
```

2. **Selective updates for safety:**
```bash
# Update only Pillars you understand
cd ~/dev/ai-dev
/update-pillars ../my-app --pillars A,B,K
```

3. **Framework as source of truth:**
```bash
# Always sync from ai-dev to projects
cd ~/dev/ai-dev
/update-pillars ../my-app
```

4. **Regular framework upgrades:**
```bash
# Monthly routine
cd ~/dev/ai-dev
/update-pillars ../my-app
```

## Integration

**With other update-* skills:**
```bash
# Must be in ai-dev directory
cd ~/dev/ai-dev

# Complete framework update
/update-pillars ../my-app   # 1. Pillars
/update-guides ../my-app    # 2. Guides
/update-skills ../my-app    # 3. Skills

# Or use meta-skill
/update-framework ../my-app # All-in-one
```

**Common workflow:**
```
Framework upgrade → Pull Pillars → Update Rules → Update Skills
Project setup → Push Pillars → Configure profile
```

## Task Management

**After each sync step**, update progress:

```
Paths validated → Update Task #1
Pillars scanned → Update Task #2
Changes detected → Update Task #3
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
- [ ] Pillars compared successfully
- [ ] User confirmed changes
- [ ] Files copied correctly
- [ ] Sync summary displayed
```

Missing items indicate incomplete sync.

## Workflow Skills Requirements

This is a **workflow skill** and must follow the standard pattern:

1. **TaskCreate** at start - Create todo list for progress tracking
2. **TaskUpdate** during execution - Mark tasks in_progress → completed
3. **Verification checklist** - Final validation before completion
4. **Output mode detection** - Check CALLED_BY_UPDATE_FRAMEWORK environment variable:
   - If set: Output 1-2 lines summary only (e.g., "✅ Pillars 同步完成: 18 个文件")
   - If not set: Output full detailed report (current behavior)

**See**: [WORKFLOW_PATTERNS.md](../WORKFLOW_PATTERNS.md) for complete implementation guide

## Testing

This skill has comprehensive test coverage following ADR-020 standards.

**Test suite includes:**
- 13 functional tests (core Pillars sync features)
- 10 argument tests (parameter validation)
- 11 safety tests (safety mechanisms)
- 11 error handling tests (exception scenarios)
- 5 integration tests (end-to-end workflows)

**Run tests:**
```bash
# All tests
pytest .claude/skills/update-pillars/tests/

# With coverage
pytest .claude/skills/update-pillars/tests/ --cov=.claude/skills/update-pillars --cov-report=term-missing

# Specific category
pytest .claude/skills/update-pillars/tests/test_functional.py
```

**Coverage:** 94% (target: ≥80%)

**See**: [tests/README.md](tests/README.md) for complete testing guide

## Related Skills

- **/update-framework** - Sync entire framework (calls this skill)
- **/update-rules** - Sync technical rules
- **/update-skills** - Sync skills
- **/update-workflow** - Sync workflow docs

---

**Version:** 3.1.0
**Last Updated:** 2026-04-07
**Changelog:**
- v3.1.0 (2026-04-07): Added comprehensive test suite with 94% coverage (50 tests, ADR-020 compliant) (Issue #531)
- v3.0.0 (2026-04-06): **BREAKING** - Removed --from/--to parameters, now only supports ai-dev → target (one direction)
- v2.2.0 (2026-04-06): **FEATURE** - Default to --to (push) when only path provided
- v2.1.0 (2026-03-12): Sync pillar documentation between projects
**Pattern:** Tool-Reference (guides sync process)
**Compliance:** ADR-001 Section 4 ✅ | ADR-020 ✅
