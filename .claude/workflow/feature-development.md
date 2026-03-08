# Feature Development Workflow - Complete Lifecycle

> From feature request to development completion. Covers all 4 phases: Documentation, Planning, Development, Release.

---

## 📋 Complete Lifecycle

```
┌──────────────────────────────────────────────────────────────────────┐
│                   FEATURE DEVELOPMENT LIFECYCLE                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  PHASE A          PHASE B: Planning        PHASE C                   │
│  (Docs)           (Two Steps)              (Development)             │
│                                                                       │
│ ┌─────────┐   ┌──────────────┐   ┌──────────────────┐              │
│ │ Docs    │   │ Step 1:      │   │ *issue pick <n>  │              │
│ │ Ready?  │───│ MVP-Level    │───│ Execute phases:  │              │
│ └─────────┘   │ (40 min)     │   │ 1. Pre-code ✓    │              │
│               │              │   │ 2. In-code ✓     │              │
│  ✓ REQ        │ Create       │   │ 3. Tests ✓       │              │
│  ✓ ARCH       │ GitHub       │   │ 4. Review ✓      │              │
│  ✓ SCHEMA     │ Issues       │   │                  │              │
│  ✓ DESIGN     │              │   │ *issue close <n> │              │
│               │              │   └──────────────────┘              │
│               │ ┌──────────────┐                                   │
│               └─│ Step 2:      │                                   │
│                 │ Feature-Level│                                   │
│                 │ (1-2h)       │                                   │
│                 │              │                                   │
│                 │ Create plan+ │                                   │
│                 │ test cases   │                                   │
│                 │              │                                   │
│                 │ Ready to code│                                   │
│                 └──────────────┘                                   │
│                                                                    │
│                    PHASE D: Release                               │
│                    (Tag + Publish)                                │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🟢 Phase A: Documentation (Prerequisite)

Ensure all docs are ready **before** starting Phase B planning:

| Document | What | Examples |
|----------|------|----------|
| REQUIREMENTS.md | User stories for feature | "As a user, I want to add items to cart" |
| ARCHITECTURE.md | Module boundaries | "Cart state in Redux" |
| SCHEMA.md | Data entities | "Cart, CartItem models" |
| DESIGN.md | UI mockups/specs | "Cart drawer screen design" |
| INTERFACES.md | API definitions | "add_to_cart, remove_from_cart endpoints" |

→ See `workflow/Phase-A-Documentation.md` for how to update docs

---

## 🟡 Phase B: Planning (Two Steps)

### Step 1: MVP-Level Decomposition (40 minutes)

**When**: Starting a new MVP release  
**Goal**: Understand what features exist + dependencies  

→ See **[`workflow/MAIN.md#strategy-layer-mvp-planning-40-minutes`](workflow/MAIN.md#strategy-layer-mvp-planning-40-minutes)** for detailed guide

```
MVP3.0 Definition
  ↓
Identify 5-8 features (10 min)
  ├─ Feature-A: Cart state
  ├─ Feature-B: Cart UI
  ├─ Feature-C: Persistence
  └─ Feature-D: Checkout
  ↓
Map dependencies (15 min)
  ├─ Feature-A: none
  ├─ Feature-B: blocked by A
  ├─ Feature-C: blocked by A
  └─ Feature-D: blocked by A, B
  ↓
Create GitHub Issues (15 min)
  ├─ #100: Feature-A (rough: 8h)
  ├─ #101: Feature-B (rough: 6h)
  ├─ #102: Feature-C (rough: 3h)
  └─ #103: Feature-D (rough: 12h)
  ↓
Ready to develop (pick features by priority)
```

**Output**: GitHub Issues with rough sizes + dependency graph

---

### Step 2: Feature-Level Planning (1-2 hours)

**When**: About to develop a specific feature  
**Goal**: Detailed implementation plan + test cases  

→ See **[`workflow/MAIN.md#campaign-layer-feature-planning-1-2-hours-per-feature`](workflow/MAIN.md#campaign-layer-feature-planning-1-2-hours-per-feature)** for detailed guide

```
Feature #100 selected from backlog
  ↓
Validate requirements (15 min)
  ├─ Check REQUIREMENTS.md for user story
  ├─ Check ARCHITECTURE.md for module definition
  └─ Check DESIGN.md for UI specs
  ↓
Create development plan (45 min)
  └─ .claude/feature-100-PLAN.md
     ├─ Step 1: Redux slice (2h)
     ├─ Step 2: UI components (3h)
     └─ Step 3: Tests (1h)
  ↓
Create test cases (45 min)
  └─ .claude/feature-100-TEST-CASES.md
     ├─ TC-1.1, TC-1.2, TC-1.3 (Step 1 tests)
     ├─ TC-2.1, TC-2.2 (Step 2 tests)
     └─ Coverage matrix (100%)
  ↓
Add to GitHub Issue (15 min)
  └─ Issue #100 now has:
     ├─ Development Plan (comment)
     ├─ Test Cases (comment)
     └─ Labels: status/planned, tier/t2, pillar/f, pillar/l
  ↓
Ready to develop
```

**Output**: Ready-to-code GitHub Issue with plan + tests

---

## 🔵 Phase C: Development (Execution)

**When**: After planning is approved  
**How**: Follow 4 coding phases  

→ See `workflow/Phase-C-Development.md` for execution details

```bash
*issue pick <n>      # Load issue #N and plan
```

### Four Development Phases

| Phase | Goal | Time |
|-------|------|------|
| **Phase 1: Pre-Code** | Setup, checklist, pillar review | 15 min |
| **Phase 2: In-Code** | Execute dev plan steps from Step 2 | 2-6h |
| **Phase 3: Tests** | Run test cases from TEST-CASES.md | 30min-2h |
| **Phase 4: Review** | Final audit, optimization | 15-30 min |

```bash
*next            # Phase 1: Pre-code checklist
*next            # Phase 2: Implement Step 1
*next            # Phase 2: Implement Step 2
*next            # Phase 2: Implement Step 3
*next            # Phase 3: Run all tests
*review          # Phase 4: Final review
*issue close <n> # Done
```

---

## 🟣 Phase D: Release

**When**: All MVP features complete  
**Goal**: Version and publish  

→ See `workflow/Phase-D-Release.md` for detailed process

```bash
# Check all MVP features complete
# Version + tag
# Publish
```

---

## 📊 Example: Complete Shopping Cart Feature

### Phase A: Documentation ✓
```
REQUIREMENTS.md: "As a user, I want to add items to cart"
ARCHITECTURE.md: "Cart state in Redux store"
SCHEMA.md: "Cart, CartItem entities defined"
DESIGN.md: "Cart drawer UI mockup created"
```

### Phase B Step 1: MVP Decomposition ✓
```
MVP2.0 Features:
├─ Feature #100: Cart state (8h)
├─ Feature #101: Cart UI (6h, blocked by #100)
├─ Feature #102: Persistence (3h, blocked by #100)
└─ Feature #103: Checkout (12h, blocked by #100, #101)
```

### Phase B Step 2: Feature Planning ✓
```
Feature #100 Plan:
┌─ Step 1: Redux slice (2h) - files, subtasks, tests
├─ Step 2: localStorage (1h) - files, subtasks, tests
└─ Step 3: Integration tests (1h)

Test Cases:
├─ TC-1.1: Add item to cart
├─ TC-1.2: Remove item
├─ TC-1.3: Update quantity
├─ TC-2.1: Persist to localStorage
└─ Coverage: 100% ✓
```

### Phase C: Development ✓
```
Day 1:
  9:00 AM: *issue pick 100
  9:15 AM: *next (Phase 1 setup)
  9:30 AM: *next (Phase 2, Step 1: Redux)
  11:30 AM: *next (Phase 2, Step 2: localStorage)
  12:30 PM: Lunch break
  1:00 PM: *next (Phase 3: Tests)
  2:00 PM: *review (Phase 4)
  2:30 PM: *issue close 100

Day 2:
  9:00 AM: *issue pick 101 (Feature #101)
  → Repeat Phase C for Feature #101
```

### Phase D: Release ✓
```
All MVP2.0 features complete
→ Version 2.0.0
→ Publish
```

---

## ⚡ Timeline Summary

| Phase | Duration | Output |
|-------|----------|--------|
| **A: Documentation** | 1-2h per feature | Docs updated |
| **B1: MVP Planning** | 40 min per MVP | GitHub Issues |
| **B2: Feature Planning** | 1-2h per feature | Dev Plan + Tests |
| **C: Development** | 1-8h per feature | Code + Tests ✓ |
| **D: Release** | 1-2h per release | Published ✓ |

---

## 🎯 Key Principles

1. **Feature is the unit**: 1 feature = 1 GitHub Issue = 1 development cycle
2. **Planning in two steps**: MVP-level (fast) + Feature-level (deep, just-in-time)
3. **Plan before coding**: Feature plan created right before development
4. **Tests from start**: TDD approach with test cases before implementation
5. **Four development phases**: Pre-code → In-code → Tests → Review

---

## ✅ Quick Checklist

**Before Phase C (Development):**
- [ ] Docs ready (REQUIREMENTS, ARCHITECTURE, SCHEMA, DESIGN)
- [ ] GitHub Issue created with goal + acceptance criteria
- [ ] Development plan created and reviewed
- [ ] Test cases created with 100% coverage
- [ ] Issue labeled and approved

**During Phase C (Development):**
- [ ] Follow dev plan steps in order
- [ ] Run test cases after each step
- [ ] Commit with issue reference (#N)

**After Phase C (Development):**
- [ ] All test cases passed
- [ ] Code reviewed
- [ ] Issue closed
- [ ] Ready for next feature

---

## 🔗 See Also

- **Phase A (Docs)**: `workflow/Phase-A-Documentation.md`
- **Phase B Step 1 (MVP)**: `workflow/workflow/MAIN.md#strategy-layer-mvp-planning-40-minutes`
- **Phase B Step 2 (Feature)**: `workflow/workflow/MAIN.md#campaign-layer-feature-planning-1-2-hours-per-feature`
- **Phase C (Development)**: `workflow/Phase-C-Development.md`
- **Phase D (Release)**: `workflow/Phase-D-Release.md`
- **Architecture**: `workflow/architecture-core.md`

