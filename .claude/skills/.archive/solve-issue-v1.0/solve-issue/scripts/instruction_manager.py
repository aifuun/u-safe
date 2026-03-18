#!/usr/bin/env python3
"""
Instruction Manager - 指令文件读写管理

负责：
- 原子读写指令文件（防止竞态条件）
- 完成标记管理
- 文件锁机制

文件格式：
  instructions.json - Python → AI 的指令
  completions.json - AI → Python 的完成标记
"""

import json
import fcntl
import time
from pathlib import Path
from typing import Dict, Optional
from contextlib import contextmanager


class InstructionManager:
    """指令管理器"""

    def __init__(self, temp_dir: Path):
        """
        初始化

        Args:
            temp_dir: 临时文件目录（.claude/skills/solve-issue/.temp/）
        """
        self.temp_dir = temp_dir
        self.instructions_file = temp_dir / "instructions.json"
        self.completions_file = temp_dir / "completions.json"

        # 确保目录存在
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _file_lock(self, file_path: Path):
        """
        文件锁上下文管理器（防止竞态条件）

        Args:
            file_path: 要锁定的文件路径

        Yields:
            文件对象
        """
        # 确保文件存在
        file_path.touch(exist_ok=True)

        with open(file_path, "r+") as f:
            try:
                # 获取排他锁（阻塞）
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                yield f
            finally:
                # 释放锁
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def write_instruction(self, instruction: Dict):
        """
        原子写入指令

        Args:
            instruction: 指令数据（dict）
        """
        with self._file_lock(self.instructions_file) as f:
            # 清空文件
            f.seek(0)
            f.truncate()

            # 写入新指令
            json.dump(instruction, f, indent=2)

    def read_instruction(self) -> Optional[Dict]:
        """
        原子读取指令

        Returns:
            指令数据（dict）或 None（文件为空或不存在）
        """
        if not self.instructions_file.exists():
            return None

        with self._file_lock(self.instructions_file) as f:
            content = f.read().strip()
            if not content:
                return None

            return json.loads(content)

    def clear_instruction(self):
        """清空指令文件"""
        if self.instructions_file.exists():
            with self._file_lock(self.instructions_file) as f:
                f.seek(0)
                f.truncate()

    def write_completion(self, phase: str, status: str = "success", data: Optional[Dict] = None):
        """
        写入完成标记

        Args:
            phase: phase 编号
            status: 状态（"success" | "error"）
            data: 附加数据（可选）
        """
        completion = {
            "phase": phase,
            "status": status,
            "timestamp": time.time(),
            "data": data or {}
        }

        with self._file_lock(self.completions_file) as f:
            f.seek(0)
            f.truncate()
            json.dump(completion, f, indent=2)

    def read_completion(self) -> Optional[Dict]:
        """
        读取完成标记

        Returns:
            完成数据（dict）或 None
        """
        if not self.completions_file.exists():
            return None

        with self._file_lock(self.completions_file) as f:
            content = f.read().strip()
            if not content:
                return None

            return json.loads(content)

    def clear_completion(self):
        """清空完成标记"""
        if self.completions_file.exists():
            with self._file_lock(self.completions_file) as f:
                f.seek(0)
                f.truncate()

    def wait_for_completion(self, phase: str, timeout: int = 300) -> Dict:
        """
        等待特定 phase 完成

        Args:
            phase: phase 编号
            timeout: 超时时间（秒）

        Returns:
            完成数据

        Raises:
            TimeoutError: 超时
        """
        start_time = time.time()

        while True:
            completion = self.read_completion()

            # 检查是否是目标 phase 的完成
            if completion and completion.get("phase") == phase:
                # 清空完成标记（避免重复读取）
                self.clear_completion()
                return completion

            # 检查超时
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Waiting for phase {phase} timed out after {timeout}s")

            # 短暂等待
            time.sleep(0.5)

    def cleanup(self):
        """清理所有临时文件"""
        self.clear_instruction()
        self.clear_completion()


# 单例模式：全局指令管理器
_manager: Optional[InstructionManager] = None


def get_instruction_manager(temp_dir: Optional[Path] = None) -> InstructionManager:
    """
    获取全局指令管理器（单例）

    Args:
        temp_dir: 临时文件目录（首次调用时需要）

    Returns:
        InstructionManager 实例
    """
    global _manager

    if _manager is None:
        if temp_dir is None:
            # 默认路径
            temp_dir = Path.cwd() / ".claude/skills/solve-issue/.temp"
        _manager = InstructionManager(temp_dir)

    return _manager


# 便捷函数
def write_instruction(instruction: Dict):
    """写入指令（便捷函数）"""
    get_instruction_manager().write_instruction(instruction)


def read_instruction() -> Optional[Dict]:
    """读取指令（便捷函数）"""
    return get_instruction_manager().read_instruction()


def write_completion(phase: str, status: str = "success", data: Optional[Dict] = None):
    """写入完成标记（便捷函数）"""
    get_instruction_manager().write_completion(phase, status, data)


def read_completion() -> Optional[Dict]:
    """读取完成标记（便捷函数）"""
    return get_instruction_manager().read_completion()


def wait_for_completion(phase: str, timeout: int = 300) -> Dict:
    """等待完成（便捷函数）"""
    return get_instruction_manager().wait_for_completion(phase, timeout)


def cleanup():
    """清理（便捷函数）"""
    get_instruction_manager().cleanup()
