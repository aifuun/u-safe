---
name: create-issue
version: "2.0.0"
last-updated: "2026-03-28"
description: |
  Create GitHub issues with intelligent size validation and recommendations.

  TRIGGER when:
  - User wants to create a new issue ("create issue", "new issue")
  - User mentions issue templates ("use bug template", "issue template")
  - User asks about issue size ("estimate issue size", "check if issue too large")
  - User wants batch issue creation ("create multiple issues", "batch create")
  - User mentions deduplication ("check for duplicates", "similar issues exist?")

  DO NOT TRIGGER when:
  - Viewing existing issues (use gh issue view)
  - Editing/updating issues (use gh issue edit)
  - Closing issues (use gh issue close)
  - Discussing issues conceptually without creating
  - Working on existing issues (use /start-issue, /work-issue)
category: project-management
allowed-tools:
  - Bash
  - Read
  - Write
---

# Create Issue - GitHub Issue Creation

Create GitHub issues using `gh` CLI with optional templates and labels.

## Overview

This skill provides a simple workflow for creating GitHub issues:

**What it does:**
1. Checks and creates labels if needed
2. Creates issue with structured body using heredoc
3. Suggests issue size validation

**When to use:**
- Need to create a new GitHub issue
- Want to use standardized issue templates
- Need label management before issue creation

## AI Execution Instructions

When executing `/create-issue`, AI MUST follow these steps:

### Step 1: Check and Create Labels

**Check if labels exist:**
```bash
# List current labels
gh label list

# Create label if missing
gh label create "enhancement" --description "New feature or request" --color "a2eeef"
gh label create "bug" --description "Something isn't working" --color "d73a4a"
gh label create "documentation" --description "Documentation improvements" --color "0075ca"
```

**Common labels to check:**
- bug (red: d73a4a)
- enhancement (teal: a2eeef)
- documentation (blue: 0075ca)
- good first issue (purple: 7057ff)
- help wanted (green: 008672)

### Step 2: Create Issue with Heredoc

**Use heredoc for issue body to handle multiline content:**

```bash
gh issue create --title "Issue title here" --body "$(cat <<'EOF'
## Background

[Describe the context and motivation]

## Goal

[What should be achieved]

## Tasks

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
EOF
)" --label "enhancement"
```

**With labels:**
```bash
gh issue create --title "Fix login button" --body "$(cat <<'EOF'
## Background

Login button is misaligned on mobile devices.

## Steps to Reproduce

1. Open app on mobile
2. Navigate to login page
3. Observe button alignment

## Expected Behavior

Button should be centered.

## Actual Behavior

Button is aligned to the left.

## Tasks

- [ ] Fix CSS alignment
- [ ] Test on iOS
- [ ] Test on Android

## Acceptance Criteria

- [ ] Button centered on all mobile devices
- [ ] No layout issues on desktop
EOF
)" --label "bug,P0"
```

### Step 3: Size Validation Suggestions

**After creating issue, suggest validation:**

```markdown
✅ Issue created: #123

Size Check:
- Tasks: {count}
- Estimated time: {estimate}

Recommendations:
- ✅ IDEAL: 3-5 tasks, 2-3 hours
- ⚠️ LARGE: 6-8 tasks, 3-4 hours (consider splitting)
- 🚫 TOO LARGE: >8 tasks, >4 hours (must split)

Current: {status}
```

## Issue Body Templates

### Bug Template

```markdown
## Background

[What is the bug? When does it occur?]

## Steps to Reproduce

1. [First step]
2. [Second step]
3. [Observe the issue]

## Expected Behavior

[What should happen]

## Actual Behavior

[What actually happens]

## Environment

- OS: [e.g., macOS 14.0]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 1.2.3]

## Tasks

- [ ] Investigate root cause
- [ ] Implement fix
- [ ] Add regression test

## Acceptance Criteria

- [ ] Bug no longer occurs
- [ ] Tests pass
- [ ] No side effects
```

### Feature Template

```markdown
## Background

[Why is this feature needed? What problem does it solve?]

## Goal

[What should this feature accomplish?]

## User Story

As a [user type],
I want to [action],
So that [benefit].

## Tasks

- [ ] Design implementation approach
- [ ] Implement core functionality
- [ ] Add tests
- [ ] Update documentation

## Acceptance Criteria

- [ ] Feature works as described
- [ ] Tests cover main scenarios
- [ ] Documentation updated
```

### Enhancement Template

```markdown
## Background

[What needs improvement? Why?]

## Current State

[How does it work now?]

## Proposed Enhancement

[How should it work after enhancement?]

## Impact

[What will improve? Who benefits?]

## Tasks

- [ ] Implement enhancement
- [ ] Update tests
- [ ] Update documentation

## Acceptance Criteria

- [ ] Enhancement works as expected
- [ ] No regression
- [ ] Performance not degraded
```

## Best Practices

### Issue Size Guidelines

**Ideal size:**
- 3-5 tasks
- 2-3 hours to complete
- < 300 lines of code changed
- Single PR

**Warning threshold:**
- 6-8 tasks
- 3-4 hours to complete
- Consider splitting into smaller issues

**Hard limit:**
- > 8 tasks
- > 4 hours to complete
- Must split into multiple issues

### Content Requirements

**Every issue should have:**
- Clear background/context
- Specific goal statement
- Concrete tasks with checkboxes
- Measurable acceptance criteria

**Avoid:**
- Vague descriptions ("improve performance")
- No tasks or acceptance criteria
- Mixing multiple unrelated features
- Issues that take > 1 week

## Examples

### Example 1: Simple Bug Fix

```bash
gh issue create --title "Fix mobile login button alignment" --body "$(cat <<'EOF'
## Background

Login button is misaligned on mobile devices (<768px).

## Steps to Reproduce

1. Open app on mobile device
2. Navigate to /login
3. Observe button position

## Expected vs Actual

Expected: Button centered
Actual: Button aligned left

## Tasks

- [ ] Update CSS for mobile breakpoint
- [ ] Test on iOS Safari
- [ ] Test on Android Chrome

## Acceptance Criteria

- [ ] Button centered on mobile
- [ ] No desktop regression
EOF
)" --label "bug,P1"
```

### Example 2: Feature Request

```bash
gh issue create --title "Add dark mode support" --body "$(cat <<'EOF'
## Background

Users have requested dark mode for better nighttime usage.

## Goal

Implement system-wide dark mode toggle.

## Tasks

- [ ] Design dark mode color palette
- [ ] Implement theme switcher
- [ ] Add user preference persistence
- [ ] Test all components

## Acceptance Criteria

- [ ] Dark mode toggle in settings
- [ ] Preference persists across sessions
- [ ] All components support dark mode
EOF
)" --label "enhancement"
```

## Related Skills

- **/start-issue** - Creates branch and plan after issue exists
- **/auto-solve-issue** - Complete workflow from issue to merge
- **/finish-issue** - Closes issue after completion

---

**Version:** 2.0.0
**Pattern:** Tool-Reference (guides gh CLI usage)
**Last Updated:** 2026-03-28
**Changelog:**
- v2.0.0: Simplified to gh CLI instruction list (removed unimplemented features)
- v1.0.0: Initial complex version with unimplemented features
