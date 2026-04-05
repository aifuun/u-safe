---
name: cleanup-project
description: |
  Clean temporary files and maintain .gitignore with profile-aware rules.

  TRIGGER when: User wants to clean project ("cleanup project", "clean temp files", "update gitignore"), monthly maintenance, or disk space issues.

  DO NOT TRIGGER when: User wants to clean specific files manually, or just wants to read .gitignore.
version: "2.0.0"
---

# Cleanup Project - Profile-Aware Maintenance

> Automate temporary file cleanup with safety mechanisms (ADR-014 compliant)

## Overview

Script-based skill for safe cleanup of temporary files with whitelist/blacklist protection.

**What it does:**
1. **Scans temp files** - Profile-aware detection (target/, node_modules/, .next/, etc.)
2. **Safety checks** - Whitelist protection prevents deletion of important files
3. **Dry-run mode** - Preview before deleting
4. **Health check** - Detect large unignored files

**Why script-based** (ADR-014):
- File deletion logic requires comprehensive safety tests
- Whitelist/blacklist patterns need unit testing
- Prevents accidental deletion of source code/config files
- Test coverage >60% ensures safety

**When to use:**
- Monthly maintenance routine
- Disk space issues
- After major refactoring
- Before archiving projects

## Arguments

```bash
/cleanup-project [options]
```

**Common usage:**
```bash
/cleanup-project                    # Clean temp files (with confirmation)
/cleanup-project --dry-run          # Preview without deleting
/cleanup-project --health-check     # Check for large unignored files
/cleanup-project --force            # Skip confirmation prompts
```

**Options:**
- `--dry-run` - Preview actions without executing
- `--force` - Skip confirmation prompts
- `--health-check` - Scan for large unignored files (>10MB)
- `--profile tauri|nextjs-aws|common` - Override auto-detection

## AI Execution Instructions

**CRITICAL: Use Python script for all cleanup operations**

When executing `/cleanup-project`, AI MUST call the Python script (do NOT implement logic in SKILL.md):

### Step 1: Parse Arguments

```python
args = parse_arguments(user_input)
# Extract: --dry-run, --force, --health-check, --profile

dry_run = '--dry-run' in args
force = '--force' in args
health_check = '--health-check' in args
profile = extract_profile(args) or None  # Auto-detect if not specified
```

### Step 2: Call Python Script

**For cleanup:**
```bash
# Dry-run mode (preview)
python3 .claude/skills/cleanup-project/scripts/cleanup.py --dry-run

# Execute cleanup (with confirmation unless --force)
python3 .claude/skills/cleanup-project/scripts/cleanup.py

# Force mode (skip confirmation)
python3 .claude/skills/cleanup-project/scripts/cleanup.py --force

# Specify profile
python3 .claude/skills/cleanup-project/scripts/cleanup.py --profile tauri
```

**For health check:**
```bash
python3 .claude/skills/cleanup-project/scripts/cleanup.py --health-check
```

### Step 3: Display Results

**Dry-run output:**
```
🧹 Project Cleanup

📋 Profile: tauri

🔍 Scanning for temporary files (DRY RUN)...

Would delete 5 items (2.3GB):
  - target/
  - node_modules/
  - __pycache__/
  - .DS_Store
  - .claude/.work-issue-state.json

Run without --dry-run to actually delete these files
```

**Execution output:**
```
🧹 Project Cleanup

📋 Profile: tauri

🗑️  Cleaning temporary files...

⚠️  About to delete 5 items.
Confirm deletion? [y/N] y

✅ Deleted 5 items (2.3GB)
```

**Health check output:**
```
🔍 Health Check - Large Files

⚠️  Found 2 large unignored files:

  - dist/bundle.js (15.2MB)
  - logs/app.log (22.5MB)

Recommendation: Add these to .gitignore if they're build artifacts
```

### Step 4: Error Handling

**Script not found:**
```bash
if [ ! -f ".claude/skills/cleanup-project/scripts/cleanup.py" ]; then
    echo "❌ Error: cleanup.py not found"
    echo "   Expected: .claude/skills/cleanup-project/scripts/cleanup.py"
    exit 1
fi
```

**Python not available:**
```bash
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    echo "   Install Python 3.7+ to use cleanup-project"
    exit 1
fi
```

**Permission errors:**
```
⚠️  Failed to delete target/debug/app: Permission denied
✅ Deleted 4 items (1.8GB) | Errors: 1
```

## Safety Mechanisms

**Whitelist Protection (NEVER DELETE):**
- `.git/` - Git repository
- `.env` - Environment secrets
- `*.py`, `*.md`, `*.ts`, `*.rs` - Source code
- `package.json`, `Cargo.toml` - Configuration
- `.claude/settings.json` - Framework settings
- `docs/` - Documentation

**Blacklist Cleanup (ALLOWED TO DELETE):**
- `target/` - Rust build artifacts (tauri)
- `node_modules/` - Node dependencies
- `.next/`, `cdk.out/` - Next.js/CDK artifacts (nextjs-aws)
- `__pycache__/`, `*.pyc` - Python bytecode
- `.DS_Store`, `Thumbs.db` - System temp files
- `.claude/.work-issue-state.json` - Workflow state

**Safety Logic:**
1. Check whitelist first (highest priority) → Skip if matched
2. Check if git-tracked → Skip if tracked
3. Check blacklist (cleanup rules) → Delete if matched
4. Default: Skip (conservative - don't delete if unsure)

**Confirmation Prompt:**
Unless `--force` is used, script will ask for confirmation before deleting files.

## Profile-Aware Rules

**Auto-detection** (in order):
1. Read `docs/project-profile.md` if exists
2. Detect feature files:
   - `src-tauri/Cargo.toml` → tauri
   - `.next/` or `cdk.json` → nextjs-aws
3. Fallback: common

**Profile rules:**
- **tauri**: Rust (`target/`) + Node (`node_modules/`) + Python
- **nextjs-aws**: Next.js (`.next/`) + CDK (`cdk.out/`) + Node
- **common**: System temp (`.DS_Store`) + Python (`__pycache__/`)

## Examples

### Example 1: Monthly Cleanup

**User:** "clean up the project"

**Execution:**
```bash
# Step 1: Preview (dry-run)
python3 .claude/skills/cleanup-project/scripts/cleanup.py --dry-run

# Output: Would delete 3 items (1.5GB)

# Step 2: Confirm and execute
python3 .claude/skills/cleanup-project/scripts/cleanup.py

# Output: Confirm deletion? [y/N] y
# ✅ Deleted 3 items (1.5GB)
```

**Time:** ~30 seconds

### Example 2: Force Cleanup

**User:** "clean project without asking"

**Execution:**
```bash
python3 .claude/skills/cleanup-project/scripts/cleanup.py --force

# Output: ✅ Deleted 3 items (1.5GB)
```

**Time:** ~10 seconds

### Example 3: Health Check

**User:** "check for large files"

**Execution:**
```bash
python3 .claude/skills/cleanup-project/scripts/cleanup.py --health-check

# Output: ⚠️ Found 2 large unignored files
#   - dist/bundle.js (15.2MB)
```

**Time:** ~20 seconds

## Testing

**Run tests:**
```bash
# All tests
python3 -m pytest .claude/skills/cleanup-project/tests/test_cleanup_safety.py -v

# With coverage
python3 -m pytest .claude/skills/cleanup-project/tests/test_cleanup_safety.py --cov=scripts/cleanup --cov-report=term-missing

# Should show >60% coverage
```

**Test categories:**
- Safety tests: Protected files never deleted
- Functionality tests: Temp files correctly deleted
- Dry-run tests: Preview mode doesn't actually delete
- Profile tests: Rules match profile
- Edge cases: Permission errors, missing files

## Architecture

**Pattern**: Script Type (ADR-014 score 6/14)

**File structure:**
```
.claude/skills/cleanup-project/
├── SKILL.md                  # This file (< 500 lines)
├── ARCHITECTURE.md           # Design documentation
├── scripts/
│   └── cleanup.py            # Core logic (Python)
└── tests/
    └── test_cleanup_safety.py # Safety tests (>60% coverage)
```

**Key classes:**
- `ProjectCleaner` - Main cleanup class
  - `scan_temp_files()` - Find temp files
  - `check_safe_to_delete()` - Safety check
  - `dry_run_cleanup()` - Preview mode
  - `execute_cleanup()` - Actual deletion

**See**: [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design

## Best Practices

1. **Always dry-run first** - Preview before deleting
2. **Monthly routine** - Clean projects regularly
3. **After refactoring** - Remove obsolete artifacts
4. **Trust safety checks** - Script protects important files
5. **Health check** - Find large unignored files

## Error Handling

**Permission errors:**
```
⚠️  Failed to delete target/debug/app: Permission denied
# Skips file, continues cleanup
```

**Missing files:**
```
# Handles gracefully (race condition)
# Skips already-deleted files
```

**Invalid profile:**
```
❌ Error: Invalid profile: unknown
    Must be one of: ['tauri', 'nextjs-aws', 'common']
```

## Performance

- **Dry-run:** <5 seconds (scan only)
- **Execution:** 10-30 seconds (depends on file count)
- **Health check:** 10-20 seconds (find large files)

Fast because:
- Python glob matching (efficient)
- Skip git-tracked files early
- Parallel-safe (no race conditions)

## Related Skills

- **/manage-claude-md --configure-profile** - Project profile management
- **/manage-claude-md** - Cleanup plans/ directory
- **/update-framework** - Framework sync and cleanup

## Migration Notes

**From v1.0.0 to v2.0.0:**
- Logic extracted to `scripts/cleanup.py` (ADR-014)
- Added safety tests (>60% coverage)
- SKILL.md simplified from 754 → <500 lines
- No behavior changes (backward compatible)

**Breaking changes:** None - same CLI interface

---

**Version:** 2.0.0
**Pattern:** Script Type (ADR-014 compliant)
**Last Updated:** 2026-03-30
**Compliance:** ADR-014 ✅
**Test Coverage:** >60% (see tests/test_cleanup_safety.py)
**Changelog:**
- v2.0.0: Script-based refactor (ADR-014) - logic to cleanup.py, added safety tests
- v1.0.0: Initial inline implementation (754 lines)
