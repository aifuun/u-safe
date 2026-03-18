# migrate-docs - Automated Documentation Migration

> Safely migrate project documentation to ai-dev standard structure

## Quick Start

```bash
# Basic migration
/migrate-docs ../buffer

# Preview without changes
/migrate-docs ../buffer --dry-run

# Migration with cleanup
/migrate-docs ../buffer --delete-old
```

## What It Does

Automates the complete documentation migration workflow:

1. ✅ Validates target project
2. ✅ Creates backup (`docs.old/`)
3. ✅ Rebuilds standard structure
4. ✅ Generates migration mapping
5. ✅ Executes content migration
6. ✅ Auto-generates docs index
7. ✅ Validates new structure
8. ✅ Generates detailed report

## Migration Strategy

**Rename + Rebuild + Index** (not direct `git mv`):
- Safer than in-place modification
- Preserves backup for rollback
- Generates complete index
- Easy to undo if needed

## Use Cases

- **buffer project**: Migrate from custom structure to ai-dev standard
- **u-safe project**: Adopt standard documentation format
- **Any project**: Convert existing docs to framework compliance

## Success Criteria

- Score improves from ~65/100 to ≥95/100
- All required directories created
- Content preserved and migrated
- Index generated with all links
- Backup preserved for safety

## Next Steps After Migration

```bash
# 1. Update code references
/update-doc-refs ../buffer

# 2. Validate structure
/check-docs

# 3. Test documentation links

# 4. Delete backup when confident
rm -rf ../buffer/docs.old
```

## Documentation

- **[SKILL.md](SKILL.md)** - Complete skill documentation
- **[INTEGRATION.md](INTEGRATION.md)** - Integration with other skills
- **[DOCUMENTATION_MIGRATION_GUIDE.md](../../docs/DOCUMENTATION_MIGRATION_GUIDE.md)** - Migration strategy details

---

**Version:** 1.0.0
**Last Updated:** 2026-03-16
