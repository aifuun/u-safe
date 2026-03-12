#!/usr/bin/env python3
"""HTML formatter module.

Generates HTML reports from project overview data.
Replaces format-html.sh per ADR-003.

Example:
    >>> from formatters import html_formatter
    >>> data = collect_all_data()
    >>> report_path = html_formatter.format(data, 'My Project')
    >>> print(f"Report: {report_path}")
"""

from typing import Dict, Any
from datetime import datetime
from pathlib import Path
import json
import webbrowser
import sys


def format(data: Dict[str, Any], project_name: str = 'Project',
           auto_open: bool = True) -> str:
    """
    Generate HTML report from collected data.

    Args:
        data: Dictionary with keys: git, framework, project, work, patterns, health
        project_name: Name of the project (default: 'Project')
        auto_open: Whether to automatically open the report in browser (default: True)

    Returns:
        Path to generated HTML file

    Raises:
        FileNotFoundError: If template file not found
        IOError: If report cannot be written

    Example:
        >>> data = {'git': {...}, 'framework': {...}, ...}
        >>> report = format(data, 'AI Dev', auto_open=False)
        >>> print(f"Report saved to: {report}")
    """
    # Create timestamp
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%S')
    readable_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    # Ensure reports directory exists
    reports_dir = Path('docs/reports')
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Define output file
    sanitized_name = _sanitize_filename(project_name)
    output_file = reports_dir / f"{sanitized_name}-overview-{timestamp}.html"

    # Build JSON data object
    json_data = _build_json_data(data, project_name, readable_timestamp)

    # Read template
    template_path = _get_template_path()
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    template_content = template_path.read_text(encoding='utf-8')

    # Replace placeholder with JSON
    html_content = template_content.replace(
        '/* DATA_PLACEHOLDER */',
        json.dumps(json_data, indent=2, ensure_ascii=False)
    )

    # Write output file
    output_file.write_text(html_content, encoding='utf-8')

    # Auto-open in browser if requested
    if auto_open:
        _open_in_browser(output_file)

    return str(output_file)


def _build_json_data(data: Dict[str, Any], project_name: str,
                     timestamp: str) -> Dict[str, Any]:
    """
    Build JSON data object for template injection.

    Args:
        data: Collected project data
        project_name: Project name
        timestamp: Human-readable timestamp

    Returns:
        Dictionary ready for JSON serialization
    """
    git_data = data.get('git', {})
    framework_data = data.get('framework', {})
    work_data = data.get('work', {})
    project_data = data.get('project', {})
    patterns = data.get('patterns', [])
    health = data.get('health', {})

    # Extract git info
    git_info = {
        'branch': git_data.get('branch', 'unknown'),
        'commit': git_data.get('commit', 'N/A'),
        'commitMessage': git_data.get('commitMessage', ''),
        'staged': git_data.get('staged', 0),
        'unstaged': git_data.get('unstaged', 0),
        'untracked': git_data.get('untracked', 0),
        'recentCommits': git_data.get('recentCommits', [])
    }

    # Extract framework info
    framework_info = {
        'profile': framework_data.get('profile', 'Not installed'),
        'pillars': framework_data.get('pillars', []),
        'pillarCount': framework_data.get('pillarCount', 0),
        'ruleCount': framework_data.get('ruleCount', 0),
        'commandCount': framework_data.get('commandCount', 0)
    }

    # Extract work info
    plans = work_data.get('activePlans', [])
    issues = work_data.get('openIssues', [])

    # Format recommendations
    recommendations = []
    for rec in health.get('recommendations', []):
        # Simple string recommendations from health_calculator
        recommendations.append({
            'title': rec,
            'priority': 'medium',
            'estimate': ''
        })

    # Build complete data object
    return {
        'projectName': project_name,
        'generatedAt': timestamp,
        'git': git_info,
        'framework': framework_info,
        'plans': plans,
        'issues': issues,
        'codeQuality': {
            'healthScore': health.get('score', 0),
            'patterns': patterns,
            'strengths': _identify_strengths(patterns, health),
            'observations': _generate_observations(data),
            'recommendations': recommendations
        },
        'projectInfo': project_data
    }


def _identify_strengths(patterns: list, health: Dict[str, Any]) -> list:
    """
    Identify project strengths based on patterns and health.

    Args:
        patterns: List of detected patterns
        health: Health score data

    Returns:
        List of strength descriptions
    """
    strengths = []

    # Check for strong patterns
    if any('Nominal Types' in p for p in patterns):
        strengths.append('Type-safe design with nominal typing')

    if any('Saga' in p for p in patterns):
        strengths.append('Robust error handling with Saga pattern')

    if any('Testing' in p for p in patterns):
        strengths.append('Comprehensive test coverage')

    if any('Clean Architecture' in p for p in patterns):
        strengths.append('Well-structured layered architecture')

    # Check health score
    score = health.get('score', 0)
    if score >= 85:
        strengths.append(f'Excellent project health ({score}/100)')
    elif score >= 70:
        strengths.append(f'Good project health ({score}/100)')

    return strengths


def _generate_observations(data: Dict[str, Any]) -> list:
    """
    Generate observations about the project.

    Args:
        data: Complete project data

    Returns:
        List of observation strings
    """
    observations = []

    git_data = data.get('git', {})
    framework_data = data.get('framework', {})
    work_data = data.get('work', {})

    # Git observations
    if git_data.get('staged', 0) > 0:
        observations.append(f"Found {git_data['staged']} staged files ready to commit")

    if git_data.get('unstaged', 0) > 5:
        observations.append(f"Large number of unstaged changes ({git_data['unstaged']} files)")

    # Framework observations
    pillar_count = framework_data.get('pillarCount', 0)
    if pillar_count >= 7:
        observations.append(f"Full framework adoption with {pillar_count} Pillars")
    elif pillar_count >= 3:
        observations.append(f"Partial framework adoption ({pillar_count} Pillars)")

    # Work observations
    plan_count = work_data.get('planCount', 0)
    if plan_count > 3:
        observations.append(f"Multiple active plans ({plan_count}), consider prioritizing")

    return observations


def _sanitize_filename(name: str) -> str:
    """
    Sanitize project name for use in filename.

    Args:
        name: Project name

    Returns:
        Sanitized filename component
    """
    # Replace spaces and special chars with hyphens
    sanitized = name.lower()
    sanitized = ''.join(c if c.isalnum() else '-' for c in sanitized)
    # Remove consecutive hyphens
    while '--' in sanitized:
        sanitized = sanitized.replace('--', '-')
    return sanitized.strip('-')


def _get_template_path() -> Path:
    """
    Get path to HTML template file.

    Returns:
        Path to combined-report.html template
    """
    # Template is in scripts/templates/ relative to this file
    script_dir = Path(__file__).parent.parent
    return script_dir / 'templates' / 'combined-report.html'


def _open_in_browser(file_path: Path) -> None:
    """
    Open HTML file in default browser.

    Args:
        file_path: Path to HTML file
    """
    try:
        webbrowser.open(f'file://{file_path.absolute()}')
    except Exception:
        # Silently fail if browser cannot be opened
        pass


if __name__ == '__main__':
    # CLI interface for testing
    import sys

    if len(sys.argv) > 1:
        # Read data from JSON file
        data_file = Path(sys.argv[1])
        if not data_file.exists():
            print(f"Error: File not found: {data_file}", file=sys.stderr)
            sys.exit(1)

        with open(data_file, 'r') as f:
            data = json.load(f)

        project_name = sys.argv[2] if len(sys.argv) > 2 else 'Project'
        auto_open = sys.argv[3].lower() != 'false' if len(sys.argv) > 3 else True
    else:
        # Example data
        data = {
            'git': {
                'branch': 'main',
                'commit': 'abc123def456',
                'commitMessage': 'feat: add Phase 4 migration',
                'staged': 0,
                'unstaged': 2,
                'untracked': 1,
                'recentCommits': [
                    {'hash': 'abc123', 'message': 'feat: add formatters', 'date': '2026-03-09'},
                    {'hash': 'def456', 'message': 'refactor: migrate collectors', 'date': '2026-03-08'}
                ]
            },
            'framework': {
                'profile': 'react-aws',
                'pillars': ['A', 'B', 'K', 'L', 'M', 'Q', 'R'],
                'pillarCount': 7,
                'ruleCount': 42,
                'commandCount': 18
            },
            'work': {
                'planCount': 2,
                'issueCount': 3,
                'activePlans': [
                    {'name': 'Issue #86: Phase 4 Migration', 'progress': '3/7', 'status': 'active'},
                    {'name': 'Issue #90: Documentation', 'progress': '1/4', 'status': 'active'}
                ],
                'openIssues': [
                    {'number': 86, 'title': 'Phase 4 Migration'},
                    {'number': 87, 'title': 'Add tests'},
                    {'number': 90, 'title': 'Update docs'}
                ]
            },
            'project': {
                'description': 'Universal AI-assisted development framework',
                'coreConcept': '18 coding pillars + workflow automation',
                'initialized': '2026-02-15',
                'techStack': {
                    'frontend': 'React + TypeScript',
                    'backend': 'Node.js + Lambda',
                    'auth': 'Cognito',
                    'iac': 'AWS CDK'
                },
                'architecture': {
                    'adrCount': 9,
                    'recentADRs': [
                        {'number': '009', 'title': 'Zustand Vanilla Store', 'status': 'Accepted'},
                        {'number': '008', 'title': 'shadcn/ui Design System', 'status': 'Accepted'}
                    ],
                    'patterns': ['Clean Architecture', 'Headless Pattern', 'Saga Pattern']
                },
                'completed': [
                    {'issue': '#84', 'title': 'Phase 2', 'description': 'Migrate finish-issue scripts'},
                    {'issue': '#85', 'title': 'Phase 3', 'description': 'Migrate collectors'}
                ],
                'documentation': [
                    {'type': 'Architecture', 'title': 'System Design', 'path': 'docs/ARCHITECTURE.md'},
                    {'type': 'ADR', 'title': 'Decision Records', 'path': 'docs/ADRs/'}
                ]
            },
            'patterns': [
                'Nominal Types (Pillar A)',
                'Schema Validation (Pillar B)',
                'Jest Testing',
                'React Frontend',
                'AWS CDK Infrastructure',
                'Saga Pattern',
                'Clean Architecture'
            ],
            'health': {
                'score': 85,
                'grade': 'B+',
                'breakdown': {
                    'git': 25,
                    'tests': 20,
                    'framework': 25,
                    'documentation': 15
                },
                'recommendations': [
                    'Commit uncommitted changes',
                    'Add more test coverage',
                    'Document recent ADRs'
                ]
            }
        }
        project_name = 'AI Dev Framework'
        auto_open = False  # Don't auto-open in test mode

    # Generate report
    try:
        report_path = format(data, project_name, auto_open)
        print(f"✅ HTML report generated: {report_path}")
    except Exception as e:
        print(f"❌ Error generating report: {e}", file=sys.stderr)
        sys.exit(1)
