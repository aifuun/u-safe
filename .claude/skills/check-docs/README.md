# Check Docs - Quick Reference

Validate documentation structure compliance and get actionable fix suggestions.

## Quick Start

```bash
# Basic validation
/check-docs

# Detailed output
/check-docs --verbose

# Auto-fix issues
/check-docs --fix

# Check specific profile
/check-docs --profile tauri

# JSON output for CI/CD
/check-docs --json
```

## What It Checks

✅ **Directory Structure** (30 points)
- Required directories exist
- Profile-specific directories present

✅ **Required Files** (40 points)
- 8 mandatory documentation files

✅ **Naming Conventions** (15 points)
- kebab-case directories
- UPPERCASE.md files
- ADR numbering format

✅ **ADR Validation** (15 points)
- Sequential numbering
- No gaps
- Index file exists

## Compliance Levels

- **100** - Perfect ✅
- **70-99** - Minor issues ⚠️
- **40-69** - Needs work 🔧
- **0-39** - Critical ❌

## Common Workflows

**After init-docs:**
```bash
/init-docs
/check-docs  # Validate structure created correctly
```

**Before release:**
```bash
/check-docs --verbose  # Check everything
/check-docs --fix      # Auto-fix if needed
```

**CI/CD pipeline:**
```bash
/check-docs --json > report.json
# Exit code: 0 (perfect), 1 (minor), 2 (major), 3 (error)
```

## Integration

- Pairs with: `/init-docs` (creates structure)
- Uses: `.framework-install` (profile detection)
- Calls: `/adr` (for ADR index generation in --fix mode)

## Full Documentation

See [SKILL.md](SKILL.md) for complete reference.
