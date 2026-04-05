# Framework-Only Skills Filtering

> Automatic exclusion of framework management tools during project synchronization

**Issue #401**: Added in update-skills v3.1.0 (2026-03-18)

## Overview

When syncing skills from the ai-dev framework to target projects, skills marked with `framework-only: true` are automatically excluded. These are framework management tools (update-* series) that are only useful in the framework repository itself.

**Why this matters:**
- Target projects don't need framework maintenance tools
- Reduces skill footprint by ~20% (28 instead of 35 skills)
- Prevents confusion about which skills are relevant
- Automatic - no manual filtering required

## Excluded Skills (7 total)

```
update-framework    - Sync framework content between projects
update-skills       - Sync skills between projects (this skill)
update-pillars      - Sync Pillars between projects
update-guides       - Sync AI guides between projects
update-permissions  - Generate permission templates
update-doc-refs     - Update documentation references
update-rules        - [Deprecated] Generate rules from templates
```

**Result**: Target projects receive 28 skills instead of 35 (↓20% footprint).

## How It Works

### 1. YAML Metadata Marking

Framework-only skills have `framework-only: true` in their YAML frontmatter:

```yaml
---
name: update-framework
version: "4.1.0"
framework-only: true  # Marks this skill as framework-only
user-invocable: true
---
```

**Fields:**
- `name`: Skill identifier
- `version`: Semantic version
- `framework-only`: `true` = exclude from sync, `false` or omitted = include
- `user-invocable`: Whether skill can be invoked by users

### 2. Automatic Filtering During Sync

**Detection logic** (from sync.py):

```python
def filter_framework_only_skills(
    skills: List[Path]
) -> Tuple[List[Path], List[str]]:
    """
    Filter out framework-only skills from skill list

    Args:
        skills: List of skill directory paths

    Returns:
        Tuple of (skills_to_sync, excluded_skill_names)
    """
    to_sync = []
    excluded = []

    for skill_dir in skills:
        skill_md = skill_dir / "SKILL.md"

        # Parse YAML frontmatter
        metadata = parse_skill_metadata(skill_md.read_text())

        # Check framework-only field (default: false)
        if metadata.get('framework-only', False):
            excluded.append(skill_dir.name)
            print(f"⏭️  Skipping {skill_dir.name} (framework-only)")
        else:
            to_sync.append(skill_dir)

    return to_sync, excluded
```

**Key points:**
- Uses `metadata.get('framework-only', False)` for backward compatibility
- Skills without `framework-only` field default to `False` (include in sync)
- Filtering happens before sync operations (no wasted work)
- Both to-be-synced and excluded lists are tracked for reporting

### 3. Works in Both Sync Modes

Filtering applies to both sync modes:
- **Default mode** (complete replacement): Excluded skills not copied
- **Incremental mode** (version comparison): Excluded skills not analyzed

**Complete replacement workflow:**
```bash
/update-skills --from ~/dev/ai-dev

1. List all skills in source (35 skills)
2. Filter framework-only (7 excluded → 28 remaining)
3. Delete target .claude/skills/ completely
4. Copy 28 filtered skills to target
```

**Incremental workflow:**
```bash
/update-skills --from ~/dev/ai-dev --incremental

1. List all skills in source (35 skills)
2. Filter framework-only (7 excluded → 28 remaining)
3. Compare 28 skills with target versions
4. Show diff preview
5. Sync updated skills only
```

## Sync Summary Output

Updated output shows excluded skills clearly:

```
📊 Skills Analysis:
- Total source skills: 35
- Framework-only (excluded): 7
- Synced to target: 28

⏭️  Excluded (framework-only):
  - update-framework
  - update-skills
  - update-pillars
  - update-guides
  - update-permissions
  - update-doc-refs
  - update-rules

✅ Synced skills (28):
  - start-issue
  - execute-plan
  - review
  - finish-issue
  - eval-plan
  - ...
```

## Adding Framework-Only Skills

To mark a new skill as framework-only:

1. **Add field to YAML frontmatter** (after version line):
   ```yaml
   ---
   name: my-framework-tool
   version: "1.0.0"
   framework-only: true  # Add this line
   user-invocable: true
   ---
   ```

2. **Skill will be auto-excluded** in future syncs to target projects

**Use cases for framework-only:**
- Framework maintenance tools (update-*)
- Internal development utilities
- Framework testing skills
- Migration scripts

## Backward Compatibility

**Skills without `framework-only` field:**
- Default to `False` (included in sync)
- No migration needed for existing skills
- Opt-in system (explicit marking required)

**Old skills continue to work:**
```yaml
---
name: review
version: "2.3.0"
# No framework-only field → defaults to false → synced normally
---
```

## Related Implementation

**Shared modules:**
- `_scripts/utils/sync.py`: Core filtering logic
  - `parse_skill_metadata()`: YAML frontmatter parser
  - `filter_framework_only_skills()`: Filtering function

**Tests:**
- `_scripts/tests/test_sync_utils.py`: Unit tests for filtering logic

**See also:**
- [SKILL.md](./SKILL.md): Core usage documentation
- [MODES.md](./MODES.md): Sync mode details
- Issue #401: Original feature request and implementation

---

**Version**: 3.1.0
**Issue**: #401
**Commit**: b55ef60
**Added**: 2026-03-18
