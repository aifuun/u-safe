---
category: "languages"
title: "Typescript Esm"
description: "ESM module patterns"
tags: [typescript]
profiles: [tauri, nextjs-aws, minimal]
paths: ['**/*.{ts,tsx}']
version: "1.0.0"
last_updated: "2026-03-27"
---

---
paths: "**/*.ts"
---

# TypeScript ESM Module Rule

> Use modern ES Modules with proper import/export syntax.

## Quick Check
- [ ] `package.json`: `"type": "module"`
- [ ] `tsconfig.json`: `"module": "ESNext"` or `"NodeNext"`
- [ ] File extensions in imports (`.js` not `.ts`)
- [ ] No `require()` or `module.exports`

## Core Pattern: ESM Imports

```typescript
// ✅ Correct - Named imports with .js extension
import { User, getUser } from './user.js';  // .js not .ts!

// ✅ Correct - Default import
import express from 'express';

// ✅ Correct - Type-only imports
import type { UserId } from './types.js';

// ✅ Correct - Namespace import
import * as utils from './utils.js';

// ❌ Wrong - CommonJS
const { User } = require('./user');  // Don't use require()
module.exports = { User };            // Don't use module.exports
```

## File Extension Rule

**Critical**: Import with `.js` extension, not `.ts`

```typescript
// Source file: user.ts
export function getUser() { ... }

// Other file: main.ts
import { getUser } from './user.js';  // ✅ Correct - .js extension
import { getUser } from './user.ts';  // ❌ Wrong - TypeScript won't work
import { getUser } from './user';     // ❌ Wrong - Node 16+ requires extension
```

**Why `.js`?** TypeScript compiles `.ts` → `.js`, so runtime needs `.js` extension.

## Configuration

### package.json
```json
{
  "type": "module",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts"
}
```

### tsconfig.json
```json
{
  "compilerOptions": {
    "module": "ESNext",
    "moduleResolution": "bundler",
    "target": "ES2022"
  }
}
```

## Common Patterns

### Top-level await
```typescript
// ✅ ESM allows top-level await
const config = await loadConfig();
export default config;
```

### Dynamic imports
```typescript
// ✅ Lazy loading
if (condition) {
  const { feature } = await import('./feature.js');
  feature();
}
```

## Related
- **TypeScript ESM Docs**: https://www.typescriptlang.org/docs/handbook/esm-node.html
- **Node.js ESM Guide**: https://nodejs.org/api/esm.html
- **Rule**: `typescript-strict.md` (strict mode)
