# Pillar Q: The Idempotency Barrier

> Prevent duplicate side effects with Intent-ID

## Rule

All Tier 3 state-changing commands must contain a globally unique **Intent-ID** (UUID). This ID is checked before processing to prevent duplicate execution.

## Purpose

- Prevent double-charging on network retries
- Handle timeout + retry scenarios safely
- Block replay attacks
- Enable safe client-side retry logic

## Implementation

### Command with Intent-ID

```typescript
interface CheckoutCommand {
  intentId: IntentId;        // Unique per user action
  orderId: OrderId;
  amount: Money;
  expectedVersion: number;
}

type IntentId = string & { readonly __brand: 'IntentId' };

function createIntentId(): IntentId {
  return crypto.randomUUID() as IntentId;
}
```

### Idempotency Barrier Pattern

```typescript
async function processCommand<T>(
  intentId: IntentId,
  execute: () => Promise<T>
): Promise<T> {
  const cacheKey = `intent:${intentId}`;

  // 1. CHECK: Already processed?
  const cached = await cache.get(cacheKey);
  if (cached) {
    return cached as T;  // Return previous result
  }

  // 2. LOCK: Mark as processing
  const locked = await cache.setNX(cacheKey, 'PROCESSING', { EX: 300 });
  if (!locked) {
    // Another process is handling this
    throw new ConcurrentProcessingError('Request already in progress');
  }

  try {
    // 3. EXECUTE: Run the actual logic
    const result = await execute();

    // 4. STORE: Cache the result
    await cache.set(cacheKey, JSON.stringify(result), { EX: 86400 });

    return result;
  } catch (error) {
    // Remove lock on failure (allow retry)
    await cache.del(cacheKey);
    throw error;
  }
}
```

### Usage in Saga

```typescript
async function checkoutSaga(cmd: CheckoutCommand, ctx: Context) {
  // Idempotency barrier FIRST
  return processCommand(cmd.intentId, async () => {
    // All saga logic inside the barrier
    const compensations: Compensation[] = [];

    try {
      // Step 1: Charge
      compensations.push(() => refund(txId));
      const txId = await charge(cmd.amount);

      // Step 2: Update order
      compensations.push(() => revertOrder(cmd.orderId));
      await updateOrder(cmd.orderId, { status: 'paid' });

      return { success: true, transactionId: txId };
    } catch (error) {
      await executeCompensations(compensations);
      throw error;
    }
  });
}
```

### Client-Side Generation

```typescript
// React hook for idempotent actions
function useIdempotentAction<T>(
  action: (intentId: IntentId) => Promise<T>
) {
  const [intentId, setIntentId] = useState<IntentId | null>(null);
  const [state, setState] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  const execute = async () => {
    // Generate intent ID once per user action
    const id = intentId ?? createIntentId();
    setIntentId(id);
    setState('loading');

    try {
      const result = await action(id);
      setState('success');
      return result;
    } catch (error) {
      setState('error');
      // Keep same intentId for retry!
      throw error;
    }
  };

  const reset = () => {
    setIntentId(null);  // New ID for new action
    setState('idle');
  };

  return { execute, reset, state, canRetry: state === 'error' };
}

// Usage
function CheckoutButton() {
  const { execute, state, canRetry } = useIdempotentAction(
    (intentId) => checkoutApi.process({ intentId, ...orderData })
  );

  return (
    <button onClick={execute} disabled={state === 'loading'}>
      {canRetry ? 'Retry' : 'Checkout'}
    </button>
  );
}
```

### Generic Cache Interface

```typescript
// Storage-agnostic idempotency cache interface
interface IdempotencyCache {
  // Check if intent was already processed
  check(intentId: IntentId): Promise<unknown | null>;

  // Lock intent for processing (returns true if locked successfully)
  lock(intentId: IntentId, ttlSeconds?: number): Promise<boolean>;

  // Store result after successful processing
  store(intentId: IntentId, result: unknown, ttlSeconds?: number): Promise<void>;

  // Remove lock on failure (allow retry)
  unlock(intentId: IntentId): Promise<void>;
}

// Sentinel value for "in progress"
const PROCESSING = '__PROCESSING__';

// Possible states
type CacheValue = typeof PROCESSING | { result: unknown };
```

## Implementation Examples

### Example 1: Redis (Distributed Cache)

```typescript
import Redis from 'ioredis';

class RedisIdempotencyCache implements IdempotencyCache {
  constructor(private redis: Redis) {}

  async check(intentId: IntentId): Promise<unknown | null> {
    const result = await this.redis.get(`intent:${intentId}`);
    if (!result) return null;
    if (result === PROCESSING) {
      throw new ConcurrentProcessingError('Request in progress');
    }
    return JSON.parse(result);
  }

  async lock(intentId: IntentId, ttlSeconds = 300): Promise<boolean> {
    const result = await this.redis.set(
      `intent:${intentId}`,
      PROCESSING,
      'EX', ttlSeconds,
      'NX'  // Set only if Not eXists
    );
    return result === 'OK';
  }

  async store(intentId: IntentId, result: unknown, ttlSeconds = 86400): Promise<void> {
    await this.redis.set(
      `intent:${intentId}`,
      JSON.stringify(result),
      'EX', ttlSeconds
    );
  }

  async unlock(intentId: IntentId): Promise<void> {
    await this.redis.del(`intent:${intentId}`);
  }
}
```

### Example 2: In-Memory (Development/Testing)

```typescript
class InMemoryIdempotencyCache implements IdempotencyCache {
  private store = new Map<string, { value: unknown; expiresAt: number }>();

  async check(intentId: IntentId): Promise<unknown | null> {
    this.cleanup();
    const entry = this.store.get(intentId);
    if (!entry) return null;
    if (entry.value === PROCESSING) {
      throw new ConcurrentProcessingError('Request in progress');
    }
    return entry.value;
  }

  async lock(intentId: IntentId, ttlSeconds = 300): Promise<boolean> {
    this.cleanup();
    if (this.store.has(intentId)) return false;

    this.store.set(intentId, {
      value: PROCESSING,
      expiresAt: Date.now() + ttlSeconds * 1000
    });
    return true;
  }

  async store(intentId: IntentId, result: unknown, ttlSeconds = 86400): Promise<void> {
    this.store.set(intentId, {
      value: result,
      expiresAt: Date.now() + ttlSeconds * 1000
    });
  }

  async unlock(intentId: IntentId): Promise<void> {
    this.store.delete(intentId);
  }

  private cleanup() {
    const now = Date.now();
    for (const [key, entry] of this.store.entries()) {
      if (entry.expiresAt < now) {
        this.store.delete(key);
      }
    }
  }
}
```

### Example 3: DynamoDB (NoSQL)

```typescript
import { DynamoDBClient, GetItemCommand, PutItemCommand, DeleteItemCommand } from '@aws-sdk/client-dynamodb';
import { marshall, unmarshall } from '@aws-sdk/util-dynamodb';

class DynamoIdempotencyCache implements IdempotencyCache {
  constructor(
    private client: DynamoDBClient,
    private tableName: string
  ) {}

  async check(intentId: IntentId): Promise<unknown | null> {
    const result = await this.client.send(new GetItemCommand({
      TableName: this.tableName,
      Key: marshall({ intentId })
    }));

    if (!result.Item) return null;

    const item = unmarshall(result.Item);

    // Check if expired
    if (item.expiresAt < Date.now() / 1000) {
      return null;
    }

    if (item.value === PROCESSING) {
      throw new ConcurrentProcessingError('Request in progress');
    }

    return item.value;
  }

  async lock(intentId: IntentId, ttlSeconds = 300): Promise<boolean> {
    try {
      await this.client.send(new PutItemCommand({
        TableName: this.tableName,
        Item: marshall({
          intentId,
          value: PROCESSING,
          expiresAt: Math.floor(Date.now() / 1000) + ttlSeconds
        }),
        ConditionExpression: 'attribute_not_exists(intentId)'
      }));
      return true;
    } catch (error: any) {
      if (error.name === 'ConditionalCheckFailedException') {
        return false;  // Already exists
      }
      throw error;
    }
  }

  async store(intentId: IntentId, result: unknown, ttlSeconds = 86400): Promise<void> {
    await this.client.send(new PutItemCommand({
      TableName: this.tableName,
      Item: marshall({
        intentId,
        value: result,
        expiresAt: Math.floor(Date.now() / 1000) + ttlSeconds
      })
    }));
  }

  async unlock(intentId: IntentId): Promise<void> {
    await this.client.send(new DeleteItemCommand({
      TableName: this.tableName,
      Key: marshall({ intentId })
    }));
  }
}
```

### Example 4: PostgreSQL (SQL Database)

```typescript
import { Pool } from 'pg';

class PostgresIdempotencyCache implements IdempotencyCache {
  constructor(private pool: Pool) {}

  async check(intentId: IntentId): Promise<unknown | null> {
    const result = await this.pool.query(
      `SELECT value, expires_at FROM idempotency_cache
       WHERE intent_id = $1 AND expires_at > NOW()`,
      [intentId]
    );

    if (result.rowCount === 0) return null;

    const { value } = result.rows[0];
    if (value === PROCESSING) {
      throw new ConcurrentProcessingError('Request in progress');
    }

    return JSON.parse(value);
  }

  async lock(intentId: IntentId, ttlSeconds = 300): Promise<boolean> {
    try {
      await this.pool.query(
        `INSERT INTO idempotency_cache (intent_id, value, expires_at)
         VALUES ($1, $2, NOW() + INTERVAL '${ttlSeconds} seconds')`,
        [intentId, PROCESSING]
      );
      return true;
    } catch (error: any) {
      if (error.code === '23505') {  // Unique violation
        return false;
      }
      throw error;
    }
  }

  async store(intentId: IntentId, result: unknown, ttlSeconds = 86400): Promise<void> {
    await this.pool.query(
      `INSERT INTO idempotency_cache (intent_id, value, expires_at)
       VALUES ($1, $2, NOW() + INTERVAL '${ttlSeconds} seconds')
       ON CONFLICT (intent_id)
       DO UPDATE SET value = EXCLUDED.value, expires_at = EXCLUDED.expires_at`,
      [intentId, JSON.stringify(result)]
    );
  }

  async unlock(intentId: IntentId): Promise<void> {
    await this.pool.query(
      `DELETE FROM idempotency_cache WHERE intent_id = $1`,
      [intentId]
    );
  }
}

// Table schema:
// CREATE TABLE idempotency_cache (
//   intent_id VARCHAR(255) PRIMARY KEY,
//   value TEXT NOT NULL,
//   expires_at TIMESTAMP NOT NULL
// );
// CREATE INDEX idx_expires_at ON idempotency_cache(expires_at);
```

## Good Example

```typescript
// ✅ Complete idempotency implementation
async function processPayment(cmd: PaymentCommand, ctx: Context) {
  logger.json('IDEMPOTENCY_CHECK', {
    intentId: cmd.intentId,
    traceId: ctx.traceId,
  });

  // Check cache first
  const cached = await idempotencyCache.check(cmd.intentId);
  if (cached) {
    logger.json('IDEMPOTENCY_HIT', { intentId: cmd.intentId });
    return cached;
  }

  // Lock and process
  if (!await idempotencyCache.lock(cmd.intentId)) {
    throw new ConcurrentProcessingError();
  }

  try {
    const result = await executePayment(cmd);
    await idempotencyCache.store(cmd.intentId, result);
    return result;
  } catch (error) {
    await idempotencyCache.unlock(cmd.intentId);
    throw error;
  }
}
```

## Bad Example

```typescript
// ❌ No idempotency - double charge possible
async function processPayment(amount) {
  return await stripe.charge(amount);
  // Network timeout + client retry = double charge!
}

// ❌ Client-side only prevention
function PayButton() {
  const [clicked, setClicked] = useState(false);

  const handleClick = () => {
    if (clicked) return;  // ❌ Page refresh resets this
    setClicked(true);
    processPayment();
  };
}

// ❌ Database-based without proper locking
async function processPayment(orderId) {
  const order = await db.get(orderId);
  if (order.paid) return;  // ❌ Race condition gap
  await stripe.charge();
  order.paid = true;
  await db.save(order);
}
```

## Anti-Patterns

1. **UI-only duplicate prevention**
   ```typescript
   // ❌ Doesn't survive page refresh
   button.disabled = true;
   ```

2. **Status check without atomicity**
   ```typescript
   // ❌ Gap between check and update
   if (!processed) {
     await process();
     processed = true;
   }
   ```

3. **Request-scoped deduplication**
   ```typescript
   // ❌ Different requests get different IDs
   const requestId = generateId();
   ```

4. **Missing cache on success**
   ```typescript
   // ❌ Result not stored, retry re-executes
   if (cached) return cached;
   return await execute();  // Forgot to cache!
   ```

## Exceptions

- Read-only operations (T1)
- Operations already idempotent by nature (e.g., setting absolute value)

## Checklist

- [ ] All T3 commands have `intentId` field
- [ ] Client generates intentId once per user action
- [ ] Server checks cache before processing
- [ ] Lock acquired before execution
- [ ] Result cached after success
- [ ] Lock released on failure (enable retry)
- [ ] TTL set on cache entries

## References

- Related: Pillar F (Concurrency) - version checks
- Related: Pillar M (Saga) - compensation on failure
- Template: `.claude/pillars/pillar-q/idempotency.ts`
- Checklist: `.claude/pillars/pillar-q/checklist.md`
- Audit: `.claude/pillars/pillar-q/audit.ts`

## Changelog

### Version 2.0.0 (2026-03-14)

**Issue**: #194 - Remove tech-stack dependencies

**Changes**:
- ✅ Added framework-agnostic idempotency barrier principles
- ✅ Created generic IdempotencyCache interface
- ✅ Replaced Redis-specific implementation with multi-storage examples:
  - Example 1: Redis (distributed cache with SET NX)
  - Example 2: In-Memory (Map with TTL cleanup)
  - Example 3: DynamoDB (conditional writes)
  - Example 4: PostgreSQL (unique constraint)
- ✅ All storage-specific code moved to clearly labeled "Implementation Examples" section

**Impact**:
- Idempotency pattern now applicable to ANY caching/storage system
- Developers can implement with their infrastructure of choice
- No dependency on specific cache technology (Redis → universal)

**Backward compatibility**: Redis example preserved, now one of four storage options
