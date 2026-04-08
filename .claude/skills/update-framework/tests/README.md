## update-framework Test Suite

Comprehensive test suite for the update-framework skill, following ADR-020 Python testing standards.

## Overview

This test suite validates the update-framework skill's functionality, including:

- **Functional tests** (8 tests): Core sync operations
- **Parameter tests** (4 tests): Argument validation
- **Safety tests** (5 tests): Security mechanisms
- **Error handling tests** (5 tests): Exception scenarios
- **Integration tests** (3 tests): End-to-end workflows

**Total**: 25 tests | **Coverage Target**: 80%+

## Quick Start

```bash
# Run all tests
pytest .claude/skills/update-framework/tests/

# Run with coverage
pytest .claude/skills/update-framework/tests/ --cov

# Run specific test file
pytest .claude/skills/update-framework/tests/test_functional.py

# Run by marker
pytest .claude/skills/update-framework/tests/ -m functional
pytest .claude/skills/update-framework/tests/ -m safety
```

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures (tmp_framework, tmp_project, etc.)
├── test_functional.py          # 8 functional tests
├── test_parameters.py          # 4 parameter validation tests
├── test_safety.py              # 5 security tests
├── test_error_handling.py      # 5 error handling tests
├── test_integration.py         # 3 integration tests
└── README.md                   # This file
```

## Test Categories

### Functional Tests (8 tests)

Tests core "What it does" functionality:

- `test_full_sync_pillars_and_skills` - Complete framework sync
- `test_pillars_only_sync` - Sync only Pillars (--only pillars)
- `test_skills_only_sync` - Sync only Skills (--only skills)
- `test_empty_directory_handling` - Initialize empty project
- `test_conflicting_files_handling` - Overwrite existing files
- `test_automatic_backup_creation` - Backup before sync
- `test_bidirectional_sync` - Both framework→project and project→framework
- `test_profile_awareness` - Profile-aware filtering

### Parameter Tests (4 tests)

Tests argument validation:

- `test_missing_source_path` - Error when framework path not found
- `test_missing_target_path` - Error when target not specified
- `test_invalid_path_format` - Reject malformed paths
- `test_conflicting_flags` - Error on --only and --skip together

### Safety Tests (5 tests)

Tests security mechanisms:

- `test_path_traversal_prevention` - Block ../ attacks
- `test_symlink_handling` - Safe symlink handling
- `test_permission_validation` - Check write permissions
- `test_disk_space_check` - Verify adequate disk space
- `test_backup_integrity` - Verify backup completeness

### Error Handling Tests (5 tests)

Tests exception scenarios:

- `test_source_not_found` - Handle missing framework directory
- `test_target_permission_denied` - Handle read-only target
- `test_git_conflict_handling` - Detect and report conflicts
- `test_partial_sync_recovery` - Rollback on failure
- `test_network_interruption` - Handle network errors (if applicable)

### Integration Tests (3 tests)

Tests end-to-end workflows:

- `test_integration_with_manage_claude_md` - Update CLAUDE.md after sync
- `test_integration_with_init_docs` - Use framework templates
- `test_full_project_initialization` - Complete project setup

## Running Tests

### All Tests

```bash
# Run all 25 tests
pytest .claude/skills/update-framework/tests/

# With verbose output
pytest .claude/skills/update-framework/tests/ -v

# With coverage report
pytest .claude/skills/update-framework/tests/ --cov --cov-report=term-missing
```

### By Category

```bash
# Functional tests only
pytest .claude/skills/update-framework/tests/ -m functional

# Safety tests only
pytest .claude/skills/update-framework/tests/ -m safety

# Error handling tests only
pytest .claude/skills/update-framework/tests/ -m error_handling

# Integration tests only
pytest .claude/skills/update-framework/tests/ -m integration
```

### By File

```bash
# Run specific test file
pytest .claude/skills/update-framework/tests/test_functional.py
pytest .claude/skills/update-framework/tests/test_parameters.py
pytest .claude/skills/update-framework/tests/test_safety.py
```

### Single Test

```bash
# Run specific test function
pytest .claude/skills/update-framework/tests/test_functional.py::test_full_sync_pillars_and_skills
```

## Coverage

Generate HTML coverage report:

```bash
# Generate coverage report
pytest .claude/skills/update-framework/tests/ --cov --cov-report=html

# Open in browser
open htmlcov/index.html
```

**Coverage Target**: 80%+ (ADR-020 standard for core utilities)

## Fixtures

Shared test fixtures from `conftest.py`:

- **tmp_framework**: Temporary framework directory with sample content
- **tmp_project**: Temporary target project directory
- **framework_and_project**: Both framework and project directories
- **empty_project**: Empty project (no .claude/ directory)
- **mock_skill_invocation**: Mock Skill() tool calls
- **mock_git**: Mock git commands
- **clean_state_files**: Auto-cleanup state files (runs automatically)

### Example Usage

```python
def test_example(framework_and_project):
    """Test using framework and project fixtures."""
    framework = framework_and_project["framework"]
    project = framework_and_project["project"]

    # Use fixtures for testing
    assert (framework / ".claude/pillars").exists()
    assert (project / ".claude").exists()
```

## Test Markers

Tests are marked for selective execution:

- `@pytest.mark.functional` - Functional tests (8 tests)
- `@pytest.mark.parameters` - Parameter tests (4 tests)
- `@pytest.mark.safety` - Safety tests (5 tests)
- `@pytest.mark.error_handling` - Error handling (5 tests)
- `@pytest.mark.integration` - Integration tests (3 tests)

## Writing New Tests

Follow ADR-020 AAA pattern:

```python
@pytest.mark.functional
def test_new_feature(tmp_framework: Path, tmp_project: Path):
    """Test description following docstring standards.

    Arrange:
        - Setup preconditions
    Act:
        - Execute action
    Assert:
        - Verify outcomes
    """
    # Arrange
    framework = tmp_framework
    project = tmp_project

    # Act
    result = perform_action(framework, project)

    # Assert
    assert result.success
    assert (project / "expected-file.md").exists()
```

## Troubleshooting

### Tests Fail Due to Permissions

```bash
# Unix-like systems may have permission issues
# Fix with:
chmod -R u+w .claude/skills/update-framework/tests/
```

### Fixtures Not Found

```bash
# Ensure running from project root
cd /path/to/ai-dev
pytest .claude/skills/update-framework/tests/
```

### Coverage Not Calculated

```bash
# Install coverage plugin
pip install pytest-cov

# Run with coverage
pytest .claude/skills/update-framework/tests/ --cov
```

## CI/CD Integration

Add to GitHub Actions workflow:

```yaml
name: Test update-framework

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          pytest .claude/skills/update-framework/tests/ --cov --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Best Practices

1. **Use fixtures** - Reuse tmp_framework and tmp_project fixtures
2. **Mark tests** - Add appropriate @pytest.mark decorators
3. **Follow AAA** - Arrange-Act-Assert pattern
4. **Clear docstrings** - Explain what test validates
5. **Fast tests** - Each test should run < 1 second
6. **Isolated tests** - No shared state between tests
7. **Descriptive names** - test_what_is_being_tested format

## Related Documentation

- [ADR-020](../../../../docs/ADRs/020-python-testing-environment.md) - Python testing standards
- [ADR-015](../../../../docs/ADRs/015-python-testing-environment.md) - Python testing environment
- [../SKILL.md](../SKILL.md) - update-framework skill documentation

---

**Version**: 1.0.0
**Last Updated**: 2026-04-07
**Issue**: #528
