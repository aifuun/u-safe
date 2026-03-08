---
name: next
description: |
  Get next task from active implementation plan - shows task details, progress, and dependencies.
  TRIGGER when: user wants next task ("what's next", "next task", "what should I work on", "get next").
  DO NOT TRIGGER when: user wants to create plans (use /plan), start issues (use /start-issue), or view all tasks (use task list).
---

# Next - Task Navigator

Get the next actionable task from your current implementation plan with context and progress tracking.

## Overview

This skill navigates active plans and provides the next task to work on:

**What it does:**
1. Locates active plan in `.claude/plans/active/`
2. Identifies next incomplete task
3. Displays task details with context
4. Shows progress and dependencies
5. Provides clear next steps

**Why it's needed:**
During implementation, developers need to know "what's next" without manually reading plan files. This skill extracts the next task, explains dependencies, and tracks progress - keeping focus on the current work.

**When to use:**
- After completing a task (what's next?)
- Starting a work session (where did I leave off?)
- Checking progress (how much is left?)
- Understanding task dependencies

## Workflow

### Step 1: Create Todo List

**Initialize task navigation tracking** using TaskCreate:

```
Task #1: Locate active plan file
Task #2: Parse plan for tasks (blocked by #1)
Task #3: Identify next incomplete task (blocked by #2)
Task #4: Extract task details and dependencies (blocked by #3)
Task #5: Display task with context (blocked by #4)
Task #6: Show progress summary (blocked by #5)
```

After creating tasks, proceed with task navigation.

## Arguments

```
$ARGUMENTS = "" | "skip" | "status"
```

**Options:**
- (empty) - Show next incomplete task
- `skip` - Skip current task, show next
- `status` - Show overall plan progress

## Core Functionality

### 1. Locate Active Plan

Search for plan files in `.claude/plans/active/`:

```bash
ls .claude/plans/active/*.md
```

**Plan detection:**
- Look for files matching `issue-{number}-plan.md` or `{feature}-plan.md`
- If multiple plans, use most recently modified
- If no plans, inform user and suggest creating one

### 2. Parse Plan for Tasks

Extract tasks from plan markdown:

**Task patterns:**
```markdown
- [ ] Task description
- [x] Completed task
```

**Section detection:**
- Look for `## Tasks` or `## Implementation Phases`
- Parse checklist items
- Track completion state

### 3. Identify Next Task

Find first incomplete task:

```
For each task in plan:
  if task is unchecked (- [ ]):
    return as next task
  else:
    mark as completed and continue
```

**Special cases:**
- All tasks complete: Congratulate and suggest next steps
- No tasks found: Guide user to add tasks to plan
- Argument `skip`: Skip first incomplete, return second

### 4. Extract Task Details

Parse task metadata:

**Standard format:**
```markdown
### Phase 1: Authentication Setup
- [ ] Install passport and jsonwebtoken packages
- [ ] Create database migration for users table
- [x] Set up OAuth providers
```

**Metadata extraction:**
- Task number (sequential position)
- Phase/section name
- Task description
- Dependencies (tasks that must complete first)
- Success criteria (if specified)

### 5. Display Task

Show comprehensive task information:

```markdown
# Next Task

**Plan**: [Plan Name]
**Progress**: X/Y tasks complete (Z%)

## Task #N: [Task Description]

### What to Do
[Clear actionable steps]

### Success Criteria
- Criterion 1
- Criterion 2

### Dependencies
✅ Task #X - DONE
✅ Task #Y - DONE

### Related Tasks
→ Task #N+1: [Next task preview]

### Context
[Why this task matters, how it fits in plan]

### Estimated Effort
[If available from plan]
```

### 6. Show Progress

Track completion:

```markdown
**Progress Summary:**
- Completed: X tasks
- Current: Task #Y
- Remaining: Z tasks
- Overall: X/Y tasks (Z%)

**Recent completions:**
- ✅ Task #1: OAuth setup
- ✅ Task #2: Database schema
- ✅ Task #3: OAuth callback
```

## Output Examples

### Example 1: Next Task

**User:** "what's next?"

**Output:**
```markdown
# Next Task

**Plan**: User Authentication Feature
**Progress**: 3/8 tasks complete (37%)

## Task #4: Implement JWT Token Generation

### What to Do
1. Create `src/auth/jwt.service.ts`
2. Add JWT_SECRET to `.env`
3. Implement `generateToken(user)` method
4. Add token expiration (1 hour)
5. Write 3 unit tests

### Success Criteria
- ✅ Tokens generate on login
- ✅ Tokens decode correctly
- ✅ Expiration works
- ✅ Tests passing

### Dependencies
✅ Task #1: OAuth setup - DONE
✅ Task #2: Database schema - DONE
✅ Task #3: OAuth callback - DONE

### Related Tasks
→ Task #5: Token refresh rotation

### Estimated Effort
2-3 hours
```

### Example 2: Skip Current Task

**User:** "/next skip"

**Output:**
```markdown
# Next Task (Skipped #4)

**Plan**: User Authentication Feature
**Progress**: 3/8 tasks complete (37%)

⏭️ Skipped: Task #4 - Implement JWT Token Generation

## Task #5: Token Refresh Rotation

### What to Do
[Details for task #5...]

**Note:** Task #4 is still incomplete. Remember to complete it later.
```

### Example 3: Show Status

**User:** "/next status"

**Output:**
```markdown
# Plan Progress: User Authentication Feature

**Overall:** 3/8 tasks complete (37%)

## Completed Tasks ✅
- ✅ Task #1: Install dependencies
- ✅ Task #2: Create database schema
- ✅ Task #3: Implement OAuth callbacks

## Current Task 🔄
- 🔄 Task #4: Implement JWT token generation

## Remaining Tasks 📋
- ⬜ Task #5: Token refresh rotation
- ⬜ Task #6: Protected routes middleware
- ⬜ Task #7: Write integration tests
- ⬜ Task #8: Documentation

## Next Steps
Continue with Task #4, then proceed to Task #5.
```

### Example 4: No Active Plan

**User:** "what's next?"

**Output:**
```markdown
# No Active Plan Found

No implementation plan found in `.claude/plans/active/`.

## Options

1. **Start an issue** (recommended):
   ```
   /start-issue #23
   ```
   Auto-creates plan from GitHub issue.

2. **Create a plan manually**:
   ```
   /plan "implement user authentication"
   ```
   Generates detailed implementation plan.

3. **Check archived plans**:
   Plans might be in `.claude/plans/archive/` if work is complete.
```

### Example 5: All Tasks Complete

**User:** "what's next?"

**Output:**
```markdown
# All Tasks Complete! 🎉

**Plan**: User Authentication Feature
**Progress**: 8/8 tasks complete (100%)

## Completed Work ✅
- ✅ Task #1: Install dependencies
- ✅ Task #2: Create database schema
- ✅ Task #3: Implement OAuth callbacks
- ✅ Task #4: Implement JWT token generation
- ✅ Task #5: Token refresh rotation
- ✅ Task #6: Protected routes middleware
- ✅ Task #7: Write integration tests
- ✅ Task #8: Documentation

## Next Steps

1. **Review your work**:
   ```
   /review
   ```

2. **Finish the issue** (if working from GitHub issue):
   ```
   /finish-issue #23
   ```

3. **Start next feature**:
   Check your backlog for next priority.

Great work! This plan is complete.
```

## Integration

**With /start-issue:**
```
/start-issue #23     # Creates plan from issue
/next                # Get first task from generated plan
```

**With /plan:**
```
/plan "new feature"  # Create manual plan
/next                # Get first task
```

**With /finish-issue:**
```
/next                # Work through tasks
# ... complete all tasks ...
/next                # Shows "All complete"
/finish-issue #23    # Finish and close issue
```

## Task Management

**After each navigation step**, update progress:

```
Plan located → Update Task #1
Plan parsed → Update Task #2
Next task identified → Update Task #3
Details extracted → Update Task #4
Task displayed → Update Task #5
Progress shown → Update Task #6
```

Provides visibility into navigation process.

## Final Verification

**Before showing task**, verify:

```
- [ ] All 6 navigation tasks completed
- [ ] Plan file located
- [ ] Tasks parsed correctly
- [ ] Next incomplete task identified
- [ ] Task details complete
- [ ] Progress calculated
- [ ] Output formatted clearly
```

Missing items indicate incomplete navigation.

## Best Practices

1. **Check progress regularly** - `/next status` shows overview
2. **Skip strategically** - Use `/next skip` for blocking tasks
3. **Update plan** - Mark tasks complete as you finish them
4. **Stay focused** - One task at a time
5. **Context matters** - Read dependencies before starting

## Related Skills

- **/start-issue** - Creates plan from GitHub issue
- **/plan** - Manual plan creation
- **/finish-issue** - Completes issue workflow

---

**Version:** 2.1.0
**Pattern:** Tool-Reference (guides task navigation)
**Compliance:** ADR-001 Section 4 ✅
