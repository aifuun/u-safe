---
name: manage-rules
version: "1.0.0"
description: Generate profile-aware rules from templates
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
user-invocable: true
---

# Manage Rules - Profile-Aware Rule Generation

Generate project-specific technical rules from templates based on project profile.

## Overview

This skill automates rule file generation by:

**What it does:**
1. **Detects project profile** - Auto-reads `.framework-install` or accepts `--profile` argument
2. **Loads profile configuration** - Reads `framework/profiles/{profile}.json` for whitelist
3. **Scans rule templates** - Finds all templates in `docs/ai-guides/rules/templates/`
4. **Filters by profile** - Applies `rules.include` whitelist (34-43 rules per stack)
5. **Generates rule files** - Copies filtered templates to `.claude/rules/`
6. **Reports results** - Shows generated count and file locations

**Why it's needed:**
Different tech stacks need different rules. Tauri projects need Rust + TypeScript rules (34 files), while Next.js-AWS needs React + Node.js + AWS rules (43 files). Manual copying is error-prone and wastes time. This skill generates exactly the rules your project needs.

**When to use:**
- Project initialization (after framework install)
- Framework sync (`/update-framework`)
- Manual rule updates when templates change
- Switching project profiles

**Integration:**
- Called by `/init-docs` during project setup
- Called by `/update-framework` when syncing
- Can be invoked manually for rule regeneration

## Arguments

```bash
/manage-rules [options]
```

**Common usage:**
```bash
/manage-rules                    # Auto-detect profile, generate instantly
/manage-rules --plan             # Dry-run (show what would be generated)
/manage-rules --profile=tauri    # Override profile detection
/manage-rules --instant          # Force immediate generation (default)
/manage-rules --update-from-guides  # Regenerate from latest templates
```

**Options:**
- `--plan` - Dry-run mode (show what would be generated without creating files)
- `--instant` - Generate immediately (default mode)
- `--update-from-guides` - Regenerate all rules from current templates
- `--profile=<name>` - Override auto-detected profile (tauri, nextjs-aws, minimal)

## Workflow

Copy this checklist to track progress:

```
Task Progress:
- [ ] Step 1: Detect profile
- [ ] Step 2: Load profile config
- [ ] Step 3: Scan templates
- [ ] Step 4: Filter by profile
- [ ] Step 5: Generate .claude/rules/ files
- [ ] Step 6: Report results
```

Execute these steps in sequence:

### Step 1: Detect Profile

**Auto-detection** (priority order):
1. Check `--profile` argument (manual override)
2. Read `.framework-install` file (format: `profile: tauri`)
3. Fallback to "tauri" (default)

**Validation**: Verify `framework/profiles/{profile}.json` exists

**Error handling**: If profile not found, show error and list available profiles

### Step 2: Load Profile Configuration

**Load config**:
```bash
# Read profile configuration
config=$(cat framework/profiles/tauri.json)

# Extract rules.include array
include_rules=$(jq -r '.rules.include[]' framework/profiles/tauri.json)
```

**Expected structure**:
```json
{
  "name": "tauri",
  "rules": {
    "include": [
      "workflow",
      "conventions",
      "error-handling",
      ...
    ],
    "exclude": []
  }
}
```

**Validation**: Ensure `rules.include` array exists and is not empty

### Step 3: Scan Templates

**Find all templates**:
```bash
# Scan docs/ai-guides/rules/templates/ for *.md.template files
templates=$(find docs/ai-guides/rules/templates/ -name "*.md.template")
```

**Extract metadata**:
- Category: Parent directory name (e.g., `core`, `architecture`)
- Rule name: Filename without `.md.template` extension

**Example mapping**:
- `docs/ai-guides/rules/templates/core/workflow.md.template` → Category: `core`, Name: `workflow`

### Step 4: Filter by Profile

**Apply whitelist**:
```python
# For each rule in profile's include list
for rule_name in include_rules:
    # Find matching template
    if template_exists(rule_name):
        add_to_filtered(rule_name, template_path, category)
    else:
        warn(f"Template not found: {rule_name}")
```

**Apply exclude patterns** (if any):
```python
# Remove rules matching exclude patterns
for pattern in config['rules'].get('exclude', []):
    filtered = [r for r in filtered if not fnmatch(r, pattern)]
```

**Validation**: Verify filtered count matches expected (34/43/13)

### Step 5: Generate .claude/rules/ Files

**Create output structure**:
```bash
# Create .claude/rules/ directory
mkdir -p .claude/rules

# For each filtered template
for template in filtered_templates:
    category=$(get_category(template))
    rule_name=$(get_rule_name(template))

    # Create category subdirectory
    mkdir -p .claude/rules/$category

    # Copy template to output
    cp $template .claude/rules/$category/$rule_name.md
done
```

**File naming**: Template `workflow.md.template` → Output `workflow.md`

**Directory structure**:
```
.claude/rules/
├── core/
│   ├── workflow.md
│   ├── conventions.md
│   └── error-handling.md
├── architecture/
│   ├── clean-architecture.md
│   └── dependency-rules.md
├── languages/
│   ├── typescript.md
│   └── rust.md
...
```

### Step 6: Report Results

**Success output**:
```
✅ Generated 34 rules for profile 'tauri'

Output: .claude/rules/
Categories: 7 (core, architecture, languages, frontend, backend, infrastructure, development)

Files:
  core/: 5 rules
  architecture/: 4 rules
  languages/: 8 rules
  frontend/: 6 rules
  backend/: 3 rules
  infrastructure/: 5 rules
  development/: 3 rules
```

**Dry-run output** (--plan mode):
```
📋 Plan: Would generate 34 rules for profile 'tauri'

Templates to copy:
  ✓ core/workflow.md
  ✓ core/conventions.md
  ✓ architecture/clean-architecture.md
  ...

(Use /manage-rules --instant to execute)
```

## Usage Modes

### Mode 1: Auto-detect + Instant (Default)

```bash
/manage-rules
```

**Behavior**:
- Auto-detects profile from `.framework-install`
- Immediately generates `.claude/rules/`
- Shows completion summary

**Use when**: Normal rule generation

### Mode 2: Dry-run (--plan)

```bash
/manage-rules --plan
```

**Behavior**:
- Shows what would be generated
- No files created
- Displays template list

**Use when**: Verifying before generation

### Mode 3: Profile Override

```bash
/manage-rules --profile=nextjs-aws
```

**Behavior**:
- Ignores `.framework-install`
- Uses specified profile
- Generates rules for that stack

**Use when**: Testing different profiles, switching stacks

### Mode 4: Update from Guides

```bash
/manage-rules --update-from-guides
```

**Behavior**:
- Deletes existing `.claude/rules/`
- Regenerates from current templates
- Updates to latest template versions

**Use when**: Templates have been updated

## Profile Detection

### Auto-Detection Method

```python
# Step 1: Check for .framework-install file
if os.path.exists(".framework-install"):
    with open(".framework-install", "r") as f:
        content = f.read()
    # Expected format: "profile: tauri"
    profile = content.split(":")[1].strip()
else:
    profile = None

# Step 2: Override with --profile argument
if args.profile:
    profile = args.profile

# Step 3: Fallback to default
if not profile:
    profile = "tauri"
    print("⚠️ No profile detected, defaulting to 'tauri'")

# Step 4: Validate profile exists
profile_config = f"framework/profiles/{profile}.json"
if not os.path.exists(profile_config):
    print(f"❌ Profile '{profile}' not found")
    print(f"Available profiles: tauri, nextjs-aws, minimal")
    sys.exit(1)
```

### Manual Override

```bash
# Specify profile explicitly
/manage-rules --profile=minimal

# Useful for:
# - Testing different profiles
# - Overriding incorrect auto-detection
# - Switching tech stacks
```

### Validation

**Profile config must exist**:
```bash
# Check for profile configuration
ls framework/profiles/tauri.json

# Expected profiles:
# - tauri.json (34 rules)
# - nextjs-aws.json (43 rules)
# - minimal.json (13 rules)
```

## Template Filtering

### Whitelist Filtering

**Load include list**:
```python
# Read profile configuration
config = read_json(f"framework/profiles/{profile}.json")
include_rules = config['rules']['include']  # e.g., 34 for tauri

# Expected structure:
# {
#   "rules": {
#     "include": ["workflow", "typescript", "rust", ...]
#   }
# }
```

**Filter templates**:
```python
# Scan all templates
template_dir = "docs/ai-guides/rules/templates/"
all_templates = glob(f"{template_dir}/**/*.md.template", recursive=True)

# Extract rule names from paths
template_map = {}
for tmpl in all_templates:
    parts = tmpl.split('/')
    category = parts[-2]  # e.g., "core"
    rule_name = parts[-1].replace('.md.template', '')  # e.g., "workflow"
    template_map[rule_name] = {
        'path': tmpl,
        'category': category
    }

# Filter by whitelist
filtered = {}
for rule_name in include_rules:
    if rule_name in template_map:
        filtered[rule_name] = template_map[rule_name]
    else:
        print(f"⚠️ Template not found: {rule_name}")
```

### Exclude Patterns

**Apply exclusions** (if configured):
```python
# Get exclude patterns (optional)
exclude_patterns = config['rules'].get('exclude', [])

# Remove matching rules
for pattern in exclude_patterns:
    filtered = {k: v for k, v in filtered.items() if not fnmatch(k, pattern)}

# Example: Exclude all testing rules
# "exclude": ["*-test", "*-testing"]
```

### Missing Templates

**Warning behavior**:
```
⚠️ Template not found: advanced-caching
⚠️ Template not found: custom-logging

Continuing with 32/34 templates found.
```

**Does not block generation** - missing templates are skipped

### Custom Rules

**Custom marker** (in template YAML):
```yaml
---
custom: true
---
```

**Behavior**: Skip templates marked `custom: true` (project-specific rules, not for generation)

**Override marker** (in template YAML):
```yaml
---
override: true
---
```

**Behavior**: Preserve templates marked `override: true` (allow customization)

## File Generation Logic

### Output Directory Structure

```python
# Create output directory
output_dir = ".claude/rules"
os.makedirs(output_dir, exist_ok=True)

# Generate files from filtered templates
generated_count = 0
for rule_name, info in filtered_templates.items():
    template_path = info['path']
    category = info['category']

    # Create category subdirectory
    category_dir = f"{output_dir}/{category}"
    os.makedirs(category_dir, exist_ok=True)

    # Read template content
    content = read_file(template_path)

    # Write to .claude/rules/{category}/{rule_name}.md
    output_file = f"{category_dir}/{rule_name}.md"
    write_file(output_file, content)

    generated_count += 1

# Report results
print(f"✅ Generated {generated_count} rules for profile '{profile}'")
print(f"Output: .claude/rules/ ({len(os.listdir(output_dir))} categories)")
```

### File Naming Convention

**Template**: `workflow.md.template`
**Output**: `workflow.md`

**Rationale**: `.template` extension removed, content copied as-is

### Category Preservation

**Template location**: `docs/ai-guides/rules/templates/core/workflow.md.template`
**Output location**: `.claude/rules/core/workflow.md`

**Category hierarchy maintained** in output structure

## AI Execution Instructions

**CRITICAL: Task creation and profile handling**

When executing `/manage-rules`, AI MUST follow this pattern:

### Step 1: Create 6 Workflow Tasks

```python
tasks = [
    TaskCreate(subject="Detect profile", description="Auto-detect from .framework-install or use --profile arg", activeForm="Detecting profile..."),
    TaskCreate(subject="Load profile config", description="Read framework/profiles/{profile}.json", activeForm="Loading profile config..."),
    TaskCreate(subject="Scan templates", description="Find all *.md.template files", activeForm="Scanning templates..."),
    TaskCreate(subject="Filter by profile", description="Apply rules.include whitelist", activeForm="Filtering templates..."),
    TaskCreate(subject="Generate .claude/rules/ files", description="Copy templates to output directory", activeForm="Generating rule files..."),
    TaskCreate(subject="Report results", description="Show counts and file locations", activeForm="Reporting results...")
]

# Add dependencies
for i in range(1, 6):
    TaskUpdate(tasks[i].id, addBlockedBy=[tasks[i-1].id])
```

### Step 2: Execute Workflow

```python
for task in tasks:
    # Mark in progress
    TaskUpdate(task.id, status="in_progress")

    # Execute step (see Workflow section for details)
    execute_step(task)

    # Mark completed
    TaskUpdate(task.id, status="completed")
```

### Step 3: Validation

**After generation**:
```bash
# Verify output count matches profile
expected_count=$(jq '.rules.include | length' framework/profiles/tauri.json)
actual_count=$(find .claude/rules -name "*.md" | wc -l)

if [ "$expected_count" != "$actual_count" ]; then
    echo "⚠️ Count mismatch: expected $expected_count, got $actual_count"
fi
```

## Error Handling

### Profile Not Found

```
❌ Profile 'unknown' not found

Available profiles:
  - tauri (34 rules)
  - nextjs-aws (43 rules)
  - minimal (13 rules)

Fix: Use /manage-rules --profile=<name>
```

**Recovery**: List available profiles, suggest valid options

### Template Not Found

```
⚠️ Template not found: advanced-caching
⚠️ Template not found: custom-logging

Continuing with 32/34 templates found.
```

**Recovery**: Skip missing templates, continue with available ones

### Permission Errors

```
❌ Permission denied: .claude/rules/

Fix: Check directory permissions or run with appropriate access
```

**Recovery**: Show clear error, suggest permission check

### Invalid Config

```
❌ Invalid profile config: framework/profiles/tauri.json
Missing required field: rules.include

Fix: Ensure profile config has correct structure
```

**Recovery**: Validate config structure, show required format

## Integration Points

**Called by /init-docs**:
```bash
# During project initialization
/init-docs
  → /manage-rules --instant  # Generate rules for detected profile
```

**Called by /update-framework**:
```bash
# During framework sync
/update-framework ~/dev/ai-dev
  → /manage-rules --update-from-guides  # Regenerate with latest templates
```

**Manual invocation**:
```bash
# User can call directly
/manage-rules --plan           # Preview
/manage-rules --instant        # Execute
/manage-rules --profile=tauri  # Override
```

## Best Practices

1. **Run after profile change** - Regenerate rules when switching tech stacks
2. **Use --plan first** - Preview before generation for verification
3. **Update from guides regularly** - Keep rules in sync with latest templates
4. **Don't edit generated files** - Customizations belong in templates or overrides
5. **Commit generated rules** - Track rule files in version control

## Related Skills

- **/init-docs** - Calls this skill during project initialization
- **/update-framework** - Calls this skill when syncing framework
- **/update-rules** - Alternative bidirectional sync (use manage-rules for generation)

---

**Version:** 1.0.0
**Pattern:** Tool-Reference (guides AI through generation workflow)
**Compliance:** ADR-001 ✅ | ADR-013 ✅
**Last Updated:** 2026-03-27
**Changelog:**
- v1.0.0: Initial release with profile-aware generation (Issue #351)
