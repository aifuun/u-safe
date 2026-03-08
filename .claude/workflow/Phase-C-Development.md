# Phase C: Development

> Part of the 4-Phase AI-Assisted Development Workflow
> See: [MAIN.md](./MAIN.md) for complete overview

## Overview

Phase C is where you **execute the implementation plan** created in Phase B planning.

```
*issue pick <n>
     │
     ▼
[Tier Classification] → [Pre-Code] → [Implementation] → [Testing] → [Review]
```

---

## Issue Management

| Command | Description |
|---------|-------------|
| `*issue` | List open issues |
| `*issue pick <n>` | Start working on issue |
| `*issue close <n>` | Complete issue |

### *issue pick Flow

**Prerequisite**: Issue should have:
- ✅ Detailed development plan (from Phase B planning)
- ✅ Plan added to issue comment
- ✅ Test cases defined
- ✅ Status labeled as `status/planned`

**If issue is missing these, return to Phase B Planning first.**

---

## Execution Phases

### Phase 1: Tier Classification (Optional)

**When to run `*tier`**:
- ✅ Data writes: "Save user profile", "Update cart"
- ✅ State management: "Form with validation", "Multi-step wizard"
- ✅ External IO: "Fetch from API", "Call Tauri IPC"
- ✅ Critical operations: "Payment", "File sync", "Account deletion"
- ❌ Skip: "Fix button color", "Update text", "Add icon"

**Process**:
1. Analyze task requirements
2. Classify into T1/T2/T3
3. Identify relevant Pillars

| Tier | When | Pillars |
|------|------|---------|
| T1 | Read-only | A, I, L |
| T2 | Local state | A, D, I, J, L |
| T3 | Distributed | A, B, D, F, M, Q, R |

---

### Phase 2: Pre-Code Audit

**Checklist**:
- [ ] Correct layer? (Domain/Module/Adapter)
- [ ] Branded Types for IDs? (Pillar A)
- [ ] FSM for state? (Pillar D)
- [ ] T3: Intent-ID planned? (Pillar Q)
- [ ] T3: Compensation defined? (Pillar M)

**Templates**: Use `.prot/pillar-*/` templates for reference.

---

### Phase 3: Implementation & Testing

**Execution**:
1. Follow development plan steps
2. Write unit tests (100% coverage)
3. Write integration tests (real dependencies)
4. Run `npm test` for full project validation

**Critical** (from Issue #89): Both unit AND integration tests required:
- **Unit tests**: Mock all dependencies
- **Integration tests**: Mock only external services, keep internal modules real

---

### Phase 4: Post-Code Review

**Complete Review Workflow**:

#### Step 1: Module Tests
```bash
npm test -- <module-name>
```
- [ ] All unit tests pass
- [ ] All integration tests pass

#### Step 2: Full Project Tests (REQUIRED)
```bash
npm test
```
- [ ] All 517+ tests pass
- [ ] No new test failures

#### Step 3: Build Verification
```bash
npm run build
```
- [ ] Compilation succeeds
- [ ] No TypeScript errors

#### Step 4: Code Quality
```bash
npm run lint
```
- [ ] No linting errors
- [ ] Code style consistent

#### Step 5: Structural Review

- [ ] No deep imports (Pillar I)
- [ ] Headless/View separation (Pillar L)
- [ ] State locality (Pillar J)

**T3 Review** (if Tier == T3):
- [ ] Idempotency barrier (Pillar Q)
- [ ] Version checks (Pillar F)
- [ ] Compensation complete (Pillar M)
- [ ] Semantic logs (Pillar R)

---

## Command Reference

| Command | Phase | Description |
|---------|-------|-------------|
| `*tier` | 1 | Classify complexity |
| `*next` | 3 | Execute next step |
| `*review` | 4 | Post-code review |
| `*sync` | Any | Save & push |

---

## Best Practices

- Follow the development plan from Phase B
- Test as you code (unit + integration)
- Run full test suite before review
- Use Pillar templates as reference
- Commit frequently with clear messages

---

## Next Phase

See [Phase-D-Release.md](./Phase-D-Release.md) for release and deployment.

---

**Part of**: 4-Phase Workflow (A → B → **C** → D)
