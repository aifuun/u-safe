---
name: configure-permissions
description: |
  Configure Claude Code permissions for work-issue auto mode.
  TRIGGER when: user wants to configure permissions ("configure permissions", "set up auto mode", "enable work-issue auto mode"), after framework sync with --configure-permissions flag, during project initialization.
  DO NOT TRIGGER when: user just wants to read about permissions, asks conceptual questions about auto mode, or wants to modify permissions manually.
allowed-tools: Bash(python3 *), Read, Write, Glob
disable-model-invocation: false
user-invocable: true
---

# Configure Permissions - Permission Configuration for work-issue Auto Mode

Configure Claude Code permissions to enable seamless work-issue auto mode execution.

## Overview

This skill configures `.claude/settings.json` with required permissions for work-issue auto mode:

**What it does:**
1. **Reads or creates** `.claude/settings.json`
2. **Detects project profile** (minimal, node-lambda, react-aws, tauri-react, nextjs-aws)
3. **Generates permission templates** based on profile
4. **Merges permissions smartly** without overwriting existing config
5. **Creates backup** before modification
6. **Validates structure** to ensure correctness
7. **Reports changes** clearly

**Why it's needed:**
Without pre-configured permissions, work-issue auto mode stops at every bash command to ask for approval, defeating the purpose of automation. This skill pre-configures the minimal required permissions for seamless execution.

**When to use:**
- After `/update-framework` to configure target project
- During project initialization with `init-project.py --configure-permissions`
- When setting up work-issue auto mode for the first time
- After changing project profile

## Arguments

```bash
/configure-permissions [target-path] [options]
```

**Common usage:**
```bash
/configure-permissions              # Configure current project
/configure-permissions ../u-safe    # Configure target project
/configure-permissions --dry-run    # Preview changes without applying
```

**Options:**
- `[target-path]` - Optional, defaults to current directory
- `--dry-run` - Preview changes without modifying files
- `--profile <name>` - Override profile detection (minimal, node-lambda, react-aws, tauri-react, nextjs-aws)

## Workflow

### Step 1: Create Todo List

**Initialize configuration tracking** using TaskCreate:

```
Task #1: Detect project profile
Task #2: Load or create settings.json (blocked by #1)
Task #3: Generate permission templates (blocked by #1)
Task #4: Merge permissions (blocked by #2, #3)
Task #5: Create backup (blocked by #2)
Task #6: Write updated settings (blocked by #4, #5)
Task #7: Validate and report (blocked by #6)
```

After creating tasks, proceed with configuration execution.

## Required Permissions by Profile

### Minimal (all profiles)

**File operation and task management tools:**
```json
{
  "allowedPrompts": [
    // File operations (for execute-plan implementation)
    {"tool": "Read", "prompt": "*"},
    {"tool": "Write", "prompt": "*"},
    {"tool": "Edit", "prompt": "*"},
    {"tool": "Glob", "prompt": "*"},
    {"tool": "Grep", "prompt": "*"},
    // Task management (for progress tracking)
    {"tool": "TaskCreate", "prompt": "*"},
    {"tool": "TaskUpdate", "prompt": "*"},
    {"tool": "TaskList", "prompt": "*"},
    {"tool": "TaskGet", "prompt": "*"},
    // Git write operations
    {"tool": "Bash", "prompt": "git add *"},
    {"tool": "Bash", "prompt": "git commit *"},
    {"tool": "Bash", "prompt": "git push *"},
    {"tool": "Bash", "prompt": "git checkout *"},
    {"tool": "Bash", "prompt": "git branch *"},
    {"tool": "Bash", "prompt": "git fetch *"},
    {"tool": "Bash", "prompt": "git merge *"},
    {"tool": "Bash", "prompt": "git worktree *"},
    {"tool": "Bash", "prompt": "git rebase *"},
    {"tool": "Bash", "prompt": "git reset *"},
    {"tool": "Bash", "prompt": "git stash *"},
    // Git read operations (for execute-plan validation)
    {"tool": "Bash", "prompt": "git status *"},
    {"tool": "Bash", "prompt": "git diff *"},
    {"tool": "Bash", "prompt": "git log *"},
    // GitHub CLI
    {"tool": "Bash", "prompt": "gh issue *"},
    {"tool": "Bash", "prompt": "gh pr *"},
    {"tool": "Bash", "prompt": "gh api *"},
    {"tool": "Bash", "prompt": "gh auth *"}
  ]
}
```

### Node.js Projects (tauri-react, nextjs-aws, node-lambda)

**Additional permissions:**
```json
{"tool": "Bash", "prompt": "npm test"},
{"tool": "Bash", "prompt": "npm run lint"},
{"tool": "Bash", "prompt": "npm run build"},
{"tool": "Bash", "prompt": "npm install"},
{"tool": "Bash", "prompt": "npm ci"}
```

### Python Projects

**Additional permissions:**
```json
{"tool": "Bash", "prompt": "pytest *"},
{"tool": "Bash", "prompt": "python -m pytest *"},
{"tool": "Bash", "prompt": "python -m *"},
{"tool": "Bash", "prompt": "pip install *"}
```

## Profile Detection

**Detection logic:**

```
1. Check for .framework-install file
   → profile: <name> field

2. If not found, check package.json
   → Node.js project (check for react, next, tauri)

3. If not found, check pyproject.toml
   → Python project

4. Default to minimal profile
```

**Profiles:**
- `minimal` - Basic git + gh permissions only
- `node-lambda` - Minimal + npm + AWS CLI
- `react-aws` - node-lambda + React dev tools
- `tauri-react` - react-aws + Tauri CLI
- `nextjs-aws` - react-aws + Next.js CLI
- `python-fastapi` - Minimal + pytest + pip

## Permission Merging Logic

**Smart merging:**

```python
def merge_permissions(existing, new):
    # 1. Preserve existing allowedPrompts
    existing_prompts = existing.get("allowedPrompts", [])

    # 2. Add new prompts not already present
    for new_prompt in new["allowedPrompts"]:
        if not prompt_exists(existing_prompts, new_prompt):
            existing_prompts.append(new_prompt)

    # 3. Update settings
    existing["allowedPrompts"] = existing_prompts
    return existing

def prompt_exists(prompts, target):
    # Match by tool and prompt pattern
    for p in prompts:
        if p["tool"] == target["tool"] and p["prompt"] == target["prompt"]:
            return True
    return False
```

**Key principles:**
- Never remove existing permissions
- Add only missing permissions
- Preserve all other settings.json fields
- Maintain formatting and structure

## Backup Strategy

**Before modification:**

```bash
# Create timestamped backup
BACKUP=".claude/settings.json.backup-$(date +%Y%m%d-%H%M%S)"
cp .claude/settings.json "$BACKUP"

echo "✅ Backup created: $BACKUP"
```

**Rollback if needed:**
```bash
# Restore from backup
cp .claude/settings.json.backup-20260312-143000 .claude/settings.json
```

## Validation

**After configuration:**

```python
def validate_settings(settings):
    # Required fields
    assert "allowedPrompts" in settings
    assert isinstance(settings["allowedPrompts"], list)

    # Validate each prompt
    for prompt in settings["allowedPrompts"]:
        assert "tool" in prompt
        assert "prompt" in prompt
        assert prompt["tool"] in ["Bash", "Read", "Edit", "Write"]

    # Git operations present (critical for work-issue)
    git_prompts = [p for p in settings["allowedPrompts"] if "git" in p["prompt"]]
    assert len(git_prompts) >= 7  # add, commit, push, checkout, branch, fetch, merge

    return True
```

## Usage Examples

### Example 1: Configure Current Project

**User says:**
> "configure permissions for work-issue auto mode"

**What happens:**
1. Detect profile: react-aws (from .framework-install)
2. Load settings.json (or create if missing)
3. Generate permissions: tools (9) + git (18) + npm (5) = 32 prompts
4. Merge: Add 29 new, preserve 3 existing
5. Backup: .claude/settings.json.backup-20260312-143000
6. Write: Updated settings.json
7. Report: "✅ Configured 32 permissions (29 added, 3 existing)"

**Time:** ~10 seconds

### Example 2: Configure Target Project

**User says:**
> "configure permissions for u-safe project"

**What happens:**
1. `/configure-permissions ../u-safe`
2. Detect profile: tauri-react
3. Generate permissions: tools (9) + git (18) + npm (5) + tauri (2) = 34 prompts
4. Create settings.json (didn't exist)
5. Write: New settings.json with 34 permissions
6. Report: "✅ Created settings.json with 34 permissions"

**Time:** ~10 seconds

### Example 3: Dry Run Preview

**User says:**
> "preview permission changes without applying"

**What happens:**
1. `/configure-permissions --dry-run`
2. Detect profile: nextjs-aws
3. Generate permissions: 18 prompts
4. Compare with existing: 10 existing, 8 to add
5. Show diff:
   ```
   📋 Dry Run - Preview Changes

   Would add 8 permissions:
   + {"tool": "Bash", "prompt": "npm run lint"}
   + {"tool": "Bash", "prompt": "npm run build"}
   + ... (6 more)

   Would preserve 10 existing permissions

   No changes written (dry run mode)
   ```

**Time:** ~5 seconds

## Integration with update-framework

**Called automatically:**

```bash
/update-framework ../target --configure-permissions
```

**Workflow:**
1. update-framework syncs Pillars, Rules, Workflow, Skills
2. Calls configure-permissions skill automatically
3. Shows permission summary in final report

**Example output:**
```
Framework Sync Complete! (36 files updated)

Permissions Configured:
✅ Detected profile: nextjs-aws
✅ Added 12 new permissions
✅ Preserved 3 existing permissions
✅ Backup: .claude/settings.json.backup-20260312-143000

work-issue auto mode ready!
```

## Integration with init-project

**Called during initialization:**

```bash
python3 scripts/init-project.py --profile=tauri-react --name=my-app --configure-permissions
```

**Workflow:**
1. init-project creates project structure
2. Installs framework files
3. Calls configure-permissions automatically
4. Project ready for work-issue auto mode

**Default behavior:**
- `--configure-permissions` flag optional (defaults to True)
- Can opt-out with `--no-configure-permissions`

## Error Handling

### Invalid Target Path

```
❌ Error: Project not found

Path: ../nonexistent
Expected: ../nonexistent/.claude/

Please check:
1. Path is correct
2. Project has .claude/ directory
3. You have write permissions
```

### Invalid Profile

```
❌ Error: Unknown profile

Profile: invalid-profile
Valid profiles:
- minimal
- node-lambda
- react-aws
- tauri-react
- nextjs-aws
- python-fastapi

Fix: Use --profile with valid profile name
```

### Permission Denied

```
❌ Error: Cannot write to settings.json

File: .claude/settings.json
Reason: Permission denied

Please check:
1. File is not read-only
2. No other process is locking the file
3. You have write permissions to .claude/
```

### Invalid settings.json

```
❌ Error: Invalid JSON in settings.json

File: .claude/settings.json
Error: Unexpected token at line 15

Options:
1. Fix manually and retry
2. Delete and recreate (backup will be preserved)
3. Restore from backup: settings.json.backup-*
```

## Safety Features

**Pre-flight checks:**
- ✅ Target path exists and has .claude/ directory
- ✅ User confirmation before changes (unless in auto mode)
- ✅ Dry-run preview available
- ✅ Automatic backup before modification

**Smart merging:**
- Never removes existing permissions
- Only adds missing permissions
- Preserves all other settings fields
- Maintains JSON structure

**Validation:**
- Ensures valid JSON structure
- Validates required fields
- Checks permission format
- Verifies git operations present

## Best Practices

1. **Run after framework installation:**
```bash
# New project
python3 scripts/init-project.py --profile=react-aws --name=my-app --configure-permissions

# Existing project
/update-framework ../target --configure-permissions
```

2. **Use dry-run for preview:**
```bash
/configure-permissions --dry-run
/configure-permissions --dry-run ../target
```

3. **Profile-specific configuration:**
```bash
# Override auto-detection
/configure-permissions --profile=minimal

# Target specific project type
/configure-permissions ../python-api --profile=python-fastapi
```

4. **Verify after configuration:**
```bash
# Check settings.json
cat .claude/settings.json | jq '.allowedPrompts'

# Test work-issue auto mode
/work-issue 123 --auto
```

## Output Examples

### Successful Configuration

```
📋 Configuring permissions for work-issue auto mode

1. Detecting profile...
   ✅ Found profile: react-aws (from .framework-install)

2. Loading settings.json...
   ✅ Found existing settings

3. Generating permission templates...
   ✅ Generated 15 permissions (git: 10, npm: 5)

4. Merging permissions...
   ✅ Added 12 new permissions
   ✅ Preserved 3 existing permissions

5. Creating backup...
   ✅ Backup: .claude/settings.json.backup-20260312-143000

6. Writing updated settings...
   ✅ Updated .claude/settings.json

7. Validating configuration...
   ✅ Valid structure
   ✅ All git operations present
   ✅ All npm operations present

✅ Configuration complete!

work-issue auto mode is now ready to run without permission prompts.
```

### Dry Run Output

```
📋 Dry Run - Preview Changes (no files modified)

Profile: nextjs-aws
Target: .claude/settings.json

Would add 8 permissions:
+ {"tool": "Bash", "prompt": "npm run lint"}
+ {"tool": "Bash", "prompt": "npm run build"}
+ {"tool": "Bash", "prompt": "npm test"}
+ {"tool": "Bash", "prompt": "npm install"}
+ {"tool": "Bash", "prompt": "npm ci"}
+ {"tool": "Bash", "prompt": "gh issue *"}
+ {"tool": "Bash", "prompt": "gh pr *"}
+ {"tool": "Bash", "prompt": "git worktree *"}

Would preserve 10 existing permissions

Total permissions after merge: 18

✅ Dry run complete - no changes written
```

## Task Management

**After each configuration step**, update progress:

```
Profile detected → Update Task #1
Settings loaded → Update Task #2
Templates generated → Update Task #3
Permissions merged → Update Task #4
Backup created → Update Task #5
Settings written → Update Task #6
Validation passed → Update Task #7
```

Provides real-time visibility of configuration progress.

## Final Verification

**Before declaring configuration complete**, verify:

```
- [ ] All 7 configuration tasks completed
- [ ] Profile detected or specified
- [ ] settings.json exists
- [ ] Backup created (if modified existing file)
- [ ] All git permissions present
- [ ] Profile-specific permissions added
- [ ] JSON structure validated
- [ ] Configuration summary displayed
```

Missing items indicate incomplete configuration.

## Workflow Skills Requirements

This is a **workflow skill** and must follow the standard pattern:

1. **TaskCreate** at start - Create todo list for progress tracking
2. **TaskUpdate** during execution - Mark tasks in_progress → completed
3. **Verification checklist** - Final validation before completion

**See**: [WORKFLOW_PATTERNS.md](../WORKFLOW_PATTERNS.md) for complete implementation guide

## Related Skills

- **/update-framework** - Calls this skill with --configure-permissions flag
- **/work-issue** - Benefits from configured permissions (auto mode)
- **/start-issue** - Uses git/gh permissions for branch creation
- **/finish-issue** - Uses git/gh permissions for PR and merge

---

**Version:** 1.0.0
**Pattern:** Tool-Reference (guides configuration process)
**Compliance:** ADR-001 ✅ | WORKFLOW_PATTERNS.md ✅
**Last Updated:** 2026-03-12
