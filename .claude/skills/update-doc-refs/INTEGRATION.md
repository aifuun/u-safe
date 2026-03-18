# Integration Guide - Update Doc Refs

> How to integrate `/update-doc-refs` into your documentation migration workflow

## Overview

This skill is part of the documentation migration trilogy:

```
1. /init-docs       → Generate documentation structure
2. /migrate-docs    → Restructure existing documentation
3. /update-doc-refs → Update all references (THIS SKILL)
4. /check-docs      → Validate quality
```

## Integration with /migrate-docs

### Workflow Sequence

```bash
# Step 1: Migrate documentation structure
cd ~/dev/ai-dev
/migrate-docs ../buffer

# Step 2: Update references (automatic after migration)
cd ../buffer
/update-doc-refs

# Step 3: Validate result
/check-docs --verbose
```

### What /migrate-docs Provides

**Required Input for update-doc-refs:**

1. **docs.old/ directory** - Backup of original structure
   ```
   docs.old/
   ├── deployment/
   │   ├── AWS.md
   │   └── MONITORING.md
   ├── workflow/
   │   └── GIT_FLOW.md
   └── Api-Guide.md
   ```

2. **docs/ directory** - New structure
   ```
   docs/
   ├── ops/
   │   ├── AWS.md
   │   └── MONITORING.md
   ├── dev/
   │   └── WORKFLOW.md
   └── arch/
       └── API.md
   ```

3. **Path mapping** - Automatically detected by comparing structures
   ```
   docs/deployment/  → docs/ops/
   docs/workflow/    → docs/dev/
   docs/Api-Guide.md → docs/arch/API.md
   ```

## How Path Mapping Works

### Detection Strategy

**update-doc-refs uses AI intelligence to detect mappings:**

```python
# 1. Scan both directories
old_structure = scan_directory("docs.old/")
new_structure = scan_directory("docs/")

# 2. AI analyzes and creates mapping based on:
#    - File name similarity
#    - Directory reorganization patterns
#    - Content similarity (if needed)
#    - Known migration patterns (deployment→ops, workflow→dev)

mapping = {
    "docs/deployment/": "docs/ops/",
    "docs/workflow/": "docs/dev/",
    "docs/dev/ROADMAP.md": "docs/product/roadmap.md",
    "docs/Api-Guide.md": "docs/arch/API.md",
}
```

### Example Mappings

| Old Path | New Path | Reason |
|----------|----------|--------|
| `docs/deployment/` | `docs/ops/` | Standard pattern: deployment → ops |
| `docs/workflow/` | `docs/dev/` | Standard pattern: workflow → dev |
| `docs/Api-Guide.md` | `docs/arch/API.md` | Case normalization + category change |
| `docs/dev/ROADMAP.md` | `docs/product/roadmap.md` | Content-based: roadmap is product planning |

## File Scanning Strategy

### Supported File Types

**update-doc-refs scans these file types for references:**

```python
file_types = {
    "*.md":    ["README.md", "CLAUDE.md", "docs/**/*.md"],
    "*.tsx":   ["src/components/**/*.tsx"],
    "*.ts":    ["src/**/*.ts", "tests/**/*.ts"],
    "*.js":    ["src/**/*.js", "scripts/**/*.js"],
    "*.json":  ["package.json", ".vscode/settings.json"],
    "*.yml":   [".github/workflows/*.yml"],
    "*.yaml":  ["config/*.yaml"]
}
```

### Grep Strategy

**Using AI Grep tool for efficient searching:**

```python
# Search Markdown files
markdown_matches = Grep(
    pattern="docs/",
    glob="*.md",
    output_mode="files_with_matches"
)

# Search React components
tsx_matches = Grep(
    pattern="docs/",
    glob="*.tsx",
    output_mode="files_with_matches"
)

# Combine results
files_with_refs = list(set(markdown_matches + tsx_matches + ...))
```

## Replacement Logic Integration

### Context-Aware Replacement

**AI analyzes context before replacement:**

```python
for file_path in files_with_refs:
    content = Read(file_path)

    for old_path, new_path in mapping.items():
        for match in find_all_matches(content, old_path):
            context = get_surrounding_context(match, lines=2)

            # Context detection
            if is_example_code(context):
                continue  # Skip placeholders
            elif is_historical_record(context):
                continue  # Skip changelog
            elif is_markdown_link(context):
                update = replace_markdown_link(content, old_path, new_path)
            elif is_anchor_link(context):
                if validate_anchor(new_path, match.anchor):
                    update = replace_with_anchor(content, old_path, new_path)
            else:
                update = replace_simple(content, old_path, new_path)

            # Apply update
            Edit(file_path, old_string=content, new_string=update)
```

### Integration with Edit Tool

**Using AI Edit tool for precise replacements:**

```python
# Example: Update README.md
old_content = Read("README.md")

# Find and replace
new_content = old_content.replace(
    "docs/deployment/AWS.md",
    "docs/ops/AWS.md"
)

# Write back
Edit("README.md", old_string=old_content, new_string=new_content)
```

## Validation Integration

### Link Validation Strategy

**After replacement, validate all links:**

```python
broken_links = []

for file_path in updated_files:
    content = Read(file_path)
    links = extract_doc_links(content)

    for link in links:
        target_file = resolve_link_path(link.path, relative_to=file_path)

        if not file_exists(target_file):
            broken_links.append({
                "source_file": file_path,
                "line": link.line_number,
                "broken_link": link.path,
                "suggestion": find_similar_file(target_file)
            })
```

### Integration with /check-docs

**After update-doc-refs, run /check-docs for validation:**

```bash
/update-doc-refs             # Update all references
/check-docs --verbose        # Validate links and structure
```

## Error Handling Integration

### Rollback Mechanism

**If user wants to undo changes:**

```bash
# Save modified file list during execution
echo "README.md CLAUDE.md src/utils/docsLoader.ts" > .update-doc-refs-modified-files.txt

# Rollback if needed
git checkout HEAD -- $(cat .update-doc-refs-modified-files.txt)
```

### Error Recovery

**Handle common error scenarios:**

```python
try:
    # Update references
    update_all_references()
except NoDocsOldError:
    print("❌ No docs.old/ found - run /migrate-docs first")
    sys.exit(1)
except NoReferencesFound:
    print("ℹ️  No documentation references found")
    sys.exit(0)
except Exception as e:
    print(f"❌ Error: {e}")
    rollback_updates()
    sys.exit(1)
```

## Real-World Integration Example

### Buffer Project Migration

**Complete workflow:**

```bash
# 1. Before migration (old structure)
buffer/
├── docs/
│   ├── deployment/
│   ├── workflow/
│   └── Api-Guide.md
└── README.md  # Contains: [AWS Guide](docs/deployment/AWS.md)

# 2. Run migration
cd ~/dev/ai-dev
/migrate-docs ../buffer

# 3. After migration (new structure)
buffer/
├── docs.old/     # Backup
├── docs/
│   ├── ops/
│   ├── dev/
│   └── arch/
│       └── API.md
└── README.md  # Still contains: [AWS Guide](docs/deployment/AWS.md) ❌

# 4. Update references
cd ../buffer
/update-doc-refs

# 5. After update-doc-refs
buffer/
└── README.md  # Now contains: [AWS Guide](docs/ops/AWS.md) ✅

# 6. Validate
/check-docs --verbose
# ✅ All links valid
# ✅ Documentation structure follows DOCUMENTATION_STRUCTURE rule
```

## Integration Checklist

**Before running update-doc-refs:**
- [ ] `/migrate-docs` completed successfully
- [ ] `docs.old/` directory exists
- [ ] `docs/` directory has new structure
- [ ] Git working directory is clean (or can be stashed)

**After running update-doc-refs:**
- [ ] Review changes: `git diff`
- [ ] Check for broken links in report
- [ ] Run `/check-docs --verbose`
- [ ] Fix any broken links manually
- [ ] Commit: `git add . && git commit -m "docs: update refs after migration"`

## Automation Integration

**For CI/CD pipelines:**

```bash
#!/bin/bash
# migrate-and-update.sh

set -e

# Step 1: Migrate
/migrate-docs $PROJECT_DIR

# Step 2: Update references
cd $PROJECT_DIR
/update-doc-refs

# Step 3: Validate
/check-docs --verbose

# Step 4: Auto-commit (optional)
if [ $? -eq 0 ]; then
    git add .
    git commit -m "docs: migrate structure and update refs"
    git push
fi
```

## Troubleshooting Integration Issues

### Issue 1: docs.old/ Missing

**Symptom:**
```
❌ No docs.old/ directory found
```

**Solution:**
```bash
# Run /migrate-docs first
cd ~/dev/ai-dev
/migrate-docs ../buffer
```

### Issue 2: No Mappings Detected

**Symptom:**
```
ℹ️  No path mappings detected
```

**Solution:**
```bash
# Check if docs.old/ and docs/ are different
diff -r docs.old/ docs/

# If identical, migration may not have happened
```

### Issue 3: References Not Updated

**Symptom:**
```
ℹ️  No documentation references found
```

**Solution:**
```bash
# Manually search for references
grep -r "docs/" --include="*.md" --include="*.ts"

# If found, references may be in unexpected format
```

## Performance Considerations

**Integration performance metrics:**

| Phase | Time | Depends On |
|-------|------|------------|
| Path mapping detection | <5s | Directory size |
| File scanning | 10-30s | Project size |
| Reference replacement | 5-20s | Reference count |
| Link validation | 5-10s | Reference count |
| **Total** | **~30-60s** | Project complexity |

**Optimization tips:**
- Run on clean git state (faster diff)
- Use `--dry-run` first to preview (no file writes)
- Run `/check-docs` after to catch issues early

---

**Version:** 1.0.0
**Last Updated:** 2026-03-16
