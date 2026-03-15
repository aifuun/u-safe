# Eval Plan - Reference Documentation

Advanced topics and detailed examples for the /eval-plan skill.

## Detailed Example Evaluations

### Example 1: Excellent Plan (Score 95/100)

**Issue**: Add user management system
**Plan tasks:**
```markdown
1. Create UserService in domain/services/ with CRUD operations
2. Add Zod schema validation for user input (email, password, name)
3. Implement error handling with Result<T, E> pattern
4. Add repository layer with UserRepository interface
5. Create unit tests for UserService (target: 85% coverage)
6. Add integration tests for user API endpoints
7. Update API documentation (OpenAPI spec)
8. Add structured logging for user operations (create, update, delete)
9. Implement rate limiting for user creation (5 requests/minute)
10. Update security audit log for user actions
```

**Evaluation breakdown:**
- Architecture (40/40): Perfect layer separation, follows clean architecture
- Coverage (30/30): All acceptance criteria mapped to tasks
- Dependencies (15/15): Logical ordering, service → repository → tests
- Best Practices (8/10): All major practices covered, minor: no performance testing
- Clarity (2/5): Most tasks clear, Task 1 could specify CRUD methods

**Issues:** None blocking
**Suggestions:** Specify UserService methods explicitly in Task 1

**Result:** ✅ Approved - Excellent plan, ready to proceed

---

### Example 2: Good with Recommendations (Score 82/100)

**Issue**: Implement shopping cart functionality
**Plan tasks:**
```markdown
1. Add cart component
2. Connect to API
3. Add validation
4. Add persistence
5. Add tests
```

**Evaluation breakdown:**
- Architecture (32/40): Unclear about layer separation in Task 2
- Coverage (28/30): Good coverage, missing: "cart quantity limits" criterion
- Dependencies (15/15): Correct sequential order
- Practices (5/10): Missing error handling, logging tasks
- Clarity (2/5): Tasks too vague (especially "Add tests")

**Recommendations:**
1. **Task 2** - Clarify: Should use CartService, not direct API calls from component
2. **Missing** - Add task for error handling (API failures, validation errors)
3. **Missing** - Add criterion: Cart quantity limits (max 99 per item)
4. **Task 5** - Specify: "Add unit tests for CartService + integration tests for cart API"
5. **Missing** - Add logging task for cart operations

**Result:** ⚠️ Approved with recommendations (fix before implementation preferred)

---

### Example 3: Problematic Plan (Score 58/100)

**Issue**: Fix user authentication
**Plan tasks:**
```markdown
1. Fix authentication
2. Add tests
3. Make it work
```

**Evaluation breakdown:**
- Architecture (15/40): No architectural guidance, unclear approach
- Coverage (12/30): Extremely vague, can't verify criteria coverage
- Dependencies (8/15): Unclear task relationships
- Practices (3/10): Missing error handling, docs, logging, security review
- Clarity (0/5): All tasks completely vague

**Blocking issues:**
1. **Task clarity**: All tasks need specific, actionable descriptions
   - "Fix authentication" → What exactly? Password reset? Token refresh? Session management?
   - "Add tests" → Which tests? For what functionality? What coverage?
   - "Make it work" → Not a real task

2. **Missing acceptance criteria mapping**: Issue has 5 criteria, none clearly addressed
   - Criterion: "Users can log in with email/password" → No corresponding task
   - Criterion: "Sessions expire after 24 hours" → Not mentioned
   - Criterion: "Password reset via email" → Not mentioned

3. **No architecture considerations**: Should use JWT? Sessions? Where stored?

**Must fix:**
- Rewrite all 3 tasks with specific descriptions
- Map each acceptance criterion to tasks
- Add error handling, logging, testing tasks
- Define authentication approach (architecture)

**Result:** ❌ Rejected - Plan needs complete revision

---

## Scoring Rubrics

### Architecture Alignment (40 points)

| Score | Description | Examples |
|-------|-------------|----------|
| 36-40 | Perfect alignment | All tasks respect layers, clear boundaries, follows patterns |
| 30-35 | Minor issues | 1-2 tasks with unclear layer placement, fixable |
| 20-29 | Some violations | Multiple layer violations, needs significant revision |
| 10-19 | Major problems | Fundamental architecture ignored, deep refactor needed |
| 0-9 | Critical issues | No architecture consideration, creates technical debt |

### Acceptance Criteria Coverage (30 points)

| Score | Description | Coverage % |
|-------|-------------|-----------|
| 28-30 | Complete | 100% criteria mapped, no scope creep |
| 24-27 | Excellent | 90-99% coverage, minor gaps |
| 18-23 | Good | 80-89% coverage, some missing items |
| 12-17 | Fair | 70-79% coverage, significant gaps |
| 0-11 | Poor | <70% coverage or major scope creep |

### Task Dependencies (15 points)

| Score | Description |
|-------|-------------|
| 13-15 | Perfect ordering, clear dependencies |
| 10-12 | Minor ordering issues, easy to fix |
| 6-9 | Several issues, needs rework |
| 3-5 | Major confusion, unclear flow |
| 0-2 | Circular dependencies or chaos |

### Best Practices (10 points)

| Score | Practices Covered |
|-------|-------------------|
| 9-10 | Error handling, tests, docs, logging, security, performance |
| 7-8 | Most practices, 1-2 minor gaps |
| 5-6 | Several gaps (e.g., no error handling, no logging) |
| 3-4 | Major gaps (e.g., no tests, no docs) |
| 0-2 | Critical practices missing (no tests at all) |

### Task Clarity (5 points)

| Score | Description |
|-------|-------------|
| 5 | All tasks specific, actionable, clear acceptance criteria |
| 3-4 | Mostly clear, 1-2 vague tasks |
| 1-2 | Several vague tasks, needs improvement |
| 0 | Most/all tasks vague or unclear |

---

## Common Plan Issues

### Issue: Vague Tasks

**Bad:**
- "Add tests"
- "Fix bugs"
- "Implement feature"
- "Make it better"

**Good:**
- "Add unit tests for UserService covering CRUD operations (target: 85% coverage)"
- "Fix null pointer exception in cart.calculateTotal() when cart is empty"
- "Implement user login with email/password validation and JWT token generation"
- "Refactor TaskList component to use React hooks instead of class components"

### Issue: Architecture Violations

**Bad:**
- "Add database query in React component"
- "Import UI component in service layer"
- "Call external API directly from component"
- "Put business logic in controller"

**Good:**
- "Create UserRepository in data layer for database operations"
- "Add service layer between UI and data access"
- "Wrap external API calls in adapter pattern"
- "Move validation logic from controller to domain service"

### Issue: Missing Dependencies

**Bad ordering:**
```markdown
1. Add tests for AuthService
2. Deploy to production
3. Create AuthService
```

**Good ordering:**
```markdown
1. Create AuthService
2. Add tests for AuthService
3. Deploy to production
```

### Issue: Scope Creep

**Issue acceptance criteria:**
1. User can create task
2. User can mark task complete

**Plan includes:**
- ✅ Task creation (criterion #1)
- ✅ Task completion (criterion #2)
- ❌ Task editing (NOT in criteria - scope creep)
- ❌ Task deletion (NOT in criteria - scope creep)
- ❌ Task priority sorting (NOT in criteria - scope creep)

**Fix:** Remove non-criteria tasks OR update issue to include new criteria

---

## Integration Patterns

### Standalone Usage

```bash
# After creating plan manually
/start-issue #23
# Edit .claude/plans/active/issue-23-plan.md
/eval-plan #23
# Review results, fix issues
/eval-plan #23  # Re-evaluate
/execute-plan #23
```

### Integrated with /work-issue

```bash
/work-issue #23

# Workflow:
# 1. /start-issue creates plan
# 2. /eval-plan runs automatically ← THIS SKILL
# 3. Checkpoint 1: Review eval results
#    - Interactive: Always stop
#    - Auto (--auto): Stop if score ≤ 90
# 4. User can edit plan and re-evaluate
# 5. Continue to /execute-plan
```

### Automation Mode

```bash
/work-issue #23 --auto

# Behavior with eval-plan:
# - Runs /eval-plan automatically
# - If score > 90: Skip Checkpoint 1, proceed
# - If score ≤ 90: Stop at Checkpoint 1 for review
# - Same threshold for /review (code quality)
```

---

## Status File Format

The `.claude/.eval-plan-status.json` file enables integration with /work-issue:

```json
{
  "timestamp": "2026-03-11T10:30:00Z",
  "issue_number": 23,
  "issue_title": "Fix user authentication flow",
  "plan_file": ".claude/plans/active/issue-23-plan.md",
  "status": "needs_improvement",
  "score": 82,
  "breakdown": {
    "architecture": { "score": 35, "max": 40 },
    "coverage": { "score": 25, "max": 30 },
    "dependencies": { "score": 12, "max": 15 },
    "practices": { "score": 7, "max": 10 },
    "clarity": { "score": 3, "max": 5 }
  },
  "issues": {
    "blocking": [],
    "recommendations": [
      {
        "task": "Task 5",
        "category": "architecture",
        "description": "API endpoint in UI component",
        "fix": "Move to service layer",
        "impact": "high"
      }
    ],
    "suggestions": [
      "Add documentation update task",
      "Add logging for auth events"
    ]
  },
  "metrics": {
    "total_tasks": 8,
    "acceptance_criteria": 5,
    "coverage_percentage": 90
  },
  "valid_until": "2026-03-11T12:00:00Z"
}
```

**Fields:**
- `status`: "approved" | "needs_improvement" | "rejected"
- `score`: 0-100 integer
- `valid_until`: ISO 8601 timestamp (90 minutes from evaluation)
- `breakdown`: Scores for each dimension
- `issues`: Categorized findings (blocking, recommendations, suggestions)

---

## Best Practices for Plan Creation

### 1. Start with Acceptance Criteria

Map each criterion to at least one task:
```
Criterion: User can reset password
→ Task: Implement password reset with email verification
→ Task: Add password reset UI form
→ Task: Test password reset flow
```

### 2. Follow Architectural Layers

```
Good task sequence:
1. Create domain entities (User, Task)
2. Create repository interfaces
3. Implement repositories (data layer)
4. Create services (domain layer)
5. Create controllers/APIs (presentation layer)
6. Create UI components
7. Add tests bottom-up (domain → presentation)
```

### 3. Include Cross-Cutting Concerns

Always consider:
- Error handling (how failures are handled)
- Logging (what events are logged)
- Testing (unit, integration, e2e)
- Documentation (API docs, README updates)
- Security (auth, validation, sanitization)
- Performance (caching, optimization)

### 4. Make Tasks Atomic

Each task should be:
- Completable in one session (30 min - 2 hours)
- Testable (clear acceptance criteria)
- Independent or with clear dependencies

---

**Version:** 1.0.0
**Last Updated:** 2026-03-11
