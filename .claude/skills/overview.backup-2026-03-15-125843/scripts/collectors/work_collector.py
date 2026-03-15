#!/usr/bin/env python3
"""Active work (plans and issues) data collection module.

Collects information about active implementation plans and open GitHub issues.
Replaces collect-work.sh per ADR-003.

Example:
    >>> from collectors import work_collector
    >>> info = work_collector.collect_work_info()
    >>> print(f"Active plans: {info['planCount']}")
    >>> print(f"Open issues: {info['issueCount']}")
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List

# Add _shared to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / '_shared'))

from fs_utils import find_files


def collect_active_plans() -> Dict[str, Any]:
    """
    Collect information about active implementation plans.

    Scans .claude/plans/active/ for plan files and extracts metadata.

    Returns:
        Dictionary with keys:
        - plans (List[Dict]): List of plan metadata
        - planCount (int): Number of active plans

    Example:
        >>> data = collect_active_plans()
        >>> for plan in data['plans']:
        ...     print(plan['name'])
        issue-85-plan
    """
    result = {
        'plans': [],
        'planCount': 0
    }

    plans_dir = Path('.claude/plans/active')
    if not plans_dir.is_dir():
        return result

    # Find all markdown files in active plans directory
    plan_files = sorted(plans_dir.glob('*.md'))

    for plan_file in plan_files:
        plan_name = plan_file.stem  # filename without extension

        # Try to extract additional metadata from plan file
        progress = 'unknown'
        try:
            with open(plan_file, 'r', encoding='utf-8') as f:
                content = f.read()

                # Look for progress indicators
                if '## Progress' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if '## Progress' in line:
                            # Count checkboxes after Progress header
                            progress_lines = lines[i+1:i+20]  # Look ahead 20 lines
                            total = sum(1 for l in progress_lines if '- [ ]' in l or '- [x]' in l)
                            completed = sum(1 for l in progress_lines if '- [x]' in l)
                            if total > 0:
                                progress = f"{completed}/{total}"
                            break
        except (IOError, UnicodeDecodeError):
            pass

        result['plans'].append({
            'name': plan_name,
            'status': 'active',
            'progress': progress
        })

    result['planCount'] = len(result['plans'])
    return result


def collect_open_issues(limit: int = 10) -> Dict[str, Any]:
    """
    Collect information about open GitHub issues.

    Uses gh CLI to fetch open issues from the current repository.

    Args:
        limit: Maximum number of issues to return (default: 10)

    Returns:
        Dictionary with keys:
        - issues (List[Dict]): List of issue metadata
        - issueCount (int): Number of open issues

    Example:
        >>> data = collect_open_issues(5)
        >>> for issue in data['issues']:
        ...     print(f"#{issue['number']}: {issue['title']}")
        #85: Phase 3: Migrate overview data collection
    """
    result = {
        'issues': [],
        'issueCount': 0
    }

    try:
        # Check if gh CLI is available
        check = subprocess.run(
            ['gh', '--version'],
            capture_output=True,
            text=True
        )
        if check.returncode != 0:
            return result

        # Fetch open issues
        proc = subprocess.run(
            ['gh', 'issue', 'list',
             '--state', 'open',
             '--limit', str(limit),
             '--json', 'number,title,state'],
            capture_output=True,
            text=True
        )

        if proc.returncode == 0 and proc.stdout.strip():
            issues = json.loads(proc.stdout)
            result['issues'] = issues
            result['issueCount'] = len(issues)

    except (FileNotFoundError, json.JSONDecodeError, subprocess.SubprocessError):
        pass

    return result


def collect_work_info(issue_limit: int = 10) -> Dict[str, Any]:
    """
    Collect comprehensive work information.

    Combines active plans and open issues into a single structure.

    Args:
        issue_limit: Maximum number of issues to include (default: 10)

    Returns:
        Dictionary with keys:
        - activePlans (List[Dict]): Active implementation plans
        - planCount (int): Number of active plans
        - openIssues (List[Dict]): Open GitHub issues
        - issueCount (int): Number of open issues

    Example:
        >>> info = collect_work_info()
        >>> print(f"Work items: {info['planCount']} plans, {info['issueCount']} issues")
        Work items: 1 plans, 5 issues
    """
    plans_data = collect_active_plans()
    issues_data = collect_open_issues(limit=issue_limit)

    return {
        'activePlans': plans_data['plans'],
        'planCount': plans_data['planCount'],
        'openIssues': issues_data['issues'],
        'issueCount': issues_data['issueCount']
    }


if __name__ == '__main__':
    # CLI interface for direct invocation
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == 'plans':
            # Print only plans
            data = collect_active_plans()
            print(json.dumps(data, indent=2))
        elif sys.argv[1] == 'issues':
            # Print only issues
            data = collect_open_issues()
            print(json.dumps(data, indent=2))
        else:
            print("Usage: work_collector.py [plans|issues]", file=sys.stderr)
            sys.exit(1)
    else:
        # Print combined work info
        info = collect_work_info()
        print(json.dumps(info, indent=2))
