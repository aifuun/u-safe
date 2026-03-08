# Strategic Planner Reference Guide

Reference guide for the `/plan` skill with examples, patterns, and best practices.

## When to Use `/plan`

- **Starting a new feature** - Break down requirements into phases
- **Architectural decisions** - Compare different approaches
- **Complex migrations** - Plan step-by-step data transitions
- **Refactoring** - Organize code restructuring work
- **Performance work** - Plan profiling and optimization steps

## Command Usage

### Direct Invocation (Recommended)
```bash
/plan "Add OAuth authentication with JWT tokens"
/plan "Migrate from MongoDB to PostgreSQL"
/plan "Implement real-time notifications with WebSockets"
/plan "Add dark mode support to React app"
```

### Conversational Mode
```
"I want to add a payment system. How should we plan this?"
"What are the phases for migrating to microservices?"
```

## Plan Structure

A good plan includes:

### 1. Analysis Phase
- **Requirements** - What must the feature do?
- **Dependencies** - What needs to be done first?
- **Scope** - What's included/excluded?
- **Risks** - What could go wrong?

### 2. Design Phase
- **Architecture** - How should it work?
- **Tech Stack** - Which tools/libraries?
- **Data Model** - Schema or type definitions
- **Security** - Authentication, authorization, data protection

### 3. Implementation Phase
- **Task Breakdown** - Concrete implementable tasks
- **Effort Estimates** - Time for each task
- **Dependencies** - Task ordering
- **Integration Points** - Where components connect

### 4. Testing Phase
- **Unit Tests** - Test individual functions
- **Integration Tests** - Test component interactions
- **E2E Tests** - Test full workflows
- **Edge Cases** - Unusual scenarios

### 5. Documentation Phase
- **API Documentation** - Endpoint/function docs
- **Usage Guide** - How to use the feature
- **Architecture Decision Record** - Why decisions were made
- **Troubleshooting** - Common issues and solutions

## Example Plans

### Example 1: Authentication Feature

**Input:**
```
/plan "Add OAuth authentication with GitHub and Google providers"
```

**Expected Output Structure:**
```
## Feature: OAuth Authentication

### Phase 1: Setup (Days 1-2)
- [ ] Create OAuth applications on GitHub and Google
- [ ] Add env variables for OAuth secrets
- [ ] Install passport and oauth libraries
- [ ] Create auth database schema (users, sessions)

### Phase 2: OAuth Flow (Days 2-3)
- [ ] Implement /auth/github/callback endpoint
- [ ] Implement /auth/google/callback endpoint
- [ ] Generate JWT tokens after successful auth
- [ ] Implement token refresh mechanism

### Phase 3: Protected Routes (Day 3)
- [ ] Create JWT middleware
- [ ] Apply middleware to protected endpoints
- [ ] Implement role-based access control
- [ ] Add logout endpoint

### Phase 4: Testing (Day 4)
- [ ] Test GitHub OAuth flow
- [ ] Test Google OAuth flow
- [ ] Test token refresh
- [ ] Test protected endpoints
- [ ] Test logout

### Phase 5: Documentation (Day 5)
- [ ] Document OAuth setup instructions
- [ ] Document API endpoints
- [ ] Create troubleshooting guide

**Estimated**: 4-5 days
**Risk Level**: Medium
**Critical Path**: OAuth app creation → JWT implementation → Protected routes
```

### Example 2: Database Migration

**Input:**
```
/plan "Migrate from MongoDB to PostgreSQL"
```

**Expected Output Structure:**
```
## Feature: MongoDB to PostgreSQL Migration

### Phase 1: Preparation (Week 1)
- [ ] Schema design in PostgreSQL
- [ ] Create PostgreSQL database and tables
- [ ] Write migration scripts
- [ ] Set up connection pooling
- [ ] Test connections in dev environment

### Phase 2: Dual-Write (Week 2)
- [ ] Add code to write to PostgreSQL on inserts
- [ ] Add code to write to PostgreSQL on updates
- [ ] Add code to write to PostgreSQL on deletes
- [ ] Monitor dual-write consistency

### Phase 3: Data Migration (Week 2)
- [ ] Migrate existing data to PostgreSQL
- [ ] Validate data integrity
- [ ] Test queries against new database
- [ ] Identify and fix performance issues

### Phase 4: Cutover (Week 3)
- [ ] Switch read traffic to PostgreSQL
- [ ] Monitor for issues
- [ ] Keep MongoDB as fallback for 1 week
- [ ] Final MongoDB shutdown

### Phase 5: Cleanup (Week 3)
- [ ] Remove dual-write code
- [ ] Remove MongoDB connection code
- [ ] Update documentation
- [ ] Archive migration notes
```

## Pro Tips

1. **Estimate Generously** - Plans often take 1.5-2x estimated time
2. **Identify Critical Path** - What must be done before other work?
3. **Plan for Testing** - Always allocate testing time
4. **Document as You Go** - Don't leave docs for the end
5. **Review with Team** - Get feedback before implementing
6. **Check Existing Pillars** - Reference framework patterns (A, B, K, M, Q, R)

## Related Pillars

Plans should reference framework patterns:
- **Pillar A** (Types) - Define data types early
- **Pillar B** (Validation) - Add airlock boundaries
- **Pillar K** (Testing) - Plan test pyramid
- **Pillar M** (Saga) - Plan compensation logic
- **Pillar Q** (Idempotency) - Plan safe retries
- **Pillar R** (Logging) - Plan observability

## How to Refine a Plan

Once you have a plan, you can refine it:

```
"Can we parallelize frontend and backend work in this plan?"
"What's the critical path?"
"Which tasks have dependencies?"
"Can we reduce the scope to launch faster?"
"Where are the biggest risks?"
```

## Common Mistakes

❌ **Too vague** - "Build auth system" (too big)
✅ **Right size** - "Implement JWT token generation" (clear task)

❌ **No dependencies** - Tasks listed without order
✅ **Clear deps** - Task 2 depends on Task 1 completion

❌ **No testing** - Implementation only
✅ **Testing included** - Test tasks for each phase

❌ **No timeline** - "Eventually do this"
✅ **Estimated times** - "Days 2-3 for this phase"
