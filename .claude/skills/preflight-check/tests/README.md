# Preflight Check Tests

## Test Scenarios

### 1. First-time Run (Permissions Unconfigured)
**Setup**: Remove `.claude/settings.json`
**Expected**: Auto-fix → Configure permissions → Pass
**Command**: `python scripts/preflight.py`

### 2. Git Working Directory Dirty
**Setup**: Create uncommitted changes
**Expected**: Auto-fix → Git stash → Pass
**Command**: `python scripts/preflight.py`

### 3. node_modules Missing
**Setup**: Remove `node_modules/` directory
**Expected**: Auto-fix → npm install → Pass
**Command**: `python scripts/preflight.py`

### 4. GitHub CLI Not Authenticated
**Setup**: `gh auth logout`
**Expected**: Blocked → Prompt "gh auth login"
**Command**: `python scripts/preflight.py`

### 5. Issue Does Not Exist
**Setup**: N/A (manual test)
**Expected**: Blocked → Prompt "Check issue number"
**Command**: (Tested in work-issue context)

## Running Tests

```bash
# Run all automated tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_permissions.py

# Manual testing
python scripts/preflight.py
```

## Test Coverage

- [ ] Permissions configuration check
- [ ] Framework directories check
- [ ] Git environment check
- [ ] GitHub CLI check
- [ ] Project structure check
- [ ] Dependencies check
- [ ] Quality tools check
- [ ] Auto-fix P1 (fast) mechanisms
- [ ] Auto-fix P2 (slow) mechanisms
- [ ] Manual fix (P3) reporting
- [ ] Parallel execution optimization
- [ ] Report formatting

## TODO

<!-- TODO: Add test coverage for edge cases and error scenarios -->
- Implement pytest test suite
- Add mock objects for subprocess calls
- Test error handling paths
- Measure parallel execution performance
