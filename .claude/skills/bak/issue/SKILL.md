---
name: issue
description: |
  Manage GitHub issues - list, pick, create, close, and link to plans.
  GitHub integration for task management.
disable-model-invocation: true
user-invocable: true
argument-hint: "[action] [number]"
allowed-tools: Bash(gh *), Bash(git *), Read
context: fork
agent: general-purpose
---

# Issue Manager

Manage GitHub issues and link to plans.

## Task

Handle issues:
1. **List** - Show open issues
2. **Pick** - Select an issue to work on
3. **Create** - File a new issue
4. **Link** - Connect issue to implementation plan
5. **Close** - Mark as done

## Commands

**Without arguments:**
```
/issue list              # Show open issues
/issue create            # File new issue
```

**With arguments** (using $ARGUMENTS):
```bash
/issue pick #42          # Start work on issue
/issue close #42         # Mark done and close
/issue link #42 plan-id  # Connect issue to plan
```

Argument format: `[action] [issue-number]` or `[action] [issue-number] [plan-id]`

Supported actions:
- `pick [number]` - Start work on issue, create branch
- `close [number]` - Mark issue done and close
- `link [number] [plan-id]` - Connect issue to plan
- `list` - Show open issues (no argument needed)

## Workflow

1. **Pick Issue**: `issue pick #42`
   - Creates feature branch
   - Links to issue
   - Updates plan

2. **Work**: Implement the issue

3. **Close**: `issue close #42`
   - Runs final tests
   - Closes issue
   - Creates PR summary

## Integration with Plans

Issues ↔ Plans ↔ Implementation

```
Issue #42 (GitHub)
    ↓
Plan: User Authentication
    ├── Task 1: Setup
    ├── Task 2: OAuth
    └── Task 3: Testing
    ↓
Implementation (code)
    ↓
Pull Request
    ↓
Issue closed
```

---

Connects:
- GitHub issues to work
- Planning to implementation
- Issues to Pull Requests
