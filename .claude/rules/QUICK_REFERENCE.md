# Rules Quick Reference - Top 20 Most-Used

> Fast lookup for the most frequently used technical rules. See [INDEX.md](./INDEX.md) for complete catalog.

**Version**: 1.0 | **Last Updated**: 2026-02-05

---

## Top 20 Rules by Usage Frequency

### 🔥 Daily Use (Every Session)

#### 1. [workflow.md](./core/workflow.md) - MVP/Issues/Plans Coordination
```typescript
// Check .claude/plans/active/, docs/dev/MVP*.md, .claude/MEMORY.md
✓ Read MVP.md at session start
✓ Update active plan when switching tasks
✓ Sync MEMORY.md with major changes
```

#### 2. [naming.md](./core/naming.md) - Naming Conventions
```typescript
// Single source of truth for all names
✓ PascalCase for types/components
✓ camelCase for functions/variables
✓ kebab-case for files
✓ Check existing patterns before creating new names
```

#### 3. [debugging.md](./core/debugging.md) - Systematic Debugging
```typescript
// Semantic logging with context
logger.info('user:login:attempt', { userId, timestamp });
✓ Use semantic IDs (domain:entity:action)
✓ Include traceId in all logs
✓ Log at boundaries (entry/exit/error)
```

---

### 🏗️ Architecture (Every Feature)

#### 4. [clean-architecture.md](./architecture/clean-architecture.md) - Layer Separation
```typescript
// Dependencies MUST point inward
kernel/ ← domains/ ← modules/ ← components/
✓ No outer layer imports inner layer
✓ Use dependency inversion for I/O
✓ Validate with ESLint boundary rules
```

#### 5. [headless.md](./architecture/headless.md) - Logic-UI Separation
```typescript
// No JSX in hooks
function useUserLogic() {
  const [state, setState] = useState({ status: 'idle' });
  return { state, load }; // Data + actions only
}
✓ Return { state, ...actions }, never JSX
✓ FSM union types for state
✓ Test without React Testing Library
```

#### 6. [service-layer.md](./architecture/service-layer.md) - Service Orchestration
```typescript
// IO-first pattern
async function createOrder(cmd: CreateOrderCmd): Promise<OrderId> {
  const payment = await paymentAdapter.charge(cmd.amount);
  const inventory = await inventoryAdapter.reserve(cmd.items);
  return await orderRepo.save({ payment, inventory });
}
✓ Services orchestrate, don't contain logic
✓ Call adapters for I/O
✓ Return domain types
```

#### 7. [adapters.md](./architecture/adapters.md) - IO Boundaries
```typescript
// No business logic in adapters
export const userApi = {
  fetchUser: async (id: UserId): Promise<User> => {
    const res = await fetch(`/users/${id}`);
    return userSchema.parse(await res.json()); // Airlock only
  }
};
✓ Pure I/O operations
✓ Schema validation at boundary
✓ No error handling beyond HTTP status
```

---

### ⚛️ Frontend (React/UI Work)

#### 8. [zustand-hooks.md](./frontend/zustand-hooks.md) - Zustand Safety
```typescript
// Prevent infinite loops
const user = useUserStore(state => state.user); // ✓ Scalar
const user = useUserStore(state => ({ user: state.user })); // ✗ New object
✓ Select scalars or use shallow comparator
✓ Never return new objects in selector
```

#### 9. [stores.md](./frontend/stores.md) - Vanilla Stores
```typescript
// No hooks in store files
export const userStore = create<UserState>()((set) => ({
  user: null,
  login: (u) => set({ user: u })
}));
✓ Use vanilla store pattern
✓ No useStore calls inside store file
```

#### 10. [design-system.md](./frontend/design-system.md) - Component Library
```typescript
// Consistent UI patterns
<Button variant="primary" size="md" />
✓ Use design tokens
✓ Headless UI + Tailwind
✓ No inline styles
```

#### 11. [views.md](./frontend/views.md) - View Layer
```typescript
// Thin views, delegate to headless
function UserView() {
  const { state, load } = useUserLogic();
  return <div>{state.status === 'loading' ? '...' : state.data.name}</div>;
}
✓ Max 50 lines per view
✓ No business logic
✓ Consume headless hooks only
```

---

### 🔧 Backend (Services/Lambda)

#### 12. [saga.md](./backend/saga.md) - Saga/Compensation
```typescript
// T3 operations require compensation
const compensations = [];
try {
  compensations.push(() => refundPayment(id));
  await chargePayment(id);
  // ...more steps
} catch {
  while (compensations.length) await compensations.pop()?.();
}
✓ Push compensation BEFORE executing step
✓ Rollback in reverse order (LIFO)
✓ Check intentId + expectedVersion
```

#### 13. [lambda-typescript-esm.md](./backend/lambda-typescript-esm.md) - Lambda + ESM
```typescript
// AWS Lambda with TypeScript + ESM
export const handler = async (event: APIGatewayEvent) => {
  return { statusCode: 200, body: JSON.stringify(result) };
};
✓ Use .mjs extension or "type": "module"
✓ esbuild with format: 'esm'
✓ Import with .js extensions
```

#### 14. [query-transactions.md](./backend/query-transactions.md) - DynamoDB Patterns
```typescript
// Optimistic locking with expectedVersion
await ddb.transactWrite({
  TransactItems: [{
    Update: {
      ConditionExpression: 'version = :v',
      UpdateExpression: 'SET #data = :data, version = :newV'
    }
  }]
});
✓ Use transactions for multi-item writes
✓ Always check version for updates
✓ Idempotent operations
```

---

### ☁️ Infrastructure (Deployment/Operations)

#### 15. [cdk-deploy.md](./infrastructure/cdk-deploy.md) - CDK Workflow
```bash
# Standard deployment flow
cdk diff           # Review changes
cdk deploy         # Deploy to AWS
✓ Always run diff first
✓ Never skip tests before deploy
✓ Use --profile for multi-account
```

#### 16. [secrets.md](./infrastructure/secrets.md) - Secrets Management
```typescript
// NEVER hardcode secrets
const apiKey = process.env.API_KEY; // ✓ From env
const apiKey = 'sk-1234...'; // ✗ NEVER
✓ Use AWS Secrets Manager
✓ Use .env.local (gitignored)
✓ Rotate secrets regularly
```

#### 17. [diagnostic-export-logging.md](./infrastructure/diagnostic-export-logging.md) - Structured Logging
```typescript
// JSON semantic logging
logger.info('payment:charge:success', {
  traceId, userId, amount, paymentId
});
✓ Use semantic IDs (domain:entity:action)
✓ Include traceId in all logs
✓ Export diagnostics on errors
```

#### 18. [time-handling.md](./infrastructure/time-handling.md) - Timestamps
```typescript
// Always use ISO 8601 UTC
const now = new Date().toISOString(); // ✓
const now = Date.now(); // ✗ Not serializable
✓ Store as ISO string
✓ Convert to local in UI only
```

---

### 📋 Development (Tests/Files)

#### 19. [infinite-loop-prevention.md](./development/infinite-loop-prevention.md) - React Loops
```typescript
// Common causes
useEffect(() => { setCount(count + 1); }); // ✗ No deps = every render
useEffect(() => { setCount(count + 1); }, [count]); // ✗ Depends on self
✓ Always specify dependency array
✓ Don't depend on values you modify
✓ Use useCallback for stable functions
```

#### 20. [typescript-strict.md](./languages/typescript-strict.md) - Type Safety
```typescript
// Strict mode enabled
"strict": true,
"noImplicitAny": true,
"strictNullChecks": true
✓ No 'any' types
✓ Handle null/undefined explicitly
✓ Use branded types for IDs
```

---

## Common Violations → Quick Fixes

| Violation | Quick Fix | Rule |
|-----------|-----------|------|
| Deep import across layers | Use dependency inversion | [clean-architecture.md](./architecture/clean-architecture.md) |
| JSX in headless hook | Move JSX to view component | [headless.md](./architecture/headless.md) |
| New object in Zustand selector | Select scalar or use shallow | [zustand-hooks.md](./frontend/zustand-hooks.md) |
| Missing compensation in saga | Add `compensations.push(undo)` before step | [saga.md](./backend/saga.md) |
| Hardcoded API key | Move to env var + Secrets Manager | [secrets.md](./infrastructure/secrets.md) |
| Missing traceId in logs | Add `{ traceId }` to log context | [diagnostic-export-logging.md](./infrastructure/diagnostic-export-logging.md) |
| `Date.now()` in API response | Use `.toISOString()` | [time-handling.md](./infrastructure/time-handling.md) |
| Infinite useEffect loop | Add dependency array or use useCallback | [infinite-loop-prevention.md](./development/infinite-loop-prevention.md) |

---

## File Type → Auto-Triggered Rules

Visual cheat sheet showing which Rules apply to which file patterns:

```
**/*.ts, **/*.tsx
├─ [typescript-strict.md] - Strict mode, no 'any'
├─ [naming.md] - camelCase functions, PascalCase types
└─ [debugging.md] - Semantic logging

**/headless/*.ts
├─ [headless.md] - No JSX, return { state, actions }
└─ [infinite-loop-prevention.md] - useEffect dependencies

**/services/*.ts
├─ [service-layer.md] - IO-first orchestration
└─ [adapters.md] - Call adapters for I/O

**/stores/*.ts
├─ [stores.md] - Vanilla store pattern
└─ [zustand-hooks.md] - Selector safety

**/lambda/**
├─ [lambda-typescript-esm.md] - ESM + .mjs
├─ [lambda-local-first.md] - Test locally first
└─ [diagnostic-export-logging.md] - JSON logs

**/*Saga.ts
├─ [saga.md] - Compensation pattern
├─ [query-transactions.md] - Optimistic locking
└─ [debugging.md] - Trace all state transitions

infra/**
├─ [cdk-deploy.md] - Diff before deploy
├─ [secrets.md] - No hardcoded secrets
└─ [aws-services.md] - AWS best practices

.claude/plans/**
├─ [workflow.md] - MVP/Issues/Plans coordination
└─ [planning-context.md] - Context management

docs/**
└─ [docs.md] - Documentation standards
```

---

## See Also

- **[INDEX.md](./INDEX.md)** - Complete catalog of all 40 Rules
- **[README.md](./README.md)** - Rules system overview
- **[templates/RULE_TEMPLATE.md](./templates/RULE_TEMPLATE.md)** - Create new Rules

---

**When to use this?** Daily reference for most common Rules
**When to use INDEX.md?** Finding Rules by scenario or Pillar
**When to use full Rule file?** Need complete context and examples
