# Workflow & MVP→Issues→TODO Quick Reference

**一页纸快速理解三层架构如何运作**

---

## 🗂️ Three-Layer Breakdown

```
LAYER 1: MVP (Strategic)          LAYER 2: Issues (Tactical)        LAYER 3: TODO (Operational)
docs/dev/MVP*.md                  GitHub #N + comments              .claude/plans/active/

Goal: Shopping Cart               Goal: Cart state management       Goal: Today's work

Business objective                Technical implementation          Session progress
Acceptance criteria               Dev plan + test cases             Sub-task checklist
Related Issues (links)            Pillar alignment                  Next steps
Environment setup                 Effort estimate                   Time tracking
                                                                    
Updated: Per release              Updated: During planning          Updated: Per session
1-4 weeks lifecycle               1-7 days lifecycle                Same-day lifecycle
Public-facing                     Team/AI-facing                    AI-facing only
```

---

## 📍 Where Does the Workflow Fit?

```
YOU (Feature Request or MVP)
     │
     ▼
PHASE B: Planning (workflow/planning.md Steps 0-8)
     │
     ├─ Step 0: Check MVP for requirements
     ├─ Step 1: Analyze scope
     ├─ Step 2: Open GitHub Issue #N ← CREATES GitHub Issue Layer
     ├─ Step 3: Decompose features
     ├─ Step 4: Create detailed plan → .claude/*-PLAN.md
     ├─ Step 5: Evaluate & optimize
     ├─ Step 6: Add plan to Issue comment ← POPULATES Issue comments
     ├─ Step 7: Create test cases → .claude/*-TEST-CASES.md ← ADDS Test Cases
     └─ Step 8: Apply labels ← UPDATES Issue labels
     │
     ▼
GitHub Issue #N is READY (has plan, test cases, labels)
     │
     ▼
PHASE C: Development (workflow/Phase-C-Development.md)
     │
     ├─ *issue pick #N → LOADS GitHub Issue, CREATES plans/active/ entry ← CREATES plans/active/ Layer
     ├─ *next (Phase 1) → Pre-code checklist
     ├─ *next (Phase 2-3) → Execute steps from dev plan (from Issue comment)
     ├─ *review (Phase 4) → Final check
     └─ *issue close #N → CLOSES Issue, CLEARS plans/active/, UPDATES MVP
     │
     ▼
MVP file updated (acceptance criteria checked)
```

---

## 🔄 Workflow Integration Points

| Workflow Step | Input | Output | Which Layer |
|---------------|-------|--------|------------|
| Step 0: Check docs | MVP file | Docs verified | L1: MVP |
| Step 2: Open Issues | Feature requirement | GitHub Issue #N | L2: Issues |
| Step 4: Create plan | Feature decomposition | .claude/*-PLAN.md | L2: Issues (comment) |
| Step 7: Test cases | Dev plan | .claude/*-TEST-CASES.md | L2: Issues (comment) |
| *issue pick | GitHub Issue #N | plans/active/ entry | L3: TODO |
| *next Phase 1-4 | Dev plan + tests | Code + commits | L3: TODO |
| *issue close | Complete code | Close Issue + update MVP | L1: MVP |

---

## 🎯 The *next Command: Three-Level Recommendation Engine

```
*next command logic:

├─ LEVEL 1: Check plans/active/ (Current Session)
│  ├─ Active issue?
│  │  ├─ YES → Show next sub-task from dev plan
│  │  │        Execute it (Phase 1-4)
│  │  │        Update plans/active/ checklist
│  │  └─ NO → Go to Level 2
│  └─ All steps done? → *issue close #N
│
├─ LEVEL 2: Check GitHub Issues (Current MVP)
│  ├─ Unfinished issues?
│  │  ├─ YES → Recommend next priority issue
│  │  │        Ask: "Start #M? (y/n)"
│  │  │        Load plan from Issue comment
│  │  │        Create plans/active/ entry
│  │  └─ NO → Go to Level 3
│  └─ Load dev plan from Issue comment
│
└─ LEVEL 3: Check next MVP (Strategic)
   ├─ All issues done?
   │  ├─ YES → Recommend next MVP file
   │  │        Ask: "Plan MVP3.1? (y/n)"
   │  │        Suggest running workflow/planning.md
   │  └─ NO → Done
   └─ Load MVP file
```

**Example in action**:

```bash
Session 1:
$ *issue pick 99
# plans/active/ created with #99, loads dev plan from Issue comment

$ *next
# Level 1: Shows "Step 1: Fix timestamp bug", ready to code

$ *next (after Step 1 done)
# Level 1: Shows "Step 2: Create roadmap"

$ *next (after all steps done)
# Recommends: *issue close 99

$ *issue close 99
# Closes #99 in GitHub, clears plans/active/ entry

---

Session 2 (new day):
$ *resume
# Loads MEMORY.md

$ *next
# Level 2: No active issue in plans/active/
# Checks GitHub for MVP3.1 issues
# Recommends: "Start #102 SQS+DLQ? (y/n)"

$ *issue pick 102
# Loads #102, creates new plans/active/ entry with dev plan from comment

$ *next
# Level 1: Shows first step from #102 dev plan
```

---

## 📊 Complete Session Lifecycle

### Before Coding (Phase B: Planning)

```
Step 1: Feature Request arrives
        ↓
Step 2: Check MVP for requirements (workflow/planning.md Step 0)
        ↓
Step 3: Create/update GitHub Issue #N with dev plan (Steps 2-7)
        ├─ Issue description
        ├─ Acceptance criteria
        ├─ Comment: Dev plan (.claude/*-PLAN.md)
        ├─ Comment: Test cases (.claude/*-TEST-CASES.md)
        └─ Labels: status/planned, tier/*, pillar/*
        ↓
Step 4: Issue is READY
```

### During Coding (Phase C: Development)

```
Step 1: *issue pick #N
        ├─ Loads: GitHub Issue + comments (dev plan + tests)
        ├─ Creates: plans/active/ entry with sub-tasks from dev plan
        └─ Status: Issue = in-progress
        ↓
Step 2: *next (Phase 1: Pre-code)
        ├─ Load templates and checklists
        ├─ Check Pillar concerns
        └─ Prepare environment
        ↓
Step 3: *next (Phase 2: In-code)
        ├─ For each sub-task in plans/active/:
        │  ├─ Execute step from dev plan
        │  ├─ Follow Pillar template
        │  ├─ Run tests
        │  └─ Mark complete ☑️
        └─ Status: plans/active/ checklist progresses
        ↓
Step 4: *review (Phase 4: Post-code)
        ├─ Final audit
        └─ Check coverage
        ↓
Step 5: *issue close #N
        ├─ Closes: GitHub Issue #N
        ├─ Clears: plans/active/ entry
        ├─ Commits: With Issue ID
        ├─ Archives: Decision to MEMORY.md
        └─ Updates: MVP acceptance criteria
        ↓
Step 6: *sync
        ├─ Pushes: To remote
        └─ Session complete
```

---

## 🔗 Data Flow Diagram

```
┌─────────────┐
│  MVP File   │
│ (Strategic) │
└──────┬──────┘
       │ Step 0: Extract requirements
       ▼
┌──────────────────────────────────────────────┐
│  Planning Workflow (workflow/planning.md)     │
│  Steps 0-8: Plan → Evaluate → Confirm       │
└──────┬───────────────────────────────────────┘
       │ Step 2-7: Create GitHub Issue
       ▼
┌─────────────────────────┐
│   GitHub Issue #N       │
│ + Dev Plan Comment      │
│ + Test Cases Comment    │
│ + Labels                │
│ (Tactical)              │
└──────┬──────────────────┘
       │ *issue pick #N: Load Issue
       ▼
┌──────────────────────────┐
│  plans/active/ (Session)       │
│  - Issue title           │
│  - Sub-tasks checklist   │
│  (Operational)           │
└──────┬───────────────────┘
       │ *next: Execute sub-tasks from dev plan
       ▼
┌──────────────────────────┐
│  Development (Phase 1-4) │
│  - Follow templates      │
│  - Run tests (from test  │
│    cases comment)        │
│  - Mark steps complete   │
└──────┬───────────────────┘
       │ *issue close #N
       ▼
┌─────────────┐
│  MVP File   │
│  Updated    │
└─────────────┘
```

---

## ✅ What Each Layer Should Contain

### MVP Layer (docs/dev/MVP*.md)

✅ DO:
- Business objective (1 sentence)
- Acceptance criteria (checklist with ☐)
- Issues list (with #N links)
- Environment setup
- Dependencies

❌ DON'T:
- Code implementation details
- Technical decision records
- Test scenarios
- Sub-task breakdowns

### Issues Layer (GitHub #N)

✅ DO:
- Issue title (clear and specific)
- Goal statement
- Acceptance criteria (checklist)
- Development plan (from Step 4)
- Test cases (from Step 7)
- Labels (status, tier, pillars)
- Discussion history

❌ DON'T:
- Duplicate MVP content
- Just a title with no context
- Missing dev plan/test cases
- No pillar alignment

### Issue Plan Layer (.claude/plans/active/)

✅ DO:
- Current session date
- Active issues (1-3 max)
- Sub-task checklist (from dev plan)
- Progress marks (☑️)
- Next up issues
- Blocked items

❌ DON'T:
- Mirror GitHub Issues content
- Save historical data
- Keep old sessions
- Include implementation details

---

## 🚀 Quick Start: From Feature to Completion

```bash
# Planning Phase (1-2 hours)
cd docs/dev
# Update or create MVP*.md with your feature

# Then follow workflow/planning.md:
# Step 0: Check docs ✓
# Step 1: Analyze ✓
# Step 2: Create Issue #N
# Step 3-8: Plan, evaluate, confirm, test cases, labels

---

# Development Phase (per session)

# Session Start
$ *resume
$ *issue pick <N>
$ *next  # Phase 1: Pre-code
$ *next  # Phase 2-3: Execute dev plan steps
$ *next  # Phase 4: Review
$ *issue close <N>
$ *sync

---

# Next Session
$ *resume
$ *next
# → Recommends next Issue from GitHub or next MVP

$ *issue pick <M>
# → Repeat...
```

---

## 📚 Reference

**For detailed information**:
- Architecture: `@workflow/architecture-core.md`
- Planning steps: `@workflow/planning.md`
- Development steps: `@workflow/Phase-C-Development.md`
- Feature workflow: `@workflow/feature-development.md`

**For standards**:
- MVP pattern: `@.claude/rules/workflow.md`
- Pillar compliance: `@.prot/AI_DEV_PROT_v15.md`
- Code checklists: `@.prot/checklists/`

