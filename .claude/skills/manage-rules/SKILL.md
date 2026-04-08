---
name: manage-rules
version: "3.0.0"
description: Generate profile-aware rules from templates using Python script (ADR-014 compliant)
allowed-tools: Bash, Read
user-invocable: true
compliance: ADR-014
---

# Manage Rules - Profile-Aware Rule Generation v3.0

**Compliance**: ADR-014 ✅ (Script-based pattern)

Generate project-specific technical rules from templates based on project profile.

## What's New in v3.0

- ✅ **ADR-014 compliant**: Logic extracted to `scripts/generate_rules.py`
- ✅ **Testable**: Unit tests with >60% coverage
- ✅ **Maintainable**: Clear separation between AI orchestration and business logic
- ✅ **Framework-only filtering**: Preserves Issue #401 functionality
- ✅ **Shared utilities**: Extracted to `_scripts/utils/` for reuse

## Overview

This skill automates rule file generation by:

**What it does:**
1. **Loads project profile** - Reads `docs/project-profile.md` for rules configuration
2. **Validates profile** - Checks YAML syntax and required fields
3. **Scans rule templates** - Finds all templates in `.claude/guides/rules/templates/` or `docs/ai-guides/rules/templates/`
4. **Filters by profile** - Applies `rules.include` whitelist from profile
5. **Filters framework-only** - Excludes templates with `framework-only: true` (Issue #401)
6. **Generates rule files** - Copies filtered templates to `.claude/rules/`
7. **Reports results** - Shows generated count and file locations

**Why it's needed:**
Different tech stacks need different rules. Tauri projects need Rust + TypeScript rules (34 files), while Next.js-AWS needs React + Node.js + AWS rules (43 files). Manual copying is error-prone and wastes time. This skill generates exactly the rules your project needs.

**When to use:**
- Project initialization (after profile setup)
- Framework sync (`/update-framework`)
- Manual rule updates when templates change
- After changing project profile

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
/manage-rules --profile tauri    # Override profile detection
/manage-rules --confirm          # Force immediate generation (default)
```

**Options:**
- `--dry-run` - Preview mode (show what would be generated without creating files)
- `--confirm` - Auto-confirm (skip confirmation prompt, generate immediately)
- `--profile <name>` - Override auto-detected profile (tauri, nextjs-aws, minimal)

## AI Execution Instructions

**CRITICAL: This is a script-based skill (ADR-014)**

AI MUST follow this pattern:

### Step 1: Validate Prerequisites

```bash
# Check Python script exists
if [ ! -f ".claude/skills/manage-rules/scripts/generate_rules.py" ]; then
  echo "❌ Error: generate_rules.py not found"
  exit 1
fi

# Check dependencies installed
uv run -c "import yaml" 2>/dev/null || {
  echo "⚠️ Warning: PyYAML not installed"
  echo "Install: pip install PyYAML"
}
```

### Step 2: Parse Arguments

```python
# Extract options from user arguments
plan_mode = "--plan" in args
instant_mode = "--instant" in args or not plan_mode  # Default: instant
profile_override = extract_arg("--profile", args)  # Optional
```

### Step 3: Execute Python Script

```bash
# Basic execution (auto-detect profile, with confirmation prompt)
uv run .claude/skills/manage-rules/scripts/generate_rules.py

# Auto-confirm (skip confirmation prompt)
uv run .claude/skills/manage-rules/scripts/generate_rules.py --confirm

# Dry-run (show plan)
uv run .claude/skills/manage-rules/scripts/generate_rules.py --dry-run

# Override profile
uv run .claude/skills/manage-rules/scripts/generate_rules.py --profile tauri --confirm
```

### Step 4: Report Results

**Script output format**:
```
🔍 Detecting profile...
✅ Profile: tauri

📖 Loading profile configuration...
✅ Config loaded: 34 include rules, 2 exclude patterns

🔍 Filtering templates...
✅ Filtered: 36 templates matched

🔍 Filtering framework-only templates...
✅ Filtered: 34 templates (excluded 2 framework-only)

📝 Generating rules...
✅ Generated 34 rules for profile 'tauri'
```

**AI should**:
- Display script output directly
- No need to re-explain the workflow (script handles it)
- Report any errors from script stderr

## Script Architecture

**File**: `scripts/generate_rules.py`

**Class**: `RuleGenerator`

**Methods**:
- `detect_profile()` → str: Detect profile from `docs/project-profile.md`
- `load_profile_config(profile)` → dict: Load rules config from `.claude/profiles/{profile}.json`
- `filter_templates(config)` → List[Path]: Filter by whitelist + exclude patterns
- `filter_framework_only_skills(templates)` → List[Path]: Exclude framework-only templates (Issue #401)
- `generate_rules(templates, dry_run)` → int: Generate rule files or show plan

**Main entry point**:
```python
def main():
    parser = argparse.ArgumentParser(...)
    args = parser.parse_args()

    generator = RuleGenerator(profile=args.profile, instant=args.instant)

    # Step 1: Detect profile
    profile = generator.detect_profile()

    # Step 2: Load config
    config = generator.load_profile_config(profile)

    # Step 3-4: Filter templates
    templates = generator.filter_templates(config)
    filtered = generator.filter_framework_only_skills(templates)

    # Step 5: Generate or show plan
    count = generator.generate_rules(filtered, dry_run=args.dry_run)
```

**See**: [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design

## Safety Features

This skill includes multiple safety mechanisms to prevent errors during rule generation:

### 1. Profile Validation

**Purpose**: Ensure valid profile configuration before processing

**How it works:**
```python
def validate_profile(profile_path: Path) -> dict:
    """Validate profile file exists and has valid YAML"""
    if not profile_path.exists():
        raise ProfileError("Profile file not found")

    with open(profile_path) as f:
        content = f.read()

    # Parse YAML frontmatter
    if not content.startswith('---'):
        raise ProfileError("Missing YAML frontmatter")

    metadata = yaml.safe_load(frontmatter)

    # Validate required fields
    if 'rules' not in metadata:
        raise ProfileError("Missing 'rules' configuration")

    return metadata
```

**Prevents:** Missing profiles, malformed YAML, incomplete configuration

### 2. Template Validation

**Purpose**: Ensure templates are valid and parseable before copying

**How it works:**
```python
def validate_template(template_path: Path) -> bool:
    """Check template has valid structure"""
    if not template_path.exists():
        return False

    if not template_path.suffix == '.md':
        return False

    # Check file is readable
    try:
        with open(template_path) as f:
            content = f.read()
        return True
    except Exception:
        return False
```

**Prevents:** Corrupt files, non-markdown files, permission errors

### 3. Framework-Only Filtering

**Purpose**: Prevent framework management skills from being copied to projects

**How it works:**
```python
def has_framework_only_marker(template_path: Path) -> bool:
    """Check if template has framework-only: true marker"""
    with open(template_path) as f:
        content = f.read()

    if content.startswith('---'):
        yaml_end = content.find('---', 3)
        frontmatter = content[3:yaml_end]
        metadata = yaml.safe_load(frontmatter)
        return metadata.get('framework-only', False)

    return False

# Filter out framework-only templates
filtered = [t for t in templates if not has_framework_only_marker(t)]
```

**Prevents:** Copying framework management skills to target projects (Issue #401)

### 4. Dry-Run Mode

**Purpose**: Preview changes before applying them

**How it works:**
```bash
# Dry-run shows what would be generated
/manage-rules --dry-run

# Output shows file operations without executing
📋 Dry Run - Would generate 34 rules:
  - template A → destination A
  - template B → destination B
```

**Enables:** Safe preview, verification before execution, no side effects

### 5. Error Recovery

**Purpose**: Graceful handling of partial failures

**How it works:**
```python
def generate_rules(templates: List[Path], dry_run: bool) -> int:
    """Generate rules with error handling"""
    count = 0
    errors = []

    for template in templates:
        try:
            copy_template(template, destination)
            count += 1
        except Exception as e:
            errors.append((template, str(e)))
            continue  # Continue with remaining files

    if errors:
        print(f"⚠️ {len(errors)} files failed:")
        for template, error in errors:
            print(f"  - {template}: {error}")

    return count
```

**Prevents:** Complete failure on single file error, provides partial success, logs failures

### Safety Best Practices

When generating rules:

1. **Always use dry-run first** - Preview changes before applying
2. **Verify profile configuration** - Check `docs/project-profile.md` is correct
3. **Check template directory** - Ensure `.claude/guides/rules/templates/` exists
4. **Review generated files** - Verify rules match your tech stack
5. **Don't edit .claude/rules/ directly** - Regenerate from templates instead

## Testing

**File**: `tests/test_rule_generator.py`

**Coverage**: >60% (focus on core logic)

**Test cases**:
- Profile detection (normal, missing file, invalid YAML)
- Template filtering (whitelist, exclude, combined)
- Framework-only filtering (detect marker, no marker, invalid YAML)
- Rule generation (normal, subdirs, dry-run)

**Run tests**:
```bash
cd .claude/skills/manage-rules
uv run -m unittest tests.test_rule_generator -v
```

**Requirements**:
```bash
pip install PyYAML>=6.0
```

## Usage Examples

### Example 1: Basic Generation (Instant Mode)

**User:** "generate rules for this project"

**Execute:**
```bash
uv run .claude/skills/manage-rules/scripts/generate_rules.py --confirm
```

**Output:**
```
🔍 Detecting profile...
✅ Profile: tauri

📖 Loading profile configuration...
✅ Config loaded: 34 include rules, 2 exclude patterns

🔍 Filtering templates...
✅ Filtered: 36 templates matched

🔍 Filtering framework-only templates...
✅ Filtered: 34 templates (excluded 2 framework-only)

📝 Generating rules...
✅ Generated 34 rules for profile 'tauri'
```

**Time:** ~2 seconds

### Example 2: Dry-Run Mode (Preview Changes)

**User:** "show me what rules would be generated"

**Execute:**
```bash
uv run .claude/skills/manage-rules/scripts/generate_rules.py --dry-run
```

**Output:**
```
🔍 Detecting profile...
✅ Profile: tauri

📖 Loading profile configuration...
✅ Config loaded: 34 include rules, 2 exclude patterns

🔍 Filtering templates...
✅ Filtered: 36 templates matched

🔍 Filtering framework-only templates...
✅ Filtered: 34 templates (excluded 2 framework-only)

📋 Dry Run - Would generate 34 rules:
  - .claude/guides/rules/templates/core/naming.md → .claude/rules/core/naming.md
  - .claude/guides/rules/templates/core/types.md → .claude/rules/core/types.md
  - .claude/guides/rules/templates/architecture/clean.md → .claude/rules/architecture/clean.md
  ...
```

**Time:** ~1 second

### Example 3: Profile-Aware Generation (Override Profile)

**User:** "generate rules for nextjs-aws profile"

**Execute:**
```bash
uv run .claude/skills/manage-rules/scripts/generate_rules.py --profile nextjs-aws --confirm
```

**Output:**
```
🔍 Detecting profile...
✅ Profile: nextjs-aws (overridden)

📖 Loading profile configuration...
✅ Config loaded: 43 include rules, 3 exclude patterns

🔍 Filtering templates...
✅ Filtered: 45 templates matched

🔍 Filtering framework-only templates...
✅ Filtered: 43 templates (excluded 2 framework-only)

📝 Generating rules...
✅ Generated 43 rules for profile 'nextjs-aws'
```

**Time:** ~2 seconds

## Error Handling

**Profile not found:**
```
❌ Profile Error: Profile file not found: docs/project-profile.md

Fix: Run /manage-claude-md --configure-profile --select-profile
```

**Invalid YAML:**
```
❌ Profile Error: Invalid YAML syntax: ...

Fix: Check docs/project-profile.md YAML frontmatter
```

**Missing templates:**
```
❌ Profile Error: Template directory not found

Fix: Ensure .claude/guides/rules/templates/ exists
```

**PyYAML not installed:**
```
⚠️ Warning: PyYAML not installed
Install: pip install PyYAML

❌ Error: No module named 'yaml'

Fix: pip install -r .claude/skills/manage-rules/requirements.txt
```

## Troubleshooting

### Issue: Script not found

**Symptom:** `generate_rules.py not found`

**Cause:** Skill not fully installed

**Fix:**
```bash
# Check script exists
ls .claude/skills/manage-rules/scripts/generate_rules.py

# If missing, sync from framework
/update-skills ~/path/to/ai-dev
```

### Issue: PyYAML import error

**Symptom:** `ModuleNotFoundError: No module named 'yaml'`

**Cause:** Dependencies not installed

**Fix:**
```bash
# Install dependencies
pip install PyYAML

# OR install from requirements
cd .claude/skills/manage-rules
pip install -r requirements.txt
```

### Issue: Wrong profile detected

**Symptom:** Generated wrong set of rules

**Cause:** Profile auto-detection incorrect

**Fix:**
```bash
# Override profile explicitly
/manage-rules --profile tauri --confirm

# Or fix profile in docs/project-profile.md
```

### Issue: Framework-only templates included

**Symptom:** update-framework.md or other framework management skills copied to project

**Cause:** Templates missing `framework-only: true` in YAML frontmatter

**Fix:**
```bash
# Add to template YAML frontmatter:
---
framework-only: true
---

# Then regenerate
/manage-rules --confirm
```

### Issue: No templates filtered

**Symptom:** "Filtered: 0 templates matched"

**Cause:** Profile whitelist doesn't match any templates

**Fix:**
```bash
# Check profile config
cat .claude/profiles/{profile}.json

# Verify templates exist
ls .claude/guides/rules/templates/

# Fix whitelist in profile config
# Example: "rules": { "include": ["core/*", "architecture/*"] }
```

## Framework-Only Filtering (Issue #401)

**Context:** Framework management skills (update-framework, update-skills, etc.) should not be copied to target projects during sync.

**Solution:** YAML metadata marking

**Implementation:**
```python
def has_framework_only_marker(template_path: Path) -> bool:
    """Check if template has framework-only: true in YAML frontmatter"""
    with open(template_path, 'r') as f:
        content = f.read()

    if content.startswith('---'):
        yaml_end = content.find('---', 3)
        frontmatter = content[3:yaml_end]

        import yaml
        metadata = yaml.safe_load(frontmatter)
        return metadata.get('framework-only', False)

    return False
```

**Usage:** Called automatically during `filter_framework_only_skills()` workflow step

**Example template with marker:**
```markdown
---
framework-only: true
---

# Update Framework Skill

This skill is only for framework maintenance.
```

## Best Practices

1. **Use instant mode by default** - Fast and convenient
2. **Use dry-run for review** - Check before generating
3. **Don't edit .claude/rules/ directly** - Regenerate from templates
4. **Keep templates in sync** - Use `/update-framework` regularly
5. **Profile-specific rules** - Use whitelist to customize per project

## Performance

- **Average time:** 2 seconds for 34 rules
- **Dry-run:** 1 second (no file I/O)
- **Template scanning:** O(n) where n = template count
- **Filtering:** O(n × m) where m = whitelist size

Fast because:
- Efficient file operations
- Minimal YAML parsing (frontmatter only)
- Batch file copying

## Testing

This skill has comprehensive test coverage following ADR-020 standards.

**Test Suite:**
- **test_arguments.py** (6 test classes) - 参数验证测试
- **test_functional.py** (7 test classes) - 功能测试（What it does章节）
- **test_safety.py** (7 test classes) - 安全特性测试
- **test_error_handling.py** (8 test classes) - 错误处理测试
- **test_integration.py** (5 test classes) - 集成测试（Usage Examples章节）
- **test_rule_generator.py** (4 test classes) - 核心逻辑单元测试

**Coverage:** >60% overall, >80% core logic (符合 ADR-020标准)

**Run tests:**
```bash
# All tests
pytest .claude/skills/manage-rules/tests/

# With coverage
pytest .claude/skills/manage-rules/tests/ --cov --cov-report=html

# Specific test file
pytest .claude/skills/manage-rules/tests/test_functional.py
```

**See:** [tests/README.md](tests/README.md) for complete testing guide (if available)

## Related Skills

- **/manage-claude-md --configure-profile** - Select and activate project profile
- **/update-framework** - Sync framework content (calls this skill)
- **/init-docs** - Initialize documentation (calls this skill)
- **/manage-docs** - Document structure management
- **/manage-adrs** - Architecture decision records

## Migration from v2.0

**Breaking changes:**
- Script execution required (not pure markdown)
- PyYAML dependency required

**Migration steps:**
1. Install dependencies: `pip install PyYAML`
2. Test script: `uv run .claude/skills/manage-rules/scripts/generate_rules.py --dry-run`
3. Regenerate rules: `/manage-rules --confirm`

**Behavioral compatibility:** v3.0 maintains identical behavior to v2.0 (same filtering logic, output structure, profile detection)

---

**Version:** 3.0.0
**Pattern:** Script-based (ADR-014)
**Compliance:** ADR-014 ✅
**Last Updated:** 2026-03-30
**Changelog:**
- v3.0.0: Refactored to script-based pattern (ADR-014), added unit tests (>60% coverage), preserved framework-only filtering (Issue #401)
- v2.0.0: Profile source changed to docs/project-profile.md
- v1.0.0: Initial release with .claude/profiles/*.json
