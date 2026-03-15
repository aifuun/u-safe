#!/usr/bin/env python3
"""Project health calculator module.

Calculates overall project health score (0-100) based on multiple metrics.
Replaces calculate-health.sh per ADR-003.

Example:
    >>> from formatters import health_calculator
    >>> data = {'git': {...}, 'framework': {...}, 'tests': 42}
    >>> health = health_calculator.calculate(data)
    >>> print(f"Health: {health['score']}/100")
"""

from typing import Dict, Any, List


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate overall project health score.

    Aggregates multiple health metrics into a 0-100 score with breakdown.

    Args:
        data: Dictionary with keys: git, framework, project, work, patterns

    Returns:
        Dictionary with:
        - score (int): Overall health 0-100
        - breakdown (Dict): Individual metric scores
        - recommendations (List[str]): Improvement suggestions

    Example:
        >>> data = collect_all_data()
        >>> health = calculate(data)
        >>> print(health['score'])
        85
    """
    breakdown = {}
    recommendations = []

    # Git health (0-30 points)
    git_score = calculate_git_health(data.get('git', {}))
    breakdown['git'] = git_score
    if git_score < 25:
        recommendations.append('Commit or stash uncommitted changes')

    # Test coverage (0-25 points)
    test_score = calculate_test_score(data.get('patterns', []))
    breakdown['tests'] = test_score
    if test_score < 15:
        recommendations.append('Add more test coverage')

    # Framework adoption (0-25 points)
    framework_score = calculate_framework_score(data.get('framework', {}))
    breakdown['framework'] = framework_score
    if framework_score < 15:
        recommendations.append('Install framework components')

    # Documentation (0-20 points)
    doc_score = calculate_documentation_score(data.get('project', {}))
    breakdown['documentation'] = doc_score
    if doc_score < 10:
        recommendations.append('Add project documentation')

    # Calculate overall score
    total_score = sum(breakdown.values())

    return {
        'score': min(100, total_score),
        'grade': get_grade(total_score),
        'breakdown': breakdown,
        'recommendations': recommendations
    }


def calculate_git_health(git_data: Dict[str, Any]) -> int:
    """
    Calculate git health score (0-30).

    Factors:
    - No uncommitted changes: +15
    - Synced with remote: +10
    - Recent commit activity: +5

    Args:
        git_data: Git status dict from git_collector

    Returns:
        Score 0-30
    """
    score = 0

    # Clean working directory (15 points)
    staged = git_data.get('staged', 0)
    unstaged = git_data.get('unstaged', 0)
    untracked = git_data.get('untracked', 0)

    if staged == 0 and unstaged == 0 and untracked == 0:
        score += 15
    elif staged + unstaged + untracked <= 3:
        score += 10
    elif staged + unstaged + untracked <= 10:
        score += 5

    # Branch synced (10 points)
    branch = git_data.get('branch', 'unknown')
    if branch not in ('unknown', 'detached'):
        score += 10

    # Has commits (5 points)
    commit = git_data.get('commit', 'N/A')
    if commit != 'N/A':
        score += 5

    return score


def calculate_test_score(patterns: List[str]) -> int:
    """
    Calculate test coverage score (0-25).

    Factors:
    - Has testing framework: +15
    - Has test files: +10

    Args:
        patterns: List of detected patterns

    Returns:
        Score 0-25
    """
    score = 0

    # Check for testing frameworks
    test_frameworks = [
        'Jest Testing',
        'Vitest Testing',
        'Mocha Testing',
        'Pytest',
        'React Testing Library',
        'Cypress E2E',
        'Playwright E2E'
    ]

    has_test_framework = any(fw in patterns for fw in test_frameworks)

    if has_test_framework:
        score += 15

    # Generic testing framework detected
    if 'Testing Framework' in patterns:
        score += 10

    return score


def calculate_framework_score(framework_data: Dict[str, Any]) -> int:
    """
    Calculate framework adoption score (0-25).

    Factors:
    - Framework installed: +10
    - Has active Pillars: +10 (2 points per pillar, max 10)
    - Has rules: +5

    Args:
        framework_data: Framework config dict

    Returns:
        Score 0-25
    """
    score = 0

    profile = framework_data.get('profile', 'Not installed')
    if profile != 'Not installed':
        score += 10

    # Pillar adoption (2 points each, max 10)
    pillar_count = framework_data.get('pillarCount', 0)
    score += min(10, pillar_count * 2)

    # Rules present (5 points)
    rule_count = framework_data.get('ruleCount', 0)
    if rule_count > 0:
        score += 5

    return score


def calculate_documentation_score(project_data: Dict[str, Any]) -> int:
    """
    Calculate documentation score (0-20).

    Factors:
    - Has project description: +10
    - Has ADRs: +10 (2 points per ADR, max 10)

    Args:
        project_data: Project metadata dict

    Returns:
        Score 0-20
    """
    score = 0

    description = project_data.get('description', '')
    if description and description != 'No project description available':
        score += 10

    # ADR count (2 points each, max 10)
    architecture = project_data.get('architecture', {})
    adr_count = architecture.get('adrCount', 0)
    score += min(10, adr_count * 2)

    return score


def get_grade(score: int) -> str:
    """
    Convert numeric score to letter grade.

    Args:
        score: Health score 0-100

    Returns:
        Letter grade: A+, A, B+, B, C+, C, D, F
    """
    if score >= 95:
        return 'A+'
    elif score >= 90:
        return 'A'
    elif score >= 85:
        return 'B+'
    elif score >= 80:
        return 'B'
    elif score >= 75:
        return 'C+'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'


def generate_recommendations(data: Dict[str, Any]) -> List[str]:
    """
    Generate actionable recommendations for improvement.

    Args:
        data: Full project data

    Returns:
        List of recommendation strings
    """
    recommendations = []

    git_data = data.get('git', {})
    framework_data = data.get('framework', {})
    project_data = data.get('project', {})

    # Git recommendations
    unstaged = git_data.get('unstaged', 0)
    if unstaged > 0:
        recommendations.append(f'Commit {unstaged} unstaged files')

    # Framework recommendations
    profile = framework_data.get('profile', 'Not installed')
    if profile == 'Not installed':
        recommendations.append('Install AI development framework')

    pillar_count = framework_data.get('pillarCount', 0)
    if pillar_count < 3:
        recommendations.append('Add more Pillars for better patterns')

    # Documentation recommendations
    adr_count = project_data.get('architecture', {}).get('adrCount', 0)
    if adr_count == 0:
        recommendations.append('Create Architecture Decision Records')

    return recommendations[:5]  # Return top 5


if __name__ == '__main__':
    # CLI interface for testing
    import json
    import sys

    if len(sys.argv) > 1:
        # Read data from file or stdin
        with open(sys.argv[1], 'r') as f:
            data = json.load(f)
    else:
        # Example data
        data = {
            'git': {'staged': 0, 'unstaged': 0, 'untracked': 0, 'branch': 'main', 'commit': 'abc123'},
            'framework': {'profile': 'react-aws', 'pillarCount': 7, 'ruleCount': 42},
            'project': {'description': 'AI Dev Framework', 'architecture': {'adrCount': 3}},
            'patterns': ['Jest Testing', 'React Frontend', 'AWS CDK Infrastructure']
        }

    health = calculate(data)
    print(json.dumps(health, indent=2))
