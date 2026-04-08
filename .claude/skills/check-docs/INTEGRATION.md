# Check-Docs Integration Guide

Cross-skill workflows and integration patterns for `/check-docs`.

## Bidirectional Workflow with /init-docs

**/init-docs creates → /check-docs validates**

### Pattern 1: Create-Then-Validate

```bash
# 1. Create documentation structure
/init-docs

# 2. Validate structure compliance
/check-docs

# Expected: 100/100 (perfect compliance)
```

**Why:** Ensures `/init-docs` creates compliant structure.

### Pattern 2: Validate-Then-Fix

```bash
# 1. Check existing documentation
/check-docs --verbose

# 2. Auto-fix issues
/check-docs --fix

# 3. Verify fixes
/check-docs
```

**Why:** Brings existing projects into compliance.

### Pattern 3: Incremental Validation

```bash
# After each documentation update
git add docs/
/check-docs

# If issues found
/check-docs --fix
git add docs/
git commit -m "docs: fix compliance issues"
```

**Why:** Maintain compliance over time.

## Auto-Fix Behavior

When `/check-docs --fix` encounters missing files, it has two strategies:

### Strategy 1: Call /init-docs (Recommended)

```python
# If multiple files missing
if len(missing_files) > 3:
    # Call /init-docs to generate all files
    Skill("init-docs", args="--force")
else:
    # Create empty files for < 3 missing
    for file in missing_files:
        touch(file)
```

**Why:** `/init-docs` creates files with proper templates, not just empty files.

### Strategy 2: Create Empty Files

```bash
# For 1-2 missing files
touch docs/TEST_PLAN.md
```

**Why:** Fast fix for minor gaps.

## Profile-Specific Validation

Both skills use `.framework-install` for profile detection:

```bash
# Tauri project
/init-docs                 # Creates docs/desktop/
/check-docs --profile tauri  # Validates docs/desktop/ required

# Tauri-AWS project
/init-docs                      # Creates docs/desktop/ + docs/aws/
/check-docs --profile tauri-aws  # Validates both required

# Next.js-AWS project
/init-docs                        # Creates docs/aws/
/check-docs --profile nextjs-aws  # Validates docs/aws/ required
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Documentation Quality

on: [push, pull_request]

jobs:
  validate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Check documentation structure
        run: /check-docs --json > docs-report.json
        continue-on-error: true

      - name: Validate score
        run: |
          SCORE=$(cat docs-report.json | jq .score)
          echo "Documentation score: $SCORE/100"

          if [ $SCORE -lt 70 ]; then
            echo "❌ Score too low. Run: /check-docs --fix"
            exit 1
          elif [ $SCORE -lt 100 ]; then
            echo "⚠️ Minor issues found. Consider fixing."
          else
            echo "✅ Perfect compliance!"
          fi

      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: docs-compliance-report
          path: docs-report.json
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check if docs/ changed
if git diff --cached --name-only | grep -q '^docs/'; then
    echo "Validating documentation structure..."

    /check-docs
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 2 ] || [ $EXIT_CODE -eq 3 ]; then
        echo "❌ Documentation validation failed"
        echo "Run: /check-docs --verbose"
        exit 1
    elif [ $EXIT_CODE -eq 1 ]; then
        echo "⚠️ Minor documentation issues found"
        echo "Consider: /check-docs --fix"
        # Allow commit with warning
    fi
fi

exit 0
```

## Integration with /adr Skill

When ADR validation fails, `/check-docs --fix` can leverage `/adr`:

```bash
# Check-docs detects missing ADR index
/check-docs --verbose
# → "❌ ADR index missing: docs/ADRs/README.md"

# Auto-fix calls /adr
/check-docs --fix
# Internally: Skill("adr", args="list > docs/ADRs/README.md")

# Verify fix
/check-docs
# → "✅ ADR Validation: 15/15"
```

## Common Workflows

### Workflow 1: New Project Setup

```bash
# Initialize framework
uv run scripts/init-project.py --profile=tauri --name=my-app

# Create documentation
/init-docs

# Validate (should be 100/100)
/check-docs

# Expected: Perfect compliance out of the box
```

### Workflow 2: Onboard Existing Project

```bash
# Check current state
/check-docs --verbose
# Score: 45/100

# Auto-fix what's possible
/check-docs --fix
# Score: 85/100

# Manual fixes for remaining issues
touch docs/PRD.md
# Add content...

# Final validation
/check-docs
# Score: 100/100
```

### Workflow 3: Pre-Release Checklist

```bash
# 1. Update documentation
vim docs/DEPLOYMENT.md

# 2. Validate structure
/check-docs --verbose

# 3. Fix any issues
/check-docs --fix

# 4. Verify ADRs complete
/adr list

# 5. Final check
/check-docs
# Must be 100/100 for release
```

### Workflow 4: Documentation Refactor

```bash
# Before refactor
/check-docs > before.txt

# Make changes
mv docs/old-structure docs/new-structure

# Check compliance
/check-docs --verbose

# Fix naming violations
/check-docs --fix

# Verify improvement
/check-docs > after.txt
diff before.txt after.txt
```

## Error Recovery Patterns

### Missing docs/ Directory

```bash
# Symptom
/check-docs
# → "❌ Documentation directory not found"

# Fix
/init-docs

# Verify
/check-docs
# → "✅ 100/100"
```

### Corrupt Structure

```bash
# Symptom
/check-docs --verbose
# → Multiple missing directories and files

# Nuclear fix
rm -rf docs/
/init-docs
/check-docs
# → "✅ 100/100"
```

### Profile Mismatch

```bash
# Symptom
/check-docs
# → "⚠️ docs/aws/ missing for nextjs-aws profile"

# Fix 1: Correct profile
/check-docs --profile tauri
# → Now validates correctly

# Fix 2: Add missing directories
mkdir -p docs/aws/
/check-docs
# → "✅ 100/100"
```

## Best Practices

1. **Always validate after /init-docs**
   - Ensures structure created correctly
   - Catches any bugs in init-docs

2. **Use --fix for bulk issues**
   - More than 3 violations → use auto-fix
   - Review changes before committing

3. **Integrate in CI/CD early**
   - Prevents compliance drift
   - Enforces standards automatically

4. **Profile consistency**
   - Use same profile in both /init-docs and /check-docs
   - Profile from .framework-install is source of truth

5. **Validate before releases**
   - Require 100/100 score
   - Use --verbose to see all details

## Cross-Skill Dependencies

```
/init-docs → creates structure
    ↓
/check-docs → validates structure
    ↓ (if issues found)
/check-docs --fix → calls /init-docs or /adr as needed
    ↓
/check-docs → re-validates (should be 100/100)
```

## Version Compatibility

| check-docs | init-docs | Compatibility |
|------------|-----------|---------------|
| 1.0.0      | 1.0.0     | ✅ Full       |
| 1.0.0      | 0.9.x     | ⚠️ Partial    |
| 1.0.0      | <0.9.0    | ❌ None       |

**Note:** Both skills should be from same framework version for guaranteed compatibility.

## Future Enhancements

**Planned integrations:**

1. **/check-docs --watch** - Continuous validation during development
2. **Auto-fix: Smart templating** - Generate file content, not just empty files
3. **Integration with /review** - Documentation quality as part of code review
4. **Custom profiles** - Define project-specific documentation requirements

---

**Version:** 1.0.0
**Last Updated:** 2026-03-15
