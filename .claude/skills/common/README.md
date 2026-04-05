# Common Directory - Shared Utilities

This directory contains shared utilities and libraries used by multiple skills. It does NOT contain a `SKILL.md` file because it is not an invocable skill.

## Contents

### Core Modules

- **change-analyzer.ts** - Analyzes code changes and impacts
- **decision-engine.ts** - Decision-making logic engine for automated workflows
- **decision-rules.yaml** - Configuration rules for decision engine
- **scoring.ts** - Scoring algorithms for evaluations (eval-plan, review, etc.)

### Templates

- **templates/** - Shared templates used across skills

## Purpose

The common directory serves as a library of reusable components that multiple skills depend on. This avoids code duplication and ensures consistency across skills.

## Usage

Skills import these modules as needed:

```typescript
import { analyzeChanges } from '../common/change-analyzer';
import { scoreImplementation } from '../common/scoring';
```

## Maintenance

When updating common utilities:
1. Test with all dependent skills
2. Maintain backward compatibility
3. Document breaking changes in skill changelogs
4. Version common modules if needed

## Not a Skill

**Important:** This directory does NOT contain a `SKILL.md` file because it is not meant to be invoked directly by users. It provides shared functionality to other skills.

## Related Skills

Skills that use common utilities:
- eval-plan (uses scoring.ts)
- review (uses scoring.ts, change-analyzer.ts)
- auto-solve-issue (uses decision-engine.ts)

---

**Type:** Shared Library Directory
**Not Invocable:** No SKILL.md by design
