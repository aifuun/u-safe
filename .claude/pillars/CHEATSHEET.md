# AI_DEV_PROT v15 Cheatsheet

> Quick reference for daily development

## Tier Classification

```
T1 Direct    │ Read-only, simple UI       │ View → Adapter
T2 Logic     │ Forms, local state, FSM    │ View → Headless → Adapter
T3 Saga      │ Distributed writes, $$$    │ View → Saga → [Adapters]
```

## 18 Pillars - Quick Lookup

See **README.md** for complete overview. Use command `*pillar <letter>` for details.

| ID | Check | ID | Check |
|----|-------|----|-------|
| **A** | Branded types for IDs | **J** | State close to usage |
| **B** | Schema-first validation | **K** | Test pyramid |
| **C** | Mock from schema | **L** | No JSX in hooks |
| **D** | FSM states, no booleans | **M** | Compensation stack |
| **E** | Match tier to pattern | **N** | TraceId propagation |
| **F** | CAS before T3 writes | **O** | 202 + poll pattern |
| **G** | @trigger/@listen | **P** | Circuit breaker |
| **H** | Policy.assert() | **Q** | Intent-ID caching |
| **I** | No deep imports | **R** | JSON semantic logs |

## T3 Saga Entry Template

```typescript
async function processSaga(cmd: Command) {
  // 1. Idempotency (Pillar Q)
  const cached = await Cache.get(`intent:${cmd.intentId}`);
  if (cached) return cached;

  // 2. Concurrency (Pillar F)
  const entity = await Repo.get(cmd.entityId);
  if (entity.version !== cmd.expectedVersion) {
    throw new StaleDataError();
  }

  // 3. Saga (Pillar M)
  const compensations = [];
  try {
    compensations.push(() => undoStep1());
    await step1();
    // ... more steps
  } catch (e) {
    while (compensations.length) await compensations.pop()();
    throw e;
  }

  // 4. Cache result
  await Cache.set(`intent:${cmd.intentId}`, result);
  return result;
}
```

## Key Concepts

### traceId vs intentId

| | traceId | intentId |
|---|---|---|
| **Scope** | Single HTTP/IPC request | Single user action (spans retries) |
| **Purpose** | Log correlation | Idempotency |
| **Created** | Once per request (middleware) | Once per command (client) |
| **Example** | `trace-abc-123` | `intent-xyz-789` |

**Key Difference**: Multiple requests can share same intentId (retries). Multiple commands can share same traceId (batch).

## Anti-Patterns (Never Do)

```typescript
// ❌ Primitive ID
function getUser(id: string) { }

// ❌ Boolean flags (use FSM)
const [isLoading, setIsLoading] = useState(false);

// ❌ Deep import
import { Button } from '../auth/components/internal/Button';

// ❌ T3 without idempotency
async function pay(amount) { await charge(amount); }

// ❌ Text logs (use structured JSON)
log.info("Payment failed");
```

## Architecture Layers

> "UI 薄、Service 厚、Adapter 狠"

| Layer | ✅ Best Practice | ❌ Anti-Pattern |
|-------|------------------|-----------------|
| **UI** | Only call actions, render state | Business logic in `onClick` |
| **Service** | Complex rules, FSM, orchestration | Thin wrapper around API |
| **Adapter** | Field mapping, Zod validation | Passthrough of raw JSON |
| **State** | Immutable updates | Direct mutation |

## Development Checklist

Complete unified checklist for the entire development workflow:

**`.claude/pillars/checklists/DEVELOPMENT_CHECKLIST.md`**
- Phase 1: Pre-Code Planning
- Phase 2: In-Code Implementation
- Phase 3: Post-Code Review

---

**Version**: v15
**Last Updated**: 2026-02-05
