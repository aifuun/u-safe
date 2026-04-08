"""
Shared pytest fixtures for manage-adrs tests.

This conftest provides reusable fixtures for:
- Temporary directories for test files
- Mock project profiles
- Mock ADR files and templates
- Helper functions for test setup
"""

import json
import pytest
import tempfile
from pathlib import Path
from datetime import datetime


@pytest.fixture
def temp_dir():
    """Provide temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_profile_basic(temp_dir):
    """Mock basic project profile without pillars."""
    profile_content = """---
name: test-project
type: generic
pillars: []
---

# Test Project Profile

Basic project for testing manage-adrs functionality.
"""
    profile_file = temp_dir / "docs" / "project-profile.md"
    profile_file.parent.mkdir(parents=True, exist_ok=True)
    profile_file.write_text(profile_content)
    return profile_file


@pytest.fixture
def mock_profile_with_pillars(temp_dir):
    """Mock project profile with active pillars."""
    profile_content = """---
name: test-project
type: tauri
pillars:
  - name: error-handling
    active: true
  - name: logging
    active: true
  - name: input-validation
    active: false
---

# Test Project Profile

Project with pillar-specific ADR requirements.
"""
    profile_file = temp_dir / "docs" / "project-profile.md"
    profile_file.parent.mkdir(parents=True, exist_ok=True)
    profile_file.write_text(profile_content)
    return profile_file


@pytest.fixture
def mock_adr_template():
    """Mock ADR template content."""
    return """# ADR-{number}: {title}

## Status

{status}

## Context

{context}

## Decision

{decision}

## Consequences

### Positive

{positive}

### Negative

{negative}

## Alternatives Considered

{alternatives}
"""


@pytest.fixture
def mock_existing_adr(temp_dir):
    """Create a mock existing ADR file."""
    adr_content = """# ADR-001: Use React for Frontend

## Status

Accepted

## Context

Need to choose a frontend framework.

## Decision

Use React for its component model and ecosystem.

## Consequences

### Positive

- Large community and ecosystem
- Good developer experience

### Negative

- Learning curve for new developers

## Alternatives Considered

- Vue.js: Simpler but smaller ecosystem
- Angular: Too heavyweight for our needs
"""
    adr_file = temp_dir / "docs" / "ADRs" / "001-use-react-for-frontend.md"
    adr_file.parent.mkdir(parents=True, exist_ok=True)
    adr_file.write_text(adr_content)
    return adr_file


@pytest.fixture
def mock_adrs_directory(temp_dir):
    """Create mock ADRs directory with multiple ADRs."""
    adrs_dir = temp_dir / "docs" / "ADRs"
    adrs_dir.mkdir(parents=True, exist_ok=True)

    # Create multiple ADR files
    adrs = [
        ("001-use-react-for-frontend.md", "Accepted"),
        ("002-use-typescript.md", "Accepted"),
        ("003-api-versioning-strategy.md", "Proposed"),
    ]

    for filename, status in adrs:
        number = filename.split("-")[0]
        title = filename.replace(f"{number}-", "").replace(".md", "").replace("-", " ").title()

        content = f"""# ADR-{number}: {title}

## Status

{status}

## Context

Test ADR for {title}.

## Decision

Decision content.

## Consequences

Consequences here.

## Alternatives Considered

Alternative 1
Alternative 2
"""
        (adrs_dir / filename).write_text(content)

    return adrs_dir


@pytest.fixture
def mock_empty_adrs_directory(temp_dir):
    """Create empty ADRs directory."""
    adrs_dir = temp_dir / "docs" / "ADRs"
    adrs_dir.mkdir(parents=True, exist_ok=True)
    return adrs_dir


@pytest.fixture
def mock_invalid_adr(temp_dir):
    """Create an ADR file with invalid structure."""
    adr_content = """# Some Random Document

This is not a valid ADR structure.
"""
    adr_file = temp_dir / "docs" / "ADRs" / "999-invalid-adr.md"
    adr_file.parent.mkdir(parents=True, exist_ok=True)
    adr_file.write_text(adr_content)
    return adr_file


def create_test_adr(directory: Path, number: int, title: str, status: str = "Proposed"):
    """Helper function to create a test ADR file."""
    filename = f"{number:03d}-{title.lower().replace(' ', '-')}.md"
    content = f"""# ADR-{number:03d}: {title}

## Status

{status}

## Context

Test context for {title}.

## Decision

Test decision.

## Consequences

### Positive

- Benefit 1

### Negative

- Drawback 1

## Alternatives Considered

- Alternative 1
"""
    adr_file = directory / filename
    adr_file.write_text(content)
    return adr_file
