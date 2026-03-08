---
name: review
description: |
  Conduct thorough code review with dynamic detection of project configuration.
  Scans enabled Pillars (from profile), architecture rules, and ADRs.
  Adapts checks to YOUR project (no hardcoded assumptions).
  Provides quality gates and detailed feedback.
  Records review status for finish-issue integration.
allowed-tools: Read, Glob, Grep, Bash(npm *), Write
---

# Code Reviewer

Review code quality, architecture decisions, and framework pattern compliance.

## Task

Analyze code changes for:
1. **Quality** - Type safety, error handling, testing
2. **Architecture** - Design patterns, separation of concerns
3. **Pillars** - Framework pattern implementation
4. **ADRs** - Architecture Decision Records compliance
5. **Security** - Potential vulnerabilities
6. **Performance** - Inefficiencies or bottlenecks

## Review Dimensions

### Quality Gates
```
✅ Types valid (TypeScript compiles)
✅ Tests passing
✅ Linting passes
✅ No obvious bugs
```

### Architecture
**Dynamically detect architecture rules** from project configuration:

```
Process:
1. Scan .claude/rules/architecture/ for enabled rules
2. Detect architecture style (Clean, Hexagonal, Layered, etc.)
3. Check code against detected architectural patterns
4. Only check rules that exist in this project

Common Architecture Checks (if rules exist):
✅ Module boundaries (if clean-architecture.md exists)
✅ Dependency direction (if dependency-rules.md exists)
✅ Layer boundaries (if layer-boundaries.md exists)
✅ Consistent naming (if naming-conventions.md exists)
✅ Error handling (if error-handling.md exists)

Adapts to Project:
- Different projects → different architecture rules
- No rules → skip architecture checks
- Reads from .claude/rules/architecture/*.md
```

### Pillar Compliance
**Dynamically detect enabled Pillars** from project installation:

```
Process:
1. Read .framework-install file to detect profile
   OR scan .prot/pillars/ to see which Pillars are installed
2. Only check Pillars enabled for this project
3. Different profiles → different Pillar checks

Profile-Based Checks:
┌─────────────────┬────────────────────────────────┐
│ Profile         │ Pillars Checked                │
├─────────────────┼────────────────────────────────┤
│ minimal         │ A, B, K (3 Pillars)            │
│ node-lambda     │ A, B, K, M, Q, R (6 Pillars)   │
│ react-aws       │ A, B, K, L, M, Q, R (7 Pillars)│
│ custom          │ Whatever is in .prot/pillars/  │
└─────────────────┴────────────────────────────────┘

Example Checks (based on enabled Pillars):
✅ Pillar A (Nominal Types) - if enabled
   Check: Branded types for IDs

✅ Pillar B (Airlock) - if enabled
   Check: Schema validation at boundaries

✅ Pillar K (Testing) - if enabled
   Check: Test pyramid structure

✅ Pillar M (Saga) - if enabled
   Check: Transaction compensation patterns

⚠️  Pillar L (Headless) - if NOT enabled
   Skip: Don't check headless patterns

Key Point:
- Only check Pillars YOUR project uses
- No assumptions about which Pillars are enabled
- Adapts to minimal/node-lambda/react-aws/custom profiles
```

### ADR Compliance
**Dynamically scan existing ADRs** in current project's `docs/adr/` and check code against documented decisions:

```
Process:
1. Scan docs/adr/ for ALL ADR files (*.md) in current project
2. Extract ADR number, title, and key requirements from each
3. Analyze code changes to identify which ADRs are relevant
4. Check compliance for each relevant ADR
5. Report violations with file:line references

How It Works:
- No hardcoded ADRs - adapts to ANY project
- Reads current project's ADRs dynamically
- Different projects = different ADR checks
- Scales automatically (works with 1 ADR or 100 ADRs)

Example ADR Checks (project-specific):
Note: These are examples from a React+AWS project.
Your project will have different ADRs.

✅ Example: ADR-009 (Zustand Vanilla Store Pattern)
   - Check: Using createStore() from zustand/vanilla (not create())
   - Check: Exporting vanilla store instance
   - Applicable to: React projects using Zustand

✅ Example: ADR-005 (Identity Model with Branded Types)
   - Check: Using branded types for all IDs
   - Check: UserId, TaskId have __brand property
   - Applicable to: TypeScript projects

✅ Example: ADR-003 (API Rate Limiting Strategy)
   - Check: Rate limiter middleware present
   - Applicable to: Backend API projects

Example Violation Report:
❌ src/stores/taskStore.ts:5
   Violation: ADR-009 (Zustand Vanilla Store)
   Issue: Using create() instead of createStore()
   Fix: import { createStore } from 'zustand/vanilla'
   Context: This ADR exists in YOUR project's docs/adr/

Key Point:
- Review scans YOUR project's ADRs (docs/adr/)
- Checks YOUR code against YOUR decisions
- No assumptions about which ADRs exist
```

**When no ADRs found**:
```
ℹ️  No ADRs found in docs/adr/
   Consider documenting architectural decisions with /adr create
```

### Security
```
✅ Input validation
✅ No hardcoded secrets
✅ SQL injection prevention
✅ CSRF protection
```

### Performance
```
✅ No N+1 queries
✅ Proper caching strategy
✅ Reasonable algorithm complexity
```

## Output

```markdown
# Code Review: [Feature/PR]

## Summary
- Files: 8 changed, 150 insertions, 50 deletions
- Quality Score: 85/100
- Ready to merge: ✅ Yes

## ✅ Strengths
1. Clear airlock pattern with schema validation
2. Comprehensive test coverage
3. Good error messages

## Framework Detection
Detected profile: react-aws (7 Pillars enabled)
Architecture rules: Clean Architecture + Layer Boundaries

## Pillar Compliance (profile: react-aws)
Checking 7 enabled Pillars (A, B, K, L, M, Q, R):

✅ Pillar A (Nominal Types): TaskId, UserId branded types used
✅ Pillar B (Airlock): zod validation at API boundary
✅ Pillar K (Testing): 88% coverage, pyramid structure
✅ Pillar L (Headless): UI logic separated from components
✅ Pillar M (Saga): Transaction patterns correctly implemented
✅ Pillar Q (Idempotency): Operations are idempotent
✅ Pillar R (Logging): Semantic logging with traceId

Note: Only checking Pillars enabled in this project's profile

## ADR Compliance
Scanned docs/adr/ and found 3 ADRs in this project:

✅ ADR-005 (Identity Model): All IDs use branded types
⚠️  ADR-009 (Zustand Vanilla Store Pattern)
    Found in: src/stores/taskStore.ts:5
    Issue: Using create() instead of createStore()
    Fix: import { createStore } from 'zustand/vanilla'
    Impact: Services cannot access store (violates ADR-009)
✅ ADR-007 (AWS Amplify Deployment): CDK patterns followed

Note: ADR checks are project-specific (based on your docs/adr/)

## ⚠️ Observations
1. ADR-009 violation (blocker - must fix)
2. Consider extracting duplicate validation logic
3. One N+1 query in user loader

## 🚀 Suggestions
1. Fix ADR-009 violation:
   ```ts
   // Before
   import { create } from 'zustand'
   export const taskStore = create(...)

   // After (per ADR-009)
   import { createStore } from 'zustand/vanilla'
   export const taskStore = createStore(...)
   ```
2. Extract common validation into reusable function
3. Add caching for user queries

## Approval
⚠️  Approved with recommendations (fix ADR-009 before merge)
```

## Approval Process

1. **Green lights** ✅
   - All quality checks pass
   - Architecture sound
   - Pillar patterns correctly used
   - ADR compliance verified
   - No security issues

2. **Yellow flags** ⚠️
   - Minor issues that don't block merge
   - Non-critical ADR deviations (with justification)
   - Can be fixed in follow-up PR
   - Logged as future improvement

3. **Red flags** ❌
   - Must fix before merge
   - Security issues
   - Breaking changes
   - Architecture problems
   - Critical ADR violations (affects other teams/services)

---

## Integration with finish-issue

After completing the review, **automatically write review status** to `.claude/.review-status.json`:

```json
{
  "timestamp": "2026-03-04T10:30:00Z",
  "status": "approved" | "approved_with_recommendations" | "issues_found",
  "score": 85,
  "files_reviewed": ["src/auth/*.ts", "src/services/*.ts"],
  "issues_count": {
    "blocking": 0,
    "non_blocking": 2
  },
  "valid_until": "2026-03-04T12:00:00Z"
}
```

**Status Mapping**:
- `"approved"` → ✅ All green lights, no issues
- `"approved_with_recommendations"` → ⚠️ Yellow flags, can merge with observations
- `"issues_found"` → ❌ Red flags, must fix before merge

**Valid Duration**: 90 minutes from review completion

**Usage**:
```bash
/review
# → Performs review
# → Writes status file
# → /finish-issue will detect and use this status
```

---

Review command enables:
- Self-review before PR
- Architecture verification (Pillars + ADRs)
- Quality consistency
- ADR compliance enforcement
- Learning opportunities
- Automatic integration with finish-issue workflow

**ADR Integration** (Dynamic & Project-Agnostic):
- Scans current project's `docs/adr/` automatically
- Works with ANY ADRs (no hardcoded checks)
- Adapts to your project's architectural decisions
- Reports violations with fix suggestions
- Ensures architectural consistency across team
- Different projects → different ADR checks
- No assumptions about which ADRs exist
