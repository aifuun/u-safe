"""
ADR validation functionality.
"""

from pathlib import Path
from typing import Tuple, List


class InvalidPathError(Exception):
    """Raised when path invalid."""
    pass


def validate_required_sections(content: str) -> Tuple[bool, List[str]]:
    """
    Validate that required sections are present.

    Args:
        content: ADR content

    Returns:
        (is_valid, missing_sections)
    """
    required_sections = [
        "## Status",
        "## Context",
        "## Decision",
        "## Consequences",
        "## Alternatives",
    ]

    missing = []
    for section in required_sections:
        if section not in content:
            # Extract section name
            section_name = section.replace("## ", "")
            missing.append(section_name)

    return (len(missing) == 0, missing)


def validate_adr(adr_path: Path = None, content: str = None) -> Tuple[bool, List[str]]:
    """
    Validate ADR structure and content.

    Args:
        adr_path: Path to ADR file
        content: Or ADR content directly

    Returns:
        (is_valid, errors)
    """
    errors = []

    # Load content if path provided
    if adr_path is not None:
        if not adr_path.exists():
            raise InvalidPathError(f"File not found: {adr_path}")

        try:
            # Check if file is readable
            content = adr_path.read_text()
        except UnicodeDecodeError:
            errors.append("File appears corrupted or is not valid text")
            return (False, errors)
        except (OSError, PermissionError) as e:
            errors.append(f"Cannot read file: {e}")
            return (False, errors)

    if content is None:
        errors.append("No content provided")
        return (False, errors)

    # Validate structure
    lines = content.split('\n')

    # Check for ADR title
    if not any(line.startswith('# ADR-') for line in lines):
        errors.append("Missing ADR title (should start with '# ADR-NNN:')")

    # Validate required sections
    is_valid, missing = validate_required_sections(content)
    if not is_valid:
        for section in missing:
            errors.append(f"Missing required section: {section}")

    # Check for empty sections
    if "## Status\n\n##" in content or "## Context\n\n##" in content:
        errors.append("Some required sections are empty (Status or Context)")

    return (len(errors) == 0, errors)


def validate_all_adrs(adrs_dir: Path) -> List[dict]:
    """
    Validate all ADRs in directory.

    Args:
        adrs_dir: Directory containing ADRs

    Returns:
        List of validation results: [{"file": Path, "is_valid": bool, "errors": [str]}]
    """
    from .list_adrs import list_adrs

    results = []
    adrs = list_adrs(adrs_dir)

    for adr_file in adrs:
        is_valid, errors = validate_adr(adr_file)
        results.append({
            "file": adr_file,
            "is_valid": is_valid,
            "errors": errors
        })

    return results
