# Skill Name - One-line Description

> Brief overview explaining what this skill does and why it's needed

## Overview

**What it does:**
1. Primary function 1
2. Primary function 2
3. Primary function 3

**Why it's needed:**
[Explain the problem this skill solves and the value it provides]

**When to use:**
- Scenario 1
- Scenario 2
- Scenario 3

**TRIGGER when** (for AI recognition):
- User phrase 1
- User action 1
- Context 1

**DO NOT TRIGGER when**:
- Alternative scenario 1
- Use different skill instead: /other-skill

## Arguments

```bash
/skill-name [required-arg] [optional-arg] [options]
```

**Common usage:**
```bash
/skill-name basic-example
/skill-name advanced-example --option value
/skill-name --dry-run              # Preview mode
```

**Options:**
- `[required-arg]` - Description of required argument
- `[optional-arg]` - Description (default: value)
- `--option` - Description of option flag
- `--dry-run` - Preview actions without executing
- `--force` - Skip safety checks (use cautiously)

## AI Execution Instructions

**CRITICAL: [Most important thing AI must remember]**

When executing `/skill-name`, AI MUST follow this pattern:

### Step 1: [First Major Step]

**[What to do]:**
```python
# AI-EXECUTABLE - Code AI can directly execute
import sys
sys.path.insert(0, '.claude/skills/_scripts')

from framework.module import function

result = function()
```

**[Explanation of why this step matters]**

### Step 2: [Second Major Step]

**[What to do]:**
```bash
# Execute commands
command --with-args
```

**Edge cases:**
- Case 1: How to handle
- Case 2: How to handle

### Step 3: [Third Major Step]

**[What to do]:**

**Validation:**
```bash
# Verify step completed successfully
check_command
```

## Workflow Steps

Copy this checklist to track progress:

```
Task Progress:
- [ ] Step 1: [Description]
- [ ] Step 2: [Description]
- [ ] Step 3: [Description]
- [ ] Step 4: [Description]
- [ ] Step 5: [Description]
```

Execute these steps in sequence:

### Step 1: [Detailed Step Name]

**Purpose**: [Why this step exists]

**Process:**
1. Sub-step 1
2. Sub-step 2
3. Sub-step 3

**Example:**
```bash
# EXAMPLE-ONLY - Reference code, not for direct execution
example_command --example-flag
```

**Validation:**
- [ ] Checkpoint 1
- [ ] Checkpoint 2

### Step 2: [Next Step]

[Continue pattern for all workflow steps...]

## Error Handling

**[Common Error 1]:**
```
❌ Error message

Cause: [Why it happens]

Fix:
1. Solution step 1
2. Solution step 2
```

**[Common Error 2]:**
```
⚠️ Warning message

Options:
1. Option 1 - [Description]
2. Option 2 - [Description]
```

## Examples

### Example 1: [Common Use Case]

**User says:**
> "[Natural language request]"

**What happens:**
1. Step 1 result
2. Step 2 result
3. Final outcome

**Time:** ~X seconds

### Example 2: [Another Use Case]

**User says:**
> "[Different request]"

**Workflow:**
1. Detection
2. Action
3. Result

**Time:** ~Y minutes

## Integration

**Workflow sequence:**
```
/prerequisite-skill → /skill-name → /follow-up-skill
```

**Related files:**
- Input: `path/to/input`
- Output: `path/to/output`
- Config: `path/to/config`

**Pairs with:**
- `/related-skill-1` - [How they work together]
- `/related-skill-2` - [Relationship]

## Best Practices

1. **Do this** - Explanation
2. **Avoid that** - Why it's problematic
3. **Prefer this over that** - Better approach
4. **Always validate** - What to check
5. **Never skip** - Critical step

## Performance

- **Average time:** X seconds
- **Fast path:** <X seconds (when Y condition)
- **Slow path:** X-Y minutes (when Z condition)

**Optimization tips:**
- Tip 1
- Tip 2

## Shared Logic Usage

**This skill uses these shared modules:**

```python
# SHARED-LOGIC - Common functions from _scripts/
from _scripts.utils.fs import validate_path
from _scripts.utils.json_handler import read_json, write_json
from _scripts.framework.issue_detector import detect_issue_number
```

**If code appears in 3+ skills**, extract to `_scripts/`:
- `_scripts/utils/`: General utilities
- `_scripts/framework/`: Core framework functions
- `_scripts/git/`: Git operations

## Final Verification

**Critical checks before completion:**

```
- [ ] All steps completed
- [ ] Output files created
- [ ] No unexpected changes
- [ ] User informed of results
```

Missing items indicate incomplete execution.

## Workflow Skills Requirements

This is a **[workflow/utility/analysis] skill** and must follow the standard pattern:

1. **TaskCreate** at start - Create todo list for progress tracking (if workflow skill)
2. **TaskUpdate** during execution - Mark tasks in_progress → completed
3. **Verification checklist** - Final validation before completion

**See**: [WORKFLOW_PATTERNS.md](./WORKFLOW_PATTERNS.md) for complete implementation guide

## Related Skills

- **/prerequisite** - Run before this skill
- **/follow-up** - Run after this skill
- **/alternative** - Different approach to same goal
- **/complement** - Use together with this skill

---

**Version:** 1.0.0
**Pattern:** [Tool-Reference/Workflow Orchestrator/Analysis/Meta-Skill]
**Compliance:** ADR-001 ✅ | ADR-014 ✅ | WORKFLOW_PATTERNS ✅
**Last Updated:** YYYY-MM-DD
**Changelog:**
- v1.0.0: Initial release

**Implementation Checklist** (Delete before publishing):
- [ ] Replace all placeholders ([Skill Name], [Description], etc.)
- [ ] Add concrete examples based on actual use cases
- [ ] Define clear TRIGGER conditions
- [ ] Specify all arguments and options
- [ ] Document error handling for known issues
- [ ] Add integration points with other skills
- [ ] Verify all code blocks are properly tagged (AI-EXECUTABLE/EXAMPLE-ONLY/SHARED-LOGIC)
- [ ] Ensure SKILL.md <500 lines (split to REFERENCE.md if needed)
- [ ] Add version number and compliance badges
- [ ] Test skill works as documented
