---
name: manage-project
version: "2.0.0"
description: Select and activate project profile with intelligent auto-detection
allowed-tools: Bash, Read, Write, Glob, Grep
user-invocable: true
---

# Manage Project - Profile Selection and Activation

Select and activate project profiles for tech-stack-specific configuration with intelligent auto-detection.

## Overview

This skill manages project profile configuration. Profiles define active Pillars, rules, tech stack, and documentation structure.

**What it does:**
1. **Intelligently detects** project profile using 4-level strategy
2. Lists available profiles from `.claude/guides/profiles/`
3. Allows interactive profile selection (with smart defaults)
4. Activates profile by copying to `docs/project-profile.md`
5. Displays current active profile
6. Shows detection process for debugging

**Intelligent Detection (NEW in v2.0):**
- **Level 1**: Check `docs/project-profile.md` (user's explicit configuration)
- **Level 2**: Check `docs/project-profile.md` (installation marker)
- **Level 3**: Smart tech stack detection (Cargo.toml, package.json, etc.)
- **Level 4**: Interactive selection (fallback)

**Why it's needed:**
Different tech stacks need different configurations. This skill provides a simple interface to switch between profiles (tauri, nextjs-aws, tauri-aws) and ensures all manage-* skills read from the same configuration file. The intelligent detection eliminates repetitive manual selection for already-configured projects.

**When to use:**
- During project initialization (called by `/init-docs`)
- When switching tech stacks
- To view current project configuration
- To debug profile detection issues

## Commands

```bash
/manage-project --select-profile          # Smart profile selection (with auto-detection)
/manage-project --select-profile --auto   # Auto-detect and use without confirmation
/manage-project --show-profile            # Display current active profile
/manage-project --list-profiles           # List all available profiles
/manage-project --show-detection          # Show detection process (debug mode)
```

## Detection Modes

### Auto Mode (--auto)

**Purpose**: Seamless profile selection without user intervention.

**Usage**:
```bash
/manage-project --select-profile --auto
```

**Behavior**:
- Runs 4-level detection
- If profile detected (Level 1/2/3): Uses automatically without confirmation
- If no profile detected: Falls back to interactive selection

**Use cases**:
- CI/CD pipelines
- Automated project setup scripts
- When you trust the detection logic completely

### Interactive Mode (default)

**Purpose**: User-confirmed profile selection with smart defaults.

**Usage**:
```bash
/manage-project --select-profile
```

**Behavior**:
- Runs 4-level detection
- If profile detected: Shows confirmation prompt
  ```
  ✓ Detected configured profile: tauri
  Continue using this profile? [Y/n]:
  ```
- User confirms (Y): Uses detected profile
- User declines (n): Shows full profile list for manual selection
- If no profile detected: Shows full profile list

**Use cases**:
- First-time profile setup
- Verifying detection accuracy
- When you want control over profile choice

### Debug Mode (--show-detection)

**Purpose**: Troubleshoot profile detection issues.

**Usage**:
```bash
/manage-project --show-detection
```

**Output example**:
```
🔍 Profile Detection Process

   Level 1: ✓ Found docs/project-profile.md (profile: tauri)
   Level 2: ✓ Found docs/project-profile.md (profile: tauri)
   Level 3: ✓ Detected tech stack Tauri Desktop

📊 Consistency Check

   Level 1: tauri
   Level 2: tauri
   Level 3: tauri
   ✅ All levels consistent
   Recommendation: tauri
```

**Use cases**:
- Profile not detected as expected
- Inconsistent detection across levels
- Understanding which detection method was used

## Workflow

Copy this checklist to track progress:

```
Task Progress:
- [ ] Step 1: Parse command arguments
- [ ] Step 2: Execute command (list/select/show)
- [ ] Step 3: Report results
```

Execute these steps in sequence:

### Step 1: Parse Command Arguments

**Detect command mode:**
```bash
# Default to --select-profile if no args
MODE="${1:---select-profile}"

case "$MODE" in
  --list-profiles)
    list_profiles
    ;;
  --show-profile)
    show_current_profile
    ;;
  --select-profile)
    select_and_activate_profile "$2"
    ;;
  --show-detection)
    show_detection_process
    ;;
  *)
    echo "Unknown option: $MODE"
    echo "Usage: /manage-project [--list-profiles|--show-profile|--select-profile [--auto]|--show-detection]"
    exit 1
    ;;
esac
```

### Step 2: Execute Command

#### List Profiles (--list-profiles)

**Scan available profiles:**
```bash
function list_profiles() {
  echo "📋 Available Profiles"
  echo

  # Find all profile files
  profiles=$(find .claude/guides/profiles -name "*.md" | sort)

  if [ -z "$profiles" ]; then
    echo "❌ No profiles found in .claude/guides/profiles/"
    echo "Run /update-guides to sync profiles from framework"
    exit 1
  fi

  # Parse and display each profile
  i=1
  for profile in $profiles; do
    name=$(grep "^name:" "$profile" | cut -d' ' -f2)
    desc=$(grep "^description:" "$profile" | cut -d' ' -f2-)
    category=$(grep "^category:" "$profile" | cut -d' ' -f2)

    echo "$i. $name ($category)"
    echo "   $desc"
    echo
    ((i++))
  done
}
```

**Expected output:**
```
📋 Available Profiles

1. nextjs-aws (fullstack)
   Full-stack Next.js application with AWS backend

2. tauri (desktop)
   Desktop application (Tauri + React, local-first)

3. tauri-aws (hybrid)
   Desktop application with cloud backend (Tauri + AWS)
```

#### Show Current Profile (--show-profile)

**Display active profile:**
```bash
function show_current_profile() {
  PROFILE_FILE="docs/project-profile.md"

  if [ ! -f "$PROFILE_FILE" ]; then
    echo "❌ No active profile"
    echo "Run /manage-project --select-profile to activate a profile"
    exit 1
  fi

  echo "📌 Current Active Profile"
  echo

  # Extract frontmatter
  name=$(grep "^name:" "$PROFILE_FILE" | cut -d' ' -f2)
  desc=$(grep "^description:" "$PROFILE_FILE" | cut -d' ' -f2-)
  category=$(grep "^category:" "$PROFILE_FILE" | cut -d' ' -f2)
  version=$(grep "^version:" "$PROFILE_FILE" | cut -d' ' -f2)

  echo "Name: $name"
  echo "Category: $category"
  echo "Version: $version"
  echo "Description: $desc"
  echo
  echo "Location: $PROFILE_FILE"
}
```

**Expected output:**
```
📌 Current Active Profile

Name: tauri
Category: desktop
Version: 1.0.0
Description: Desktop application (Tauri + React, local-first)

Location: docs/project-profile.md
```

#### Select and Activate Profile (--select-profile)

**Smart selection with auto-detection:**
```bash
function select_and_activate_profile() {
  AUTO_MODE=false
  if [ "$1" = "--auto" ]; then
    AUTO_MODE=true
  fi

  # Step 1: Try intelligent detection
  echo "🔍 Detecting project profile..."
  echo

  DETECTOR=".claude/skills/manage-project/profile_detector.py"
  if [ -f "$DETECTOR" ]; then
    # Run Python detector
    DETECTED_PROFILE=$(python3 "$DETECTOR" 2>/dev/null | grep "Detected profile:" | cut -d' ' -f3)
    DETECTION_METHOD=$(python3 "$DETECTOR" 2>/dev/null | grep "via" | cut -d' ' -f5 | tr -d ')')

    if [ -n "$DETECTED_PROFILE" ]; then
      echo "✓ Detected configured profile: $DETECTED_PROFILE (via $DETECTION_METHOD)"
      echo

      # Auto mode: use directly without confirmation
      if [ "$AUTO_MODE" = true ]; then
        activate_profile "$DETECTED_PROFILE"
        return 0
      fi

      # Interactive mode: confirm with user
      read -p "Continue using this profile? [Y/n]: " confirm
      confirm=${confirm:-Y}

      if [[ "$confirm" =~ ^[Yy]$ ]]; then
        activate_profile "$DETECTED_PROFILE"
        return 0
      else
        echo "Entering interactive selection..."
        echo
      fi
    fi
  fi

  # Step 2: Fallback to interactive selection
  echo "📋 Available Profiles"
  echo

  profiles=($(find .claude/guides/profiles -name "*.md" | sort))

  if [ ${#profiles[@]} -eq 0 ]; then
    echo "❌ No profiles found"
    echo "Run /update-guides to sync profiles from framework"
    exit 1
  fi

  # Display options
  i=1
  for profile in "${profiles[@]}"; do
    name=$(grep "^name:" "$profile" | cut -d' ' -f2)
    desc=$(grep "^description:" "$profile" | cut -d' ' -f2-)

    echo "$i. $name - $desc"
    ((i++))
  done

  echo
  read -p "Select profile [1-${#profiles[@]}]: " choice

  # Validate choice
  if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt ${#profiles[@]} ]; then
    echo "❌ Invalid selection: $choice"
    exit 1
  fi

  # Activate selected profile
  selected_profile="${profiles[$((choice-1))]}"
  profile_name=$(grep "^name:" "$selected_profile" | cut -d' ' -f2)
  activate_profile "$profile_name"
}

function activate_profile() {
  PROFILE_NAME=$1
  SOURCE=".claude/guides/profiles/${PROFILE_NAME}.md"
  TARGET="docs/project-profile.md"

  if [ ! -f "$SOURCE" ]; then
    echo "❌ Profile not found: $SOURCE"
    exit 1
  fi

  cp "$SOURCE" "$TARGET"

  echo
  echo "✅ Profile activated: $PROFILE_NAME"
  echo "Location: $TARGET"
  echo
  echo "Affected skills:"
  echo "  - /manage-rules (reads rules configuration)"
  echo "  - /manage-adrs (reads pillars configuration)"
  echo "  - /manage-claude-md (reads project metadata)"
  echo "  - /manage-docs (reads documentation structure)"
}

function show_detection_process() {
  DETECTOR=".claude/skills/manage-project/profile_detector.py"

  if [ ! -f "$DETECTOR" ]; then
    echo "❌ Profile detector not found"
    echo "Expected: $DETECTOR"
    exit 1
  fi

  # Run detector with --show-detection flag
  python3 "$DETECTOR" --show-detection

  # Also run consistency check
  echo
  python3 "$DETECTOR" --check-consistency
}
```

### Step 3: Report Results

**Success indicators:**
- ✅ Profile list displayed (--list-profiles)
- ✅ Current profile shown (--show-profile)
- ✅ Profile activated successfully (--select-profile)

**Error handling:**
- No profiles found → Suggest `/update-guides`
- Invalid selection → Show available options
- File write error → Check permissions

## Integration

**Used by:**
- `/init-docs` - Auto-activates profile during project setup
- User manual invocation - Change project profile

**Affects:**
- `/manage-rules` - Reads rules configuration from profile
- `/manage-adrs` - Reads pillars configuration from profile
- `/manage-claude-md` - Reads project metadata from profile
- `/manage-docs` - Reads documentation structure from profile

All manage-* skills read from `docs/project-profile.md` as single source of truth.

## Detection Rules (Level 3: Tech Stack)

### Tauri Desktop Profile

**Detected when:**
- ✅ `Cargo.toml` exists
- ✅ `src-tauri/tauri.conf.json` exists
- ❌ `cdk/` or `infra/` does NOT exist

**Profile**: `tauri`

### Tauri AWS Profile

**Detected when:**
- ✅ `Cargo.toml` exists
- ✅ `src-tauri/tauri.conf.json` exists
- ✅ `cdk/` or `infra/` exists

**Profile**: `tauri-aws`

### Next.js AWS Profile

**Detected when:**
- ✅ `package.json` contains `next` dependency
- ✅ `cdk/` or `infra/` exists

**Profile**: `nextjs-aws`

### Detection Priority

When multiple detection levels find different profiles:

1. **Level 1** (docs/project-profile.md) - Highest priority (user's explicit config)
2. **Level 3** (tech stack detection) - Medium priority (actual code state)
3. **Level 2** (docs/project-profile.md) - Lowest priority (historical record)

**Inconsistency handling:**
```
⚠️ Detected inconsistent profile configuration:
- docs/project-profile.md: tauri
- docs/project-profile.md: tauri-aws
- Tech stack detection: tauri-aws

Suggestion: Use tech stack detection result 'tauri-aws'
```

The tool will warn about inconsistencies and recommend the most accurate profile (usually Level 3 tech stack detection).

## Error Handling

### No Profiles Found

```
❌ No profiles found in .claude/guides/profiles/

Fix: Run /update-guides to sync profiles from framework
```

**Recovery:** Sync AI guides to get profile templates

### Invalid Selection

```
❌ Invalid selection: 5

Available options: 1-3
```

**Recovery:** Re-run command with valid choice

### File Write Error

```
❌ Permission denied: docs/project-profile.md

Fix: Check directory permissions
```

**Recovery:** Verify write access to docs/ directory

### No Active Profile

```
❌ No active profile found

Run /manage-project --select-profile to activate a profile
```

**Recovery:** Select and activate a profile first

## Usage Examples

### Example 1: List Available Profiles

```bash
/manage-project --list-profiles
```

**Output:**
```
📋 Available Profiles

1. nextjs-aws (fullstack)
   Full-stack Next.js application with AWS backend

2. tauri (desktop)
   Desktop application (Tauri + React, local-first)

3. tauri-aws (hybrid)
   Desktop application with cloud backend (Tauri + AWS)
```

### Example 2: Activate Profile

```bash
/manage-project --select-profile
```

**Interaction:**
```
📋 Available Profiles

1. nextjs-aws - Full-stack Next.js application with AWS backend
2. tauri - Desktop application (Tauri + React, local-first)
3. tauri-aws - Desktop application with cloud backend (Tauri + AWS)

Select profile [1-3]: 2

✅ Profile activated: tauri
Location: docs/project-profile.md

Affected skills:
  - /manage-rules (reads rules configuration)
  - /manage-adrs (reads pillars configuration)
  - /manage-claude-md (reads project metadata)
  - /manage-docs (reads documentation structure)
```

### Example 3: Show Current Profile

```bash
/manage-project --show-profile
```

**Output:**
```
📌 Current Active Profile

Name: tauri
Category: desktop
Version: 1.0.0
Description: Desktop application (Tauri + React, local-first)

Location: docs/project-profile.md
```

## Best Practices

1. **Run after framework sync** - Ensure profiles are up-to-date with `/update-guides`
2. **Activate during init** - Let `/init-docs` auto-activate profile
3. **Switch deliberately** - Profile changes affect multiple skills
4. **Verify activation** - Use `--show-profile` to confirm
5. **Document changes** - Note profile switches in project history

## Related Skills

- **/init-docs** - Calls this skill during project initialization
- **/update-guides** - Syncs profiles from framework to project
- **/manage-rules** - Uses activated profile for rules filtering
- **/manage-adrs** - Uses activated profile for Pillar selection
- **/manage-claude-md** - Uses activated profile for metadata

---

**Version:** 1.0.0
**Pattern:** Tool-Reference (guides profile management workflow)
**Compliance:** ADR-001 ✅
**Last Updated:** 2026-03-27
**Changelog:**
- v1.0.0: Initial release - Profile selection and activation (Issue #370)
