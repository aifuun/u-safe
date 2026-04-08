# Integration Guide - migrate-docs

> How migrate-docs integrates with other framework skills

## Skill Dependencies

### Required Skills

**migrate-docs depends on:**

1. **`/init-docs`** (Issue #222)
   - Called in Step 3 to create standard structure
   - Must be installed in target project
   - Generates standard directories based on profile

2. **`/check-docs`** (Issue #223)
   - Called in Step 1 for baseline score
   - Called in Step 7 for validation
   - Provides before/after comparison

### Optional Skills (Recommended)

**Works well with:**

3. **`/update-doc-refs`** (Issue #241)
   - Run AFTER migration completes
   - Fixes code references to moved docs
   - Prevents broken links in codebase

## Workflow Integration

### Complete Migration Workflow

```bash
# Phase 1: Migration
cd ~/dev/ai-dev
/migrate-docs ../buffer

# Phase 2: Fix References
/update-doc-refs ../buffer

# Phase 3: Validation
cd ../buffer
/check-docs --verbose

# Phase 4: Cleanup (when confident)
rm -rf docs.old/
```

### Integration with Framework Sync

**Before migration:**
```bash
# Ensure target project has latest skills
cd ~/dev/ai-dev
/update-skills ../buffer

# Verify /init-docs and /check-docs are available
cd ../buffer
ls .claude/skills/init-docs/
ls .claude/skills/check-docs/
```

**After migration:**
```bash
# Update documentation
cd ~/dev/ai-dev
git add docs/DOCUMENTATION_MIGRATION_GUIDE.md
git commit -m "docs: update migration guide with buffer example"
```

## Error Handling

**If `/init-docs` is missing:**
```
❌ /init-docs skill not found in target project

Fix:
cd ~/dev/ai-dev
/update-skills ../buffer
```

**If `/check-docs` is missing:**
```
⚠️  /check-docs not available - skipping score validation

Recommendation: Install skill for score tracking
cd ~/dev/ai-dev
/update-skills ../buffer
```

## Data Flow

```
Input:
  - Target project path (e.g., ../buffer)
  - Existing docs/ structure
  - Project profile

Processing:
  1. /check-docs → Baseline score
  2. mv docs docs.old → Backup
  3. /init-docs → Standard structure
  4. Migration mapping → COPY/MERGE/MOVE
  5. File operations → Content migration
  6. Index generation → docs/README.md
  7. /check-docs → New score

Output:
  - docs/ (ai-dev standard)
  - docs.old/ (backup)
  - docs/README.md (index)
  - Migration report
```

## State Management

**No persistent state** - single execution model:
- Skill runs to completion in one invocation
- Uses filesystem for backup (docs.old/)
- No resume capability (rerun if interrupted)

**Idempotent execution:**
- Can safely rerun if migration fails
- Rollback mechanism restores original state
- docs.old/ existence check prevents conflicts

## Profile-Aware Behavior

**Different profiles = different structures:**

| Profile | ops/ Directory | Deployment Docs |
|---------|----------------|-----------------|
| `tauri` | ❌ Not created | ❌ Not migrated |
| `tauri-aws` | ✅ Created | ✅ Migrated |
| `nextjs-aws` | ✅ Created | ✅ Migrated |

**Detection:**
```bash
# Reads target project's profile
PROFILE=$(cat $TARGET_PROJECT/.framework-install | grep profile)

# Adjusts migration mapping accordingly
if [ "$PROFILE" = "tauri" ]; then
    # Skip ops/ migration
    skip_deployment_docs
fi
```

## Testing Integration

**Test with real projects:**
```bash
# Test 1: buffer project (tauri profile)
/migrate-docs ../buffer --dry-run
# Expected: No ops/ directory in mapping

# Test 2: nextjs-aws project
/migrate-docs ../some-web-app --dry-run
# Expected: ops/ directory in mapping

# Test 3: Rollback mechanism
/migrate-docs ../test-project --force
# Simulate failure, verify rollback works
```

## API for Future Skills

**If other skills need to call migrate-docs programmatically:**

```bash
# Minimal invocation
migrate_docs_api() {
    local target_path=$1
    local options=${2:-""}

    cd ~/dev/ai-dev
    /migrate-docs "$target_path" $options
}

# Usage example
migrate_docs_api "../buffer" "--dry-run"
```

## Version Compatibility

**migrate-docs v1.0.0 requires:**
- init-docs ≥ v1.0.0 (from Issue #222)
- check-docs ≥ v1.0.0 (from Issue #223)
- DOCUMENTATION_MIGRATION_GUIDE.md (from Issue #239)

**update-doc-refs compatibility:**
- Works with update-doc-refs v1.0.0+ (from Issue #241)
- Optional dependency (migration works without it)

## Related Documentation

- **[SKILL.md](SKILL.md)** - Complete skill documentation
- **[README.md](README.md)** - Quick start guide
- **[DOCUMENTATION_MIGRATION_GUIDE.md](../../docs/DOCUMENTATION_MIGRATION_GUIDE.md)** - Migration strategy

---

**Version:** 1.0.0
**Last Updated:** 2026-03-16
