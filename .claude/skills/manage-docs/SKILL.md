---
name: manage-docs
version: "1.1.0"
description: |
  Manage project documentation structure and content with profile awareness.
  TRIGGER when: user wants to check documentation structure, validate docs, or generate missing documentation.
  DO NOT TRIGGER when: user wants to manage CLAUDE.md (use /manage-claude-md), ADRs (use /manage-adrs), or just read documentation.
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
user-invocable: true
---

# manage-docs - Documentation Management (Profile-Aware)

**New skill** (extracted from deprecated `/maintain-project`)

## Purpose

Profile-aware documentation structure management and validation.

**Why This Skill Exists**:
- ✅ Validates documentation structure matches profile requirements
- ✅ Detects missing documentation for tech stack
- ✅ Generates documentation from templates
- ✅ Checks for broken links and outdated content
- ✅ Ensures consistency across project documentation

---

## Arguments

```bash
/manage-docs [options]
```

**Common usage:**
```bash
/manage-docs                    # Run all checks (check + validate)
/manage-docs --check            # Check documentation structure
/manage-docs --validate         # Validate content (links, code examples)
/manage-docs --generate         # Generate missing documentation
/manage-docs --instant          # All-in-one (check + validate + generate)
```

**Options:**
- `--check` - Check documentation structure against profile requirements
- `--validate` - Validate documentation content (links, code examples, format)
- `--generate` - Generate missing documentation from templates
- `--instant` - Run all operations in sequence (check + validate + generate)
- `--profile=<name>` - Override profile from project-profile.md
- `--dry-run` - Preview actions without executing
- `--force` - Skip safety checks and prompts

**Advanced options:**
- `--template-dir=<path>` - Use custom template directory
- `--output-dir=<path>` - Generate docs to specific directory
- `--fix-links` - Auto-fix broken internal links
- `--update-index` - Regenerate documentation index

## Usage

```bash
/manage-docs                          # Run all checks (check + validate)
/manage-docs --check                  # Check documentation structure
/manage-docs --validate               # Validate content (links, code examples)
/manage-docs --generate               # Generate missing documentation
/manage-docs --instant                # All-in-one (check + validate + generate)
```

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
pillars: [A, B, K, L]
---
```

**Uses profile for**:
1. **Required docs detection**: Different stacks need different docs
2. **Template selection**: Generate stack-specific documentation
3. **Validation rules**: Check stack-specific conventions

**Tech stack → Required documentation**:

| Tech Stack | Required Documentation |
|------------|------------------------|
| **Tauri** | `docs/architecture/tauri-ipc.md`, `docs/development/desktop-builds.md`, `docs/development/rust-backend.md` |
| **Next.js + AWS** | `docs/architecture/nextjs-routing.md`, `docs/infrastructure/aws-deployment.md`, `docs/api/lambda-functions.md` |
| **React** | `docs/architecture/component-structure.md`, `docs/development/react-patterns.md` |
| **Rust** | `docs/development/rust-guidelines.md`, `docs/testing/rust-tests.md` |

---

## Safety Features

This skill includes multiple safety mechanisms to ensure reliable documentation management:

### 1. Document Structure Validation

**Purpose**: Prevent corrupted or incomplete documentation structures

**How it works:**
- Validates required directory structure exists (`docs/`, `docs/architecture/`, etc.)
- Checks for required files based on profile (README.md, API.md, etc.)
- Ensures documentation follows project conventions

**Prevents:**
- Generating docs in wrong locations
- Overwriting existing important files
- Creating orphaned documentation

### 2. Profile Configuration Checks

**Purpose**: Ensure profile-aware operations use valid configuration

**How it works:**
```python
# Validate profile file exists and is parseable
if not profile_exists():
    warn("Project profile not found, using defaults")
    return default_config

# Validate YAML syntax
try:
    profile = yaml.safe_load(profile_content)
except YAMLError:
    error("Invalid YAML in project-profile.md")
    return None

# Validate required fields
required = ["name", "techStack", "pillars"]
missing = [f for f in required if f not in profile]
if missing:
    error(f"Profile missing fields: {missing}")
```

**Prevents:**
- Operating with invalid/corrupted profiles
- Missing required profile fields causing failures
- Type errors from malformed YAML

### 3. File Conflict Detection

**Purpose**: Avoid overwriting user-modified documentation

**How it works:**
```python
# Before generating docs, check for conflicts
for doc in docs_to_generate:
    if file_exists(doc.path):
        if file_modified_by_user(doc.path):
            conflicts.append(doc.path)

if conflicts:
    prompt_user(f"These files exist: {conflicts}")
    options = ["Skip", "Backup and overwrite", "Merge", "Cancel"]
    action = ask_user(options)
```

**Prevents:**
- Losing user customizations
- Overwriting manual edits
- Data loss from automated generation

### 4. Backup Mechanism

**Purpose**: Provide rollback capability for generated documentation

**How it works:**
```python
# Before any modifications, create backups
backup_dir = f".claude/backups/docs-{timestamp}/"
for file in files_to_modify:
    backup(file, backup_dir)

# On failure, auto-restore
try:
    generate_documentation()
except Exception as e:
    restore_from_backup(backup_dir)
    raise
```

**Enables:**
- Rollback on generation failures
- Manual recovery if needed
- Audit trail of changes

### 5. Permission Validation

**Purpose**: Ensure filesystem permissions allow documentation operations

**How it works:**
```python
# Check write permissions before operations
def validate_permissions():
    directories = ["docs/", ".claude/", ".claude/backups/"]

    for dir in directories:
        if not can_write(dir):
            error(f"No write permission for {dir}")
            suggest_fix(f"chmod 755 {dir}")
            return False

    return True
```

**Prevents:**
- Silent failures from permission denied
- Partial writes leaving inconsistent state
- Unclear error messages

### Safety Best Practices

When managing documentation:

1. **Run --check before --generate** - Preview what will be created
2. **Use --dry-run first** - Validate operations without executing
3. **Keep backups** - Auto-backups in `.claude/backups/docs-*/`
4. **Review generated docs** - Always check before committing
5. **Validate profile first** - Ensure configuration is correct

## Error Handling

All operations include graceful error handling:

### 1. Missing Project Profile

```bash
if [ ! -f "docs/project-profile.md" ]; then
  echo "⚠️  Warning: Project profile not configured"
  echo "Run: /manage-claude-md --configure-profile --select-profile"
  echo "Using default documentation checks..."
  # Continue with minimal validation
fi
```

### 2. Invalid YAML Syntax

```bash
# Validate YAML before reading
if ! uv run -c "import yaml; yaml.safe_load(open('docs/project-profile.md'))" 2>/dev/null; then
  echo "⚠️  Warning: Invalid YAML in project-profile.md"
  echo "Continuing with default checks..."
  # Skip profile-based validation
fi
```

### 3. Template Not Found

```bash
# Check if template exists before generating
if [ ! -f ".claude/guides/doc-templates/$template.md" ]; then
  echo "⚠️  Warning: Template not found: $template.md"
  echo "Skipping generation for this document"
  # Continue with other documents
fi
```

### 4. File I/O Errors

```bash
# Check write permissions
if [ ! -w "docs/" ]; then
  echo "❌ Error: No write permission for docs/ directory"
  echo "Check permissions: ls -la docs/"
  exit 1
fi
```

---

## Core Functions

### 1. Check Documentation Structure

**What it does**:
1. Loads profile to determine tech stack
2. Scans `docs/` directory for existing files
3. Compares with expected structure for tech stack
4. Reports missing, unexpected, or misplaced files

**Workflow**:
```bash
# 1. Load profile
if [ -f "docs/project-profile.md" ]; then
    profile_name=$(grep "name:" docs/project-profile.md | cut -d' ' -f2)
    tech_stack=$(sed -n '/techStack:/,/^[a-z]/p' docs/project-profile.md)
    echo "📋 Profile: $profile_name"
fi

# 2. Determine expected documentation
case "$profile_name" in
    tauri)
        expected_docs=(
            "docs/architecture/tauri-ipc.md"
            "docs/development/desktop-builds.md"
            "docs/development/rust-backend.md"
            "docs/testing/integration-tests.md"
        )
        ;;
    nextjs-aws)
        expected_docs=(
            "docs/architecture/nextjs-routing.md"
            "docs/infrastructure/aws-deployment.md"
            "docs/api/lambda-functions.md"
            "docs/testing/e2e-tests.md"
        )
        ;;
    *)
        # Default minimal docs
        expected_docs=(
            "docs/README.md"
            "docs/ARCHITECTURE.md"
            "docs/DEVELOPMENT.md"
        )
        ;;
esac

# 3. Scan existing documentation
existing_docs=$(find docs/ -name "*.md" -type f | sort)

# 4. Compare expected vs existing
missing_docs=()
for doc in "${expected_docs[@]}"; do
    if [ ! -f "$doc" ]; then
        missing_docs+=("$doc")
    fi
done

# 5. Check for unexpected files (optional)
# ...
```

**Example output**:
```
Documentation Structure Check
=============================
📋 Profile: tauri (React + Rust + Tauri)

Expected documentation (10 files):
  ✅ docs/README.md
  ✅ docs/ARCHITECTURE.md
  ✅ docs/DEVELOPMENT.md
  ✅ docs/architecture/tauri-ipc.md
  ✅ docs/development/desktop-builds.md
  ❌ docs/development/rust-backend.md (MISSING)
  ❌ docs/testing/integration-tests.md (MISSING)
  ⚠️  docs/random-notes.md (unexpected - consider removing)

Status: 2 missing, 1 unexpected
Completeness: 80% (8/10)
```

---

### 2. Validate Content

**What it does**:
1. Checks for broken internal links
2. Validates code examples (optional)
3. Detects outdated content
4. Verifies documentation structure

**Workflow**:
```bash
# 1. Check internal links
for doc in $(find docs/ -name "*.md"); do
    # Extract all markdown links: [text](path)
    links=$(grep -oP '\[.*?\]\(\K[^)]+' "$doc")

    for link in $links; do
        # Skip external links (http/https)
        if [[ "$link" =~ ^https?:// ]]; then
            continue
        fi

        # Resolve relative path
        doc_dir=$(dirname "$doc")
        target="$doc_dir/$link"

        # Check if target exists
        if [ ! -f "$target" ] && [ ! -d "$target" ]; then
            echo "❌ Broken link in $doc: $link"
        fi
    done
done

# 2. Check for TODO/FIXME markers
todos=$(grep -rn "TODO\|FIXME" docs/ | grep -v ".git")
if [ -n "$todos" ]; then
    echo "⚠️  Found TODO markers in documentation:"
    echo "$todos"
fi

# 3. Check for outdated timestamps (optional)
# Look for "Last Updated" fields and compare with file modification time
```

**Example output**:
```
Documentation Validation
========================

Internal Links:
  ✅ 42 links checked
  ❌ 2 broken links found:
     - docs/architecture/overview.md → ../api/endpoints.md (missing)
     - docs/README.md → ./setup/install.md (missing)

Content Markers:
  ⚠️  3 TODO items found:
     - docs/DEVELOPMENT.md:45: TODO: Add Rust build instructions
     - docs/testing/README.md:12: FIXME: Update test command
     - docs/api/rest-api.md:89: TODO: Document authentication

Outdated Content:
  ⚠️  2 files not updated in >60 days:
     - docs/ARCHITECTURE.md (last updated: 2025-12-15)
     - docs/api/rest-api.md (last updated: 2025-11-20)
```

---

### 3. Generate Missing Documentation

**What it does**:
1. Detects missing documentation from check
2. Selects appropriate templates based on tech stack
3. Generates documentation from templates
4. Fills in profile-specific content

**Workflow**:
```bash
# 1. Get list of missing docs from check
missing_docs=( ... )  # From check function

# 2. For each missing doc, find template
for doc in "${missing_docs[@]}"; do
    # Extract doc type from path
    # docs/architecture/tauri-ipc.md → type: tauri-ipc

    doc_name=$(basename "$doc" .md)
    doc_category=$(basename $(dirname "$doc"))

    # Look for template in ai-guides
    template=".claude/guides/doc-templates/${doc_category}/${doc_name}.md"

    if [ -f "$template" ]; then
        echo "📝 Generating $doc from template"

        # Copy template
        mkdir -p $(dirname "$doc")
        cp "$template" "$doc"

        # Fill in placeholders (profile name, tech stack, etc.)
        sed -i "s/{{PROJECT_NAME}}/$profile_name/g" "$doc"
        sed -i "s/{{TECH_STACK}}/$tech_stack/g" "$doc"
    else
        echo "⚠️  No template found for $doc"
        echo "Creating minimal structure..."

        # Create minimal doc
        cat > "$doc" << EOF
# $(basename "$doc" .md | tr '-' ' ' | sed 's/\b\(.\)/\u\1/g')

> Generated by /manage-docs on $(date +%Y-%m-%d)

## Overview

<!-- TODO: Add overview -->

## Details

<!-- TODO: Add details -->

---

**Last Updated**: $(date +%Y-%m-%d)
**Tech Stack**: $tech_stack
EOF
    fi
done
```

**Example output**:
```
Generate Missing Documentation
==============================

✅ Generated 2 documents:
   - docs/development/rust-backend.md (from template)
   - docs/testing/integration-tests.md (from template)

⚠️  1 document created with minimal structure (no template):
   - docs/api/custom-endpoints.md

Next steps:
  1. Review generated documentation
  2. Fill in TODO sections
  3. Update placeholders with project-specific content
```

---

## Command Options

### All-in-One (Default)

```bash
/manage-docs
# OR
/manage-docs --instant

# Runs all three functions:
# 1. Check structure
# 2. Validate content
# 3. Generate missing (optional, with confirmation)
```

### Individual Components

```bash
# Only check structure
/manage-docs --check

# Only validate content
/manage-docs --validate

# Only generate missing
/manage-docs --generate
```

---

## Integration with Other Skills

**Workflow integration**:
```bash
# After profile change, regenerate docs
/manage-claude-md --configure-profile --select-profile → /manage-docs --check

# After init-docs, validate structure
/init-docs → /manage-docs --validate

# Before release, comprehensive check
/manage-docs --instant
```

---

## Best Practices

### When to Run

**Monthly routine**:
```bash
# Check documentation health
/manage-docs --validate
```

**After tech stack changes**:
```bash
# Regenerate docs for new stack
/manage-docs --check
/manage-docs --generate
```

**Before releases**:
```bash
# Ensure docs are complete
/manage-docs --instant
```

---

## Usage Examples

This section provides practical examples of manage-docs usage across different scenarios.

### Example 1: Check Documentation Structure

**Scenario**: Validate project documentation completeness before PR

**User says:**
> "check if our documentation is complete"

**Execution:**
```bash
/manage-docs --check
```

**What happens:**
1. **Load profile** - Reads `docs/project-profile.md`
   ```yaml
   name: tauri
   techStack:
     frontend: React
     backend: Rust
     desktop: Tauri
   ```

2. **Determine required docs** based on tech stack:
   - ✅ `docs/architecture/tauri-ipc.md`
   - ✅ `docs/development/desktop-builds.md`
   - ❌ `docs/development/rust-backend.md` (missing)
   - ✅ `docs/architecture/component-structure.md`
   - ❌ `docs/testing/rust-tests.md` (missing)

3. **Validate directory structure:**
   - ✅ `docs/` exists
   - ✅ `docs/architecture/` exists
   - ✅ `docs/development/` exists
   - ⚠️ `docs/api/` missing (optional)

4. **Report findings:**
   ```
   📋 Documentation Check Results

   Profile: tauri
   Tech Stack: React + Rust + Tauri

   Missing Documentation (2):
   - docs/development/rust-backend.md
   - docs/testing/rust-tests.md

   Optional (1):
   - docs/api/ directory

   Recommendation: Run /manage-docs --generate
   ```

**Time:** ~5 seconds

**Key insight:** Profile-aware checking ensures tech-stack-specific docs are present.

### Example 2: Generate Missing Documentation

**Scenario**: Auto-create missing docs from templates

**User says:**
> "generate the missing documentation files"

**Execution:**
```bash
/manage-docs --generate
```

**What happens:**
1. **Run check first** to identify missing docs

2. **Find templates** for missing files:
   - Template: `.claude/guides/doc-templates/rust-backend.md.template`
   - Template: `.claude/guides/doc-templates/rust-tests.md.template`

3. **Customize templates** with project data:
   ```markdown
   # Rust Backend Development

   > Auto-generated from template for project: tauri-app

   ## Tech Stack
   - Backend: Rust
   - IPC: Tauri Commands

   ## Project Structure
   ```

4. **Create backup** before writing:
   ```bash
   Backup created: .claude/backups/docs-20260407-154530/
   ```

5. **Write generated files:**
   - Created: `docs/development/rust-backend.md`
   - Created: `docs/testing/rust-tests.md`

6. **Update documentation index:**
   ```bash
   Updated: docs/INDEX.md
   Added 2 new entries
   ```

7. **Report results:**
   ```
   ✅ Documentation Generated

   Created (2):
   - docs/development/rust-backend.md
   - docs/testing/rust-tests.md

   Backup: .claude/backups/docs-20260407-154530/

   Next steps:
   1. Review generated files
   2. Customize content for your project
   3. Commit changes
   ```

**Time:** ~10 seconds

**Key insight:** Templates are customized with project context from profile.

### Example 3: Profile-Specific Documentation

**Scenario**: Generate docs for different profile (e.g., testing Next.js setup)

**User says:**
> "show me what docs would be needed for a Next.js + AWS setup"

**Execution:**
```bash
/manage-docs --check --profile=nextjs-aws --dry-run
```

**What happens:**
1. **Override profile** temporarily:
   ```python
   profile = load_profile("nextjs-aws")  # Instead of reading project-profile.md
   ```

2. **Determine required docs** for Next.js + AWS:
   - `docs/architecture/nextjs-routing.md`
   - `docs/infrastructure/aws-deployment.md`
   - `docs/api/lambda-functions.md`
   - `docs/development/react-patterns.md`

3. **Compare with current docs:**
   - ❌ None exist (different stack)

4. **Dry-run report** (no files created):
   ```
   🔍 Dry Run: Profile nextjs-aws

   Would require (4 files):
   - docs/architecture/nextjs-routing.md
   - docs/infrastructure/aws-deployment.md
   - docs/api/lambda-functions.md
   - docs/development/react-patterns.md

   Would create backup: .claude/backups/docs-20260407-154600/

   ℹ️  Dry run - no changes made
   Run without --dry-run to generate
   ```

**Time:** ~3 seconds

**Key insight:** --profile override allows testing different configurations without modifying project.

### Example 4: Validate and Fix Broken Links

**Scenario**: Check documentation for broken internal links

**User says:**
> "validate our documentation and fix any broken links"

**Execution:**
```bash
/manage-docs --validate --fix-links
```

**What happens:**
1. **Scan all markdown files** in `docs/`

2. **Check internal links:**
   ```markdown
   # Found in docs/architecture/overview.md:
   [Component Structure](../development/components.md)  ✅ Valid
   [API Guide](../api/endpoints.md)  ❌ Broken (file not found)
   [Rust Backend](./backend.md)  ❌ Broken (should be ../development/rust-backend.md)
   ```

3. **Check external links:**
   ```markdown
   https://tauri.app/v1/guides/  ✅ Valid (200 OK)
   https://example.com/old-page  ⚠️ Warning (404 Not Found)
   ```

4. **Auto-fix enabled** - attempt repairs:
   ```
   Fixing broken links:
   - ./backend.md → ../development/rust-backend.md (found nearby)
   - ../api/endpoints.md → (no fix available, flagged for manual review)
   ```

5. **Report results:**
   ```
   📝 Validation Results

   Internal links checked: 24
   - ✅ Valid: 20
   - ❌ Broken: 2 (1 auto-fixed)
   - ⚠️  Manual review needed: 1

   External links checked: 8
   - ✅ Valid: 7
   - ⚠️  404 errors: 1

   Auto-fixed (1):
   - docs/architecture/overview.md:
     ./backend.md → ../development/rust-backend.md

   Manual review needed (1):
   - docs/architecture/overview.md:
     ../api/endpoints.md (file does not exist)

   Next: Review changes and commit
   ```

**Time:** ~15 seconds (includes HTTP requests for external links)

**Key insight:** --fix-links automates common link corrections while flagging issues needing manual attention.

## Related Documentation

- [Project Profile](../../docs/project-profile.md) - Tech stack config
- [Doc Templates](../../.claude/guides/doc-templates/) - Templates directory
- [Documentation Guide](../../.claude/guides/DOCUMENTATION_GUIDE.md) - Standards

---

## AI Execution Instructions

When user invokes `/manage-docs`:

1. **Always check profile first**:
   ```bash
   if [ -f "docs/project-profile.md" ]; then
       echo "📋 Using profile: $(grep 'name:' docs/project-profile.md)"
   else
       echo "⚠️  No profile configured (using defaults)"
   fi
   ```

2. **Graceful degradation**:
   - If profile missing → use minimal doc structure
   - If template missing → create basic structure
   - If validation fails → continue with warnings

3. **Logging**:
   ```bash
   LOG_FILE=".claude/logs/manage-docs-$(date +%Y%m%d).log"
   echo "[$(date)] Checked docs: 2 missing, 1 broken link" >> "$LOG_FILE"
   ```

4. **Confirmation for generation**:
   - Always ask before generating multiple docs
   - Show list of docs to be created
   - Allow selective generation

---

**Version:** 1.0.0
**Pattern:** Profile-Aware Management Skill
**Last Updated:** 2026-03-27
**Changelog:**
- v1.0.0 (2026-03-27): Initial release - documentation structure and content management with profile integration
