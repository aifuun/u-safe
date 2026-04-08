"""
ADR display functionality.
"""

from pathlib import Path
from typing import Optional


class ADRNotFoundError(Exception):
    """Raised when ADR not found."""
    pass


class InvalidADRNumberError(Exception):
    """Raised when ADR number invalid."""
    pass


class MalformedADRError(Exception):
    """Raised when ADR content malformed."""
    pass


def show_adr(number: Optional[int] = None, file_path: Optional[Path] = None) -> str:
    """
    Show ADR content.

    Args:
        number: ADR number to show
        file_path: Or direct file path

    Returns:
        ADR content as string

    Raises:
        ADRNotFoundError: If ADR doesn't exist
        InvalidADRNumberError: If number invalid
        MalformedADRError: If content malformed
    """
    if number is not None:
        if number <= 0:
            raise InvalidADRNumberError(f"ADR number must be >= 1, got {number}")

        # Try to find ADR by number
        # This is simplified - in reality would search in configured directory
        raise ADRNotFoundError(
            f"ADR #{number} not found. "
            f"Check available ADRs with: /manage-adrs list"
        )

    if file_path is not None:
        if not file_path.exists():
            raise InvalidPathError(f"File not found: {file_path}")

        try:
            content = file_path.read_text()

            # Basic malformed check
            if content.startswith("---"):
                # Has YAML frontmatter - try to validate
                import yaml
                try:
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        yaml.safe_load(parts[1])
                except yaml.YAMLError:
                    raise MalformedADRError("Invalid YAML frontmatter")

            return content
        except (OSError, PermissionError) as e:
            raise ADRNotFoundError(f"Cannot read file: {e}")

    raise ValueError("Must provide either number or file_path")


class InvalidPathError(Exception):
    """Raised when path invalid."""
    pass
