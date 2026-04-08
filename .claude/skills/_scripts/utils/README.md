# Shared Utility Modules

> Reusable logic extracted from skills following ADR-014 modular pattern

## Overview

This directory contains shared utility modules used by multiple skills to avoid code duplication and improve maintainability.

**Created by**: Issue #405 (P1 Skills optimization)

## Modules

### sync.py (282 lines)

**Purpose**: Skill synchronization logic for update-skills

**Functions**:
- `parse_skill_metadata(content: str) -> Dict` - Parse YAML frontmatter from SKILL.md
- `filter_framework_only_skills(skills: List[Path]) -> Tuple[List[Path], List[str]]` - Filter framework-only skills (Issue #401)
- `sync_skill(source: Path, target: Path, mode: str)` - Execute skill synchronization

**Used by**: `.claude/skills/update-skills/`

**Sync modes**:
- `REPLACE` - Complete directory replacement (default)
- `INCREMENTAL` - Version-aware selective sync
- `SELECTIVE` - Sync specific skills only

**Example usage**:
```python
import sys
sys.path.insert(0, '.claude/skills/_scripts')

from utils.sync import (
    parse_skill_metadata,
    filter_framework_only_skills,
    sync_skill
)

# Filter framework-only skills
skills_to_sync, excluded = filter_framework_only_skills(source_skills)

# Sync skill
sync_skill(source_path, target_path, skill_name)
```

**Issue #401 Feature**: Auto-excludes 7 framework management tools during sync:
- update-framework, update-skills, update-pillars, update-guides
- update-permissions, update-doc-refs, update-rules

**Result**: Target projects receive 28 skills instead of 35 (↓20% footprint)

### version.py (235 lines)

**Purpose**: Unified version management and validation logic

**Functions**:
- `validate_version_format(version: str) -> bool` - Validate semantic versioning format (X.Y or X.Y.Z)
- `get_version_from_frontmatter(content: str) -> Optional[str]` - Extract version field from YAML frontmatter
- `check_version_field(skill_path: Path) -> Dict` - Check SKILL.md has valid version field
- `compare_versions(v1: str, v2: str) -> int` - Compare two version numbers (-1/0/1)

**Used by**:
- `.claude/skills/eval-plan/` (v1.4.1+) - Plan version validation
- `.claude/skills/review/` (v2.4.1+) - Skill version update checking

**Example usage**:
```python
import sys
from pathlib import Path
sys.path.insert(0, '.claude/skills/_scripts')

from utils.version import validate_version_format, check_version_field

# Validate version format
is_valid = validate_version_format("1.4.0")  # True
is_valid = validate_version_format("v1.0.0")  # False (no v prefix)

# Check SKILL.md version field
result = check_version_field(Path(".claude/skills/eval-plan/SKILL.md"))
print(result['has_version'])  # True
print(result['version'])      # "1.4.1"
print(result['valid_format']) # True

# Compare versions
from utils.version import compare_versions
compare_versions("1.0.0", "2.0.0")  # -1 (v1 < v2)
compare_versions("2.0.0", "2.0.0")  # 0 (v1 == v2)
compare_versions("2.1.0", "2.0.0")  # 1 (v1 > v2)
```

**Exception**:
- `VersionError` - Raised when version format is invalid during comparison

**Created by**: Issue #406 (Shared infrastructure building)

### Other Utility Modules

- `config.py` - Configuration management
- `format.py` - Text formatting utilities
- `fs.py` - Filesystem operations
- `git.py` - Git command wrappers
- `test.py` - Testing utilities
- `validation.py` - Input validation helpers

## Design Principles

1. **Single Responsibility** - Each module has one clear purpose
2. **Type Safety** - All functions have type hints
3. **Error Handling** - Graceful degradation and clear error messages
4. **Documentation** - Docstrings for all public functions
5. **Testing** - Unit tests in `_scripts/tests/`

## Testing

**Test suite**:
- `.claude/skills/_scripts/tests/test_sync_utils.py` (246 lines) - sync.py tests
- `.claude/skills/_scripts/tests/test_version.py` (232 lines) - version.py tests

**Run tests**:
```bash
cd .claude/skills/_scripts
uv run -m pytest tests/
```

**Coverage**: Core sync functions, version validation, framework-only filtering, edge cases

## Related ADRs

- **ADR-014**: Skill Implementation Patterns - Modular documentation standard
- **ADR-016**: Specific implementation for eval-plan modular structure

## Related Issues

- **Issue #406**: Shared infrastructure building - Created version.py module
- **Issue #405**: P1 Skills optimization - 4 skills refactored
- **Issue #418**: Skill 1 (update-skills) - Created sync.py module
- **Issue #401**: Framework-only filtering - Preserved in sync.py

## Maintenance

**When adding new shared utilities**:
1. Follow single responsibility principle
2. Add type hints to all functions
3. Write comprehensive docstrings
4. Create unit tests in `tests/` directory
5. Update this README.md
6. Reference from skills using:
   ```python
   sys.path.insert(0, '.claude/skills/_scripts')
   from utils.module_name import function_name
   ```

**When updating existing utilities**:
1. Update function docstrings
2. Update or add unit tests
3. Check all skills using the utility (use grep)
4. Test affected skills end-to-end
5. Update version number in affected SKILL.md files

---

**Created**: 2026-03-30 (Issue #422)
**Maintained by**: Framework developers
**Status**: Production
