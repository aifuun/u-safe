# manage-adrs Test Suite

Comprehensive test suite for the manage-adrs skill, following ADR-020 testing documentation standards.

## Overview

This test suite validates manage-adrs functionality across 5 categories:

| Category | Tests | Purpose |
|----------|-------|---------|
| **Functional** | 8 tests | Core "What it does" features (create, list, show, validate) |
| **Arguments** | 12 tests | Argument parsing and validation |
| **Safety** | 10 tests | Safety mechanisms (prevent overwrites, validate permissions) |
| **Error Handling** | 9 tests | Error scenarios and recovery |
| **Integration** | 9 tests | End-to-end workflows |

**Total**: 48 tests

**Target Coverage**: ≥ 80% (per ADR-015)

## Quick Start

```bash
# Navigate to skill directory
cd .claude/skills/manage-adrs

# Activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov --cov-report=term-missing
```

## Test Structure

```
tests/
├── __init__.py                    # Empty marker file
├── conftest.py                    # Shared fixtures (10 fixtures)
├── pytest.ini                     # pytest configuration
├── test_functional.py             # Core feature tests (8 tests)
├── test_arguments.py              # Argument validation (12 tests)
├── test_safety.py                 # Safety mechanisms (10 tests)
├── test_error_handling.py         # Error scenarios (9 tests)
├── test_integration.py            # End-to-end workflows (9 tests)
└── README.md                      # This file
```

## Running Tests

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test File

```bash
pytest tests/test_functional.py
pytest tests/test_integration.py
```

### Run by Marker

```bash
# Functional tests only
pytest tests/ -m functional

# Safety tests only
pytest tests/ -m safety

# Integration tests only
pytest tests/ -m integration

# Skip slow tests
pytest tests/ -m "not slow"
```

### Run Specific Test

```bash
pytest tests/test_functional.py::test_create_adr_basic
pytest tests/test_integration.py::test_complete_adr_lifecycle
```

### Verbose Output

```bash
pytest tests/ -v
```

### Stop on First Failure

```bash
pytest tests/ -x
```

### Run Last Failed Tests

```bash
pytest tests/ --lf
```

## Coverage

### Generate Coverage Report

```bash
# Terminal report with missing lines
pytest tests/ --cov --cov-report=term-missing

# HTML report
pytest tests/ --cov --cov-report=html
open htmlcov/index.html
```

### Coverage Goals

| Component | Target | Command |
|-----------|--------|---------|
| Overall | ≥ 80% | `pytest --cov` |
| Core scripts | ≥ 85% | `pytest --cov=scripts/` |
| Edge cases | 100% | `pytest -m safety` |

## Test Markers

Tests are organized with pytest markers for selective execution:

```ini
# From pytest.ini
markers =
    functional: Functional tests for core "What it does" features
    arguments: Tests for argument parsing and validation
    safety: Tests for safety mechanisms
    error: Tests for error handling
    integration: Integration tests for end-to-end workflows
    slow: Tests that take longer to run
```

### Usage Examples

```bash
# Run only functional tests
pytest -m functional

# Run functional + argument tests
pytest -m "functional or arguments"

# Run everything except slow tests
pytest -m "not slow"

# Run safety + error tests
pytest -m "safety or error"
```

## Fixtures

Shared test fixtures in `conftest.py`:

| Fixture | Purpose | Usage |
|---------|---------|-------|
| `temp_dir` | Temporary directory for test files | `def test_example(temp_dir):` |
| `mock_profile_basic` | Basic project profile without pillars | `def test_example(mock_profile_basic):` |
| `mock_profile_with_pillars` | Profile with active pillars | `def test_example(mock_profile_with_pillars):` |
| `mock_adr_template` | ADR template content | `def test_example(mock_adr_template):` |
| `mock_existing_adr` | Single valid ADR file | `def test_example(mock_existing_adr):` |
| `mock_adrs_directory` | Directory with 3 ADRs | `def test_example(mock_adrs_directory):` |
| `mock_empty_adrs_directory` | Empty ADRs directory | `def test_example(mock_empty_adrs_directory):` |
| `mock_invalid_adr` | Invalid ADR structure | `def test_example(mock_invalid_adr):` |
| `create_test_adr()` | Helper to create test ADR | `create_test_adr(dir, 1, "Title")` |

## Test Categories

### 1. Functional Tests (test_functional.py)

Tests core features of manage-adrs:

- **test_create_adr_basic** - Create basic ADR
- **test_list_adrs_empty** - List empty directory
- **test_list_adrs_multiple** - List multiple ADRs
- **test_show_adr_content** - Show ADR content
- **test_validate_adr_valid** - Validate valid ADR
- **test_validate_adr_invalid** - Validate invalid ADR
- **test_create_adr_with_custom_template** - Custom template usage
- **test_list_adrs_sorted_by_number** - Verify sorting

**Coverage**: Create, list, show, validate commands

### 2. Argument Tests (test_arguments.py)

Tests argument parsing and validation:

- Command validation (valid/invalid)
- Required arguments enforcement
- Optional arguments handling
- Flag parsing (--help, --all, --status)
- File path validation

**Coverage**: CLI argument handling

### 3. Safety Tests (test_safety.py)

Tests safety mechanisms:

- **Prevent overwrites** - Existing ADR protection
- **Permission validation** - Read-only directory handling
- **Path sanitization** - Special character filtering
- **Path traversal prevention** - Security validation
- **Atomic writes** - No partial files on failure
- **Required sections** - Structure enforcement

**Coverage**: Data protection, filesystem safety

### 4. Error Handling Tests (test_error_handling.py)

Tests error scenarios:

- **Missing files** - Clear error messages
- **Invalid templates** - Template not found errors
- **Disk full** - Graceful degradation
- **Malformed content** - YAML/structure errors
- **Interrupted operations** - Cleanup verification
- **Informative errors** - Resolution steps included

**Coverage**: Error messages, recovery mechanisms

### 5. Integration Tests (test_integration.py)

Tests end-to-end workflows:

- **Complete lifecycle** - Create → list → show → validate
- **Multiple ADRs** - Batch operations
- **Profile-aware creation** - Pillar integration
- **Index generation** - INDEX.md creation
- **Batch validation** - Validate all ADRs
- **Update workflows** - Status changes
- **Auto-numbering** - Sequential number assignment
- **Search functionality** - Keyword search

**Coverage**: Real-world usage patterns

## Continuous Integration

Add to `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m venv .venv
          source .venv/bin/activate
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          source .venv/bin/activate
          pytest .claude/skills/manage-adrs/tests/ --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Troubleshooting

### Import Errors

```bash
# Error: ModuleNotFoundError: No module named 'scripts'
# Fix: Run from skill directory
cd .claude/skills/manage-adrs
pytest tests/
```

### Virtual Environment Issues

```bash
# Error: pytest not found
# Fix: Activate virtual environment
source .venv/bin/activate
pip install pytest pytest-cov
```

### Permission Errors

```bash
# Error: Permission denied on temp directories
# Fix: Check directory permissions
chmod 755 .claude/skills/manage-adrs/tests/
```

### Coverage Not Generating

```bash
# Error: No coverage data
# Fix: Install pytest-cov
pip install pytest-cov

# Verify installation
pytest --version
```

## Best Practices

1. **Run tests before commits** - Ensure changes don't break functionality
2. **Add tests for new features** - Maintain coverage ≥ 80%
3. **Use markers** - Organize tests by category
4. **Keep tests independent** - Each test should work in isolation
5. **Mock external dependencies** - Use fixtures for filesystem operations
6. **Test edge cases** - Include error scenarios, not just happy paths
7. **Document test purpose** - Clear docstrings for each test

## Related Documentation

- [ADR-015: Python Testing Environment](../../../../docs/ADRs/015-python-testing-environment.md) - Testing standards
- [ADR-020: Skill Testing Documentation Standard](../../../../docs/ADRs/020-skill-testing-documentation-standard.md) - Test documentation guide
- [manage-adrs SKILL.md](../SKILL.md) - Skill documentation

---

**Version**: 1.0.0
**Last Updated**: 2026-04-07
**Compliance**: ADR-015 ✅ | ADR-020 ✅
