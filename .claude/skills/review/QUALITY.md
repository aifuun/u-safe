# Quality Standards and Scoring

Quality assessment framework for code review.

## Overview

This document defines quality standards, scoring methodology, and approval thresholds used by the `/review` skill.

## Scoring Dimensions

### 1. Quality Gates (30 points)

**What it checks:**
- TypeScript compilation (types valid)
- Test execution (all passing)
- Linting (no errors)
- Build success

**Scoring:**
- 30 points: All gates pass
- 20 points: 1 gate fails (non-critical)
- 10 points: 2 gates fail
- 0 points: 3+ gates fail or critical failure

**Critical gates:**
- TypeScript compilation
- Build success

**Non-critical gates:**
- Linting (warnings OK)

### 2. Architecture Validation (25 points)

**What it checks:**
- Layer separation (UI → Domain → Data)
- Dependency direction (inward only)
- Module boundaries (no circular deps)
- Adherence to architecture rules

**Scoring:**
- 25 points: Perfect architecture compliance
- 20 points: Minor violations (1-2 issues)
- 15 points: Moderate violations (3-4 issues)
- 10 points: Significant violations (5+ issues)
- 0 points: Architectural anti-patterns present

**Common violations:**
- UI layer imports from data layer (-5 points)
- Circular dependencies between modules (-10 points)
- Business logic in UI components (-5 points)

### 3. Pillar Compliance (20 points)

**What it checks:**
- Error handling present
- Logging at appropriate levels
- Input validation at boundaries
- Documentation for public APIs
- Test coverage for changes

**Scoring:**
- 20 points: All pillars followed
- 15 points: 1 pillar violation
- 10 points: 2 pillar violations
- 5 points: 3 pillar violations
- 0 points: 4+ pillar violations

**Pillar weights:**
- Error handling: Critical (5 points)
- Logging: Important (3 points)
- Input validation: Important (4 points)
- Documentation: Moderate (4 points)
- Test coverage: Important (4 points)

### 4. ADR Compliance (10 points)

**What it checks:**
- Code follows applicable ADRs
- No ADR violations
- Justified deviations documented

**Scoring:**
- 10 points: Full ADR compliance
- 7 points: Minor deviation (documented)
- 5 points: Minor deviation (not documented)
- 0 points: Major ADR violation

### 5. Security (10 points)

**What it checks:**
- Input validation present
- No SQL injection vulnerabilities
- No XSS vulnerabilities
- No secrets in code
- Dependency vulnerabilities checked

**Scoring:**
- 10 points: No security issues
- 7 points: Low severity issues only
- 5 points: Medium severity issues
- 0 points: High/critical security issues

**Severity levels:**
- Critical: Remote code execution, SQL injection, XSS
- High: Authentication bypass, authorization issues
- Medium: Information disclosure, CSRF
- Low: Security headers missing, weak crypto

### 6. Performance (5 points)

**What it checks:**
- No O(n²) algorithms where O(n) possible
- Efficient data structures
- No memory leaks
- Database queries optimized

**Scoring:**
- 5 points: No performance issues
- 3 points: Minor issues (low impact)
- 1 point: Moderate issues (medium impact)
- 0 points: Critical issues (high impact)

## Total Score Calculation

```javascript
totalScore =
  qualityGates +
  architecture +
  pillarCompliance +
  adrCompliance +
  security +
  performance

// Maximum: 100 points
```

## Approval Levels

### ✅ Approved (Score > 90)

**Criteria:**
- All critical gates pass
- No blocking issues
- Minor suggestions only

**Action:**
- Ready to merge
- No changes required
- Proceed to `/finish-issue`

**Example:**
```json
{
  "status": "APPROVED",
  "score": 95,
  "breakdown": {
    "quality_gates": 30,
    "architecture": 23,
    "pillar_compliance": 20,
    "adr_compliance": 10,
    "security": 10,
    "performance": 2
  },
  "issues": [],
  "recommendations": ["Consider caching in Task 5 for better performance"]
}
```

### ⚠️ Needs Improvement (Score 70-90)

**Criteria:**
- Some gates fail or recommendations present
- No critical/blocking issues
- Can merge with awareness

**Action:**
- Review recommendations
- Can proceed if time-constrained
- Better to fix first

**Example:**
```json
{
  "status": "NEEDS_IMPROVEMENT",
  "score": 82,
  "breakdown": {
    "quality_gates": 30,
    "architecture": 20,
    "pillar_compliance": 15,
    "adr_compliance": 7,
    "security": 10,
    "performance": 0
  },
  "issues": [
    {
      "severity": "medium",
      "category": "architecture",
      "description": "Task 5 - API call in UI component",
      "fix": "Move to service layer"
    }
  ]
}
```

### ❌ Rejected (Score < 70)

**Criteria:**
- Critical gates fail
- Blocking issues present
- High rework risk

**Action:**
- Must fix before merge
- Re-run review after fixes
- Do not proceed to `/finish-issue`

**Example:**
```json
{
  "status": "REJECTED",
  "score": 58,
  "breakdown": {
    "quality_gates": 10,
    "architecture": 15,
    "pillar_compliance": 10,
    "adr_compliance": 5,
    "security": 10,
    "performance": 8
  },
  "issues": [
    {
      "severity": "critical",
      "category": "quality_gates",
      "description": "TypeScript compilation fails",
      "fix": "Fix type errors in src/components/..."
    },
    {
      "severity": "high",
      "category": "architecture",
      "description": "Circular dependency between modules",
      "fix": "Refactor module boundaries"
    }
  ]
}
```

## Adaptive Scoring (NEW)

**Smart decision strategy** adjusts scoring based on change size:

### Small Changes (< 50 lines)
- Focus on quality gates (40% weight)
- Quick architecture check (30% weight)
- Skip full Pillar review (use heuristics)

### Medium Changes (50-200 lines)
- Balanced scoring (standard weights)
- Full dimension evaluation
- Standard thresholds apply

### Large Changes (> 200 lines)
- Deep architecture review (35% weight)
- Full Pillar compliance (25% weight)
- Critical path analysis

## Goal Coverage Integration

**New first-phase check** (added in v2.3.0):

### Coverage Score (affects final score)

```javascript
goalCoverageScore = (
  requirementsCoverage * 0.5 +  // 50% weight
  tasksCompletion * 0.3 +        // 30% weight
  (1 - scopeCreep) * 0.2         // 20% weight
) * 100

// If goalCoverageScore < 80, auto-reject
if (goalCoverageScore < 80) {
  return {
    status: 'REJECTED',
    reason: 'Goal coverage too low',
    blocking: true
  }
}
```

### Output Format

```json
{
  "goal_coverage": {
    "score": 85,
    "requirements_coverage": 0.8,
    "tasks_completion": 1.0,
    "uncovered": ["AC3: 批量操作", "AC7: 撤销功能"],
    "status": "NEEDS_IMPROVEMENT"
  }
}
```

## Pass/Fail Decision Tree

```
START
  ↓
[Goal Coverage ≥ 80%?]
  ↓ NO → REJECTED (blocking)
  ↓ YES
[Quality Gates Pass?]
  ↓ NO → REJECTED (critical)
  ↓ YES
[Skill Versions Updated?]
  ↓ NO → NEEDS_IMPROVEMENT (blocking)
  ↓ YES
[Total Score ≥ 90?]
  ↓ YES → APPROVED
  ↓ NO
[Total Score ≥ 70?]
  ↓ YES → NEEDS_IMPROVEMENT
  ↓ NO → REJECTED
```

## Examples

### Example 1: Perfect Score (100)

```
Quality Gates: 30/30 (all pass)
Architecture: 25/25 (perfect compliance)
Pillars: 20/20 (all followed)
ADRs: 10/10 (compliant)
Security: 10/10 (no issues)
Performance: 5/5 (optimal)

Total: 100/100 ✅ APPROVED
```

### Example 2: Good Score (88)

```
Quality Gates: 30/30 (all pass)
Architecture: 20/25 (minor violation - API in UI)
Pillars: 18/20 (missing logging in 1 module)
ADRs: 10/10 (compliant)
Security: 10/10 (no issues)
Performance: 0/5 (O(n²) loop detected)

Total: 88/100 ⚠️ NEEDS_IMPROVEMENT
```

### Example 3: Failed Score (45)

```
Quality Gates: 10/30 (2 gates fail)
Architecture: 10/25 (circular deps)
Pillars: 10/20 (no error handling)
ADRs: 5/10 (deviation not justified)
Security: 5/10 (XSS vulnerability)
Performance: 5/5 (OK)

Total: 45/100 ❌ REJECTED
```

## Related

- **Parent skill**: `/review` - Main code review skill
- **CHECKLIST.md**: Detailed checklist for each dimension
- **VERSION_CHECK.md**: Skill version validation logic

---

**Version:** 1.0.0
**Last Updated:** 2026-03-30
**Part of:** review skill v2.4.0
