# Review Skill Test Suite

Complete test suite for the review skill, compliant with ADR-020 standards.

## Overview

This test suite provides comprehensive coverage of the review skill based on test cases extracted directly from the SKILL.md documentation.

**Test Structure** (ADR-020 compliant):
- `test_functionality.py` - Based on "What it does" (8 test classes, ~25 tests)
- `test_arguments.py` - Based on "Arguments" (3 test classes, ~9 tests)
- `test_safety.py` - Based on "Safety Features" (5 test classes, ~17 tests)
- `test_errors.py` - Based on "Error Handling" (5 test classes, ~15 tests)
- `test_integration.py` - Based on "Usage Examples" (4 test classes, ~10 tests)

**Total**: ~76 test placeholders covering all critical functionality

## Quick Start

```bash
# Navigate to tests directory
cd .claude/skills/review/tests

# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Running Tests

### All Tests

```bash
pytest
```

### By Category

```bash
# Functionality tests only
pytest test_functionality.py
pytest -m functional

# Argument tests
pytest test_arguments.py
pytest -m arguments

# Safety tests
pytest test_safety.py
pytest -m safety

# Error handling tests
pytest test_errors.py
pytest -m errors

# Integration tests
pytest test_integration.py
pytest -m integration
```

### Coverage Analysis

```bash
# Generate coverage report
pytest --cov --cov-report=term-missing

# HTML coverage report
pytest --cov --cov-report=html
open htmlcov/index.html
```

## Test Structure

### Functionality Tests (test_functionality.py)

Based on "What it does" - 8 core capabilities:

1. **Quality Gates** - Types, tests, linting (30 points)
2. **Architecture Validation** - Pattern compliance (25 points)
3. **Version Update Checks** - SKILL.md version tracking
4. **Pillar Compliance** - Profile-based checks (20 points)
5. **ADR Compliance** - Architecture decisions (10 points)
6. **Security Vulnerabilities** - Common issues (10 points)
7. **Performance Issues** - Algorithm efficiency (5 points)
8. **Status File Generation** - Integration with /finish-issue

### Argument Tests (test_arguments.py)

Based on "Arguments" - Parameter validation:

1. **Argument Parsing** - --strict, --mode=auto, --files
2. **Invalid Arguments** - Error handling
3. **Argument Defaults** - Default behavior verification

### Safety Tests (test_safety.py)

Based on "Safety Features" - 5 safety mechanisms:

1. **Read-Only Operations** - No file modifications
2. **Dynamic Configuration Detection** - Adaptive checks
3. **Graceful Degradation** - Partial failure handling
4. **Smart Strategy Selection** - Change-size based strategy
5. **Status File Validation** - Atomic writes, validity window

### Error Handling Tests (test_errors.py)

Based on "Error Handling" - 5 error categories:

1. **Configuration Errors** - Missing rules, corrupt files
2. **GitHub API Errors** - Rate limits, authentication
3. **File System Errors** - Permissions, missing files
4. **Scoring Calculation Errors** - Edge cases
5. **Recovery Mechanisms** - Retry, fallback, clear messages

### Integration Tests (test_integration.py)

Based on "Usage Examples" - 4 real-world scenarios:

1. **Review Current Changes** - Basic workflow
2. **Goal Coverage Failure** - Incomplete implementation
3. **Skill Version Not Updated** - Version tracking
4. **End-to-End Workflow** - Complete integration

## Implementation Status

**Current**: Test structure and placeholders created (Issue #522)

**Next Steps**:
1. Implement test logic for each placeholder
2. Add mock objects for Claude Code tool interactions
3. Create test fixtures for common scenarios
4. Achieve target coverage (>60% required, 80%+ goal)

## Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| Functionality | 80%+ | TBD |
| Arguments | 90%+ | TBD |
| Safety | 85%+ | TBD |
| Errors | 75%+ | TBD |
| Integration | 70%+ | TBD |
| **Overall** | **80%+** | **TBD** |

## ADR Compliance

This test suite follows:
- **ADR-020**: Skill 测试驱动文档标准
  - ✅ Tests extracted from SKILL.md sections
  - ✅ Direct mapping: documentation → test cases
  - ✅ Complete coverage of test baseline sections

- **ADR-015**: Python 测试环境标准
  - ✅ pytest as test framework
  - ✅ Coverage reporting with pytest-cov
  - ✅ Standard directory structure

## Related Documentation

- [review SKILL.md](../SKILL.md) - Source documentation
- [ADR-020](../../../../docs/ADRs/020-skill-testing-documentation-standard.md) - Testing standard
- [ADR-015](../../../../docs/ADRs/015-python-testing-environment.md) - Python testing environment

---

**Version**: 1.0.0
**Created**: 2026-04-07
**Issue**: #522
