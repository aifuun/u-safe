# AI-Assisted Development Workflow

> Complete workflow guide for the AI Development Framework

---

## Overview

This framework uses a **4-Phase workflow** with **3-Layer planning** architecture:

```
Phase A: Documentation  (Define what to build)
    ↓
Phase B: Planning       (How to build it)
    ├─ Strategy Layer   → MVP Planning (product goals)
    ├─ Campaign Layer   → GitHub Issues (task breakdown)
    └─ Tactics Layer    → Feature Plans (implementation)
    ↓
Phase C: Development    (Build it)
    ↓
Phase D: Release        (Ship it)
```

---

## 🎯 Quick Reference: Workflow → Checklist Mapping

**Looking for the right checklist for your task?**

👉 **See: [CHECKLIST_BY_WORKFLOW.md](./CHECKLIST_BY_WORKFLOW.md)** - Workflow-centric guide

**By workflow type**:
- 🆕 **Feature Development** → DEVELOPMENT_CHECKLIST (Phase 1-3)
- 🐛 **Bug Fix** → DEVELOPMENT_CHECKLIST Phase 2-3 (abbreviated)
- 🚨 **Production Hotfix** → DEVELOPMENT_CHECKLIST Phase 2-3 (minimal)
- ♻️ **Refactoring** → DEVELOPMENT_CHECKLIST Phase 2-3 (test focus)
- 📦 **Release** → Release command automation
- 📝 **Session Management** → `*resume` and `*next` commands

**Checklists available**:
- `.prot/checklists/DEVELOPMENT_CHECKLIST.md` - Main workflow (3 phases)
- `.prot/checklists/ISSUE_COMPLETION_CHECKLIST.md` - Issue closure
- `.prot/checklists/design-compliance.md` - UI/design (frontend)
- `.prot/checklists/lambda-layer-deployment.md` - AWS deployment (DevOps)

---

## 🎯 Navigation

**New to the framework?**
→ Start with [Quick Start](#quick-start) (5 minutes)

**Planning a new MVP?**
→ [Strategy Layer: MVP Planning](#strategy-layer-mvp-planning-40-minutes)

**Planning a feature?**
→ [Campaign Layer: Feature Planning](#campaign-layer-feature-planning-1-2-hours-per-feature)

**Ready to develop?**
→ [Phase C: Development](./Phase-C-Development.md) or [4-Phase Workflow System](#4-phase-workflow-system)

**Looking for quick reference?**
→ [Command Reference](#command-reference) | [Core Principles](#core-principles) | [Checklists](./CHECKLIST_BY_WORKFLOW.md)

---

## Core Principles

### 1. Branch-First Rule (CRITICAL)

**BEFORE starting ANY code changes, ALWAYS create a feature branch.**

**Branch naming convention:**
```
feature/#XXX-short-description   (new features)
bugfix/#XXX-short-description    (bug fixes)
hotfix/#XXX-short-description    (urgent production fixes)
```

**Checklist** (MUST verify before coding):
- [ ] NOT on `development` or `master` branch
- [ ] Branch name follows convention
- [ ] Created from latest `development` or `main`

**Example workflow:**
```bash
# 1. Check current branch
git branch --show-current

# 2. If on development/main, create feature branch
git checkout main
git pull origin main
git checkout -b feature/13-standardize-workflow-docs

# 3. NOW start coding
```

**Why?** Feature branches allow safe experimentation, easy rollback, clean history, and parallel development.

---

### 2. Issue-Driven Development

**Every task is tracked as a GitHub Issue.**

**Key principles:**
- One Issue = one technical focus
- Each Issue has a `.claude/plans/active/#XXX.md` plan file
- Plan files track real-time progress with checkboxes
- Completed Issues are closed and plans are archived

**Issue structure:**
```markdown
## Issue #XXX: Title

**Priority**: P0/P1/P2
**Labels**: feature, enhancement, bug, documentation

### Description
[What needs to be done]

### Tasks
- [ ] Task 1
- [ ] Task 2

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

---

### 3. PR Target Branch Rule (CRITICAL)

**ALWAYS create Pull Requests to merge into `development` branch, NOT `master`.**

**PR checklist** (MUST verify before submitting):
- [ ] Base branch is `development` (NOT master)
- [ ] Head branch is `feature/XXX-*` or `bugfix/XXX-*`
- [ ] PR title matches issue title
- [ ] PR description includes "Closes #XXX"

**Correct workflow:**
```
feature/XXX → (PR) → development → (tested) → master → production
```

**Why?**
- Master only gets stable, tested code from development
- Integration testing happens in development
- Master always represents last known good state

---

### 4. Branch Cleanup Rule (CRITICAL)

**AFTER issue is closed, ALWAYS delete the feature branch (locally AND on GitHub).**

**Cleanup checklist:**
- [ ] Feature branch deleted locally: `git branch -d feature/XXX-*`
- [ ] Feature branch deleted on GitHub: `git push origin --delete feature/XXX-*`
- [ ] Plan file archived: `plans/active/#XXX.md` → `plans/archive/`

**Why?**
- Prevents branch clutter
- Clear development history
- Easier session resumption
- Better PR hygiene

---

## 3-Layer Planning Architecture

The framework uses a hierarchical planning system that separates strategic, tactical, and implementation concerns:

```
┌─────────────────────────────────────────────────────────────┐
│  Strategy Layer: MVP Planning                               │
│  Duration: 40 minutes                                       │
│  Output: Product goals, feature modules, rough sizing      │
│  File: docs/dev/MVP*.md                                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Campaign Layer: GitHub Issues                              │
│  Duration: 1-2 hours total                                  │
│  Output: Technical tasks, implementation details            │
│  Location: GitHub Issues or .github/issues/                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Tactics Layer: Feature Plans                               │
│  Duration: Real-time (per session)                          │
│  Output: Active task tracking, progress checkboxes         │
│  File: .claude/plans/active/#XXX.md                        │
└─────────────────────────────────────────────────────────────┘
```

### Strategy Layer: MVP Planning (40 minutes)

**When**: Starting a new MVP release (v1.0, v2.0, etc.)
**Goal**: Understand the feature landscape and dependencies
**Output**: GitHub Issues with rough sizing and dependencies
**Duration**: 40 minutes

#### Process

1. **Analyze MVP goals** (10 min)
   - Read MVP documentation
   - Understand business objectives
   - Identify core features needed

2. **Identify feature modules** (10 min)
   - Break down MVP into 5-8 major features
   - Name each feature clearly
   - Estimate rough size (8h, 16h, 24h)

3. **Map dependencies** (10 min)
   - Identify which features depend on others
   - Create dependency graph
   - Determine parallel vs sequential work

4. **Create GitHub Issues** (10 min)
   - One Issue per feature
   - Include: title, rough size, dependencies
   - Add labels: feature, mvp-XX, priority

#### Example Output

```
MVP3.0: E-commerce Cart (5 features, ~35 hours)

#100: Cart State Management (8h) → #101, #102, #103
#101: Cart UI Components (6h, depends on #100)
#102: Cart Persistence (4h, depends on #100)
#103: Checkout Flow (12h, depends on #100, #101)
#104: Order Confirmation (5h, depends on #103)

Development path:
Start #100 (8h)
→ After #100, start #101 + #102 in parallel (10h)
→ After #101, start #103 (12h)
→ After #103, start #104 (5h)
```

#### Deliverables

✅ All features identified and roughly sized
✅ Dependencies mapped and visualized
✅ GitHub Issues created (5-10 typical)
✅ Team understands MVP scope and timeline
✅ Ready to pick features for detailed planning

---

### Campaign Layer: Feature Planning (1-2 hours per feature)

**When**: About to start developing a specific feature
**Goal**: Create detailed implementation plan and test specification
**Output**: Dev Plan + Test Cases in GitHub Issue
**Duration**: 1-2 hours per feature

#### Step 1: Architecture Preparation (15 min)

Review architecture context:
- **ADRs**: Check relevant Architecture Decision Records
- **Pillars**: Identify applicable coding standards (A, B, K for T1; add D, I, J, L for T2; add F, M, Q, R for T3)
- **Patterns**: Review patterns from docs/architecture/

#### Step 2: Function Contracts & Tests (15 min)

Define key functions BEFORE implementation:
- **Function signature**: Name, parameters, return type
- **Pre-conditions**: What must be true before calling
- **Post-conditions**: What will be true after success
- **Unit tests**: Test cases covering happy path, edge cases, errors
- **Integration tests**: Module-to-module interaction tests

#### Step 3: Validate Requirements (15 min)

Ensure all prerequisite docs are ready:
- [ ] REQUIREMENTS.md has user story
- [ ] ARCHITECTURE.md defines module boundaries
- [ ] SCHEMA.md lists required entities
- [ ] DESIGN.md has UI specifications

#### Step 4: Create Implementation Plan (45 min)

Create `.claude/[feature-name]-PLAN.md`:
- Break down into detailed steps
- Identify files to create/modify
- Estimate time per step
- Identify technical risks
- Note Pillar compliance

**Example steps**:
```
Step 1: Redux slice setup (2h)
- Create src/redux/cart.slice.ts
- Define state interface: CartState, CartItem
- Implement actions, reducers, selectors
- Unit tests for reducer

Step 2: Cart persistence middleware (1h)
- Create src/middleware/cartPersistence.ts
- Save cart to localStorage on state changes
- Restore cart on app initialization
- Handle localStorage errors

Step 3: Integration and testing (1h)
- Integration tests for cart flow
- Performance testing (large carts)
- Manual QA and verification
```

#### Step 5: Define Test Cases (45 min)

Create `.claude/[feature-name]-TEST-CASES.md`:

**Unit Tests** (mock all dependencies):
- Happy path: Main workflow
- Edge cases: Empty inputs, null values, boundaries
- Race conditions: Concurrent operations
- Error flows: Network failures, validation errors

**Integration Tests** (real modules, mock external):
- Module-to-module information flow
- State synchronization through layers
- Event propagation and handlers
- All module exports present and correct

**Critical requirement** (from Issue #89):
- Both unit AND integration tests required
- Unit tests alone can hide architectural issues
- Integration tests catch what unit tests miss

#### Step 6: Enrich GitHub Issue (15 min)

Add to issue:
- Development Plan (steps + time estimates)
- Test Cases (unit + integration)
- Pillar references (architecture compliance)
- Labels: tier/T1-T3, pillar/*, status/planned

#### Deliverables

✅ Architecture context understood
✅ Key functions defined with tests
✅ Detailed implementation steps (files, times)
✅ Test cases covering all acceptance criteria
✅ Pillar concerns identified
✅ Risk assessment done
✅ Issue labeled and ready for `*issue pick`

---

### Tactics Layer: Feature Plans (real-time)

**When**: During active development session
**Goal**: Track real-time progress on current Issue
**Output**: Updated plan file with checked-off tasks

**Process:**
1. Copy plan from GitHub Issue to `.claude/plans/active/#XXX.md`
2. Mark current task with `←` indicator
3. Check off completed tasks
4. Update in real-time as work progresses
5. Archive to `plans/archive/` when complete

**Template**: `workflow/templates/TEMPLATE-feature-plan.md`

---

## 4-Phase Workflow System

### Phase A: Documentation

**Purpose**: Define what to build
**Activities**:
- Review project requirements
- Create/update MVP documentation
- Define acceptance criteria
- Establish project structure

**See**: [Phase-A-Documentation.md](./Phase-A-Documentation.md)

---

### Phase B: Planning

**Purpose**: Plan how to build it
**Activities**:
- Two-step planning (MVP → Feature)
- Create GitHub Issues
- Develop feature plans
- Establish dependencies

**See**: [Phase-B-Planning.md](./Phase-B-Planning.md)

**Key guides:**
- [MAIN.md#strategy-layer-mvp-planning-40-minutes](#strategy-layer-mvp-planning-40-minutes) - MVP decomposition
- [MAIN.md#campaign-layer-feature-planning-1-2-hours-per-feature](#campaign-layer-feature-planning-1-2-hours-per-feature) - Feature planning

---

### Phase C: Development

**Purpose**: Build it
**Activities**:
- Pick issues with `*issue pick`
- Create feature branches
- Implement features
- Write tests
- Create pull requests

**See**: [Phase-C-Development.md](./Phase-C-Development.md)

**Key commands:**
- `*next` - Get next task
- `*review` - Code review
- `*sync` - Sync with remote

---

### Phase D: Release

**Purpose**: Ship it
**Activities**:
- Merge to development
- Integration testing
- Deploy to staging
- Release to production
- Post-release verification

**See**: [Phase-D-Release.md](./Phase-D-Release.md)

**Key commands:**
- `*deploy` - Deploy to environment
- `*release` - Create release

---

## Command Reference

### Session Commands
- `*resume` - Resume previous work session
- `*status` - Show current status and active tasks

### Planning Commands
- `*plan` - Create MVP or feature plan
- `*tier` - Classify feature complexity (T1/T2/T3)

### Development Commands
- `*next` - Get next task from active plan
- `*issue pick <n>` - Pick and start working on issue #n
- `*issue create` - Create new GitHub issue
- `*sync` - Sync with remote or design files

### Quality Commands
- `*review` - Run code review
- `*audit` - Audit codebase for issues

### Deployment Commands
- `*deploy` - Deploy to environment
- `*release` - Create release version

**Full command list**: See [commands/](../commands/) directory

---

## Quick Start

### Your First Session

1. **Read documentation** (15 min)
   - [WORKFLOW.md](../WORKFLOW.md) - Quick navigation
   - [MEMORY.md](../MEMORY.md) - Project decisions
   - This file (MAIN.md) - Complete workflow

2. **Check active work** (5 min)
   - Look in [plans/active/](../plans/active/) for ongoing tasks
   - Check GitHub Issues for pending work

3. **Get your first task**
   ```bash
   *next
   ```

4. **Create feature branch**
   ```bash
   git checkout -b feature/XXX-description
   ```

5. **Start developing**
   - Follow the plan in `plans/active/#XXX.md`
   - Check off tasks as you complete them
   - Commit frequently with clear messages

---

### Planning a New Feature

1. **Read Phase-B Planning guide**
   - [Phase-B-Planning.md](./Phase-B-Planning.md)

2. **Copy appropriate template**
   - MVP: `templates/TEMPLATE-mvp.md`
   - Feature: `templates/TEMPLATE-feature-plan.md`
   - Issue: `templates/TEMPLATE-github-issue.md`

3. **Create plan**
   - For MVP: Create in `docs/dev/MVP*.md`
   - For Feature: Add to GitHub Issue description
   - For tracking: Create in `plans/active/#XXX.md`

4. **Start development**
   ```bash
   *issue pick XXX
   *next
   ```

---

## Best Practices

### Single Source of Truth
- Technical details live only in GitHub Issues
- MVP files are indexes, not duplicates
- Plan files are temporary, archive when done

### Minimal Maintenance
- Update progress in plan files only
- Close Issues when complete (GitHub auto-records time)
- Archive important decisions to ADRs or MEMORY.md

### Progressive Planning
- Don't plan all features upfront
- Plan feature details just-in-time (before development)
- Adjust plans based on learnings from previous features

### Clear Communication
- One Issue = one technical focus
- Clear commit messages referencing Issues (#XXX)
- PR descriptions include "Closes #XXX"

---

## Success Metrics

**Well-organized workflow:**
- [ ] Active work visible in `plans/active/`
- [ ] All tasks tracked in GitHub Issues
- [ ] Feature branches follow naming convention
- [ ] PRs target correct branch (development)
- [ ] Completed work properly archived

**Effective planning:**
- [ ] MVP goals clearly documented
- [ ] Features properly decomposed into Issues
- [ ] Dependencies mapped and understood
- [ ] Just-in-time feature planning before development

**Quality development:**
- [ ] Tests written for all features
- [ ] Code reviewed before merge
- [ ] Important decisions documented in ADRs
- [ ] Clean git history with meaningful commits

---

## Related Documentation

### Workflow Phases
- [Phase-A-Documentation.md](./Phase-A-Documentation.md) - Define what to build
- [Phase-B-Planning.md](./Phase-B-Planning.md) - Plan how to build
- [Phase-C-Development.md](./Phase-C-Development.md) - Build it
- [Phase-D-Release.md](./Phase-D-Release.md) - Ship it

### Planning Guides
- [Strategy Layer: MVP Planning](#strategy-layer-mvp-planning-40-minutes) - MVP decomposition (40 min)
- [Campaign Layer: Feature Planning](#campaign-layer-feature-planning-1-2-hours-per-feature) - Feature planning (1-2h)

### Templates
- [TEMPLATE-mvp.md](./templates/TEMPLATE-mvp.md) - MVP planning template
- [TEMPLATE-feature-plan.md](./templates/TEMPLATE-feature-plan.md) - Feature plan template
- [TEMPLATE-github-issue.md](./templates/TEMPLATE-github-issue.md) - Issue template

### Other Resources
- [branch-strategy.md](./branch-strategy.md) - Branching strategies
- [architecture-core.md](./architecture-core.md) - Architecture decisions
- [quick-reference.md](./quick-reference.md) - Quick reference

---

**Framework Version**: AI_DEV v1.0
**Last Updated**: 2026-03-14
