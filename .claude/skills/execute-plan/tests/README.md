# execute-plan Test Suite

> Comprehensive tests for execute-plan skill based on ADR-020 testing standards

## Overview

This test suite validates the execute-plan skill across multiple dimensions following ADR-020 test-driven documentation approach.

**Test Coverage**: Targets >60% code coverage

**Test Categories**:
- **Functional Tests** (test_functional.py): Core "What it does" functionality
- **Argument Tests** (test_arguments.py): Parameter validation and handling
- **Safety Tests** (test_safety.py): Safety mechanisms and error prevention

## Running Tests

### Quick Start

```bash
# Run all tests
cd .claude/skills/execute-plan
pytest tests/

# Run with coverage
pytest tests/ --cov --cov-report=html

# Run specific category
pytest tests/test_functional.py
pytest tests/ -m functional
pytest tests/ -m safety
```

### Test Markers

Tests are organized with markers for selective execution:

```bash
# By test type
pytest -m unit            # Unit tests only
pytest -m integration     # Integration tests only

# By category
pytest -m functional      # Functional tests (What it does)
pytest -m safety          # Safety feature tests
pytest -m error           # Error handling tests
```

## Test Structure

### conftest.py
Provides reusable fixtures:
- `temp_dir`: Isolated temporary directory
- `mock_plan_simple`: Simple 3-task plan
- `mock_plan_complex`: Multi-phase plan with sub-tasks
- `mock_plan_with_dependencies`: Plan with explicit dependencies
- `mock_git_env`: Mocked git environment
- `mock_task_tracker`: Task management simulation
- `mock_plan_file`: Plan file in temp directory
- `mock_state_file`: State file for resume testing

### test_functional.py (7 tests)
Based on "What it does" from SKILL.md:

1. `test_load_plan_file`: Load plan from file path
2. `test_extract_tasks_from_plan`: Extract tasks from markdown
3. `test_create_todos_from_tasks`: Create todos with dependencies
4. `test_sequential_task_execution`: Execute tasks respecting dependencies
5. `test_validate_task_completion`: Mark tasks completed
6. `test_prepare_deliverables_summary`: Generate review summary
7. `test_complete_workflow_end_to_end`: Full integration test

### test_arguments.py (6 tests)
Based on "Arguments" from SKILL.md:

1. `test_issue_number_from_branch`: Extract issue number from branch name
2. `test_resume_flag_loads_checkpoint`: Load saved state for resume
3. `test_skip_task_marks_completed_without_execution`: Skip task functionality
4. `test_dry_run_shows_preview_without_changes`: Dry-run mode validation
5. `test_invalid_arguments_handling`: Invalid argument detection
6. `test_auto_detect_from_active_plan`: Auto-detect issue from plan file

### test_safety.py (7 tests)
Based on "Safety Features" from SKILL.md:

1. `test_plan_structure_validation_empty_plan`: Reject empty plans
2. `test_plan_structure_validation_malformed_markdown`: Reject malformed plans
3. `test_task_dependency_no_cycles`: Circular dependency detection
4. `test_error_recovery_save_checkpoint`: Save state on failure
5. `test_failure_limits_max_retries`: Max retry limit enforcement
6. `test_state_file_cleanup_on_completion`: Cleanup after success
7. `test_stale_state_warning`: Warn on old state files (>24h)

## Coverage Goals

| Component | Target | Status |
|-----------|--------|--------|
| Core logic | 80%+ | 🎯 |
| Argument handling | 70%+ | 🎯 |
| Safety mechanisms | 75%+ | 🎯 |
| Overall | 60%+ | ✅ |

## Adding New Tests

When adding tests, follow ADR-020 principles:

1. **Extract from SKILL.md**: Base tests on documented behavior
2. **Use markers**: Tag with appropriate markers (@pytest.mark.unit, etc.)
3. **Use fixtures**: Leverage conftest.py fixtures for consistency
4. **Document clearly**: Add docstring explaining what's tested

Example:
```python
@pytest.mark.functional
@pytest.mark.unit
def test_new_feature(mock_plan_simple):
    \"\"\"Test description based on SKILL.md section\"\"\"
    # Given: Setup
    # When: Action
    # Then: Assertion
    pass
```

## CI/CD Integration

Tests run automatically on:
- Pull requests (all tests)
- Main branch commits (all tests)
- Coverage reports generated and uploaded

See `.github/workflows/test.yml` for CI configuration.

## Troubleshooting

### Tests failing locally?

```bash
# Clean pytest cache
pytest --cache-clear

# Re-install dependencies
pip install -r requirements.txt

# Check Python version (requires 3.8+)
python --version
```

### Coverage not measuring correctly?

```bash
# Ensure .coveragerc exists
# Run with explicit source path
pytest --cov=. --cov-report=term-missing
```

## References

- **ADR-020**: Skill Testing Documentation Standard
- **ADR-015**: Python Testing Environment
- **execute-plan SKILL.md**: Source of test requirements
- **pytest docs**: https://docs.pytest.org/

---

**Last Updated**: 2026-04-07
**Test Count**: 20 tests across 3 files
**Coverage Target**: >60%
