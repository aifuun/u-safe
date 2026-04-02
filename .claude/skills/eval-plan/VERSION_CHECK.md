# Eval Plan - Version Field Check

Version field validation for plan frontmatter (YAML metadata).

## Overview

This document describes the version field checking logic added to eval-plan. This feature ensures all implementation plans include proper version metadata for tracking and change management.

**Implementation**: As of v1.4.1, version checking uses the shared `.claude/skills/_scripts/utils/version.py` module (Issue #406) instead of embedded logic.

**Related**: See [SKILL.md](SKILL.md) for overview | [CHECKLIST.md](CHECKLIST.md) for evaluation criteria | [SCORING.md](SCORING.md) for scoring

---

## Purpose

**Why check version fields?**

1. **Change tracking** - Version history helps understand plan evolution
2. **Compatibility** - Skills can check if plan format is compatible
3. **Documentation** - Clear versioning improves maintainability
4. **Standards compliance** - Follows ADR-016 and skill versioning standards

**When to check?**

- During eval-plan execution (Step 6.5)
- After plan generation by /start-issue
- Before plan execution by /execute-plan

---

## Validation Logic

### YAML Frontmatter Format

**Expected structure**:
```yaml
---
version: "2.0"
issue: 419
title: "Issue title"
status: active
created: 2026-03-30
worktree: /path/to/worktree
branch: feature/419-issue-title
---
```

**Required fields**:
- `version` - Semantic version string (e.g., "2.0", "1.5.3")
- `issue` - Issue number (integer)
- `title` - Issue title (string)
- `status` - Plan status: "active" | "completed" | "archived"

**Optional fields**:
- `created` - Creation date (YYYY-MM-DD)
- `worktree` - Worktree path (if using worktrees)
- `branch` - Git branch name

### Check Implementation

```python
# AI-EXECUTABLE
import re
import yaml

def check_version_field(plan_content: str) -> dict:
    """
    检查计划文件的 YAML frontmatter 是否包含 version 字段

    Returns:
        dict with keys:
        - has_version: bool
        - version_value: str | None
        - is_valid: bool
        - error: str | None
    """
    # Extract YAML frontmatter
    frontmatter_match = re.match(r'^---\n(.+?)\n---', plan_content, re.DOTALL)

    if not frontmatter_match:
        return {
            "has_version": False,
            "version_value": None,
            "is_valid": False,
            "error": "No YAML frontmatter found"
        }

    try:
        # Parse YAML
        frontmatter = yaml.safe_load(frontmatter_match.group(1))

        # Check version field
        if "version" not in frontmatter:
            return {
                "has_version": False,
                "version_value": None,
                "is_valid": False,
                "error": "Missing 'version' field in frontmatter"
            }

        version = frontmatter["version"]

        # Validate version format (semantic versioning)
        if not re.match(r'^\d+\.\d+(\.\d+)?$', str(version)):
            return {
                "has_version": True,
                "version_value": version,
                "is_valid": False,
                "error": f"Invalid version format: '{version}' (expected: X.Y or X.Y.Z)"
            }

        return {
            "has_version": True,
            "version_value": version,
            "is_valid": True,
            "error": None
        }

    except yaml.YAMLError as e:
        return {
            "has_version": False,
            "version_value": None,
            "is_valid": False,
            "error": f"YAML parsing error: {e}"
        }
```

### Integration with Eval-Plan

```python
# AI-EXECUTABLE
# Step 6.5: Check version field (after Step 6: Check task clarity)
TaskUpdate(version_check_task_id, status="in_progress")

version_check = check_version_field(plan_content)

if not version_check["has_version"]:
    # Warning (not blocking) - can be auto-fixed
    issues.append({
        "task": "Plan frontmatter",
        "category": "version_missing",
        "severity": "warning",
        "description": "Plan frontmatter missing version field",
        "fix": "Add 'version: \"2.0\"' to YAML frontmatter",
        "impact": "low"
    })

    # Deduct 2 points from clarity score (or create separate dimension)
    # Note: This is a minor issue, doesn't significantly affect score

elif not version_check["is_valid"]:
    # Warning - invalid version format
    issues.append({
        "task": "Plan frontmatter",
        "category": "version_invalid",
        "severity": "warning",
        "description": f"Invalid version format: '{version_check['version_value']}'",
        "fix": "Use semantic versioning (e.g., '2.0', '1.5.3')",
        "impact": "low"
    })

TaskUpdate(version_check_task_id, status="completed")
```

---

## Auto-Fix

**When version field is missing**, auto-fix can add it:

```python
# AI-EXECUTABLE
def add_version_field(plan_content: str) -> tuple[str, dict]:
    """
    Add version field to plan frontmatter

    Returns:
        (modified_content, fix_log)
    """
    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.+?)\n---', plan_content, re.DOTALL)

    if not frontmatter_match:
        # No frontmatter - create one
        new_frontmatter = '''---
version: "2.0"
---

'''
        modified_content = new_frontmatter + plan_content

        return modified_content, {
            "type": "version_missing",
            "description": "Added version field to new frontmatter",
            "after": 'version: "2.0"'
        }

    # Parse existing frontmatter
    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    frontmatter["version"] = "2.0"  # Default version

    # Reconstruct content
    new_frontmatter_str = yaml.dump(frontmatter, default_flow_style=False)
    remaining_content = plan_content[frontmatter_match.end():]
    modified_content = f"---\n{new_frontmatter_str}---{remaining_content}"

    return modified_content, {
        "type": "version_missing",
        "description": "Added version: \"2.0\" to plan frontmatter"
    }
```

**Auto-fix conditions**:
- Mode is `--mode=auto`
- Score ≥ 90 (passing threshold)
- Issue is `version_missing` (auto-fixable)

**Example**:

Before:
```yaml
---
issue: 419
title: "Optimize eval-plan"
status: active
---
```

After auto-fix:
```yaml
---
version: "2.0"  # ← Added
issue: 419
title: "Optimize eval-plan"
status: active
---
```

---

## Versioning Guidelines

### When to Increment Version

Follow semantic versioning for plan versions:

**Major version (X.0)**: Breaking changes to plan structure
- Example: 1.0 → 2.0 when changing task format

**Minor version (X.Y)**: New tasks or significant additions
- Example: 2.0 → 2.1 when adding new phase

**Patch version (X.Y.Z)**: Minor fixes or clarifications
- Example: 2.1 → 2.1.1 when fixing typo or clarifying task

### Default Version

When creating new plans:
- **First plan for issue**: `version: "1.0"`
- **Plan revision**: Increment from previous version

When auto-fixing missing version:
- **Default**: `version: "2.0"` (assumes modern plan format)

---

## Examples

### Example 1: Valid Version Field

```yaml
---
version: "2.0"
issue: 419
title: "Optimize eval-plan"
status: active
created: 2026-03-30
---
```

**Check result**:
```json
{
  "has_version": true,
  "version_value": "2.0",
  "is_valid": true,
  "error": null
}
```

**Evaluation**: ✅ Pass (no warnings)

### Example 2: Missing Version Field

```yaml
---
issue: 419
title: "Optimize eval-plan"
status: active
---
```

**Check result**:
```json
{
  "has_version": false,
  "version_value": null,
  "is_valid": false,
  "error": "Missing 'version' field in frontmatter"
}
```

**Evaluation**: ⚠️ Warning (auto-fixable)

**Auto-fix**: Add `version: "2.0"` to frontmatter

### Example 3: Invalid Version Format

```yaml
---
version: "v2.0"  # ← Invalid (has 'v' prefix)
issue: 419
---
```

**Check result**:
```json
{
  "has_version": true,
  "version_value": "v2.0",
  "is_valid": false,
  "error": "Invalid version format: 'v2.0' (expected: X.Y or X.Y.Z)"
}
```

**Evaluation**: ⚠️ Warning (manual fix required)

**Fix**: Change `version: "v2.0"` to `version: "2.0"`

---

## Testing

### Test Cases

**Test 1**: Plan with valid version field
```python
# AI-EXECUTABLE
plan_with_version = """---
version: "2.0"
issue: 419
---

# Issue #419
...
"""

result = check_version_field(plan_with_version)
assert result["has_version"] == True
assert result["is_valid"] == True
```

**Test 2**: Plan without version field
```python
# AI-EXECUTABLE
plan_without_version = """---
issue: 419
---

# Issue #419
...
"""

result = check_version_field(plan_without_version)
assert result["has_version"] == False
assert result["error"] == "Missing 'version' field in frontmatter"
```

**Test 3**: Auto-fix adds version field
```python
# AI-EXECUTABLE
plan_without_version = """---
issue: 419
title: "Test"
---

# Issue #419
"""

fixed_content, fix_log = add_version_field(plan_without_version)

# Verify version was added
result = check_version_field(fixed_content)
assert result["has_version"] == True
assert result["version_value"] == "2.0"
```

---

## Summary

**What it does**:
- Checks plan YAML frontmatter for `version` field
- Validates version format (semantic versioning)
- Auto-fixes missing version in auto mode

**When it runs**:
- Step 6.5 of eval-plan execution
- After task clarity check (Step 6)
- Before final scoring (Step 7)

**Severity**:
- Missing version: ⚠️ Warning (auto-fixable, low impact)
- Invalid version: ⚠️ Warning (manual fix, low impact)

**Auto-fix**:
- Adds `version: "2.0"` to frontmatter when missing
- Only in auto mode with score ≥ 90
- Included in AUTO_FIXABLE issues

**Integration**:
- Part of eval-plan workflow (SKILL.md)
- Contributes to overall evaluation score
- Recorded in status file

**See Also**:
- [SKILL.md](SKILL.md) - Skill overview and AI execution instructions
- [CHECKLIST.md](CHECKLIST.md) - Evaluation criteria (5 dimensions)
- [SCORING.md](SCORING.md) - Scoring algorithm and auto-fix mode

---

**Version:** 1.0.0
**Last Updated:** 2026-03-30
**Part of**: eval-plan skill (v1.4.0)
**Feature Origin**: Issue #401 (framework-only metadata marking)
**Compliance:** ADR-016 ✅ (modular documentation)
