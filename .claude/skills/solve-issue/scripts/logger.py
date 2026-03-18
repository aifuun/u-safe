#!/usr/bin/env python3
"""
Logger - Execution Logging and Progress Tracking

负责：
- 执行日志写入 logs/solve-issue-{N}.log
- 进度追踪（时间戳、phase、状态）
- 错误诊断信息
- 多级日志（DEBUG, INFO, WARNING, ERROR）
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class SolveIssueLogger:
    """solve-issue 专用日志器"""

    def __init__(self, issue_number: int, log_dir: Optional[Path] = None):
        """
        初始化日志器

        Args:
            issue_number: GitHub issue 编号
            log_dir: 日志目录（默认：.claude/skills/solve-issue/logs/）
        """
        self.issue_number = issue_number

        # 日志文件路径
        if log_dir is None:
            log_dir = Path.cwd() / ".claude/skills/solve-issue/logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        self.log_file = log_dir / f"solve-issue-{issue_number}.log"

        # 创建 logger
        self.logger = logging.getLogger(f"solve-issue-{issue_number}")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers = []  # 清空现有 handlers

        # 文件 handler（所有级别）
        file_handler = logging.FileHandler(self.log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # 控制台 handler（INFO 及以上）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # 写入启动标记
        self._log_separator()
        self.logger.info(f"🚀 solve-issue #{issue_number} started")
        self.logger.info(f"   Log file: {self.log_file}")

    def _log_separator(self):
        """写入分隔线"""
        separator = "=" * 80
        # 直接写入文件（不通过 logger，避免时间戳）
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{separator}\n")

    def phase_start(self, phase: str, name: str):
        """
        记录 phase 开始

        Args:
            phase: phase 编号
            name: phase 名称
        """
        self.logger.info(f"━━━ Phase {phase}: {name} ━━━")
        self.logger.debug(f"Phase {phase} started")

    def phase_complete(self, phase: str, duration: float):
        """
        记录 phase 完成

        Args:
            phase: phase 编号
            duration: 持续时间（秒）
        """
        self.logger.info(f"✅ Phase {phase} complete ({duration:.1f}s)")
        self.logger.debug(f"Phase {phase} completed in {duration:.2f}s")

    def phase_error(self, phase: str, error: Exception, duration: float):
        """
        记录 phase 错误

        Args:
            phase: phase 编号
            error: 异常对象
            duration: 持续时间（秒）
        """
        self.logger.error(f"❌ Phase {phase} failed after {duration:.1f}s")
        self.logger.error(f"   Error: {error}")
        self.logger.debug(f"Exception details:", exc_info=True)

    def checkpoint(self, phase: str, score: int, mode: str, continued: bool):
        """
        记录 checkpoint

        Args:
            phase: phase 编号
            score: 评分
            mode: 模式（auto | interactive）
            continued: 是否继续
        """
        action = "continuing" if continued else "stopping"
        symbol = "✅" if continued else "⏸️"

        self.logger.info(f"📊 Checkpoint: Phase {phase}")
        self.logger.info(f"   Score: {score}/100")
        self.logger.info(f"   Mode: {mode}")
        self.logger.info(f"   {symbol} {action.capitalize()}")

        self.logger.debug(f"Checkpoint decision: phase={phase}, score={score}, mode={mode}, continued={continued}")

    def skill_call(self, skill_name: str, args: str):
        """
        记录 skill 调用

        Args:
            skill_name: skill 名称
            args: skill 参数
        """
        self.logger.info(f"📞 Calling /{skill_name} {args}")
        self.logger.debug(f"Skill invocation: {skill_name} with args: {args}")

    def skill_complete(self, skill_name: str, duration: float):
        """
        记录 skill 完成

        Args:
            skill_name: skill 名称
            duration: 持续时间（秒）
        """
        self.logger.debug(f"Skill {skill_name} completed in {duration:.2f}s")

    def timeout(self, phase: str, timeout_seconds: int):
        """
        记录超时

        Args:
            phase: phase 编号
            timeout_seconds: 超时时间
        """
        self.logger.error(f"⏱️  Timeout: Phase {phase} exceeded {timeout_seconds}s")
        self.logger.debug(f"Timeout details: phase={phase}, limit={timeout_seconds}s")

    def user_interrupt(self):
        """记录用户中断（Ctrl+C）"""
        self.logger.warning("⚠️  Interrupted by user (Ctrl+C)")
        self.logger.debug("User interrupt signal received")

    def fatal_error(self, error: Exception):
        """
        记录致命错误

        Args:
            error: 异常对象
        """
        self.logger.error(f"💥 Fatal error: {error}")
        self.logger.debug("Fatal error details:", exc_info=True)

    def completion(self, total_duration: float):
        """
        记录完成

        Args:
            total_duration: 总持续时间（秒）
        """
        self.logger.info(f"🎉 Issue #{self.issue_number} complete!")
        self.logger.info(f"   Total time: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")
        self.logger.debug(f"Workflow completed in {total_duration:.2f}s")
        self._log_separator()

    def debug(self, message: str):
        """调试日志"""
        self.logger.debug(message)

    def info(self, message: str):
        """信息日志"""
        self.logger.info(message)

    def warning(self, message: str):
        """警告日志"""
        self.logger.warning(message)

    def error(self, message: str):
        """错误日志"""
        self.logger.error(message)


# 全局 logger 实例（单例模式）
_logger: Optional[SolveIssueLogger] = None


def init_logger(issue_number: int, log_dir: Optional[Path] = None) -> SolveIssueLogger:
    """
    初始化全局 logger

    Args:
        issue_number: GitHub issue 编号
        log_dir: 日志目录（可选）

    Returns:
        SolveIssueLogger 实例
    """
    global _logger
    _logger = SolveIssueLogger(issue_number, log_dir)
    return _logger


def get_logger() -> SolveIssueLogger:
    """
    获取全局 logger

    Returns:
        SolveIssueLogger 实例

    Raises:
        RuntimeError: 如果 logger 未初始化
    """
    if _logger is None:
        raise RuntimeError("Logger not initialized. Call init_logger() first.")
    return _logger


# 便捷函数
def phase_start(phase: str, name: str):
    """记录 phase 开始（便捷函数）"""
    get_logger().phase_start(phase, name)


def phase_complete(phase: str, duration: float):
    """记录 phase 完成（便捷函数）"""
    get_logger().phase_complete(phase, duration)


def phase_error(phase: str, error: Exception, duration: float):
    """记录 phase 错误（便捷函数）"""
    get_logger().phase_error(phase, error, duration)


def checkpoint(phase: str, score: int, mode: str, continued: bool):
    """记录 checkpoint（便捷函数）"""
    get_logger().checkpoint(phase, score, mode, continued)


def skill_call(skill_name: str, args: str):
    """记录 skill 调用（便捷函数）"""
    get_logger().skill_call(skill_name, args)


def skill_complete(skill_name: str, duration: float):
    """记录 skill 完成（便捷函数）"""
    get_logger().skill_complete(skill_name, duration)


def timeout(phase: str, timeout_seconds: int):
    """记录超时（便捷函数）"""
    get_logger().timeout(phase, timeout_seconds)


def user_interrupt():
    """记录用户中断（便捷函数）"""
    get_logger().user_interrupt()


def fatal_error(error: Exception):
    """记录致命错误（便捷函数）"""
    get_logger().fatal_error(error)


def completion(total_duration: float):
    """记录完成（便捷函数）"""
    get_logger().completion(total_duration)


def debug(message: str):
    """调试日志（便捷函数）"""
    get_logger().debug(message)


def info(message: str):
    """信息日志（便捷函数）"""
    get_logger().info(message)


def warning(message: str):
    """警告日志（便捷函数）"""
    get_logger().warning(message)


def error(message: str):
    """错误日志（便捷函数）"""
    get_logger().error(message)
