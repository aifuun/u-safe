# manage-claude-md Test Suite

Comprehensive test suite for the manage-claude-md skill following ADR-020 standards.

## Overview

**Test Coverage**: Target ≥60% (ADR-020 requirement)

**Test Categories**:
- **Functional** (6 tests) - Core "What it does" functionality
- **Arguments** (4 tests) - Argument validation and handling
- **Safety** (5 tests) - Safety mechanisms validation

**Total**: 15 tests across 3 files

## Test Structure

```
tests/
├── README.md           # This file
├── pytest.ini          # pytest configuration
├── conftest.py         # Shared fixtures (8 fixtures)
├── test_functional.py  # Functional tests (6 tests)
├── test_arguments.py   # Argument tests (4 tests)
└── test_safety.py      # Safety tests (5 tests)
```

## Running Tests

### Setup Environment

```bash
# Navigate to skill directory
cd .claude/skills/manage-claude-md

# Create virtual environment (if not exists)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

# Install dependencies
pip install pytest pytest-cov
```

### Run All Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov --cov-report=term-missing
```

### Run Specific Categories

```bash
# Run only functional tests
pytest tests/test_functional.py
pytest tests/ -m functional

# Run only argument tests
pytest tests/test_arguments.py
pytest tests/ -m argument

# Run only safety tests
pytest tests/test_safety.py
pytest tests/ -m safety

# Run only unit tests
pytest tests/ -m unit

# Run only integration tests
pytest tests/ -m integration
```

### Coverage Analysis

```bash
# Generate HTML coverage report
pytest tests/ --cov --cov-report=html

# Open coverage report in browser
open htmlcov/index.html  # macOS
# OR
start htmlcov/index.html  # Windows
```

## Test Fixtures

Defined in `conftest.py`:

| Fixture | Purpose | Type |
|---------|---------|------|
| `temp_dir` | Temporary directory for test isolation | Path |
| `mock_claude_md` | Mock CLAUDE.md with skills list | Path |
| `mock_plans_dir` | Mock plans directory (active/archive) | Dict |
| `mock_git_env` | Mock git environment | Dict |
| `mock_skill_files` | Mock skill files in .claude/skills/ | Path |
| `mock_state_files` | Mock status files (.eval-plan-status.json, etc.) | Dict |
| `mock_profile_config` | Mock profile configuration in CLAUDE.md | Path |

## Test Categories Explained

### Functional Tests (test_functional.py)

Tests core functionality described in SKILL.md "What it does" section:

1. **test_update_skills_list** - Update CLAUDE.md skills list from .claude/skills/
2. **test_archive_completed_plans** - Archive completed plans from active to archive
3. **test_generate_health_report** - Generate project health report
4. **test_clean_stale_files** - Clean stale status files (>24h old)
5. **test_instant_mode_workflow** - Complete instant mode workflow
6. **test_configure_profile** - Profile configuration functionality

### Argument Tests (test_arguments.py)

Tests argument handling and validation:

1. **test_instant_flag** - --instant flag triggers instant mode
2. **test_dry_run_flag** - --dry-run shows preview without changes
3. **test_configure_profile_flag** - --configure-profile flag
4. **test_invalid_arguments** - Invalid arguments raise errors

### Safety Tests (test_safety.py)

Tests safety mechanisms:

1. **test_backup_before_modify** - Backups created before modifying CLAUDE.md
2. **test_atomic_file_operations** - Atomic writes prevent partial updates
3. **test_read_only_validation** - Read-only mode doesn't modify files
4. **test_error_recovery** - Graceful recovery from errors
5. **test_dry_run_no_changes** - Dry-run mode makes no actual changes

## Markers

Tests are marked with pytest markers for selective execution:

- `@pytest.mark.unit` - Unit tests (isolated, no external dependencies)
- `@pytest.mark.integration` - Integration tests (multiple components)
- `@pytest.mark.functional` - Tests from "What it does" section
- `@pytest.mark.argument` - Argument handling tests
- `@pytest.mark.safety` - Safety feature tests

## CI/CD Integration

Tests run automatically on:
- Pull requests
- Pushes to main branch
- Manual workflow dispatch

See `.github/workflows/test-manage-claude-md.yml` for configuration.

## Troubleshooting

### Tests not found

```bash
# Verify pytest discovers tests
pytest --collect-only tests/

# Check PYTHONPATH if imports fail
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

### Import errors

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Coverage too low

```bash
# Identify untested code
pytest tests/ --cov --cov-report=term-missing

# Look for "Missing" column in output
# Add tests for uncovered lines
```

## Adding New Tests

1. **Choose appropriate test file**:
   - Core functionality → `test_functional.py`
   - Arguments → `test_arguments.py`
   - Safety → `test_safety.py`

2. **Use existing fixtures**:
   ```python
   def test_my_feature(mock_claude_md, mock_plans_dir):
       # Test implementation
       pass
   ```

3. **Add appropriate markers**:
   ```python
   @pytest.mark.functional
   @pytest.mark.unit
   def test_my_feature():
       pass
   ```

4. **Run and verify**:
   ```bash
   pytest tests/test_functional.py::test_my_feature -v
   ```

## Related Documentation

- [ADR-020: Skill Testing Documentation](../../../../docs/ADRs/020-skill-testing-documentation.md)
- [ADR-015: Python Testing Environment](../../../../docs/ADRs/015-python-testing-environment.md)
- [SKILL.md](../SKILL.md) - Skill implementation guide

---

**Test Suite Version**: 1.0.0
**Last Updated**: 2026-04-07
**Coverage Target**: ≥60%
**Compliance**: ADR-015 ✅ | ADR-020 ✅
