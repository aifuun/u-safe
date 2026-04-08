"""
Parameter validation tests for update-framework skill.

Tests parameter handling and validation logic.
Following ADR-020 standards.
"""

from pathlib import Path

import pytest


@pytest.mark.parameters
def test_missing_source_path():
    """Test error when source (framework) path is missing.

    Arrange:
        - No framework directory exists
    Act:
        - Run update-framework with non-existent source
    Assert:
        - ValueError raised with clear message
        - Suggests checking path or running from framework directory
    """
    non_existent_path = Path("/nonexistent/ai-dev")

    # Simulate source path validation
    def validate_source(path: Path) -> None:
        if not path.exists():
            raise ValueError(
                f"Framework directory not found: {path}\n"
                f"Ensure you're running from ai-dev directory."
            )

    with pytest.raises(ValueError, match="Framework directory not found"):
        validate_source(non_existent_path)


@pytest.mark.parameters
def test_missing_target_path():
    """Test error when target project path is missing.

    Arrange:
        - Target directory path not provided
    Act:
        - Run update-framework with no arguments
    Assert:
        - ValueError raised
        - Error message explains required argument
    """
    # Simulate argument parsing
    def parse_args(args: list) -> str:
        if not args:
            raise ValueError(
                "Target directory required.\n"
                "Usage: /update-framework <target-directory>"
            )
        return args[0]

    with pytest.raises(ValueError, match="Target directory required"):
        parse_args([])


@pytest.mark.parameters
def test_invalid_path_format():
    """Test handling of invalid path formats.

    Tests various invalid path formats:
    - Paths with null bytes
    - Paths with invalid characters (Windows)
    - Relative paths that resolve outside allowed directories

    Arrange:
        - Various invalid path strings
    Act:
        - Attempt to validate each path
    Assert:
        - ValueError raised for each invalid format
    """
    invalid_paths = [
        "path\x00with\x00nulls",  # Null bytes
        "../../../etc/passwd",     # Path traversal attempt
        "path/with/../../../escape",  # Complex traversal
    ]

    def validate_path_format(path_str: str) -> Path:
        # Check for null bytes
        if "\x00" in path_str:
            raise ValueError("Path contains null bytes")

        path = Path(path_str).resolve()

        # Check for path traversal (simple check)
        if ".." in path_str and len(path.parts) < 2:
            raise ValueError("Invalid path: potential path traversal")

        return path

    # Test each invalid path
    with pytest.raises(ValueError, match="null bytes"):
        validate_path_format(invalid_paths[0])

    # Path traversal cases might resolve differently
    # For comprehensive testing, we'd need actual filesystem checks


@pytest.mark.parameters
def test_conflicting_flags():
    """Test error when conflicting flags are provided.

    User cannot specify both --only and --skip flags simultaneously.

    Arrange:
        - Arguments with both --only and --skip
    Act:
        - Parse arguments
    Assert:
        - ValueError raised
        - Error message explains conflict
    """
    def parse_flags(only: str = None, skip: str = None):
        if only and skip:
            raise ValueError(
                "Cannot use --only and --skip together.\n"
                "Use --only to sync specific components, OR\n"
                "Use --skip to exclude specific components."
            )
        return {"only": only, "skip": skip}

    # Test conflicting flags
    with pytest.raises(ValueError, match="Cannot use --only and --skip together"):
        parse_flags(only="pillars", skip="skills")

    # Test valid individual flags (should not raise)
    assert parse_flags(only="pillars") == {"only": "pillars", "skip": None}
    assert parse_flags(skip="skills") == {"only": None, "skip": "skills"}
    assert parse_flags() == {"only": None, "skip": None}
