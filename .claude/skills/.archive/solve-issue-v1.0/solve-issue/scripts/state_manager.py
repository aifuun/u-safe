#!/usr/bin/env python3
"""
State Manager - 状态管理和中断恢复

负责：
- 读写 .claude/.solve-issue-state.json
- Resume 功能（--resume）
- 中断恢复
- 状态持久化
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class WorkflowState:
    """工作流状态"""
    issue_number: int
    mode: str  # "auto" | "interactive"
    current_phase_index: int
    completed_phases: List[str]
    failed_phase: Optional[str] = None
    checkpoint_stopped: bool = False
    checkpoint_phase: Optional[str] = None
    checkpoint_score: Optional[int] = None
    started_at: Optional[str] = None
    updated_at: Optional[str] = None
    total_duration: float = 0.0


class StateManager:
    """状态管理器"""

    def __init__(self, state_file: Optional[Path] = None):
        """
        初始化状态管理器

        Args:
            state_file: 状态文件路径（默认：.claude/.solve-issue-state.json）
        """
        if state_file is None:
            state_file = Path.cwd() / ".claude/.solve-issue-state.json"

        self.state_file = state_file
        self.state: Optional[WorkflowState] = None

    def save_state(self, state: WorkflowState):
        """
        保存状态到文件

        Args:
            state: 工作流状态
        """
        # 更新时间戳
        state.updated_at = datetime.now().isoformat()
        if state.started_at is None:
            state.started_at = state.updated_at

        # 写入文件（原子操作）
        temp_file = self.state_file.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(asdict(state), f, indent=2)

        temp_file.replace(self.state_file)
        self.state = state

    def load_state(self) -> Optional[WorkflowState]:
        """
        从文件加载状态

        Returns:
            工作流状态，如果文件不存在则返回 None
        """
        if not self.state_file.exists():
            return None

        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.state = WorkflowState(**data)
            return self.state

        except (json.JSONDecodeError, TypeError, KeyError) as e:
            print(f"⚠️  Warning: Corrupted state file ({e}), ignoring...")
            return None

    def clear_state(self):
        """清除状态文件"""
        if self.state_file.exists():
            self.state_file.unlink()
        self.state = None

    def can_resume(self) -> bool:
        """
        检查是否可以恢复

        Returns:
            True 如果有有效的状态可以恢复
        """
        if self.state is None:
            self.load_state()

        return self.state is not None and (
            self.state.checkpoint_stopped or
            self.state.failed_phase is not None
        )

    def get_resume_info(self) -> Optional[Dict]:
        """
        获取恢复信息

        Returns:
            恢复信息字典，如果无法恢复则返回 None
        """
        if not self.can_resume():
            return None

        state = self.state
        if state is None:
            return None

        # 计算下一个 phase 索引
        next_phase_index = state.current_phase_index
        if state.checkpoint_stopped:
            # Checkpoint 停止：继续当前 phase 的下一个阶段
            next_phase_index = state.current_phase_index + 1
        elif state.failed_phase:
            # 失败：重试当前 phase
            next_phase_index = state.current_phase_index

        return {
            "issue_number": state.issue_number,
            "mode": state.mode,
            "next_phase_index": next_phase_index,
            "completed_phases": state.completed_phases,
            "checkpoint_stopped": state.checkpoint_stopped,
            "checkpoint_phase": state.checkpoint_phase,
            "checkpoint_score": state.checkpoint_score,
            "failed_phase": state.failed_phase,
            "elapsed_time": state.total_duration
        }

    def mark_phase_complete(self, phase: str):
        """
        标记 phase 完成

        Args:
            phase: phase 编号
        """
        if self.state is None:
            raise RuntimeError("State not initialized")

        if phase not in self.state.completed_phases:
            self.state.completed_phases.append(phase)

        self.save_state(self.state)

    def mark_checkpoint_stop(self, phase: str, score: int):
        """
        标记在 checkpoint 停止

        Args:
            phase: phase 编号
            score: checkpoint 分数
        """
        if self.state is None:
            raise RuntimeError("State not initialized")

        self.state.checkpoint_stopped = True
        self.state.checkpoint_phase = phase
        self.state.checkpoint_score = score

        self.save_state(self.state)

    def mark_phase_failed(self, phase: str):
        """
        标记 phase 失败

        Args:
            phase: phase 编号
        """
        if self.state is None:
            raise RuntimeError("State not initialized")

        self.state.failed_phase = phase

        self.save_state(self.state)

    def update_progress(self, current_phase_index: int, total_duration: float):
        """
        更新进度

        Args:
            current_phase_index: 当前 phase 索引
            total_duration: 总持续时间（秒）
        """
        if self.state is None:
            raise RuntimeError("State not initialized")

        self.state.current_phase_index = current_phase_index
        self.state.total_duration = total_duration

        self.save_state(self.state)


# 全局状态管理器（单例模式）
_state_manager: Optional[StateManager] = None


def init_state_manager(state_file: Optional[Path] = None) -> StateManager:
    """
    初始化全局状态管理器

    Args:
        state_file: 状态文件路径（可选）

    Returns:
        StateManager 实例
    """
    global _state_manager
    _state_manager = StateManager(state_file)
    return _state_manager


def get_state_manager() -> StateManager:
    """
    获取全局状态管理器

    Returns:
        StateManager 实例

    Raises:
        RuntimeError: 如果状态管理器未初始化
    """
    if _state_manager is None:
        # 自动初始化（使用默认路径）
        return init_state_manager()
    return _state_manager


# 便捷函数
def save_state(state: WorkflowState):
    """保存状态（便捷函数）"""
    get_state_manager().save_state(state)


def load_state() -> Optional[WorkflowState]:
    """加载状态（便捷函数）"""
    return get_state_manager().load_state()


def clear_state():
    """清除状态（便捷函数）"""
    get_state_manager().clear_state()


def can_resume() -> bool:
    """检查是否可以恢复（便捷函数）"""
    return get_state_manager().can_resume()


def get_resume_info() -> Optional[Dict]:
    """获取恢复信息（便捷函数）"""
    return get_state_manager().get_resume_info()


def mark_phase_complete(phase: str):
    """标记 phase 完成（便捷函数）"""
    get_state_manager().mark_phase_complete(phase)


def mark_checkpoint_stop(phase: str, score: int):
    """标记 checkpoint 停止（便捷函数）"""
    get_state_manager().mark_checkpoint_stop(phase, score)


def mark_phase_failed(phase: str):
    """标记 phase 失败（便捷函数）"""
    get_state_manager().mark_phase_failed(phase)


def update_progress(current_phase_index: int, total_duration: float):
    """更新进度（便捷函数）"""
    get_state_manager().update_progress(current_phase_index, total_duration)
