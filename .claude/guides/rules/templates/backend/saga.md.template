---
category: "backend"
title: "Saga"
description: "Saga compensation pattern"
tags: [typescript, aws]
profiles: [nextjs-aws]
pillar_refs: [M]
paths: ['**/*.{ts,tsx}']
version: "1.0.0"
last_updated: "2026-03-27"
---

---
paths: "**/*Saga.ts"
---
# Saga/Workflow Rules

> 📖 **Complete Guide**: `.claude/pillars/pillars/q4-resilience-observability/pillar-m/saga.md`
> T3 operations (distributed writes, payments). High risk, high protection.

## Quick Check (30 seconds)
- [ ] Every step has compensation function defined
- [ ] `compensations.push(undo)` BEFORE executing step
- [ ] Rollback in reverse order (LIFO) on failure
- [ ] `intentId` checked at entry (Pillar Q: Idempotency)
- [ ] `expectedVersion` checked before write (Pillar F: Concurrency)
- [ ] All state transitions logged with `traceId` (Pillar R)
- [ ] Compensations are idempotent (safe to retry)

## Core Pattern: T3 Saga Entry
```typescript
// Standard saga pattern - copy directly
async function processOrderSaga(cmd: OrderCommand) {
  // 1. Idempotency check (Pillar Q)
  const cached = await Cache.get(`intent:${cmd.intentId}`);
  if (cached) return cached;

  // 2. Version check (Pillar F)
  const order = await orderRepo.get(cmd.orderId);
  if (order.version !== cmd.expectedVersion) throw new StaleDataError();

  // 3. Execute with compensation (Pillar M)
  const compensations: Array<() => Promise<void>> = [];
  try {
    // Step 1: Charge payment
    compensations.push(() => refundPayment(paymentId));
    await chargePayment(cmd.paymentId);

    // Step 2: Reserve inventory
    compensations.push(() => releaseInventory(cmd.items));
    await reserveInventory(cmd.items);

    // Success
    const result = { success: true, orderId: cmd.orderId };
    await Cache.set(`intent:${cmd.intentId}`, result);
    return result;
  } catch (error) {
    // Rollback in reverse order
    while (compensations.length > 0) {
      await compensations.pop()?.();
    }
    throw error;
  }
}
```

## When to Read Full Pillar?
- ❓ Need complete Saga theory and patterns → Read Pillar M
- ❓ Unsure about error handling strategies → Read Pillar M
- ❓ Need idempotency implementation details → Read Pillar Q
- ❓ Need concurrency control (CAS) examples → Read Pillar F
- ❓ Want observability best practices → Read Pillar R

## Related
- **Pillar M**: `.claude/pillars/pillars/q4-resilience-observability/pillar-m/saga.md` (complete Saga guide)
- **Pillar Q**: Idempotency (intent caching)
- **Pillar F**: Concurrency (optimistic locking)
- **Pillar R**: Observability (semantic logging)
- **Rule**: `query-transactions.md` (database transactions)
