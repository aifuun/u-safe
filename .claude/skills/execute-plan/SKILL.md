---
name: execute-plan
description: |
  Execute implementation plan step-by-step - creates todos from plan, guides through tasks sequentially, runs until issue resolved.
  TRIGGER when: user wants to execute the plan after /start-issue (e.g., "execute the plan", "execute plan for #23", "implement issue #23", "work on the plan").
  DO NOT TRIGGER when: user just wants to plan (use /start-issue), review code (use /review), or finish work (use /finish-issue).
version: "3.3.0"
argument-hint: "[issue-number] [--resume] [--skip-task N]"
allowed-tools: Bash(git *), Bash(gh *), Bash(npm *), Read, Write, Glob, Grep, Edit
disable-model-invocation: false
user-invocable: true
---

# Execute Plan - Implementation Plan Executor

Execute implementation plan step-by-step until issue is resolved.

## Overview

This skill bridges `/start-issue` (planning) and `/review` (quality check) by orchestrating active development:

**What it does:**
1. **Loads plan** from `/start-issue` (`.claude/plans/active/issue-{N}-plan.md`)
2. **Creates todos** from plan tasks for progress tracking
3. **Guides implementation** task-by-task with context
4. **Validates progress** after each task (tests, linting, build)
5. **Continues until complete** - all tasks done, tests passing
6. **Prepares deliverables** for `/review` to validate quality

**Why it's needed:**
The gap between planning and completion lacks structure. Developers lose focus, skip tasks, or forget validation. This skill provides systematic task execution with built-in checkpoints.

**When to use:**
- After `/start-issue` creates branch and plan
- User says "start development", "implement", "work on issue"
- Need structured guidance through multi-task implementation

**Workflow sequence:**
```
/start-issue #23   → Creates branch + plan
/execute-plan #23     → Executes plan tasks (this skill)
/review            → Validates quality
/finish-issue #23  → Commits + PR + merge
```

## Arguments

```bash
/execute-plan [issue-number] [options]
```

**Common usage:**
```bash
/execute-plan #23              # Start fresh implementation
/execute-plan #23 --resume     # Resume after interruption
/execute-plan --skip-task 3    # Skip specific task (rare)
```

**Options:**
- `[issue-number]` - Optional, inferred from branch if omitted
- `--resume` - Resume from last incomplete task
- `--skip-task N` - Skip task N (use cautiously)
- `--dry-run` - Preview workflow without executing

## AI Execution Instructions

**CRITICAL: Task creation and worktree path handling**

When executing `/execute-plan`, AI MUST follow this pattern:

### Step 1: Load Plan from Worktree (if exists)

```python
# Check plan metadata for worktree path
plan_file = f".claude/plans/active/issue-{issue_number}-plan.md"
plan_content = Read(plan_file)

# Extract worktree path from plan metadata
worktree_match = re.search(r'\*\*Worktree\*\*: (.+)', plan_content)
if worktree_match:
    worktree_path = worktree_match.group(1)
    # CRITICAL: Use worktree path for all operations
    plan_file = f"{worktree_path}/.claude/plans/active/issue-{issue_number}-plan.md"
```

### Step 2: Parse Tasks and Create Todos

```python
# Extract tasks from plan's ## Tasks section
tasks = parse_tasks_from_plan(plan_content)

# Create TaskCreate for each with dependencies
for i, task in enumerate(tasks):
    todo = TaskCreate(
        subject=task.title,
        description=task.details,
        activeForm=f"{task.verb}ing..."
    )

    # Add dependency: task i+1 blocked by task i
    if i > 0:
        TaskUpdate(todo.id, addBlockedBy=[previous_todo.id])
```

### Step 3: Execute Tasks Sequentially

```python
for task_id in task_ids:
    # Mark in progress
    TaskUpdate(task_id, status="in_progress")

    # Display context and guide implementation
    display_task_context(task)
    execute_or_guide_task(task)

    # Validate completion (tests, linting if applicable)
    validate_task_completion(task)

    # Mark completed
    TaskUpdate(task_id, status="completed")
```

### Step 4: Worktree Path Usage

**CRITICAL**: If worktree exists, ALL file operations use worktree path:

```python
# ✅ CORRECT
Read(f"{worktree_path}/src/component.tsx")
Edit(f"{worktree_path}/.claude/skills/skill/SKILL.md")
Bash(f'git -C "{worktree_path}" status')

# ❌ WRONG
Read("src/component.tsx")  # Uses main repo
Bash("git status")  # Missing -C flag
```

## Workflow Steps

Copy this checklist to track progress:

```
Task Progress (High-Level):
- [ ] Step 1: Load plan and prerequisites
- [ ] Step 2: Create todos from plan
- [ ] Step 3: Execute tasks sequentially
- [ ] Step 4: Final validation
- [ ] Step 5: Report completion

Specific Tasks (from plan):
- [ ] Task 1: {from your plan}
- [ ] Task 2: {from your plan}
- [ ] Task 3: {from your plan}
... (tasks extracted from .claude/plans/active/issue-N-plan.md)
```

**Note**: Specific tasks are extracted from your implementation plan. The checklist above shows the high-level workflow phases.

Execute in sequence with progress tracking:

### Step 0: Issue Number Detection (Multi-Strategy)

If no issue number was provided as argument, use the shared detector module:

**Using the detector:**
```python
import sys
sys.path.insert(0, '.claude/skills/_scripts')

from framework.issue_detector import detect_issue_number

# Auto-detect with all 4 strategies + validation
issue_num = detect_issue_number(check_github=True, required=True)
# Returns: int (issue number) or raises IssueDetectionError
```

**Detection strategies (automatic, in order):**
1. **Extract from branch name** - `feature/137-python-shared-libs` → `137`
2. **Find single active plan** - If exactly 1 plan in `.claude/plans/active/`
3. **Extract from worktree path** - `ai-dev-137-python-shared-libs` → `137`
4. **Ask user** - Fallback prompt if all auto-detection fails

**For AI orchestration:**
When the user provides no issue number:
```markdown
1. Call detector: python -c "import sys; sys.path.insert(0, '.claude/skills/_scripts'); from framework.issue_detector import detect_issue_number; print(detect_issue_number())"
2. Capture issue number from output
3. If detection fails and user input needed:
   - Use AskUserQuestion tool to ask for issue number
   - Validate plan exists: .claude/plans/active/issue-{N}-plan.md
4. Continue with detected/provided issue number
```

**Plan file path:**
```bash
PLAN_FILE=".claude/plans/active/issue-${ISSUE_NUM}-plan.md"
```

### Step 1: Load Plan and Prerequisites

**Verify environment:**
- On feature branch (not main)
- Plan file exists: `.claude/plans/active/issue-{N}-plan.md`
- Git working directory clean (or can be stashed)

**Load plan:**
```bash
# Read plan file
PLAN_FILE=".claude/plans/active/issue-${ISSUE_NUM}-plan.md"
cat "$PLAN_FILE"
```

**Extract tasks** from plan's `## Tasks` section (look for `- [ ]` checkboxes or numbered lists).

**Abort if**:
- Not on feature branch → suggest `/start-issue #N`
- Plan file missing → suggest `/start-issue #N` or `/plan`
- No tasks found in plan → ask user to clarify plan

### Step 2: Create Todos from Plan

**Parse tasks** from plan and create with TaskCreate:

```markdown
For each task in plan:
1. Extract task description
2. Create todo: TaskCreate(subject, description, activeForm)
3. Add dependencies: task N blocks task N+1
4. Track task ID mapping
```

**Example:**
Plan has:
```markdown
## Tasks
- [ ] Read execute-plan/SKILL.md
- [ ] Create REFERENCE.md
- [ ] Update SKILL.md with links
```

Creates 3 linked todos:
- Task #1: "Read execute-plan/SKILL.md"
- Task #2: "Create REFERENCE.md" (blocked by #1)
- Task #3: "Update SKILL.md" (blocked by #2)

**Why todos:** Visual progress in Claude Code UI + checkpoint tracking.

### Step 3: Execute Tasks Sequentially

**For each task:**

**3.1. Display task context:**
```markdown
📋 Current Task (X/Y)

**Task**: {task description}
**From plan**: {link to plan section}
**Dependencies**: {completed tasks}
**Remaining**: {Y-X tasks}

**Acceptance criteria** (if defined in plan):
- {criteria 1}
- {criteria 2}
```

**3.2. Guide implementation:**
- Explain what needs to be done
- Show relevant code patterns or examples
- Suggest file locations and structure
- Provide implementation approach

**3.3. Execute or guide user:**
- For straightforward tasks (file edits, renames): Execute directly
- For complex tasks (new features, algorithms): Provide guidance + code snippets
- For research tasks (investigation, analysis): Conduct research and summarize

**3.4. Validate task completion:**
```bash
# After each task, run quick checks:
- If code changed: npm run lint (if exists)
- If tests exist: npm test (quick smoke test)
- If build required: npm run build
- Git status: ensure changes are intentional
```

**3.5. Mark task complete:**
```
TaskUpdate(task_id, status="completed")
```

**3.6. Move to next task:**
- Unblock next task in dependency chain
- Display next task context
- Repeat 3.1-3.5

**Interruption handling:**
- If user stops mid-task: Save progress state
- Resume with `--resume`: Continue from last incomplete task
- Show clear "You are here" indicator

### Step 4: Final Validation

**After all tasks complete:**

**4.1. Run comprehensive checks:**
```bash
# If tests exist
npm test || echo "⚠️ Tests need attention"

# If linting configured
npm run lint || echo "⚠️ Linting issues found"

# If build exists
npm run build || echo "⚠️ Build failed"

# Git status
git status --short
```

**4.2. Verify all tasks done:**
```markdown
✅ All tasks complete (Y/Y)

Completed:
- ✅ Task 1: {description}
- ✅ Task 2: {description}
- ✅ Task 3: {description}
...
```

**4.3. Prepare deliverables summary:**
```markdown
📦 Deliverables Ready for Review

**Files changed**: {count} files
**Lines added/removed**: +X/-Y
**Tests**: {passing}/{total} passing
**Linting**: {status}
**Build**: {status}

**Review checklist**:
- [ ] Code quality (run /review)
- [ ] Tests comprehensive
- [ ] Documentation updated
- [ ] No unintended changes
```

### Step 5: Report Completion

**Output mode detection**:
- **Auto mode** (called by /work-issue): Minimal 2-line output
- **Interactive mode** (direct invocation): Concise summary ≤20 lines

**Auto mode output**:
```python
is_auto_mode = os.path.exists('.claude/.work-issue-state.json')

if is_auto_mode:
    print(f"✅ Plan executed: {completed_tasks}/{total_tasks} tasks | {files_changed} files changed")
    print(f"Next: /review")
else:
    # Interactive mode - show concise summary
    print(f"""
🎉 Development Complete!

Issue #{issue_number}: {title}
Tasks: {completed_tasks}/{total_tasks} ✅
Files changed: {files_changed}
Tests: {test_status}

Next: /review → /finish-issue #{issue_number}
""")
```

**What NOT to do:**
- Don't commit yet (that's `/finish-issue`'s job)
- Don't push yet
- Don't create PR yet

**Hand off to:**
- `/review` - Quality validation
- `/finish-issue #23` - Final commit + PR + merge

## Safety Features

This skill includes multiple safety mechanisms to prevent issues during execution:

### 1. Plan Structure Validation

**Purpose**: Prevent infinite loops and malformed execution

**How it works:**
```python
# Validate required sections and parseable tasks
validate_sections(["## Tasks", "## Acceptance Criteria"])
tasks = extract_tasks_from_plan(plan_content)
if not tasks: raise ValidationError("No tasks found")
```

**Prevents:** Empty plans, malformed markdown, missing sections

### 2. Task Dependency Checking

**Purpose**: Prevent circular dependencies and deadlocks

**How it works:**
```python
# DFS cycle detection when adding dependencies
def validate_no_cycles(task_id, blockedBy_ids):
    visited = set()
    if task_id in visited:
        raise CircularDependencyError(task_id)
```

**Prevents:** Task A blocks B → B blocks A (deadlock), long chains with cycles, unexecutable graphs

### 3. Error Recovery Mechanism

**Purpose**: Save progress and resume after failures

**How it works:**
```python
# Save checkpoint before each task
state = {"issue_number": N, "current_task": id, "completed": [ids]}
save_to(".claude/.execute-plan-state.json")

# Resume with --resume flag
state = load_checkpoint()
skip_completed_tasks(state["completed"])
```

**Enables:** Resume after interruption, skip completed tasks, state persistence

### 4. Failure Limits

**Purpose**: Prevent infinite retry loops

**How it works:**
```python
MAX_RETRIES = 3
retry_count = 0

while retry_count < MAX_RETRIES:
    try:
        execute_task(task)
        break
    except TaskExecutionError as e:
        retry_count += 1
        if retry_count >= MAX_RETRIES:
            save_checkpoint(issue_num, task_id, completed_tasks)
            raise MaxRetriesExceeded(f"Task failed after {MAX_RETRIES} attempts")
        log.warning(f"Task failed, retry {retry_count}/{MAX_RETRIES}")
```

**Prevents:**
- Infinite loops on persistent failures
- Resource exhaustion
- Unrecoverable errors blocking workflow

### 5. State File Management

**Purpose**: Clean up temporary files and prevent state corruption

**How it works:**
```python
# On successful completion
cleanup_files([".claude/.execute-plan-state.json", ...])

# On start, warn if state older than 24h
if state_age > 86400:
    warn("State file stale, consider fresh start")
```

**Prevents:** Stale state confusion, disk accumulation, corruption from incomplete cleanup

### Safety Best Practices

When executing plans:

1. **Always validate before execution** - Run `/eval-plan` first to catch plan issues
2. **Use --resume carefully** - Verify state is recent and relevant
3. **Monitor task execution** - Watch for repeated failures indicating deeper issues
4. **Clean state on completion** - Automatic cleanup ensures fresh starts
5. **Respect failure limits** - If task fails 3 times, investigate root cause before forcing

## Error Handling

**Not on feature branch:**
```
❌ Not on feature branch

You're on: {current-branch}
Need: feature/{N}-{title}

Fix: /start-issue #23
```

**Plan file missing:**
```
❌ Plan not found

Expected: .claude/plans/active/issue-{N}-plan.md

Options:
1. Create plan: /start-issue #23
2. Custom plan: /plan "feature description"
```

**Task fails validation:**
```
⚠️ Task validation failed

Task: {description}
Error: {error message}

Options:
1. Fix and retry
2. Skip (--skip-task N) - not recommended
3. Pause and investigate
```

**Tests fail mid-implementation:**
```
❌ Tests failing

Failed: {test names}

This is expected during TDD. Continue implementing, then fix tests.

Options:
1. Continue (tests can fail during development)
2. Fix now (recommended for regressions)
3. Pause and debug
```

## Examples

### Example 1: Basic Implementation

**User says:**
> "start development on issue 95"

**Workflow:**
1. Load plan from `.claude/plans/active/issue-95-plan.md`
2. Create 15 todos from plan tasks
3. Execute task 1: "Read execute-plan/SKILL.md" → provides summary
4. Execute task 2: "Create REFERENCE.md" → creates file
5. Execute task 3: "Update SKILL.md" → updates with links
6. ... continues through all 15 tasks ...
7. Final validation: all tasks ✅, tests passing
8. Report: "Ready for review"

**Time:** Varies by complexity (30 min - 2 hours)

### Example 2: Resume After Interruption

**User says:**
> "resume development on issue 95"

**Workflow:**
1. Load plan and todo state
2. Find last incomplete task (task #8)
3. Display context: "Resuming from task 8/15"
4. Continue execution from task 8
5. Complete remaining tasks
6. Final validation and report

**Time:** Depends on remaining tasks

### Example 3: Skip Task

**User says:**
> "continue development but skip task 3, I already did it manually"

**Workflow:**
1. Load plan and current task (#2 just completed)
2. Skip task 3 (mark as completed without executing)
3. Move to task 4
4. Continue normally

**Time:** Same as basic flow minus one task

## Integration

**Workflow integration:**
```
Issue Lifecycle:
1. /start-issue #23     - Create branch + plan (30 sec)
2. /execute-plan #23       - Execute plan (30 min - 2 hrs) ← THIS SKILL
3. /review              - Quality check (5-10 min)
4. /finish-issue #23    - Commit + PR + merge (2-3 min)
```

**Plan structure expected:**
```markdown
## Tasks
- [ ] Task 1 description
- [ ] Task 2 description
- [ ] Task 3 description

## Acceptance Criteria
- Criteria 1
- Criteria 2
```

**Files involved:**
- Input: `.claude/plans/active/issue-{N}-plan.md`
- State: Tracked via TaskCreate/TaskUpdate
- Output: Modified code files (not committed yet)

## Best Practices

1. **Always use after /start-issue** - Ensure plan exists
2. **Don't skip tasks** unless absolutely necessary
3. **Let validation run** - Catches issues early
4. **Review before finishing** - Use `/review` before `/finish-issue`
5. **Commit at logical points** - If multi-day work, commit WIP

## Performance

- **Startup time:** <5 seconds (load plan + create todos)
- **Per task:** 2-15 minutes (depends on complexity)
- **Total time:** 30 minutes - 2 hours (typical)
- **Validation:** 10-30 seconds per task

Fast because:
- Structured task execution (no wandering)
- Built-in checkpoints (validate after each task)
- Clear context (always know next step)

## Worktree Support

If the issue was started with `/start-issue` and a worktree was created, all operations MUST use the worktree path.

### Auto-Detection

1. **Read plan file** to get worktree path:
   ```bash
   PLAN_FILE=".claude/plans/active/issue-${ISSUE_NUM}-plan.md"
   WORKTREE_PATH=$(grep "^**Worktree**:" "$PLAN_FILE" | cut -d' ' -f2)
   ```

2. **If worktree path exists**, use it for ALL operations
3. **If no worktree path**, use current directory (backward compatibility)

### File Operations with Worktree

**Always use absolute paths** when worktree is detected:

```bash
# Read files
Read ${WORKTREE_PATH}/.claude/plans/active/issue-117-plan.md
Read ${WORKTREE_PATH}/.claude/skills/execute-plan/SKILL.md
Read ${WORKTREE_PATH}/src/components/Button.tsx

# Edit files
Edit ${WORKTREE_PATH}/.claude/skills/start-issue/SKILL.md
Edit ${WORKTREE_PATH}/src/utils/helpers.ts

# Write new files
Write ${WORKTREE_PATH}/src/services/new-service.ts

# Git operations (use -C flag)
git -C ${WORKTREE_PATH} status
git -C ${WORKTREE_PATH} add .
git -C ${WORKTREE_PATH} diff

# Run commands in worktree context
cd ${WORKTREE_PATH} && npm test
# OR
npm --prefix ${WORKTREE_PATH} test
```

### Example: Full Task Execution

```markdown
## Task 1: Update start-issue SKILL.md

# ✅ CORRECT - Uses worktree path
Read /Users/woo/dev/ai-dev-117-auto-detect-worktree/.claude/skills/start-issue/SKILL.md
Edit /Users/woo/dev/ai-dev-117-auto-detect-worktree/.claude/skills/start-issue/SKILL.md

# ❌ WRONG - Uses relative path or main repo
Read .claude/skills/start-issue/SKILL.md
Edit /Users/woo/dev/ai-dev/.claude/skills/start-issue/SKILL.md
```

### Fallback Behavior

If no worktree path found in plan metadata:
- ✅ Use current working directory (traditional workflow)
- ✅ Relative paths work as before
- ✅ Backward compatible with non-worktree setups

**This ensures the skill works correctly whether or not worktrees are used.**

---

## Final Verification

**Critical checks before completion:**

```
- [ ] All plan tasks completed
- [ ] Todo list all marked completed
- [ ] Git status shows only expected changes
- [ ] No unintended file modifications
- [ ] Ready for /review phase
```

If any item fails, address before completing execution.

## Workflow Skills Requirements

This is a **workflow skill** and must follow the standard pattern:

1. **TaskCreate** at start - Create todo list from plan tasks
2. **TaskUpdate** during execution - Mark tasks as completed
3. **Verification checklist** - Final validation before completion

**See**: [WORKFLOW_PATTERNS.md](../WORKFLOW_PATTERNS.md) for complete implementation guide

## Usage Examples

This section provides practical examples of execute-plan usage across different scenarios.

### Example 1: Simple Task List Execution

**Scenario**: Implementing a documentation update with 3-4 independent tasks

**Plan excerpt:**
```markdown
## Tasks
- [ ] Update SKILL.md with new safety section
- [ ] Add usage examples section
- [ ] Verify ADR-020 compliance
- [ ] Check document length < 1000 lines
```

**Execution:**
```bash
/execute-plan #509
```

**What happens:**
1. **Load plan** - Reads issue-509-plan.md from worktree
2. **Create 4 todos** - Each task becomes a tracked todo
3. **Execute Task 1** - Updates SKILL.md with safety content
   - Validates: No syntax errors
4. **Execute Task 2** - Adds usage examples section
   - Validates: Section properly formatted
5. **Execute Task 3** - Runs compliance check
   - Validates: All 5 required sections present
6. **Execute Task 4** - Counts lines
   - Validates: 820 lines < 1000 ✅
7. **Final validation** - All tasks complete, ready for review

**Output:**
```
✅ All tasks complete (4/4)

Files changed: 1 file
- .claude/skills/execute-plan/SKILL.md (+180/-0)

Next: /review → /finish-issue #509
```

**Time:** ~15-20 minutes (documentation tasks are straightforward)

### Example 2: Tasks with Dependencies

**Scenario**: Feature implementation requiring sequential order

**Plan excerpt:**
```markdown
## Tasks
- [ ] Create service layer (src/services/auth.ts)
- [ ] Add repository methods (src/repositories/user.ts)
- [ ] Implement API endpoint (src/routes/auth.ts)
- [ ] Add integration tests (tests/auth.test.ts)
```

**Execution:**
```bash
/execute-plan #142
```

**What happens:**
1. **Task dependencies created** automatically:
   - Task 2 blocked by Task 1 (repository needs service)
   - Task 3 blocked by Task 2 (endpoint needs repository)
   - Task 4 blocked by Task 3 (tests need endpoint)

2. **Execute Task 1: Create service**
   ```typescript
   // src/services/auth.ts created
   export class AuthService {
     constructor(private userRepo: UserRepository) {}
     async login(email: string, password: string) { ... }
   }
   ```
   - Validation: TypeScript compiles ✅

3. **Execute Task 2: Add repository**
   ```typescript
   // src/repositories/user.ts updated
   async findByEmail(email: string): Promise<User | null> { ... }
   ```
   - Validation: TypeScript compiles ✅

4. **Execute Task 3: Implement endpoint**
   ```typescript
   // src/routes/auth.ts created
   router.post('/login', async (req, res) => { ... })
   ```
   - Validation: TypeScript compiles ✅

5. **Execute Task 4: Add tests**
   ```typescript
   // tests/auth.test.ts created
   describe('Auth API', () => { ... })
   ```
   - Validation: Tests run and pass ✅

**Output:**
```
✅ All tasks complete (4/4)

Files changed: 4 files
- src/services/auth.ts (+45 lines)
- src/repositories/user.ts (+30 lines)
- src/routes/auth.ts (+60 lines)
- tests/auth.test.ts (+80 lines)

Tests: 8/8 passing ✅

Next: /review → /finish-issue #142
```

**Time:** ~45-60 minutes (includes implementation + tests)

**Key insight:** Dependencies ensure correct order - you can't implement the endpoint before the service exists.

### Example 3: Resume After Failure

**Scenario**: Task 3 fails due to missing dependency, fix it and resume

**Initial execution:**
```bash
/execute-plan #88
```

**What happens:**
```
✅ Task 1 complete: Install auth library
✅ Task 2 complete: Create auth service
❌ Task 3 failed: Add login endpoint

Error: Missing type definition for AuthRequest

Options:
1. Fix and retry
2. Skip (--skip-task 3) - not recommended
3. Pause and investigate
```

**User investigates and fixes:**
```bash
# Install missing type package
npm install --save-dev @types/auth-request

# Resume execution
/execute-plan #88 --resume
```

**Resume execution:**
```
📋 Resuming from checkpoint

Completed:
✅ Task 1: Install auth library
✅ Task 2: Create auth service

Current:
⏯️ Task 3: Add login endpoint (retrying)

Remaining: 2 tasks
```

**What happens:**
1. **Load checkpoint** - Reads .claude/.execute-plan-state.json
2. **Skip completed tasks** - Tasks 1-2 already done
3. **Retry Task 3** - Missing types now available ✅
4. **Continue to Task 4** - Add tests
5. **Complete Task 5** - Update documentation
6. **Cleanup state** - Remove .execute-plan-state.json

**Output:**
```
✅ All tasks complete (5/5)

Resumed from: Task 3
Fixed issues: Missing type definition installed

Files changed: 3 files
Tests: 12/12 passing ✅

Next: /review → /finish-issue #88
```

**Time:**
- Initial run: 20 minutes (failed at task 3)
- Investigation: 5 minutes
- Resume run: 15 minutes (tasks 3-5)
- **Total:** 40 minutes (vs 60 minutes if restarted from scratch)

**Key insight:** Resume mechanism saves significant time by skipping completed work.

### Example 4: Worktree-Based Execution

**Scenario**: Working on issue in isolated worktree directory

**Setup (from /start-issue):**
```bash
/start-issue #123
# Creates: /Users/woo/dev/ai-dev-123-add-logging
# Branch: feature/123-add-logging
```

**Execute plan:**
```bash
/execute-plan #123
```

**What happens (worktree-aware):**
1. **Detect worktree** - Reads plan metadata:
   ```markdown
   **Worktree**: /Users/woo/dev/ai-dev-123-add-logging
   ```

2. **All file operations use worktree path:**
   ```python
   # ✅ CORRECT
   Read("/Users/woo/dev/ai-dev-123-add-logging/src/logger.ts")
   Edit("/Users/woo/dev/ai-dev-123-add-logging/.claude/skills/...")

   # ❌ WRONG (would modify main repo)
   Read("src/logger.ts")
   ```

3. **Git operations use -C flag:**
   ```bash
   git -C /Users/woo/dev/ai-dev-123-add-logging status
   git -C /Users/woo/dev/ai-dev-123-add-logging add .
   ```

4. **Execute tasks in worktree context:**
   - Task 1: Create logger.ts (in worktree)
   - Task 2: Update app.ts to use logger (in worktree)
   - Task 3: Add tests (in worktree)

**Benefits:**
- ✅ Main repo stays clean (still on main branch)
- ✅ Can work on multiple issues in parallel
- ✅ Each worktree has isolated dependencies
- ✅ No branch switching needed

**Output:**
```
✅ All tasks complete (3/3)

Worktree: /Users/woo/dev/ai-dev-123-add-logging
Files changed: 3 files

Next: /review → /finish-issue #123
```

**Key insight:** Worktrees enable parallel development without interference.

## Testing

This skill has comprehensive test coverage following ADR-020 standards.

### Test Suite

**Location**: `.claude/skills/execute-plan/tests/`

**Coverage**: 96% (target: >60%)

**Test Files**:
- `test_functional.py` (7 tests) - Core "What it does" functionality
- `test_arguments.py` (6 tests) - Argument validation and handling
- `test_safety.py` (7 tests) - Safety mechanisms validation

**Total**: 20 tests across 3 categories

### Running Tests

```bash
# Navigate to skill directory
cd .claude/skills/execute-plan

# Activate virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov --cov-report=term-missing

# Run specific category
pytest tests/test_functional.py
pytest tests/ -m functional
pytest tests/ -m safety
```

### Test Categories

**1. Functional Tests** (test_functional.py)
- Load plan from file path
- Extract tasks from markdown plan
- Create todos with dependencies
- Execute tasks respecting order
- Validate task completion
- Generate deliverables summary
- Complete end-to-end workflow

**2. Argument Tests** (test_arguments.py)
- Extract issue number from branch name
- Load checkpoint with --resume flag
- Skip task functionality
- Dry-run preview mode
- Invalid argument detection
- Auto-detect from active plan

**3. Safety Tests** (test_safety.py)
- Empty plan validation
- Malformed markdown detection
- Circular dependency prevention
- Error recovery checkpoints
- Max retry limits
- State file cleanup
- Stale state warnings

### Detailed Documentation

See [tests/README.md](tests/README.md) for:
- Complete test suite overview
- Running tests with markers
- Adding new tests
- CI/CD integration
- Troubleshooting

## Related Skills

- **/start-issue** - Creates branch and plan (Phase 1 - run before this)
- **/eval-plan** - Validates plan quality (Phase 1.5 - recommended before execution)
- **/review** - Quality validation (Phase 2.5 - run after this)
- **/finish-issue** - Commit and close issue (Phase 3 - final step)
- **/next** - Get single next task (lighter alternative)

---

**Version:** 3.3.0
**Pattern:** Workflow Orchestrator (executes plan step-by-step)
**Compliance:** ADR-001 ✅ | ADR-015 ✅ | ADR-020 ✅ | WORKFLOW_PATTERNS.md ✅
**Last Updated:** 2026-04-07
**Changelog:**
- v3.3.0: Added comprehensive test suite with 96% coverage (20 tests, ADR-020 compliant) (Issue #521)
- v3.2.0: Added Safety Features and Usage Examples sections for ADR-020 compliance (Issue #509)
- v3.1.0: Added mode-aware output (2 lines auto, ≤20 lines interactive) (Issue #263)
- v3.0.0: Worktree support and task execution
- v2.0.0: Added progress tracking
