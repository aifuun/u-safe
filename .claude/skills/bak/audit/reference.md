# Project Audit Reference Guide

Complete reference for the `/audit` skill with pillar patterns, detection methods, and audit checklists.

## When to Use `/audit`

- **After framework initialization** - Verify patterns are used
- **Regular compliance checks** - Quarterly audits
- **Before refactoring** - Understand current state
- **New team member onboarding** - Show implemented patterns
- **Architecture review** - Verify patterns match design
- **Migration planning** - Identify missing patterns

## Command Usage

### Full Audit (All Installed Pillars)
```bash
/audit              # Audit all pillars in profile
```

### Specific Pillars
```bash
/audit A            # Audit only Pillar A (Nominal Typing)
/audit A B K        # Audit specific pillars
/audit M Q R        # Audit multiple pillars
```

## Pillar Detection Patterns

### Pillar A: Nominal Typing (Branded Types)

**What to look for:**
- `declare const brand: unique symbol` declarations
- `Branded<T, Brand>` type definitions
- Type guard functions (`isBrandedType`)
- Branded types in function signatures

**Detection code:**
```bash
grep -r "unique symbol\|Branded<" src/
grep -r "function is[A-Z]\|const is[A-Z]" src/  # Type guards
```

**Example:**
```typescript
// ✅ Pillar A implemented
type UserId = Branded<string, 'UserId'>;
function isUserId(value: unknown): value is UserId { ... }
function getUserById(id: UserId) { ... }

// ❌ Not implementing Pillar A
function getUserById(id: string) { ... }  // No nominal type
```

### Pillar B: Airlock Pattern (Schema Validation)

**What to look for:**
- Schema definitions (Zod, io-ts, Joi, etc.)
- Parse/validate functions at API boundaries
- Separation of untrusted → validated → trusted types
- Error handling for validation failures

**Detection code:**
```bash
grep -r "z\.\|zod\|io-ts\|parse\|validate" src/
grep -r "SafeParseResult\|Type.is" src/
```

**Example:**
```typescript
// ✅ Pillar B implemented
const UserSchema = z.object({ email: z.string().email() });
function parseUser(untrusted: unknown): User {
  return UserSchema.parse(untrusted);
}
app.post('/users', (req, res) => {
  const user = parseUser(req.body);  // Airlock
  // ...
});

// ❌ Not implementing Pillar B
app.post('/users', (req, res) => {
  const user = req.body;  // No validation!
  db.save(user);
});
```

### Pillar K: Testing Pyramid

**What to look for:**
- Test file presence (*.test.ts, *.spec.ts)
- Test types: unit, integration, e2e
- Test coverage (should be >80%)
- Mock/stub patterns for isolation

**Detection code:**
```bash
find . -name "*.test.ts" -o -name "*.spec.ts"
grep -r "describe\|it\|test(" src/  # Test definitions
```

**Coverage targets:**
- Unit tests: 70%+ coverage
- Integration tests: 50%+ of API paths
- E2E tests: All happy paths

### Pillar M: Saga Pattern (Orchestration)

**What to look for:**
- Saga orchestrators
- Compensation/rollback logic
- Event-driven coordination
- Multi-step workflow handling

**Detection code:**
```bash
grep -r "saga\|Saga\|orchestrat\|compensat" src/
grep -r "yield\|async.*retry\|try.*catch" src/
```

**Example:**
```typescript
// ✅ Pillar M implemented
class OrderSaga {
  async execute(order: Order) {
    try {
      await payment.charge(order);
    } catch (e) {
      await payment.refund(order);  // Compensation
      throw e;
    }
  }
}

// ❌ Not implementing Pillar M
async function processOrder(order: Order) {
  await payment.charge(order);  // What if inventory fails?
  await inventory.reserve(order);
}
```

### Pillar Q: Idempotency (Safe Retries)

**What to look for:**
- Idempotency key handling
- Request deduplication
- Safe retry logic
- Idempotent endpoint implementations

**Detection code:**
```bash
grep -r "idempotent\|idempotencyKey\|dedup" src/
grep -r "Idempotent\|Retry\|retryPolicy" src/
```

### Pillar R: Structured Logging

**What to look for:**
- JSON logging format
- Correlation IDs for request tracing
- Structured fields (not string interpolation)
- Structured log levels (debug, info, warn, error)

**Detection code:**
```bash
grep -r "JSON.stringify\|logger\.\|log(" src/
grep -r "correlationId\|traceId\|requestId" src/
```

**Example:**
```typescript
// ✅ Pillar R implemented
logger.info({
  event: 'user_created',
  userId: user.id,
  timestamp: new Date(),
  correlationId: ctx.traceId
});

// ❌ Not implementing Pillar R
console.log(`User created: ${user.id}`);  // String interpolation
```

## Audit Report Structure

A good audit report includes:

### 1. Summary
```
Profile: react-aws
Installed Pillars: A, B, K, L, M, Q, R (7)
Coverage: 71% (5 fully implemented, 2 partial)
Date: 2026-02-28
```

### 2. Per-Pillar Status
```
| Pillar | Status | Coverage | Files | Issues |
|--------|--------|----------|-------|--------|
| A | ✅ | 100% | 5 | 0 |
| B | ⚠️ | 60% | 3 | 2 |
| K | ✅ | 100% | 12 | 0 |
```

### 3. Detailed Findings
For each pillar with issues:
```
Pillar B: Airlock Pattern
  Status: ⚠️ Partial
  Files: src/api/handlers.ts, src/validation/schemas.ts
  Coverage: 60% of endpoints have validation
  Issues:
    - POST /users endpoint missing schema validation
    - PUT /profile lacks input validation
  Files Affected:
    - src/api/handlers.ts:42 (missing validation)
    - src/api/handlers.ts:78 (missing validation)
```

### 4. Recommendations
```
Priority 1 (Do First):
  - Add schema validation to POST /users
  - Implement airlock pattern on PUT /profile

Priority 2 (Important):
  - Complete Pillar Q implementation (idempotency)
  - Add structured logging to error cases
```

## Common Audit Findings

### Finding: Missing Validation
**Pattern:** No airlock at API boundaries
**Fix:** Add Zod schema + parseUser function
**Pillar:** B

### Finding: Untyped IDs
**Pattern:** Using string IDs instead of branded types
**Fix:** Create UserId, OrderId types
**Pillar:** A

### Finding: No Test Structure
**Pattern:** Tests in single file or no tests
**Fix:** Organize by unit/integration/e2e
**Pillar:** K

### Finding: No Retries
**Pattern:** API calls fail on transient errors
**Fix:** Add idempotency keys + safe retry
**Pillar:** Q

### Finding: Console Logs
**Pattern:** `console.log("User created: " + user)`
**Fix:** Structured logger with JSON
**Pillar:** R

## Running Regular Audits

**Monthly Audit:**
```bash
/audit              # Check all pillars
```

**Targeted Audit:**
```bash
/audit A B K        # Check implementation patterns
```

**Tracking:**
- Save audit reports to `.claude/audits/`
- Compare over time to track improvement
- Update roadmap based on findings

## Pro Tips

1. **Start with Core** - Implement A, B, K first
2. **Priority Order** - A → B → K → Q → R → M
3. **Document Decisions** - Record why patterns chosen
4. **Team Review** - Have team discuss findings
5. **Iterate** - Audit regularly, improve incrementally

## Integration with Planning

Use audit findings to create implementation plans:

1. Run audit: `/audit`
2. Identify top 3 gaps
3. Create plan: `/plan "Implement Pillar B airlock pattern"`
4. Execute plan tasks
5. Re-audit to verify improvement
