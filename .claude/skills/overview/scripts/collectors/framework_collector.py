#!/usr/bin/env python3
"""Framework configuration data collection module.

Collects information about installed framework components (Pillars, Rules, Skills).
Replaces collect-framework.sh per ADR-003.

Example:
    >>> from collectors import framework_collector
    >>> info = framework_collector.collect_framework_info()
    >>> print(f"Profile: {info['profile']}")
    >>> print(f"Pillars: {', '.join(info['pillars'])}")
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, List

# Add _scripts to path

from fs_utils import check_file_exists, find_files


def collect_framework_info() -> Dict[str, Any]:
    """
    Collect framework configuration information.

    Detects framework profile, active Pillars, and counts of rules/commands/skills.

    Returns:
        Dictionary with keys:
        - profile (str): Framework profile name or "Not installed"
        - pillars (List[str]): List of active Pillar IDs (e.g., ["A", "B", "K"])
        - pillarCount (int): Number of active Pillars
        - ruleCount (int): Number of rules
        - commandCount (int): Number of commands
        - skillCount (int): Number of skills

    Example:
        >>> info = collect_framework_info()
        >>> print(info['profile'])
        react-aws
        >>> print(info['pillarCount'])
        7
    """
    result = {
        'profile': 'Not installed',
        'pillars': [],
        'pillarCount': 0,
        'ruleCount': 0,
        'commandCount': 0,
        'skillCount': 0
    }

    # Detect framework profile from .framework-install
    if check_file_exists('.framework-install'):
        try:
            with open('.framework-install', 'r', encoding='utf-8') as f:
                content = f.read().strip()

            # Try JSON format first
            if content.startswith('{') or content.startswith('['):
                try:
                    data = json.loads(content)
                    result['profile'] = data.get('profile', 'unknown')

                    # Extract pillars from JSON
                    pillars = data.get('pillars', [])
                    if pillars:
                        result['pillars'] = pillars
                        result['pillarCount'] = len(pillars)
                except json.JSONDecodeError:
                    pass

            # Try text format
            if result['profile'] == 'Not installed':
                match = re.search(r'\*\*Profile\*\*:\s*(.+)', content)
                if match:
                    result['profile'] = match.group(1).strip()

        except (IOError, UnicodeDecodeError):
            pass

    # Detect Pillars from .prot/pillars directory if not found in metadata
    if result['pillarCount'] == 0 and Path('.prot/pillars').is_dir():
        pillar_dirs = list(Path('.prot/pillars').glob('pillar-*'))
        pillar_ids = []

        for pillar_dir in pillar_dirs:
            # Extract pillar ID from directory name (e.g., "pillar-a" → "A")
            match = re.search(r'pillar-([a-z])', pillar_dir.name)
            if match:
                pillar_id = match.group(1).upper()
                pillar_ids.append(pillar_id)

        if pillar_ids:
            result['pillars'] = sorted(pillar_ids)
            result['pillarCount'] = len(pillar_ids)

    # Count rules
    if Path('.claude/rules').is_dir():
        rule_files = find_files('**/*.md', '.claude/rules')
        result['ruleCount'] = len(rule_files)

    # Count commands
    if Path('.claude/commands').is_dir():
        command_files = find_files('**/*.md', '.claude/commands')
        result['commandCount'] = len(command_files)

    # Count skills
    if Path('.claude/skills').is_dir():
        skill_dirs = [d for d in Path('.claude/skills').iterdir()
                     if d.is_dir() and (d / 'SKILL.md').exists()]
        result['skillCount'] = len(skill_dirs)

    return result


def get_pillar_details() -> List[Dict[str, Any]]:
    """
    Get detailed information about each active Pillar.

    Returns:
        List of dictionaries with keys:
        - id (str): Pillar ID (e.g., "A")
        - name (str): Pillar name (e.g., "Nominal Typing")
        - path (str): Path to pillar directory

    Example:
        >>> pillars = get_pillar_details()
        >>> for pillar in pillars:
        ...     print(f"{pillar['id']}: {pillar['name']}")
        A: Nominal Typing
        B: Schema Validation
    """
    pillars = []

    if not Path('.prot/pillars').is_dir():
        return pillars

    for pillar_dir in sorted(Path('.prot/pillars').glob('pillar-*')):
        match = re.search(r'pillar-([a-z])', pillar_dir.name)
        if not match:
            continue

        pillar_id = match.group(1).upper()

        # Try to extract pillar name from README or markdown files
        pillar_name = f"Pillar {pillar_id}"
        readme_path = pillar_dir / 'README.md'
        if readme_path.exists():
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    # Extract name from markdown heading
                    if first_line.startswith('#'):
                        pillar_name = first_line.lstrip('#').strip()
            except (IOError, UnicodeDecodeError):
                pass

        pillars.append({
            'id': pillar_id,
            'name': pillar_name,
            'path': str(pillar_dir)
        })

    return pillars


if __name__ == '__main__':
    # CLI interface for direct invocation
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'pillars':
        # Print detailed pillar info
        pillars = get_pillar_details()
        print(json.dumps(pillars, indent=2))
    else:
        # Print framework info
        info = collect_framework_info()
        print(json.dumps(info, indent=2))
