# Workflow Skills Pattern

**Version**: 1.0.0
**Last Updated**: 2026-03-10
**Applies to**: Multi-step skills (start-issue, finish-issue, sync, execute-plan)

---

## What are Workflow Skills?

**Workflow skills** are multi-step skills that guide users through complex processes:
- **start-issue** - Begin GitHub issue workflow
- **eval-plan** - Evaluate implementation plan before execution
- **execute-plan** - Execute implementation plan step-by-step
- **finish-issue** - Complete issue (commit + PR + merge)
- **sync** - Sync branch with main
- **work-issue** - Meta-workflow orchestrating all 5 above skills

These skills involve multiple sequential operations and benefit from progress tracking.

---

## Required Pattern

All workflow skills **MUST** implement this pattern:

### 1. TaskCreate at Start

Create a todo list at the beginning to track progress:

```python
# Example from start-issue
tasks = [
    "Validate environment",
    "Fetch issue from GitHub",
    "Create feature branch",
    "Generate implementation plan",
    "Sync with main",
    "Report success"
]

for task in tasks:
    # Use TaskCreate tool
    create_task(subject=task, description=details, activeForm=f"{verb}ing...")
```

**Why**:
- Users can see overall progress
- Clear understanding of remaining steps
- Better user experience

### 2. TaskUpdate During Execution

Update task status as each step completes:

```python
# Start working on a task
update_task(task_id=1, status="in_progress")

# ... do the work ...

# Mark as complete
update_task(task_id=1, status="completed")

# Move to next task
update_task(task_id=2, status="in_progress")
```

**Why**:
- Real-time progress visibility
- Users know current step
- Claude Code UI shows active task

### 3. Verification Checklist

Include a final verification checklist:

```markdown
## Final Verification

Before declaring success, verify:

```
- [ ] Environment validated
- [ ] Branch created and pushed
- [ ] Plan generated
- [ ] All tasks completed
- [ ] Working tree clean
```

Missing items indicate incomplete execution.
```

**Why**:
- Ensures nothing was skipped
- Provides confidence in completion
- Easy to debug if something failed

### 4. Copyable Workflow Checklist

**NEW REQUIREMENT**: Provide a copyable checklist that Claude can include in responses to show progress to users.

**Location**: Place after "## Workflow Steps" heading, before detailed step descriptions.

**Format**:
```markdown
## Workflow Steps

Copy this checklist to track progress:

\```
Task Progress:
- [ ] Step 1: {Short description}
- [ ] Step 2: {Short description}
- [ ] Step 3: {Short description}
...
\```

Execute these steps in sequence:

### Step 1: {Detailed Heading}
{Detailed explanation}
```

**Example** (from start-issue):
```markdown
Copy this checklist to track progress:

\```
Task Progress:
- [ ] Step 1: Validate environment
- [ ] Step 2: Fetch or create issue
- [ ] Step 3: Create feature branch
- [ ] Step 4: Generate implementation plan
- [ ] Step 5: Create todo list from plan
- [ ] Step 6: Sync and setup
- [ ] Step 7: Report success
\```
```

**Why**:
- Users see progress in Claude's response (not just UI)
- Complies with [Anthropic best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#use-workflows-for-complex-tasks)
- Provides clear visual feedback during long workflows
- Easy to track if a step was skipped

**Special cases**:
- **Multiple workflows** (e.g., sync): Provide separate checklists for each workflow variant
- **Dynamic tasks** (e.g., execute-plan): Show high-level phases + note that specific tasks come from plan

---

## Feedback Loops

### Pattern: Validate → Fix → Repeat

**Core Principle**: Anthropic best practices emphasize iterative validation loops to improve output quality. Always validate, fix errors, and repeat until valid.

> "Run validator → fix errors → repeat. This pattern greatly improves output quality."
> — Anthropic Agent Best Practices

Feedback loops are essential for workflow skills to ensure quality and correctness before proceeding to the next step.

### Implementation Patterns

**Example 1: Tool-reference validation**

Validate against reference documentation:

1. Generate plan or output
2. Review against STYLE_GUIDE.md or reference docs
3. If issues found: note them, revise output, review again
4. Only proceed when validation passes

**Use case**: Validating generated plans against coding standards, style guides, or architectural rules.

**Example 2: Script-based validation**

Validate using automated scripts:

1. Make changes (code, config, documentation)
2. Run automated validator (e.g., `./validate.py`, linters, tests)
3. If validation fails: fix errors, validate again
4. Only proceed when all checks pass

**Use case**: Running linters, type checkers, unit tests, or custom validation scripts.

**Example 3: Multi-stage validation**

Combine multiple validation layers:

1. Make changes
2. Run quick checks (syntax, formatting)
3. If fails: fix and retry
4. Run comprehensive checks (tests, integration)
5. If fails: fix and retry from step 2
6. Only proceed when all validations pass

**Use case**: Complex workflows requiring multiple validation stages (e.g., code generation → lint → type check → test).

### Why This Matters

| Aspect | With Feedback Loops | Without |
|--------|-------------------|---------|
| Quality | ✅ High - validated output | ❌ Low - errors slip through |
| Confidence | ✅ Know output is correct | ❌ Uncertain quality |
| Debugging | ✅ Errors caught early | ❌ Errors found later |
| Compliance | ✅ Standards enforced | ❌ Inconsistent results |
| User Trust | ✅ Reliable workflows | ❌ Unpredictable outcomes |

### Integration with Workflow Skills

Feedback loops should be integrated into workflow skills at critical validation points:

```python
# Example: start-issue with plan validation
def generate_plan():
    """Generate plan with feedback loop."""
    plan = create_initial_plan()

    while True:
        # Validate against style guide
        issues = validate_plan(plan, style_guide="STYLE_GUIDE.md")

        if not issues:
            print("✅ Plan validated successfully")
            break

        print(f"⚠️ Found {len(issues)} issues, revising...")
        plan = revise_plan(plan, issues)

    return plan
```

**Best practices**:
- ✅ **Validate before proceeding** - Don't move to next step with errors
- ✅ **Show validation results** - Display what passed/failed
- ✅ **Limit iterations** - Add max retry limit to prevent infinite loops
- ✅ **Clear error messages** - Help user understand what needs fixing
- ✅ **Track validation in tasks** - Use TaskUpdate to show validation progress

---

## Benefits

This pattern provides:

### For Users
- ✅ **Progress visibility** - Know what's happening at all times
- ✅ **Clear expectations** - See remaining steps
- ✅ **Confidence** - Verification checklist ensures completion
- ✅ **Debugging** - Easy to see where failures occurred

### For Developers
- ✅ **Consistent UX** - All workflow skills behave similarly
- ✅ **Task dependencies** - Express blockedBy relationships
- ✅ **Progress tracking** - Built-in status management
- ✅ **Reusability** - Common pattern across skills

---

## Architecture Principle

**Core Principle**: Workflow skills should be **AI-orchestrated operations**, not monolithic scripts.

**Note**: This principle aligns with the **3-layer skill architecture** (see [ARCHITECTURE.md](ARCHITECTURE.md)):
- **Layer 1 (Meta-Skills)**: Workflow orchestrators like `/work-issue` that coordinate multiple Atomic skills
- **Layer 2 (Atomic Skills)**: Individual workflow skills like `/start-issue`, `/finish-issue` that perform single operations
- **Layer 3 (Python Libraries)**: Reusable code imported by Atomic skills

**See**: [ADR-006](../../docs/ADRs/006-skill-composition-pattern.md) for skill composition patterns

```
┌─────────────────────────────────┐
│  SKILL.md (AI Instructions)     │  ← Workflow definition
│  - TaskCreate (show plan)        │
│  - Run atomic operation A        │
│  - TaskUpdate (mark progress)    │
│  - Run atomic operation B        │
│  - Verify result (checklist)     │
└─────────────────────────────────┘
           ↓ Claude orchestrates
┌─────────────────────────────────┐
│  Python Scripts or Tools        │  ← Atomic operations
│  - collect_data.py / git status │
│  - validate.py / gh issue view  │
│  - generate.py / bash commands  │
└─────────────────────────────────┘
```

### Pattern Comparison

**✅ AI-Orchestrated (Correct)**:
- SKILL.md guides Claude step-by-step
- Each step is atomic (single responsibility)
- TaskUpdate shows real-time progress
- User can interrupt/resume at any step
- Example: `/start-issue` - Claude runs `gh issue view #123` → TaskUpdate → `git checkout -b` → TaskUpdate

**❌ Monolithic Script (Anti-pattern)**:
- One big script does everything internally
- AI just launches script and waits
- No progress visibility (black box)
- Cannot interrupt mid-process
- Example: `./do_everything.py` - runs 5 steps internally, no TaskUpdate, user waits 30 seconds

### Why This Matters

| Aspect | AI Orchestrated | Monolithic |
|--------|----------------|------------|
| Progress | ✅ Real-time | ❌ Black box |
| Control | ✅ Claude decides | ❌ Script controls |
| Debug | ✅ Know failed step | ❌ Generic error |
| Interrupt | ✅ Pause/resume | ❌ All-or-nothing |
| Reuse | ✅ Independent ops | ❌ Coupled code |
| Test | ✅ Test per operation | ❌ Test entire flow |
| UX | ✅ Progress bar | ❌ Long wait |

### Implementation Guidelines

**1. Break into atomic operations**: One responsibility per script/command
**2. Let AI orchestrate**: SKILL.md guides Claude, not Python
**3. Use TaskCreate/TaskUpdate**: Show plan upfront, update progress
**4. Scripts are stateless tools**: Input → Processing → Output (no internal workflow)
**5. Choose appropriate tools**:
   - Python: Complex processing, reusable logic, type safety
   - Built-in (git/gh/bash): Simple operations, file I/O, standard commands
   - **Layer 3 libraries**: Shared code (e.g., `worktree_manager.py`, `issue_detector.py`) - see [ARCHITECTURE.md](ARCHITECTURE.md)

**Example**:
```markdown
# Tool-Reference: start-issue (no Python needed)
Step 1: gh issue view #123 → TaskUpdate
Step 2: git checkout -b feature/123 → TaskUpdate

# With Python: overview (complex processing)
Step 1: ./collect_git.py > git.json → TaskUpdate
Step 2: ./analyze.py git.json > report.html → TaskUpdate
```

---

## Implementation Example

### Complete Workflow Skill Structure

```
start-issue/
├── SKILL.md              # Documents the workflow
└── scripts/
    └── start_issue.py    # Implements the pattern
```

### Python Implementation Pattern

```python
#!/usr/bin/env python3
"""Example workflow skill implementing the pattern."""

import sys
from pathlib import Path

# Add shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent / '_scripts'))

from format_utils import success, error, info, header

def create_tasks() -> list[str]:
    """
    Create todo list for workflow tracking.

    Returns:
        List of task IDs created
    """
    tasks = [
        ("Step 1: Validate", "Check environment", "Validating"),
        ("Step 2: Fetch", "Get data from source", "Fetching"),
        ("Step 3: Process", "Process the data", "Processing"),
        ("Step 4: Verify", "Run verification", "Verifying"),
    ]

    task_ids = []
    for subject, description, active_form in tasks:
        # Use Claude Code's TaskCreate
        task_id = task_create(
            subject=subject,
            description=description,
            activeForm=active_form
        )
        task_ids.append(task_id)

    return task_ids

def execute_workflow(task_ids: list[str]) -> int:
    """
    Execute workflow with progress tracking.

    Args:
        task_ids: List of task IDs to track

    Returns:
        Exit code (0 = success)
    """
    for i, task_id in enumerate(task_ids):
        try:
            # Mark task as in progress
            task_update(task_id, status="in_progress")

            # Do the actual work
            result = perform_step(i + 1)

            if not result:
                print(error(f"❌ Step {i+1} failed"))
                return 1

            # Mark as completed
            task_update(task_id, status="completed")
            print(success(f"✅ Step {i+1} completed"))

        except Exception as e:
            print(error(f"❌ Error in step {i+1}: {e}"))
            return 1

    return 0

def perform_step(step_num: int) -> bool:
    """
    Perform a single workflow step.

    Args:
        step_num: Step number to execute

    Returns:
        True if successful, False otherwise
    """
    # Actual implementation here
    print(info(f"Executing step {step_num}..."))
    return True

def main() -> int:
    """Main entry point."""
    print(header("Starting Workflow"))

    # Step 1: Create tasks
    task_ids = create_tasks()
    print(info(f"Created {len(task_ids)} tasks"))

    # Step 2: Execute workflow with tracking
    result = execute_workflow(task_ids)

    # Step 3: Verify completion
    if result == 0:
        print(success("✅ Workflow completed successfully"))
    else:
        print(error("❌ Workflow failed"))

    return result

if __name__ == '__main__':
    sys.exit(main())
```

---

## Compliance Check

### Is Your Skill a Workflow Skill?

Ask these questions:

1. **Multiple steps?** - Does it involve 3+ sequential operations?
2. **Takes time?** - Does it run for >30 seconds?
3. **Complex process?** - Would users benefit from seeing progress?

If **YES** to 2+ questions → Use workflow pattern (including copyable checklist)

If **NO** to all → Simple skill, pattern not required

**Required elements for workflow skills:**
1. ✅ TaskCreate at start
2. ✅ TaskUpdate during execution
3. ✅ Verification checklist at end
4. ✅ **Copyable workflow checklist** in SKILL.md (NEW)

### Examples

| Skill | Workflow? | Why |
|-------|-----------|-----|
| start-issue | ✅ Yes | 6-7 steps, ~30 sec, complex |
| eval-plan | ❌ No | Single analysis step (30-60 sec but atomic) |
| execute-plan | ✅ Yes | Multiple phases, long-running |
| finish-issue | ✅ Yes | 7-8 steps, ~2 min, complex |
| sync | ✅ Yes | 5-7 steps, ~1 min, complex |
| work-issue | ✅ Yes | 7 phases with checkpoints, orchestrates 5 skills |
| plan | ❌ No | Single analysis step |
| next | ❌ No | Quick file read |
| adr | ❌ No | Simple file operations |

---

## ADR References

This pattern is defined in:
- **[ADR-001](../../docs/ADRs/001-official-skill-patterns.md)** - Official skill patterns
- **[ADR-006](../../docs/ADRs/006-skill-composition-pattern.md)** - Skill composition pattern (3-layer architecture)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 3-layer architecture implementation guide
- **[skills/README.md](README.md)** - Quick overview in Core Policies section

---

## When to Update This Document

Update when:
- ✅ Adding new workflow skills
- ✅ Pattern requirements change
- ✅ New benefits or use cases discovered
- ✅ Implementation examples improve

---

## Questions?

**For workflow skill developers**:
- See ADR-001 for complete requirements
- Check existing workflow skills (start-issue, finish-issue) for examples
- Ask in team chat if unsure whether your skill should use this pattern

---

## Distribution

This document travels with skills when synced via `/update-skills`:

```bash
# When syncing skills, WORKFLOW_PATTERNS.md is automatically copied
cd ~/dev/ai-dev
/update-skills ../my-app

# What gets synced:
✅ .claude/skills/README.md                  # Navigation hub
✅ .claude/skills/WORKFLOW_PATTERNS.md       # This file
✅ .claude/skills/PYTHON_GUIDE.md            # Development guide
✅ .claude/skills/_scripts/                   # Utilities
✅ .claude/skills/{skill-name}/              # Individual skills
```

**Why this matters:**
- Workflow pattern requirements travel with skills to other projects
- No knowledge isolation - pattern docs are always available
- Single source of truth maintained across projects

**See**: [update-skills/SKILL.md](update-skills/SKILL.md) for sync details

---

**Status**: Canonical Reference 📚
**Ownership**: Framework Team
**Feedback**: [Open an issue](https://github.com/aifuun/ai-dev/issues)
