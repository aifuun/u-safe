# Review Examples

Real-world usage examples for the `/review` skill.

## Example 1: Review Current Changes

**User says:**
> "review my code"

**What happens:**
1. Detect issue number from branch: `feature/421-skill-4-review-optimization` → #421
2. Run smart decision: Analyze change size (4 files, 120 lines)
3. Select strategy: MEDIUM (balanced review)
4. Execute checks:
   - ✅ Quality gates (30/30)
   - ✅ Architecture (23/25) - minor: file too long
   - ✅ Pillars (18/20) - missing: error handling in 1 function
   - ✅ ADRs (10/10)
   - ✅ Security (10/10)
   - ⚠️ Performance (3/5) - suggestion: cache repeated calls
5. Write status file: `.claude/.review-status.json`
6. Report: **Score 94/100 - APPROVED**

**Time:** ~60 seconds

## Example 2: Review Specific Files

**User says:**
> "review just the changes in src/components/"

**What happens:**
1. Run smart decision on filtered files
2. Detect: Small change (2 files, 35 lines)
3. Select strategy: SMALL (quality-focused)
4. Execute checks:
   - ✅ Quality gates
   - ✅ Quick architecture scan
   - Skip: Full Pillar review (use heuristics)
5. Report: **Score 92/100 - APPROVED**

**Time:** ~30 seconds (faster due to SMALL strategy)

## Example 3: Pre-PR Review

**User says:**
> "run a thorough review before I create the PR"

**What happens:**
1. Full review with all dimensions
2. Include goal coverage check
3. Skill version check (if SKILL.md modified)
4. Report comprehensive findings:
   - Goal coverage: 90% (AC3 missing)
   - Quality: 95/100
   - Recommendations: 3
5. Status: **NEEDS_IMPROVEMENT** (AC3 not implemented)

**Time:** ~90 seconds

## Example 4: Goal Coverage Failure

**Scenario:** Issue #301 requires 5 acceptance criteria, but only 3 implemented.

**Review output:**
```markdown
## 1. Goal Coverage Check ❌

**Issue Requirements**: 3/5 (60%) ← Below 80% threshold
Missing:
- AC3: Support batch operations
- AC5: Add undo functionality

**Plan Tasks**: 10/10 (100%)

**Score**: 60/100
**Status**: REJECTED (blocking)

→ Cannot proceed. Implement AC3 and AC5 first.
```

**Action:** Fix missing ACs, re-run `/review`

## Example 5: Skill Version Not Updated

**Scenario:** Modified `.claude/skills/eval-plan/SKILL.md` but forgot to update version.

**Review output:**
```markdown
## 3. Skill Version Check ⚠️

**Modified Skills**: 1

⚠️ `.claude/skills/eval-plan/SKILL.md`
   Version: 1.1.0 (unchanged) ← Content modified
   Suggested: 1.2.0 (minor bump)
   Reason: Added auto-fix feature

**Fix:**
1. Edit .claude/skills/eval-plan/SKILL.md
2. Change: version: "1.1.0"
3. To: version: "1.2.0"
4. Re-run /review

**Status**: NEEDS_IMPROVEMENT (blocking)
```

**Action:** Update version, re-run `/review`

## Example 6: Architecture Violation

**Scenario:** API call directly in React component (violates clean architecture).

**Review output:**
```markdown
## 5. Architecture Validation ⚠️

**Issue Found:**
- File: src/components/UserProfile.tsx:45
- Violation: Direct API call in UI component
- Rule: UI layer should not import from data layer

**Fix:**
```typescript
// ❌ WRONG (current code)
import { fetchUser } from '@/api/users';

function UserProfile() {
  const user = await fetchUser(userId); // Direct API call
  ...
}

// ✅ CORRECT (move to service layer)
import { useUserService } from '@/services/userService';

function UserProfile() {
  const { user } = useUserService(userId); // Service layer handles API
  ...
}
```

**Impact:** Medium
**Score Deduction:** -5 points (from Architecture dimension)
```

## Example 7: Security Vulnerability

**Scenario:** User input not validated, XSS risk.

**Review output:**
```markdown
## 8. Security Scan ❌

**Vulnerability Found:**
- File: src/components/CommentForm.tsx:28
- Type: XSS (Cross-Site Scripting)
- Severity: HIGH
- Description: User input rendered directly without sanitization

**Vulnerable Code:**
```typescript
<div dangerouslySetInnerHTML={{ __html: userComment }} />
```

**Fix:**
```typescript
import DOMPurify from 'dompurify';

<div dangerouslySetInnerHTML={{
  __html: DOMPurify.sanitize(userComment)
}} />
```

**Impact:** Critical
**Status**: REJECTED (must fix before merge)
```

## Example 8: Performance Issue

**Scenario:** O(n²) algorithm where O(n) possible.

**Review output:**
```markdown
## 9. Performance Check ⚠️

**Issue Found:**
- File: src/utils/arrayHelpers.ts:12
- Type: Algorithmic complexity
- Current: O(n²)
- Optimal: O(n)

**Inefficient Code:**
```typescript
function findDuplicates(arr: number[]): number[] {
  const duplicates = [];
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {  // O(n²)
      if (arr[i] === arr[j]) {
        duplicates.push(arr[i]);
      }
    }
  }
  return duplicates;
}
```

**Optimized Code:**
```typescript
function findDuplicates(arr: number[]): number[] {
  const seen = new Set<number>();
  const duplicates = new Set<number>();

  for (const num of arr) {  // O(n)
    if (seen.has(num)) {
      duplicates.add(num);
    } else {
      seen.add(num);
    }
  }

  return Array.from(duplicates);
}
```

**Impact:** Medium (acceptable for small arrays, but could be better)
**Score Deduction:** -2 points
```

## Example 9: Auto Mode (Called by /work-issue)

**Context:** Part of automated workflow, minimal output.

**Review output:**
```
✅ Review complete: 92/100 (approved)
Status: .claude/.review-status.json
```

**Status file:**
```json
{
  "timestamp": "2026-03-30T10:30:00Z",
  "issue_number": 421,
  "status": "approved",
  "score": 92,
  "breakdown": {
    "quality_gates": 30,
    "architecture": 23,
    "pillar_compliance": 18,
    "adr_compliance": 10,
    "security": 10,
    "performance": 1
  },
  "issues_count": {
    "blocking": 0,
    "recommendations": 2
  }
}
```

## Example 10: Interactive Mode (Direct Invocation)

**Context:** User directly runs `/review`, full output.

**Review output:**
```markdown
# Code Review: Issue #421

Score: 92/100 (approved)
Issues: 0 blocking, 2 recommendations

Top Recommendations:
1. Architecture - Task 5: Move API call to service layer (-2 pts)
2. Performance - Use Set for faster lookup in Task 3 (-2 pts)

Full details: .claude/.review-status.json
Next: /finish-issue #421
```

## Usage Patterns

### Pattern 1: Standard Workflow
```bash
/start-issue #23      # Create plan
/execute-plan #23     # Implement
/review               # Validate ← THIS EXAMPLE
/finish-issue #23     # Ship
```

### Pattern 2: Iterative Development
```bash
/review               # Check current state
# ... fix issues ...
/review               # Re-check
# ... repeat until APPROVED ...
/finish-issue #23
```

### Pattern 3: Auto Mode (No Intervention)
```bash
/auto-solve-issue #23  # Runs review automatically as Phase 2.5
# Review happens transparently with minimal output
```

## Related

- **Parent skill**: `/review` - Main code review skill
- **CHECKLIST.md**: Complete review checklist
- **QUALITY.md**: Scoring methodology

---

**Version:** 1.0.0
**Last Updated:** 2026-03-30
**Part of:** review skill v2.4.0
