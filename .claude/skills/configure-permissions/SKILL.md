---
name: configure-permissions
description: |
  Configure Claude Code permissions for work-issue auto mode.
  TRIGGER when: user wants to configure permissions ("configure permissions", "set up auto mode", "enable work-issue auto mode"), after framework sync with --configure-permissions flag, during project initialization.
  DO NOT TRIGGER when: user just wants to read about permissions, asks conceptual questions about auto mode, or wants to modify permissions manually.
version: "3.0.0"
allowed-tools: Bash(uv *), Read, Write, Glob
disable-model-invocation: false
user-invocable: true
---

# Configure Permissions - Standard Permission Configuration

Configure Claude Code permissions by copying ai-dev's standard `.claude/settings.json` to your project.

## Overview

**Simplified approach**: This skill copies ai-dev's `.claude/settings.json` to your project as the standard configuration. No templates, no profile detection - just use ai-dev's own settings as the standard.

**What it does:**
1. **Locates ai-dev** root directory (auto-detection or explicit path)
2. **Reads** `ai-dev/.claude/settings.json`
3. **Copies** to target project `.claude/settings.json`
4. **Backs up** existing settings if present

**Why this approach:**
- ai-dev project itself is the "standard configuration"
- Simpler - no template system to maintain
- Consistent - all projects use same permissions
- Easy to update - edit ai-dev settings, sync to projects

**Why it's needed:**
Without pre-configured permissions, work-issue auto mode stops at every bash command to ask for approval, defeating the purpose of automation. This skill pre-configures the required permissions for seamless execution.

**When to use:**
- After `/update-framework` to configure target project
- When setting up work-issue auto mode for the first time
- When you want to sync updated permissions from ai-dev

## Arguments

```bash
/configure-permissions [target-path] [options]
```

**Common usage:**
```bash
/configure-permissions              # Configure current project (auto-detect ai-dev)
/configure-permissions ../my-proj   # Configure specific project
/configure-permissions --dry-run    # Preview changes without applying
/configure-permissions --source ~/dev/ai-dev  # Explicit ai-dev path
```

**Options:**
- `[target-path]` - Optional, defaults to current directory
- `--source <path>` - Explicit path to ai-dev root (auto-detected if not provided)
- `--dry-run` - Preview changes without modifying files

## Safety Features

**Pre-flight checks:**
- ✅ ai-dev root directory exists and is valid
- ✅ ai-dev settings.json exists and readable
- ✅ Target .claude/ directory exists
- ✅ Write permissions for target settings.json

**Smart defaults:**
- Auto-detects ai-dev from common locations (cwd, parent dirs, ~/dev/ai-dev)
- Creates backup before overwriting existing settings
- Preserves existing settings if copy fails
- Dry-run mode for safe preview

**Validation points:**
- Source path contains .claude/pillars/ (confirms ai-dev root)
- settings.json has valid JSON structure
- Target path is a valid directory
- No permission conflicts

**Data integrity:**
- Atomic file copy (no partial writes)
- Backup created with timestamp before overwrite
- Original preserved on failure
- Clear error messages on validation failure

## AI Execution Instructions

**CRITICAL: Direct file copy approach**

When executing `/configure-permissions`, AI MUST follow this pattern:

### Step 1: Create 4 Subtasks

```python
tasks = [
    TaskCreate(
        subject="Locate ai-dev root",
        description="Find ai-dev directory (contains .claude/pillars/)",
        activeForm="Locating ai-dev..."
    ),
    TaskCreate(
        subject="Validate paths",
        description="Verify ai-dev settings.json and target .claude/ directory",
        activeForm="Validating paths..."
    ),
    TaskCreate(
        subject="Copy settings.json",
        description="Copy ai-dev/.claude/settings.json to target",
        activeForm="Copying settings..."
    ),
    TaskCreate(
        subject="Report summary",
        description="Show what was configured",
        activeForm="Generating summary..."
    )
]
```

### Step 2: Execute with Status Updates

```python
# Step 1: Locate ai-dev
TaskUpdate(tasks[0], "in_progress")
ai_dev_root = find_ai_dev_root()  # Check cwd, parents, ~/dev/ai-dev, etc.
TaskUpdate(tasks[0], "completed")

# Step 2: Validate paths
TaskUpdate(tasks[1], "in_progress")
settings_source = ai_dev_root / ".claude" / "settings.json"
assert settings_source.exists(), "ai-dev settings.json not found"
TaskUpdate(tasks[1], "completed")

# Step 3: Copy settings
TaskUpdate(tasks[2], "in_progress")
target_settings = target_path / ".claude" / "settings.json"
if target_settings.exists():
    # Backup existing
    shutil.copy(target_settings, target_settings + ".backup")
shutil.copy(settings_source, target_settings)
TaskUpdate(tasks[2], "completed")

# Step 4: Report
TaskUpdate(tasks[3], "in_progress")
print(f"✅ Configured permissions from ai-dev")
print(f"   Source: {settings_source}")
print(f"   Target: {target_settings}")
TaskUpdate(tasks[3], "completed")
```

### Step 3: Call Python Script

```bash
uv run .claude/skills/configure-permissions/scripts/configure.py [target-path] [options]
```

**Script handles:**
- Auto-detection of ai-dev root
- Reading source settings.json
- Backing up existing target settings
- Writing new settings
- Validation and error handling

## Workflow

### Step 1: Locate ai-dev Root

**Auto-detection tries:**
1. Current directory (if contains `.claude/pillars/`)
2. Parent directories
3. `~/dev/ai-dev`
4. `~/projects/ai-dev`
5. `~/ai-dev`

**If not found:**
- Ask user to provide `--source` path explicitly

### Step 2: Validate Paths

**Check source:**
- ai-dev root exists
- `.claude/settings.json` exists in ai-dev
- settings.json is valid JSON

**Check target:**
- Target directory exists
- `.claude/` directory exists or can be created

### Step 3: Copy Settings

**Process:**
1. Read ai-dev's `.claude/settings.json`
2. If target has existing settings → backup to `.claude/settings.json.backup`
3. Write ai-dev settings to target `.claude/settings.json`
4. Verify write successful

**No merging:** Complete replacement (ai-dev is the standard)

### Step 4: Report Summary

```
✅ Configuration complete!

Source: /Users/user/dev/ai-dev/.claude/settings.json
Target: /Users/user/my-project/.claude/settings.json
Backup: /Users/user/my-project/.claude/settings.json.backup (if existed)

Permissions: 45 auto-approve patterns

Next steps:
  1. Review: cat .claude/settings.json
  2. Test: /work-issue --auto
```

## Usage Examples

### Example 1: Configure Current Project

**User says:**
> "configure permissions for this project"

**Execution:**
```bash
uv run .claude/skills/configure-permissions/scripts/configure.py .
```

**Result:**
- Auto-detects ai-dev from ~/dev/ai-dev
- Copies settings.json to current project
- Reports success

**Time:** ~5 seconds

### Example 2: Configure Specific Project

**User says:**
> "configure permissions for ../u-safe"

**Execution:**
```bash
uv run .claude/skills/configure-permissions/scripts/configure.py ../u-safe
```

**Result:**
- Locates ai-dev
- Copies settings to ../u-safe/.claude/settings.json
- Creates backup if existed

**Time:** ~5 seconds

### Example 3: Dry Run (Preview)

**User says:**
> "preview permission configuration for this project"

**Execution:**
```bash
uv run .claude/skills/configure-permissions/scripts/configure.py . --dry-run
```

**Output:**
```
Source (ai-dev): /Users/user/dev/ai-dev
Target project: /Users/user/my-project

🔍 DRY RUN - No changes will be made

Would backup existing: /Users/user/my-project/.claude/settings.json → .backup
Would write settings to: /Users/user/my-project/.claude/settings.json
Permissions: 45 auto-approve patterns
```

**Time:** <5 seconds

### Example 4: Explicit ai-dev Path

**User says:**
> "configure permissions using ai-dev from ~/repos/ai-dev"

**Execution:**
```bash
uv run .claude/skills/configure-permissions/scripts/configure.py . --source ~/repos/ai-dev
```

**Result:**
- Uses explicit ai-dev path
- Skips auto-detection
- Copies settings

**Time:** ~5 seconds

## Error Handling

### ai-dev Not Found

```
❌ Could not auto-detect ai-dev root directory

Tried:
- Current directory and parents
- ~/dev/ai-dev
- ~/projects/ai-dev
- ~/ai-dev

Please specify --source path explicitly
```

**Fix:** Provide explicit path with `--source`

### Source Settings Missing

```
❌ Source settings not found: /path/to/ai-dev/.claude/settings.json
```

**Fix:** Ensure ai-dev has `.claude/settings.json` file

### Target Directory Missing

```
❌ Target path does not exist: /path/to/target
```

**Fix:** Verify target path is correct

### Permission Denied

```
❌ Failed to write settings: [Errno 13] Permission denied
```

**Fix:** Check write permissions on target `.claude/` directory

## Integration

**Called by:**
- `/update-framework --configure-permissions` (automatic after framework sync)
- Manual invocation when setting up auto mode

**Files involved:**
- Input: `ai-dev/.claude/settings.json` (standard config)
- Output: `target-project/.claude/settings.json`
- Backup: `target-project/.claude/settings.json.backup` (if existed)

## Best Practices

1. **After framework sync** - Always configure permissions after `/update-framework`
2. **Standard config** - Edit ai-dev's settings.json to update standard
3. **Test auto mode** - Run `/work-issue --auto` to verify configuration
4. **Keep in sync** - Re-run after updating ai-dev permissions
5. **Backup first** - Script automatically backs up existing settings

## Performance

- **Auto-detection:** <1 second
- **Copy operation:** <1 second
- **Total time:** ~5 seconds

Fast because:
- Simple file copy (no template processing)
- No profile detection needed
- No complex merging logic

## What Changed (v3.0.0)

**Before (v2.x):**
- Complex template system (all/safe/minimal/read-only)
- Profile-aware permission generation
- Hardcoded permission lists in code
- Template merging logic

**After (v3.0.0):**
- Direct file copy from ai-dev
- No templates, no profiles
- ai-dev is the standard
- Simpler, easier to maintain

**Migration:**
If you used custom templates before, edit `ai-dev/.claude/settings.json` directly and re-run this skill.

## Workflow Skills Requirements

This is a **workflow skill** and must follow the standard pattern:

1. **TaskCreate** at start - Create todo list for progress tracking
2. **TaskUpdate** during execution - Mark tasks in_progress → completed
3. **Verification checklist** - Final validation before completion

**See**: [WORKFLOW_PATTERNS.md](../WORKFLOW_PATTERNS.md) for complete implementation guide

## Related Skills

- **/update-framework** - Calls this skill with `--configure-permissions` flag
- **/work-issue** - Requires permissions configured by this skill

## Advanced Topics

For detailed guidance on:
- **Permission patterns** - Understanding autoApprovePatterns syntax
- **Security considerations** - What to approve vs require manual confirmation
- **Custom configurations** - Editing ai-dev settings for specific needs

**See**: [PERMISSIONS_GUIDE.md](../../../docs/PERMISSIONS_GUIDE.md)

---

**Version:** 3.0.0
**Pattern:** Tool-Reference (direct file copy)
**Compliance:** ADR-001 ✅ | WORKFLOW_PATTERNS.md ✅
**Last Updated:** 2026-03-28
**Changelog:**
- v3.0.0: Simplified to direct copy from ai-dev (removed template system)
- v2.0.1: Added template mode
- v2.0.0: Profile-aware configuration
- v1.0.0: Initial release
