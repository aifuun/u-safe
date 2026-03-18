# Update Doc Refs - Documentation Reference Updater

> Automatically update all documentation references after structure migration

## Quick Start

After running `/migrate-docs` on a project:

```bash
cd ~/dev/buffer
/update-doc-refs                  # Update all references
/update-doc-refs --dry-run        # Preview changes first
/update-doc-refs --verbose        # Detailed output
```

## What It Does

This skill updates documentation references throughout your project after `/migrate-docs` restructures the documentation:

1. **Detects changes** - Compares `docs.old/` vs `docs/` to generate path mapping
2. **Scans files** - Finds all documentation references in Markdown, source code, and config files
3. **Replaces intelligently** - Updates references with context awareness (7 scenarios)
4. **Validates links** - Ensures updated references point to existing files
5. **Reports results** - Detailed change report with recommendations

## Why You Need It

After documentation migration, references scattered across your project become outdated:

- ❌ Broken links in README.md
- ❌ Outdated paths in source code
- ❌ Invalid references in configuration files

Manual updates are error-prone and time-consuming. This skill automates the entire process.

## Context-Aware Replacement (7 Scenarios)

The skill intelligently handles different reference contexts:

| Scenario | Action | Example |
|----------|--------|---------|
| **Markdown links** | ✅ Replace | `[Guide](docs/deployment/AWS.md)` → `[Guide](docs/ops/AWS.md)` |
| **Relative paths** | ✅ Replace | `docs/dev/ROADMAP.md` → `docs/product/roadmap.md` |
| **Code strings** | ✅ Replace | `const path = "docs/deployment/"` → `"docs/ops/"` |
| **Example code** | ❌ Skip | `// Example: docs/your-category/your-file.md` (placeholder) |
| **Historical records** | ❌ Skip | `## Changelog - 2024-01-01: Created docs/deployment/AWS.md` |
| **Anchor links** | ✅ Replace + Validate | `[Strategy](docs/workflow/GIT_FLOW.md#branching)` → `[Strategy](docs/dev/WORKFLOW.md#branching)` |
| **JSON config** | ✅ Replace | `{"docsPath": "docs/deployment"}` → `{"docsPath": "docs/ops"}` |

## Complete Workflow

```bash
# Step 1: Migrate documentation structure
cd ~/dev/ai-dev
/migrate-docs ../buffer

# Step 2: Update all references (this skill)
cd ../buffer
/update-doc-refs

# Step 3: Validate result
/check-docs --verbose

# Step 4: Review and commit
git diff
git add . && git commit -m "docs: update refs after migration"
```

## Example Output

```
📋 Detecting documentation structure changes...
   15 path mappings detected

🔍 Scanning project files...
   13 files with doc refs found (33 references)

✅ Replacements Applied:
   📄 README.md (5 references updated)
   📄 CLAUDE.md (8 references updated)
   📄 src/utils/docsLoader.ts (2 references updated)

✅ 13 files updated, 31 references fixed
❌ 2 broken links (manual review needed)
⏭️  6 references skipped (placeholders/history)

Next steps:
  1. Review changes: git diff
  2. Fix broken links manually (2 found)
  3. Commit: git commit -m "docs: update refs after migration"
```

## Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview changes without applying |
| `--verbose` | Show detailed output for each replacement |
| `--quiet` | Minimal output (only summary) |

## Error Handling

**No docs.old/ directory:**
```
❌ No docs.old/ directory found
This skill requires docs.old/ from /migrate-docs.
Fix: Run /migrate-docs first
```

**No references found:**
```
ℹ️  No documentation references found
All files scanned, but no "docs/" references detected.
```

## Best Practices

1. **Always run after /migrate-docs** - This skill requires `docs.old/` backup
2. **Use --dry-run first** - Preview changes before applying
3. **Review git diff** - Check all replacements make sense
4. **Fix broken links** - Address any broken links flagged in report
5. **Commit separately** - Keep ref updates in dedicated commit

## Related Skills

- **/migrate-docs** - Documentation structure migration (run before this)
- **/check-docs** - Documentation quality validation (run after this)
- **/init-docs** - Initialize documentation structure

## Performance

- **Detection**: <5 seconds
- **Scanning**: 10-30 seconds (depends on project size)
- **Replacement**: 5-20 seconds
- **Validation**: 5-10 seconds
- **Total**: ~30-60 seconds

Fast because AI tools (Grep, Read, Edit) are optimized for search and replacement.

---

**Version:** 1.0.0
**Pattern:** Tool-Reference (pure AI instruction implementation)
**Compliance:** ADR-001 ✅
**Last Updated:** 2026-03-16
