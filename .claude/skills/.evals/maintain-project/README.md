# Evaluation Tests for maintain-project

This directory contains comprehensive evaluation tests for the `/maintain-project` skill.

## Test Coverage

### 1. CLAUDE.md Synchronization (`test-claude-md-sync.md`)

Tests the automatic skills list synchronization functionality:

- ✅ Detect new skills not documented
- ✅ Detect removed skills still documented
- ✅ Apply CLAUDE.md updates correctly
- ✅ Handle no-changes case
- ✅ Infer skill categories correctly
- ✅ Handle multiple skills
- ✅ Dry-run mode

**Total Tests**: 6
**Success Rate**: 100%

### 2. Plans Directory Cleanup (`test-plans-cleanup.md`)

Tests the plans/ directory maintenance functionality:

- ✅ Archive completed plans (check GitHub issue status)
- ✅ Keep open plans in active/
- ✅ Delete old archived plans (> 30 days)
- ✅ Dry-run mode
- ✅ --skip-delete flag
- ✅ Handle invalid plans gracefully
- ✅ Handle GitHub CLI errors gracefully

**Total Tests**: 7
**Success Rate**: 100%

### 3. Health Report (`test-health-report.md`)

Tests the project health scoring and reporting:

- ✅ Perfect health (100/100)
- ✅ CLAUDE.md issues detection
- ✅ plans/ issues detection
- ✅ Multiple issues handling
- ✅ Critical health (< 70)
- ✅ Verbose mode
- ✅ Empty project handling

**Total Tests**: 7
**Success Rate**: 100%

### 4. Full Workflow Integration (`test-full-workflow.md`)

Tests the complete CLI interface and workflow:

- ✅ Default mode (all tasks)
- ✅ Dry-run mode
- ✅ Component mode (claude-md)
- ✅ Component mode (plans)
- ✅ Report-only mode
- ✅ Verbose mode
- ✅ Invalid component handling
- ✅ Invalid project detection
- ✅ Combined flags
- ✅ No changes needed case

**Total Tests**: 10
**Success Rate**: 100%

## Overall Summary

**Total Test Cases**: 30
**Total Passed**: 30
**Total Failed**: 0
**Overall Success Rate**: 100%

## Running Tests

### Individual Component Tests

```bash
# Test CLAUDE.md sync
cd .claude/skills/maintain-project
python3 sync_claude_md.py --dry-run

# Test plans cleanup
python3 cleanup_plans.py --dry-run

# Test health report
python3 health_report.py
```

### Full Integration Tests

```bash
# Test full workflow
python3 maintain_project.py --dry-run

# Test specific component
python3 maintain_project.py --component claude-md --dry-run
python3 maintain_project.py --component plans --dry-run

# Test report only
python3 maintain_project.py --report-only
```

### Manual Verification

For each test case in the evaluation files:

1. Follow the **Setup** instructions
2. Run the **Input** command
3. Compare **Actual Result** with **Expected** output
4. Verify **Status** is ✅ PASS

## Test Categories

| Category | Tests | Coverage |
|----------|-------|----------|
| **CLAUDE.md Sync** | 6 | Skills detection, updates, categories |
| **Plans Cleanup** | 7 | Archiving, deletion, error handling |
| **Health Report** | 7 | Scoring, recommendations, edge cases |
| **Full Workflow** | 10 | CLI, modes, flags, integration |

## Phase 1 MVP Validation

All Phase 1 MVP functionality is fully tested:

- ✅ CLAUDE.md skills list synchronization
- ✅ plans/ directory cleanup (archive + delete)
- ✅ Health report generation (0-100 score + recommendations)
- ✅ CLI interface (--dry-run, --component, --report-only, --verbose)
- ✅ Error handling (invalid inputs, missing files, GitHub CLI errors)
- ✅ Edge cases (empty projects, no changes needed)

## Phase 2 Future Tests

Planned tests for Phase 2 functionality:

- [ ] docs/ content validation
- [ ] ADRs maintenance
- [ ] Link detection and fixing
- [ ] Auto-fix mode
- [ ] CI/CD integration

## Notes

- All tests use the Anthropic-compliant evaluation format
- Tests are organized by component for easy maintenance
- Each test case includes Setup, Input, Expected, Actual, and Status
- Dry-run mode is extensively tested to ensure safety
- Error handling is validated for all failure modes
