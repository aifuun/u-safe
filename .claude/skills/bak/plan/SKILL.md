---
name: plan
description: |
  Create or update implementation plans for features, MVPs, and milestones.
  Strategic decomposition of features into actionable tasks.
argument-hint: "[feature-description]"
allowed-tools: Read, Glob, Grep, Bash(git *)
---

# Strategic Planner

Create implementation plans by analyzing project scope, architecture, and dependencies.

## Task

Generate detailed implementation plans that decompose features into:
1. **Analysis Phase** - Understand requirements and dependencies
2. **Design Phase** - Architectural decisions
3. **Implementation Phase** - Concrete tasks
4. **Testing Phase** - Verification strategy
5. **Documentation Phase** - Knowledge capture

## How It Works

### Input: Feature Description

If invoked with an argument, use that feature description:
```
/plan "Add user authentication with OAuth and JWT tokens"
```

The feature request is: **$ARGUMENTS**

Or ask the user to describe the feature they want to plan if no argument provided.

### Analysis
1. **Requirements** - What must it do?
2. **Scope** - What's included/excluded?
3. **Dependencies** - What's needed first?
4. **Risks** - What could go wrong?
5. **Architecture** - How should it work?

### Output: Implementation Plan
```
## Feature: User Authentication with OAuth + JWT

### Phase 1: Setup (Day 1)
- [ ] Install auth libraries (passport, jwt)
- [ ] Configure OAuth provider (GitHub/Google)
- [ ] Create auth database schema

### Phase 2: OAuth Flow (Days 2-3)
- [ ] Implement OAuth callback handler
- [ ] Generate JWT tokens on login
- [ ] Add refresh token rotation

### Phase 3: Protected Routes (Day 3)
- [ ] Add JWT middleware
- [ ] Protect API endpoints
- [ ] Add role-based access

### Phase 4: Testing (Day 4)
- [ ] Test OAuth login flow
- [ ] Test token refresh
- [ ] Test authorization on endpoints

Estimated: 3-4 days
Risk Level: Medium
Dependencies: None
```

## Smart Planning

Considers:
- **Project context** (tech stack, architecture)
- **Team size** (solo, team, large)
- **Timeline** (urgent, normal, flexible)
- **Framework patterns** (which Pillars apply?)
- **Existing code** (build on what's there)

## Usage

**With argument (feature description):**
```bash
/plan "Add user authentication with OAuth and JWT"
/plan "Implement real-time notifications"
/plan "Migrate database to PostgreSQL"
/plan "Add dark mode support"
```

**Without argument:**
- Ask user: "What feature would you like to plan?"
- Then generate the plan based on their response

**Refine existing plan:**
```
"Can we parallelize the frontend and backend work?"
"What's the critical path?"
```

---

Output should be:
- ✅ Detailed (concrete tasks)
- ✅ Realistic (considers dependencies)
- ✅ Actionable (clear what to do next)
- ✅ Risk-aware (highlights concerns)
