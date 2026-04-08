"""
Safety mechanism tests for manage-adrs.

Tests safety features that prevent data loss and errors:
- Prevent overwriting existing ADRs
- Validate directory permissions
- Handle missing directories gracefully
- Prevent invalid ADR numbers
- Safe file operations
"""

import pytest
from pathlib import Path
import os


@pytest.mark.safety
def test_create_prevents_overwrite_existing_adr(mock_existing_adr, mock_adrs_directory):
    """Test that creating ADR with existing number is prevented."""
    from ...scripts.create_adr import create_adr, ADRExistsError

    with pytest.raises(ADRExistsError):
        create_adr(
            title="Duplicate ADR",
            number=1,  # Already exists
            adrs_dir=mock_adrs_directory
        )


@pytest.mark.safety
def test_create_requires_writable_directory(temp_dir):
    """Test that create fails gracefully with read-only directory."""
    from ...scripts.create_adr import create_adr, PermissionError

    adrs_dir = temp_dir / "readonly_adrs"
    adrs_dir.mkdir()

    # Make directory read-only
    os.chmod(adrs_dir, 0o444)

    try:
        with pytest.raises(PermissionError):
            create_adr(
                title="Test ADR",
                adrs_dir=adrs_dir
            )
    finally:
        # Restore permissions for cleanup
        os.chmod(adrs_dir, 0o755)


@pytest.mark.safety
def test_list_handles_missing_directory_gracefully(temp_dir):
    """Test that list handles missing ADRs directory gracefully."""
    from ...scripts.list_adrs import list_adrs

    non_existent_dir = temp_dir / "does_not_exist"

    # Should return empty list, not crash
    adrs = list_adrs(non_existent_dir)
    assert adrs == []


@pytest.mark.safety
def test_show_validates_adr_number_range():
    """Test that show rejects invalid ADR numbers."""
    from ...scripts.show_adr import show_adr, InvalidADRNumberError

    with pytest.raises(InvalidADRNumberError):
        show_adr(number=0)  # Invalid: must be >= 1

    with pytest.raises(InvalidADRNumberError):
        show_adr(number=-5)  # Invalid: negative


@pytest.mark.safety
def test_validate_handles_corrupted_adr_file(temp_dir):
    """Test that validate handles corrupted/binary files gracefully."""
    from ...scripts.validate_adr import validate_adr

    # Create binary file disguised as ADR
    corrupted_file = temp_dir / "docs" / "ADRs" / "999-corrupted.md"
    corrupted_file.parent.mkdir(parents=True, exist_ok=True)
    corrupted_file.write_bytes(b'\x00\xFF\x00\xFF\x00')  # Binary content

    is_valid, errors = validate_adr(corrupted_file)

    assert is_valid is False
    assert any("corrupted" in err.lower() or "invalid" in err.lower() for err in errors)


@pytest.mark.safety
def test_create_sanitizes_title_for_filename():
    """Test that create sanitizes special characters in title."""
    from ...scripts.create_adr import sanitize_title

    dangerous_title = "Use <script>alert('xss')</script> Framework"
    safe_filename = sanitize_title(dangerous_title)

    assert '<' not in safe_filename
    assert '>' not in safe_filename
    assert 'script' in safe_filename.lower()
    assert 'framework' in safe_filename.lower()


@pytest.mark.safety
def test_create_prevents_path_traversal_in_title():
    """Test that create prevents path traversal attacks."""
    from ...scripts.create_adr import sanitize_title

    malicious_title = "../../../etc/passwd"
    safe_filename = sanitize_title(malicious_title)

    assert '..' not in safe_filename
    assert '/' not in safe_filename
    assert os.path.sep not in safe_filename


@pytest.mark.safety
def test_atomic_file_write_prevents_partial_writes(mock_empty_adrs_directory):
    """Test that ADR creation is atomic (no partial writes on failure)."""
    from ...scripts.create_adr import create_adr_atomic

    class SimulatedWriteError(Exception):
        pass

    # Simulate failure during write
    with pytest.raises(SimulatedWriteError):
        with create_adr_atomic(
            title="Test ADR",
            adrs_dir=mock_empty_adrs_directory
        ) as f:
            f.write("# ADR-001: Test\n")
            raise SimulatedWriteError("Disk full")

    # Verify no partial file left behind
    adr_files = list(mock_empty_adrs_directory.glob("*.md"))
    assert len(adr_files) == 0


@pytest.mark.safety
def test_validate_rejects_adr_without_required_sections():
    """Test that validate enforces required sections."""
    from ...scripts.validate_adr import validate_required_sections

    incomplete_content = """# ADR-001: Test

## Status

Proposed

## Context

Some context.
"""
    # Missing: Decision, Consequences, Alternatives

    is_valid, missing = validate_required_sections(incomplete_content)

    assert is_valid is False
    assert "Decision" in missing
    assert "Consequences" in missing
    assert "Alternatives" in missing
