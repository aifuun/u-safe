# Issue #14: chore: consolidate ADR directories (docs/adr + docs/ADRs → docs/ADRs)

**GitHub**: https://github.com/aifuun/u-safe/issues/14
**Branch**: feature/14-consolidate-adr-directories
**Worktree**: /Users/woo/dev/u-safe-14-consolidate-adr-directories
**Started**: 2026-03-14

## Context

ADR files are scattered across two directories with inconsistent path references throughout the codebase:

### Existing Directories
| Directory | Content |
|-----------|---------|
| `docs/adr/` | 0001-record-architecture-decisions.md, 0002-technical-stack.md, 0003-encryption-strategy.md |
| `docs/ADRs/` | 001-design-token-system-css-variables.md, README.md, TEMPLATE.md |

### Path Reference Confusion
Three different path patterns found in the codebase:
- `docs/adr/` — Referenced by docs/README.md, docs/spec/*.md, docs/arch/*.md
- `docs/ADRs/` — Referenced by CLAUDE.md, .claude/skills/*.md, docs/roadmap/*.md
- `docs/architecture/ADR/` — Referenced by .claude/rules/ (directory doesn't exist)

## Goal

Consolidate to `docs/ADRs/` (the single canonical location defined in CLAUDE.md)

## Tasks

### Phase 1: Migrate Files (15 min)
- [ ] **Task 1.1**: Move docs/adr/0001-record-architecture-decisions.md to docs/ADRs/002-record-architecture-decisions.md
- [ ] **Task 1.2**: Move docs/adr/0002-technical-stack.md to docs/ADRs/003-technical-stack.md
- [ ] **Task 1.3**: Move docs/adr/0003-encryption-strategy.md to docs/ADRs/004-encryption-strategy.md
- [ ] **Task 1.4**: Update docs/ADRs/README.md index to include all 4 ADRs
- [ ] **Task 1.5**: Delete empty docs/adr/ directory

### Phase 2: Update References to docs/adr/ (10 min)
- [ ] **Task 2.1**: Update docs/README.md (2 references)
- [ ] **Task 2.2**: Update docs/arch/Database_Schema.md (2 references)
- [ ] **Task 2.3**: Update docs/spec/UI_UX_Design_System.md (2 references)
- [ ] **Task 2.4**: Update docs/spec/PRD_Core_Logic.md (1 reference)
- [ ] **Task 2.5**: Update .claude/skills/review/SKILL.md (4 references)

### Phase 3: Update References to docs/architecture/ADR/ (5 min)
- [ ] **Task 3.1**: Update .claude/rules/development/file-creation.md (3 references)
- [ ] **Task 3.2**: Update .claude/rules/core/memory-management.md (4 references)
- [ ] **Task 3.3**: Update .claude/workflow/ISSUE_COMPLETION_CHECKLIST.md (2 references)

### Phase 4: Verification (5 min)
- [ ] **Task 4.1**: Search codebase for remaining "docs/adr/" references
- [ ] **Task 4.2**: Search codebase for remaining "docs/architecture/ADR/" references
- [ ] **Task 4.3**: Verify docs/ADRs/README.md index is complete
- [ ] **Task 4.4**: Test that all ADR links work correctly

## Acceptance Criteria

1. ✅ All ADR files are in `docs/ADRs/` with consistent numbering (001-004)
2. ✅ `docs/adr/` directory deleted
3. ✅ No references to `docs/adr/` remain in codebase
4. ✅ No references to `docs/architecture/ADR/` remain in codebase
5. ✅ `docs/ADRs/README.md` index lists all 4 ADRs
6. ✅ All ADR links in documentation work correctly

## Affected Files

**Files to move**:
- docs/adr/0001-record-architecture-decisions.md → docs/ADRs/002-record-architecture-decisions.md
- docs/adr/0002-technical-stack.md → docs/ADRs/003-technical-stack.md
- docs/adr/0003-encryption-strategy.md → docs/ADRs/004-encryption-strategy.md

**Files with `docs/adr/` references** (8 files):
- docs/README.md
- docs/arch/Database_Schema.md
- docs/spec/UI_UX_Design_System.md
- docs/spec/PRD_Core_Logic.md
- .claude/skills/review/SKILL.md
- .claude/skills/overview/ scripts (optional)
- .claude/plans/archive/ (historical, optional)

**Files with `docs/architecture/ADR/` references** (3 files):
- .claude/rules/development/file-creation.md
- .claude/rules/core/memory-management.md
- .claude/workflow/ISSUE_COMPLETION_CHECKLIST.md

## Progress

- [ ] Phase 1: Migrate files complete
- [ ] Phase 2: Update docs/adr/ references complete
- [ ] Phase 3: Update docs/architecture/ADR/ references complete
- [ ] Phase 4: Verification complete
- [ ] All acceptance criteria met
- [ ] Ready for review

## Next Steps

1. Review this plan
2. Execute: /execute-plan #14
3. Verify all changes
4. When done: /finish-issue #14

## Estimated Time

35 minutes total:
- Phase 1: 15 min (file migration + index update)
- Phase 2: 10 min (update 8 files)
- Phase 3: 5 min (update 3 files)
- Phase 4: 5 min (verification)
