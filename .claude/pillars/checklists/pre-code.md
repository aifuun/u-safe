# Pre-Code Checklist

> Run BEFORE writing any implementation code
>
> **Full Details**: See [PILLAR_CHECKLISTS.md](./PILLAR_CHECKLISTS.md#quick-lookup-checklist-by-phase) for complete checklists.

## Essential Pre-Code Checks

### 0. Git Workflow Setup

- [ ] **Create feature branch** (if starting new issue/feature)
  ```bash
  git checkout main  # Or development, depending on project
  git pull origin main
  git checkout -b feature/<issue-number>-<short-description>
  ```
  - **Example**: `feature/15-user-authentication`
  - **Never** code directly on `main` or `development`
  - **Branch naming**: `feature/<issue>-<description>` or `bugfix/<issue>-<description>`

---

### 1. Task Classification

- [ ] Task complexity classified: **T1** (Simple) / **T2** (Standard) / **T3** (Complex)
- [ ] Pattern selected matching complexity:
  - **T1**: View → Headless → Adapter (single operation)
  - **T2**: View → Headless (+ validation) → Adapter (multiple operations)
  - **T3**: View → Saga → Adapters (distributed transaction)

→ **Full checklist**: [Pillar E: Adaptive Orchestration](../pillars/q2-flow-concurrency/pillar-e/orchestration.md)

---

### 2. Data Integrity (Q1)

#### Pillar A: Nominal Typing
- [ ] Domain IDs identified (UserId, OrderId, ProductId, etc.)
- [ ] Branded types defined for all domain IDs
- [ ] No primitive types (string/number) for domain entities

→ **Full checklist**: [Pillar A: Nominal Typing](../pillars/q1-data-integrity/pillar-a/nominal-typing.md)

#### Pillar B: Airlock (Schema Validation)
- [ ] External data sources identified (API, user input, database)
- [ ] Zod/validation schemas defined for all boundaries
- [ ] Upcast strategy planned for legacy data migration

→ **Full checklist**: [Pillar B: Airlock](../pillars/q1-data-integrity/pillar-b/airlock.md)

#### Pillar D: FSM (State Machines)
- [ ] States identified (not boolean flags like `isLoading`, `hasError`)
- [ ] State transitions defined explicitly
- [ ] State machine diagram created (if complex)

→ **Full checklist**: [Pillar D: FSM](../pillars/q1-data-integrity/pillar-d/fsm.md)

---

### 3. Flow & Concurrency (Q2)

#### Pillar E: Orchestration
- [ ] Task tier identified (T1/T2/T3)
- [ ] Flow pattern matches tier (simple/standard/saga)
- [ ] No over-engineering for simple tasks

→ **Full checklist**: [Pillar E: Orchestration](../pillars/q2-flow-concurrency/pillar-e/orchestration.md)

#### Pillar F: Concurrency (If T3)
- [ ] Concurrent write scenarios identified
- [ ] Version field added to data model
- [ ] Optimistic locking strategy planned (CAS pattern)

→ **Full checklist**: [Pillar F: Concurrency](../pillars/q2-flow-concurrency/pillar-f/concurrency.md)

#### Pillar Q: Idempotency (If T3)
- [ ] Critical operations identified (payments, orders, critical writes)
- [ ] Idempotency key mechanism designed
- [ ] Cache/result store strategy planned

→ **Full checklist**: [Pillar Q: Idempotency](../pillars/q2-flow-concurrency/pillar-q/idempotency.md)

---

### 4. Structure & Boundaries (Q3)

#### Pillar I: Firewalls
- [ ] Layer structure defined (kernel → domains → modules → views)
- [ ] Allowed import directions documented
- [ ] Public APIs (`index.ts` or equivalent) planned

→ **Full checklist**: [Pillar I: Firewalls](../pillars/q3-structure-boundaries/pillar-i/firewalls.md)

#### Pillar L: Headless
- [ ] Business logic separated from UI in design
- [ ] Headless hooks/functions API designed
- [ ] Hooks will contain NO UI code (no JSX/HTML templates)

→ **Full checklist**: [Pillar L: Headless](../pillars/q3-structure-boundaries/pillar-l/headless.md)

---

### 5. Resilience & Observability (Q4)

#### Pillar M: Saga (For T3 Only)
- [ ] Multi-service operations identified
- [ ] Compensation actions designed for each step
- [ ] Saga flow diagram created

→ **Full checklist**: [Pillar M: Saga](../pillars/q4-resilience-observability/pillar-m/saga.md)

#### Pillar N: Context
- [ ] Context structure designed (traceId, userId, requestId)
- [ ] Context propagation mechanism planned
- [ ] All logs will include traceId

→ **Full checklist**: [Pillar N: Context](../pillars/q4-resilience-observability/pillar-n/context.md)

#### Pillar R: Observability
- [ ] Logging strategy planned (structured JSON)
- [ ] Semantic log IDs planned (domain:entity:action format)
- [ ] Critical paths identified for detailed logging

→ **Full checklist**: [Pillar R: Observability](../pillars/q4-resilience-observability/pillar-r/observability.md)

---

## Proceed When

✅ All applicable items checked → Create/update issue plan → Start coding

---

## Related Resources

- **Complete Checklists**: [PILLAR_CHECKLISTS.md](./PILLAR_CHECKLISTS.md) - All 18 Pillars with full details
- **Quick Reference**: [../.prot-template/CHEATSHEET.md](../.prot-template/CHEATSHEET.md) - One-page overview
- **Next Phase**: [in-code.md](./in-code.md) - Checklist during implementation
