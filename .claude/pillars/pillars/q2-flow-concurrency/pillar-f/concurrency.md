# Pillar F: Zero-Trust Concurrency

> Assume race conditions will occur on every T3 write

## Rule

Every Tier 3 write operation must assume a race condition **WILL** occur. Use Optimistic Locking (CAS) to prevent lost updates.

## Purpose

- Prevent "Lost Update" anomalies
- Handle concurrent modifications safely
- Provide clear conflict resolution path
- Maintain data integrity without pessimistic locks

## Core Concept

Concurrent updates to shared data can cause lost updates when multiple processes read-modify-write simultaneously. Use **Compare-And-Swap (CAS)** with version fields to detect and prevent lost updates.

**Key Principle**: Every update includes the expected version number. If the version doesn't match (another process modified it), the update fails and the client must refresh and retry.

## Generic Implementation (TypeScript)

### Entity with Version Field

```typescript
// Universal pattern - works with any storage layer
interface Entity {
  id: string;
  version: number;  // Increment on every update
  // ... other fields
  updatedAt: Date;
}

type Order = Entity & {
  status: OrderStatus;
  items: OrderItem[];
};
```

### Compare-And-Swap Pattern

```typescript
// Generic CAS interface - storage-agnostic
interface CASRepository<T extends Entity> {
  update(
    id: string,
    expectedVersion: number,
    updates: Partial<T>
  ): Promise<T>;
}

// Generic implementation
async function compareAndSwap<T extends Entity>(
  repo: CASRepository<T>,
  id: string,
  expectedVersion: number,
  updates: Partial<T>
): Promise<T> {
  const updated = await repo.update(id, expectedVersion, updates);

  if (!updated) {
    throw new StaleDataError(
      'Entity was modified by another process. Please refresh and retry.'
    );
  }

  return updated;
}
```

### Error Handling

```typescript
// Standard error for version conflicts
class StaleDataError extends Error {
  constructor(message: string, public readonly entity?: string) {
    super(message);
    this.name = 'StaleDataError';
  }
}

// Generic retry wrapper
async function withRetry<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3
): Promise<T> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      if (error instanceof StaleDataError && attempt < maxRetries) {
        // Exponential backoff before retry
        await new Promise(resolve => setTimeout(resolve, 100 * Math.pow(2, attempt)));
        continue;
      }
      throw error;
    }
  }
  throw new Error('Max retries exceeded');
}
```

## Implementation Examples

### Example 1: PostgreSQL / SQL Databases

```typescript
import { Pool } from 'pg';

class PostgresCASRepository<T extends Entity> implements CASRepository<T> {
  constructor(private pool: Pool, private tableName: string) {}

  async update(
    id: string,
    expectedVersion: number,
    updates: Partial<T>
  ): Promise<T> {
    // Atomic update with version check using SQL WHERE clause
    const result = await this.pool.query(`
      UPDATE ${this.tableName}
      SET
        status = $1,
        version = version + 1,
        updated_at = NOW()
      WHERE id = $2 AND version = $3
      RETURNING *
    `, [updates.status, id, expectedVersion]);

    if (result.rowCount === 0) {
      throw new StaleDataError(
        `${this.tableName} was modified by another process`
      );
    }

    return result.rows[0] as T;
  }
}

// Usage
const orderRepo = new PostgresCASRepository<Order>(pool, 'orders');
const updated = await orderRepo.update(orderId, 5, { status: 'shipped' });
```

### Example 2: DynamoDB (NoSQL)

```typescript
import { DynamoDBClient, UpdateItemCommand } from '@aws-sdk/client-dynamodb';
import { marshall, unmarshall } from '@aws-sdk/util-dynamodb';

class DynamoCASRepository<T extends Entity> implements CASRepository<T> {
  constructor(private client: DynamoDBClient, private tableName: string) {}

  async update(
    id: string,
    expectedVersion: number,
    updates: Partial<T>
  ): Promise<T> {
    try {
      const result = await this.client.send(new UpdateItemCommand({
        TableName: this.tableName,
        Key: marshall({ id }),
        UpdateExpression: 'SET #status = :status, #version = :newVersion',
        ConditionExpression: '#version = :expectedVersion',
        ExpressionAttributeNames: {
          '#status': 'status',
          '#version': 'version',
        },
        ExpressionAttributeValues: marshall({
          ':status': updates.status,
          ':newVersion': expectedVersion + 1,
          ':expectedVersion': expectedVersion,
        }),
        ReturnValues: 'ALL_NEW',
      }));

      return unmarshall(result.Attributes!) as T;
    } catch (error: any) {
      if (error.name === 'ConditionalCheckFailedException') {
        throw new StaleDataError('Concurrent modification detected');
      }
      throw error;
    }
  }
}
```

### Example 3: In-Memory (Testing/Development)

```typescript
class InMemoryCASRepository<T extends Entity> implements CASRepository<T> {
  private store = new Map<string, T>();

  async update(
    id: string,
    expectedVersion: number,
    updates: Partial<T>
  ): Promise<T> {
    const current = this.store.get(id);

    if (!current) {
      throw new Error(`Entity ${id} not found`);
    }

    if (current.version !== expectedVersion) {
      throw new StaleDataError(
        `Expected version ${expectedVersion}, but current is ${current.version}`
      );
    }

    const updated = {
      ...current,
      ...updates,
      version: current.version + 1,
      updatedAt: new Date(),
    } as T;

    this.store.set(id, updated);
    return updated;
  }

  // Test helper
  reset() {
    this.store.clear();
  }
}
```

### Example 4: Frontend Integration (Framework-Agnostic)

```typescript
// Generic client-side CAS handler
class CASClient<T extends Entity> {
  constructor(private apiEndpoint: string) {}

  async update(
    id: string,
    currentEntity: T,
    updates: Partial<T>
  ): Promise<T> {
    try {
      const response = await fetch(`${this.apiEndpoint}/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          expectedVersion: currentEntity.version,
          updates,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        if (error.code === 'STALE_DATA') {
          throw new StaleDataError('Entity was modified, please refresh');
        }
        throw new Error(error.message);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof StaleDataError) {
        // Refresh and notify user
        const refreshed = await this.get(id);
        throw new RetryableError('Data changed, refreshed', { refreshed });
      }
      throw error;
    }
  }

  private async get(id: string): Promise<T> {
    const response = await fetch(`${this.apiEndpoint}/${id}`);
    return response.json();
  }
}

// Usage in React
const client = new CASClient<Order>('/api/orders');
try {
  const updated = await client.update(order.id, order, { status: 'shipped' });
  setOrder(updated);
} catch (error) {
  if (error instanceof RetryableError) {
    setOrder(error.context.refreshed);
    showNotification('Order was updated by another user, showing latest');
  }
}

// Usage in Vue/Svelte - same client, different state management
```

## Good Example

```typescript
// ✅ Complete CAS implementation
async function checkout(cmd: CheckoutCommand, ctx: Context) {
  // 1. Read current state
  const cart = await cartRepo.get(cmd.cartId);

  // 2. Validate version matches
  if (cart.version !== cmd.expectedVersion) {
    throw new StaleDataError('Cart was modified');
  }

  // 3. Process with version increment
  const order = await createOrder({
    ...cart,
    version: cart.version + 1,
  });

  // 4. Log with version info
  logger.json('ORDER_CREATED', {
    orderId: order.id,
    fromVersion: cmd.expectedVersion,
    toVersion: order.version,
    traceId: ctx.traceId,
  });

  return order;
}
```

## Bad Example

```typescript
// ❌ No version check - lost updates possible
async function updateOrder(orderId, updates) {
  const order = await db.get(orderId);
  // Another process could modify between read and write!
  order.status = updates.status;
  await db.save(order);  // Overwrites concurrent changes
}

// ❌ Client-side only check
async function updateOrder(orderId, updates) {
  if (localOrder.updatedAt === serverOrder.updatedAt) {
    // Race condition: server could change after this check
    await db.save(updates);
  }
}
```

## Anti-Patterns

1. **Read-modify-write without atomicity**
   ```typescript
   const data = await read();
   data.value = newValue;
   await write(data);  // ❌ Gap between read and write
   ```

2. **Timestamp-based comparison**
   ```typescript
   // ❌ Timestamp precision issues, clock skew
   if (local.updatedAt >= server.updatedAt) { }
   ```

3. **Last-write-wins**
   ```typescript
   // ❌ Silently loses updates
   await db.save(updates);
   ```

4. **Ignoring version mismatch**
   ```typescript
   // ❌ Proceeding despite conflict
   if (version !== expected) console.log('warning');
   await save(data);
   ```

## Exceptions

- **Append-only logs**: Audit trails, event logs don't need locking
- **Idempotent operations**: Operations that produce same result regardless of repetition
- **Read-only operations**: T1 tier doesn't modify data

## Checklist

- [ ] All mutable entities have `version` field
- [ ] Updates use atomic CAS operations (SQL WHERE clause, DynamoDB ConditionExpression, etc.)
- [ ] StaleDataError thrown on version mismatch
- [ ] Client receives clear retry guidance
- [ ] Version included in logs for debugging
- [ ] Storage layer supports conditional writes

## References

- Related: Pillar Q (Idempotency) - prevent duplicate processing
- Related: Pillar M (Saga) - compensation on failure
- Pattern: Optimistic Concurrency Control (OCC)
- Template: `.claude/pillars/pillar-f/optimistic-lock.ts`
- Checklist: `.claude/pillars/pillar-f/checklist.md`

## Changelog

### Version 2.0.0 (2026-03-14)

**Issue**: #194 - Remove tech-stack dependencies

**Changes**:
- ✅ Added framework-agnostic core concepts section
- ✅ Created generic CAS (Compare-And-Swap) repository interface
- ✅ Replaced AWS DynamoDB-specific implementation with multi-storage examples:
  - Example 1: PostgreSQL (SQL with WHERE version clause)
  - Example 2: DynamoDB (ConditionExpression)
  - Example 3: In-Memory (Map-based)
  - Example 4: Frontend (fetch with version headers)
- ✅ All storage-specific code moved to clearly labeled "Implementation Examples" section

**Impact**:
- Core optimistic locking pattern now applicable to ANY storage system
- Developers can implement CAS with their database of choice
- No cloud vendor lock-in (AWS → universal)

**Backward compatibility**: DynamoDB example preserved, now one of four options
