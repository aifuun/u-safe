"""
Integration tests for manage-adrs end-to-end workflows.

Tests complete workflows:
- Create → List → Show workflow
- Create → Validate workflow
- Multiple ADR management workflow
- Profile-aware ADR creation
- Index generation workflow
"""

import pytest
from pathlib import Path


@pytest.mark.integration
def test_complete_adr_lifecycle(mock_empty_adrs_directory, temp_dir):
    """Test complete ADR lifecycle: create → list → show → validate."""
    from ...scripts.create_adr import create_adr
    from ...scripts.list_adrs import list_adrs
    from ...scripts.show_adr import show_adr
    from ...scripts.validate_adr import validate_adr

    # Step 1: Create ADR
    adr_file = create_adr(
        title="Use React for Frontend",
        adrs_dir=mock_empty_adrs_directory
    )
    assert adr_file.exists()

    # Step 2: List ADRs
    adrs = list_adrs(mock_empty_adrs_directory)
    assert len(adrs) == 1
    assert "001-use-react-for-frontend.md" in str(adrs[0])

    # Step 3: Show ADR content
    content = show_adr(file_path=adr_file)
    assert "# ADR-001: Use React for Frontend" in content

    # Step 4: Validate ADR
    is_valid, errors = validate_adr(adr_file)
    assert is_valid is True
    assert len(errors) == 0


@pytest.mark.integration
def test_multiple_adrs_workflow(mock_empty_adrs_directory):
    """Test creating and managing multiple ADRs."""
    from ...scripts.create_adr import create_adr
    from ...scripts.list_adrs import list_adrs

    # Create 3 ADRs
    titles = [
        "Use React for Frontend",
        "Use TypeScript for Type Safety",
        "Use REST API for Backend"
    ]

    for title in titles:
        create_adr(title=title, adrs_dir=mock_empty_adrs_directory)

    # List all ADRs
    adrs = list_adrs(mock_empty_adrs_directory)
    assert len(adrs) == 3

    # Verify ordering
    numbers = [int(adr.name.split('-')[0]) for adr in adrs]
    assert numbers == [1, 2, 3]


@pytest.mark.integration
def test_profile_aware_adr_creation(mock_profile_with_pillars, temp_dir):
    """Test ADR creation adapts to project profile pillars."""
    from ...scripts.create_adr import create_adr_with_profile
    from ...scripts.profile import load_profile

    # Load profile with active pillars
    profile = load_profile(mock_profile_with_pillars)

    adrs_dir = temp_dir / "docs" / "ADRs"
    adrs_dir.mkdir(parents=True)

    # Create ADR with profile awareness
    adr_file = create_adr_with_profile(
        title="Error Handling Strategy",
        profile=profile,
        adrs_dir=adrs_dir
    )

    content = adr_file.read_text()

    # Should include pillar-specific sections
    assert "## Error Handling" in content or "error" in content.lower()
    assert "## Logging" in content or "logging" in content.lower()


@pytest.mark.integration
def test_index_generation_workflow(mock_adrs_directory, temp_dir):
    """Test generating ADR index from existing ADRs."""
    from ...scripts.generate_index import generate_adr_index

    index_file = mock_adrs_directory / "INDEX.md"

    # Generate index
    generate_adr_index(
        adrs_dir=mock_adrs_directory,
        output_file=index_file
    )

    assert index_file.exists()

    content = index_file.read_text()

    # Verify index contains all ADRs
    assert "001-use-react-for-frontend" in content
    assert "002-use-typescript" in content
    assert "003-api-versioning-strategy" in content

    # Verify index structure
    assert "# Architecture Decision Records" in content
    assert "## Index" in content or "## ADRs" in content


@pytest.mark.integration
@pytest.mark.slow
def test_batch_validation_workflow(mock_adrs_directory, mock_invalid_adr):
    """Test validating all ADRs in directory."""
    from ...scripts.validate_adr import validate_all_adrs

    # Add invalid ADR to directory
    invalid_file = mock_adrs_directory / "999-invalid.md"
    invalid_file.write_text(mock_invalid_adr.read_text())

    # Validate all ADRs
    results = validate_all_adrs(mock_adrs_directory)

    # 3 valid + 1 invalid = 4 total
    assert len(results) == 4

    valid_count = sum(1 for r in results if r['is_valid'])
    invalid_count = sum(1 for r in results if not r['is_valid'])

    assert valid_count == 3
    assert invalid_count == 1

    # Check invalid ADR has errors
    invalid_result = next(r for r in results if r['file'].name == "999-invalid.md")
    assert len(invalid_result['errors']) > 0


@pytest.mark.integration
def test_update_existing_adr_workflow(mock_existing_adr):
    """Test updating an existing ADR's status."""
    from ...scripts.update_adr import update_adr_status

    # Update status from Proposed to Accepted
    update_adr_status(
        adr_file=mock_existing_adr,
        new_status="Superseded",
        superseded_by=42  # ADR-042
    )

    # Verify update
    content = mock_existing_adr.read_text()
    assert "Superseded" in content
    assert "42" in content or "ADR-042" in content


@pytest.mark.integration
def test_create_with_existing_number_auto_increment(mock_adrs_directory):
    """Test that creating ADR with existing number auto-increments."""
    from ...scripts.create_adr import create_adr_auto_number

    # Directory has ADR 001, 002, 003
    adr_file = create_adr_auto_number(
        title="New ADR",
        adrs_dir=mock_adrs_directory
    )

    # Should create ADR-004
    assert "004-new-adr.md" in adr_file.name
    assert adr_file.exists()


@pytest.mark.integration
def test_search_adrs_by_keyword(mock_adrs_directory):
    """Test searching ADRs by keyword in content."""
    from ...scripts.search_adrs import search_adrs

    results = search_adrs(
        keyword="React",
        adrs_dir=mock_adrs_directory
    )

    assert len(results) >= 1
    assert any("001-use-react-for-frontend" in str(r) for r in results)
