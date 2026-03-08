---
name: next
description: |
  Get the next task from your current implementation plan.
  Provides task details, acceptance criteria, and progress tracking.
argument-hint: "[skip]"
allowed-tools: Read, Glob, Grep
---

# Task Navigator

Get your next task and understand what needs to be done.

## Task

Navigate current plans and provide next actionable task.

## How It Works

1. **Read current plan** - Look for plan files in `.claude/plans/active/`
2. **Find next task** - Identify incomplete tasks (not checked off)
3. **Explain task** - What it is, why it matters, how to complete
4. **Show progress** - How many tasks done, how many remaining
5. **Provide context** - Dependencies, related tasks, success criteria

## Output

```markdown
# Next Task

**Plan**: User Authentication Feature
**Progress**: 3/8 tasks complete (37%)

## Current Task: #4 - Implement JWT Token Generation

### Description
Generate JWT tokens on successful OAuth login. Tokens should:
- Encode user ID and email
- Have 1-hour expiration
- Include refresh token for renewal

### What to do
1. Create `src/auth/jwt.ts` with token generation
2. Add to `.env`: JWT_SECRET
3. Call from OAuth callback handler

### Success Criteria
- ✅ JWT tokens generate on login
- ✅ Tokens decode correctly
- ✅ Token expiration works
- ✅ 3 unit tests passing

### Effort Estimate
2-3 hours

### Dependencies
✅ Task #1 (OAuth setup) - DONE
✅ Task #2 (Database schema) - DONE
✅ Task #3 (OAuth callback) - DONE

### Related Tasks
→ Task #5: Token Refresh Rotation (depends on this)

### Next Steps
1. Create jwt.ts file
2. Write token generation function
3. Add unit tests
4. Check this task as complete
```

## Quick Navigation

**Show next task (current or skip):**
```bash
/next              - Show next task
/next skip         - Skip current task, show next
```

If argument is provided: **$ARGUMENTS**

Options for `$ARGUMENTS`:
- `skip` - Skip current task and show the next one
- (empty or no arg) - Show current next task

**Show overall progress:**
```bash
/next status       - Show overall plan progress
```

---

This skill helps:
- Stay focused on current work
- Understand task relationships
- Track progress
- Know what's blocking what
