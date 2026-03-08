---
name: check-naming
description: |
  Check naming conventions and product name usage in codebase.
  Ensures single source of truth for configuration (product.config.json).
argument-hint: "[--quick]"
allowed-tools: Read, Glob, Grep, Bash(grep *)
---

# Naming Convention Checker

You are a naming architecture validator ensuring product configuration consistency.

## Your Task

Verify that product naming follows the single-source-of-truth pattern:
- **User-Visible**: `productName` (can change)
- **Code Structure**: Neutral names (never change)
- **Runtime Resources**: `technicalName` (rarely change)

## Implementation

### Step 1: Verify Configuration

Check for `product.config.json`:

```json
{
  "productName": "Recie",      // What users see
  "technicalName": "recie",    // Database names, buckets, etc.
  "version": "1.0.0",
  "...": "..."
}
```

Required fields:
- `productName` - User-visible product name
- `technicalName` - Technical identifier (lowercase, no spaces)

### Step 2: Check 1 - No Hardcoded Product Names

Search codebase for hardcoded product names:

```bash
# Look for patterns where product name appears directly
grep -r "productName" src/ --include="*.ts" --include="*.tsx"
grep -r "technicalName" src/ --include="*.ts" --include="*.tsx"

# These are OK only if they're reading from generated config
# Not OK if they're hardcoded strings
```

Violations to catch:
```typescript
// ❌ BAD: Hardcoded product name
const db = new Database('sqlite:recie.db');
const bucket = 's3://recie-documents/';
const prefix = 'recie:feature';

// ✅ GOOD: From generated config
import { DB_PATH, S3_BUCKET } from './generated/config';
const db = new Database(DB_PATH);
const bucket = `s3://${S3_BUCKET}/`;
```

### Step 3: Check 2 - Generated Config Files

Verify generated files exist and are up-to-date:

```
Required files:
- app/src/generated/config.ts      (app configuration)
- infra/lib/generated/config.ts    (infrastructure configuration)
```

```typescript
// Generated config should export:
export const DB_NAME = 'recie';
export const S3_BUCKET = 'recie-documents';
export const STORAGE_PREFIX = 'recie:';
export const TECHNICAL_NAME = 'recie';
```

Check:
- Files exist and are recent
- Generated from product.config.json
- Imported by code files

### Step 4: Check 3 - Code Uses Generated Config

Search for improper configuration usage:

```bash
# Should import from generated/config
grep -r "Database\.load\|new.*Stack\|S3_BUCKET" \
  --include="*.ts" --include="*.tsx" src/ infra/

# Look for hardcoded values instead of imports
grep -r "sqlite:.*\.db\|s3://.*documents\|technicalName" \
  --include="*.ts" --include="*.tsx" src/ infra/
```

Violations:
```typescript
// ❌ BAD: Hardcoded in code
class RecieStack extends cdk.Stack {
  constructor(...) { ... }
}

// ✅ GOOD: Neutral name
class MainStack extends cdk.Stack {
  constructor(...) { ... }
}

// ✅ GOOD: Read from config
import { DB_PATH } from './generated/config';
const db = new Database(DB_PATH);
```

### Step 5: Check 4 - Naming Conventions

Verify consistent neutral naming patterns:

**Allowed stack names**:
- MainStack
- AdminStack
- ProcessingStack
- MonitoringStack
- WebStack
- ApiStack

**Not allowed**:
- ProductNameStack
- RecieStack (specific to product)

## Output Format

### Success Case

```markdown
## Naming Convention Check ✅

**Config File**: product.config.json
**Product Name**: Recie
**Technical Name**: recie
**Time**: 0.5s

### Summary

| Check | Status | Issues |
|-------|--------|--------|
| No hardcoded names | ✅ Pass | 0 |
| Config file valid | ✅ Pass | 0 |
| Generated files | ✅ Pass | 0 |
| Usage compliance | ✅ Pass | 0 |

**Total**: 4/4 Pass

✅ All naming convention checks passed!
Codebase uses generated config consistently.
```

### Failure Case

```markdown
## Naming Convention Check ⚠️

**Config File**: product.config.json
**Product Name**: Recie
**Technical Name**: recie
**Time**: 0.5s

### Summary

| Check | Status | Issues |
|-------|--------|--------|
| No hardcoded names | ✅ Pass | 0 |
| Config file valid | ✅ Pass | 0 |
| Generated files | ⚠️ Warn | 1 |
| Usage compliance | ❌ Fail | 2 |

**Total**: 2/4 Pass, 1 Warning

### Warnings

Generated file is outdated: `app/src/generated/config.ts`
- Last modified: 2 days ago
- Config modified: 1 hour ago
- **Fix**: Run `npm run config:sync`

### Failures Detail

#### Usage Compliance (2 violations)

1. **app/src/00_kernel/storage/db.ts:15**
   ```typescript
   const db = await Database.load('sqlite:recie.db');
   ```
   - **Issue**: Hardcoded database name (product-specific)
   - **Fix**: Import from generated config
   ```typescript
   import { DB_PATH } from '../../generated/config';
   const db = await Database.load(DB_PATH);
   ```

2. **infra/lib/main-stack.ts:8**
   ```typescript
   export class RecieStack extends cdk.Stack {
   ```
   - **Issue**: Product name in class name (should be neutral)
   - **Fix**: Use neutral naming
   ```typescript
   export class MainStack extends cdk.Stack {
   ```

### Recommended Actions

1. Update `app/src/00_kernel/storage/db.ts` to import DB_PATH
2. Regenerate config files: `npm run config:sync`
3. Rename RecieStack to MainStack in infra
4. Re-run check: `check-naming`
```

## Quick Mode

```
check-naming --quick
```

Skips file modification timestamp checks, runs in ~0.3s.

## Fix Suggestions

Provide specific code examples for each violation:

```
File: app/src/api/handlers.ts:42

Current:
  const bucket = 's3://recie-images/';

Should be:
  import { S3_IMAGES_BUCKET } from '../generated/config';
  const bucket = `s3://${S3_IMAGES_BUCKET}/`;

Then regenerate config: npm run config:sync
```

---

This command ensures:
- Product name changes are centralized (product.config.json)
- Code doesn't need updates when product rebrand
- Database, bucket, and resource names stay in sync
- Clear separation between config and code
