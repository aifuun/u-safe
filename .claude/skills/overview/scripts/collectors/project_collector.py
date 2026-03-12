#!/usr/bin/env python3
"""Project information data collection module.

Collects comprehensive project metadata from CLAUDE.md and repository structure.
Replaces collect-project-info.sh per ADR-003.

Example:
    >>> from collectors import project_collector
    >>> info = project_collector.collect_project_info()
    >>> print(info['description'])
    AI-assisted development framework
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add _shared to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / '_shared'))

from fs_utils import check_file_exists, find_files


def collect_project_info(project_root: str = '.') -> Dict[str, Any]:
    """
    Collect comprehensive project information.

    Parses CLAUDE.md and scans repository for project metadata.

    Args:
        project_root: Path to project root (default: current directory)

    Returns:
        Dictionary with keys:
        - description (str): Project description
        - coreConcept (str): Core concept/purpose
        - initialized (str): Initialization date
        - techStack (Dict): Frontend, backend, auth, iac
        - documentation (List[Dict]): Documentation links
        - completed (List[Dict]): Completed work items
        - architecture (Dict): ADR count, recent ADRs, patterns

    Example:
        >>> info = collect_project_info()
        >>> print(info['techStack']['frontend'])
        React + TypeScript
    """
    claude_md = Path(project_root) / 'CLAUDE.md'

    return {
        'description': extract_description(claude_md),
        'coreConcept': extract_core_concept(claude_md),
        'initialized': extract_initialized_date(claude_md),
        'techStack': extract_tech_stack(claude_md),
        'documentation': extract_documentation(claude_md),
        'completed': extract_completed(claude_md),
        'architecture': extract_architecture(project_root)
    }


def extract_description(claude_md: Path) -> str:
    """
    Extract project description from CLAUDE.md.

    Looks for **Product**: line.

    Args:
        claude_md: Path to CLAUDE.md file

    Returns:
        Project description (max 300 chars)

    Example:
        >>> desc = extract_description(Path('CLAUDE.md'))
        >>> print(desc)
        AI-assisted development framework for Claude Code integration
    """
    if not claude_md.exists():
        return "No project description available"

    try:
        with open(claude_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find **Product**: line
        match = re.search(r'\*\*Product\*\*:\s*(.+?)(?:\n|$)', content)
        if match:
            desc = match.group(1).strip()
            return desc[:300]  # Limit to 300 chars

        return "No description found"

    except (IOError, UnicodeDecodeError):
        return "Error reading project description"


def extract_core_concept(claude_md: Path) -> str:
    """
    Extract core concept from CLAUDE.md.

    Looks for ### 🎯 Core Concept section.

    Args:
        claude_md: Path to CLAUDE.md file

    Returns:
        Core concept description

    Example:
        >>> concept = extract_core_concept(Path('CLAUDE.md'))
        >>> print(concept)
        Universal framework for Claude Code integration...
    """
    if not claude_md.exists():
        return ""

    try:
        with open(claude_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find Core Concept section
        match = re.search(r'### 🎯 Core Concept\s*\n(.+?)(?:\n###|\Z)', content, re.DOTALL)
        if match:
            concept_text = match.group(1).strip()
            # Remove code blocks and empty lines
            concept_text = re.sub(r'```[\s\S]*?```', '', concept_text)
            concept_text = '\n'.join(line for line in concept_text.split('\n') if line.strip())
            # Get first 4 lines
            lines = concept_text.split('\n')[:4]
            return ' '.join(lines)

        return ""

    except (IOError, UnicodeDecodeError):
        return ""


def extract_initialized_date(claude_md: Path) -> str:
    """
    Extract initialization date from CLAUDE.md.

    Args:
        claude_md: Path to CLAUDE.md file

    Returns:
        Initialization date or "unknown"
    """
    if not claude_md.exists():
        return "unknown"

    try:
        with open(claude_md, 'r', encoding='utf-8') as f:
            content = f.read()

        match = re.search(r'\*\*Initialized\*\*:\s*(.+)', content)
        if match:
            return match.group(1).strip()

        return "unknown"

    except (IOError, UnicodeDecodeError):
        return "unknown"


def extract_tech_stack(claude_md: Path) -> Dict[str, str]:
    """
    Extract technology stack from CLAUDE.md.

    Looks for table rows with Frontend, Backend, Auth, IaC.

    Args:
        claude_md: Path to CLAUDE.md file

    Returns:
        Dictionary with keys: frontend, backend, auth, iac

    Example:
        >>> stack = extract_tech_stack(Path('CLAUDE.md'))
        >>> print(stack['frontend'])
        React + TypeScript
    """
    default = {
        'frontend': 'N/A',
        'backend': 'N/A',
        'auth': 'N/A',
        'iac': 'N/A'
    }

    if not claude_md.exists():
        return default

    try:
        with open(claude_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract from table format: | **Frontend** | value |
        for key in ['frontend', 'backend', 'auth', 'iac']:
            pattern = rf'\|\s*\*\*{key.capitalize()}\*\*\s*\|\s*(.+?)\s*\|'
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                default[key] = match.group(1).strip()

        # Special case for IaC (Infrastructure as Code)
        iac_match = re.search(r'\|\s*\*\*IaC\*\*\s*\|\s*(.+?)\s*\|', content)
        if iac_match:
            default['iac'] = iac_match.group(1).strip()

        return default

    except (IOError, UnicodeDecodeError):
        return default


def extract_documentation(claude_md: Path) -> List[Dict[str, str]]:
    """
    Extract documentation links from CLAUDE.md.

    Looks for markdown links to PRD, Schema, Roadmap docs.

    Args:
        claude_md: Path to CLAUDE.md file

    Returns:
        List of documentation dictionaries with title, path, type

    Example:
        >>> docs = extract_documentation(Path('CLAUDE.md'))
        >>> for doc in docs:
        ...     print(f"{doc['type']}: {doc['title']}")
        PRD: Product Requirements
        Architecture: System Schema
    """
    if not claude_md.exists():
        return []

    try:
        with open(claude_md, 'r', encoding='utf-8') as f:
            content = f.read()

        docs = []

        # Find PRD
        prd_match = re.search(r'\[PRD[^\]]*\]\(([^\)]+\.md)\)', content)
        if prd_match:
            docs.append({
                'title': 'PRD',
                'path': prd_match.group(1),
                'type': 'PRD'
            })

        # Find Schema
        schema_match = re.search(r'\[[^\]]*Schema[^\]]*\]\(([^\)]+\.md)\)', content)
        if schema_match:
            docs.append({
                'title': 'Schema',
                'path': schema_match.group(1),
                'type': 'Architecture'
            })

        # Find Roadmap
        roadmap_match = re.search(r'\[Roadmap[^\]]*\]\(([^\)]+\.md)\)', content)
        if roadmap_match:
            docs.append({
                'title': 'Roadmap',
                'path': roadmap_match.group(1),
                'type': 'Planning'
            })

        return docs

    except (IOError, UnicodeDecodeError):
        return []


def extract_completed(claude_md: Path) -> List[Dict[str, str]]:
    """
    Extract completed work items from CLAUDE.md.

    Looks for **Completed**: section with issue listings.

    Args:
        claude_md: Path to CLAUDE.md file

    Returns:
        List of completed work dictionaries with issue, title, description

    Example:
        >>> completed = extract_completed(Path('CLAUDE.md'))
        >>> for item in completed:
        ...     print(f"{item['issue']}: {item['title']}")
        #85: Migrate collectors
    """
    if not claude_md.exists():
        return []

    try:
        with open(claude_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find Completed section
        match = re.search(r'\*\*Completed\*\*:(.+?)(?:^---$|\Z)', content, re.MULTILINE | re.DOTALL)
        if not match:
            return []

        completed_section = match.group(1)
        completed = []

        # Parse issue lines: - **Issue #XX ✅**: Title (Description)
        pattern = r'- \*\*Issue (#\d+) ✅\*\*:\s*([^(]+)\s*\(([^)]+)\)'
        for match in re.finditer(pattern, completed_section):
            completed.append({
                'issue': match.group(1),
                'title': match.group(2).strip(),
                'description': match.group(3).strip()
            })

        return completed[:5]  # Return latest 5

    except (IOError, UnicodeDecodeError):
        return []


def extract_architecture(project_root: str = '.') -> Dict[str, Any]:
    """
    Extract architecture information (ADRs, patterns).

    Args:
        project_root: Path to project root

    Returns:
        Dictionary with keys:
        - adrCount (int): Number of ADRs
        - recentADRs (List[Dict]): Latest 5 ADRs
        - patterns (List[str]): Detected patterns

    Example:
        >>> arch = extract_architecture()
        >>> print(f"ADRs: {arch['adrCount']}")
        ADRs: 3
    """
    adr_dir = Path(project_root) / 'docs' / 'ADRs'

    result = {
        'adrCount': 0,
        'recentADRs': [],
        'patterns': []
    }

    # Count ADRs
    if adr_dir.is_dir():
        adr_files = list(adr_dir.glob('[0-9]*.md'))
        result['adrCount'] = len(adr_files)

        # Get latest 5 ADRs (sorted by modification time)
        adr_files_sorted = sorted(adr_files, key=lambda f: f.stat().st_mtime, reverse=True)
        for adr_file in adr_files_sorted[:5]:
            try:
                with open(adr_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract number from filename
                num_match = re.search(r'^(\d+)', adr_file.name)
                number = num_match.group(1) if num_match else '0'

                # Extract title from first heading
                title_match = re.search(r'^# ADR-\d+:\s*(.+)', content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else 'Unknown'

                # Extract status
                status_match = re.search(r'## Status\s*\n\s*(.+)', content)
                status = status_match.group(1).strip() if status_match else 'Unknown'

                result['recentADRs'].append({
                    'number': number,
                    'title': title,
                    'status': status
                })

            except (IOError, UnicodeDecodeError):
                continue

    # Detect patterns (delegate to pattern_detector)
    try:
        from . import pattern_detector
        result['patterns'] = pattern_detector.detect_patterns()
    except ImportError:
        result['patterns'] = []

    return result


if __name__ == '__main__':
    # CLI interface for direct invocation
    import json

    project_root = sys.argv[1] if len(sys.argv) > 1 else '.'
    info = collect_project_info(project_root)
    print(json.dumps(info, indent=2))
