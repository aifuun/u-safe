"""
ADR listing functionality.
"""

from pathlib import Path
from typing import List


def list_adrs(adrs_dir: Path) -> List[Path]:
    """
    List all ADR files in directory.

    Args:
        adrs_dir: Directory containing ADRs

    Returns:
        List of ADR file paths, sorted by number

    Handles:
        - Missing directory (returns empty list)
        - Unreadable files (skips them)
    """
    if not adrs_dir.exists():
        return []

    adr_files = []

    for f in adrs_dir.glob("[0-9]*.md"):
        # Skip unreadable files
        try:
            if f.is_file() and os.access(f, os.R_OK):
                adr_files.append(f)
        except (OSError, PermissionError):
            # Skip files we can't access
            continue

    # Sort by number
    def extract_number(path: Path) -> int:
        import re
        match = re.match(r'(\d+)-', path.name)
        return int(match.group(1)) if match else 999999

    adr_files.sort(key=extract_number)

    return adr_files


import os
