# Manage-Rules Architecture Document

## Overview

This document describes the architecture for manage-rules v3.0.0 refactoring to ADR-014 compliant script-based pattern.

## Current State (v2.0.0)

**Structure**: ~800-line SKILL.md with embedded workflow logic

**Issues**:
- Logic embedded in markdown (difficult to test)
- No unit test coverage
- ADR-014 score: 9/14 (needs script extraction)
- Template filtering + framework-only filtering logic untested

**Workflow**:
1. Load profile from `docs/project-profile.md`
2. Scan templates in `.claude/guides/rules/templates/`
3. Filter by whitelist (`rules.include` from profile)
4. Filter by exclude patterns (`rules.exclude` from profile)
5. Copy filtered templates to `.claude/rules/`
6. Report results

## Target State (v3.0.0)

**Structure**: Script-based pattern (ADR-014)

```
.claude/skills/manage-rules/
├── SKILL.md (< 500 lines)           # AI instructions
├── scripts/
│   └── generate_rules.py (new)      # Core logic
└── tests/
    └── test_rule_generator.py (new) # Unit tests (>60% coverage)
```

**Benefits**:
- ✅ Testable Python code
- ✅ >60% test coverage
- ✅ ADR-014 compliant
- ✅ Maintainable architecture
- ✅ Reusable RuleGenerator class

## Architecture Design

### RuleGenerator Class

**Purpose**: Orchestrate rule generation workflow

**Methods**:

```python
class RuleGenerator:
    def __init__(self, profile: Optional[str] = None, instant: bool = True):
        """Initialize with optional profile override and execution mode"""
        self.profile = profile
        self.instant = instant

    def detect_profile(self) -> str:
        """
        Detect project profile from docs/project-profile.md

        Returns:
            str: Profile name (tauri, nextjs-aws, minimal)

        Raises:
            ProfileNotFoundError: If profile file missing
            ProfileInvalidError: If YAML syntax invalid
        """
        pass

    def load_profile_config(self, profile: str) -> dict:
        """
        Load profile configuration with rules whitelist

        Args:
            profile: Profile name

        Returns:
            dict: Profile config with 'rules': {'include': [...], 'exclude': [...]}

        Raises:
            ProfileConfigError: If profile config invalid
        """
        pass

    def filter_templates(self, config: dict) -> List[Path]:
        """
        Filter templates by profile whitelist and exclude patterns

        Args:
            config: Profile configuration dict

        Returns:
            List[Path]: Filtered template paths

        Logic:
            1. Scan .claude/guides/rules/templates/
            2. Apply include whitelist
            3. Apply exclude patterns (fnmatch)
            4. Return filtered list
        """
        pass

    def filter_framework_only_skills(self, templates: List[Path]) -> List[Path]:
        """
        Filter out framework-only templates (Issue #401)

        Args:
            templates: List of template paths

        Returns:
            List[Path]: Templates without framework-only items

        Logic:
            1. For each template, read YAML frontmatter
            2. Check for 'framework-only: true' field
            3. Exclude templates with framework-only=true
            4. Return filtered list

        Note: This preserves Issue #401 functionality
        """
        pass

    def generate_rules(self, templates: List[Path]) -> int:
        """
        Generate .claude/rules/ files from filtered templates

        Args:
            templates: Filtered template paths

        Returns:
            int: Count of generated rule files

        Logic:
            1. Create .claude/rules/ structure
            2. Copy each template to appropriate category subdirectory
            3. Remove .template suffix from filenames
            4. Return count
        """
        pass
```

### Workflow Orchestration

**Main execution**:

```python
def main(profile: Optional[str] = None, instant: bool = True, dry_run: bool = False):
    """
    Main entry point for rule generation

    Args:
        profile: Optional profile override
        instant: Execute immediately (default True)
        dry_run: Show plan without executing
    """
    generator = RuleGenerator(profile=profile, instant=instant)

    # Step 1: Detect profile
    detected_profile = generator.detect_profile()

    # Step 2: Load config
    config = generator.load_profile_config(detected_profile)

    # Step 3: Filter templates
    templates = generator.filter_templates(config)

    # Step 4: Filter framework-only (Issue #401)
    filtered = generator.filter_framework_only_skills(templates)

    # Step 5: Generate or show plan
    if dry_run:
        show_plan(filtered)
    elif instant:
        count = generator.generate_rules(filtered)
        print(f"✅ Generated {count} rules for profile '{detected_profile}'")

    return filtered
```

### Shared Utilities Extraction

**Target**: `.claude/skills/_scripts/utils/`

#### validation.py

```python
def validate_profile(profile: str) -> bool:
    """
    Validate profile exists and has valid config

    Args:
        profile: Profile name to validate

    Returns:
        bool: True if valid, False otherwise
    """
    pass
```

#### config.py

```python
def load_profile_config(profile: str) -> dict:
    """
    Load profile configuration from docs/project-profile.md

    Args:
        profile: Profile name

    Returns:
        dict: Profile configuration

    Raises:
        ProfileConfigError: If config invalid
    """
    pass
```

## Framework-Only Filtering (Issue #401)

**Context**: Framework management skills (update-framework, update-skills, etc.) should not be copied to target projects during sync.

**Solution**: YAML metadata marking

**Implementation**:

```python
def has_framework_only_marker(template_path: Path) -> bool:
    """
    Check if template has framework-only: true in YAML frontmatter

    Args:
        template_path: Path to template file

    Returns:
        bool: True if framework-only, False otherwise
    """
    with open(template_path, 'r') as f:
        content = f.read()

    # Parse YAML frontmatter
    if content.startswith('---'):
        yaml_end = content.find('---', 3)
        frontmatter = content[3:yaml_end]

        # Check for framework-only field
        import yaml
        metadata = yaml.safe_load(frontmatter)
        return metadata.get('framework-only', False)

    return False


def filter_framework_only_skills(templates: List[Path]) -> List[Path]:
    """Filter out templates with framework-only: true"""
    return [t for t in templates if not has_framework_only_marker(t)]
```

**Usage**: Called automatically during `filter_templates()` workflow

## Testing Strategy

### Unit Tests (>60% Coverage)

**File**: `tests/test_rule_generator.py`

**Test Cases**:

1. **Profile Detection**:
   - `test_detect_profile_from_file()` - Normal case
   - `test_detect_profile_missing_file()` - Error case
   - `test_detect_profile_invalid_yaml()` - Error case

2. **Template Filtering**:
   - `test_filter_by_whitelist()` - Include filtering
   - `test_filter_by_exclude()` - Exclude patterns
   - `test_filter_combined()` - Both filters

3. **Framework-Only Filtering** (Issue #401):
   - `test_filter_framework_only()` - Detect and exclude
   - `test_filter_no_marker()` - Keep templates without marker
   - `test_filter_invalid_yaml()` - Handle parse errors

4. **Rule Generation**:
   - `test_generate_rules()` - Normal case
   - `test_generate_with_subdirs()` - Category structure
   - `test_generate_dry_run()` - Plan mode

**Coverage Target**: >60% (focus on core logic, not error paths)

## Migration Path

### Phase 1: Extract to Script (Task 2.2)
- Create `scripts/generate_rules.py`
- Implement RuleGenerator class
- Preserve framework-only filtering

### Phase 2: Shared Utilities (Task 2.3)
- Extract `validate_profile()` to `_scripts/utils/validation.py`
- Extract `load_profile_config()` to `_scripts/utils/config.py`

### Phase 3: Testing (Task 2.4)
- Write unit tests
- Achieve >60% coverage
- Focus on template filtering and framework-only logic

### Phase 4: Documentation (Task 2.5)
- Simplify SKILL.md to < 500 lines
- Add script invocation examples
- Mark ADR-014 compliance

### Phase 5: Validation (Task 2.6)
- Test with 3 profiles (tauri, nextjs-aws, minimal)
- Verify framework-only filtering
- Create VALIDATION.md report

## Behavioral Compatibility

**CRITICAL**: Must maintain identical behavior to v2.0.0

**Verification**:
1. Same template filtering logic (whitelist + exclude)
2. Same output structure (`.claude/rules/` with categories)
3. Framework-only filtering preserved (Issue #401)
4. Same dry-run vs instant modes
5. Same profile detection logic

**No Breaking Changes**:
- ✅ Same command-line arguments
- ✅ Same output format
- ✅ Same file locations
- ✅ Same error messages

## Performance Considerations

**Current performance**: ~2 seconds for 34 rules

**Target performance**: ≤ 3 seconds (acceptable overhead for testability)

**Optimizations**:
- Cache profile config reads
- Batch file operations
- Avoid unnecessary YAML parsing

## Error Handling

**Error Categories**:
1. Profile not found → Clear error message + suggested fix
2. Invalid YAML → Show line number + syntax error
3. Template not found → List available templates
4. Permission denied → Check file permissions
5. Framework-only parse error → Log warning, skip template

**Graceful Degradation**:
- If framework-only check fails → Log warning, include template
- If exclude pattern invalid → Log warning, skip pattern
- If category unknown → Use "other" category

## Future Enhancements (Not in v3.0.0)

1. **Incremental updates** - Only copy changed templates
2. **Template validation** - Lint templates before copying
3. **Profile inheritance** - Base profiles with overrides
4. **Custom template sources** - Support external template repos
5. **Rule conflict detection** - Warn on duplicate rules

---

**Version**: 3.0.0 (Draft)
**Created**: 2026-03-30
**Status**: Design Complete
**Next**: Implementation (Task 2.2)
