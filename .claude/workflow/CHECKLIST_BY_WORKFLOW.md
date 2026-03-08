# Checklist Guide by Workflow

> **Workflow-centric checklist reference**: Find the right checklist for your current task

**TL;DR**:
- **Planning a feature?** → [Feature Development](#feature-development-workflow)
- **Fixing a bug?** → [Bugfix](#bugfix-workflow)
- **Emergency production fix?** → [Hotfix](#hotfix-workflow)
- **Refactoring code?** → [Refactoring](#refactoring-workflow)
- **Releasing a version?** → [Release](#release-workflow)
- **Starting work session?** → [Session Management](#session-management-workflow)

---

# FEATURE DEVELOPMENT WORKFLOW

> Most common workflow: MVP decomposition → detailed planning → implementation → review → closure

## Workflow Stages & Checklist Usage

### 1️⃣ MVP-Level Planning (40 minutes)

**What**: Break down MVP goals into GitHub Issues
**When**: Starting new major release (v1.0, v2.0, etc.)
**Command**: `*plan mvp`

| Step | Checklist | Items | Duration |
|------|-----------|-------|----------|
| Understand MVP goals | Manual review (REQUIREMENTS.md) | Review product objectives | 10 min |
| Identify feature modules | None | List 5-8 feature modules | 10 min |
| Map dependencies | None | Draw dependency diagram | 15 min |
| Create GitHub Issues | None | Create Issue #1-#8 with estimates | 5 min |

**Output**: GitHub Issues #1-#8 ready for feature-level planning

**Reference Document**: `workflow/workflow/MAIN.md#strategy-layer-mvp-planning-40-minutes`

---

### 2️⃣ Feature-Level Planning (1-2 hours)

**What**: Detailed implementation plan for ONE issue
**When**: Before starting development on a specific feature
**Command**: `*plan #<issue-number>`

#### Checklist: **DEVELOPMENT_CHECKLIST.md - Phase 1: Pre-Code Planning**

**Apply these items to your feature**:

| Pillar | Check Items | Must Do? | T1 | T2 | T3 |
|--------|------------|----------|----|----|----|
| **A: Nominal Typing** | Domain IDs identified as branded types | Yes | ✓ | ✓ | ✓ |
| **B: Airlock** | External data sources + Zod schemas identified | Yes | ✓ | ✓ | ✓ |
| **D: FSM** | States and transitions defined (no booleans) | Yes | ✗ | ✓ | ✓ |
| **E: Tier Classification** | Task tier determined (T1/T2/T3) | Yes | ✓ | ✓ | ✓ |
| **F: Concurrency** | Version field strategy (for concurrent writes) | No | ✗ | ✗ | ✓ |
| **I: Firewalls** | Layer structure and public APIs planned | Yes | ✓ | ✓ | ✓ |
| **L: Headless** | Business logic vs UI separation designed | Yes | ✗ | ✓ | ✓ |
| **M: Saga** | Compensation steps designed (if T3) | Cond | ✗ | ✗ | ✓ |
| **Q: Idempotency** | Intent-ID mechanism designed (if T3) | Cond | ✗ | ✗ | ✓ |

**Outputs to Create**:
- Development plan: `.claude/plans/active/#<N>-*.md`
- Test cases: `.claude/plans/active/#<N>-TEST-CASES.md`
- GitHub issue comment with plan + tier/pillar labels

**Reference Document**: `workflow/workflow/MAIN.md#campaign-layer-feature-planning-1-2-hours-per-feature`

---

### 3️⃣ Development Execution (2-6 hours)

**What**: Write code following the development plan
**When**: After planning complete
**Command**: `*issue pick <N>` → `*next` (per task)

#### Checklist: **DEVELOPMENT_CHECKLIST.md - Phase 2: In-Code Implementation**

**Run continuously during coding** (not just at end):

| Pillar | In-Code Checks | Check Per | Auto-Verify |
|--------|---|---|---|
| **A: Branded Types** | All IDs use branded types (no `string`) | Per file | TypeScript compiler |
| **B: Airlock** | Schema validation at every boundary (`.parse()`) | Per adapter | Manual check |
| **D: FSM** | FSM states used (no boolean `loading`, `isOpen`) | Per state management | Type safety |
| **G: Traceability** | `@trigger`, `@listen`, `@ai-intent` comments | Per handler | Manual check |
| **H: Policy** | Authorization in `policy.assert()` (not business logic) | Per auth check | Code review |
| **I: Firewalls** | No deep imports, use `index.ts` exports | Per import | ESLint |
| **J: Locality** | State at correct level (component/page/global) | Per state | Manual check |
| **K: Testing** | Unit tests written for business logic | Per task | npm test |
| **L: Headless** | **NO JSX in hooks** (this is critical) | Per hook | Manual verification |
| **M: Saga** | Compensation stack + reversal (if T3) | Per saga step | Integration test |
| **N: Context** | traceId propagated to all async calls | Per async call | Manual check |
| **Q: Idempotency** | intentId caching (if T3 critical ops) | Per critical op | Manual check |
| **R: Structured Logging** | JSON logs, semantic fields, no `console.log` | Per log statement | Code review |

**When to Check**:
- After each subtask in development plan
- After finishing each file/module
- Before committing

**Verify Commands**:
```bash
npm test                # Run tests
npm run type-check      # TypeScript compilation
npm run lint            # ESLint + formatting
npm run build          # Build verification
```

**Reference Document**: `workflow/feature-development.md`

---

### 4️⃣ Code Review (20-30 minutes)

**What**: Final verification before issue closure
**When**: After implementation complete and tests passing
**Command**: `*review`

#### Checklist: **DEVELOPMENT_CHECKLIST.md - Phase 3: Post-Code Review**

**Run all audit items**:

| Category | Verification | Auto-Check | Manual Check |
|----------|---|---|---|
| **Static Checks** | TypeScript builds without errors | ✅ npm run build | - |
| | ESLint passes without warnings | ✅ npm run lint | - |
| **Architecture** | No primitive types for domain IDs | - | ✅ Code review |
| | No FSM replaced with booleans | - | ✅ Code review |
| | No deep imports (`../../../`) | ✅ ESLint | - |
| | No JSX in headless hooks | - | ✅ Manual |
| **Tests** | Overall coverage ≥80% | ✅ npm test --coverage | - |
| | All tests passing | ✅ npm test | - |
| | Tests fast (<1s total) | ✅ npm test timing | - |
| **Code Quality** | No `console.log` in code | - | ✅ grep |
| | No hardcoded secrets/API keys | - | ✅ Manual |
| | Proper error handling | - | ✅ Code review |

**Decision**:
- ✅ **PASS**: Ready for `*issue close`
- ❌ **NEEDS_FIX**: Create follow-up fix tasks

#### Supplementary Checklist: **ISSUE_COMPLETION_CHECKLIST.md**

Run this checklist right before closing the issue:

| Section | Items | For UI? | For Backend? |
|---------|-------|--------|--------------|
| **1. Architecture Compliance** | ADRs, 4-layer, service patterns | ✓ | ✓ |
| **2. Code Quality** | Pillars A-R coverage | ✓ | ✓ |
| **3. UI/UX** | Design tokens, accessibility, responsive | ✓ only | - |
| **4. Testing** | Coverage, unit/integration/e2e | ✓ | ✓ |
| **5. Documentation** | ADRs, SCHEMA, updated feature plans | ✓ | ✓ |
| **6. Git Workflow** | Branch naming, commits, PR format | ✓ | ✓ |
| **7. Code Hygiene** | No temp files, no secrets, clean | ✓ | ✓ |
| **8. Quick Commands** | test, lint, type-check, build | ✓ | ✓ |
| **9. Issue-Specific** | Feature/bug/refactoring specific | ✓ | ✓ |

**Reference Document**: `workflow/ISSUE_COMPLETION_CHECKLIST.md`

---

### 5️⃣ Issue Closure (5-10 minutes)

**What**: Merge feature and close issue
**When**: Code review passed
**Command**: `*issue close <N>`

| Step | What to Check | Checklist Reference |
|------|---|---|
| Pre-closure | All Phase 3 items complete | DEVELOPMENT_CHECKLIST Phase 3 |
| Pre-closure | All feature plan steps done | Feature plan checklist |
| Code commit | Final changes with issue reference | Git workflow |
| Create PR | Target development branch | Git workflow |
| PR review | Wait for review approval | GitHub PR |
| Merge | Merge with `--no-ff` flag | Git workflow |
| Cleanup | Delete feature branch | Git workflow |
| Archive | Move feature plan to archive | File organization |

**Reference Document**: `workflow/branch-strategy.md`

---

## Feature Development Summary

```
MVP Planning (40 min)
    ↓
Feature Planning (1-2h) → DEVELOPMENT_CHECKLIST Phase 1
    ↓
Development (2-6h) → DEVELOPMENT_CHECKLIST Phase 2 (continuous)
    ↓
Code Review (20-30m) → DEVELOPMENT_CHECKLIST Phase 3 + ISSUE_COMPLETION_CHECKLIST
    ↓
Issue Closure (5-10m) → Git workflow
```

---

# BUGFIX WORKFLOW

> Fix bugs in development/staging (non-production)

## When to Use This Workflow

- Bug discovered in development environment
- Error doesn't affect production
- Can wait for next development release
- Duration: 1-4 hours typically

## Checklist Usage

### 1️⃣ Root Cause Analysis (15-30 minutes)

**No checklist required** - diagnostic phase

**Steps**:
1. Reproduce the bug with minimal steps
2. Check logs for error messages and traceId
3. Identify root cause (usually FSM state transition issue)
4. Create test case that reproduces bug

**Reference**: `@.claude/rules/debugging.md`

---

### 2️⃣ Bugfix Implementation (30 min - 2 hours)

**What**: Implement minimal fix
**Command**: `*next`

#### Checklist: **DEVELOPMENT_CHECKLIST.md - Phase 2** (abbreviated)

**Apply only relevant items**:

| Pillar | Check | Must Do |
|--------|-------|---------|
| **D: FSM** | State transitions correct (root cause of most bugs) | ✓ |
| **K: Testing** | Add regression test | ✓ |
| **L: Headless** | If UI-related, no JSX in hooks | ✓ |
| **N: Context** | Logs capture bug scenario | ✓ |
| **R: Observability** | Logs confirm fix | ✓ |

**Key Rule**: "Keep fix minimal - don't refactor surrounding code"

---

### 3️⃣ Bugfix Verification (10-15 minutes)

**Checklist**: **DEVELOPMENT_CHECKLIST.md - Phase 3** (abbreviated)

| Check | Required | How |
|-------|----------|-----|
| Tests passing | ✓ | `npm test` (all pass) |
| Type check | ✓ | `npm run type-check` |
| Local reproduction | ✓ | Manually verify bug fixed |
| Logs confirm fix | ✓ | Check logs for expected behavior |
| Regression test added | ✓ | Test for same bug never happens again |

---

### 4️⃣ Bugfix Completion

**Command**: `*bugfix finish`

| Step | Checklist |
|------|-----------|
| All checks pass | DEVELOPMENT_CHECKLIST Phase 3 (abbreviated) |
| Commit final | Branch naming convention |
| Merge to development | Git workflow |
| Delete branch | Git cleanup |

---

# HOTFIX WORKFLOW

> **CRITICAL**: Production bug fix on main branch (use rarely)

## When to Use This Workflow

- Production system failure
- Payment/security issue
- Cannot wait for next development release
- **MUST BE MINIMAL** - fix only, no improvements

## Checklist Usage

### 1️⃣ Create Hotfix Branch

**CRITICAL**: Branch from **main**, NOT development

```bash
*hotfix start <critical-issue-description>
```

**No checklist required** - emergency mode

---

### 2️⃣ Hotfix Implementation (30 min - 1 hour)

**Command**: `*next`

#### Checklist: **DEVELOPMENT_CHECKLIST.md - Phase 2** (minimal)

**Apply ONLY critical items**:

| Pillar | Check | Reason |
|--------|-------|--------|
| **D: FSM** | State transitions correct | Root cause fix |
| **K: Testing** | Minimal local testing | Verify fix works |

**Key Rule**: "In hotfix, skip nice-to-haves. Fix production issue. Done."

---

### 3️⃣ Hotfix Verification

**Checklist**: **DEVELOPMENT_CHECKLIST.md - Phase 3** (minimal)

| Check | Required |
|-------|----------|
| Fix verified locally | ✓ |
| No regressions in hotfix code | ✓ |

---

### 4️⃣ Hotfix Completion (CRITICAL SYNC STEP)

**Command**: `*hotfix finish`

| Step | Critical? | Action |
|------|-----------|--------|
| Commit final changes | ✓ | `git commit -m "fix: <desc> (hotfix)"` |
| Merge to **main** | ✓ | Merge with merge commit |
| **SYNC TO DEVELOPMENT** | ✓✓ **DO NOT SKIP** | `git checkout development && git merge main && git push` |
| Delete branch | ✓ | Clean up locally + remote |
| Tag release | Optional | `npm version patch` if needed |

**⚠️ WARNING**: If you don't sync hotfix to development, the bug will reappear in next release!

---

# REFACTORING WORKFLOW

> Code reorganization without behavior changes

## When to Use This Workflow

- Improving code structure
- Performance optimization
- Consolidating duplicate code
- **Key Constraint**: All existing tests must still pass

## Checklist Usage

### 1️⃣ Planning (15-30 minutes)

**No checklist required** - planning phase

**Important**: Document the "before/after" pattern

---

### 2️⃣ Refactoring (1-6 hours)

**Command**: `*next`

#### Checklist: **DEVELOPMENT_CHECKLIST.md - Phase 2**

**Critical items for refactoring**:

| Pillar | Check | Reason |
|--------|-------|--------|
| **I: Firewalls** | Import boundaries still clean | Refactoring might break layers |
| **K: Testing** | All tests still pass | **No behavior changes allowed** |
| **L: Headless** | Hooks still have no JSX | Structure shouldn't change |

**Golden Rule**: "If a test fails, you've changed behavior. Stop."

---

### 3️⃣ Refactoring Verification

**Checklist**: **DEVELOPMENT_CHECKLIST.md - Phase 3**

| Check | Requirement |
|-------|-------------|
| All existing tests pass | 100% (no skipped tests) |
| Test coverage maintained | ≥80% overall |
| Code complexity reduced | Measured (cyclomatic complexity) |
| Performance not degraded | Benchmarks stable |
| Documentation updated | If interface changed |

**Decision**:
- ✓ Tests pass, behavior unchanged → **PASS**
- ✗ Test fails → Go back and fix the refactoring

---

# RELEASE WORKFLOW

> Publish new version to production

## When to Use This Workflow

- MVP features complete
- Ready to publish new version
- Duration: 1-2 hours

## Checklist Usage

### 1️⃣ Pre-Release Verification (15-30 minutes)

**No specific checklist file** - manual verification

| Check | How |
|-------|-----|
| All MVP issues closed | Check GitHub milestone |
| Tests passing | `npm test` |
| Documentation updated | Check CHANGELOG, README |
| No uncommitted changes | `git status` |

---

### 2️⃣ Release Execution

**Command**: `*release [patch|minor|major]`

| Step | Checklist |
|------|-----------|
| Verify clean state | `git status` |
| Merge development to main | Git workflow |
| Update version | `npm version <type>` |
| Update CHANGELOG | Manual edit |
| Create git tag | Automatic |
| Push and publish | Automatic |

**Post-Release**:
- [ ] Verify release available (npm registry, GitHub releases)
- [ ] Monitor logs for issues
- [ ] Update project documentation

---

# SESSION MANAGEMENT WORKFLOW

> Starting work, finding next task, saving progress

## When to Use This Workflow

- Every work session start
- Returning after break
- Finding next task to work on
- Saving progress before leaving

## Checklist Usage

### 1️⃣ Resume Session (5-10 minutes)

**What**: Understand current project state
**Command**: `*resume`

**No checklist required** - context loading phase

**Automatic loads**:
- [ ] MEMORY.md (project decisions, ADRs)
- [ ] `.claude/plans/active/` (active issues)
- [ ] Current branch and git status

---

### 2️⃣ Get Next Task (5 minutes)

**What**: Find next task to work on
**Command**: `*next`

**3-Level Cascade** (automatic):

1. **Level 1: Active Tasks**
   - Check `.claude/plans/active/` for pending steps
   - If found → Show next step
   - If all complete → Suggest `*review`

2. **Level 2: Recommend Issues**
   - Find current MVP
   - Extract uncompleted issues
   - Show P1 issues first
   - Estimate complexity (T1/T2/T3)

3. **Level 3: Recommend MVP**
   - If current MVP complete → Check next MVP
   - Show MVP goal and acceptance criteria

**No checklist** - navigation phase only

---

### 3️⃣ Update Progress (5 minutes)

**What**: Save work to git
**Command**: `*sync`

**No checklist required** - git automation

**Variants**:
- `*sync` - Commit and push current changes
- `*sync --ask` - Interactive mode (ask for summary)
- `*sync --memory` - Update MEMORY.md with ADR links
- `*sync --no-push` - Commit only

---

# DECISION TREE: WHICH WORKFLOW?

```
Issue/Task arrives
    │
    ├─ Production system broken? (main branch)
    │  └─ YES → HOTFIX WORKFLOW
    │
    ├─ Bug in development branch?
    │  └─ YES → BUGFIX WORKFLOW
    │
    ├─ Code reorganization (no behavior change)?
    │  └─ YES → REFACTORING WORKFLOW
    │
    ├─ New feature/functionality?
    │  ├─ MVP-level? → *plan mvp
    │  ├─ Feature-level? → *plan #N
    │  └─ Ready to code? → FEATURE DEVELOPMENT WORKFLOW
    │
    └─ Time to release?
       └─ YES → RELEASE WORKFLOW
```

---

# QUICK REFERENCE BY ROLE

## Frontend Developer
```
Session Start           → *resume
Plan feature           → *plan #N (use DEVELOPMENT_CHECKLIST Phase 1)
Implement              → *next (use DEVELOPMENT_CHECKLIST Phase 2)
Before closing issue   → Also check design-compliance.md (UI/design)
Review and close       → *review (use DEVELOPMENT_CHECKLIST Phase 3)
Save work             → *sync
```

## Backend Developer
```
Session Start           → *resume
Plan feature           → *plan #N (use DEVELOPMENT_CHECKLIST Phase 1)
Implement              → *next (use DEVELOPMENT_CHECKLIST Phase 2)
Before deploying       → Check lambda-layer-deployment.md if applicable
Review and close       → *review (use DEVELOPMENT_CHECKLIST Phase 3)
Save work             → *sync
```

## Full-Stack Developer
```
Session Start           → *resume
Plan MVP features      → *plan mvp
Plan feature           → *plan #N (use DEVELOPMENT_CHECKLIST Phase 1, all Pillars)
Implement              → *next (use DEVELOPMENT_CHECKLIST Phase 2)
Before closing issue   → Check both design-compliance.md + lambda-layer-deployment.md if applicable
Review and close       → *review (use DEVELOPMENT_CHECKLIST Phase 3)
Save work             → *sync
```

---

# TIER-BASED CHECKLIST FOCUS

**Determined by**: `*tier` command during Phase 1 Pre-Code Planning

| Tier | Focus Pillars | Checklist Emphasis |
|------|---|---|
| **T1** | A, I, L | Simple types, clean imports, UI separation |
| **T2** | A, D, I, L, K | Add FSM, testing requirements |
| **T3** | A, B, D, F, I, L, M, N, Q, R | All critical Pillars + saga/idempotency |

---

# SUMMARY TABLE: Checklist by Workflow Phase

| Workflow | Phase | Checklist | Duration | Frequency |
|----------|-------|-----------|----------|-----------|
| Feature Development | Planning | DEVELOPMENT_CHECKLIST Phase 1 | 30-40 min | Per feature |
| Feature Development | Coding | DEVELOPMENT_CHECKLIST Phase 2 | Continuous | Per task |
| Feature Development | Review | DEVELOPMENT_CHECKLIST Phase 3 + ISSUE_COMPLETION_CHECKLIST | 20-30 min | Per issue |
| Bugfix | Diagnosis | None (manual) | 15-30 min | Per bug |
| Bugfix | Implementation | DEVELOPMENT_CHECKLIST Phase 2 (abbrev) | 30m-2h | Per bug |
| Bugfix | Verification | DEVELOPMENT_CHECKLIST Phase 3 (abbrev) | 10-15 min | Per bug |
| Hotfix | Implementation | DEVELOPMENT_CHECKLIST Phase 2 (minimal) | 30m-1h | Emergency |
| Hotfix | Verification | DEVELOPMENT_CHECKLIST Phase 3 (minimal) | 5-10 min | Emergency |
| Refactoring | Implementation | DEVELOPMENT_CHECKLIST Phase 2 (focus: tests) | 1-6h | Occasional |
| Refactoring | Verification | DEVELOPMENT_CHECKLIST Phase 3 (tests critical) | 10-15 min | Occasional |
| Release | Pre-release | Manual verification | 15-30 min | Per release |
| Release | Execution | Release command automation | 10 min | Per release |

---

**Version**: 1.0
**Created**: 2026-02-25
**Purpose**: Help developers find the right checklist for their current workflow
