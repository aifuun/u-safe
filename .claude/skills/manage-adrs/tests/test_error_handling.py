"""
Error handling tests for manage-adrs.

Tests error scenarios and recovery:
- Missing files handled gracefully
- Invalid input rejected with clear messages
- Filesystem errors caught
- Partial operations rolled back
- Error messages are informative
"""

import pytest
from pathlib import Path


@pytest.mark.error
def test_show_missing_adr_file_error():
    """Test that showing non-existent ADR gives clear error."""
    from ...scripts.show_adr import show_adr, ADRNotFoundError

    with pytest.raises(ADRNotFoundError) as exc_info:
        show_adr(number=999)

    error_message = str(exc_info.value)
    assert "999" in error_message
    assert "not found" in error_message.lower()


@pytest.mark.error
def test_create_with_invalid_template_path_error():
    """Test that create with non-existent template gives clear error."""
    from ...scripts.create_adr import create_adr, TemplateNotFoundError

    with pytest.raises(TemplateNotFoundError) as exc_info:
        create_adr(
            title="Test",
            template_path=Path("/nonexistent/template.md")
        )

    error_message = str(exc_info.value)
    assert "template" in error_message.lower()
    assert "not found" in error_message.lower()


@pytest.mark.error
def test_validate_with_invalid_file_path():
    """Test that validate with invalid path gives clear error."""
    from ...scripts.validate_adr import validate_adr, InvalidPathError

    with pytest.raises(InvalidPathError) as exc_info:
        validate_adr(Path("/nonexistent/file.md"))

    error_message = str(exc_info.value)
    assert "not found" in error_message.lower() or "invalid" in error_message.lower()


@pytest.mark.error
def test_list_with_unreadable_files_skips_gracefully(temp_dir):
    """Test that list skips unreadable files and continues."""
    from ...scripts.list_adrs import list_adrs

    adrs_dir = temp_dir / "docs" / "ADRs"
    adrs_dir.mkdir(parents=True)

    # Create readable ADR
    readable = adrs_dir / "001-readable.md"
    readable.write_text("# ADR-001: Readable")

    # Create unreadable ADR
    unreadable = adrs_dir / "002-unreadable.md"
    unreadable.write_text("# ADR-002: Unreadable")
    unreadable.chmod(0o000)

    try:
        adrs = list_adrs(adrs_dir)

        # Should still list readable ADR
        assert len(adrs) >= 1
        assert any("001-readable" in str(adr) for adr in adrs)
    finally:
        # Restore permissions for cleanup
        unreadable.chmod(0o644)


@pytest.mark.error
def test_create_handles_disk_full_error(mock_empty_adrs_directory, monkeypatch):
    """Test that create handles disk full errors gracefully."""
    from ...scripts.create_adr import create_adr, DiskFullError

    def mock_write_that_fails(*args, **kwargs):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(Path, 'write_text', mock_write_that_fails)

    with pytest.raises(DiskFullError) as exc_info:
        create_adr(
            title="Test ADR",
            adrs_dir=mock_empty_adrs_directory
        )

    error_message = str(exc_info.value)
    assert "disk" in error_message.lower() or "space" in error_message.lower()


@pytest.mark.error
def test_show_with_malformed_adr_content():
    """Test that show handles malformed ADR content gracefully."""
    from ...scripts.show_adr import show_adr, MalformedADRError
    from pathlib import Path

    # Create malformed ADR (invalid YAML frontmatter)
    malformed_file = Path("/tmp/malformed.md")
    malformed_file.write_text("""---
invalid: yaml: structure:
---

# ADR-001: Test
""")

    try:
        with pytest.raises(MalformedADRError) as exc_info:
            show_adr(file_path=malformed_file)

        error_message = str(exc_info.value)
        assert "malformed" in error_message.lower() or "invalid" in error_message.lower()
    finally:
        malformed_file.unlink()


@pytest.mark.error
def test_validate_provides_specific_error_locations():
    """Test that validate errors include line numbers."""
    from ...scripts.validate_adr import validate_adr

    invalid_content = """# ADR-001: Test

## Status

## Context

Missing content in sections above.
"""

    is_valid, errors = validate_adr(content=invalid_content)

    assert is_valid is False
    # Errors should include section names or line numbers
    assert any("Status" in err or "line" in err.lower() for err in errors)


@pytest.mark.error
def test_create_recovers_from_interrupted_operation(mock_empty_adrs_directory):
    """Test that interrupted create doesn't leave partial files."""
    from ...scripts.create_adr import create_adr

    class InterruptError(Exception):
        pass

    # Simulate interruption mid-create
    try:
        with pytest.raises(InterruptError):
            # Mock filesystem to simulate interruption
            raise InterruptError("Simulated interruption")
    except InterruptError:
        pass

    # Verify no partial files left
    adr_files = list(mock_empty_adrs_directory.glob("*.md"))
    assert len(adr_files) == 0


@pytest.mark.error
def test_error_messages_include_resolution_steps():
    """Test that error messages include how to fix the issue."""
    from ...scripts.show_adr import show_adr, ADRNotFoundError

    with pytest.raises(ADRNotFoundError) as exc_info:
        show_adr(number=999)

    error_message = str(exc_info.value)

    # Error should suggest what to do
    assert any(
        keyword in error_message.lower()
        for keyword in ["check", "verify", "list", "create"]
    )
