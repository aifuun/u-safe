#!/usr/bin/env python3
"""
Coordinator - Decision Engine for solve-issue skill

协调器：负责工作流决策和指令写入
- 定义 5-phase workflow
- 写入执行指令（call_skill, checkpoint, complete, error）
- 等待 AI 完成每个 phase
- 根据 checkpoint score 决定是否继续

架构：
  Python (coordinator) → JSON 指令文件 → AI (executor)
"""

import json
import time
import sys
import signal
import atexit
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass, asdict

# Import logger and state_manager
try:
    from . import logger
    from . import state_manager
except ImportError:
    import logger
    import state_manager


@dataclass
class Instruction:
    """指令定义"""
    type: Literal["call_skill", "checkpoint", "complete", "error"]
    phase: str
    skill_name: Optional[str] = None
    skill_args: Optional[str] = None
    message: Optional[str] = None
    checkpoint_data: Optional[Dict] = None


class Coordinator:
    """协调器主类"""

    # 5-phase workflow 定义
    WORKFLOW = [
        {"phase": "1", "skill": "start-issue", "name": "Start Issue"},
        {"phase": "1.5", "skill": "eval-plan", "name": "Evaluate Plan", "checkpoint": True},
        {"phase": "2", "skill": "execute-plan", "name": "Execute Plan"},
        {"phase": "2.5", "skill": "review", "name": "Review Code", "checkpoint": True},
        {"phase": "3", "skill": "finish-issue", "name": "Finish Issue"},
    ]

    def __init__(self, issue_number: int, mode: str = "auto", resume: bool = False):
        """
        初始化协调器

        Args:
            issue_number: GitHub issue 编号
            mode: 执行模式 ("auto" | "interactive")
            resume: 是否从上次中断处恢复
        """
        self.issue_number = issue_number
        self.mode = mode
        self.current_phase_index = 0
        self.resume = resume
        self.completed_phases: List[str] = []

        # 文件路径
        self.repo_root = Path.cwd()
        self.instructions_file = self.repo_root / ".claude/skills/solve-issue/.temp/instructions.json"
        self.completions_file = self.repo_root / ".claude/skills/solve-issue/.temp/completions.json"
        self.state_file = self.repo_root / ".claude/.solve-issue-state.json"

        # 确保目录存在
        self.instructions_file.parent.mkdir(parents=True, exist_ok=True)

        # 初始化日志器
        self.log = logger.init_logger(issue_number)
        self.start_time = time.time()

        # 初始化状态管理器
        self.state_mgr = state_manager.init_state_manager()

        # 处理 resume
        if resume:
            self._load_resume_state()

        # 注册清理函数和信号处理
        atexit.register(self._cleanup_on_exit)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _load_resume_state(self):
        """从保存的状态恢复"""
        resume_info = self.state_mgr.get_resume_info()

        if resume_info is None:
            self.log.warning("No saved state found, starting from beginning")
            self.resume = False
            return

        # 恢复状态
        self.current_phase_index = resume_info["next_phase_index"]
        self.completed_phases = resume_info["completed_phases"]
        self.start_time = time.time() - resume_info["elapsed_time"]

        self.log.info(f"🔄 Resuming from saved state")
        self.log.info(f"   Completed phases: {', '.join(self.completed_phases)}")
        self.log.info(f"   Next phase index: {self.current_phase_index}")

        if resume_info["checkpoint_stopped"]:
            self.log.info(f"   Stopped at checkpoint: Phase {resume_info['checkpoint_phase']} (score: {resume_info['checkpoint_score']})")
        elif resume_info["failed_phase"]:
            self.log.info(f"   Failed at: Phase {resume_info['failed_phase']}")

    def _cleanup_on_exit(self):
        """退出时清理临时文件"""
        try:
            if self.instructions_file.exists():
                self.instructions_file.unlink()
            if self.completions_file.exists():
                self.completions_file.unlink()
            self.log.debug("Temporary files cleaned up")
        except Exception as e:
            if hasattr(self, 'log'):
                self.log.warning(f"Cleanup warning: {e}")
            else:
                print(f"⚠️  Cleanup warning: {e}", file=sys.stderr)

    def _signal_handler(self, signum, frame):
        """信号处理器（Ctrl+C, SIGTERM）"""
        if hasattr(self, 'log'):
            self.log.warning(f"Received signal {signum}, cleaning up...")
            self.log.user_interrupt()
        self._write_instruction(Instruction(
            type="error",
            phase=self.WORKFLOW[self.current_phase_index]["phase"] if self.current_phase_index < len(self.WORKFLOW) else "unknown",
            message="Interrupted by user"
        ))
        sys.exit(1)

    def _report_progress(self):
        """报告当前进度"""
        total_phases = len(self.WORKFLOW)
        completed = len(self.completed_phases)
        percentage = (completed / total_phases) * 100

        self.log.info(f"📊 Progress: {completed}/{total_phases} phases ({percentage:.0f}%)")
        self.log.debug(f"Completed phases: {', '.join(self.completed_phases)}")

    def _show_workflow_overview(self):
        """显示工作流概览"""
        self.log.info("Workflow: 5 phases with 2 automated checkpoints")
        self.log.info("├─ Phase 1: Start Issue (~30s)")
        self.log.info("├─ Phase 1.5: Evaluate Plan (~60s)")
        self.log.info("│  └─ Checkpoint 1: Score-based (auto mode)")
        self.log.info("├─ Phase 2: Execute Plan (~30-60min)")
        self.log.info("├─ Phase 2.5: Review Code (~90s)")
        self.log.info("│  └─ Checkpoint 2: Score-based (auto mode)")
        self.log.info("└─ Phase 3: Finish Issue (~3min)")
        self.log.info("")

    def run(self):
        """主循环：执行完整的 5-phase workflow"""
        self.log.info(f"🚀 solve-issue #{self.issue_number} starting in --{self.mode} mode")
        self.log.info("")
        self._show_workflow_overview()
        self._report_progress()  # Initial progress: 0%

        try:
            # 执行每个 phase（从当前索引开始）
            for i, phase_info in enumerate(self.WORKFLOW):
                # 跳过已完成的 phases（resume 时）
                if i < self.current_phase_index:
                    self.log.debug(f"Skipping completed phase {i}: {phase_info['name']}")
                    continue

                self.current_phase_index = i
                phase_start_time = time.time()
                try:
                    self._execute_phase(phase_info)
                    phase_duration = time.time() - phase_start_time
                    self.log.phase_complete(phase_info["phase"], phase_duration)

                    # 标记 phase 完成
                    self.completed_phases.append(phase_info["phase"])
                    self._save_state()
                    self._report_progress()  # Show progress after each phase
                except TimeoutError as e:
                    phase_duration = time.time() - phase_start_time
                    self.log.phase_error(phase_info["phase"], e, phase_duration)
                    self.log.timeout(phase_info["phase"], 300)
                    self._write_instruction(Instruction(
                        type="error",
                        phase=phase_info["phase"],
                        message=f"Timeout: {str(e)}"
                    ))
                    raise
                except Exception as e:
                    phase_duration = time.time() - phase_start_time
                    self.log.phase_error(phase_info["phase"], e, phase_duration)
                    self._write_instruction(Instruction(
                        type="error",
                        phase=phase_info["phase"],
                        message=f"Phase error: {str(e)}"
                    ))
                    raise

                # 如果是 checkpoint，检查是否需要停止
                if phase_info.get("checkpoint"):
                    should_continue, checkpoint_score = self._handle_checkpoint(phase_info)
                    if not should_continue:
                        # 返回 False 表示停止
                        self.log.info(f"\n⏸️  Stopped at checkpoint: {phase_info['name']}")
                        # 保存 checkpoint 状态
                        state = state_manager.WorkflowState(
                            issue_number=self.issue_number,
                            mode=self.mode,
                            current_phase_index=self.current_phase_index,
                            completed_phases=self.completed_phases,
                            checkpoint_stopped=True,
                            checkpoint_phase=phase_info["phase"],
                            checkpoint_score=checkpoint_score,
                            total_duration=time.time() - self.start_time
                        )
                        self.state_mgr.save_state(state)
                        return

            # 所有 phase 完成
            total_duration = time.time() - self.start_time
            self._report_progress()  # Final progress: 100%

            # 显示完成摘要
            self.log.info("")
            self.log.info(f"✅ All {len(self.WORKFLOW)} phases completed successfully!")
            self.log.info(f"   Phases: {' → '.join(p['phase'] for p in self.WORKFLOW)}")
            self.log.info(f"   Mode: {self.mode}")
            self.log.completion(total_duration)

            self._write_instruction(Instruction(
                type="complete",
                phase="final",
                message="✅ All phases complete! Issue resolved."
            ))

            # 清除状态文件（工作流已完成）
            self.state_mgr.clear_state()
            self._cleanup_on_exit()

        except KeyboardInterrupt:
            self.log.user_interrupt()
            self._write_instruction(Instruction(
                type="error",
                phase=self.WORKFLOW[self.current_phase_index]["phase"] if self.current_phase_index < len(self.WORKFLOW) else "unknown",
                message="Interrupted by user (Ctrl+C)"
            ))
            sys.exit(1)
        except Exception as e:
            self.log.fatal_error(e)
            self._write_instruction(Instruction(
                type="error",
                phase=self.WORKFLOW[self.current_phase_index]["phase"] if self.current_phase_index < len(self.WORKFLOW) else "unknown",
                message=f"Fatal error: {str(e)}"
            ))
            raise

    def _execute_phase(self, phase_info: Dict):
        """
        执行单个 phase

        Args:
            phase_info: phase 配置（skill name, args, checkpoint）
        """
        phase = phase_info["phase"]
        skill = phase_info["skill"]
        name = phase_info["name"]

        self.log.phase_start(phase, name)

        # 构造 skill 参数
        if skill in ["start-issue", "eval-plan", "execute-plan", "finish-issue"]:
            skill_args = str(self.issue_number)
        elif skill == "review":
            skill_args = ""
        else:
            skill_args = ""

        # 如果是 eval-plan 且是 auto 模式，添加 --mode=auto
        if skill == "eval-plan" and self.mode == "auto":
            skill_args += " --mode=auto"

        # 记录 skill 调用
        self.log.skill_call(skill, skill_args)

        # 写入指令：调用 skill
        skill_start_time = time.time()
        self._write_instruction(Instruction(
            type="call_skill",
            phase=phase,
            skill_name=skill,
            skill_args=skill_args,
            message=f"Executing /{skill} {skill_args}"
        ))

        # 等待 AI 完成
        self._wait_for_completion(phase)

        # 记录 skill 完成
        skill_duration = time.time() - skill_start_time
        self.log.skill_complete(skill, skill_duration)

    def _handle_checkpoint(self, phase_info: Dict) -> tuple[bool, int]:
        """
        处理 checkpoint 逻辑

        Args:
            phase_info: phase 配置

        Returns:
            (should_continue, score): True/False = 继续/停止, score = checkpoint 分数
        """
        phase = phase_info["phase"]
        skill = phase_info["skill"]

        # 读取状态文件（eval-plan 或 review 写入的）
        if skill == "eval-plan":
            status_file = self.repo_root / ".claude/.eval-plan-status.json"
        elif skill == "review":
            status_file = self.repo_root / ".claude/.review-status.json"
        else:
            return True  # 非 checkpoint phase，继续

        # 读取 score
        if not status_file.exists():
            self.log.warning(f"Status file not found: {status_file}")
            return (True, 0)  # 降级：继续执行

        try:
            with open(status_file) as f:
                status = json.load(f)
        except json.JSONDecodeError as e:
            self.log.warning(f"Status file corrupted: {e}")
            return (True, 0)  # 降级：继续执行
        except (OSError, IOError) as e:
            self.log.warning(f"Cannot read status file: {e}")
            return (True, 0)  # 降级：继续执行

        score = status.get("score", 0)

        # 验证 score 有效性
        if not isinstance(score, (int, float)) or score < 0 or score > 100:
            self.log.warning(f"Invalid score: {score}, treating as 0")
            score = 0

        # 决策逻辑
        if self.mode == "auto":
            # Auto 模式：score > 90 自动继续，否则停止
            if score > 90:
                self.log.checkpoint(phase, score, self.mode, continued=True)
                return (True, score)
            else:
                self.log.checkpoint(phase, score, self.mode, continued=False)
                self._write_instruction(Instruction(
                    type="checkpoint",
                    phase=phase,
                    message=f"Checkpoint: Score {score}/100 ≤ 90",
                    checkpoint_data=status
                ))
                return (False, score)

        elif self.mode == "interactive":
            # Interactive 模式：总是停止
            self.log.checkpoint(phase, score, self.mode, continued=False)
            self._write_instruction(Instruction(
                type="checkpoint",
                phase=phase,
                message=f"Checkpoint: Manual review required (score: {score}/100)",
                checkpoint_data=status
            ))
            return (False, score)

        return (True, score)

    def _write_instruction(self, instruction: Instruction):
        """
        写入指令到 JSON 文件（原子操作）

        Args:
            instruction: 指令对象
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "issue_number": self.issue_number,
            "instruction": asdict(instruction)
        }

        # 原子写入：先写临时文件，再重命名
        temp_file = self.instructions_file.with_suffix(".tmp")
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=2)

        temp_file.replace(self.instructions_file)

    def _wait_for_completion(self, phase: str, timeout: int = 300):
        """
        等待 AI 完成当前 phase

        Args:
            phase: phase 编号
            timeout: 超时时间（秒）

        Raises:
            TimeoutError: 超时
            json.JSONDecodeError: 完成文件格式错误
        """
        start_time = time.time()

        while True:
            try:
                # 检查完成标记文件
                if self.completions_file.exists():
                    try:
                        with open(self.completions_file) as f:
                            completion = json.load(f)
                    except json.JSONDecodeError as e:
                        self.log.debug(f"Corrupted completion file, retrying... ({e})")
                        time.sleep(1)
                        continue

                    # 验证是否是当前 phase 的完成
                    if completion.get("phase") == phase:
                        # 检查状态
                        if completion.get("status") == "error":
                            error_msg = completion.get("data", {}).get("error", "Unknown error")
                            raise RuntimeError(f"Phase {phase} failed: {error_msg}")

                        # 删除完成标记文件
                        self.completions_file.unlink()
                        return

                # 检查超时
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    raise TimeoutError(f"Phase {phase} timed out after {timeout}s (no completion marker received)")

                # 短暂等待
                time.sleep(1)

            except (OSError, IOError) as e:
                # 文件系统错误（罕见）
                self.log.debug(f"File system error: {e}, retrying...")
                time.sleep(1)

    def _save_state(self):
        """保存当前状态（用于 resume）"""
        state = state_manager.WorkflowState(
            issue_number=self.issue_number,
            mode=self.mode,
            current_phase_index=self.current_phase_index,
            completed_phases=self.completed_phases,
            total_duration=time.time() - self.start_time
        )

        self.state_mgr.save_state(state)
        self.log.debug(f"State saved: phase {self.current_phase_index}, {len(self.completed_phases)} completed")


def main():
    """入口函数"""
    if len(sys.argv) < 2:
        print("Usage: coordinator.py <issue_numbers> [mode] [options]")
        print("  issue_numbers: Single issue (123) or batch ([123,456,789])")
        print("  mode: auto (default) | interactive")
        print("  --resume: Resume from saved state")
        print("  --stop-on-error: Stop batch on first error (default)")
        print("  --continue-on-error: Continue batch even if errors occur")
        sys.exit(1)

    # 解析 issue numbers（单个或批量）
    issues_arg = sys.argv[1]
    if issues_arg.startswith("[") and issues_arg.endswith("]"):
        # 批量模式: [123,456,789]
        issue_numbers = [int(x.strip()) for x in issues_arg[1:-1].split(",")]
        is_batch = True
    else:
        # 单个 issue
        issue_numbers = [int(issues_arg)]
        is_batch = False

    mode = "auto"
    resume = False
    stop_on_error = True

    # 解析参数
    for arg in sys.argv[2:]:
        if arg == "--resume":
            resume = True
        elif arg in ["auto", "interactive"]:
            mode = arg
        elif arg == "--stop-on-error":
            stop_on_error = True
        elif arg == "--continue-on-error":
            stop_on_error = False

    # 执行
    if is_batch and not resume:
        # 批量模式
        run_batch(issue_numbers, mode, stop_on_error)
    else:
        # 单个 issue
        coordinator = Coordinator(issue_numbers[0], mode, resume)
        coordinator.run()


def run_batch(issue_numbers: List[int], mode: str, stop_on_error: bool):
    """
    批量处理多个 issues

    Args:
        issue_numbers: issue 编号列表
        mode: 执行模式
        stop_on_error: 遇到错误时是否停止
    """
    print(f"🚀 Batch mode: processing {len(issue_numbers)} issues")
    print(f"   Issues: {', '.join(f'#{n}' for n in issue_numbers)}")
    print(f"   Mode: {mode}")
    print(f"   Error strategy: {'stop-on-error' if stop_on_error else 'continue-on-error'}\n")

    results = {}

    for i, issue_num in enumerate(issue_numbers, 1):
        print(f"\n{'━' * 60}")
        print(f"Issue #{issue_num} ({i}/{len(issue_numbers)})")
        print(f"{'━' * 60}\n")

        try:
            coordinator = Coordinator(issue_num, mode, resume=False)
            coordinator.run()
            results[issue_num] = {"status": "success"}
            print(f"\n✅ Issue #{issue_num} complete\n")

        except Exception as e:
            results[issue_num] = {"status": "failed", "error": str(e)}
            print(f"\n❌ Issue #{issue_num} failed: {e}\n")

            if stop_on_error:
                print(f"⚠️  Stopping batch (--stop-on-error)")
                break
            else:
                print(f"⚠️  Continuing to next issue (--continue-on-error)")
                continue

    # 最终汇总
    print(f"\n{'━' * 60}")
    print("Batch Summary")
    print(f"{'━' * 60}")

    success_count = sum(1 for r in results.values() if r["status"] == "success")
    failed_count = sum(1 for r in results.values() if r["status"] == "failed")
    skipped_count = len(issue_numbers) - len(results)

    print(f"✅ Success: {success_count}/{len(issue_numbers)}")
    if failed_count > 0:
        print(f"❌ Failed: {failed_count}/{len(issue_numbers)}")
    if skipped_count > 0:
        print(f"⏸️  Skipped: {skipped_count}/{len(issue_numbers)}")

    # 显示失败详情
    if failed_count > 0:
        print(f"\nFailed issues:")
        for issue_num, result in results.items():
            if result["status"] == "failed":
                print(f"  #{issue_num}: {result['error']}")


if __name__ == "__main__":
    main()
