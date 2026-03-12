# Skill Evaluation Usage Guide

> Complete guide to using the skill evaluation system

## Table of Contents

- [Overview](#overview)
- [When to Run Evals](#when-to-run-evals)
- [Running Evaluations](#running-evaluations)
- [Creating Test Cases](#creating-test-cases)
- [Interpreting Results](#interpreting-results)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The skill evaluation system provides automated quality assurance for Claude Code skills following [Anthropic's official best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#build-evaluations-first).

**Key principle**: "Build evaluations BEFORE extensive documentation"

**Current phase**: Phase 1 (Baseline test cases)

## When to Run Evals

### During Development (On-Demand)

Run specific test cases while developing or debugging a skill:

```bash
# Test a specific scenario
python3 .claude/skills/.evals/runner.py .claude/skills/.evals/test-cases/start-issue/basic.json

# Quick validation after changes
python3 .claude/skills/.evals/runner.py .claude/skills/.evals/test-cases/start-issue/*.json
```

**Use case**: Immediate feedback during skill development

### Pre-Commit (Optional)

Add a git hook to run quick smoke tests before committing:

```bash
# .git/hooks/pre-commit
#!/bin/bash
python3 .claude/skills/.evals/runner.py --all --quick
```

**Use case**: Catch regressions before they enter version control

### Pre-Release (Required)

Run full test suite before releasing new framework version:

```bash
# Run all test cases
python3 .claude/skills/.evals/runner.py --all

# Or run by skill
python3 .claude/skills/.evals/runner.py --skill start-issue
python3 .claude/skills/.evals/runner.py --skill finish-issue
python3 .claude/skills/.evals/runner.py --skill execute-plan
```

**Use case**: Comprehensive validation before shipping

### CI/CD (Phase 2)

Automated runs on pull requests and main branch:

```yaml
# .github/workflows/eval-skills.yml (Future)
name: Skill Evaluations
on: [pull_request, push]
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - run: python3 .claude/skills/.evals/runner.py --all
```

**Use case**: Continuous regression testing

## Running Evaluations

### Single Test Case

```bash
# Basic usage
python3 .claude/skills/.evals/runner.py .claude/skills/.evals/test-cases/start-issue/basic.json

# Expected output:
# ❌ FAIL: start-issue-basic  (Phase 1 - structure only)
# Expected behaviors:
#   - Fetches issue #23 details from GitHub
#   - Creates feature branch: feature/23-{kebab-title}
#   ...
```

### All Tests for a Skill (Phase 2)

```bash
python3 .claude/skills/.evals/runner.py --skill start-issue
```

### All Tests (Phase 2)

```bash
python3 .claude/skills/.evals/runner.py --all
```

## Creating Test Cases

### Step 1: Identify Scenario

**Good scenarios to test**:
- ✅ Basic happy path (most common use case)
- ✅ Optional flags (--no-plan, --resume, --dry-run)
- ✅ Error handling (missing issue, invalid input)
- ✅ Edge cases (branch already exists, uncommitted changes)

**Skip scenarios**:
- ❌ Trivial variations (different issue numbers)
- ❌ Implementation details (internal function behavior)

### Step 2: Create JSON File

**File naming**: `{skill-name}/{scenario-name}.json`

**Examples**:
- `start-issue/basic.json` - Happy path
- `start-issue/no-plan.json` - Skip plan generation
- `finish-issue/no-merge.json` - Create PR without merging

### Step 3: Define Test Case

```json
{
  "name": "descriptive-test-name",
  "skills": ["skill-name"],
  "query": "user request as natural language",
  "files": ["optional/test/fixtures.txt"],
  "expected_behavior": [
    "Observable outcome 1",
    "Observable outcome 2",
    "Observable outcome 3"
  ]
}
```

**Required fields**:
- `name`: Unique identifier (kebab-case)
- `skills`: List of skills to invoke
- `query`: User's natural language request
- `expected_behavior`: List of observable outcomes

**Optional fields**:
- `files`: Test fixture files needed
- `assertions`: Specific checks (Phase 2)

### Step 4: Write Expected Behaviors

**Good expected behaviors**:
- ✅ "Creates feature branch: feature/23-{kebab-title}"
- ✅ "Generates plan at .claude/plans/active/issue-23-plan.md"
- ✅ "Pushes branch to remote origin"

**Bad expected behaviors**:
- ❌ "Works correctly" (too vague)
- ❌ "Calls GitHub API" (implementation detail)
- ❌ "Returns success" (not observable)

**Key principle**: Expected behaviors should be **observable outcomes** that a user or automated system can verify.

### Step 5: Validate Test Case

```bash
# Run the test case
python3 .claude/skills/.evals/runner.py .claude/skills/.evals/test-cases/your-skill/scenario.json

# Should pass validation (Phase 1 shows FAIL with structure)
```

### Example: Creating a Test Case

**Scenario**: Test /start-issue with custom branch prefix

```bash
# Create file
cat > .claude/skills/.evals/test-cases/start-issue/custom-prefix.json << 'EOF'
{
  "name": "start-issue-custom-prefix",
  "skills": ["start-issue"],
  "query": "start issue #48 --branch-prefix fix",
  "expected_behavior": [
    "Fetches issue #48 details from GitHub",
    "Creates branch with custom prefix: fix/48-{kebab-title}",
    "Generates implementation plan",
    "Pushes branch to remote origin"
  ]
}
EOF

# Validate
python3 .claude/skills/.evals/runner.py .claude/skills/.evals/test-cases/start-issue/custom-prefix.json
```

## Interpreting Results

### Phase 1 (Current)

All tests show **FAIL** because actual execution is not implemented yet:

```
❌ FAIL: start-issue-basic

Expected behaviors:
  - Fetches issue #23 details from GitHub
  - Creates feature branch: feature/23-{kebab-title}
  ...

Actual behaviors:
  - [Not implemented yet - Phase 1 creates structure only]

Errors:
  - Eval execution not implemented in Phase 1
```

**This is expected** - Phase 1 focuses on infrastructure and test case creation.

### Phase 2+ (Future)

Tests will show **PASS** or **FAIL** based on actual execution:

```
✅ PASS: start-issue-basic
Score: 95/100

Expected behaviors:
  - Fetches issue #23 details from GitHub ✓
  - Creates feature branch: feature/23-{kebab-title} ✓
  ...

Actual behaviors:
  - Fetched issue #23 successfully
  - Created branch feature/23-fix-authentication
  ...
```

## Best Practices

### Test Case Creation

1. **Start with happy path** - Cover basic usage first
2. **Add edge cases gradually** - One scenario per test case
3. **Keep tests focused** - Test one feature/flag per case
4. **Use descriptive names** - Clear what scenario tests
5. **Document expected behaviors clearly** - Observable outcomes

### Test Maintenance

1. **Update tests with skill changes** - Keep in sync
2. **Remove obsolete tests** - Delete when feature removed
3. **Add tests for bug fixes** - Prevent regressions
4. **Review coverage regularly** - Ensure critical paths tested

### Running Tests

1. **Run relevant tests during development** - Fast feedback
2. **Run all tests before committing** - Catch regressions
3. **Run all tests before release** - Comprehensive validation
4. **Don't skip failing tests** - Fix or update them

## Troubleshooting

### Test Case Validation Fails

**Error**: "Missing required field: 'query'"

**Fix**: Add `"query": "..."` to your test case JSON

**Error**: "Invalid JSON"

**Fix**: Validate JSON syntax with `python3 -m json.tool your-test.json`

### Runner Not Found

**Error**: "command not found: python"

**Fix**: Use `python3` instead of `python`

### Import Errors

**Error**: "ModuleNotFoundError: No module named 'dataclasses'"

**Fix**: Use Python 3.9+ (check: `python3 --version`)

### Test Case Not Loading

**Error**: "Test case not found: test-cases/..."

**Fix**: Use full path: `.claude/skills/.evals/test-cases/skill-name/scenario.json`

## Related Documentation

- **[README.md](README.md)** - Overview and quick start
- **[ADR-004](../../docs/ADRs/004-skill-evaluation-framework.md)** - Architecture decision
- **[Anthropic Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#build-evaluations-first)** - Official guidance

---

**Last Updated**: 2026-03-11
**Phase**: 1 (Baseline)
**Next**: Phase 2 (Execution + CI)
