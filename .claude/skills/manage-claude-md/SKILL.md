---
name: manage-claude-md
description: |
  Maintain CLAUDE.md and plans directory with profile awareness.
  TRIGGER when: user wants to update CLAUDE.md skills list, clean up plans, or run project health check.
  DO NOT TRIGGER when: user wants framework sync (use /update-framework), document management (use /manage-docs), or ADR management (use /manage-adrs).
version: "3.2.0"
allowed-tools: Bash(ls *), Bash(find *), Bash(gh *), Bash(git *), Read, Write, Glob, Grep, Edit
disable-model-invocation: false
user-invocable: true
---

# manage-claude-md - CLAUDE.md and Plans Maintenance

**Extracted from**: `/maintain-project` v1.1.0

## Overview

This skill provides automated maintenance for CLAUDE.md documentation and implementation plans.

**What it does:**
1. **Sync CLAUDE.md skills list** - Scans `.claude/skills/`, extracts metadata, updates skills table
2. **Clean plans directory** - Archives completed plans, removes stale ones, validates with GitHub
3. **Health check** - Generates 0-100 project health score with actionable recommendations
4. **Profile configuration** - Sets up or updates project profile in CLAUDE.md frontmatter
5. **Profile validation** - Validates installed skills against tech stack requirements

**Why it's needed:**
CLAUDE.md becomes outdated as skills are added/removed, causing Claude to reference non-existent skills or miss new capabilities. Plans accumulate after issues close, cluttering the workspace. Manual maintenance is error-prone and time-consuming. This skill automates these tasks in ~10 seconds vs 15-20 minutes manually.

**When to use:**
- After `/update-framework` or `/update-skills` (new skills installed)
- After adding 5+ new skills manually
- Monthly health check
- Before major releases (ensure documentation current)
- When plans directory feels cluttered

## Arguments

```bash
/manage-claude-md [options]
```

**Common usage:**
```bash
/manage-claude-md                      # Run all maintenance (sync + clean + health)
/manage-claude-md --instant            # Same as above (all-in-one)
/manage-claude-md --sync-skills        # Only sync CLAUDE.md skills list
/manage-claude-md --clean-plans        # Only clean plans/ directory
/manage-claude-md --health-check       # Only run health check
/manage-claude-md --configure-profile  # Configure profile in CLAUDE.md frontmatter
```

**Options:**
- `--instant` - Run all maintenance tasks in one command (sync + clean + health)
- `--sync-skills` - Only synchronize CLAUDE.md skills table with installed skills
- `--clean-plans` - Only archive completed plans and remove stale ones
- `--health-check` - Only generate project health score and recommendations
- `--configure-profile` - Interactive profile configuration (sets up project tech stack)

**Option combinations:**
- ✅ Can use multiple single-task options together: `--sync-skills --clean-plans`
- ✅ `--instant` runs all tasks, equivalent to `--sync-skills --clean-plans --health-check`
- ❌ Cannot combine `--instant` with other options (it already does everything)
- ❌ `--configure-profile` should run alone (interactive prompt)

**Exit codes:**
- `0` - Success (all selected tasks completed)
- `1` - Critical error (missing CLAUDE.md, invalid profile YAML)
- `2` - Partial failure (some tasks failed, others succeeded)

## Safety Features

This skill includes multiple safety mechanisms to prevent documentation corruption and data loss:

### 1. Pre-flight Validation

**What it checks:**
- CLAUDE.md file exists and is writable
- `.claude/plans/` directory exists
- Profile YAML syntax valid (if profile configured)
- GitHub CLI authenticated (for plans cleanup)

**Why it matters:**
- Prevents writing to non-existent files
- Ensures permissions before modification
- Validates profile data integrity
- Confirms issue status checks will work

**On failure:**
```
❌ Safety check failed: CLAUDE.md not writable

Check permissions: chmod 644 CLAUDE.md
Current owner: ls -la CLAUDE.md
```

### 2. Backup Before Modification

**How it works:**
```bash
# Automatic backup before CLAUDE.md updates
cp CLAUDE.md CLAUDE.md.backup
# Modify CLAUDE.md
# On success: rm CLAUDE.md.backup
# On failure: mv CLAUDE.md.backup CLAUDE.md
```

**Prevents:**
- Data loss from failed updates
- Corruption from interrupted writes
- Loss of manual customizations

**Restoration:**
```bash
# Manual restore if needed
mv CLAUDE.md.backup CLAUDE.md
```

### 3. Dry-run Validation

**Purpose**: Preview changes before applying

**How it works:**
```bash
# Skills sync dry-run
echo "Would add: manage-adrs, manage-claude-md"
echo "Would remove: adr (deprecated)"
echo "Would update: 3 version numbers"
# No actual writes performed
```

**Enables:**
- Review proposed changes
- Catch unexpected modifications
- Validate logic before execution

### 4. Profile Schema Validation

**Purpose**: Prevent invalid profile configurations

**How it works:**
```python
# Validate YAML structure
required_fields = ["name", "techStack"]
if not all(field in profile for field in required_fields):
    raise ProfileValidationError("Missing required fields")

# Validate tech stack values
valid_stacks = ["React", "Vue", "Rust", "Tauri", "Next.js"]
if profile.techStack not in valid_stacks:
    warn("Unknown tech stack, validation may be limited")
```

**Prevents:**
- Typos in profile names
- Invalid tech stack references
- Broken profile-based validation

### 5. Archive Safety (Plans Cleanup)

**Purpose**: Never delete plans that might be needed

**Safety rules:**
```bash
# Only archive if ALL conditions met:
1. Issue is CLOSED on GitHub (verified via gh CLI)
2. Plan file older than 7 days
3. Plan file not in .claude/plans/archive/ already

# Never delete:
- Active plans (issue still OPEN)
- Recent plans (< 7 days old)
- Already archived plans
```

**Prevents:**
- Accidental deletion of work-in-progress
- Loss of recent work
- Duplicate archiving

### Safety Best Practices

1. **Run --health-check first** - Preview state before changes
2. **Backup manually** - `cp CLAUDE.md CLAUDE.md.manual.backup` for critical updates
3. **Use --sync-skills alone** - Test skills sync before running full --instant
4. **Verify profile** - Check `docs/project-profile.md` syntax before --configure-profile
5. **Check archives** - Review `.claude/plans/archive/` before manual cleanup

---

## CLAUDE.md Best Practices

### Positioning

**Primary Audience**: Claude Code (AI agent)
- CLAUDE.md is the AI's project profile and operation memory
- Contains essential context for autonomous task execution
- Structured for machine parsing and human readability

**Secondary Audience**: Human Developers
- Quick reference for framework capabilities
- Onboarding guide for new team members
- Documentation hub linking to detailed guides

### Standard Architecture (13 Recommended Chapters)

```markdown
# {Project Name}

## 🎯 What Is This Project? (Essential - 50-100 lines)
## ⚡ Skills System (Essential - 30-50 lines)
## 🏗️ Core Architecture (Essential - 40-60 lines)
## 📋 Workflow & Status (Essential - 20-30 lines)
## 🔐 Permission Templates (Essential - 30-40 lines)
## 🚀 Quick Start (High value - 80-120 lines)
## 💡 Quick Examples (High value - 60-100 lines)
## 🧪 Testing (Important - 40-60 lines)
## 🛠️ Troubleshooting (Important - 50-80 lines)
## 📚 Documentation (Essential - 40-60 lines)
## 🤝 Contributing (Optional - 20-40 lines)
## 📄 License & Version (Essential - 10-20 lines)
```
**Total: ~300-420 lines ideal**

### DO / DON'T

**DO:**
- ✅ Link to detailed docs instead of duplicating content
- ✅ Use tables for Skills/Permissions (high information density)
- ✅ Include practical examples with actual commands
- ✅ Keep chapter summaries under 100 lines each
- ✅ Update Skills count when adding/removing skills
- ✅ Use emoji section markers for visual navigation
- ✅ Link to ADRs for architectural decisions
- ✅ Position as AI-first document (AI context > human reference)

**DON'T:**
- ❌ Duplicate Pillar/Rule content (link instead)
- ❌ Include full skill documentation (link to SKILL.md)
- ❌ Create multiple chapters for same topic
- ❌ Exceed 500 lines total (too dense for AI context)
- ❌ Use vague descriptions ("20+ skills" → specify "35 skills")
- ❌ Forget to update after major changes

### Length Control

**Ideal**: 300-400 lines
- Quick AI context loading
- Essential info only
- High signal-to-noise ratio

**Acceptable**: 400-500 lines
- Some redundancy allowed
- More examples included
- Still fits in AI context window

**Too Long**: >500 lines
- AI context overload risk
- Likely has duplication
- Consider splitting sections

### Information Density Classification

**High Density Areas** (optimize heavily):
- Skills System table
- Permission Templates table
- Quick Examples (commands only)
- Documentation links

**Medium Density** (balanced):
- What Is This Project
- Core Architecture
- Workflow & Status

**Low Density OK** (explanatory):
- Quick Start (step-by-step)
- Troubleshooting (detailed solutions)
- Testing (commands + explanations)

---

**When to Regenerate**: After framework sync (`/update-framework`), after adding 5+ skills, quarterly health check.

---

## Profile Integration

**Reads from** `docs/project-profile.md`:

```yaml
---
name: tauri
techStack:
  frontend: React
  backend: Rust
  desktop: Tauri
---
```

**Uses profile for**:
1. **Skills validation**: Check if installed skills match tech stack
2. **Health scoring**: Lower score if missing stack-specific skills
3. **Recommendations**: Suggest skills based on tech stack

**Example**:
```bash
Profile: tauri
Tech Stack: React, Rust, Tauri

✅ Good: tauri-specific skills installed
⚠️  Missing: No rust-analyzer skill found
💡 Recommend: Install /tauri-ipc skill for desktop-specific IPC patterns
```

---

## Error Handling

All operations include graceful error handling:

### 1. Missing Project Profile

```bash
if [ ! -f "docs/project-profile.md" ]; then
  echo "⚠️  Warning: Project profile not configured"
  echo "Run: /manage-claude-md --configure-profile --select-profile"
  echo "Continuing with reduced validation..."
  # Continue without profile-specific checks
fi
```

### 2. Invalid YAML Syntax

```bash
# Validate YAML before reading
if ! uv run -c "import yaml; yaml.safe_load(open('docs/project-profile.md'))" 2>/dev/null; then
  echo "⚠️  Warning: Invalid YAML in project-profile.md"
  echo "Continuing without profile validation..."
  # Skip profile-based validation
fi
```

### 3. GitHub CLI Not Available

```bash
# Check gh CLI availability
if ! command -v gh &> /dev/null; then
  echo "⚠️  Warning: gh CLI not found"
  echo "Plans cleanup will skip issue status checks"
  echo "Install: brew install gh"
  # Continue with file-based cleanup only
fi
```

### 4. File I/O Errors

```bash
# Check write permissions
if [ ! -w "CLAUDE.md" ]; then
  echo "❌ Error: No write permission for CLAUDE.md"
  echo "Check permissions: ls -la CLAUDE.md"
  exit 1
fi
```

---

## Core Functions

### 1. Sync CLAUDE.md Skills List

**What it does**:
1. Scans `.claude/skills/` for installed skills
2. Extracts metadata from each SKILL.md (name, version, description)
3. Compares with current CLAUDE.md skills table
4. Detects new/removed/updated skills
5. **NEW**: Validates against profile tech stack
6. Auto-updates skills table in CLAUDE.md

**Workflow**:
```bash
# 1. Scan installed skills
find .claude/skills -name "SKILL.md" -type f

# 2. Extract metadata from each skill
for skill in $(find .claude/skills -name "SKILL.md"); do
    name=$(grep "^name:" "$skill" | cut -d' ' -f2)
    version=$(grep "^version:" "$skill" | cut -d' ' -f2)
    description=$(grep "^description:" "$skill" | sed -n '/description:/,/^[a-z]/p')
done

# 3. Load profile for validation
if [ -f "docs/project-profile.md" ]; then
    tech_stack=$(sed -n '/techStack:/,/^[a-z]/p' docs/project-profile.md)
    echo "📋 Validating against tech stack: $tech_stack"
fi

# 4. Compare with CLAUDE.md current table
current_skills=$(sed -n '/## ⚡ Skills System/,/^## /p' CLAUDE.md | grep '|')

# 5. Detect differences
new_skills=$(comm -13 <(echo "$current_skills") <(echo "$installed_skills"))
removed_skills=$(comm -23 <(echo "$current_skills") <(echo "$installed_skills"))

# 6. Update CLAUDE.md skills table
# Preserve category structure (Issue Lifecycle, Quality, etc.)
# Add new skills to appropriate categories
# Remove deprecated skills
# Update version numbers
```

**Example output**:
```
CLAUDE.md Skills Sync
=====================
📋 Profile: tauri (React + Rust + Tauri)

✅ Scanned 35 installed skills
✅ Found 2 new skills not documented:
   - manage-adrs v2.0.0 (Management)
   - manage-claude-md v1.0.0 (Management)

✅ Found 1 removed skill still documented:
   - adr v1.1.0 (deprecated → use manage-adrs)

✅ Updated CLAUDE.md skills table

⚠️  Profile validation:
   - Missing skill for Rust: No rust-analyzer integration
   💡 Recommend: Add Rust-specific linting/formatting skills
```

---

### 2. Clean Plans Directory

**What it does**:
1. Scans `.claude/plans/active/` for plan files
2. Extracts issue numbers from plan metadata
3. **Checks issue status** via `gh issue view` (if available)
4. **Archives completed plans** to `.claude/plans/archive/`
5. **Deletes stale plans** (archived > 30 days)

**Workflow**:
```bash
# 1. Archive completed plans
for plan in .claude/plans/active/*.md; do
    issue_num=$(grep -oP 'Issue #\K\d+' "$plan" | head -1)

    # Check if gh CLI available
    if command -v gh &> /dev/null; then
        # Check issue status via GitHub
        if gh issue view "$issue_num" --json state --jq .state | grep -q "CLOSED"; then
            echo "✅ Archiving completed plan: $plan"
            mv "$plan" .claude/plans/archive/
        fi
    else
        # Fallback: archive plans older than 7 days
        if [ $(find "$plan" -mtime +7) ]; then
            echo "⚠️  Archiving old plan (no gh CLI): $plan"
            mv "$plan" .claude/plans/archive/
        fi
    fi
done

# 2. Delete stale archived plans (> 30 days)
for plan in .claude/plans/archive/*.md; do
    if [ $(find "$plan" -mtime +30) ]; then
        issue_num=$(grep -oP 'Issue #\K\d+' "$plan" | head -1)
        echo "🗑️  Deleting stale plan (>30 days): Issue #$issue_num"
        rm "$plan"
    fi
done
```

**Example output**:
```
Plans Cleanup
=============
✅ Found 3 completed plans in active/
✅ Archived 3 plans (issues closed)
✅ Deleted 1 stale plan (closed > 30 days ago)

Before: 8 files in active/
After:  5 files in active/ (optimal)
```

---

### 3. Project Health Check

**What it does**:
1. Analyzes project health across multiple dimensions
2. **Uses profile** for tech-stack-specific checks
3. Generates 0-100 health score
4. Provides actionable recommendations

**Health dimensions**:

| Dimension | Weight | Checks |
|-----------|--------|--------|
| **Documentation** | 30% | CLAUDE.md current, skills documented |
| **Plans hygiene** | 20% | Active plans <10, no stale plans |
| **Profile alignment** | 25% | Skills match tech stack |
| **Git status** | 15% | Clean working directory |
| **Dependencies** | 10% | No outdated dependencies |

**Scoring formula**:
```python
# Documentation (30 points max)
doc_score = 0
if claude_md_current: doc_score += 15
if all_skills_documented: doc_score += 10
if no_broken_links: doc_score += 5

# Plans hygiene (20 points max)
plans_score = 0
active_plans_count = len(glob(".claude/plans/active/*.md"))
if active_plans_count < 5: plans_score += 10
elif active_plans_count < 10: plans_score += 7
else: plans_score += 0

if no_stale_archived_plans: plans_score += 10

# Profile alignment (25 points max)
profile_score = 0
if profile_exists: profile_score += 10
if skills_match_tech_stack >= 80%: profile_score += 15

# Git status (15 points max)
git_score = 0
if clean_working_directory: git_score += 10
if no_untracked_files: git_score += 5

# Dependencies (10 points max)
deps_score = 0
if no_outdated_deps: deps_score += 10

# Total (100 points max)
total_score = doc_score + plans_score + profile_score + git_score + deps_score
```

**Health ratings**:
- **90-100**: Excellent ✅
- **70-89**: Good ⚠️
- **50-69**: Needs attention ⚠️
- **<50**: Critical ❌

**Example output**:
```
Project Health Check
====================
Profile: tauri (React + Rust + Tauri)

Score: 82/100 ⚠️ Good

Breakdown:
  Documentation:     25/30 ✅
  Plans hygiene:     18/20 ✅
  Profile alignment: 20/25 ⚠️
  Git status:        12/15 ✅
  Dependencies:      7/10 ⚠️

Issues:
  ⚠️  5 skills missing for tech stack (Rust/Tauri)
  ⚠️  2 npm packages have security vulnerabilities

Recommendations:
  1. Add Rust-specific skills for desktop development
  2. Run: npm audit fix
  3. Consider adding /tauri-ipc skill
  4. Update documentation for new skills

Next steps:
  - /manage-claude-md --sync-skills (fix documentation)
  - npm audit fix (fix dependencies)
```

---

## Command Options

### All-in-One (Default)

```bash
/manage-claude-md
# OR
/manage-claude-md --instant

# Runs all three functions:
# 1. Sync CLAUDE.md skills
# 2. Clean plans/
# 3. Health check
```

### Individual Components

```bash
# Only sync skills list
/manage-claude-md --sync-skills

# Only clean plans
/manage-claude-md --clean-plans

# Only health check
/manage-claude-md --health-check
```

---

## Scope vs Other Skills

**What manage-claude-md manages**:
- ✅ CLAUDE.md skills table
- ✅ .claude/plans/ directory
- ✅ Project health scoring

**What it does NOT manage** (use other skills):
- ❌ docs/ content → Use `/manage-docs`
- ❌ ADRs → Use `/manage-adrs`
- ❌ Skills installation → Use `/update-skills`
- ❌ Rules → Use `/manage-rules`
- ❌ Profile selection → Use `/manage-claude-md --configure-profile`

**Clear boundaries**:
```bash
# CLAUDE.md + plans/ maintenance
/manage-claude-md

# Documentation structure
/manage-docs

# ADRs management
/manage-adrs

# Profile selection
/manage-claude-md --configure-profile --select-profile

# Framework sync
/update-framework
```

---

## Migration from /maintain-project

**Old command** → **New command**:
```bash
/maintain-project              → /manage-claude-md --instant
/maintain-project --component plans → /manage-claude-md --clean-plans
```

**What's extracted**:
- ✅ CLAUDE.md skills sync
- ✅ plans/ cleanup
- ✅ Health check

**What's moved to other skills**:
- ❌ docs/ maintenance → `/manage-docs` (new skill)
- ❌ ADRs maintenance → `/manage-adrs` (renamed from /adr)

---

## Usage Examples

This section provides practical examples of manage-claude-md usage across different scenarios.

### Example 1: Monthly Maintenance Routine

**Scenario**: End of sprint, need to clean up workspace and verify project health

**User says:**
> "Run monthly maintenance on the project"

**Execution:**
```bash
/manage-claude-md --instant
```

**What happens:**
1. **Skills sync** - Scans `.claude/skills/`, finds 35 installed skills
   - Detects 2 new skills: `manage-adrs`, `manage-claude-md`
   - Detects 1 removed skill: `adr` (deprecated)
   - Updates CLAUDE.md skills table
2. **Plans cleanup** - Scans `.claude/plans/active/`
   - Finds 5 completed issues (verified via gh CLI)
   - Archives 5 plans to `.claude/plans/archive/`
   - Removes 2 stale plans (> 30 days old, issues closed)
3. **Health check** - Generates project health score
   - Score: 92/100 (Excellent)
   - 2 recommendations: Update ADR index, add missing tests

**Output:**
```
CLAUDE.md Skills Sync
=====================
✅ Updated 35 skills in CLAUDE.md
   +2 new: manage-adrs, manage-claude-md
   -1 removed: adr (deprecated)

Plans Directory Cleanup
=======================
✅ Archived 5 completed plans
✅ Removed 2 stale plans
📁 Active plans: 3 remaining

Project Health Check
====================
Score: 92/100 (Excellent)

Recommendations:
1. Update docs/ADRs/INDEX.md (2 new ADRs not indexed)
2. Add tests for manage-claude-md skill

Total time: 12 seconds
```

**Time:** ~10-15 seconds (vs 15-20 minutes manually)

### Example 2: After Installing New Skills

**Scenario**: Just ran `/update-skills` and installed 10 new skills from framework

**User says:**
> "Sync the new skills to CLAUDE.md"

**Execution:**
```bash
/manage-claude-md --sync-skills
```

**What happens:**
1. **Scan skills directory** - Finds 45 installed skills (was 35)
2. **Extract metadata** - Reads SKILL.md frontmatter for each skill
3. **Compare with CLAUDE.md** - Detects 10 new skills not documented
4. **Update skills table** - Adds new skills to appropriate categories
   - Issue Lifecycle: `start-issue`, `execute-plan`, `finish-issue`
   - Quality: `eval-plan`, `review`
   - Management: `manage-adrs`, `manage-claude-md`, `manage-docs`
   - Sync: `update-framework`, `update-skills`
5. **Profile validation** - Checks if new skills match tech stack (tauri profile)

**Output:**
```
CLAUDE.md Skills Sync
=====================
✅ Added 10 new skills to CLAUDE.md

New skills by category:
- Issue Lifecycle (3): start-issue, execute-plan, finish-issue
- Quality (2): eval-plan, review
- Management (3): manage-adrs, manage-claude-md, manage-docs
- Sync (2): update-framework, update-skills

Profile validation (tauri):
✅ All new skills compatible with tech stack

Updated: CLAUDE.md skills count (35 → 45)
```

**Time:** ~5 seconds

### Example 3: Clean Up After Multiple Issues Closed

**Scenario**: Finished 8 issues this week, plans directory cluttered

**User says:**
> "Archive completed plans"

**Execution:**
```bash
/manage-claude-md --clean-plans
```

**What happens:**
1. **Scan active plans** - Finds 11 plans in `.claude/plans/active/`
2. **Check GitHub status** - Uses `gh issue view` for each plan
   - 8 issues closed
   - 3 issues still open
3. **Archive completed** - Moves 8 plans to `.claude/plans/archive/`
4. **Remove stale** - Finds 1 plan for issue #42 (closed 45 days ago)
   - Moves to archive with timestamp
5. **Verify remaining** - 3 active plans remain

**Output:**
```
Plans Directory Cleanup
=======================
Scanned: 11 active plans

Archived (8):
✅ issue-101-plan.md (Issue #101 closed 2 days ago)
✅ issue-102-plan.md (Issue #102 closed 3 days ago)
✅ issue-103-plan.md (Issue #103 closed 1 day ago)
✅ issue-104-plan.md (Issue #104 closed 5 days ago)
✅ issue-105-plan.md (Issue #105 closed 4 days ago)
✅ issue-106-plan.md (Issue #106 closed 6 days ago)
✅ issue-107-plan.md (Issue #107 closed 2 days ago)
✅ issue-108-plan.md (Issue #108 closed 1 day ago)

Removed stale (1):
🗑️ issue-42-plan.md (Issue #42 closed 45 days ago)

Remaining active (3):
📋 issue-109-plan.md (Issue #109 - open)
📋 issue-110-plan.md (Issue #110 - open)
📋 issue-111-plan.md (Issue #111 - open)

Total freed: 450 KB
```

**Time:** ~8 seconds (depends on number of plans)

**Key insight:** Automatic GitHub verification ensures only truly completed plans are archived.

### Example 4: Configure Profile for New Project

**Scenario**: New Tauri project, need to set up project profile

**User says:**
> "Configure project profile"

**Execution:**
```bash
/manage-claude-md --configure-profile
```

**What happens (interactive):**
1. **Prompt for profile** - Shows available profiles
   ```
   Select project profile:
   1. tauri (React + Rust + Tauri)
   2. nextjs-aws (Next.js + AWS)
   3. python-cli (Python + CLI)
   4. custom (Manual configuration)
   ```
2. **User selects** - "1. tauri"
3. **Generate profile** - Creates `docs/project-profile.md`
4. **Update CLAUDE.md** - Adds profile to frontmatter
5. **Validate skills** - Checks if installed skills match profile

**Output:**
```
Project Profile Configuration
==============================

Selected profile: tauri
Tech stack: React, Rust, Tauri

✅ Created docs/project-profile.md
✅ Updated CLAUDE.md frontmatter

Profile validation:
✅ React-specific skills found (2)
⚠️ Missing Rust-specific skills
   💡 Recommend: Install rust-analyzer integration
✅ Tauri-specific skills found (1)

Next steps:
1. Review docs/project-profile.md
2. Run /manage-claude-md --sync-skills to validate skills
3. Consider installing recommended skills
```

**Time:** ~10 seconds (interactive, depends on user input)

**Key insight:** Profile configuration enables profile-aware validation and recommendations.

---

## Testing

This skill has comprehensive test coverage following ADR-020 standards.

### Test Suite

**Location**: `.claude/skills/manage-claude-md/tests/`

**Coverage**: Target ≥60% (ADR-020 requirement)

**Test Files**:
- `test_functional.py` (6 tests) - Core "What it does" functionality
- `test_arguments.py` (4 tests) - Argument validation and handling
- `test_safety.py` (5 tests) - Safety mechanisms validation

**Total**: 15 tests across 3 categories

### Running Tests

```bash
# Navigate to skill directory
cd .claude/skills/manage-claude-md

# Activate virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov --cov-report=term-missing

# Run specific category
pytest tests/test_functional.py
pytest tests/ -m functional
pytest tests/ -m safety
```

### Test Categories

**1. Functional Tests** (test_functional.py)
- Update skills list in CLAUDE.md
- Archive completed plans
- Generate project health report
- Clean stale status files (>24h old)
- Instant mode workflow
- Configure profile

**2. Argument Tests** (test_arguments.py)
- --instant flag triggers instant mode
- --dry-run shows preview without changes
- --configure-profile flag
- Invalid arguments raise errors

**3. Safety Tests** (test_safety.py)
- Backup before modify
- Atomic file operations
- Read-only validation
- Error recovery
- Dry-run no changes

### Detailed Documentation

See [tests/README.md](tests/README.md) for:
- Complete test suite overview
- Running tests with markers
- Adding new tests
- CI/CD integration
- Troubleshooting

---

## Best Practices

### When to Run

**Monthly routine**:
```bash
# Clean up after sprint
/manage-claude-md --instant
```

**After installing skills**:
```bash
# Sync new skills to CLAUDE.md
/manage-claude-md --sync-skills
```

**After completing issues**:
```bash
# Archive completed plans
/manage-claude-md --clean-plans
```

**Before releases**:
```bash
# Ensure project health
/manage-claude-md --health-check
```

---

## Integration with Workflow

### work-issue Integration

```bash
# work-issue can call this automatically after issue completion
/work-issue #23
  → start-issue
  → execute-plan
  → review
  → finish-issue
  → manage-claude-md --clean-plans (auto-cleanup)
```

### solve-issues Integration

```bash
# solve-issues can trigger maintenance after batch completion
/solve-issues #23 #24 #25
  → ... solve all issues ...
  → manage-claude-md --instant (batch cleanup)
```

---

## Related Documentation

- [CLAUDE.md](../../CLAUDE.md) - Main AI reference doc
- [Project Profile](../../docs/project-profile.md) - Tech stack config
- [Plans README](../.claude/plans/README.md) - Plans structure

---

## Notes for Claude

When user invokes `/manage-claude-md`:

1. **Always check profile first**:
   ```bash
   if [ -f "docs/project-profile.md" ]; then
       echo "📋 Using profile: $(grep 'name:' docs/project-profile.md)"
   else
       echo "⚠️  No profile configured (reduced validation)"
   fi
   ```

2. **Graceful degradation**:
   - If profile missing → skip tech stack validation
   - If gh CLI missing → use file-based plan cleanup
   - If errors occur → continue with warnings

3. **Logging**:
   ```bash
   LOG_FILE=".claude/logs/manage-claude-md-$(date +%Y%m%d).log"
   echo "[$(date)] Synced CLAUDE.md: +2 skills, -1 deprecated" >> "$LOG_FILE"
   ```

4. **Atomic operations**:
   - Backup CLAUDE.md before modifying
   - Use temp files for edits
   - Only replace if validation passes

---

**Version:** 3.2.0
**Pattern:** Profile-Aware Management Skill
**Compliance:** ADR-014 ✅ | ADR-020 ✅
**Last Updated:** 2026-04-07
**Changelog:**
- v3.2.0 (2026-04-07): Added comprehensive test suite - 15 tests across 3 categories (functional, arguments, safety), ADR-015/ADR-020 compliant (Issue #526)
- v2.0.0 (2026-04-07): Documentation refactor for ADR-020 compliance - Added Overview, Arguments, Safety Features, Usage Examples sections (Issue #514)
- v1.2.0 (2026-04-02): Added Python script implementation (sync_claude_md.py, cleanup_plans.py, health_report.py) - ADR-014 compliant (Issue #446)
- v1.0.0 (2026-03-27): Extracted from /maintain-project v1.1.0, added profile integration
