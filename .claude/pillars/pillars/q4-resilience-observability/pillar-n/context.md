# Pillar N: Context Ubiquity

> TraceID, User, and Signal accessible everywhere

## Rule

A **Request Context** containing TraceID, User, and Cancellation Signal must be accessible at every point in the execution chain without explicit parameter passing.

## Purpose

- Correlate logs across distributed systems
- Enable request cancellation
- Track user identity throughout flow
- Avoid "parameter drilling" through call stacks

## Core Concept

**Context Propagation**: Make request-scoped data (traceId, user, cancellation signal) accessible throughout the execution chain without explicit parameter passing.

**Key Principle**: Use language/framework-native context mechanisms (AsyncLocalStorage, React Context, contextvars) to avoid "parameter drilling" while maintaining clean function signatures.

## Generic Implementation

### Context Definition (Universal)

```typescript
// Framework-agnostic context interface
interface RequestContext {
  // Tracing (for distributed logging)
  traceId: string;
  spanId: string;
  parentSpanId?: string;

  // User identity
  userId?: string;
  sessionId?: string;
  roles: string[];

  // Request control
  signal: AbortSignal;
  startTime: Date;
  deadline?: Date;

  // Metadata
  source: 'web' | 'mobile' | 'api' | 'internal';
  metadata?: Record<string, unknown>;
}
```

### Generic Context Store Pattern

```typescript
// Generic interface for context storage
interface ContextStore<T> {
  // Run a function with context
  run<R>(context: T, fn: () => R): R;

  // Get current context (throws if missing)
  get(): T;

  // Get current context (returns undefined if missing)
  getOptional(): T | undefined;
}
```

### Context Initialization Pattern

```
1. Request arrives at entry point (HTTP handler, event listener, etc.)
2. Create RequestContext with:
   - traceId (from header or generate new)
   - userId (from authentication)
   - AbortSignal (tied to request lifecycle)
   - startTime, source, etc.
3. Store context using framework mechanism
4. Execute request handler
5. Context accessible everywhere in call chain
```

### Usage Pattern

```typescript
// Anywhere in the call chain, access context without passing
async function createOrder(cmd: CreateOrderCommand): Promise<Order> {
  // Get context from storage (no parameter drilling!)
  const ctx = getRequestContext();

  // Use for logging
  logger.info('Creating order', {
    traceId: ctx.traceId,
    userId: ctx.userId
  });

  // Check cancellation
  if (ctx.signal.aborted) {
    throw new RequestCancelledError();
  }

  // Continue with business logic...
  logger.json('ORDER_CREATING', {
    traceId: ctx.traceId,
    userId: ctx.userId,
    orderId: cmd.orderId,
  });

  // Pass signal to long operations
  const result = await db.query(sql, { signal: ctx.signal });

  return result;
}
```

## Implementation Examples

### Example 1: Node.js (AsyncLocalStorage)

```typescript
import { AsyncLocalStorage } from 'async_hooks';

// Create context store
const contextStore = new AsyncLocalStorage<RequestContext>();

export const ContextStore = {
  run<T>(context: RequestContext, fn: () => T): T {
    return contextStore.run(context, fn);
  },

  get(): RequestContext {
    const ctx = contextStore.getStore();
    if (!ctx) {
      throw new Error('No context - ensure middleware initialized');
    }
    return ctx;
  },

  getOptional(): RequestContext | undefined {
    return contextStore.getStore();
  }
};

// Express middleware
function contextMiddleware(req: Request, res: Response, next: NextFunction) {
  const context: RequestContext = {
    traceId: req.headers['x-trace-id'] || crypto.randomUUID(),
    spanId: crypto.randomUUID(),
    userId: req.user?.id,
    sessionId: req.session?.id,
    roles: req.user?.roles || [],
    signal: createAbortSignal(req),
    startTime: new Date(),
    source: 'web'
  };

  res.setHeader('x-trace-id', context.traceId);
  ContextStore.run(context, () => next());
}

// Usage in service
async function createOrder(cmd: CreateOrderCommand): Promise<Order> {
  const ctx = ContextStore.get();

  logger.info('Creating order', { traceId: ctx.traceId, userId: ctx.userId });

  if (ctx.signal.aborted) {
    throw new RequestCancelledError();
  }

  // ... business logic
}
```

### Example 2: React (Context API)

```typescript
import { createContext, useContext, useMemo, useEffect } from 'react';

interface FrontendContext {
  traceId: string;
  userId?: string;
  abortController: AbortController;
}

const RequestContext = createContext<FrontendContext | null>(null);

// Provider component
export function RequestProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const abortController = useMemo(() => new AbortController(), []);

  const context = useMemo(() => ({
    traceId: crypto.randomUUID(),
    userId: user?.id,
    abortController
  }), [user?.id]);

  useEffect(() => {
    return () => abortController.abort();
  }, [abortController]);

  return (
    <RequestContext.Provider value={context}>
      {children}
    </RequestContext.Provider>
  );
}

// Hook to access context
export function useRequestContext() {
  const ctx = useContext(RequestContext);
  if (!ctx) throw new Error('Missing RequestProvider');
  return ctx;
}

// Usage in component
function OrderButton() {
  const ctx = useRequestContext();

  const handleClick = async () => {
    try {
      await createOrder({ userId: ctx.userId, traceId: ctx.traceId });
    } catch (error) {
      if (ctx.abortController.signal.aborted) {
        console.log('Request cancelled');
      }
    }
  };

  return <button onClick={handleClick}>Create Order</button>;
}
```

### Example 3: Python (contextvars)

```python
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional
import uuid

@dataclass
class RequestContext:
    trace_id: str
    span_id: str
    user_id: Optional[str]
    roles: list[str]
    start_time: float

# Create context variable
_request_context: ContextVar[Optional[RequestContext]] = ContextVar(
    'request_context',
    default=None
)

class ContextStore:
    @staticmethod
    def set(context: RequestContext) -> None:
        _request_context.set(context)

    @staticmethod
    def get() -> RequestContext:
        ctx = _request_context.get()
        if ctx is None:
            raise RuntimeError('No context available')
        return ctx

    @staticmethod
    def get_optional() -> Optional[RequestContext]:
        return _request_context.get()

# FastAPI middleware
from fastapi import Request

async def context_middleware(request: Request, call_next):
    context = RequestContext(
        trace_id=request.headers.get('x-trace-id', str(uuid.uuid4())),
        span_id=str(uuid.uuid4()),
        user_id=request.state.user_id if hasattr(request.state, 'user_id') else None,
        roles=request.state.roles if hasattr(request.state, 'roles') else [],
        start_time=time.time()
    )

    ContextStore.set(context)

    response = await call_next(request)
    response.headers['x-trace-id'] = context.trace_id
    return response

# Usage in service
async def create_order(cmd: CreateOrderCommand) -> Order:
    ctx = ContextStore.get()

    logger.info('Creating order', extra={
        'trace_id': ctx.trace_id,
        'user_id': ctx.user_id
    })

    # ... business logic
```

### Example 4: Go (context.Context)

```go
package main

import (
    "context"
    "github.com/google/uuid"
)

type contextKey string

const requestContextKey contextKey = "requestContext"

type RequestContext struct {
    TraceID   string
    SpanID    string
    UserID    *string
    Roles     []string
    StartTime time.Time
}

// Store context
func WithRequestContext(parent context.Context, rc *RequestContext) context.Context {
    return context.WithValue(parent, requestContextKey, rc)
}

// Retrieve context
func GetRequestContext(ctx context.Context) (*RequestContext, error) {
    rc, ok := ctx.Value(requestContextKey).(*RequestContext)
    if !ok {
        return nil, errors.New("no request context")
    }
    return rc, nil
}

// HTTP middleware
func contextMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        traceID := r.Header.Get("X-Trace-ID")
        if traceID == "" {
            traceID = uuid.New().String()
        }

        rc := &RequestContext{
            TraceID:   traceID,
            SpanID:    uuid.New().String(),
            StartTime: time.Now(),
        }

        ctx := WithRequestContext(r.Context(), rc)
        w.Header().Set("X-Trace-ID", traceID)

        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// Usage
func createOrder(ctx context.Context, cmd CreateOrderCommand) (*Order, error) {
    rc, err := GetRequestContext(ctx)
    if err != nil {
        return nil, err
    }

    log.Printf("Creating order: trace_id=%s user_id=%v", rc.TraceID, rc.UserID)

    // ... business logic
}
```

### Passing Context in Fetch

```typescript
// adapters/apiClient.ts

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const ctx = ContextStore.get();

  const response = await fetch(endpoint, {
    ...options,
    headers: {
      ...options.headers,
      'x-trace-id': ctx.traceId,
      'x-user-id': ctx.userId || '',
    },
    signal: ctx.signal,
  });

  if (!response.ok) {
    throw new ApiError(response.status, await response.text());
  }

  return response.json();
}
```

## Good Example

```typescript
// ✅ Context available everywhere without drilling

// Controller
app.post('/orders', contextMiddleware, async (req, res) => {
  const order = await orderService.create(req.body);
  res.json(order);
});

// Service - no context parameter needed
async function createOrder(cmd: CreateOrderCommand) {
  const ctx = ContextStore.get();  // Available!

  logger.json('ORDER_STARTED', { traceId: ctx.traceId });

  const order = await orderRepo.save(cmd);
  await notificationService.notify(order);  // Also has access to ctx

  return order;
}

// Deep in call stack - still available
async function sendEmail(order: Order) {
  const ctx = ContextStore.get();

  await emailClient.send({
    template: 'order-confirmation',
    metadata: { traceId: ctx.traceId },  // For email logs
  });
}
```

## Bad Example

```typescript
// ❌ Parameter drilling
async function createOrder(cmd, traceId, userId, signal) {
  const order = await orderRepo.save(cmd, traceId);
  await notify(order, traceId, userId, signal);
}

async function notify(order, traceId, userId, signal) {
  await sendEmail(order, traceId, userId, signal);
  await sendSms(order, traceId, userId, signal);
}

async function sendEmail(order, traceId, userId, signal) {
  // Drilling through 4 layers!
}
```

## Anti-Patterns

1. **Missing context initialization**
   ```typescript
   // ❌ Forgot middleware
   app.post('/orders', handler);  // No context!
   ```

2. **Global mutable context**
   ```typescript
   // ❌ Race conditions with concurrent requests
   let globalContext = {};
   ```

3. **Ignoring abort signal**
   ```typescript
   // ❌ Request cancelled but work continues
   await longOperation();  // Should check signal
   ```

4. **Context in closure**
   ```typescript
   // ❌ Stale context captured
   const ctx = ContextStore.get();
   setTimeout(() => {
     // ctx may be from different request!
   }, 1000);
   ```

## Exceptions

- Batch jobs may create synthetic context
- Background workers need explicit context passing

## Checklist

- [ ] Middleware initializes context for all requests
- [ ] TraceID propagated in all service calls
- [ ] Abort signal checked in long operations
- [ ] Logs include traceId and userId
- [ ] Cross-service calls forward trace headers
- [ ] No parameter drilling for context

## References

- Related: Pillar R (Observability) - logging with context
- Related: Pillar Q (Idempotency) - intentId in context
- Pattern: AsyncLocalStorage, Thread-Local Storage

## Assets

- Template: `.claude/pillars/pillar-n/context.ts`
- Checklist: `.claude/pillars/pillar-n/checklist.md`

## Changelog

### Version 2.0.0 (2026-03-14)

**Issue**: #194 - Remove tech-stack dependencies

**Changes**:
- ✅ Added framework-agnostic context propagation principles
- ✅ Created generic ContextStore interface
- ✅ Replaced Node.js AsyncLocalStorage and React Context-specific implementations with multi-framework examples:
  - Example 1: Node.js (AsyncLocalStorage)
  - Example 2: React (Context API)
  - Example 3: Python (contextvars)
  - Example 4: Go (context.Context)
- ✅ All framework-specific code moved to clearly labeled "Implementation Examples" section

**Impact**:
- Context propagation pattern now applicable to ANY language/framework
- Developers see native context mechanisms across 4 major ecosystems
- Principle of "avoid parameter drilling" is universal

**Backward compatibility**: Node.js and React examples preserved, now part of multi-language showcase
