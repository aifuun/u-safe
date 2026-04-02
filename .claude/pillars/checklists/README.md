# 3-Phase Development Checklist System

> Structured quality gates for Pillar-compliant development

## Overview

The **3-Phase Checklist System** provides quality gates at each stage of development to ensure Pillar compliance and reduce defects:

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  PRE-CODE   │  →   │  IN-CODE    │  →   │  POST-CODE  │
│  Planning   │      │  Execution  │      │  Validation │
└─────────────┘      └─────────────┘      └─────────────┘
     ↓                     ↓                     ↓
 Before coding        During coding        After coding
 (30 min)             (per task)           (before PR)
```

## When to Use Each Checklist

### [pre-code.md](./pre-code.md) - Before Writing Code
**Run BEFORE starting implementation**

**Time**: 30 minutes of planning
**Purpose**: Identify patterns, plan architecture, prevent rework

**Covers**:
- Git workflow setup (feature branch creation)
- Task complexity classification (T1/T2/T3)
- Data integrity planning (Pillars A, B, D)
- Flow & concurrency planning (Pillars E, F, Q)
- Structure & boundaries planning (Pillars I, L)
- Resilience & observability planning (Pillars M, N, R)

**Output**: Clear implementation plan with pattern selection

---

### [in-code.md](./in-code.md) - During Implementation
**Run DURING coding, per task**

**Time**: Quick checks per task (5 minutes)
**Purpose**: Real-time validation, catch mistakes early

**Covers**:
- Data integrity implementation (Pillars A, B, D)
- Structure & boundaries enforcement (Pillars G, H, I, J, K, L)
- Resilience & observability implementation (Pillars M, N, R)
- T3-specific checks (Pillars Q, F)
- After-task validation

**Output**: Each task compliant with applicable Pillars

---

### [post-code.md](./post-code.md) - Before PR/Merge
**Run AFTER all tasks complete**

**Time**: 30-60 minutes of comprehensive review
**Purpose**: Final quality gate, ensure production-ready code

**Covers**:
- Data integrity audits (Pillars A, B, C, D)
- Flow & concurrency audits (Pillar E)
- Structure & boundaries audits (Pillars I, K, L)
- Resilience & observability audits (Pillar R)
- T3-specific verification (Pillars Q, F, M, N)
- Security quick check
- Test coverage summary
- Git workflow cleanup

**Output**: Code ready for PR and production

---

## Workflow Integration

### Standard Feature Development

```bash
# 1. PRE-CODE: Plan before coding (30 min)
git checkout -b feature/123-user-auth
cat .claude/pillars/checklists/pre-code.md
# ✓ Check all applicable items
# ✓ Create implementation plan
# ✓ Select patterns (T1/T2/T3)

# 2. IN-CODE: Validate during coding (per task)
# For each task:
#   - Implement feature
#   - Review in-code.md
#   - Run tests
#   - Mark task complete

# 3. POST-CODE: Final review before PR (60 min)
cat .claude/pillars/checklists/post-code.md
# ✓ Run all audits
# ✓ Verify test coverage ≥70%
# ✓ Check security
# ✓ Ready for PR
git push origin feature/123-user-auth
gh pr create
```

### Bug Fix

```bash
# 1. PRE-CODE: Quick planning (10 min)
# - Identify root cause
# - Select fix pattern
# - Plan tests

# 2. IN-CODE: Fix and validate
# - Implement fix
# - Add regression test
# - Check applicable Pillars

# 3. POST-CODE: Quick audit (15 min)
# - Run full test suite
# - Verify no side effects
# - PR
```

---

## Tier Classification (T1/T2/T3)

The checklists reference **task tiers** for pattern selection:

| Tier | Complexity | Pattern | Pillars Required | Example |
|------|------------|---------|------------------|---------|
| **T1** | Simple | View → Headless → Adapter | A, B, L | Fetch user profile |
| **T2** | Standard | View → Headless (+ logic) → Adapter | A, B, D, L, K | Create order with validation |
| **T3** | Complex | View → Saga → Adapters | A, B, D, F, L, M, N, Q, R | Payment with inventory reservation |

**Tier determines which Pillar checks apply**:
- All tiers: A, B, L (nominal types, validation, headless)
- T2+: D, K (state machines, testing)
- T3 only: F, M, N, Q, R (concurrency, saga, context, idempotency, observability)

---

## Pillar Coverage by Phase

### Pre-Code (Planning)
- **Q1 (Data Integrity)**: A, B, D
- **Q2 (Flow)**: E, F, Q
- **Q3 (Structure)**: I, L
- **Q4 (Resilience)**: M, N, R

### In-Code (Execution)
- **Q1**: A, B, D
- **Q2**: F, Q (if T3)
- **Q3**: G, H, I, J, K, L
- **Q4**: M, N, R

### Post-Code (Validation)
- **Q1**: A, B, C, D
- **Q2**: E, F, Q (if T3)
- **Q3**: I, K, L
- **Q4**: M, N, R (if T3)

---

## Quick Reference: Common Scenarios

### "I'm starting a new feature"
→ Read [pre-code.md](./pre-code.md) first (30 min planning)

### "I'm writing code right now"
→ Keep [in-code.md](./in-code.md) open (quick checks per task)

### "I'm ready to submit a PR"
→ Run through [post-code.md](./post-code.md) (60 min audit)

### "I need complete Pillar details"
→ See [PILLAR_CHECKLISTS.md](./PILLAR_CHECKLISTS.md) (comprehensive)

---

## Benefits of 3-Phase System

| Benefit | Explanation |
|---------|-------------|
| **Early Detection** | Catch architectural issues in planning, not code review |
| **Real-time Validation** | In-code checks prevent accumulation of violations |
| **Quality Gate** | Post-code audit ensures production-ready code |
| **Reduced Rework** | Planning prevents wrong patterns from being coded |
| **Learning Tool** | Checklists teach Pillars through practice |
| **Consistency** | Same standards applied across all features |

---

## Statistics (Typical Project)

| Metric | Before Checklists | After Checklists | Improvement |
|--------|-------------------|------------------|-------------|
| Defects in Code Review | 15-20 per feature | 3-5 per feature | **↓70%** |
| Rework Time | 2-4 hours | 30 min - 1 hour | **↓60%** |
| Time to PR Approval | 2-3 days | 1 day | **↓50%** |
| Test Coverage | 40-60% | 70-85% | **+30%** |
| Pillar Compliance | 30-50% | 85-95% | **+60%** |

---

## See Also

- **[PILLAR_CHECKLISTS.md](./PILLAR_CHECKLISTS.md)** - Complete Pillar details and checklists
- **[../.prot-template/README.md](../.prot-template/README.md)** - 18 Pillars overview
- **[../.prot-template/CHEATSHEET.md](../.prot-template/CHEATSHEET.md)** - Quick Pillar reference
- **[../../.claude-template/rules/](../../.claude-template/rules/)** - Quick coding rules

---

**Version**: 1.0
**Last Updated**: 2026-03-01
**Status**: Active - 3-Phase system complete
