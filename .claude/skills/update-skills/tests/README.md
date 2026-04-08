# update-skills Tests

Complete test suite for the update-skills synchronization skill, following ADR-015 Python testing standards.

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures
├── test_complete_replacement.py   # Default mode tests
├── test_incremental_sync.py       # Incremental mode tests
├── test_arguments.py              # Parameter validation
├── test_safety.py                 # Safety checks
├── test_error_handling.py         # Error scenarios
└── README.md                      # This file
```

## Running Tests

### Run All Tests

```bash
# From project root
pytest .claude/skills/update-skills/tests/

# Or activate venv first
source .venv/bin/activate
pytest .claude/skills/update-skills/tests/
```

### Run Specific Test File

```bash
pytest .claude/skills/update-skills/tests/test_complete_replacement.py
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=.claude/skills/update-skills .claude/skills/update-skills/tests/

# HTML coverage report
pytest --cov=.claude/skills/update-skills --cov-report=html .claude/skills/update-skills/tests/
open htmlcov/index.html
```

### Run by Marker

```bash
# Run only unit tests
pytest -m unit .claude/skills/update-skills/tests/

# Run only integration tests
pytest -m integration .claude/skills/update-skills/tests/
```

## Test Categories

### 1. Complete Replacement Tests (`test_complete_replacement.py`)

Tests for default sync mode (complete directory replacement):

- Directory deletion
- Complete copy operation
- Subdirectories inclusion (_scripts, _shared, _templates)
- Sync reporting

**Based on**: SKILL.md "What it does" + "Sync Modes - Default Mode"

### 2. Incremental Sync Tests (`test_incremental_sync.py`)

Tests for `--incremental` mode:

- Source/target skill scanning
- Version comparison (NEW, NEWER, OLDER, SAME, CONFLICT)
- Selective sync (`--skills` parameter)
- Version conflict detection

**Based on**: SKILL.md "Sync Modes - Incremental Mode" + "Comparison Logic"

### 3. Argument Validation Tests (`test_arguments.py`)

Parameter validation tests:

- Missing required arguments
- `--dry-run` mode
- `--incremental` flag
- `--skills` filter
- `--skip-validation` flag
- Invalid parameter combinations

**Based on**: SKILL.md "Arguments"

### 4. Safety Tests (`test_safety.py`)

Pre-flight checks and safety validations:

- Source path existence
- Target path writability
- Dry-run doesn't modify files
- Version format validation
- File permission preservation

**Based on**: SKILL.md "Safety Features"

### 5. Error Handling Tests (`test_error_handling.py`)

Error scenario testing:

- Source path not found
- Invalid parameter combinations
- Version conflicts (incremental mode)
- Permission errors
- User-friendly error messages

**Based on**: SKILL.md "Error Handling"

## Shared Fixtures

From `conftest.py`:

- `temp_source_dir`: Temporary source directory with skills
- `temp_target_dir`: Temporary target directory
- `mock_skill_with_version`: Create skill content with version
- `create_skill_structure`: Create skill directory structure
- `assert_directory_synced`: Verify sync correctness

## Coverage Target

**Target**: 80%+ coverage of core functionality

**Focus areas**:
- Complete replacement mode (P0)
- Argument parsing (P0)
- Error handling (P0)
- Safety checks (P1)
- Incremental mode (P1)

## Writing New Tests

### Test Naming Convention

```python
def test_<feature>_<scenario>_<expected_result>():
    """One-line description of what this test verifies."""
    # Test implementation
```

### Example

```python
def test_sync_deletes_target_directory_before_copy():
    """Verify complete replacement deletes target .claude/skills/ first."""
    # Arrange
    source = temp_source_dir()
    target = create_existing_target()

    # Act
    sync_skills(source, target)

    # Assert
    assert target_was_replaced_not_merged(target)
```

### Docstring Requirements

Every test MUST have a docstring explaining:
1. What is being tested
2. Why it matters (maps to SKILL.md section)
3. Expected behavior

## Debugging Failed Tests

```bash
# Verbose output
pytest -v .claude/skills/update-skills/tests/

# Stop on first failure
pytest -x .claude/skills/update-skills/tests/

# Show local variables
pytest -l .claude/skills/update-skills/tests/

# Run specific test
pytest .claude/skills/update-skills/tests/test_complete_replacement.py::test_sync_deletes_target
```

## References

- **SKILL.md**: Primary specification for test extraction
- **ADR-015**: Python testing environment standards
- **docs/TESTING.md**: Project-wide testing guide
- **pytest.ini**: Project pytest configuration

## Continuous Integration

Tests run automatically on:
- Pull request creation
- Push to main branch
- Manual workflow trigger

See `.github/workflows/test.yml` for CI configuration.
