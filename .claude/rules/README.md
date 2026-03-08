# Rules System - Quick Reference + Deep Dive

> **Rules are lightweight, path-triggered guides that link to comprehensive Pillars.**
>
> Rules = Quick Check (30 seconds) + Core Pattern (copy-paste ready) + Link to Pillar (deep dive)

---

## 📚 Navigation

**Start here based on your needs:**

| Need | Go To | Description |
|------|-------|-------------|
| 🔍 Find a specific Rule | **[INDEX.md](./INDEX.md)** | Complete catalog of all 40 Rules, organized by category and Pillar |
| ⚡ Quick reference during coding | **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** | Top 20 most-used Rules with Quick Checks |
| 📖 Learn the system | **This file (README.md)** | Understand Rules vs Pillars, index pattern, and how to use them |
| 🎯 Find Rules by scenario | **[INDEX.md § Find Rules by Scenario](./INDEX.md#find-rules-by-scenario)** | "I'm writing React..." → Which Rules? |
| 🏗️ Create a new Rule | **[templates/RULE_TEMPLATE.md](./templates/RULE_TEMPLATE.md)** | Standard template for new Rules |
| 🔬 Deep dive into concepts | **[../.prot/README.md](../.prot-template/README.md)** | 18 Pillars with complete theory |

---

## What Are Rules?

**Rules** are the AI Dev Framework's context-aware development guides:

- **Path-triggered**: Auto-load when you work on matching files (e.g., `**/headless/*.ts`)
- **Lightweight**: 20-70 lines, designed for quick scanning (30-second Quick Check)
- **Actionable**: Copy-paste ready code patterns
- **Linked**: Point to comprehensive Pillars for deep understanding

## Rules vs Pillars: Two Levels of Detail

The framework uses a **two-tier documentation system**:

```
┌─────────────────────────────────────────┐
│  Rules (40+ files, 20-70 lines each)   │  ← You are here
│  • Quick Check (30 seconds)             │  ← Fast validation
│  • Core Pattern (copy-paste ready)      │  ← Practical code
│  • Link to Pillar                       │  ← Deep dive when needed
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Pillars (18 files, 200-300 lines each) │  ← ../prot/pillars/
│  • Complete theory and examples         │  ← Comprehensive guide
│  • Anti-patterns and edge cases         │  ← What NOT to do
│  • Advanced patterns                    │  ← Deep understanding
└─────────────────────────────────────────┘
```

### When to Use What?

| Scenario | Use | Why |
|----------|-----|-----|
| Writing new code | **Rule** | Fast, actionable, focused |
| Quick validation | **Rule** (Quick Check) | 30-second checklist |
| Need copy-paste template | **Rule** (Core Pattern) | Ready-to-use code |
| Deep understanding needed | **Pillar** | Complete theory + examples |
| Debugging complex issue | **Pillar** | Anti-patterns, edge cases |
| Learning new concept | **Pillar** first, then **Rule** | Theory → Practice |
| Code review | **Rule** (Quick Check) | Fast validation |

## Index Pattern Design

**Rules follow the "index pattern"** (established in Issue #9, Phase 1):

### Standard Rule Structure

```markdown
---
paths: "**/*Pattern.ts"
---
# Rule Name

> 📖 **Complete Guide**: `.prot/pillars/<quadrant>/<pillar>/<name>.md`
> Brief one-line description

## Quick Check (30 seconds)
- [ ] Check 1 (most important pattern)
- [ ] Check 2 (common mistake to avoid)
- [ ] Check 3 (safety requirement)
- [ ] ...
- [ ] Check 7 (typically 5-8 items)

## Core Pattern
```typescript
// Concise, copy-paste ready code example
// Shows the "happy path" implementation
```

## When to Read Full Pillar?
- ❓ Scenario 1 requiring deep knowledge → Read Pillar X
- ❓ Scenario 2 with edge cases → Read Pillar Y
- ❓ Scenario 3 for advanced usage → Read Pillar Z

## Related
- **Pillar X**: Link (primary reference)
- **Pillar Y**: Link (related concept)
- **Rule Y**: Related rule
```

### Key Metrics for Rules

- **Length**: 20-70 lines (target: 30-50 lines)
- **Quick Check**: 5-8 items, scannable in 30 seconds
- **Core Pattern**: 10-30 lines of copy-paste ready code
- **Link to Pillar**: Always present at top
- **"When to Read Full Pillar?"**: Always present (helps users decide)

## How Rules Work

### 1. Path Triggers

Rules activate based on file paths you're working on:

```yaml
---
paths: "**/headless/*.ts"
---
```

When you edit `src/features/user/headless/useUserLogic.ts`, the `headless.md` rule auto-loads.

### 2. Quick Check (30 seconds)

Every Rule starts with a **Quick Check** - a scannable checklist:

```markdown
## Quick Check (30 seconds)
- [ ] Returns `{ state, ...actions }` pattern, never JSX
- [ ] State uses FSM union types (`'idle' | 'loading' | 'success' | 'error'`)
- [ ] No DOM manipulation or `window`/`document` access
- [ ] Calls adapters for I/O (not direct `fetch`)
- [ ] Uses `useReducer` for complex state (not multiple `useState`)
- [ ] All actions wrapped in `useCallback`
- [ ] Can be tested without React Testing Library
```

**Purpose**: Catch common mistakes in 30 seconds, before writing code.

### 3. Core Pattern (Copy-Paste Ready)

Every Rule includes a **Core Pattern** - working code you can copy:

```typescript
// Standard headless hook - copy directly
type State = { status: 'idle' | 'loading' | 'success' | 'error'; data?: User };

function useUserLogic(userId: UserId) {
  const [state, setState] = useState<State>({ status: 'idle' });

  const load = useCallback(async () => {
    setState({ status: 'loading' });
    try {
      const data = await userApi.fetchUser(userId);
      setState({ status: 'success', data });
    } catch {
      setState({ status: 'error' });
    }
  }, [userId]);

  return { state, load };  // Data + actions, no JSX
}
```

**Purpose**: Get started immediately with proven patterns.

### 4. Link to Pillar (Deep Dive)

Every Rule links to its **authoritative Pillar**:

```markdown
> 📖 **Complete Guide**: `.prot/pillars/q3-structure-boundaries/pillar-l/headless.md`
```

**Purpose**: When Quick Check + Core Pattern aren't enough, dive deep.

### 5. "When to Read Full Pillar?" (Decision Guide)

Every Rule helps you decide when to read the full Pillar:

```markdown
## When to Read Full Pillar?
- ❓ Need complete FSM state machine examples → Read Pillar L
- ❓ Unsure how to handle complex multi-step state → Read Pillar L
- ❓ Need anti-patterns and common mistakes → Read Pillar L
- ❓ Want comprehensive testing strategies → Read Pillar L
```

**Purpose**: Don't guess - the Rule tells you when you need more context.

## Pillars: The Single Source of Truth (SSOT)

**Pillars are the authoritative reference for coding standards.**

### 18 Pillars (AI_DEV_PROT v15)

For complete Pillar documentation, see [../.prot-template/README.md](../.prot-template/README.md#18-pillars-overview)

Organized into **4 quadrants**:

**Q1: Data Integrity** - A (Nominal Typing), B (Airlock), C (Mocking), D (FSM)

**Q2: Flow & Concurrency** - E (Orchestration), F (Concurrency), Q (Idempotency)

**Q3: Structure & Boundaries** - G (Traceability), H (Policy), I (Firewalls), J (Locality), K (Testing), L (Headless)

**Q4: Resilience & Observability** - M (Saga), N (Context), O (Async), P (Circuit Breaker), R (Observability)

### Pillar Characteristics

- **Comprehensive**: 200-300 lines, complete theory
- **Educational**: Explains "why" and "when", not just "how"
- **Anti-patterns**: Shows what NOT to do
- **Edge cases**: Handles advanced scenarios
- **Checklists**: Complete validation lists for code review

**Location**: `framework/.prot-template/pillars/`

## Rules Categories (40+ Rules)

### Core Rules (7)
Workflow, naming, debugging, documentation, memory management

**Key Rules**: `workflow.md`, `naming.md`, `debugging.md`

### Architecture Rules (7)
Clean architecture, layers, boundaries, headless, services

**Key Rules**: `headless.md`, `service-layer.md`, `adapters.md`

### Frontend Rules (6)
React, Zustand, design systems, views, CSS

**Key Rules**: `design-system.md`, `zustand-hooks.md`, `views.md`

### Backend Rules (5)
Saga, Lambda, APIs, queries, transactions

**Key Rules**: `saga.md`, `lambda-typescript-esm.md`, `query-transactions.md`

### Infrastructure Rules (10)
CDK, Tauri, deployment, secrets, logging, time, URLs

**Key Rules**: `cdk-deploy.md`, `tauri-stack.md`, `secrets.md`

### Development Rules (2)
Testing, file creation, infinite loop prevention

**Key Rules**: `infinite-loop-prevention.md`, `file-creation.md`

### Language Rules (3)
TypeScript strict mode, nominal types, ESM

**Key Rules**: `typescript-strict.md`, `typescript-nominal-types.md`

## Finding Rules

### 1. By Index (Most Common)

**Use the index files as your primary navigation:**

**[INDEX.md](./INDEX.md)** - Complete Catalog
- All 40 Rules organized by 7 categories
- Rules by Pillar cross-reference table
- Find Rules by Scenario (5 common development scenarios)
- Statistics and metadata

**[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Daily Use
- Top 20 most-used Rules
- Quick Checks for fast validation
- Common violations → Quick fixes table
- File type → Auto-triggered Rules visual cheat sheet

### 2. By File Path (Auto-Triggered)

Rules auto-load based on file paths you're working on:

| File Path Example | Auto-Loads Rule |
|-------------------|-----------------|
| `src/features/user/headless/useUserLogic.ts` | [headless.md](./architecture/headless.md) |
| `src/services/orderService.ts` | [service-layer.md](./architecture/service-layer.md) |
| `src/backend/orderSaga.ts` | [saga.md](./backend/saga.md) |
| `src/stores/userStore.ts` | [stores.md](./frontend/stores.md) |
| `infra/lib/api-stack.ts` | [cdk-deploy.md](./infrastructure/cdk-deploy.md) |

**88% of Rules are path-triggered** - they appear automatically when you need them.

### 3. By Scenario (Contextual)

**See [INDEX.md § Find Rules by Scenario](./INDEX.md#find-rules-by-scenario)** for complete list:

- **"I'm writing a React component"** → [design-system.md](./frontend/design-system.md), [headless.md](./architecture/headless.md), [zustand-hooks.md](./frontend/zustand-hooks.md), [views.md](./frontend/views.md)
- **"I'm writing a backend service"** → [service-layer.md](./architecture/service-layer.md), [adapters.md](./architecture/adapters.md), [saga.md](./backend/saga.md)
- **"I'm deploying to AWS"** → [cdk-deploy.md](./infrastructure/cdk-deploy.md), [secrets.md](./infrastructure/secrets.md), [aws-services.md](./infrastructure/aws-services.md)
- **"I'm writing tests"** → [lambda-local-first.md](./backend/lambda-local-first.md), [cdk-watch-testing.md](./infrastructure/cdk-watch-testing.md)
- **"I encountered a bug"** → [debugging.md](./core/debugging.md), [infinite-loop-prevention.md](./development/infinite-loop-prevention.md)

### 4. By Pillar (Theoretical)

**See [INDEX.md § Rules by Pillar](./INDEX.md#rules-by-pillar)** for cross-reference table:

- **Pillar A (Nominal Typing)** → [typescript-nominal-types.md](./languages/typescript-nominal-types.md), [identity.md](./architecture/identity.md)
- **Pillar L (Headless)** → [headless.md](./architecture/headless.md), [views.md](./frontend/views.md), [design-system.md](./frontend/design-system.md), [stores.md](./frontend/stores.md)
- **Pillar M (Saga)** → [saga.md](./backend/saga.md)
- **Pillar R (Observability)** → [debugging.md](./core/debugging.md), [diagnostic-export-logging.md](./infrastructure/diagnostic-export-logging.md)

**70% of Rules relate to specific Pillars** - use this to understand the theoretical foundation.

## Why Index Pattern?

### Before Refactor (Problem)
- Rules: 150+ lines each, full documentation
- Pillars: 200-300 lines, comprehensive theory
- **Result**: 40% content duplication (~5,000 lines)

### After Refactor (Solution)
- Rules: 20-70 lines, index pattern
- Pillars: 200-300 lines (unchanged, SSOT)
- **Result**: ↓64% reduction in Rules, zero duplication

### Benefits

1. **Single Source of Truth**: Pillars are authoritative, Rules point to them
2. **No Duplication**: Each concept documented once, referenced many times
3. **Fast Scanning**: 30-second Quick Check catches 80% of issues
4. **Progressive Disclosure**: Start with Quick Check → Core Pattern → Full Pillar
5. **AI-Friendly**: Clear, actionable, context-aware

## For AI Assistants

### When to Use Rules

**Always check relevant Rules before:**
- Writing new code (Quick Check)
- Creating files (path triggers)
- Code review (validation)
- Bug fixing (debugging Rules)

### When to Read Pillars

**Read Pillars when:**
- Rule's "When to Read Full Pillar?" section applies
- Implementing complex patterns (Saga, FSM, etc.)
- Need anti-patterns or edge cases
- Learning new concepts
- Code review reveals violations

### Rule Usage Pattern

1. **Path trigger**: Rule auto-loads
2. **Quick Check**: Scan checklist (30 seconds)
3. **Core Pattern**: Copy-paste starting point
4. **Validate**: Did I pass Quick Check?
5. **If stuck**: Read linked Pillar

## Statistics

**See [INDEX.md § Statistics](./INDEX.md#statistics) for complete breakdown.**

Summary:
- **Total Rules**: 40
- **Average Length**: 30-50 lines (target)
- **Path-Triggered**: 35 (88%)
- **Related to Pillars**: 28 (70%)
- **Total Line Count**: ~1,620 lines (after refactor)
- **Reduction vs Pre-Refactor**: ↓64%

**By Category**:
- Core: 7 (18%)
- Architecture: 7 (18%)
- Frontend: 6 (15%)
- Backend: 5 (13%)
- Infrastructure: 10 (25%)
- Development: 2 (5%)
- Languages: 3 (8%)

## See Also

### Rules System
- **[INDEX.md](./INDEX.md)** - Complete catalog of all 40 Rules
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Top 20 most-used Rules
- **[templates/RULE_TEMPLATE.md](./templates/RULE_TEMPLATE.md)** - Create new Rules

### Pillars System
- **[../.prot-template/README.md](../.prot-template/README.md)** - 18 Pillars overview
- **[../.prot-template/CHEATSHEET.md](../.prot-template/CHEATSHEET.md)** - Pillars quick lookup

### Framework
- **[../../CLAUDE.md](../../CLAUDE.md)** - AI Dev Framework overview
- **[../../README.md](../../README.md)** - Project documentation

## Version History

- **v1.0** (2026-02-05): Initial index pattern implementation
  - Refactored `headless.md` (70 → 50 lines)
  - Refactored `saga.md` (83 → 67 lines)
  - Established index pattern standard

---

**For Developers**: Rules are your quick reference. Pillars are your deep understanding. Use both.

**For AI**: Rules guide real-time coding. Pillars guide complex decisions. Read Rules first, Pillars when needed.
