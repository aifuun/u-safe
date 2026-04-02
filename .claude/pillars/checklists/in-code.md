# In-Code Checklist

> Run DURING implementation, per task
>
> **Full Details**: See [PILLAR_CHECKLISTS.md](./PILLAR_CHECKLISTS.md#quick-lookup-checklist-by-phase) for complete checklists.

## Essential In-Code Checks

### Data Integrity (Q1)

#### Pillar A: Nominal Typing
- [ ] All domain IDs use branded types (not primitive strings/numbers)
- [ ] Factory functions validate before creating IDs
- [ ] No `as` type casts for IDs (use validation functions)

→ **Full checklist**: [Pillar A: Nominal Typing](../pillars/q1-data-integrity/pillar-a/nominal-typing.md)

#### Pillar B: Airlock (Schema Validation)
- [ ] Every adapter has schema validation (`.parse()` or `.safeParse()`)
- [ ] Validation at boundary, not deep in business logic
- [ ] Upcast functions handle legacy formats

→ **Full checklist**: [Pillar B: Airlock](../pillars/q1-data-integrity/pillar-b/airlock.md)

#### Pillar D: FSM (State Machines)
- [ ] State represented as enum/union type, not booleans
- [ ] Transitions are explicit functions
- [ ] Invalid transitions prevented by type system

→ **Full checklist**: [Pillar D: FSM](../pillars/q1-data-integrity/pillar-d/fsm.md)

---

### Structure & Boundaries (Q3)

#### Pillar L: Headless
- [ ] **NO UI code in headless hooks** (zero exceptions)
- [ ] Hooks return data/functions only
- [ ] All business logic in headless layer, not in View layer

→ **Full checklist**: [Pillar L: Headless](../pillars/q3-structure-boundaries/pillar-l/headless.md)

#### Pillar G: Traceability
- [ ] `@trigger` comment on user action handlers
- [ ] `@listen` comment on event handlers
- [ ] `@ai-generated` comment on AI-generated code sections

→ **Full checklist**: [Pillar G: Traceability](../pillars/q3-structure-boundaries/pillar-g/traceability.md)

#### Pillar H: Policy
- [ ] Authorization checks in dedicated policy functions
- [ ] Business logic does NOT contain `if (user.role === ...)`
- [ ] Policy violations throw appropriate errors

→ **Full checklist**: [Pillar H: Policy](../pillars/q3-structure-boundaries/pillar-h/policy.md)

#### Pillar I: Firewalls
- [ ] Imports follow dependency rule (outer → inner only)
- [ ] No deep imports (`../../../otherModule/internal`)
- [ ] Public API via `index.ts` or public exports

→ **Full checklist**: [Pillar I: Firewalls](../pillars/q3-structure-boundaries/pillar-i/firewalls.md)

#### Pillar J: Locality
- [ ] Component state for component-only data
- [ ] Feature state for feature-wide data
- [ ] Global state only for truly global data

→ **Full checklist**: [Pillar J: Locality](../pillars/q3-structure-boundaries/pillar-j/locality.md)

#### Pillar K: Testing
- [ ] Unit tests for business logic written
- [ ] Test coverage ≥70% for this feature
- [ ] Tests use mock factories, not inline objects

→ **Full checklist**: [Pillar K: Testing](../pillars/q3-structure-boundaries/pillar-k/testing.md)

---

### Resilience & Observability (Q4)

#### Pillar M: Saga (For T3 Only)
- [ ] Each saga step has compensation function
- [ ] Compensation stack built as saga executes
- [ ] On failure, compensations run in reverse order (LIFO)

→ **Full checklist**: [Pillar M: Saga](../pillars/q4-resilience-observability/pillar-m/saga.md)

#### Pillar N: Context
- [ ] Every request generates unique `traceId`
- [ ] Context passed to all functions (explicit parameter or context object)
- [ ] All logs include `traceId` field

→ **Full checklist**: [Pillar N: Context](../pillars/q4-resilience-observability/pillar-n/context.md)

#### Pillar R: Observability
- [ ] All logs are structured (JSON or key-value pairs)
- [ ] Logs include semantic fields (userId, orderId, etc.)
- [ ] Log levels used correctly (ERROR, WARN, INFO, DEBUG)

→ **Full checklist**: [Pillar R: Observability](../pillars/q4-resilience-observability/pillar-r/observability.md)

---

## T3-Specific Checks

If implementing Tier 3 (Saga/Complex operations):

#### Pillar Q: Idempotency
- [ ] Client generates idempotency key for each operation
- [ ] Server checks cache before executing
- [ ] Result cached with idempotency key

→ **Full checklist**: [Pillar Q: Idempotency](../pillars/q2-flow-concurrency/pillar-q/idempotency.md)

#### Pillar F: Concurrency
- [ ] Version field present in mutable entities
- [ ] Read includes version, write checks version (CAS)
- [ ] Stale version handled appropriately (retry or error)

→ **Full checklist**: [Pillar F: Concurrency](../pillars/q2-flow-concurrency/pillar-f/concurrency.md)

---

## After Each Task

1. [ ] Run unit tests for this code
2. [ ] Mark task item complete in plan
3. [ ] No debug statements left in code
4. [ ] Review applicable Pillars above

---

## Related Resources

- **Complete Checklists**: [PILLAR_CHECKLISTS.md](./PILLAR_CHECKLISTS.md) - All 18 Pillars with full details
- **Previous Phase**: [pre-code.md](./pre-code.md) - Planning checklist
- **Next Phase**: [post-code.md](./post-code.md) - Review/audit checklist
