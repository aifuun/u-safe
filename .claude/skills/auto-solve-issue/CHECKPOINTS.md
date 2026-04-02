# Auto-Solve Issue - Checkpoint System

> Checkpoint validation and resume mechanism for workflow safety

## Overview

The checkpoint system provides safety gates during automated workflow execution:

1. **Checkpoint 1** (Phase 1.5): Validates implementation plan quality before coding starts
2. **Checkpoint 2** (Phase 2.5): Validates code quality before merging

**Checkpoint behavior:**
- **Auto mode** (`--auto`): Stop if score < 90, auto-continue if score ≥ 90
- **Interactive mode** (`--interactive`): Always ask user at checkpoints

**Resume capability:**
- Saves workflow state to `.claude/.auto-solve-state.json`
- Can resume from any checkpoint using `--resume` flag
- Preserves task IDs, mode, and failure reason

## Checkpoint Validation

### Status File Reading

Each checkpoint reads its respective status file:

- **Checkpoint 1** → `.claude/.eval-plan-status.json` (from /eval-plan skill)
- **Checkpoint 2** → `.claude/.review-status.json` (from /review skill)

**Status file format:**
```json
{
  "timestamp": "2026-03-30T10:30:00Z",
  "issue_number": 409,
  "status": "approved",
  "score": 95,
  "valid_until": "2026-03-30T12:00:00Z"  // 90-minute expiry
}
```

### Checkpoint Logic Implementation

```python
def check_checkpoint(checkpoint_name: str, mode: str) -> dict:
    """
    检查 checkpoint 分数并决定是否继续

    Args:
        checkpoint_name: "Checkpoint 1" (eval-plan) 或 "Checkpoint 2" (review)
        mode: "auto" 或 "interactive"

    Returns:
        {
            "should_continue": bool,
            "score": int | None,
            "reason": str
        }
    """
    # 根据 checkpoint 名称读取相应的状态文件
    if checkpoint_name == "Checkpoint 1":
        status_file = ".claude/.eval-plan-status.json"
        skill_name = "eval-plan"
    elif checkpoint_name == "Checkpoint 2":
        status_file = ".claude/.review-status.json"
        skill_name = "review"
    else:
        return {
            "should_continue": False,
            "score": None,
            "reason": f"Unknown checkpoint: {checkpoint_name}"
        }

    # 读取状态文件
    try:
        with open(status_file, "r") as f:
            data = json.load(f)

        score = data.get("score")
        status = data.get("status")

        # 验证 valid_until 时间戳（状态文件有效期 90 分钟）
        valid_until = data.get("valid_until")
        if valid_until:
            from datetime import datetime
            valid_time = datetime.fromisoformat(valid_until)
            now = datetime.now()
            if now > valid_time:
                return {
                    "should_continue": False,
                    "score": score,
                    "reason": f"{skill_name} status expired - re-run {skill_name}"
                }

    except FileNotFoundError:
        return {
            "should_continue": False,
            "score": None,
            "reason": f"Status file not found: {status_file}"
        }
    except json.JSONDecodeError:
        return {
            "should_continue": False,
            "score": None,
            "reason": f"Invalid JSON in {status_file}"
        }

    # 判断是否继续
    threshold = 90

    if score is None:
        # 分数不可用
        if mode == "auto":
            return {
                "should_continue": False,
                "score": None,
                "reason": "Score unavailable in auto mode"
            }
        else:
            # Interactive mode - 让用户决定
            return {
                "should_continue": ask_user_to_continue() == "continue",
                "score": None,
                "reason": "User decision (score unavailable)"
            }

    elif score < threshold:
        # 分数低于阈值
        if mode == "auto":
            return {
                "should_continue": False,
                "score": score,
                "reason": f"Score {score} < {threshold} (auto mode)"
            }
        else:
            # Interactive mode - 让用户决定
            return {
                "should_continue": ask_user_to_continue() == "continue",
                "score": score,
                "reason": f"User decision (score {score} < {threshold})"
            }

    else:
        # 分数 >= 阈值
        return {
            "should_continue": True,
            "score": score,
            "reason": f"Score {score} ≥ {threshold}"
        }


def ask_user_to_continue() -> str:
    """
    在 interactive mode 下询问用户是否继续

    Returns:
        "continue" 或 "stop"
    """
    # 使用 AskUserQuestion tool
    response = AskUserQuestion(
        questions=[{
            "question": "Continue to next phase?",
            "header": "Checkpoint",
            "options": [
                {
                    "label": "Continue",
                    "description": "Proceed to next phase despite issues"
                },
                {
                    "label": "Stop",
                    "description": "Pause workflow to fix issues"
                }
            ],
            "multiSelect": False
        }]
    )

    # Parse response
    if "Continue" in response.values():
        return "continue"
    else:
        return "stop"
```

### Decision Matrix

| Condition | Auto Mode | Interactive Mode |
|-----------|-----------|------------------|
| **Score ≥ 90** | ✅ Auto-continue | ✅ Auto-continue |
| **Score < 90** | ❌ Stop, save resume point | ⏸️ Ask user |
| **Score unavailable** | ❌ Stop, save resume point | ⏸️ Ask user |
| **File not found** | ❌ Stop, save resume point | ❌ Stop, save resume point |
| **Status expired** | ❌ Stop, re-run skill | ❌ Stop, re-run skill |

### Edge Cases

1. **Status file not found**:
   - Reason: Skill didn't execute or failed before writing status
   - Action: Stop workflow, run skill manually

2. **Invalid JSON in status file**:
   - Reason: Corrupted file or incomplete write
   - Action: Stop workflow, delete file, re-run skill

3. **Status expired (>90 minutes)**:
   - Reason: Too long between checkpoint and check
   - Action: Stop workflow, re-run skill to refresh status

4. **Score unavailable (null)**:
   - Auto mode: Stop immediately (requires score for automation)
   - Interactive mode: Ask user to decide

## Resume Mechanism

### Saving Resume Points

Resume points are saved when:
- Checkpoint score < 90 (auto mode)
- Max retries exceeded (3 failures)
- User stops workflow (interactive mode)
- Score unavailable (auto mode)

```python
def save_resume_point(task_id: str, reason: str):
    """
    保存当前工作流恢复点

    Args:
        task_id: 停止时的任务 ID
        reason: 停止原因（score_below_threshold, max_retries_exceeded等）
    """
    from datetime import datetime

    # 获取任务详细信息
    task = TaskGet(task_id)

    # 构建恢复点数据
    resume_data = {
        "timestamp": datetime.now().isoformat(),
        "issue_number": task.metadata.get("issue_number"),
        "stopped_at_task_id": task_id,
        "stopped_at_phase": task.metadata.get("phase"),
        "stopped_at_skill": task.metadata.get("skill"),
        "reason": reason,
        "task_ids": task_ids,  # 所有工作流任务的 ID
        "mode": mode  # auto 或 interactive
    }

    # 写入状态文件
    state_file = ".claude/.auto-solve-state.json"
    with open(state_file, "w") as f:
        json.dump(resume_data, f, indent=2)

    print(f"\n💾 Resume point saved:")
    print(f"   State file: {state_file}")
    print(f"   Stopped at: Phase {task.metadata.get('phase')}")
    print(f"   Reason: {reason}")
    print(f"\n   Resume with: /auto-solve-issue #{issue_number} --resume")
```

### Resume State File Format

`.claude/.auto-solve-state.json`:

```json
{
  "timestamp": "2026-03-30T10:45:00Z",
  "issue_number": 409,
  "stopped_at_task_id": "task_140",
  "stopped_at_phase": "1.5",
  "stopped_at_skill": "eval-plan",
  "reason": "score_below_threshold",
  "task_ids": ["task_138", "task_139", "task_140", "task_141", "task_142"],
  "mode": "auto"
}
```

**Fields:**
- `timestamp`: When workflow was paused
- `issue_number`: Which issue being worked on
- `stopped_at_task_id`: Task ID where execution stopped
- `stopped_at_phase`: Phase number (1, 1.5, 2, 2.5, or 3)
- `stopped_at_skill`: Skill name that failed/paused
- `reason`: Why execution stopped (see reasons below)
- `task_ids`: All 5 workflow task IDs for resumption
- `mode`: Execution mode (auto or interactive)

**Common reasons:**
- `score_below_threshold`: Checkpoint score < 90 in auto mode
- `score_unavailable`: Status file missing or score null
- `max_retries_exceeded`: Phase failed 3 times
- `user_stopped`: User chose to stop in interactive mode
- `task_system_error`: Unexpected error in task system

### Loading and Resuming

```python
def load_resume_point() -> dict | None:
    """
    加载保存的恢复点

    Returns:
        恢复点数据，如果不存在则返回 None
    """
    state_file = ".claude/.auto-solve-state.json"

    try:
        with open(state_file, "r") as f:
            data = json.load(f)

        print(f"\n💾 Resume point found:")
        print(f"   Saved at: {data['timestamp']}")
        print(f"   Stopped at: Phase {data['stopped_at_phase']}")
        print(f"   Reason: {data['reason']}")

        return data

    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print(f"⚠️ Invalid resume state file: {state_file}")
        return None


def resume_workflow(resume_data: dict):
    """
    从保存的恢复点继续执行工作流

    Args:
        resume_data: 从 load_resume_point() 加载的恢复点数据
    """
    # 提取恢复信息
    stopped_task_id = resume_data["stopped_at_task_id"]
    task_ids = resume_data["task_ids"]
    mode = resume_data["mode"]
    issue_number = resume_data["issue_number"]

    print(f"\n🔄 Resuming workflow...")
    print(f"   Issue: #{issue_number}")
    print(f"   Mode: {mode}")

    # 重置停止的任务状态为 pending
    # 这样 find_next_available_task() 会重新找到它
    TaskUpdate(stopped_task_id, status="pending")

    print(f"   Reset task {stopped_task_id} to pending")
    print(f"   Continuing execution loop...")

    # 返回恢复后的上下文
    return {
        "task_ids": task_ids,
        "mode": mode,
        "issue_number": issue_number,
        "resumed": True
    }
```

**Resume workflow:**
1. Load state from `.claude/.auto-solve-state.json`
2. Extract task IDs, mode, issue number
3. Reset stopped task to `pending` status
4. Continue main execution loop from that task

### Cleanup on Completion

```python
def cleanup_state_files():
    """
    清理工作流状态文件
    """
    import os

    state_files = [
        ".claude/.auto-solve-state.json",
        ".claude/.eval-plan-status.json",
        ".claude/.review-status.json"
    ]

    for file_path in state_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"   Cleaned: {file_path}")
        except Exception as e:
            print(f"   Warning: Failed to clean {file_path}: {e}")
```

**When cleanup runs:**
- All 5 phases completed successfully
- No errors or checkpoints failed
- Issue closed and merged

**Why cleanup:**
- Prevents stale state from affecting next run
- Ensures fresh start for next issue
- Clears temporary validation data

## Example Scenarios

### Scenario 1: Checkpoint Passed (Auto Mode)

```
Phase 1.5: eval-plan completes
Status file: .claude/.eval-plan-status.json
Score: 95/100

⏸️ Checkpoint 1
   Score: 95/100
   Threshold: 90

✅ Score 95 ≥ 90 - auto-continuing

→ Proceeds to Phase 2: execute-plan
```

### Scenario 2: Checkpoint Failed (Auto Mode)

```
Phase 1.5: eval-plan completes
Status file: .claude/.eval-plan-status.json
Score: 75/100

⏸️ Checkpoint 1
   Score: 75/100
   Threshold: 90

⚠️ Score 75 < 90

⏸️ Stopping at Checkpoint 1
   Score 75/100 is below threshold 90
   Fix issues and resume: /auto-solve-issue #409 --resume

💾 Resume point saved:
   State file: .claude/.auto-solve-state.json
   Stopped at: Phase 1.5
   Reason: score_below_threshold
```

### Scenario 3: Resume After Fix

```
User fixes plan issues
User runs: /auto-solve-issue #409 --resume

💾 Resume point found:
   Saved at: 2026-03-30T10:45:00Z
   Stopped at: Phase 1.5
   Reason: score_below_threshold

🔄 Resuming workflow...
   Issue: #409
   Mode: auto
   Reset task task_140 to pending
   Continuing execution loop...

→ Re-runs Phase 1.5: eval-plan
→ New score: 95/100 ✅
→ Continues to Phase 2
```

### Scenario 4: Interactive Checkpoint

```
Phase 2.5: review completes
Score: 82/100

⏸️ Checkpoint 2
   Score: 82/100
   Threshold: 90

⚠️ Score 82 < 90

? Continue to next phase?
  [1] Continue - Proceed despite issues
  [2] Stop - Pause workflow to fix issues

User selects: [1]

→ Continues to Phase 3: finish-issue
```

---

**See also:**
- [PHASES.md](./PHASES.md) - Detailed workflow execution
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Error handling
- [EXAMPLES.md](./EXAMPLES.md) - More usage examples
