---
category: "architecture"
title: "Clean Architecture"
description: "Hexagonal architecture"
tags: [typescript, react]
profiles: [tauri, nextjs-aws]
pillar_refs: [L]
paths: ['**/*.{ts,tsx}']
version: "1.0.0"
last_updated: "2026-03-27"
---

---
paths:
  - "src/**/*.ts"
  - "app/src/**/*.ts"
---

# Clean Architecture Rule

> 📖 **Complete Guides**: Pillar I (Firewalls), Pillar J (Locality)

## Quick Check
- [ ] Dependencies flow inward only: components → modules → domains → kernel
- [ ] No deep imports (use index.ts and path aliases)
- [ ] No circular dependencies (verify with `madge`)
- [ ] Each layer imports only from inner layers
- [ ] No domain-to-domain or module-to-module imports

## 4-Layer Architecture

### Layer 0: Kernel
**Role**: Core types and interfaces (no dependencies)
**Allowed imports**: None
**Contains**: Branded types, base interfaces, constants

```typescript
// kernel/types/ids.ts
export type UserId = string & { readonly __brand: unique symbol };
export type OrderId = string & { readonly __brand: unique symbol };

// kernel/interfaces/repository.ts
export interface IRepository<T, ID> {
  findById(id: ID): Promise<T | null>;
  save(entity: T): Promise<void>;
}
```

### Layer 1: Domains
**Role**: Business logic and entities (pure functions, no I/O)
**Allowed imports**: Kernel only
**Contains**: Domain models, business rules, value objects

```typescript
// domains/user/User.ts
import type { UserId } from '@/kernel/types/ids';

export interface User {
  readonly id: UserId;
  readonly name: string;
  readonly email: string;
}

// domains/user/rules.ts
export function canDeleteUser(user: User): boolean {
  return user.role !== 'admin';  // Pure business logic
}
```

### Layer 2: Modules
**Role**: Use cases, services, adapters (I/O operations)
**Allowed imports**: Kernel, Domains
**Contains**: Services, repositories, adapters, headless hooks

```typescript
// modules/user/userService.ts
import type { UserId } from '@/kernel/types/ids';
import type { User } from '@/domains/user/User';
import { userRepository } from './userRepository';

export async function getUser(id: UserId): Promise<User> {
  return userRepository.findById(id);
}

// modules/user/userRepository.ts
import type { IRepository } from '@/kernel/interfaces/repository';
import type { UserId } from '@/kernel/types/ids';
import type { User } from '@/domains/user/User';

export const userRepository: IRepository<User, UserId> = {
  async findById(id) {
    const response = await api.get(`/users/${id}`);
    return response.data;
  },
  async save(user) {
    await api.post(`/users/${user.id}`, user);
  },
};
```

### Layer 3: Components
**Role**: UI and presentation
**Allowed imports**: Kernel, Domains, Modules
**Contains**: React components, views, pages

```typescript
// components/UserProfile.tsx
import type { UserId } from '@/kernel/types/ids';
import { useUserLogic } from '@/modules/user/hooks/useUserLogic';

export function UserProfile({ userId }: { userId: UserId }) {
  const { state, loadUser } = useUserLogic(userId);

  if (state.status === 'loading') return <div>Loading...</div>;
  if (state.status === 'error') return <div>Error</div>;

  return <div>{state.data.name}</div>;
}
```

## Import Firewall Rules

### Rule 1: No Deep Imports
```typescript
// ❌ WRONG - Deep import bypasses public API
import { User } from '../../domains/user/entities/User';
import { calculateTax } from '../../../domains/order/utils/tax';

// ✅ CORRECT - Use index.ts
import { User } from '@/domains/user';
import { calculateTax } from '@/domains/order';
```

### Rule 2: No Sibling Imports Across Modules
```typescript
// ❌ WRONG - Module reaching into another module
// In modules/order/orderService.ts
import { getUserName } from '../user/utils/name';  // Crossing module boundary!

// ✅ CORRECT - Use public API through index.ts
import { userService } from '@/modules/user';
const name = await userService.getUserName(userId);
```

### Rule 3: Layer Boundary Enforcement
```typescript
// ❌ WRONG - Domain importing from Module (outer layer!)
// In domains/user/User.ts
import { userService } from '@/modules/user/userService';  // VIOLATION!

// ✅ CORRECT - Domains are pure, no I/O
// In domains/user/User.ts
export interface User {
  id: UserId;
  name: string;
}
```

### Rule 4: Index.ts Per Directory
Every directory should have `index.ts` exposing only public API:

```typescript
// kernel/index.ts
export * from './types/ids';
export * from './interfaces/repository';

// domains/user/index.ts
export * from './User';
export * from './UserRole';
export * from './rules';

// modules/user/index.ts
export { userService } from './userService';
export { useUserLogic } from './hooks/useUserLogic';
// Internal files NOT exported: userRepository, utils
```

## Dependency Flow Diagram

```
┌─────────────────────────────────┐
│  Components (Layer 3)           │  ← UI, Views, Pages
│        ↓ imports                │
├─────────────────────────────────┤
│  Modules (Layer 2)              │  ← Services, Adapters, Hooks
│        ↓ imports                │
├─────────────────────────────────┤
│  Domains (Layer 1)              │  ← Business Logic (pure)
│        ↓ imports                │
├─────────────────────────────────┤
│  Kernel (Layer 0)               │  ← Types, Interfaces
│        ↓ NO imports             │
└─────────────────────────────────┘

✅ Inward only
❌ Never outward or sideways
```

## Path Aliases Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/kernel/*": ["src/kernel/*"],
      "@/domains/*": ["src/domains/*"],
      "@/modules/*": ["src/modules/*"],
      "@/components/*": ["src/components/*"]
    }
  }
}
```

## Verification

### Manual Check
```bash
# List all imports in a file
grep -E "^import .* from" src/domains/user/User.ts

# Should only see @/kernel imports for domains
```

### Automated Check with madge
```bash
# Install madge
npm install --save-dev madge

# Check for circular dependencies
npx madge --circular src/

# Visualize dependency graph
npx madge --image graph.svg src/
```

### Audit Script
```bash
# Use provided audit script
npx tsx scripts/audit/check-layer-boundaries.ts
```

## Common Violations & Fixes

| Violation | Example | Fix |
|-----------|---------|-----|
| Deep import | `import x from '../../../kernel/types'` | Use `@/kernel/types` alias |
| Domain imports Module | Domain file imports service | Remove import, use dependency injection |
| Circular dependency | A → B → A | Extract shared code to lower layer (kernel) |
| No index.ts | Direct file imports | Create index.ts with public exports |
| Module-to-module import | `modules/order` imports `modules/user/utils` | Use public API through index.ts |

## When to Read Full Pillars?
- ❓ Need to understand Firewall enforcement in depth → Read Pillar I
- ❓ Need to understand state locality principles → Read Pillar J
- ❓ Need complete Clean Architecture theory → Read external docs

## Related
- **Pillar I**: `.claude/pillars/pillars/q3-structure-boundaries/pillar-i/firewalls.md` (import prevention)
- **Pillar J**: `.claude/pillars/pillars/q3-structure-boundaries/pillar-j/locality.md` (state management)
- **Rule**: `dependency-rule.md` (circular dependency detection)
- **Rule**: `service-layer.md` (service orchestration patterns)
- **Rule**: `adapters.md` (I/O boundary patterns)
