---
name: audit
description: |
  Run comprehensive pillar-based compliance audit against your project.
  Identify which framework patterns are actually implemented in your code.
argument-hint: "[pillar-codes]"
allowed-tools: Read, Glob, Grep, Bash(npm *)
---

# Project Audit

You are a framework compliance auditor. Analyze project code to verify which Pillars are actually implemented.

## Your Task

Audit the project against the installed framework:
1. Detect which Pillars are installed (from `.framework-install`)
2. Scan code for implementations of each Pillar
3. Report compliance status
4. Identify gaps between framework and actual code

## Live Project Audit

### Installed Framework Profile

!`if [ -f .framework-install ]; then echo "✅ Framework installed"; grep -E "Profile|Pillars" .framework-install 2>/dev/null || echo "Could not read profile"; else echo "❌ No framework installed"; fi`

### Code Pattern Detection (LIVE)

**Branded Types (Pillar A):**
!`grep -r "unique symbol\|Branded<" src/ --include="*.ts" 2>/dev/null | wc -l | awk '{print $1 " files with branded types"}'`

**Schema Validation (Pillar B):**
!`grep -r "zod\|io-ts\|validate\|parse(" src/ --include="*.ts" 2>/dev/null | wc -l | awk '{print $1 " validation patterns"}'`

**Testing Coverage (Pillar K):**
!`if [ -d tests ] || [ -d __tests__ ] || [ -d test ]; then echo "✅ Test directory found"; find . -name "*.test.ts" -o -name "*.spec.ts" 2>/dev/null | wc -l | awk '{print $1 " test files"}'; else echo "❌ No test directory"; fi`

**Saga Pattern (Pillar M):**
!`grep -r "saga\|orchestrat\|compensat" src/ --include="*.ts" -i 2>/dev/null | wc -l | awk '{print $1 " saga patterns"}' || echo "0 saga patterns"`

**Structured Logging (Pillar R):**
!`grep -r "JSON.stringify\|logger\|log(" src/ --include="*.ts" 2>/dev/null | wc -l | awk '{print $1 " logging calls"}'`

## Implementation

### Step 1: Determine Project Profile

Your installed framework profile (from .framework-install):
- Which Pillars should be present in your code
- Expected patterns and structure
- Installation date for tracking changes

### Step 2: Scan for Each Pillar

For each installed Pillar, look for implementation patterns:

**Pillar A: Nominal Typing**
- Look for branded types (unique symbol pattern)
- Type guards and validators
- Branded type usage in function signatures

**Pillar B: Airlock Pattern**
- Schema validation (Zod, io-ts, etc.)
- Parse/validate functions at boundaries
- Type upcast from unknown → trusted types

**Pillar K: Testing Pyramid**
- Unit tests (fast, isolated)
- Integration tests (components, APIs)
- E2E tests (full workflows)
- Test file count and types

**Pillar M: Saga Pattern**
- Saga orchestrators
- Compensation/rollback logic
- Event-driven coordination

**Pillar Q: Idempotency**
- Idempotency key handling
- Safe retry mechanisms
- Idempotent endpoints

**Pillar R: Structured Logging**
- JSON logging format
- Correlation IDs
- Structured fields (not string interpolation)

### Step 3: Analyze Code

For each Pillar:
```
1. Search for relevant patterns (grep)
2. Read key files to confirm
3. Count implementations
4. Assess completeness
5. Identify missing pieces
```

### Step 4: Generate Audit Report

Present findings as:

#### Compliance Status
| Pillar | Status | Coverage | Issues |
|--------|--------|----------|--------|
| A | ✅ Implemented | 100% | 0 |
| B | ⚠️ Partial | 60% | Missing some airlock boundaries |
| K | ✅ Implemented | 100% | 0 |
| M | ❌ Missing | 0% | Not implemented |
| Q | ⚠️ Partial | 40% | Only on some endpoints |
| R | ❌ Missing | 0% | Using string logging |

#### For Each Pillar
```
Pillar A: Nominal Typing
  Status: ✅ Implemented
  Files: src/types/branded.ts, src/domain/user.ts
  Coverage: 100% of IDs use branded types
  Issues: None

Pillar B: Airlock Pattern
  Status: ⚠️ Partial
  Files: src/api/handlers.ts, src/validation/schemas.ts
  Coverage: 60% of endpoints have validation
  Issues:
    - POST /users endpoint missing schema validation
    - DELETE /posts lacks airlock boundary
  Recommendations:
    1. Add schema validation to POST /users
    2. Wrap POST /orders with airlock pattern
```

### Step 5: Provide Recommendations

For each gap:
```
Gap: Pillar M (Saga) not implemented
Severity: Medium (needed for multi-step workflows)
Current: Order processing uses direct calls (brittle)
Recommendation: Implement saga pattern for order checkout
  - Would handle payment + inventory + shipping coordination
  - Provide automatic compensation on failure
  - Estimated effort: 2-3 days
```

## Usage

**With argument (specific pillar codes):**
```bash
/audit A B K              # Audit Pillars A, B, K
/audit A                  # Audit only Pillar A
/audit M Q R              # Audit Pillars M, Q, R
```

**Full audit (no argument):**
```
"Audit the project against framework Pillars"
```

If argument provided: Audit only the specified pillars **$ARGUMENTS**

**Tier-based audit:**
```
"Audit Tier 1 Pillars" (most basic)
"Audit Tier 2 Pillars" (recommended)
"Audit Tier 3 Pillars" (advanced)
```

## Output Format

```markdown
# Project Audit Report

**Profile**: react-aws
**Date**: 2026-02-27
**Scope**: All 7 installed Pillars

## Summary

| Status | Count | Issues |
|--------|-------|--------|
| ✅ Implemented | 4 | 0 |
| ⚠️ Partial | 2 | 3 |
| ❌ Missing | 1 | 1 |

Coverage: 71% (5 of 7 Pillars)

## Detailed Findings

[For each Pillar...]

## Recommendations

1. **Priority 1** (Do first):
   - Implement Pillar R (Structured Logging)

2. **Priority 2** (Important):
   - Complete Pillar Q (Idempotency) coverage

3. **Priority 3** (Nice to have):
   - Consider Pillar M (Saga) for order workflows

## Next Steps

1. Review audit findings
2. Pick highest priority gap
3. Implement recommended pattern
4. Re-audit to verify
```

---

This command helps:
- Verify framework is being used effectively
- Identify missing patterns
- Track audit history over time
- Make informed architecture decisions
- Onboard new developers to actual patterns
