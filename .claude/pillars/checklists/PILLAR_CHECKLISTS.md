# Pillar Checklists - Unified Reference

> **Single source of truth** for all Pillar verification checklists.
> Referenced by: `DEVELOPMENT_CHECKLIST.md` and all Pillar documentation.

**Purpose**: Consolidate all 18 Pillar checklists into one maintainable file to eliminate version drift and duplication.

---

## Table of Contents

### [Q1: Data Integrity](#q1-data-integrity)
- [Pillar A: Nominal Typing](#pillar-a-nominal-typing)
- [Pillar B: Airlock (Schema Validation)](#pillar-b-airlock-schema-validation)
- [Pillar C: Mocking (Test Data)](#pillar-c-mocking-test-data)
- [Pillar D: FSM (State Machines)](#pillar-d-fsm-state-machines)

### [Q2: Flow & Concurrency](#q2-flow--concurrency)
- [Pillar E: Adaptive Orchestration (Tier Classification)](#pillar-e-adaptive-orchestration-tier-classification)
- [Pillar F: Concurrency (CAS Locking)](#pillar-f-concurrency-cas-locking)
- [Pillar Q: Idempotency](#pillar-q-idempotency)

### [Q3: Structure & Boundaries](#q3-structure--boundaries)
- [Pillar G: Traceability](#pillar-g-traceability)
- [Pillar H: Policy (Authorization)](#pillar-h-policy-authorization)
- [Pillar I: Firewalls (Import Boundaries)](#pillar-i-firewalls-import-boundaries)
- [Pillar J: Locality (State Proximity)](#pillar-j-locality-state-proximity)
- [Pillar K: Testing (Test Pyramid)](#pillar-k-testing-test-pyramid)
- [Pillar L: Headless (Logic-UI Separation)](#pillar-l-headless-logic-ui-separation)

### [Q4: Resilience & Observability](#q4-resilience--observability)
- [Pillar M: Saga (Compensation Pattern)](#pillar-m-saga-compensation-pattern)
- [Pillar N: Context (TraceId Propagation)](#pillar-n-context-traceid-propagation)
- [Pillar O: Async (Long Operations)](#pillar-o-async-long-operations)
- [Pillar P: Circuit Breaker](#pillar-p-circuit-breaker)
- [Pillar R: Observability (Semantic Logging)](#pillar-r-observability-semantic-logging)

### [Quick Lookup](#quick-lookup-checklist-by-phase)

---

## Q1: Data Integrity

### Pillar A: Nominal Typing

**Purpose**: Use branded types for domain IDs to prevent mixing incompatible types.

#### Pre-Code Phase
- [ ] Identify all domain entity IDs (UserId, OrderId, ProductId, etc.)
- [ ] Define branded type for each ID
- [ ] Plan factory functions with validation
- [ ] Document ID type in schema

#### In-Code Phase
- [ ] All domain IDs use branded types (not primitive strings/numbers)
- [ ] Factory functions validate before creating IDs
- [ ] No `as` type casts for IDs (use factory functions)
- [ ] IDs are readonly and immutable

#### Post-Code Phase
- [ ] No primitive types for domain entities in codebase
- [ ] All ID parameters use branded types
- [ ] TypeScript compiler catches type mismatches
- [ ] Code review confirms no type bypasses

#### Common Violations
- ❌ `userId: string` → ✅ `userId: UserId`
- ❌ `orderId: number` → ✅ `orderId: OrderId`
- ❌ Mixing `UserId` with `OrderId` → Prevented by type system

---

### Pillar B: Airlock (Schema Validation)

**Purpose**: Validate all external data at system boundaries using schemas.

#### Pre-Code Phase
- [ ] Identify all external data sources (API, user input, DB, file)
- [ ] Define Zod schemas for each boundary
- [ ] Plan upcast strategy for legacy data
- [ ] Document schema versioning approach

#### In-Code Phase
- [ ] Every adapter has schema validation (`.parse()` or `.safeParse()`)
- [ ] Validation happens at boundary, not deep in business logic
- [ ] Invalid data rejected with clear error messages
- [ ] Upcast functions handle legacy formats

#### Post-Code Phase
- [ ] All external data validated with schemas
- [ ] No `any` types from external sources
- [ ] Schema tests verify validation logic
- [ ] Legacy data handling tested

#### Common Violations
- ❌ `JSON.parse()` without schema → ✅ `schema.parse(JSON.parse())`
- ❌ Validation in business logic → ✅ Validation at adapter boundary
- ❌ Silent data coercion → ✅ Explicit upcast with logging

---

### Pillar C: Mocking (Test Data)

**Purpose**: Generate realistic test data with factory functions.

#### Pre-Code Phase
- [ ] Plan mock data factories for each entity
- [ ] Identify required vs optional fields
- [ ] Design builder pattern for complex entities
- [ ] Plan test data variations (valid, invalid, edge cases)

#### In-Code Phase
- [ ] Factory functions for all domain entities
- [ ] Realistic default values (not `"test"` everywhere)
- [ ] Builder pattern for customization
- [ ] Factories use branded types (Pillar A)

#### Post-Code Phase
- [ ] All tests use factories, not inline object literals
- [ ] No magic strings in tests
- [ ] Mock data is realistic and diverse
- [ ] Factories cover common test scenarios

#### Common Violations
- ❌ `{ id: "123", name: "test" }` → ✅ `createUser({ name: "Alice" })`
- ❌ Same data in all tests → ✅ Varied data via factory parameters
- ❌ Invalid mock data → ✅ Factories validate with schemas

---

### Pillar D: FSM (State Machines)

**Purpose**: Use explicit finite state machines instead of boolean flags.

#### Pre-Code Phase
- [ ] Identify all states the system can be in
- [ ] Define allowed state transitions
- [ ] Plan initial state and terminal states
- [ ] Document state machine diagram

#### In-Code Phase
- [ ] State represented as enum/union type, not booleans
- [ ] Transitions are explicit functions
- [ ] Invalid transitions prevented by type system
- [ ] State changes logged for debugging

#### Post-Code Phase
- [ ] No boolean flags for state (`isLoading && !isError`)
- [ ] State transitions testable and predictable
- [ ] State machine documented
- [ ] Code review confirms FSM pattern usage

#### Common Violations
- ❌ `isLoading, isError, isSuccess` → ✅ `status: 'idle' | 'loading' | 'success' | 'error'`
- ❌ Impossible states possible → ✅ Type system prevents invalid states
- ❌ Undocumented state flow → ✅ Explicit state machine diagram

---

## Q2: Flow & Concurrency

### Pillar E: Adaptive Orchestration (Tier Classification)

**Purpose**: Classify operations by complexity and use appropriate pattern.

#### Pre-Code Phase
- [ ] Answer: Is this a read or write operation?
- [ ] Answer: Does it touch multiple services/tables?
- [ ] Answer: Does it need local state or validation?
- [ ] **Determine Tier**: T1 (Direct) / T2 (Logic) / T3 (Saga)
- [ ] Select pattern matching tier

#### In-Code Phase
- [ ] **All tiers use Headless pattern** (even T1 fetchers)
- [ ] T1: View → Headless → Adapter
- [ ] T2: View → Headless (+ validation/FSM) → Adapter
- [ ] T3: View → Saga → Multiple Adapters
- [ ] Pattern matches tier classification

#### Post-Code Phase
- [ ] Tier documented in PR description
- [ ] No over-engineering (saga for simple reads)
- [ ] No under-engineering (direct call for payments)
- [ ] Code review confirms tier/pattern match

#### Common Violations
- ❌ T3 saga for GET request → ✅ T1 direct fetch
- ❌ T1 direct call for payment → ✅ T3 saga with compensation
- ❌ View calls adapter directly → ✅ View → Headless → Adapter

---

### Pillar F: Concurrency (CAS Locking)

**Purpose**: Prevent race conditions with optimistic locking (Compare-And-Swap).

#### Pre-Code Phase
- [ ] Identify concurrent write scenarios
- [ ] Add `version` field to data model
- [ ] Plan optimistic locking strategy
- [ ] Define retry logic for conflicts

#### In-Code Phase
- [ ] Version field present in all mutable entities
- [ ] Read includes version, write checks version
- [ ] Stale version throws `ConflictError`
- [ ] Client retries with fresh data

#### Post-Code Phase
- [ ] All concurrent writes use version checking
- [ ] Conflict scenarios tested
- [ ] Retry logic tested
- [ ] Race condition prevention verified

#### Common Violations
- ❌ Direct write without version check → ✅ CAS with version
- ❌ Last-write-wins → ✅ Conflict detection and retry
- ❌ No conflict handling → ✅ Explicit `ConflictError`

---

### Pillar Q: Idempotency

**Purpose**: Make operations safe to retry by using idempotency keys.

#### Pre-Code Phase
- [ ] Identify operations that must be idempotent (payments, orders, emails)
- [ ] Design `intentId` mechanism
- [ ] Plan cache/DB storage for intent results
- [ ] Define TTL for intent cache

#### In-Code Phase
- [ ] Client generates `intentId` for each operation
- [ ] Server checks cache before executing
- [ ] Result cached with `intentId` key
- [ ] Retry returns cached result immediately

#### Post-Code Phase
- [ ] Critical operations are idempotent
- [ ] Retry tests confirm same result
- [ ] Intent cache has appropriate TTL
- [ ] Duplicate prevention verified

#### Common Violations
- ❌ No idempotency for payments → ✅ `intentId` caching
- ❌ Retry creates duplicate order → ✅ Cached result returned
- ❌ Intent storage missing → ✅ DynamoDB/Redis cache

---

## Q3: Structure & Boundaries

### Pillar G: Traceability

**Purpose**: Document action flow with `@trigger`, `@listen`, and `@ai-intent` comments.

#### Pre-Code Phase
- [ ] Plan event flow through system
- [ ] Identify triggers (user actions, timers, events)
- [ ] Identify listeners (handlers, callbacks)
- [ ] Document AI decision points

#### In-Code Phase
- [ ] `@trigger` comment on user action handlers
- [ ] `@listen` comment on event handlers
- [ ] `@ai-intent` comment on AI-generated suggestions
- [ ] Event flow traceable via comments

#### Post-Code Phase
- [ ] All event sources documented
- [ ] Event flow can be traced by reading comments
- [ ] AI decisions explicitly marked
- [ ] Code review confirms traceability

#### Common Violations
- ❌ Unclear event source → ✅ `@trigger user:click-button`
- ❌ Handler purpose unclear → ✅ `@listen order:created`
- ❌ AI suggestion unmarked → ✅ `@ai-intent optimize-query`

---

### Pillar H: Policy (Authorization)

**Purpose**: Separate authorization logic from business logic.

#### Pre-Code Phase
- [ ] Identify authorization requirements
- [ ] Design policy functions (separate from business logic)
- [ ] Plan role/permission structure
- [ ] Document authorization flows

#### In-Code Phase
- [ ] Authorization checks in dedicated policy functions
- [ ] Business logic does not contain `if (user.role === ...)`
- [ ] Policy violations throw `ForbiddenError`
- [ ] Policies testable independently

#### Post-Code Phase
- [ ] All authorization in policy layer
- [ ] No inline permission checks in business logic
- [ ] Policy changes don't require business logic changes
- [ ] Authorization tests comprehensive

#### Common Violations
- ❌ `if (user.role === 'admin')` in business logic → ✅ `requireAdmin(user)` in policy
- ❌ Mixed auth and business logic → ✅ Separate layers
- ❌ Hard to test permissions → ✅ Policy functions unit tested

---

### Pillar I: Firewalls (Import Boundaries)

**Purpose**: Prevent deep imports that violate layer boundaries.

#### Pre-Code Phase
- [ ] Define layer structure (kernel, domains, modules, migrations)
- [ ] Document allowed import directions
- [ ] Plan ESLint rules for boundary enforcement
- [ ] Create `index.ts` public APIs for each module

#### In-Code Phase
- [ ] Imports follow dependency rule (outer → inner only)
- [ ] Public API via `index.ts` exports
- [ ] No deep imports (`../../../otherModule/internal`)
- [ ] ESLint prevents boundary violations

#### Post-Code Phase
- [ ] No circular dependencies
- [ ] Layer boundaries respected
- [ ] ESLint checks passing
- [ ] Dependency graph clean

#### Common Violations
- ❌ `import from '../../../domains/user/internal'` → ✅ `import from '@/domains/user'`
- ❌ Circular imports → ✅ Dependency inversion
- ❌ Module accesses internal implementation → ✅ Public API only

---

### Pillar J: Locality (State Proximity)

**Purpose**: Keep state close to where it's used, not in global stores.

#### Pre-Code Phase
- [ ] Identify state scope (component, page, global)
- [ ] Plan state placement based on usage
- [ ] Avoid premature global state
- [ ] Document state ownership

#### In-Code Phase
- [ ] Component state for component-only data
- [ ] Page state for page-wide data
- [ ] Global state only for truly global data (user, theme)
- [ ] State collocated with usage

#### Post-Code Phase
- [ ] No global state for local concerns
- [ ] State ownership clear
- [ ] State changes don't affect unrelated components
- [ ] Code review confirms locality

#### Common Violations
- ❌ Form state in global store → ✅ Local `useState` in form component
- ❌ Everything in Redux → ✅ Only shared data in global store
- ❌ Prop drilling 5 levels → ✅ Context or Zustand slice

---

### Pillar K: Testing (Test Pyramid)

**Purpose**: 3-layer test pyramid: Unit (70%) > Integration (20%) > E2E (10%).

#### Pre-Code Phase
- [ ] Plan test coverage targets
- [ ] Identify critical paths for E2E
- [ ] Design testable architecture (dependency injection)
- [ ] Set up testing infrastructure

#### In-Code Phase
- [ ] Unit tests for business logic (≥70% coverage)
- [ ] Integration tests for API/DB interactions
- [ ] E2E tests for critical user flows
- [ ] Test pyramid proportions maintained

#### Post-Code Phase
- [ ] Coverage ≥80% overall
- [ ] Fast unit tests (<1s total)
- [ ] Integration tests isolated
- [ ] E2E tests stable and minimal

#### Common Violations
- ❌ All E2E tests, no unit tests → ✅ Pyramid proportions
- ❌ Slow tests → ✅ Fast unit tests with mocks
- ❌ Flaky E2E tests → ✅ Stable with proper waits

---

### Pillar L: Headless (Logic-UI Separation)

**Purpose**: Keep business logic in headless hooks, UI in components.

#### Pre-Code Phase
- [ ] Identify business logic vs rendering logic
- [ ] Plan headless hooks for each feature
- [ ] Design hook API (inputs → outputs)
- [ ] Ensure hooks have no JSX

#### In-Code Phase
- [ ] All business logic in headless hooks
- [ ] Hooks return data/functions, no JSX
- [ ] Components render only, no business logic
- [ ] Hooks testable without React

#### Post-Code Phase
- [ ] No JSX in headless hooks
- [ ] All hooks unit tested (without React)
- [ ] Components thin and declarative
- [ ] Code review confirms separation

#### Common Violations
- ❌ Business logic in component → ✅ Move to headless hook
- ❌ `return <div>` in hook → ✅ Return data only
- ❌ Hook depends on DOM → ✅ Pure logic, DOM-independent

---

## Q4: Resilience & Observability

### Pillar M: Saga (Compensation Pattern)

**Purpose**: Implement distributed transactions with compensation for rollback.

#### Pre-Code Phase
- [ ] Identify multi-service operations
- [ ] Design compensation actions for each step
- [ ] Plan execution order and compensation order
- [ ] Document saga flow diagram

#### In-Code Phase
- [ ] Each saga step has compensation function
- [ ] Compensation stack built as saga executes
- [ ] On failure, compensations run in reverse order
- [ ] Saga is idempotent (Pillar Q)

#### Post-Code Phase
- [ ] All multi-service operations use saga
- [ ] Failure scenarios tested with compensation
- [ ] Partial completion impossible
- [ ] Saga resumable after failure

#### Common Violations
- ❌ No compensation for payment → ✅ Refund compensation
- ❌ Manual rollback → ✅ Automatic compensation stack
- ❌ Partial state after failure → ✅ Full rollback via compensations

---

### Pillar N: Context (TraceId Propagation)

**Purpose**: Propagate `traceId` through all operations for debugging.

#### Pre-Code Phase
- [ ] Design context structure (traceId, userId, etc.)
- [ ] Plan context propagation mechanism
- [ ] Ensure all logs include traceId
- [ ] Document context flow

#### In-Code Phase
- [ ] Every request generates unique `traceId`
- [ ] Context passed to all functions (explicit parameter)
- [ ] All logs include `traceId` field
- [ ] Async operations preserve context

#### Post-Code Phase
- [ ] All operations traceable via traceId
- [ ] Logs can be filtered by traceId
- [ ] Cross-service tracing works
- [ ] Context propagation verified

#### Common Violations
- ❌ No traceId in logs → ✅ All logs include traceId
- ❌ Lost context in async → ✅ Explicit context parameter
- ❌ Can't trace request flow → ✅ Complete trace via traceId

---

### Pillar O: Async (Long Operations)

**Purpose**: Use 202 + polling for operations > 5 seconds.

#### Pre-Code Phase
- [ ] Identify long-running operations (reports, exports, imports)
- [ ] Design async operation API (POST → 202, GET → status)
- [ ] Plan result storage (S3, DB)
- [ ] Define polling intervals and timeouts

#### In-Code Phase
- [ ] Long operations return 202 with `operationId`
- [ ] Client polls `/operations/{id}` for status
- [ ] Result URL provided when complete
- [ ] Operation status: pending, running, completed, failed

#### Post-Code Phase
- [ ] No timeout errors for long operations
- [ ] Clients poll correctly
- [ ] Result retrieval tested
- [ ] Timeout and failure scenarios handled

#### Common Violations
- ❌ Synchronous report generation (timeout) → ✅ 202 + poll
- ❌ Client blocks waiting → ✅ Async with status updates
- ❌ Result lost on completion → ✅ Stored in S3/DB

---

### Pillar P: Circuit Breaker

**Purpose**: Prevent cascading failures by breaking circuit to failing services.

#### Pre-Code Phase
- [ ] Identify external service dependencies
- [ ] Define failure thresholds (5 failures in 10s)
- [ ] Plan circuit states (closed, open, half-open)
- [ ] Design fallback responses

#### In-Code Phase
- [ ] Circuit breaker wraps external service calls
- [ ] Failure threshold triggers open circuit
- [ ] Open circuit returns fallback immediately
- [ ] Half-open state allows test requests

#### Post-Code Phase
- [ ] Circuit breaker tested with failing services
- [ ] Fallback responses appropriate
- [ ] Circuit recovers when service healthy
- [ ] Cascading failures prevented

#### Common Violations
- ❌ Retry forever on service failure → ✅ Circuit opens after threshold
- ❌ No fallback → ✅ Graceful degradation
- ❌ Cascading failures → ✅ Circuit breaks prevents spread

---

### Pillar R: Observability (Semantic Logging)

**Purpose**: Structured JSON logging with semantic fields for debugging and monitoring.

#### Pre-Code Phase
- [ ] Design log structure (level, message, context, traceId)
- [ ] Plan semantic fields for each log type
- [ ] Choose log aggregation tool (CloudWatch, Datadog)
- [ ] Define log retention policy

#### In-Code Phase
- [ ] All logs are structured JSON
- [ ] Logs include semantic fields (userId, orderId, etc.)
- [ ] Log levels used correctly (ERROR for failures, INFO for events)
- [ ] Sensitive data excluded from logs

#### Post-Code Phase
- [ ] Logs queryable by semantic fields
- [ ] All errors logged with context
- [ ] No console.log in production
- [ ] Log aggregation and alerting working

#### Common Violations
- ❌ `console.log("error")` → ✅ `logger.error({ message: "...", context: {...} })`
- ❌ Plain text logs → ✅ Structured JSON
- ❌ No context in error logs → ✅ Full context with traceId

---

## Quick Lookup: Checklist by Phase

### Pre-Code Phase (Planning)

**Check these Pillars BEFORE writing any code:**

- [ ] **Pillar A**: Identify domain IDs needing branded types
- [ ] **Pillar B**: Define Zod schemas for all boundaries
- [ ] **Pillar D**: Design state machine (not boolean flags)
- [ ] **Pillar E**: Classify operation tier (T1/T2/T3)
- [ ] **Pillar F**: Add version field for concurrent writes
- [ ] **Pillar Q**: Plan idempotency for critical operations
- [ ] **Pillar M**: Design compensation actions (if T3)

---

### In-Code Phase (Implementation)

**Verify these Pillars DURING coding:**

- [ ] **Pillar A**: Use branded types for all IDs
- [ ] **Pillar B**: Validate at boundaries with schemas
- [ ] **Pillar L**: All logic in headless hooks (no JSX)
- [ ] **Pillar G**: Add `@trigger`/`@listen` comments
- [ ] **Pillar H**: Authorization in policy functions
- [ ] **Pillar I**: No deep imports (use public APIs)
- [ ] **Pillar J**: State close to usage
- [ ] **Pillar K**: Write unit tests (≥70% coverage)
- [ ] **Pillar M**: Implement compensation stack (if saga)
- [ ] **Pillar N**: Propagate traceId in context
- [ ] **Pillar R**: JSON semantic logs

---

### Post-Code Phase (Review/Audit)

**Audit these Pillars AFTER coding:**

- [ ] **Pillar A**: No primitive types for domain entities
- [ ] **Pillar B**: All external data validated
- [ ] **Pillar C**: All tests use factories (not inline objects)
- [ ] **Pillar D**: No boolean flags for state
- [ ] **Pillar E**: Tier matches pattern
- [ ] **Pillar I**: No boundary violations (ESLint passing)
- [ ] **Pillar K**: Test coverage ≥80%
- [ ] **Pillar L**: All hooks are headless
- [ ] **Pillar R**: All logs are structured JSON

---

## Cross-Reference: Pillar Dependencies

Some Pillars work together. When using one, check related Pillars:

| If Using | Also Check |
|----------|------------|
| **Pillar E** (T3 Saga) | **M** (Compensation), **Q** (Idempotency), **F** (Locking), **N** (TraceId) |
| **Pillar M** (Saga) | **Q** (Idempotency), **R** (Logging), **N** (Context) |
| **Pillar L** (Headless) | **D** (FSM for state), **K** (Unit tests) |
| **Pillar B** (Airlock) | **A** (Branded types), **C** (Mock factories) |
| **Pillar A** (Nominal Types) | **B** (Schema validation), **C** (Factories) |

---

## Related Documentation

- **Pillar Details**: `pillars/<quadrant>/<pillar>/<name>.md` - Full Pillar documentation
- **Development Workflow**: `checklists/DEVELOPMENT_CHECKLIST.md` - Complete planning → implementation → review
- **Quick Reference**: `.claude/pillars/CHEATSHEET.md` - One-page overview
- **Design Compliance**: `checklists/design-compliance.md` - UI/Frontend checklist
- **Lambda Deployment**: `checklists/lambda-layer-deployment.md` - DevOps procedures

---

**Last Updated**: 2026-02-05
**Version**: 1.0 (Initial consolidated version)
**Consolidated From**: 18 individual `pillars/*/checklist.md` files
