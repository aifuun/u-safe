#!/usr/bin/env python3
"""Terminal formatter module.

Formats project overview data for terminal display with ANSI colors.
Replaces format-terminal.sh per ADR-003.

Example:
    >>> from formatters import terminal_formatter
    >>> data = collect_all_data()
    >>> output = terminal_formatter.format(data)
    >>> print(output)
"""

from typing import Dict, Any, List
import shutil


# ANSI color codes
class Colors:
    """ANSI color constants for terminal output."""
    CYAN = '\033[0;36m'
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    NC = '\033[0m'  # No Color


def format(data: Dict[str, Any], project_name: str = 'Project') -> str:
    """
    Format collected data for terminal display.

    Args:
        data: Dictionary with keys: git, framework, project, work, patterns, health
        project_name: Name of the project (default: 'Project')

    Returns:
        Formatted string with ANSI colors ready for terminal output

    Example:
        >>> data = {'git': {...}, 'framework': {...}, ...}
        >>> output = format(data, 'My Project')
        >>> print(output)
    """
    sections = []

    # Header
    sections.append(_format_header(project_name))

    # Git Section
    sections.append(_format_git_section(data.get('git', {})))

    # Framework Section
    sections.append(_format_framework_section(data.get('framework', {})))

    # Active Work Section
    sections.append(_format_work_section(data.get('work', {})))

    # Code Quality Section
    sections.append(_format_quality_section(
        data.get('patterns', []),
        data.get('health', {})
    ))

    return '\n\n'.join(sections) + '\n'


def _format_header(project_name: str) -> str:
    """Format the header section."""
    term_width = shutil.get_terminal_size((80, 20)).columns
    separator = '=' * min(term_width, 80)

    return f"""{Colors.BOLD}{Colors.CYAN}{separator}
📊 {project_name} - Development Status
{separator}{Colors.NC}"""


def _format_git_section(git_data: Dict[str, Any]) -> str:
    """Format the Git status section."""
    branch = git_data.get('branch', 'unknown')
    commit = git_data.get('commit', 'N/A')[:8]
    staged = git_data.get('staged', 0)
    unstaged = git_data.get('unstaged', 0)
    untracked = git_data.get('untracked', 0)

    # Status indicator
    if staged == 0 and unstaged == 0 and untracked == 0:
        status = f"{Colors.GREEN}✅ Clean{Colors.NC}"
    elif staged > 0:
        status = f"{Colors.YELLOW}⚠️ Staged changes{Colors.NC}"
    else:
        status = f"{Colors.YELLOW}⚠️ Uncommitted{Colors.NC}"

    lines = [
        f"{Colors.BLUE}🔀 Git Status{Colors.NC}",
        f"  Branch:  {Colors.CYAN}{branch}{Colors.NC}",
        f"  Commit:  {Colors.DIM}{commit}{Colors.NC}",
        f"  Status:  {status}",
    ]

    # Show file counts if non-zero
    if staged > 0 or unstaged > 0 or untracked > 0:
        details = []
        if staged > 0:
            details.append(f"{staged} staged")
        if unstaged > 0:
            details.append(f"{unstaged} unstaged")
        if untracked > 0:
            details.append(f"{untracked} untracked")
        lines.append(f"  Files:   {', '.join(details)}")

    return '\n'.join(lines)


def _format_framework_section(framework_data: Dict[str, Any]) -> str:
    """Format the Framework section."""
    profile = framework_data.get('profile', 'Not installed')
    pillar_count = framework_data.get('pillarCount', 0)
    rule_count = framework_data.get('ruleCount', 0)
    command_count = framework_data.get('commandCount', 0)

    lines = [
        f"{Colors.BLUE}⚙️ Framework{Colors.NC}",
        f"  Profile:  {Colors.CYAN}{profile}{Colors.NC}",
    ]

    if profile != 'Not installed':
        lines.extend([
            f"  Pillars:  {pillar_count}",
            f"  Rules:    {rule_count}",
            f"  Commands: {command_count}",
        ])
    else:
        lines.append(f"  {Colors.DIM}(Framework not detected){Colors.NC}")

    return '\n'.join(lines)


def _format_work_section(work_data: Dict[str, Any]) -> str:
    """Format the Active Work section."""
    plan_count = work_data.get('planCount', 0)
    issue_count = work_data.get('issueCount', 0)
    active_plans = work_data.get('activePlans', [])

    lines = [
        f"{Colors.BLUE}📋 Active Work{Colors.NC}",
        f"  Plans:  {plan_count}",
        f"  Issues: {issue_count}",
    ]

    # Show active plan details
    if active_plans:
        lines.append(f"\n  {Colors.BOLD}Current Plans:{Colors.NC}")
        for plan in active_plans[:3]:  # Show top 3
            name = plan.get('name', 'Unknown')
            progress = plan.get('progress', 'N/A')
            lines.append(f"    • {name} ({progress})")

        if len(active_plans) > 3:
            remaining = len(active_plans) - 3
            lines.append(f"    {Colors.DIM}... and {remaining} more{Colors.NC}")
    else:
        lines.append(f"  {Colors.DIM}(No active plans){Colors.NC}")

    return '\n'.join(lines)


def _format_quality_section(patterns: List[str], health: Dict[str, Any]) -> str:
    """Format the Code Quality section."""
    score = health.get('score', 0)
    grade = health.get('grade', 'N/A')
    recommendations = health.get('recommendations', [])

    # Health score color
    if score >= 85:
        score_color = Colors.GREEN
        score_emoji = "✅"
    elif score >= 70:
        score_color = Colors.YELLOW
        score_emoji = "⚠️"
    else:
        score_color = Colors.RED
        score_emoji = "❌"

    lines = [
        f"{Colors.BLUE}✨ Code Quality{Colors.NC}",
        f"  Health:  {score_color}{score_emoji} {score}/100 (Grade: {grade}){Colors.NC}",
    ]

    # Show patterns
    if patterns:
        lines.append(f"  Patterns: {len(patterns)} detected")
        # Show first few patterns
        for pattern in patterns[:5]:
            lines.append(f"    • {Colors.DIM}{pattern}{Colors.NC}")
        if len(patterns) > 5:
            remaining = len(patterns) - 5
            lines.append(f"    {Colors.DIM}... and {remaining} more{Colors.NC}")
    else:
        lines.append(f"  Patterns: {Colors.DIM}None detected{Colors.NC}")

    # Show recommendations
    if recommendations:
        lines.append(f"\n  {Colors.BOLD}Recommendations:{Colors.NC}")
        for rec in recommendations[:3]:  # Show top 3
            lines.append(f"    {Colors.YELLOW}→{Colors.NC} {rec}")

    return '\n'.join(lines)


def _truncate(text: str, max_length: int) -> str:
    """
    Truncate text to max_length, adding ellipsis if needed.

    Args:
        text: Text to truncate
        max_length: Maximum length including ellipsis

    Returns:
        Truncated text with '...' if longer than max_length
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'


if __name__ == '__main__':
    # CLI interface for testing
    import json
    import sys

    if len(sys.argv) > 1:
        # Read data from file
        with open(sys.argv[1], 'r') as f:
            data = json.load(f)
        project_name = sys.argv[2] if len(sys.argv) > 2 else 'Project'
    else:
        # Example data
        data = {
            'git': {
                'branch': 'main',
                'commit': 'abc123def456',
                'staged': 0,
                'unstaged': 2,
                'untracked': 1
            },
            'framework': {
                'profile': 'react-aws',
                'pillarCount': 7,
                'ruleCount': 42,
                'commandCount': 18
            },
            'work': {
                'planCount': 2,
                'issueCount': 5,
                'activePlans': [
                    {'name': 'Issue #86: Phase 4 Migration', 'progress': '3/7'},
                    {'name': 'Issue #90: Documentation Update', 'progress': '1/4'}
                ]
            },
            'patterns': [
                'Nominal Types (Pillar A)',
                'Schema Validation (Pillar B)',
                'Jest Testing',
                'React Frontend',
                'AWS CDK Infrastructure'
            ],
            'health': {
                'score': 85,
                'grade': 'B+',
                'recommendations': [
                    'Commit uncommitted changes',
                    'Add more test coverage'
                ]
            }
        }
        project_name = 'AI Dev Framework'

    output = format(data, project_name)
    print(output)
