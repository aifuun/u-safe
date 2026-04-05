---
name: manage-docs
version: "1.0.0"
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
if ! python3 -c "import yaml; yaml.safe_load(open('docs/project-profile.md'))" 2>/dev/null; then
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

## Related Documentation

- [Project Profile](../../docs/project-profile.md) - Tech stack config
- [Doc Templates](../../.claude/guides/doc-templates/) - Templates directory
- [Documentation Guide](../../.claude/guides/DOCUMENTATION_GUIDE.md) - Standards

---

## Notes for Claude

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
