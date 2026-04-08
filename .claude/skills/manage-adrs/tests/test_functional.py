"""
Functional tests for manage-adrs core features.

Tests the "What it does" functionality:
- Create ADRs
- List ADRs
- Show ADR content
- Validate ADR structure
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.create_adr import create_adr


@pytest.mark.functional
def test_create_adr_basic(mock_empty_adrs_directory, temp_dir):
    """Test creating a basic ADR."""

    title = "Use React for Frontend"
    adr_file = create_adr(
        title=title,
        adrs_dir=mock_empty_adrs_directory,
        template_path=None  # Use default template
    )

    assert adr_file.exists()
    assert "001-use-react-for-frontend.md" in adr_file.name

    content = adr_file.read_text()
    assert "# ADR-001: Use React for Frontend" in content
    assert "## Status" in content
    assert "## Context" in content
    assert "## Decision" in content


from scripts.list_adrs import list_adrs
from scripts.show_adr import show_adr
from scripts.validate_adr import validate_adr


@pytest.mark.functional
def test_list_adrs_empty(mock_empty_adrs_directory):
    """Test listing ADRs when directory is empty."""
    adrs = list_adrs(mock_empty_adrs_directory)

    assert adrs == []


@pytest.mark.functional
def test_list_adrs_multiple(mock_adrs_directory):
    """Test listing multiple ADRs."""
    adrs = list_adrs(mock_adrs_directory)

    assert len(adrs) == 3
    assert any("001-use-react-for-frontend.md" in str(adr) for adr in adrs)
    assert any("002-use-typescript.md" in str(adr) for adr in adrs)
    assert any("003-api-versioning-strategy.md" in str(adr) for adr in adrs)


@pytest.mark.functional
def test_show_adr_content(mock_existing_adr):
    """Test showing ADR content."""
    content = show_adr(file_path=mock_existing_adr)

    assert "# ADR-001: Use React for Frontend" in content
    assert "## Status" in content
    assert "Accepted" in content
    assert "## Context" in content
    assert "Need to choose a frontend framework" in content


@pytest.mark.functional
def test_validate_adr_valid(mock_existing_adr):
    """Test validating a valid ADR structure."""
    is_valid, errors = validate_adr(mock_existing_adr)

    assert is_valid is True
    assert len(errors) == 0


@pytest.mark.functional
def test_validate_adr_invalid(mock_invalid_adr):
    """Test validating an invalid ADR structure."""
    is_valid, errors = validate_adr(mock_invalid_adr)

    assert is_valid is False
    assert len(errors) > 0
    assert any("missing" in err.lower() or "invalid" in err.lower() for err in errors)


@pytest.mark.functional
def test_create_adr_with_custom_template(mock_empty_adrs_directory, mock_adr_template, temp_dir):
    """Test creating ADR with custom template."""
    # Write custom template to file
    template_file = temp_dir / "custom_template.md"
    template_file.write_text(mock_adr_template)

    adr_file = create_adr(
        title="Custom Template Test",
        adrs_dir=mock_empty_adrs_directory,
        template_path=template_file
    )

    assert adr_file.exists()
    content = adr_file.read_text()
    assert "# ADR-001: Custom Template Test" in content


@pytest.mark.functional
def test_list_adrs_sorted_by_number(mock_adrs_directory):
    """Test that listed ADRs are sorted by number."""
    adrs = list_adrs(mock_adrs_directory)

    # Extract numbers from filenames
    numbers = [int(adr.name.split('-')[0]) for adr in adrs]

    assert numbers == sorted(numbers)
    assert numbers == [1, 2, 3]
