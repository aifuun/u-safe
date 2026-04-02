# Eval Plan - Evaluation Checklist

Detailed evaluation criteria for the 5 dimensions used in plan validation.

## Overview

This document provides the complete evaluation checklist for assessing implementation plans. Each dimension has specific criteria, scoring guidelines, and examples.

**Total Score**: 100 points (Architecture 40 + Coverage 30 + Dependencies 15 + Practices 10 + Clarity 5)

**Related**: See [SKILL.md](SKILL.md) for overview | [SCORING.md](SCORING.md) for scoring algorithm

---

## Dimension 1: Architecture Alignment (40 points)

**Purpose**: Ensure plan respects architectural boundaries and follows clean architecture principles.

### What It Checks

- **Module boundaries** - Components grouped by domain, not technical layer
- **Dependency direction** - Always inward (UI → Domain → Data, never reversed)
- **Layer separation** - UI, business logic, and data access are distinct
- **Anti-patterns** - No God objects, circular dependencies, or tight coupling
- **Standards compliance** - Follows `.claude/rules/architecture/` guidelines

### How to Check

1. **Read architecture rules**:
   ```bash
   ls .claude/rules/architecture/
   # Read applicable architecture files
   ```

2. **Review task descriptions** for violations:
   - UI component directly calling database
   - Business logic in React components
   - Circular imports between modules
   - Tight coupling to external APIs

3. **Check layer ordering**:
   ```
   ✅ CORRECT: UI → Service → Repository → Database
   ❌ WRONG:   UI → Database (skips service layer)
   ❌ WRONG:   Service → UI (reversed dependency)
   ```

### Common Violations

| Violation | Example | Fix |
|-----------|---------|-----|
| **DB in UI** | `<LoginForm>` has SQL query | Move query to `authService.login()` |
| **UI in Service** | `userService` imports `<Button>` | Remove UI dependency, use callbacks |
| **API in Component** | `fetch()` in component | Move to service layer with abstraction |
| **Circular Deps** | Module A imports B, B imports A | Introduce interface or third module |
| **God Object** | `Utils` class with 50 methods | Split by domain (userUtils, dateUtils, etc.) |

### Scoring Rubric

| Score | Criteria | Example |
|-------|----------|---------|
| **40/40** | Perfect separation, all dependencies correct, no violations | Service → Repository → Model pattern throughout |
| **35/40** | 1-2 minor issues, easily fixable | One component with inline fetch (not systemic) |
| **30/40** | 3-4 minor issues or 1 moderate issue | Some components bypass service layer |
| **20/40** | Multiple moderate issues or 1 major issue | Several UI components with DB access |
| **10/40** | Major architectural problems | No separation, tight coupling throughout |
| **0/40** | Fundamentally flawed architecture | All logic in UI, no service layer |

### Examples

**Score 40/40 (Perfect)**:
```markdown
## Tasks
1. Create UserRepository (data access)
2. Create UserService (business logic, uses UserRepository)
3. Create LoginPage component (UI, uses UserService)
4. Add unit tests for UserRepository
5. Add integration tests for UserService
```

**Score 25/40 (Needs Improvement)**:
```markdown
## Tasks
1. Create UserForm component with validation
2. Add database query to UserForm  ← VIOLATION: DB in UI
3. Create UserService (unused)
4. Add tests
```

**Score 10/40 (Major Problems)**:
```markdown
## Tasks
1. Add login form with inline fetch  ← UI → API
2. Put validation in component  ← Business logic in UI
3. Query database from onClick  ← DB in UI
```

---

## Dimension 2: Acceptance Criteria Coverage (30 points)

**Purpose**: Verify all issue requirements are addressed in the plan.

### What It Checks

- **Complete coverage** - Every acceptance criterion has corresponding task(s)
- **No gaps** - No criteria left unaddressed
- **Clear mapping** - Tasks explicitly reference which criterion they satisfy
- **No scope creep** - No extra features not in acceptance criteria

### How to Check

1. **Extract acceptance criteria** from issue:
   ```markdown
   ## Acceptance Criteria
   - [ ] User can log in with email/password
   - [ ] Session persists across page reloads
   - [ ] Error messages display for invalid credentials
   - [ ] Loading state shown during authentication
   ```

2. **Map each criterion to task(s)**:
   ```markdown
   Criterion 1 → Task 3 (Create login form)
   Criterion 2 → Task 5 (Implement session storage)
   Criterion 3 → Task 7 (Add error handling)
   Criterion 4 → Task 4 (Add loading spinner)
   ```

3. **Flag coverage gaps**:
   - Criterion has no corresponding task = **BLOCKING**
   - Task addresses no criterion = **Scope creep warning**

### Scoring Rubric

| Score | Coverage | Gap Analysis |
|-------|----------|--------------|
| **30/30** | 100% | All criteria addressed, clear mapping |
| **28/30** | 95-99% | 1 minor criterion not explicitly covered but implied |
| **25/30** | 90-94% | 1 criterion missing or 1-2 unclear mappings |
| **20/30** | 80-89% | 2 criteria missing or significant mapping gaps |
| **15/30** | 70-79% | Multiple missing criteria |
| **10/30** | 50-69% | Half or more criteria unaddressed |
| **0/30** | <50% | Most criteria not covered |

### Examples

**Score 30/30 (Perfect Coverage)**:
```markdown
## Issue Acceptance Criteria
- [ ] Login form with email/password
- [ ] Session persists
- [ ] Error handling

## Plan Tasks
1. Create login form (addresses criterion 1)
2. Implement JWT storage (addresses criterion 2)
3. Add error messages (addresses criterion 3)
4. Add tests for all criteria
```

**Score 20/30 (Gaps Present)**:
```markdown
## Issue Acceptance Criteria
- [ ] Login form
- [ ] Session persists  ← NOT ADDRESSED
- [ ] Error handling

## Plan Tasks
1. Create login form (criterion 1 ✓)
2. Add error messages (criterion 3 ✓)
3. Add styling  ← SCOPE CREEP (not in criteria)
```

---

## Dimension 3: Task Dependencies (15 points)

**Purpose**: Ensure tasks are ordered correctly with proper dependencies.

### What It Checks

- **Topological order** - Tasks can be executed in sequence without backtracking
- **Dependencies explicit** - Clear which tasks must complete before others
- **No circular dependencies** - Task A doesn't depend on B while B depends on A
- **Logical prerequisites** - Setup tasks before implementation, tests after code

### How to Check

1. **Build dependency graph**:
   ```
   Task 1 (Setup DB schema)
     ↓
   Task 2 (Create models) ← depends on Task 1
     ↓
   Task 3 (Create service) ← depends on Task 2
     ↓
   Task 4 (Add tests) ← depends on Task 3
   ```

2. **Check for cycles**:
   ```
   Task A → Task B → Task C → Task A  ← CIRCULAR (invalid)
   ```

3. **Verify logical order**:
   ```
   ✅ CORRECT: Create function → Test function → Document function
   ❌ WRONG:   Test function → Create function (can't test what doesn't exist)
   ```

### Common Issues

| Issue | Example | Fix |
|-------|---------|-----|
| **Test before code** | Task 1: Test UserService<br>Task 2: Create UserService | Swap order |
| **Circular deps** | Task A needs B, Task B needs A | Introduce Task C (interface) |
| **Missing prerequisites** | Task 1: Use database<br>(no schema setup task) | Add Task 0: Setup schema |
| **Parallel impossible** | Tasks marked parallel but share resources | Mark as sequential |

### Scoring Rubric

| Score | Criteria | Issues |
|-------|----------|--------|
| **15/15** | Perfect topological order, no cycles, all dependencies clear | None |
| **12/15** | 1-2 minor ordering issues (easy to fix) | One test task slightly out of order |
| **10/15** | 3-4 minor issues or 1 moderate issue | Missing intermediate task |
| **7/15** | Multiple moderate issues | Several dependency violations |
| **5/15** | Major ordering problems | Many tasks can't execute due to dependencies |
| **0/15** | Circular dependencies or complete chaos | Cannot determine valid execution order |

### Examples

**Score 15/15 (Perfect Order)**:
```markdown
1. Setup database schema
2. Create User model (depends on #1)
3. Create UserRepository (depends on #2)
4. Create UserService (depends on #3)
5. Add unit tests (depends on #2, #3, #4)
6. Add integration tests (depends on #5)
```

**Score 8/15 (Dependency Issues)**:
```markdown
1. Create UserService  ← WRONG: needs models first
2. Test UserService  ← WRONG: before service created
3. Create User model  ← SHOULD BE FIRST
4. Add database  ← SHOULD BE BEFORE models
```

---

## Dimension 4: Best Practices (10 points)

**Purpose**: Ensure plan includes essential software engineering practices.

### What It Checks

- **Error handling** - Strategy for handling failures defined
- **Documentation** - Plan includes doc updates (README, API docs, etc.)
- **Logging/monitoring** - Appropriate logging for debugging and observability
- **Test coverage** - Unit tests, integration tests, or E2E tests planned
- **Security** - Security considerations addressed (input validation, auth, etc.)
- **Performance** - Performance implications considered (caching, optimization)

### Checklist

```markdown
Best Practices Checklist:
- [ ] Error handling strategy (try/catch, error boundaries, fallbacks)
- [ ] Tests planned (unit/integration/E2E)
- [ ] Documentation updates (README, API docs, comments)
- [ ] Logging added (debug logs, error logs, metrics)
- [ ] Security considered (validation, sanitization, auth)
- [ ] Performance assessed (caching, lazy loading, optimization)
```

### Scoring Rubric

| Score | Coverage | Details |
|-------|----------|---------|
| **10/10** | All 6 practices covered | Explicit tasks for each practice |
| **8/10** | 5/6 practices covered | Missing one non-critical practice |
| **7/10** | 4/6 practices covered | Missing 2 practices |
| **5/10** | 3/6 practices covered | Missing several key practices |
| **3/10** | 2/6 practices covered | Only tests and docs |
| **0/10** | 0-1/6 practices covered | No best practices considered |

### Examples

**Score 10/10 (All Practices)**:
```markdown
## Tasks
1. Create UserService
   - Add input validation (security ✓)
   - Add error handling (error handling ✓)
   - Add caching layer (performance ✓)
2. Add unit tests (tests ✓)
3. Add logging for auth events (logging ✓)
4. Update API documentation (documentation ✓)
```

**Score 5/10 (Gaps)**:
```markdown
## Tasks
1. Create UserService  ← No error handling mentioned
2. Add tests (tests ✓)
3. Update README (documentation ✓)
   ← Missing: logging, security, performance
```

---

## Dimension 5: Task Clarity (5 points)

**Purpose**: Ensure tasks are specific, actionable, and unambiguous.

### What It Checks

- **Specificity** - Task describes exactly what to build
- **Actionability** - Clear verb ("Create X", "Add Y", "Update Z")
- **No vagueness** - Avoid "Fix bugs", "Add tests", "Improve code"
- **Appropriate granularity** - Not too large (>1 day) or too small (<15 min)
- **Acceptance criteria** - Each task has clear "done" condition

### Bad vs Good Examples

| ❌ Bad (Vague) | ✅ Good (Specific) |
|---------------|-------------------|
| "Add tests" | "Add unit tests for UserService: login(), logout(), validateToken() with 80% coverage" |
| "Fix bugs" | "Fix login bug where session expires after 5 min instead of 30 min" |
| "Improve performance" | "Add Redis caching to reduce API response time from 500ms to <100ms" |
| "Update docs" | "Update README.md with authentication flow diagram and API usage examples" |
| "Refactor code" | "Extract validation logic from UserController to UserValidator class" |

### Scoring Rubric

| Score | Criteria | Example |
|-------|----------|---------|
| **5/5** | All tasks specific, actionable, clear acceptance criteria | "Create UserRepository with CRUD methods (create, read, update, delete) and error handling" |
| **4/5** | 1-2 tasks slightly vague but understandable | "Add validation" (understandable but not specific about what to validate) |
| **3/5** | 3-5 tasks vague, several need clarification | Mix of specific and vague tasks |
| **2/5** | Most tasks vague, hard to execute without questions | "Add features", "Fix issues" |
| **0/5** | All tasks extremely vague or missing | "Do stuff", "Make it work" |

### Granularity Guidelines

| Size | Duration | Example | Assessment |
|------|----------|---------|------------|
| **Too small** | <15 min | "Import React", "Add one line of code" | ❌ Merge with related task |
| **Good** | 30 min - 4 hours | "Create UserService with login/logout" | ✅ Ideal size |
| **Acceptable** | 4 hours - 1 day | "Implement authentication system" | ⚠️ Consider splitting |
| **Too large** | >1 day | "Build entire user management system" | ❌ Must split into subtasks |

---

## Summary

**Total Possible**: 100 points

| Dimension | Max Points | Key Focus |
|-----------|------------|-----------|
| Architecture Alignment | 40 | Clean separation, correct dependencies |
| Acceptance Criteria Coverage | 30 | All requirements addressed |
| Task Dependencies | 15 | Correct order, no cycles |
| Best Practices | 10 | Error handling, tests, docs, logging, security, performance |
| Task Clarity | 5 | Specific, actionable, appropriate granularity |

**Approval Thresholds**:
- **90-100**: ✅ Approved (excellent plan)
- **70-89**: ⚠️ Needs Improvement (acceptable with recommendations)
- **<70**: ❌ Rejected (must fix before implementation)

**See Also**:
- [SKILL.md](SKILL.md) - Skill overview and usage
- [SCORING.md](SCORING.md) - Scoring algorithm and status file format
- [VERSION_CHECK.md](VERSION_CHECK.md) - Version field validation

---

**Version:** 1.0.0
**Last Updated:** 2026-03-30
**Part of**: eval-plan skill (v1.4.0)
**Compliance:** ADR-016 ✅ (modular documentation)
