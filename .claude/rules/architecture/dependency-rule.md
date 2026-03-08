---
paths:
  - "src/**/*.ts"
  - "**/*.ts"
---

# Dependency Rule - Circular Dependency Detection

> 📖 **Architecture Overview**: See `clean-architecture.md`
> This Rule focuses on detecting and preventing circular dependencies.

## Quick Check
- [ ] No circular dependencies (verify with `madge` or `dpdm`)
- [ ] Dependencies flow inward (outer → inner layers)
- [ ] Interfaces used to break circular deps (Dependency Inversion)
- [ ] CI runs circular dependency checks on every PR

## Core Problem: Circular Dependencies

### What Are Circular Dependencies?
```
A.ts imports B.ts
    ↓
B.ts imports C.ts
    ↓
C.ts imports A.ts  ← CIRCULAR!
```

**Why Bad?**
- Hard to reason about code flow
- Difficult to test in isolation
- Module initialization order issues
- Tight coupling prevents refactoring
- Can cause runtime errors (especially in Node.js)

### Real Example: Circular Dependency
```typescript
// ❌ CIRCULAR DEPENDENCY

// services/userService.ts
import { orderService } from './orderService';

export function getUserOrders(userId: UserId) {
  return orderService.getOrdersByUser(userId);  // Calls orderService
}

// services/orderService.ts
import { userService } from './userService';  // ← CIRCULAR!

export function getOrderWithUser(orderId: OrderId) {
  const order = getOrder(orderId);
  const user = userService.getUser(order.userId);  // ← Calls userService
  return { ...order, user };
}

// Result: Module initialization error or runtime crash
```

## Solution 1: Dependency Inversion

Break cycles by extracting interfaces to a lower layer (kernel).

### Pattern: Extract Interface to Kernel
```typescript
// ✅ CORRECT - No circular dependency

// kernel/interfaces/UserService.ts
export interface IUserService {
  getUser(id: UserId): Promise<User>;
  getUserOrders(id: UserId): Promise<Order[]>;
}

// modules/user/userService.ts
import type { IUserService } from '@/kernel/interfaces/UserService';

export const userService: IUserService = {
  async getUser(id) {
    return userRepository.findById(id);
  },
  async getUserOrders(id) {
    // Import orderService HERE (not at top level)
    const { orderService } = await import('./orderService');
    return orderService.getOrdersByUser(id);
  },
};

// modules/order/orderService.ts
import type { IUserService } from '@/kernel/interfaces/UserService';

// Injected dependency
export function createOrderService(userSvc: IUserService) {
  return {
    async getOrderWithUser(orderId: OrderId) {
      const order = await getOrder(orderId);
      const user = await userSvc.getUser(order.userId);  // ✅ No circular import
      return { ...order, user };
    },
  };
}
```

## Solution 2: Extract Shared Code to Lower Layer

Move shared logic down to kernel or domains.

```typescript
// ❌ BEFORE - Circular between domains

// domains/user/User.ts
import { Order } from '../order/Order';  // ← Cross-domain import

export interface User {
  id: UserId;
  orders: Order[];  // ← Circular!
}

// domains/order/Order.ts
import { User } from '../user/User';  // ← Cross-domain import

export interface Order {
  id: OrderId;
  user: User;  // ← Circular!
}

// ✅ AFTER - Extract IDs to kernel

// kernel/types/ids.ts
export type UserId = string & { readonly __brand: unique symbol };
export type OrderId = string & { readonly __brand: unique symbol };

// domains/user/User.ts
import type { UserId, OrderId } from '@/kernel/types/ids';

export interface User {
  id: UserId;
  orderIds: OrderId[];  // ← Just IDs, no circular import
}

// domains/order/Order.ts
import type { OrderId, UserId } from '@/kernel/types/ids';

export interface Order {
  id: OrderId;
  userId: UserId;  // ← Just ID, no circular import
}
```

## Detection Tools

### Tool 1: madge (Recommended)
```bash
# Install
npm install --save-dev madge

# Check for circular dependencies
npx madge --circular src/

# Output
Processed 245 files (2.1s)
✖ Found 1 circular dependency!

1) services/userService.ts > services/orderService.ts > services/userService.ts

# Visualize
npx madge --circular --image graph.svg src/
```

### Tool 2: dpdm
```bash
# Install
npm install --save-dev dpdm

# Check specific file
npx dpdm src/services/userService.ts

# Check entire project
npx dpdm --circular src/**/*.ts
```

### Tool 3: ESLint Plugin
```bash
# Install
npm install --save-dev eslint-plugin-import

# .eslintrc.js
module.exports = {
  plugins: ['import'],
  rules: {
    'import/no-cycle': ['error', { maxDepth: Infinity }],
  },
};
```

## CI Integration

### GitHub Actions
```yaml
# .github/workflows/check-dependencies.yml
name: Check Dependencies

on: [pull_request]

jobs:
  check-circular:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npx madge --circular src/
      - name: Fail if circular dependencies found
        run: |
          if npx madge --circular src/ | grep -q "circular"; then
            echo "❌ Circular dependencies found!"
            exit 1
          fi
```

## Common Patterns & Fixes

| Pattern | Problem | Solution |
|---------|---------|----------|
| Service calls service | A.ts → B.ts → A.ts | Extract interface to kernel, use DI |
| Domain imports domain | User → Order → User | Use IDs instead of full objects |
| Shared utilities | A → util → B → util → A | Move util to kernel |
| Type dependencies | Type A uses Type B uses Type A | Extract shared types to kernel |

## When to Read Full Pillar?
- ❓ Need complete Clean Architecture theory → Read Pillar I
- ❓ Need dependency injection patterns → Read external DI docs
- ❓ Need testing strategies for dependencies → Read Pillar K

## Related
- **Rule**: `clean-architecture.md` (layer structure and boundaries)
- **Pillar I**: Firewalls (import prevention)
- **Tool**: madge (https://github.com/pahen/madge)
- **Tool**: dpdm (https://github.com/acrazing/dpdm)
