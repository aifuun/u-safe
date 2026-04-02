"""Overview data collectors module.

This module provides Python-based data collectors for the overview skill,
replacing the legacy Bash scripts per ADR-003.

Each collector module returns structured dictionaries (not string output)
that can be easily serialized to JSON and consumed by the overview formatter.

Example:
    >>> from collectors import git_collector
    >>> data = git_collector.collect_git_status()
    >>> print(data['branch'])
    main
"""

from typing import Dict, Any, List, Protocol


class Collector(Protocol):
    """Base protocol for all data collectors.

    All collector modules should implement functions that:
    - Return Dict[str, Any] (structured data, not strings)
    - Have comprehensive type hints
    - Have docstrings with Args, Returns, Example
    - Handle errors gracefully (return empty/default values)
    - Use shared utilities from _scripts/ where possible
    """

    def collect(self) -> Dict[str, Any]:
        """Collect data and return as structured dictionary."""
        ...


# Export collector modules when implemented
__all__ = [
    'git_collector',
    'project_collector',
    'work_collector',
    'framework_collector',
    'pattern_detector',
]


# Type definitions for collector return values
# These match the JSON structures from the Bash versions

GitStatus = Dict[str, Any]  # {branch, commit, commitMessage, staged, unstaged, untracked}
ProjectInfo = Dict[str, Any]  # {description, techStack, documentation, ...}
WorkInfo = Dict[str, Any]  # {activePlans, tasks, currentIssue, ...}
FrameworkInfo = Dict[str, Any]  # {profile, pillars, pillarCount, ruleCount, ...}
PatternList = List[str]  # ["Clean Architecture", "Jest", ...]


def collect_all() -> Dict[str, Any]:
    """
    Collect data from all collectors.

    Convenience function that runs all collectors and returns
    a combined dictionary with all data.

    Returns:
        Dictionary with keys: git, project, work, framework, patterns

    Example:
        >>> data = collect_all()
        >>> print(data['git']['branch'])
        main
        >>> print(data['framework']['pillarCount'])
        7
    """
    from . import (
        git_collector,
        project_collector,
        work_collector,
        framework_collector,
        pattern_detector,
    )

    return {
        'git': git_collector.collect_git_status(),
        'project': project_collector.collect_project_info(),
        'work': work_collector.collect_work_info(),
        'framework': framework_collector.collect_framework_info(),
        'patterns': pattern_detector.detect_patterns(),
    }
