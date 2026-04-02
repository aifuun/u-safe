# Review Checklist - Complete Quality Checks

Complete checklist for manual and automated code review.

## Overview

This document provides the complete review checklist used by the `/review` skill. Use it for:
- Manual code reviews
- Understanding automated checks
- Creating custom review workflows

## 1. Quality Gates

Basic quality checks that every project needs:

### TypeScript Compilation
```bash
# Check types are valid
npx tsc --noEmit

# Expected: No type errors
# ❌ Fail if: Type errors present
```

### Test Execution
```bash
# Run all tests
npm test

# Expected: All tests passing
# ❌ Fail if: Any test failures
```

### Linting
```bash
# Check code style
npm run lint

# Expected: No linting errors
# ⚠️ Warn if: Linting warnings (not blocking)
```

### Build
```bash
# Verify build succeeds
npm run build

# Expected: Build completes without errors
# ❌ Fail if: Build fails
```

## 2. Architecture Validation

Check architecture patterns based on project rules:

### Layer Separation
- ✅ UI layer doesn't import from data layer
- ✅ Business logic in domain/service layer
- ✅ Data access in repository/data layer

### Dependency Direction
- ✅ Dependencies point inward (UI → Domain → Data)
- ❌ No outward dependencies (Data → UI)
- ❌ No cross-layer shortcuts

### Module Boundaries
- ✅ Clear module interfaces
- ✅ No circular dependencies between modules
- ✅ Cohesive modules (related functionality together)

## 3. Pillar Compliance

Check against project Pillars (based on profile):

### Common Pillars (All Projects)
- [ ] Error handling present and comprehensive
- [ ] Logging at appropriate levels
- [ ] Input validation at boundaries
- [ ] Clear documentation for public APIs
- [ ] Test coverage for new/modified code

### Profile-Specific Pillars
**Tauri Projects:**
- [ ] Secure IPC commands
- [ ] State management patterns
- [ ] Event handling

**Next.js Projects:**
- [ ] Server/client component separation
- [ ] Data fetching patterns
- [ ] Route organization

## 4. ADR Compliance

Verify adherence to Architecture Decision Records:

### ADR Discovery
```bash
# Find ADRs in project
find docs/ADRs -name "*.md" | sort
```

### Compliance Check
For each relevant ADR:
- [ ] Read ADR decision and rationale
- [ ] Verify code follows ADR pattern
- [ ] Check for violations
- [ ] Flag deviations with justification

### Common ADRs to Check
- ADR-001: Skill patterns
- ADR-007: Profile-aware rules
- ADR-012: Modular docs management
- ADR-014: Skill implementation patterns

## 5. Security Scan

Identify security vulnerabilities:

### Input Validation
- [ ] User inputs validated
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection (if web app)

### Authentication & Authorization
- [ ] Authentication checks present
- [ ] Authorization for protected resources
- [ ] Session management secure

### Data Handling
- [ ] Sensitive data encrypted
- [ ] No secrets in code
- [ ] Proper error messages (no info leakage)

### Dependencies
```bash
# Check for vulnerable dependencies
npm audit

# Expected: No high/critical vulnerabilities
# ⚠️ Warn if: Moderate vulnerabilities
```

## 6. Performance Check

Detect performance issues:

### Algorithmic Complexity
- [ ] No O(n²) loops where O(n) possible
- [ ] Efficient data structures used
- [ ] No unnecessary computations

### Resource Usage
- [ ] No memory leaks
- [ ] Database queries optimized
- [ ] File handles closed properly

### Caching
- [ ] Expensive operations cached
- [ ] Cache invalidation handled
- [ ] No over-caching (stale data)

### Frontend Performance
- [ ] No unnecessary re-renders
- [ ] Large lists virtualized
- [ ] Images optimized
- [ ] Code splitting for large bundles

## 7. Code Quality

General code quality checks:

### Readability
- [ ] Clear variable/function names
- [ ] Appropriate comments (explain "why", not "what")
- [ ] Consistent formatting
- [ ] No overly complex functions

### Maintainability
- [ ] Single Responsibility Principle
- [ ] DRY (Don't Repeat Yourself)
- [ ] Clear abstractions
- [ ] Testable code structure

### Error Handling
- [ ] Errors handled gracefully
- [ ] User-friendly error messages
- [ ] Logging for debugging
- [ ] No empty catch blocks

## 8. Documentation

Check documentation completeness:

### Code Documentation
- [ ] Public APIs documented
- [ ] Complex logic explained
- [ ] Examples for usage patterns
- [ ] TODO comments for follow-up work

### Project Documentation
- [ ] README updated (if needed)
- [ ] CHANGELOG updated (if needed)
- [ ] Migration guide (if breaking changes)
- [ ] ADRs created (if architectural decisions)

## Review Workflow

### Pre-Review
1. Ensure all changes committed
2. Sync with main branch
3. Run quality gates locally

### During Review
1. Run automated checks (Steps 1-6)
2. Manual code review (Step 7)
3. Check documentation (Step 8)
4. Record findings

### Post-Review
1. Write `.claude/.review-status.json`
2. Report score and issues
3. Provide fix recommendations

## Scoring

Each dimension scored independently:

| Dimension | Max Points | Weight |
|-----------|------------|--------|
| Quality Gates | 30 | Critical |
| Architecture | 25 | High |
| Pillar Compliance | 20 | High |
| ADR Compliance | 10 | Medium |
| Security | 10 | High |
| Performance | 5 | Medium |

**Total Score**: 0-100

**Approval Levels**:
- ✅ **Approved** (>90): Ready to merge
- ⚠️ **Needs Improvement** (70-90): Fix recommendations, can merge
- ❌ **Rejected** (<70): Must fix blocking issues

## Usage

**As part of /review skill:**
The skill automatically runs these checks and scores each dimension.

**For manual review:**
Use this checklist to systematically review code changes.

**For custom workflows:**
Select relevant sections based on project needs.

---

**Version:** 1.0.0
**Last Updated:** 2026-03-30
**Part of:** review skill v2.4.0
