# Auto-Solve Issue - 5-Phase Workflow

> Detailed workflow steps for AI execution of automated issue resolution

## Overview

This document details the 7-step execution pattern for `/auto-solve-issue`. The workflow is orchestrated by `coordinator.py`'s `IssueSolver` class, which manages:

1. Task dependency chain creation
2. Main execution loop (find → execute → checkpoint → complete)
3. Checkpoint validation (score ≥ 90 for auto-continue)
4. Resume mechanism (save/load state)
5. Error handling (retry up to 3 times)

## AI Execution Instructions

**CRITICAL: Task dependencies + direct skill call pattern**

When executing `/auto-solve-issue`, AI MUST follow this pattern:

### Step 0: Read Workflow Guide (CRITICAL - do this first)

**Read issue lifecycle standards** before executing automation:

```python
# Read workflow guide for 5-phase standards
lifecycle_guide = read_file(".claude/guides/ISSUE_LIFECYCLE_GUIDE.md")

# Extract workflow standards
workflow_standards = extract_workflow_standards(lifecycle_guide)
# - Phase 1: start-issue (worktree creation, plan generation)
# - Phase 1.5: eval-plan (score ≥90 for auto-continue, auto-fix if score ≥90)
# - Phase 2: execute-plan (task-by-task implementation)
# - Phase 2.5: review (score ≥90 for auto-continue)
# - Phase 3: finish-issue (commit, PR, merge, cleanup)
# - Checkpoint thresholds: ≥90 auto-continue, <90 stop in interactive mode
# - Auto-fix types: missing_todo, incomplete_test, format_issue, etc.
```

**Use these standards when**:
- **Phase execution**: Follow 5-phase workflow structure
- **Checkpoint decisions**: Apply score thresholds (≥90 for auto-continue)
- **Auto-fix**: Apply fixes when score ≥90 (eval-plan only)
- **Error handling**: Stop on blocking issues, continue on warnings

### Step 1: Create 5-Task Dependency Chain

```python
# Create 5 tasks representing the workflow phases
# Each task includes metadata for checkpoints and phase tracking

# Phase 1: Start Issue
task1 = TaskCreate(
    subject="Phase 1: start-issue",
    description="Create branch, generate plan, sync with main",
    activeForm="Creating branch and plan",
    metadata={
        "phase": "1",
        "skill": "start-issue",
        "checkpoint": False,
        "issue_number": issue_number
    }
)

# Phase 1.5: Evaluate Plan (with checkpoint)
task2 = TaskCreate(
    subject="Phase 1.5: eval-plan",
    description="Validate implementation plan (score must be ≥ 90 for auto-continue)",
    activeForm="Evaluating plan",
    metadata={
        "phase": "1.5",
        "skill": "eval-plan",
        "checkpoint": True,
        "checkpoint_name": "Checkpoint 1",
        "score_threshold": 90,
        "issue_number": issue_number
    }
)
# Block Phase 1.5 until Phase 1 completes
TaskUpdate(task2.id, addBlockedBy=[task1.id])

# Phase 2: Execute Plan
task3 = TaskCreate(
    subject="Phase 2: execute-plan",
    description="Implement all tasks from plan",
    activeForm="Executing implementation plan",
    metadata={
        "phase": "2",
        "skill": "execute-plan",
        "checkpoint": False,
        "issue_number": issue_number
    }
)
# Block Phase 2 until Phase 1.5 completes (including checkpoint)
TaskUpdate(task3.id, addBlockedBy=[task2.id])

# Phase 2.5: Review Code (with checkpoint)
task4 = TaskCreate(
    subject="Phase 2.5: review",
    description="Validate code quality (score must be ≥ 90 for auto-continue)",
    activeForm="Reviewing code quality",
    metadata={
        "phase": "2.5",
        "skill": "review",
        "checkpoint": True,
        "checkpoint_name": "Checkpoint 2",
        "score_threshold": 90,
        "issue_number": issue_number
    }
)
# Block Phase 2.5 until Phase 2 completes
TaskUpdate(task4.id, addBlockedBy=[task3.id])

# Phase 3: Finish Issue
task5 = TaskCreate(
    subject="Phase 3: finish-issue",
    description="Commit, create PR, merge, close issue",
    activeForm="Finishing issue",
    metadata={
        "phase": "3",
        "skill": "finish-issue",
        "checkpoint": False,
        "issue_number": issue_number
    }
)
# Block Phase 3 until Phase 2.5 completes (including checkpoint)
TaskUpdate(task5.id, addBlockedBy=[task4.id])

# Store task IDs for main loop
task_ids = [task1.id, task2.id, task3.id, task4.id, task5.id]
```

**Key Design Decisions:**

1. **Dependency Chain**: Each task blocks the next, creating a sequential workflow
2. **Metadata**: Stores phase number, skill name, checkpoint flag, score threshold
3. **Checkpoints**: Phases 1.5 and 2.5 are checkpoints with score validation
4. **Auto-unlock**: When a task completes, the next task automatically becomes available

### Step 2: Find Next Available Task

```python
def find_next_available_task(task_ids: list[str]) -> dict | None:
    """
    查找下一个可用任务（pending 且无 blockedBy 的任务）

    Args:
        task_ids: 所有工作流任务的 ID 列表

    Returns:
        下一个可用任务的详细信息，如果没有则返回 None
        返回格式: {
            "id": str,
            "subject": str,
            "status": str,
            "metadata": dict,
            "blockedBy": list
        }
    """
    # 获取所有任务的当前状态
    all_tasks = TaskList()

    # 过滤出我们创建的工作流任务
    workflow_tasks = [t for t in all_tasks if t.id in task_ids]

    # 查找第一个 pending 且无 blockedBy 的任务
    for task in workflow_tasks:
        # 跳过已完成的任务
        if task.status == "completed":
            continue

        # 跳过有阻塞依赖的任务
        if task.blockedBy and len(task.blockedBy) > 0:
            # 检查是否所有阻塞任务都已完成
            all_blockers_done = True
            for blocker_id in task.blockedBy:
                blocker = next((t for t in workflow_tasks if t.id == blocker_id), None)
                if blocker and blocker.status != "completed":
                    all_blockers_done = False
                    break

            # 如果还有未完成的阻塞任务，跳过
            if not all_blockers_done:
                continue

        # 找到了下一个可用任务
        return {
            "id": task.id,
            "subject": task.subject,
            "status": task.status,
            "metadata": task.metadata,
            "blockedBy": task.blockedBy
        }

    # 没有找到可用任务
    return None
```

**Logic Explanation:**

1. **Get current state**: Use TaskList() to fetch all tasks
2. **Filter workflow tasks**: Only consider our 5 created tasks
3. **Find available task**:
   - Status must be "pending" (not "completed")
   - No blockedBy dependencies, OR all blockers are completed
4. **Return first match**: The task that's ready to execute

**Edge Cases:**
- All tasks completed → return None (workflow done)
- Tasks still blocked → return None (wait for blocker to complete)
- Task in_progress → skip it (shouldn't happen in normal flow)

### Step 3: Execute Phase (Direct Call or Subagent)

**DEFAULT: Use direct skill calls (--no-subagent)**

```python
def execute_with_skill_call(task: dict, mode: str) -> dict:
    """
    使用 Skill tool 直接调用（推荐方式，默认）

    优势：
    - 保持工作目录一致
    - 继承 worktree 上下文
    - 输出文件写入正确位置
    - 避免 subagent 上下文隔离问题

    Args:
        task: 任务详细信息（包含 metadata 中的 skill 名称）
        mode: 执行模式 ("auto" 或 "interactive")

    Returns:
        执行结果 {
            "success": bool,
            "score": int | None,  # For checkpoint phases
            "error": str | None
        }
    """
    skill_name = task["metadata"]["skill"]
    issue_number = task["metadata"]["issue_number"]
    is_checkpoint = task["metadata"].get("checkpoint", False)

    # 构建 skill 参数
    if skill_name == "eval-plan":
        skill_args = f"{issue_number} --mode={mode}"
    elif skill_name == "review":
        skill_args = ""  # review 自动检测当前分支
    elif skill_name in ["start-issue", "execute-plan", "finish-issue"]:
        skill_args = str(issue_number)
    else:
        skill_args = str(issue_number)

    # 直接调用 skill（不使用 subagent）
    try:
        Skill(
            skill=skill_name,
            args=skill_args
        )

        # 读取分数（如果是 checkpoint）
        score = None
        if is_checkpoint:
            if skill_name == "eval-plan":
                score = read_eval_plan_score()
            elif skill_name == "review":
                score = read_review_score()

        return {
            "success": True,
            "score": score,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "score": None,
            "error": str(e)
        }


def execute_with_subagent(task: dict, mode: str) -> dict:
    """
    使用 Subagent 执行指定的 skill

    Args:
        task: 任务详细信息（包含 metadata 中的 skill 名称）
        mode: 执行模式 ("auto" 或 "interactive")

    Returns:
        执行结果 {
            "success": bool,
            "score": int | None,  # For checkpoint phases
            "error": str | None
        }
    """
    skill_name = task["metadata"]["skill"]
    issue_number = task["metadata"]["issue_number"]
    is_checkpoint = task["metadata"].get("checkpoint", False)

    # 构建 skill 参数
    if skill_name == "eval-plan":
        skill_args = f"{issue_number} --mode={mode}"
    elif skill_name == "review":
        skill_args = ""  # review 自动检测当前分支
    elif skill_name in ["start-issue", "execute-plan", "finish-issue"]:
        skill_args = str(issue_number)
    else:
        skill_args = str(issue_number)

    # 启动 Subagent 执行 skill
    try:
        # 使用 Task tool 启动 subagent
        result = Task(
            subagent_type="general-purpose",
            description=f"Execute {skill_name}",
            prompt=f"Execute /{skill_name} {skill_args}",
            model="sonnet",  # 使用 sonnet 确保质量
            max_turns=30  # 60 minutes timeout (2 min per turn)
        )

        # 如果是 checkpoint phase，读取 score
        score = None
        if is_checkpoint:
            if skill_name == "eval-plan":
                score = read_eval_plan_score()
            elif skill_name == "review":
                score = read_review_score()

        return {
            "success": True,
            "score": score,
            "error": None
        }

    except Exception as e:
        # Subagent 执行失败
        return {
            "success": False,
            "score": None,
            "error": str(e)
        }


def read_eval_plan_score() -> int | None:
    """从 .claude/.eval-plan-status.json 读取分数"""
    try:
        status_file = ".claude/.eval-plan-status.json"
        with open(status_file, "r") as f:
            data = json.load(f)
            return data.get("score")
    except:
        return None


def read_review_score() -> int | None:
    """从 .claude/.review-status.json 读取分数"""
    try:
        status_file = ".claude/.review-status.json"
        with open(status_file, "r") as f:
            data = json.load(f)
            return data.get("score")
    except:
        return None
```

**Execution Method Selection:**

```python
# Parse --no-subagent flag (default: True)
use_subagent = "--no-subagent" not in args  # Default: False (use direct calls)

# Select execution method
if use_subagent:
    result = execute_with_subagent(next_task, mode)
else:
    result = execute_with_skill_call(next_task, mode)  # DEFAULT
```

**Key Design Points:**

1. **Direct Skill Calls (Default)**: Execute in current context
   - ✅ Maintains working directory consistency
   - ✅ Inherits worktree context
   - ✅ Output files written to correct location
   - ✅ No subagent isolation issues
   - **Use by default** - only use subagent if explicitly needed

2. **Subagent Isolation (Legacy)**: Each phase runs in independent context
   - No context pollution between phases
   - Clean execution environment
   - Separate error handling
   - **Known issue**: Output file path problems with worktrees
   - **Use only when**: You need complete context isolation

3. **Skill Arguments**: Customize args per skill
   - eval-plan: Needs --mode=auto/interactive
   - review: Auto-detects current branch
   - Others: Just need issue number

4. **Timeout**: max_turns=30 = ~60 minutes per phase
   - Prevents infinite loops
   - Allows complex phases to complete
   - Can be adjusted based on testing

5. **Score Reading**: For checkpoint phases
   - eval-plan writes .eval-plan-status.json
   - review writes .review-status.json
   - Read after execution completes

6. **Error Handling**: Return structured result
   - success flag indicates completion
   - score extracted for checkpoints
   - error message captured

### Step 4: Main Execution Loop

```python
# Parse --no-subagent flag (default: use direct calls)
use_subagent = "--no-subagent" not in args  # Default: False

# Check if resuming from previous run
if resume_flag:
    resume_data = load_resume_point()

    if resume_data:
        # Resume workflow from saved state
        context = resume_workflow(resume_data)
        task_ids = context["task_ids"]
        mode = context["mode"]
        issue_number = context["issue_number"]
        # Preserve use_subagent from args (user can override on resume)
    else:
        print("⚠️ No resume point found, starting fresh")
        # Continue with fresh start (task_ids already created)
else:
    # Fresh start - task_ids already created in Step 1
    pass

# Main workflow loop - continues until all phases complete
while True:
    # 1. Find next available task
    next_task = find_next_available_task(task_ids)

    # 2. Check if workflow complete
    if next_task is None:
        # All tasks completed
        print("✅ All phases completed!")
        cleanup_state_files()
        break

    # 3. Display current phase
    phase = next_task["metadata"]["phase"]
    skill = next_task["metadata"]["skill"]
    is_checkpoint = next_task["metadata"].get("checkpoint", False)

    print(f"\n📋 Executing Phase {phase}: {skill}")

    # 4. Mark task as in_progress
    TaskUpdate(next_task["id"], status="in_progress")

    # 5. Execute phase (direct call or subagent)
    if use_subagent:
        result = execute_with_subagent(next_task, mode)
    else:
        result = execute_with_skill_call(next_task, mode)  # DEFAULT

    # 6. Check execution result
    if not result["success"]:
        # Execution failed
        print(f"❌ Phase {phase} failed: {result['error']}")

        # Increment retry count
        retry_count = next_task["metadata"].get("retry_count", 0)
        retry_count += 1

        if retry_count >= 3:
            # Max retries exceeded
            print(f"❌ Max retries (3) exceeded for Phase {phase}")
            save_resume_point(next_task["id"], "max_retries_exceeded")
            break
        else:
            # Retry
            print(f"⚠️ Retrying Phase {phase} (attempt {retry_count + 1}/3)")
            TaskUpdate(
                next_task["id"],
                status="pending",
                metadata={"retry_count": retry_count}
            )
            continue

    # 7. Handle checkpoint phases
    if is_checkpoint:
        score = result["score"]
        threshold = next_task["metadata"]["score_threshold"]
        checkpoint_name = next_task["metadata"]["checkpoint_name"]

        print(f"\n⏸️ {checkpoint_name}")
        print(f"   Score: {score}/100")
        print(f"   Threshold: {threshold}")

        if score is None:
            # Score not available
            print(f"⚠️ Score not available, treating as checkpoint")
            if mode == "auto":
                # Auto mode requires score
                save_resume_point(next_task["id"], "score_unavailable")
                print(f"⏸️ Stopping - fix issue and use --resume")
                break
            else:
                # Interactive mode - ask user
                user_decision = ask_user_to_continue()
                if user_decision != "continue":
                    save_resume_point(next_task["id"], "user_stopped")
                    break

        elif score < threshold:
            # Score below threshold
            print(f"⚠️ Score {score} < {threshold}")

            if mode == "auto":
                # Auto mode stops on low score
                save_resume_point(next_task["id"], "score_below_threshold")
                print(f"\n⏸️ Stopping at {checkpoint_name}")
                print(f"   Score {score}/100 is below threshold {threshold}")
                print(f"   Fix issues and resume: /auto-solve-issue #{issue_number} --resume")
                break
            else:
                # Interactive mode - ask user
                user_decision = ask_user_to_continue()
                if user_decision != "continue":
                    save_resume_point(next_task["id"], "user_stopped")
                    break

        else:
            # Score ≥ threshold
            print(f"✅ Score {score} ≥ {threshold} - auto-continuing")

    # 8. Mark task as completed
    TaskUpdate(next_task["id"], status="completed")
    print(f"✅ Phase {phase} completed")

# Workflow complete or stopped
if next_task is None:
    print("\n🎉 Issue lifecycle complete!")
    print(f"   Issue #{issue_number} resolved")
    print(f"   All phases executed successfully")
else:
    print(f"\n⏸️ Workflow paused at Phase {phase}")
    print(f"   Resume with: /auto-solve-issue #{issue_number} --resume")
```

**Loop Flow:**

1. **Find next task**: Check which task is ready (pending + no blockers)
2. **Completion check**: If none found, all tasks are done
3. **Display phase**: Show current phase to user
4. **Mark in progress**: Update task status
5. **Execute skill**: Run directly or via subagent
6. **Error handling**: Retry up to 3 times, then save resume point
7. **Checkpoint logic**:
   - Auto mode: Stop if score < 90
   - Interactive mode: Always ask user
   - Continue if score ≥ 90
8. **Mark completed**: Task done, dependency automatically unlocks next task

**Key Features:**

- **Continuous execution**: Loop continues until all tasks done or checkpoint stops
- **Auto-unlock**: Completing a task automatically unblocks the next
- **Retry logic**: Failed phases retry up to 3 times
- **Checkpoint validation**: Score-based decision in auto mode
- **Resume points**: Save state when stopping for resume later

---

**See also:**
- [CHECKPOINTS.md](./CHECKPOINTS.md) - Checkpoint validation and resume mechanism
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Error handling patterns
- [EXAMPLES.md](./EXAMPLES.md) - Usage examples
