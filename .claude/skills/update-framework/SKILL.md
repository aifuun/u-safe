---
name: update-framework
description: |
  Sync framework content (Pillars, Skills) - Rules excluded (use /manage-rules).
  TRIGGER when: user wants complete framework sync ("update framework from X", "sync entire framework", "pull all from framework", "upgrade framework").
  DO NOT TRIGGER when: user wants specific components only (use /update-pillars, /update-skills), or just wants to read framework docs.
version: "4.1.1"
framework-only: true
allowed-tools: Bash(cp *), Bash(mkdir *), Bash(ls *), Bash(find *), Bash(test *), Bash(cat *), Bash(git *), Bash(gh *), Read, Write, Glob, Grep, Edit
disable-model-invocation: false
user-invocable: true
---

# Update Framework - Complete Framework Synchronization Meta-Skill

Sync framework components (Pillars, Guides, Skills) between projects in one command.

## Overview

This meta-skill orchestrates framework content synchronization:

**What it does:**
1. Syncs Pillars from framework (18 coding standards)
2. Syncs Guides (AI reference docs and profiles)
3. Syncs Skills (workflow automation commands)

**Note**: Rules are project-specific and generated via `/manage-rules` (see ADR-013).

**Why it's needed:**
Monthly framework upgrades require syncing framework components. Running separate commands with multiple confirmations takes time. This meta-skill does it in one command in ~30 seconds.

**When to use:**
- Monthly framework upgrades (pull all updates)
- Initial project setup (push framework to new project)
- Complete framework sync needed
- Cross-project consistency enforcement

## AI Execution Instructions

**CRITICAL: Task creation and skill delegation**

When executing `/update-framework`, AI MUST follow this pattern:

### Step 1: Create 6 or 7 Subtasks

```python
# Create all tasks at the start
tasks = {
    "profile": TaskCreate(
        subject="Detect tech stack profile",
        description="Load profile from .framework-install or run questionnaire",
        activeForm="Detecting profile..."
    ),
    "validate": TaskCreate(
        subject="Validate source and target paths",
        description="Verify ai-dev and target project exist",
        activeForm="Validating paths..."
    ),
    "pillars": TaskCreate(
        subject="Sync Pillars via update-pillars",
        description="Call /update-pillars with profile filters",
        activeForm="Syncing Pillars..."
    ),
    "guides": TaskCreate(
        subject="Sync Guides via update-guides",
        description="Call /update-guides",
        activeForm="Syncing Guides..."
    ),
    "skills": TaskCreate(
        subject="Sync Skills via update-skills",
        description="Call /update-skills",
        activeForm="Syncing Skills..."
    ),
    "summary": TaskCreate(
        subject="Report comprehensive summary",
        description="Aggregate results and display stats",
        activeForm="Generating summary..."
    )
}

# Add permissions task by default (unless --without-permission-enable flag set)
if not without_permission_enable:
    tasks["permissions"] = TaskCreate(
        subject="Sync permissions via update-permissions",
        description="Copy .claude/settings.json from framework to target",
        activeForm="Syncing permissions..."
    )
```

### Step 2: Execute with Status Updates

```python
# Profile detection
TaskUpdate(tasks["profile"], "in_progress")
profile = detect_profile_from_framework_install(target_path)
TaskUpdate(tasks["profile"], "completed")

# Path validation
TaskUpdate(tasks["validate"], "in_progress")
validate_paths(source, target)
TaskUpdate(tasks["validate"], "completed")

# Set environment variable for sub-skills to detect meta-skill mode
import os
os.environ["CALLED_BY_UPDATE_FRAMEWORK"] = "1"

# Call update-pillars sub-skill
TaskUpdate(tasks["pillars"], "in_progress")
Skill("update-pillars", args=f"--to {target} --pillars {profile.pillars} --skip-validation")
TaskUpdate(tasks["pillars"], "completed")

# Call update-guides sub-skill
TaskUpdate(tasks["guides"], "in_progress")
Skill("update-guides", args=f"--to {target} --skip-validation")
TaskUpdate(tasks["guides"], "completed")

# Call update-skills sub-skill
TaskUpdate(tasks["skills"], "in_progress")
Skill("update-skills", args=f"--to {target} --skip-validation")
TaskUpdate(tasks["skills"], "completed")

# Call update-permissions sub-skill by default (unless --without-permission-enable flag set)
if not without_permission_enable and "permissions" in tasks:
    TaskUpdate(tasks["permissions"], "in_progress")
    Skill("update-permissions", args=f"--to {target} --skip-validation")
    TaskUpdate(tasks["permissions"], "completed")

# Clean up environment variable after all sub-skills complete
del os.environ["CALLED_BY_UPDATE_FRAMEWORK"]

# Summary (optimized table format)
TaskUpdate(tasks["summary"], "in_progress")
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 Framework 同步完成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌────────────────┬──────────┬─────────┐
│ 组件           │ 状态     │ 文件数  │
├────────────────┼──────────┼─────────┤
│ Pillars        │ ✅ 完成  │ 18      │
│ Guides         │ ✅ 完成  │ 20      │
│ Skills         │ ✅ 完成  │ 28      │
│ Permissions    │ ✅ 完成  │ 1       │
└────────────────┴──────────┴─────────┘

总计: 67 个文件已同步
下一步: /manage-rules --profile tauri --instant
""")
TaskUpdate(tasks["summary"], "completed")
```

### Step 3: DO NOT Use Direct rsync

**❌ WRONG - Do not do this:**
```python
rsync -av .claude/pillars/ ../target/.claude/pillars/
rsync -av .claude/rules/ ../target/.claude/rules/
rm -rf ../target/.claude/rules/backend  # Manual cleanup
```

**✅ CORRECT - Delegate to sub-skills:**
```python
Skill("update-pillars", args="--to ../target --pillars A,B,K,L")
Skill("update-rules", args="--to ../target --profile nextjs-aws")
Skill("update-skills", args="--to ../target")
```

**Why**: Sub-skills handle filtering, validation, error handling, and backups correctly.

## Workflow

### Step 0: Profile-Based Filtering (Auto-Detection)

**Before syncing, auto-detect the target project's profile** to filter irrelevant components.

**How it works:**
1. **Auto-detect profile** from `docs/project-profile.md` file in target project
2. **Load profile configuration** from `.claude/profiles/{profile}.json`
3. **Extract rules list** from profile's `rules` array
4. **Filter during sync** - only copy rules that match the profile
5. **Fallback to questionnaire** if `.framework-install` not found

**Supported profiles:**
- `tauri` - 4 Pillars (A, B, K, L), 23 rules - Desktop apps (Tauri + React)
- `tauri-aws` - TBD Pillars, TBD rules - Desktop + cloud backend
- `nextjs-aws` - 15 Pillars (full-stack), 30 rules - Full-stack web apps (Next.js + AWS)

**Actual results (from Issue #162):**
- u-safe (tauri): 46 rules → 23 rules ✅ (50% reduction, 100% compliance)
- buffer (nextjs-aws): 43 rules → 30 rules ✅ (30% reduction, 100% compliance)
- Zero incorrect rules after profile-aware sync

**Benefits:**
- ✅ **No repetitive questions** - Profile already known from init-project
- ✅ **Consistent filtering** - Same rules every time based on profile
- ✅ **Automatic** - Works without user interaction
- ✅ **Fallback available** - Questionnaire still used if config missing

**See**: [PROFILE_FILTERING.md](PROFILE_FILTERING.md) for profile detection logic and examples.

### Step 1: Create Todo List

**Initialize sync tracking** using TaskCreate:

```
Task #0: Tech stack questionnaire (if needed)
Task #1: Validate source and target paths (blocked by #0)
Task #2: Aggregate component analysis (blocked by #1)
Task #3: Show unified diff preview (blocked by #2)
Task #4: Execute all component syncs (blocked by #3)
Task #5: Collect results from all components (blocked by #4)
Task #6: Report comprehensive summary (blocked by #5)
```

After creating tasks, proceed with meta-sync execution.

## What Gets Synced

### Complete Framework (Default)

```
Sync Order (dependency-optimized):
1. 📚 Pillars    → .claude/pillars/            (Foundation)
2. 📖 Guides     → .claude/guides/             (AI reference docs)
3. ⚡ Skills     → .claude/skills/             (Implements workflow)
```

### Component Details

| Component | What Syncs | Delegated Skill |
|-----------|------------|-----------------|
| **Pillars** | 18 coding standards (.claude/pillars/) | /update-pillars |
| **Guides** | AI guides & profiles (.claude/guides/) | /update-guides |
| **Skills** | All skills (.claude/skills/) | /update-skills |

## Usage

### Push Framework to Target Project

**Must run from ai-dev framework directory.**

Push entire framework from ai-dev to target project:

```bash
# Must be in ai-dev directory
cd ~/dev/ai-dev

# Push to target project
/update-framework ../target-project
/update-framework ../target-project --dry-run
/update-framework ../target-project --skip skills
```

**What happens:**
0. **Validate working directory** - must be in ai-dev framework
1. Auto-detect profile from target project's `.framework-install`
2. Load profile configuration and extract rules list
3. Call all 4 update-* skills with target path and filter config
4. Aggregate analysis results (with filter summary)
5. Show what will be pushed
6. Confirm once
7. Execute all 4 syncs with smart filtering

### 3. Dry Run Mode (--dry-run)

Preview all changes without applying:

```bash
/update-framework --from ~/dev/ai-dev --dry-run
```

**Output:**
- Aggregated analysis from all 4 components
- Shows what would be synced
- No confirmation required
- No actual changes made

### 4. Selective Sync (--skip / --only)

Sync only specific components:

```bash
/update-framework --from ~/dev/ai-dev --only skills
/update-framework --from ~/dev/ai-dev --skip pillars
```

**Available components:**
- `pillars` - Pillar documentation
- `guides` - AI guides and profiles
- `skills` - Skills (commands)

**Note:** Cannot use both --skip and --only together.

### 5. Reconfigure Tech Stack (--reconfigure)

Update tech stack configuration and regenerate filters:

```bash
/update-framework --to ../u-safe --reconfigure
/update-framework --from ~/dev/ai-dev --reconfigure
```

**What happens:**
1. Ignore existing `.claude/framework-config.json`
2. Show tech stack questionnaire again
3. Generate new filter configuration based on new answers
4. Save updated config
5. Apply new filters during sync

**When to use:**
- Project tech stack changed (e.g., migrated from Vue to React)
- Added/removed cloud services (e.g., started using AWS)
- Want to adjust which rules are synced
- Initial config was incorrect

### 6. Configure Permissions (Default Behavior)

**Permission configuration is ENABLED BY DEFAULT** after framework sync:

```bash
# Default: permissions configured automatically
/update-framework ../target-project
/update-framework --from ~/dev/ai-dev

# Opt-out: skip permission configuration
/update-framework ../target-project --without-permission-enable
/update-framework --from ~/dev/ai-dev --without-permission-enable
```

**What happens by default:**
1. Complete framework sync (Pillars, Skills)
2. Automatically call `/update-permissions` skill
3. Copy `.claude/settings.json` from framework to target
4. Show permission summary in final report

**Configured permissions:**
- ✅ All git operations (add, commit, push, checkout, branch, fetch, merge, worktree)
- ✅ All gh CLI operations (issue, pr)
- ✅ Profile-specific operations (npm test/lint/build for Node.js projects, pytest for Python projects)

**When to skip (--without-permission-enable):**
- Already configured permissions manually
- Using custom permission setup
- Testing framework sync without modifying settings

**Result:**
After configuration, `work-issue --auto` runs without permission prompts.

## Orchestration Logic

**How meta-skill delegates to component skills:**

```
1. Call all 4 update-* skills with --dry-run flags
2. Capture and aggregate analysis from each skill
3. Show unified summary table with new/updated/unchanged counts
4. If NOT dry-run, confirm once
5. Execute all 4 syncs with filter configuration
6. Report comprehensive summary
```

**Sync order (dependency-aware):**
- Pillars → Skills

**See**: [ADVANCED.md](ADVANCED.md) for complete delegation flow, output examples, and partial failure recovery.

## Usage Examples

### Example 1: Framework Upgrade (Recommended Monthly)

**User says:**
> "update framework from ai-dev"

**What happens (with 7-task progress tracking):**

```
🚀 Starting framework sync...

Task Progress:
✅ Task 1/7: Detect tech stack profile (profile: tauri)
✅ Task 2/7: Validate source and target paths
⏳ Task 3/7: Syncing Pillars via update-pillars...
   Launching skill: update-pillars
   ✅ Synced 4 Pillars (A, B, K, L)
✅ Task 3/7: Complete

⏳ Task 4/7: Syncing Guides via update-guides...
   Launching skill: update-guides
   ✅ Synced 18 guide files
✅ Task 4/7: Complete

⏳ Task 5/7: Syncing Skills via update-skills...
   Launching skill: update-skills
   ✅ Synced 35 skills
✅ Task 5/7: Complete

✅ Task 6/7: Report comprehensive summary

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Profile: tauri
✅ Pillars: 18 synced
✅ Guides: 18 synced
✅ Skills: 35 synced
⚠️  Rules NOT synced (use /manage-rules --profile tauri)

Total: 71 items synced in 25 seconds
```

**Time:** ~30 seconds

### Example 2: Initial Project Setup

**User says:**
> "push entire framework to my new project at ~/projects/new-app"

**What happens:**
1. `/update-framework --to ~/projects/new-app`
2. Detect profile: nextjs-aws (from .framework-install)
3. Aggregate: 38 NEW items to push
4. Confirm once
5. Execute all 4 pushes with profile-based filtering
6. Report: "Pushed 38 items (nextjs-aws profile)"

**Time:** ~45 seconds

### Example 3: Selective Update (Documentation Only)

**User says:**
> "update framework from ai-dev but skip skills"

**What happens:**
1. `/update-framework --from ~/dev/ai-dev --skip skills`
2. Only call update-pillars
3. Aggregate: 8 items to sync (skip skills)
4. Confirm and sync
5. Report: "Updated 8 items (skipped skills)"

**Time:** ~20 seconds

### Example 4: Dry Run Preview

**User says:**
> "show me what would change if I pulled framework from ai-dev"

**What happens:**
1. `/update-framework --from ~/dev/ai-dev --dry-run`
2. Call all 4 skills with --dry-run
3. Show aggregated analysis
4. No confirmation, no changes
5. Report: "11 items would be synced (dry run)"

**Time:** ~15 seconds

## Safety Features

**Pre-flight checks:**
- ✅ Source/target paths exist
- ✅ Source has framework components
- ✅ All 4 component skills exist
- ✅ Single confirmation for all updates
- ✅ Dry-run preview available

**Smart defaults:**
- Dependency-aware sync order (Pillars → Skills)
- Aggregated summary before confirmation
- Progress shown for each component
- Clean error messages per component
- Partial failure handling (continue other components)

**Backup protection:**
- Inherited from individual update-* skills
- Each skill creates backups before overwrite
- Timestamped backup directories

## Error Handling

### Invalid Source/Target

```
❌ Error: Project not found

Path: ../nonexistent
Expected framework components in: ../nonexistent/

Please check:
1. Path is correct
2. Project has framework components (.claude/pillars/, .claude/)
3. You have read permissions
```

### Missing Component Skills

```
❌ Error: Required skill not found

Missing: update-pillars

This meta-skill requires these component skills:
- update-pillars
- update-skills

Please ensure all skills are installed.
```

### No Updates Needed

```
✅ All framework components are up to date!

No new or updated items found in source.
Current project has all latest versions.

┌────────────┬─────┬─────┬──────┐
│ Component  │ New │ Upd │ Same │
├────────────┼─────┼─────┼──────┤
│ Pillars    │  0  │  0  │  18  │
│ Skills     │  0  │  0  │  35  │
└────────────┴─────┴─────┴──────┘
```

### Partial Failure

```
⚠️  Framework sync completed with warnings

✅ Pillars: Updated 2 items
✅ Skills: Updated 3 items
⚠️  Rules NOT synced (use /manage-rules)

Summary:
- Successful: 2/2 components
- Total: 5 items synced

Framework sync complete.
```

## Best Practices

1. **Always dry-run first for major updates:**
```bash
/update-framework --from ~/dev/ai-dev --dry-run
/update-framework --from ~/dev/ai-dev
```

2. **Regular framework upgrades:**
```bash
# Weekly/monthly routine
/update-framework --from ~/dev/ai-dev
```

3. **Selective updates for safety:**
```bash
# Only update documentation first
/update-framework --from ~/dev/ai-dev --only pillars,rules,workflow

# Then update tools after testing
/update-framework --from ~/dev/ai-dev --only skills
```

4. **Framework as source of truth:**
```bash
# In projects: pull from framework
/update-framework --from ~/dev/ai-dev

# In framework: pull innovations from projects
/update-framework --from ~/projects/my-app --only skills
```

## Integration with Component Skills

**You can still use individual update-* skills:**

```bash
# Fine-grained control
/update-pillars --from ~/dev/ai-dev --pillars A,B,K
/update-skills --from ~/dev/ai-dev --skills adr,review

# For rules, use /manage-rules (deprecated: /update-rules)
/manage-rules --profile tauri --instant

# Coarse-grained control (this meta-skill)
/update-framework --from ~/dev/ai-dev
```

**When to use update-framework:**
- ✅ Monthly framework upgrades
- ✅ Initial project setup
- ✅ Complete sync needed
- ✅ Want simplicity (one command)

**When to use individual update-* skills:**
- ✅ Only need specific component
- ✅ Need fine-grained filtering (--pillars, --profile, etc.)
- ✅ Testing updates incrementally
- ✅ Debugging sync issues

## Task Management

**After each meta-sync step**, update progress:

```
Paths validated → Update Task #1
Component analysis aggregated → Update Task #2
Unified diff shown → Update Task #3
All component syncs executed → Update Task #4
Results collected → Update Task #5
Summary reported → Update Task #6
```

Provides real-time visibility of meta-sync progress.

## Final Verification

**Before declaring sync complete**, verify:

```
- [ ] All 6 or 7 meta-sync tasks completed (depending on permissions flag)
- [ ] Source and target paths valid
- [ ] All 3 component skills called successfully (pillars, guides, skills)
- [ ] User confirmed unified changes
- [ ] All components synced (or partial failure reported)
- [ ] Comprehensive summary displayed
- [ ] Tasks cleaned up (see cleanup logic below)
```

**Task Cleanup Logic**:
```python
# Get all current tasks
all_tasks = TaskList()

# Only delete tasks created by this skill execution
for task in all_tasks:
    if task.id in created_task_ids:  # created_task_ids from Step 1
        try:
            TaskUpdate(task.id, status="deleted")
        except Exception:
            pass  # Already cleaned up, ignore error
```

Missing items indicate incomplete meta-sync.

## Comparison with Individual Skills

| Aspect | Individual Skills | update-framework |
|--------|-------------------|------------------|
| **Commands** | 3 separate | 1 command |
| **Confirmations** | 3 prompts | 1 prompt |
| **Time** | ~90 seconds | ~25 seconds |
| **Complexity** | Must remember 3 | Simple, memorable |
| **Use case** | Fine-grained | Complete sync |

## Migration from v2.x

**Breaking Change**: Rules are no longer synced by `/update-framework`.

**Old workflow (v2.x)**:
```bash
/update-framework --from ~/dev/ai-dev
# Rules automatically synced
```

**New workflow (v4.0.0+)**:
```bash
# 1. Sync framework content (Pillars, Guides, Skills)
/update-framework --from ~/dev/ai-dev

# 2. Generate project-specific rules
/manage-rules --profile tauri --instant
```

**Why this change**: Rules are now profile-aware and project-specific. Different tech stacks need different rules (Tauri: 34, Next.js-AWS: 43, Minimal: 13). See ADR-013 for architecture details.

**Migration steps**:
1. Run `/update-framework` to sync Pillars, Guides, Skills (guides now included)
2. Run `/manage-rules --profile <your-profile>` to generate rules
3. Commit generated rules to your project

**See**: ADR-013 (#348) for complete architecture

## Workflow Skills Requirements

This is a **workflow skill** and must follow the standard pattern:

1. **TaskCreate** at start - Create todo list for progress tracking
2. **TaskUpdate** during execution - Mark tasks in_progress → completed
3. **Verification checklist** - Final validation before completion

**See**: [WORKFLOW_PATTERNS.md](../WORKFLOW_PATTERNS.md) for complete implementation guide

## Related Skills

- **/update-pillars** - Sync Pillars (called by this meta-skill)
- **/update-guides** - Sync AI guides and profiles (called by this meta-skill)
- **/update-skills** - Sync skills (called by this meta-skill)
- **/manage-rules** - Generate project-specific rules (separate workflow, ADR-013)

---

**Version:** 4.1.0
**Pattern:** Meta-Skill (orchestrates update-* skills)
**Compliance:** ADR-001 ✅ | ADR-013 ✅
**Last Updated:** 2026-03-29
**Changelog:**
- v4.1.0: Replace /configure-permissions with /update-permissions for direct framework copy (Issue #398)
- v4.0.0: Remove outdated workflow/rules references, update component structure (Issue #375)
- v3.0.0: **BREAKING** - Remove rules sync, use /manage-rules instead (Issue #353, ADR-013)
- v2.1.0: Added update-guides orchestration
- v2.0.0: Meta-skill architecture
