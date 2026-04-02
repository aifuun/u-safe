---
category: "languages"
title: "Typescript Strict"
description: "TypeScript strict mode"
tags: [typescript]
profiles: [tauri, nextjs-aws, minimal]
paths: ['**/*.{ts,tsx}']
version: "1.0.0"
last_updated: "2026-03-27"
---

---
paths: "**/*.ts"
---

# TypeScript Strict Mode Rule

> Enforce strict TypeScript compiler settings for maximum type safety.

## Quick Check
- [ ] `tsconfig.json` has `"strict": true`
- [ ] `noUncheckedIndexedAccess: true` (array safety)
- [ ] All type errors resolved (no `@ts-ignore`)
- [ ] No `any` types (except temporary migration)

## Core Pattern: Strict tsconfig.json

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler"
  }
}
```

## Common Errors & Fixes

### Error 1: Object is possibly 'undefined'
```typescript
// ❌ Problem
const user = users.find(u => u.id === id);
console.log(user.name);  // Error: user might be undefined

// ✅ Fix 1: Guard clause
const user = users.find(u => u.id === id);
if (!user) throw new Error('User not found');
console.log(user.name);  // OK

// ✅ Fix 2: Optional chaining
console.log(user?.name ?? 'Unknown');
```

### Error 2: Element implicitly has 'any' type
```typescript
// ❌ Problem (with noUncheckedIndexedAccess)
const value = array[0];
console.log(value.toUpperCase());  // Error: value might be undefined

// ✅ Fix
const value = array[0];
if (value === undefined) throw new Error('Empty array');
console.log(value.toUpperCase());  // OK
```

### Error 3: Argument of type 'string | undefined'
```typescript
// ❌ Problem
function greet(name: string) { console.log(`Hello ${name}`); }
greet(user.name);  // Error if user.name is optional

// ✅ Fix: Nullish coalescing
greet(user.name ?? 'Guest');
```

### Error 4: Property has no initializer
```typescript
// ❌ Problem
class User {
  name: string;  // Error: not initialized
}

// ✅ Fix 1: Initialize in constructor
class User {
  name: string;
  constructor(name: string) {
    this.name = name;
  }
}

// ✅ Fix 2: Definite assignment
class User {
  name!: string;  // Trust me, I'll initialize this
}
```

## Migration Strategy

If adding strict mode to existing project:

```json
{
  "compilerOptions": {
    "strict": true,
    // Allow gradual migration
    "noImplicitAny": false,  // Temporarily allow 'any'
  }
}
```

Fix errors incrementally, then enable all flags.

## Related
- **TypeScript Handbook**: https://www.typescriptlang.org/tsconfig#strict
- **Rule**: `typescript-nominal-types.md` (branded types)
- **Rule**: `typescript-esm.md` (module system)
