# Pillar Interdependencies and Constraints

> Guide to understanding how AI_DEV_PROT pillars depend on and complement each other

## Quick Reference: Recommended Combinations

| Use Case | Pillars | Dependencies | Rationale |
|----------|---------|--------------|-----------|
| **Learning** | A, B, K | None | Foundational trio for understanding |
| **Simple API** | A, B, K, R | K requires careful testing | Type safety + validation + logging |
| **Full-stack Web** | A, B, K, L, M, Q, R | L requires good boundaries | UI separation + transactional safety |
| **Microservice** | A, B, K, M, Q, R | M requires compensation logic | Distributed system resilience |
| **Complex Distributed** | All 18 | See detailed matrix | Maximum patterns, maximum safety |

---

## Dependency Matrix

### Q1: Data Integrity Pillars

**A (Nominal Typing) → Foundation for All**
- Dependencies: None
- Complements: B (validates branded types), L (UI can't misuse types)
- Conflicts: None - foundational pattern
- When to use: Always (except minimal scripts)
- Enables: Type-safe development in TypeScript/Python/Go

**B (Airlock) → Validation Gateway**
- Dependencies: None (but works best with A)
- Complements: A (validates branded types), H (auth airlock), K (test validation)
- Conflicts: None - essential pattern
- When to use: Always at system boundaries
- Enables: Safe data transformation at API boundaries
- Examples:
  ```typescript
  // B requires A for branded types
  interface User { id: UserId; email: Email }  // A's branded types
  parseUser(untrusted) → User                  // B's validation
  ```

**C (Mocking) → Test Data**
- Dependencies: K (testing), B (schema validation)
- Complements: K (mocking objects), D (mock FSM states)
- Conflicts: None - test-only pattern
- When to use: For complex test scenarios
- Examples: Mock factories for entities with FSM states (Pillar D)

**D (FSM) → State Validation**
- Dependencies: A (branded types for state), B (schema for FSM)
- Complements: M (sagas transition through FSM states), E (orchestration with FSMs), K (test FSM transitions)
- Conflicts: None - works well with orchestration
- When to use: When state transitions matter (orders, workflows, user lifecycle)
- Enables: Impossible invalid states
- Cost: Design upfront (worth it for complex flows)

### Q2: Flow & Concurrency Pillars

**E (Orchestration) → Multi-step Workflows**
- Dependencies: D (FSM for state transitions), M (compensation for failures)
- Complements: M (sagas), D (FSM states), E, Q (idempotency)
- Conflicts: None - designed to work with M and D
- When to use: Multi-step operations (order processing, user signup)
- Requires: Clear step definition and compensation logic

**F (Concurrency) → CAS + Optimistic Locking**
- Dependencies: A (branded types for version), B (validation of concurrent data)
- Complements: D (FSM prevents race conditions), Q (idempotency for retries)
- Conflicts: None - standard concurrency pattern
- When to use: When multiple updates race (inventory, balances)
- Examples: CAS operations with versioned branded types

**Q (Idempotency) → Safe Retries**
- Dependencies: None (but requires careful design with E)
- Complements: E (safe saga step retries), M (saga compensation), R (trace retries)
- Conflicts: None - essential for distributed systems
- When to use: Network-exposed operations, async tasks
- Cost: Idempotency key generation and tracking

### Q3: Structure & Boundaries Pillars

**G (Traceability) → Event Tracking**
- Dependencies: R (logging the events), N (context with traceId)
- Complements: R (logs events), M (sagas trigger events), N (traceId propagation)
- Conflicts: None - information pattern
- When to use: For debugging distributed flows
- Examples: @trigger/@listen decorators for saga steps

**H (Policy) → Authorization Separation**
- Dependencies: B (airlock validates policies)
- Complements: I (firewalls separate concerns), K (test policy enforcement)
- Conflicts: None - security pattern
- When to use: Complex auth (role-based, attribute-based)
- Examples: Separate service/permission layers from business logic

**I (Firewalls) → Import Boundaries**
- Dependencies: H (policies define boundaries)
- Complements: H (policy separation), J (locality principles)
- Conflicts: None - architectural pattern
- When to use: Large codebases (prevent deep coupling)
- Implementation: ESLint rules, import restrictions

**J (Locality) → State Proximity**
- Dependencies: None (architectural principle)
- Complements: L (headless UI keeps state close), H (locality to policy boundaries)
- Conflicts: None - design principle
- When to use: Always (avoid global state)
- Pattern: State managed by component using it, passed down

**K (Testing) → 3-Layer Pyramid**
- Dependencies: None (but needs other patterns to test effectively)
- Complements: C (mocking), D (test FSMs), A (test branded type constructors)
- Conflicts: None - quality pattern
- When to use: All projects (mandatory)
- Structure: Unit (80%) → Integration (15%) → E2E (5%)

**L (Headless) → Logic-UI Separation**
- Dependencies: A (branded types in headless), K (test hooks separately)
- Complements: J (locality of state), K (test headless + UI separately)
- Conflicts: None - architecture pattern
- When to use: Frontend projects, desktop apps
- Cost: Duplication of state (headless + hooks)
- Benefit: UI-agnostic logic testable without rendering

### Q4: Resilience & Observability Pillars

**M (Saga) → Distributed Transactions**
- Dependencies: D (FSM states), E (orchestration), Q (idempotency)
- Complements: E (multi-step coordination), D (state transitions), N (context), R (logging)
- Conflicts: None - works with all patterns
- When to use: Multi-service operations (payments, fulfillment)
- Cost: Compensation logic complexity
- Benefit: No distributed 2-phase commit needed

**N (Context) → TraceId Propagation**
- Dependencies: R (needs observability to use it), G (events tracked)
- Complements: R (logs with traceId), G (events with traceId), M (sagas traced)
- Conflicts: None - observability pattern
- When to use: Microservices (essential for debugging)
- Implementation: AsyncContext, middleware propagation

**O (Async) → Long Operations**
- Dependencies: Q (idempotency for polling), N (context for async)
- Complements: Q (safe retries), N (trace async completion), R (observe polling)
- Conflicts: None - async pattern
- When to use: Long-running operations (exports, reports)
- Pattern: 202 Accepted + polling

**P (Circuit Breaker) → Failure Isolation**
- Dependencies: R (observe circuit state), N (context for breaker decision)
- Complements: Q (idempotency with circuit), R (log circuit changes)
- Conflicts: None - resilience pattern
- When to use: External service calls (APIs, databases)
- Implementation: Layered (request → circuit → exponential backoff)

**R (Observability) → JSON Logging**
- Dependencies: None (but needs other patterns for value)
- Complements: G (logs events), N (logs with traceId), M (logs saga steps), Q (logs retries)
- Conflicts: None - information pattern
- When to use: All services (essential for production)
- Structure: JSON semantic logging with structured fields

---

## Dependency Graph: Visualized

### Tier 0: Foundational (No Dependencies)
```
A (Nominal Typing)
B (Airlock)
J (Locality)
K (Testing)
R (Observability)
```
These can be used independently. Start here.

### Tier 1: Enhancing Tier 0
```
C (Mocking)        → K
D (FSM)            → A, B
F (Concurrency)    → A, B
G (Traceability)   → R, N
H (Policy)         → B
I (Firewalls)      → H
L (Headless)       → A, K
N (Context)        → R, G
Q (Idempotency)    → None (but best with E, M)
```

### Tier 2: Building on Tier 1
```
E (Orchestration)  → D, M
M (Saga)           → D, E, Q
O (Async)          → Q, N
P (Circuit)        → R, N
```

---

## Profile-Pillar Alignment

### Minimal (Beginner)
```
A → B → K
↓
Foundation for understanding patterns
```
- **Dependencies satisfied**: ✓ A has none, B depends on A, K tests all
- **What's missing**: Architecture patterns (L, M), observability (R)

### React Frontend
```
A → B → K
  ↘   ↙
    L (Headless UI)
```
- **Dependencies satisfied**: ✓ All foundational
- **What's missing**: Backend patterns (M, Q, R)
- **Cost**: Learning UI/headless separation

### Node Lambda
```
A → B → K      D → E
  ↘   ↙        ↙   ↓
    ?         M ← Q
    ↓         ↓
    R (Observability)
```
- **Dependencies satisfied**: ✓ Carefully selected
- **What's missing**: Some Q1/Q2 patterns (C, F), Authorization (H)

### React AWS
```
All foundations:        A, B, K, L
Added:                  D, E, M, Q, R
Missing but optional:   C, F, G, H, I, J, N, O, P
```

### Next.js AWS (Comprehensive)
```
All 18 pillars enabled with full dependency chain
```

---

## Forbidden Combinations (None!)

Unlike many frameworks, AI_DEV_PROT has **no forbidden combinations**. Each pillar was designed to work independently and with others.

However, some combinations have **minimal benefit**:

| Combination | Benefit | Cost | Notes |
|-------------|---------|------|-------|
| M without D, E | ~30% benefit | Compensation logic confusing | Hard to reason about without states/orchestration |
| E without D | ~40% benefit | States implicit | Orchestration clearer with explicit FSM |
| L without K | ~50% benefit | Hard to test | Separate logic from UI, but test both |
| P without N | ~60% benefit | Hard to reason about | Circuit breaker needs distributed context |

---

## Dependency Paths: From Simple to Complex

### Path 1: Type Safety Progression
```
A (branded types)
  ↓
A + B (+ airlock validation)
  ↓
A + B + D (+ FSM states, impossible invalid)
  ↓
A + B + D + E (+ orchestration of FSM transitions)
  ↓
A + B + D + E + M + Q (+ saga compensation + idempotency)
```

### Path 2: UI Development Progression
```
A (branded types)
  ↓
A + K (+ testing)
  ↓
A + K + L (+ headless UI, separate logic)
  ↓
A + K + L + B (+ validation in UI boundary)
  ↓
A + K + L + B + M (+ long-running async operations)
```

### Path 3: Backend Service Progression
```
A + B (type safety + validation)
  ↓
A + B + K (+ testing)
  ↓
A + B + K + R (+ observability logging)
  ↓
A + B + K + R + Q (+ idempotent retries)
  ↓
A + B + K + R + Q + M (+ multi-step transactions)
  ↓
A + B + K + R + Q + M + N (+ distributed tracing)
  ↓
All 18 (+ full resilience suite)
```

---

## When to Add Pillars: Decision Flow

### Decision Tree

```
Start with: A, B, K (foundational)
↓
Project has frontend?
├─ YES → Add L (headless)
└─ NO → Skip L
↓
Multi-step workflows?
├─ YES → Add D, E, M
└─ NO → Skip D, E, M
↓
Distributed system?
├─ YES → Add Q, N, R
└─ NO → Skip Q, N
↓
Complex authorization?
├─ YES → Add H, I
└─ NO → Skip H, I
↓
Large codebase with many developers?
├─ YES → Add G, J
└─ NO → Skip G, J
↓
External service integrations?
├─ YES → Add P, F
└─ NO → Skip P, F
↓
Edge case: Need everything?
└─ Use nextjs-aws profile (15 pillars)
```

---

## Coupling Diagram: Which Pillars Communicate

### High Coupling (Tight Dependencies)
```
D (FSM) ←→ E (Orchestration)
  ↓         ↓
M (Saga)  ← Q (Idempotency)

These 4 work as a unit for multi-step workflows
```

### Medium Coupling (Related Patterns)
```
A (Nominal) → B (Airlock) → L (Headless)
              ↓
           H (Policy)

Type safety cascades through validation layer into boundaries
```

### Low Coupling (Independent Patterns)
```
K (Testing) - standalone pattern, tests other pillars
R (Observability) - standalone, logged by other pillars
J (Locality) - principle affecting all layers
```

---

## Cost vs Benefit Analysis

| Pillar | Setup Time | Learning Curve | Runtime Cost | Test Complexity | Benefit (Security/DX) |
|--------|-----------|---------------|--------------|-----------------|-----------------------|
| A | 1h | Easy | 0% | Low | High (type safety) |
| B | 2h | Easy | 0% | Low | High (validation) |
| C | 3h | Medium | 5% | Medium | Medium (test factories) |
| D | 4h | Hard | 2% | High | High (state safety) |
| E | 3h | Hard | 5% | High | Medium (orchestration) |
| F | 2h | Medium | 5% | Low | Medium (concurrency) |
| Q | 2h | Medium | 3% | Low | High (idempotency) |
| G | 1h | Easy | 0% | Low | Medium (traceability) |
| H | 4h | Hard | 3% | Medium | High (authorization) |
| I | 2h | Easy | 0% | Low | Medium (architecture) |
| J | 1h | Easy | 0% | Low | High (locality) |
| K | 4h | Medium | 0% | High | High (testing) |
| L | 8h | Hard | 0% | High | High (UI testing) |
| M | 6h | Hard | 2% | High | High (saga safety) |
| N | 3h | Medium | 3% | Medium | High (tracing) |
| O | 3h | Medium | 5% | Medium | Medium (async) |
| P | 4h | Medium | 2% | Low | High (resilience) |
| R | 2h | Easy | 3% | Low | High (observability) |

**Legend**: Low = <1 day, Medium = 1-3 days, High = 3+ days

---

## Optimization: Pillar Selection by Team Size

### Solo Developer (1 person)
- **Start**: A, B, K (minimum)
- **Add** (week 2): L (if frontend), R (if distributed)
- **Skip**: C, F, G, H, I, J (overhead for one person)
- **Total**: ~7-10 pillars

### Small Team (2-5 people)
- **Foundation**: A, B, K, R (mandatory)
- **Add**: L (if frontend), M, Q (if distributed)
- **Consider**: D, E, H (for clarity)
- **Skip**: C, F, G, I (less critical at this scale)
- **Total**: ~9-12 pillars

### Large Team (5+ people, multiple services)
- **Foundation**: All A-R (full suite)
- **Reason**: Prevents miscommunication, enables async work
- **Cost**: Training + setup (1-2 weeks)
- **Benefit**: Consistent patterns across all services
- **Total**: All 18 pillars

---

## Migration Paths: Adding Pillars to Existing Projects

### Minimal → React AWS

```
Start: A, B, K
Week 1: Add L (separate headless from UI)
Week 2: Add R (add logging to headless)
Week 3: Add M, Q (if doing async operations)
Week 4: Add D, E (if state is complex)
Result: 7-10 pillars, production-ready
```

### Minimal → Node Lambda

```
Start: A, B, K
Week 1: Add R (observability is critical)
Week 2: Add M, Q, N (distributed systems)
Week 3: Add D, E (if workflows are complex)
Week 4: Add H (authorization patterns)
Result: 9-11 pillars, enterprise-ready
```

---

## FAQ: Pillar Interdependencies

**Q: Can I use M (Saga) without D (FSM)?**
A: Technically yes, but highly discouraged. Sagas transition through states - FSM makes this explicit. Without FSM, you'll reinvent it implicitly (worse).

**Q: Can I use E (Orchestration) without M (Saga)?**
A: Yes if you're just sequencing deterministic steps. But if any step can fail and needs compensation, you need M.

**Q: Must I use K (Testing)?**
A: Technically no, but practically yes. Framework assumes tested code. K is the only way to verify other pillars work.

**Q: Can I skip Q (Idempotency) in a distributed system?**
A: No. In distributed systems, retries happen automatically. Q is how you make retries safe.

**Q: What if I use all 18 - is that overkill?**
A: No. See nextjs-aws profile - it's used in production complex systems. Each pillar solves a real problem.

---

## Recommended Reading Order

1. **Start here**: A (Nominal Typing), B (Airlock) - understanding types and validation
2. **Then**: K (Testing) - testing the above
3. **Then**: L (Headless) or M (Saga) - depending on your project
4. **Then**: R (Observability) - debugging and production visibility
5. **Then**: Other Q3/Q4 patterns based on needs
6. **Finally**: C (Mocking) and F (Concurrency) - optimization patterns

---

## Related Documentation

- **[Profiles README](../profiles/README.md)** - Profile-pillar mappings
- **[.claude/pillars/README.md](README.md)** - Pillar overview
- **[.claude/pillars/CHEATSHEET.md](CHEATSHEET.md)** - Quick reference
- **Pillar Details**: See individual pillar directories (pillar-a/, pillar-b/, etc.)
