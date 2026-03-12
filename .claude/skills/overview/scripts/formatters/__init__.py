"""Overview formatters module.

This module provides formatting capabilities for the overview skill,
replacing Bash scripts with Python per ADR-003.

Formatters:
- health_calculator: Calculate project health score (0-100)
- terminal_formatter: ANSI-colored terminal output
- html_formatter: Jinja2-based HTML report generation

Example:
    >>> from formatters import terminal_formatter
    >>> data = collect_all_data()
    >>> output = terminal_formatter.format(data)
    >>> print(output)
"""

__all__ = [
    'health_calculator',
    'terminal_formatter',
    'html_formatter',
]
