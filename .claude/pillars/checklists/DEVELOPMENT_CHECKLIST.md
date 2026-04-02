# Development Checklist - Complete Workflow

> Unified checklist for the entire development lifecycle: **Planning → Implementation → Review**
>
> **Full Pillar Details**: See [PILLAR_CHECKLISTS.md](./PILLAR_CHECKLISTS.md) for comprehensive guidance on all 18 Pillars.

---

## 📋 Quick Navigation

- **Phase 1: Pre-Code (Planning)** → [Jump to Planning](#phase-1-pre-code-planning)
- **Phase 2: In-Code (Implementation)** → [Jump to Implementation](#phase-2-in-code-implementation)
- **Phase 3: Post-Code (Review)** → [Jump to Review](#phase-3-post-code-review)

---

# PHASE 1: PRE-CODE PLANNING

> **When**: Before writing any implementation code
> **Who**: Architect, Tech Lead, Developer planning the task
> **Duration**: 30-40 minutes
> **Commands**: `*tier`, `*plan`, `*approve`

## 1. Tier Classification

Determine the complexity tier for this task:

- [ ] Task tier classified: **T1** / **T2** / **T3**
- [ ] Pattern selected matching tier:
  - **T1** (Direct/Read): View → Headless → Adapter
  - **T2** (Logic/Forms): View → Headless (+ logic) → Adapter
  - **T3** (Saga/Distributed): View → Saga → Adapters

→ **Full Details**: [Pillar E: Adaptive Orchestration](./PILLAR_CHECKLISTS.md#pillar-e-adaptive-orchestration-tier-classification)

---

## 2. Data Integrity (Q1) Design

### Pillar A: Nominal Typing
- [ ] Domain IDs identified (UserId, OrderId, PaymentId, etc.)
- [ ] Branded types defined for all IDs
- [ ] No primitive types (string/number) for domain entities

→ [Pillar A: Nominal Typing](./PILLAR_CHECKLISTS.md#pillar-a-nominal-typing)

### Pillar B: Airlock (Schema Validation)
- [ ] External data sources identified (API, user input, database, file)
- [ ] Zod schemas defined for all boundaries
- [ ] Upcast strategy planned for legacy data handling

→ [Pillar B: Airlock](./PILLAR_CHECKLISTS.md#pillar-b-airlock-schema-validation)

### Pillar D: FSM (State Machines)
- [ ] States identified (not boolean flags)
- [ ] State transitions defined and documented
- [ ] State machine diagram created

→ [Pillar D: FSM](./PILLAR_CHECKLISTS.md#pillar-d-fsm-state-machines)

---

## 3. Flow & Concurrency (Q2) Design

### Pillar F: Concurrency
- [ ] Concurrent write scenarios identified
- [ ] Version field planned for mutable entities
- [ ] Optimistic locking strategy documented

→ [Pillar F: Concurrency](./PILLAR_CHECKLISTS.md#pillar-f-concurrency-cas-locking)

### Pillar Q: Idempotency (T3 Only)
- [ ] Critical operations identified (payments, transfers, orders)
- [ ] `intentId` mechanism designed
- [ ] Cache strategy for intent results planned

→ [Pillar Q: Idempotency](./PILLAR_CHECKLISTS.md#pillar-q-idempotency)

---

## 4. Structure & Boundaries (Q3) Design

### Pillar I: Firewalls
- [ ] Layer structure defined (kernel, domains, modules, migrations)
- [ ] Allowed import directions documented
- [ ] Public APIs (`index.ts` exports) planned

→ [Pillar I: Firewalls](./PILLAR_CHECKLISTS.md#pillar-i-firewalls-import-boundaries)

### Pillar L: Headless (Frontend Only)
- [ ] Business logic vs UI separated in design
- [ ] Headless hooks API designed
- [ ] Hooks will have NO JSX (zero exceptions)

→ [Pillar L: Headless](./PILLAR_CHECKLISTS.md#pillar-l-headless-logic-ui-separation)

---

## 5. Resilience & Observability (Q4) Design

### Pillar M: Saga (T3 Only)
- [ ] Multi-service operations identified
- [ ] Compensation actions designed for each step
- [ ] Saga flow diagram created (ASCII or Figma)

→ [Pillar M: Saga](./PILLAR_CHECKLISTS.md#pillar-m-saga-compensation-pattern)

### Pillar N: Context
- [ ] Context structure designed (traceId, userId, intentId)
- [ ] Context propagation mechanism planned
- [ ] All logs will include traceId field

→ [Pillar N: Context](./PILLAR_CHECKLISTS.md#pillar-n-context-traceid-propagation)

---

## Pre-Code Summary

✅ **Ready for Implementation When**:
- [ ] All applicable items above are checked
- [ ] Issue plan created with checklist results
- [ ] Approval received from tech lead/architect
- [ ] Ready to start coding

**Next**: → Proceed to **Phase 2: In-Code Implementation**

---

# PHASE 2: IN-CODE IMPLEMENTATION

> **When**: During implementation, per task/feature
> **Who**: Developer implementing the code
> **Duration**: Continuous during development
> **Commands**: `*next` (per task), continuous verification

## Implementation Phase Overview

As you code each task, verify these items. This is a continuous checklist, not a one-time review.

---

## 1. Data Integrity (Q1) Implementation

### Pillar A: Nominal Typing
- [ ] All domain IDs use branded types (not primitive string/number)
- [ ] Factory functions validate before creating IDs
- [ ] No `as` type casts for domain IDs
- [ ] TypeScript compiler prevents ID type mismatches

→ [Pillar A: Nominal Typing](./PILLAR_CHECKLISTS.md#pillar-a-nominal-typing)

### Pillar B: Airlock (Schema Validation)
- [ ] Every adapter/boundary has schema validation (`.parse()` or `.safeParse()`)
- [ ] Validation at boundary, not scattered in business logic
- [ ] Upcast functions handle legacy data formats gracefully
- [ ] No `any` types from external sources

→ [Pillar B: Airlock](./PILLAR_CHECKLISTS.md#pillar-b-airlock-schema-validation)

---

## 2. Structure & Boundaries (Q3) Implementation

### Pillar L: Headless (Frontend Only)
- [ ] **NO JSX in headless hooks** (zero exceptions)
- [ ] Hooks return data and functions only
- [ ] All business logic in headless, not in View components
- [ ] Business logic unit-testable without React

→ [Pillar L: Headless](./PILLAR_CHECKLISTS.md#pillar-l-headless-logic-ui-separation)

### Pillar D: FSM
- [ ] State represented as enum/union type, not booleans
- [ ] State transitions are explicit functions
- [ ] Invalid transitions prevented by type system
- [ ] State machine tested comprehensively

→ [Pillar D: FSM](./PILLAR_CHECKLISTS.md#pillar-d-fsm-state-machines)

### Pillar G: Traceability
- [ ] `@trigger` comment on user action handlers
- [ ] `@listen` comment on event listeners
- [ ] `@ai-intent` comment on AI-generated code sections
- [ ] Comments explain intent, not just what code does

→ [Pillar G: Traceability](./PILLAR_CHECKLISTS.md#pillar-g-traceability)

### Pillar H: Policy (Authorization)
- [ ] Authorization checks in dedicated policy functions
- [ ] Business logic does NOT contain role/permission checks
- [ ] Policy violations throw `ForbiddenError`
- [ ] Policies centralized and testable

→ [Pillar H: Policy](./PILLAR_CHECKLISTS.md#pillar-h-policy-authorization)

### Pillar I: Firewalls
- [ ] Imports follow dependency rule (outer → inner only)
- [ ] No deep imports (`../../../module/internal`)
- [ ] Public API via `index.ts` exports only
- [ ] ESLint boundary checks passing

→ [Pillar I: Firewalls](./PILLAR_CHECKLISTS.md#pillar-i-firewalls-import-boundaries)

### Pillar J: Locality
- [ ] Component state for component-only data (UI state)
- [ ] Page state for page-wide data
- [ ] Global state only for truly application-wide data (auth, theme)
- [ ] State lifted to correct component level

→ [Pillar J: Locality](./PILLAR_CHECKLISTS.md#pillar-j-locality-state-proximity)

### Pillar K: Testing
- [ ] Unit tests written for business logic
- [ ] Test coverage ≥70% for this feature
- [ ] Tests use mock factories, not inline object literals
- [ ] Tests are fast (<1s per test)

→ [Pillar K: Testing](./PILLAR_CHECKLISTS.md#pillar-k-testing-test-pyramid)

---

## 3. Resilience & Observability (Q4) Implementation

### Pillar M: Saga (T3 Only)
- [ ] Each saga step has compensation function
- [ ] Compensation stack built as saga executes
- [ ] On failure, compensations run in reverse order
- [ ] Saga resumable after infrastructure recovery

→ [Pillar M: Saga](./PILLAR_CHECKLISTS.md#pillar-m-saga-compensation-pattern)

### Pillar N: Context
- [ ] Every request generates unique `traceId` (UUID)
- [ ] Context passed to all functions (explicit parameter, not global)
- [ ] All logs include `traceId` field for correlation
- [ ] Cross-service tracing enables end-to-end debugging

→ [Pillar N: Context](./PILLAR_CHECKLISTS.md#pillar-n-context-traceid-propagation)

### Pillar R: Observability
- [ ] All logs are structured JSON (not string interpolation)
- [ ] Logs include semantic fields (userId, orderId, operationId)
- [ ] Log levels used correctly (ERROR, WARN, INFO, DEBUG)
- [ ] No `console.log` in code (use structured logging)

→ [Pillar R: Observability](./PILLAR_CHECKLISTS.md#pillar-r-observability-semantic-logging)

---

## T3-Specific Implementation (Tier 3 Only)

If implementing Tier 3 (Saga with distributed operations):

### Pillar Q: Idempotency
- [ ] Client generates `intentId` for each operation
- [ ] Server checks cache/database before executing
- [ ] Result cached with `intentId` key
- [ ] Cache has appropriate TTL and cleanup

→ [Pillar Q: Idempotency](./PILLAR_CHECKLISTS.md#pillar-q-idempotency)

### Pillar F: Concurrency
- [ ] Version field present in mutable entities
- [ ] Read includes version, write checks version
- [ ] Stale version throws `ConflictError`
- [ ] Race condition scenarios tested

→ [Pillar F: Concurrency](./PILLAR_CHECKLISTS.md#pillar-f-concurrency-cas-locking)

---

## After Each Task

- [ ] Run unit tests for this code (should pass)
- [ ] Mark GitHub TODO item complete
- [ ] No `console.log` left in code
- [ ] No debugging code remains
- [ ] Related Pillar items reviewed above

---

## In-Code Summary

✅ **Ready for Review When**:
- [ ] All applicable implementation items checked
- [ ] Tests passing (unit tests ≥70% coverage)
- [ ] Code follows Pillar patterns
- [ ] Ready for code review (phase 3)

**Next**: → Proceed to **Phase 3: Post-Code Review**

---

# PHASE 3: POST-CODE REVIEW

> **When**: After all implementation tasks complete, before issue closure
> **Who**: Code Reviewer, Tech Lead, QA
> **Duration**: 20-30 minutes per issue
> **Commands**: `*review`, `*issue close`

## Post-Code Verification & Audit

This is the final comprehensive audit before issue closure. All implementation is complete; this phase verifies quality standards.

---

## 1. Data Integrity (Q1) Audit

### Pillar A: Nominal Typing
- [ ] No primitive types for domain entities anywhere in codebase
- [ ] All ID parameters use branded types
- [ ] TypeScript compiler catches type mismatches at compile time

→ [Pillar A: Nominal Typing](./PILLAR_CHECKLISTS.md#pillar-a-nominal-typing)

### Pillar B: Airlock (Schema Validation)
- [ ] All external data validated with Zod schemas
- [ ] No `any` types from external sources
- [ ] Schema tests verify validation logic
- [ ] Edge cases handled (empty, null, invalid formats)

→ [Pillar B: Airlock](./PILLAR_CHECKLISTS.md#pillar-b-airlock-schema-validation)

### Pillar C: Mocking
- [ ] All tests use factories, not inline object literals
- [ ] No magic strings in tests (use named constants)
- [ ] Mock data is realistic and diverse (multiple scenarios)

→ [Pillar C: Mocking](./PILLAR_CHECKLISTS.md#pillar-c-mocking-test-data)

### Pillar D: FSM
- [ ] No boolean flags for state (states are enums/unions)
- [ ] State transitions testable and predictable
- [ ] State machine diagram present and accurate

→ [Pillar D: FSM](./PILLAR_CHECKLISTS.md#pillar-d-fsm-state-machines)

---

## 2. Flow & Concurrency (Q2) Audit

### Pillar E: Adaptive Orchestration
- [ ] Tier documented in PR description
- [ ] Pattern matches tier classification (no over/under-engineering)
- [ ] Orchestration strategy verified

→ [Pillar E: Orchestration](./PILLAR_CHECKLISTS.md#pillar-e-adaptive-orchestration-tier-classification)

---

## 3. Structure & Boundaries (Q3) Audit

### Pillar I: Firewalls
- [ ] No circular dependencies detected
- [ ] Layer boundaries respected throughout
- [ ] ESLint boundary checks passing (100%)

→ [Pillar I: Firewalls](./PILLAR_CHECKLISTS.md#pillar-i-firewalls-import-boundaries)

### Pillar K: Testing
- [ ] Overall coverage ≥80%
- [ ] Unit tests are fast (<1s total suite)
- [ ] E2E tests minimal and stable
- [ ] Critical paths well-tested

→ [Pillar K: Testing](./PILLAR_CHECKLISTS.md#pillar-k-testing-test-pyramid)

### Pillar L: Headless (Frontend Only)
- [ ] Verified: NO JSX in headless hooks
- [ ] All hooks unit tested (without React)
- [ ] Components thin and declarative

→ [Pillar L: Headless](./PILLAR_CHECKLISTS.md#pillar-l-headless-logic-ui-separation)

---

## 4. Resilience & Observability (Q4) Audit

### Pillar R: Observability
- [ ] Logs queryable by semantic fields (userId, orderId, etc.)
- [ ] All errors logged with full context
- [ ] No `console.log` in production code
- [ ] CloudWatch/monitoring queries validate log structure

→ [Pillar R: Observability](./PILLAR_CHECKLISTS.md#pillar-r-observability-semantic-logging)

---

## T3-Specific Verification (Tier 3 Only)

If Tier 3 (Saga) was implemented:

### Pillar Q: Idempotency
- [ ] Critical operations are idempotent
- [ ] Retry tests confirm same result every time
- [ ] Intent cache has appropriate TTL
- [ ] Cache cleanup tested

→ [Pillar Q: Idempotency](./PILLAR_CHECKLISTS.md#pillar-q-idempotency)

### Pillar F: Concurrency
- [ ] All concurrent writes use version checking
- [ ] Conflict scenarios tested and handled
- [ ] Race condition prevention verified with stress tests

→ [Pillar F: Concurrency](./PILLAR_CHECKLISTS.md#pillar-f-concurrency-cas-locking)

### Pillar M: Saga
- [ ] All multi-service operations use saga pattern
- [ ] Failure scenarios tested with compensation
- [ ] Saga logs enable step-by-step auditing

→ [Pillar M: Saga](./PILLAR_CHECKLISTS.md#pillar-m-saga-compensation-pattern)

### Pillar N: Context
- [ ] All operations traceable via traceId
- [ ] Logs can be filtered by traceId (demonstrable)
- [ ] Cross-service tracing works end-to-end

→ [Pillar N: Context](./PILLAR_CHECKLISTS.md#pillar-n-context-traceid-propagation)

---

## Security Quick Check

- [ ] No secrets in code (AWS keys, API tokens, etc.)
- [ ] Input validated at all boundaries (Pillar B)
- [ ] No SQL/command injection risks
- [ ] Authorization checks present (Pillar H)
- [ ] Sensitive data not logged

---

## Test Coverage Summary

| Layer | Minimum Required | Actual |
|-------|------------------|--------|
| Domain / Business Logic | 100% | ___% |
| Headless / Hooks | ≥80% | ___% |
| Adapters / Boundaries | Contract Tests | ___% |
| Workflows (T3) | Integration Tests | ___% |
| **Overall** | **≥80%** | ___% |

---

## Final Verdict

```
□ ✅ PASS - Ready for *issue close
□ ⚠️  NEEDS_FIX - Create follow-up fix tasks
□ ❌ REJECT - Return to development phase
```

**Review Notes**:
```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

---

## Post-Code Summary

✅ **Issue Ready for Closure When**:
- [ ] All applicable audit items checked
- [ ] Final verdict is PASS
- [ ] All Pillar items verified
- [ ] Security check passed
- [ ] Test coverage meets standards

---

# QUICK REFERENCE BY ROLE

## For Frontend Developers

**Pre-Code Focus**: Pillar L (Headless), Pillar A (Types)
```
Pre-Code → In-Code → Post-Code (including design-compliance.md check)
```

## For Backend Developers

**Pre-Code Focus**: Pillar Q (Idempotency), Pillar M (Saga)
```
Pre-Code → In-Code → Post-Code (including lambda-layer-deployment.md if applicable)
```

## For Full-Stack Developers

**Pre-Code Focus**: All sections (T1/T2/T3 design)
```
Pre-Code → In-Code → Post-Code (all checks)
```

## For Architects/Tech Leads

**Focus**: Pre-Code (approval), Post-Code (audit)
```
Pre-Code Approval → Code Review → Post-Code Verification
```

---

# RELATED RESOURCES

- **Pillar Details**: [PILLAR_CHECKLISTS.md](./PILLAR_CHECKLISTS.md) - All 18 Pillars with comprehensive guidance
- **Quick Reference**: [../CHEATSHEET.md](../CHEATSHEET.md) - One-page Pillar overview
- **Design Compliance** (UI Only): [design-compliance.md](./design-compliance.md) - Design system verification
- **Lambda Deployment** (DevOps): [lambda-layer-deployment.md](./lambda-layer-deployment.md) - AWS Lambda procedures
- **Issue Completion**: [../workflow/ISSUE_COMPLETION_CHECKLIST.md](../workflow/ISSUE_COMPLETION_CHECKLIST.md) - PR submission checklist

---

## Version

- **Version**: 1.0 Unified
- **Created**: 2026-02-25
- **Consolidation**: Merged pre-code.md, in-code.md, post-code.md
