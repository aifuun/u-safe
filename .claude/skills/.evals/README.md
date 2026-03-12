# Skill Evaluation System

> Automated testing for Claude Code skills following Anthropic's official evaluation format

## Overview

This directory contains the skill evaluation infrastructure as defined in [ADR-004](../../../docs/ADRs/004-skill-evaluation-framework.md).

**Purpose**: Systematic quality assurance for skills through automated testing

**Format**: Anthropic's official evaluation schema (JSON test cases)

## Directory Structure

```
.claude/skills/.evals/
├── runner.py              # Eval executor (Python 3.9+)
├── test-cases/            # JSON test cases by skill
│   ├── start-issue/       # Tests for /start-issue skill
│   ├── finish-issue/      # Tests for /finish-issue skill
│   └── execute-plan/      # Tests for /execute-plan skill
├── results/               # Eval results (gitignored)
└── README.md              # This file
```

## Quick Start

### Run a single test case

```bash
python .claude/skills/.evals/runner.py .claude/skills/.evals/test-cases/start-issue/basic.json
```

### Run all tests for a skill (Phase 2)

```bash
python .claude/skills/.evals/runner.py --skill start-issue
```

### Run all tests (Phase 2)

```bash
python .claude/skills/.evals/runner.py --all
```

## Test Case Format

Following Anthropic's official schema:

```json
{
  "name": "start-issue-basic",
  "skills": ["start-issue"],
  "query": "start issue #23",
  "files": [],
  "expected_behavior": [
    "Creates feature branch",
    "Generates implementation plan",
    "Pushes branch to remote"
  ]
}
```

**Required fields**:
- `skills`: List of skill names to test
- `query`: User request as natural language
- `expected_behavior`: List of expected outcomes

**Optional fields**:
- `name`: Test case identifier
- `files`: List of test fixture file paths
- `assertions`: Specific checks to perform

## Creating Test Cases

1. **Identify skill to test** (e.g., `/start-issue`)
2. **Choose scenario** (basic usage, edge case, error handling)
3. **Create JSON file** in `test-cases/{skill-name}/`
4. **Define query** - typical user request
5. **List expected behaviors** - observable outcomes
6. **Run test** to validate

**Example workflow**:
```bash
# Create test case
cat > .claude/skills/.evals/test-cases/start-issue/basic.json << 'EOF'
{
  "name": "start-issue-basic",
  "skills": ["start-issue"],
  "query": "start issue #23",
  "expected_behavior": [
    "Creates feature branch",
    "Generates plan file",
    "Pushes to remote"
  ]
}
EOF

# Run test
python .claude/skills/.evals/runner.py .claude/skills/.evals/test-cases/start-issue/basic.json
```

## Development Phases

### Phase 1 (Current - Issue #97)
- ✅ Directory structure created
- ✅ Runner skeleton implemented
- ✅ Test case format validated
- 🔲 Baseline test cases for 3 skills

**Status**: Infrastructure ready, test cases in progress

### Phase 2 (Future - P1)
- 🔲 Runner execution logic (actually runs skills)
- 🔲 CI integration (GitHub Actions)
- 🔲 Regression testing on PR

### Phase 3 (Future - P2)
- 🔲 Extended test coverage (all skills)
- 🔲 Performance benchmarking
- 🔲 Pre-release validation

## Testing Levels (from ADR-002)

**Level 1 (Quick)**: No evals required (simple skills, docs)
**Level 2 (Basic)**: 1-2 test cases (core workflows)
**Level 3 (Full)**: Complete coverage (meta-tools, release)

## Integration with Workflow

```
/skill-creator "create new-skill"
  → Write skill code
  → Create eval test cases
  → Run: python .claude/skills/.evals/runner.py --skill new-skill
  → Ship if passing
```

## Best Practices

1. **Start simple** - One basic test case per skill
2. **Cover edge cases** - Error handling, invalid input
3. **Keep tests focused** - One scenario per test case
4. **Use descriptive names** - `start-issue-basic.json`, `start-issue-no-plan.json`
5. **Document expected behavior** - Clear, observable outcomes

## Current Test Coverage

| Skill | Test Cases | Status |
|-------|-----------|--------|
| start-issue | 3 | ✅ Complete (basic, no-plan, custom-prefix) |
| finish-issue | 2 | ✅ Complete (basic, no-merge) |
| execute-plan | 3 | ✅ Complete (basic, resume, dry-run) |

**Total**: 8 test cases across 3 skills
**Target**: 2-3 test cases per skill (Phase 1) - ✅ EXCEEDED

## Related Documentation

- **[ADR-004](../../../docs/ADRs/004-skill-evaluation-framework.md)** - Evaluation framework architecture
- **[ADR-002](../../../docs/ADRs/002-skill-creation-workflow.md)** - Testing levels and workflow
- **[Anthropic Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#build-evaluations-first)** - Official guidance

---

**Version**: 1.0.0 (Phase 1)
**Last Updated**: 2026-03-11
**Next Review**: After Phase 2 implementation
