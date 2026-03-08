# Phase B: Planning

> Part of the 4-Phase AI-Assisted Development Workflow
> See: [MAIN.md](./MAIN.md) for complete overview

## Overview

Phase B is where we plan **how to build** the features. This phase uses a **two-step planning system** that separates strategic MVP decomposition from tactical feature planning.

### Why Two Steps?

**One-step (all-at-once) planning** = 20-40 hours upfront, plans get outdated, can't adjust based on learnings

**Two-step approach** = Fast MVP decomposition (40 min) + just-in-time feature planning (1-2h per feature)

---

## Step 1: MVP-Level Decomposition (40 min)

**When**: Starting a new MVP release
**Output**: GitHub Issues with rough sizing and dependencies

### Process

1. **Analyze MVP goals** (10 min) - Read MVP documentation, understand objectives
2. **Identify feature modules** (10 min) - Break down MVP into 5-8 major features, estimate rough size
3. **Map dependencies** (10 min) - Identify which features depend on others
4. **Create GitHub Issues** (10 min) - One Issue per feature with size, dependencies

### Deliverables

✅ All features identified and sized
✅ Dependencies mapped
✅ GitHub Issues created (5-10 typical)
✅ Team understands MVP scope
✅ Ready to pick features for development

**Detailed guide**: See [MAIN.md#strategy-layer-mvp-planning-40-minutes](./MAIN.md#strategy-layer-mvp-planning-40-minutes)

---

## Step 2: Feature-Level Planning (1-2h per feature)

**When**: About to start developing a specific feature
**Output**: Detailed Dev Plan + Test Cases in GitHub Issue

### Process

1. **Validate requirements** (15 min) - Review feature description, check acceptance criteria
2. **Create implementation plan** (45 min) - Break down into detailed steps, identify files, estimate time, note Pillar compliance
3. **Define test cases** (45 min) - Create test cases for each acceptance criterion, ensure 100% coverage
4. **Enrich GitHub Issue** (15 min) - Add Development Plan, Test Cases, labels, mark as ready

### Deliverables

✅ Requirements validated against docs
✅ Detailed implementation steps (files, time estimates)
✅ Test cases covering all acceptance criteria
✅ Pillar concerns identified
✅ Risk assessment done
✅ Issue labeled and ready for `*issue pick`

**Detailed guide**: See [MAIN.md#campaign-layer-feature-planning-1-2-hours](./MAIN.md#campaign-layer-feature-planning-1-2-hours)

---

## Step Comparison

| Aspect | MVP-Level | Feature-Level |
|--------|-----------|---------------|
| **When** | Per release start | Before developing a feature |
| **Duration** | 40 minutes | 1-2 hours |
| **Output** | GitHub Issues (minimal) | Dev Plan + Test Cases |
| **Details** | Rough sizes, dependencies | Detailed steps, files, tests |

---

## Commands

| Command | Description |
|---------|-------------|
| `*plan mvp` | Start MVP planning |
| `*plan #<n>` | Start feature planning for issue #n |
| `*tier` | Classify complexity (T1/T2/T3) |

---

## Templates

- **TEMPLATE-mvp.md** - MVP planning document
- **TEMPLATE-feature-plan.md** - Feature development plan
- **TEMPLATE-github-issue.md** - GitHub issue format

---

## Success Criteria

**MVP-Level Planning Complete:**
- [ ] All features identified and sized
- [ ] Dependencies mapped
- [ ] GitHub Issues created (5-10 issues typical)
- [ ] Team understands MVP scope

**Feature-Level Planning Complete:**
- [ ] Development plan with detailed steps
- [ ] Test cases with 100% coverage
- [ ] All labels applied (tier, pillar, status)
- [ ] Issue approved by team

---

## Next Phase

See [Phase-C-Development.md](./Phase-C-Development.md) for development execution.

---

**Part of**: 4-Phase Workflow (A → **B** → C → D)
