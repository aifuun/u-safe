"""
ADR creation functionality.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional
import re


class ADRExistsError(Exception):
    """Raised when ADR with given number already exists."""
    pass


class TemplateNotFoundError(Exception):
    """Raised when template file not found."""
    pass


class DiskFullError(Exception):
    """Raised when disk is full."""
    pass


def sanitize_title(title: str) -> str:
    """
    Sanitize title for use in filename.

    Removes special characters and prevents path traversal.
    """
    # Remove path traversal attempts
    title = title.replace("..", "")
    title = title.replace("/", "")
    title = title.replace("\\", "")

    # Remove special characters
    title = re.sub(r'[<>:"|?*]', '', title)

    # Convert to kebab-case
    title = re.sub(r'\s+', '-', title)
    title = title.lower()

    return title


def get_next_adr_number(adrs_dir: Path) -> int:
    """Get next sequential ADR number."""
    if not adrs_dir.exists():
        return 1

    adr_files = list(adrs_dir.glob("[0-9]*.md"))
    if not adr_files:
        return 1

    numbers = []
    for f in adr_files:
        match = re.match(r'(\d+)-', f.name)
        if match:
            numbers.append(int(match.group(1)))

    return max(numbers) + 1 if numbers else 1


def create_adr(
    title: str,
    adrs_dir: Path,
    template_path: Optional[Path] = None,
    number: Optional[int] = None,
    status: str = "Proposed"
) -> Path:
    """
    Create a new ADR file.

    Args:
        title: ADR title
        adrs_dir: Directory to create ADR in
        template_path: Optional custom template
        number: Optional ADR number (auto-assigned if None)
        status: Initial status (default: Proposed)

    Returns:
        Path to created ADR file

    Raises:
        ADRExistsError: If ADR with number already exists
        TemplateNotFoundError: If template path invalid
        PermissionError: If directory not writable
        DiskFullError: If disk full
    """
    # Auto-assign number if not provided
    if number is None:
        number = get_next_adr_number(adrs_dir)

    # Check if ADR already exists
    sanitized = sanitize_title(title)
    adr_filename = f"{number:03d}-{sanitized}.md"
    adr_path = adrs_dir / adr_filename

    if adr_path.exists():
        raise ADRExistsError(f"ADR {number} already exists")

    # Check directory writable
    if not adrs_dir.exists():
        adrs_dir.mkdir(parents=True)

    if not os.access(adrs_dir, os.W_OK):
        raise PermissionError(f"No write permission for {adrs_dir}")

    # Load template
    if template_path and not template_path.exists():
        raise TemplateNotFoundError(f"Template not found: {template_path}")

    template_content = ""
    if template_path:
        template_content = template_path.read_text()
    else:
        # Default template
        template_content = f"""# ADR-{number:03d}: {title}

## Status

{status}

## Context

What is the issue that we're seeing that is motivating this decision or change?

## Decision

What is the change that we're proposing and/or doing?

## Consequences

### Positive

What becomes easier or better?

### Negative

What becomes more difficult or worse?

## Alternatives Considered

What other approaches did we consider?
"""

    # Write file
    try:
        adr_path.write_text(template_content)
    except OSError as e:
        if e.errno == 28:  # No space left
            raise DiskFullError("No space left on device")
        raise

    return adr_path


def create_adr_auto_number(title: str, adrs_dir: Path) -> Path:
    """Create ADR with auto-assigned number."""
    return create_adr(title, adrs_dir, number=None)


def create_adr_atomic(title: str, adrs_dir: Path):
    """
    Context manager for atomic ADR creation.

    Ensures no partial files on failure.
    """
    import tempfile
    import shutil

    class AtomicADRCreator:
        def __init__(self, title, adrs_dir):
            self.title = title
            self.adrs_dir = adrs_dir
            self.temp_file = None
            self.final_path = None

        def __enter__(self):
            # Create temp file
            self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md')
            return self.temp_file

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.temp_file.close()

            if exc_type is None:
                # Success - move temp to final location
                number = get_next_adr_number(self.adrs_dir)
                sanitized = sanitize_title(self.title)
                self.final_path = self.adrs_dir / f"{number:03d}-{sanitized}.md"
                shutil.move(self.temp_file.name, self.final_path)
            else:
                # Failure - clean up temp file
                Path(self.temp_file.name).unlink(missing_ok=True)

            return False  # Don't suppress exceptions

    return AtomicADRCreator(title, adrs_dir)


# Import os for permission checks
import os
