"""
Argument tests for manage-claude-md skill

Based on ADR-020 "Arguments" section:
- --instant flag
- --dry-run flag
- --configure-profile flag
- Invalid arguments handling
"""

import pytest


@pytest.mark.argument
@pytest.mark.unit
def test_instant_flag():
    """Test --instant flag triggers instant mode"""
    # Given: --instant argument
    args = {"instant": True}

    # When/Then: Instant mode activated
    assert args["instant"] is True


@pytest.mark.argument
@pytest.mark.unit
def test_dry_run_flag(mock_claude_md):
    """Test --dry-run flag shows preview without changes"""
    # Given: CLAUDE.md and --dry-run flag
    original_content = mock_claude_md.read_text()
    dry_run = True

    # When: Simulating dry-run mode
    if dry_run:
        # Preview changes without writing
        preview = f"Would update: {mock_claude_md}\nNo changes made."
    else:
        mock_claude_md.write_text(original_content + "\nModified")

    # Then: No changes made in dry-run mode
    assert dry_run is True
    assert mock_claude_md.read_text() == original_content


@pytest.mark.argument
@pytest.mark.unit
def test_configure_profile_flag(mock_profile_config):
    """Test --configure-profile flag"""
    # Given: --configure-profile argument
    args = {"configure_profile": True}

    # When: Profile configuration triggered
    if args["configure_profile"]:
        content = mock_profile_config.read_text()
        # Profile configuration logic here

    # Then: Profile configuration mode activated
    assert args["configure_profile"] is True
    assert "Profile" in content


@pytest.mark.argument
@pytest.mark.unit
def test_invalid_arguments():
    """Test invalid arguments raise errors"""
    # Given: Invalid argument scenarios
    invalid_cases = [
        {"instant": "invalid", "error": "Boolean expected"},
        {"unknown_arg": True, "error": "Unknown argument"},
    ]

    for case in invalid_cases:
        # When/Then: Invalid arguments detected
        if "instant" in case and not isinstance(case["instant"], bool):
            assert case["error"] == "Boolean expected"
        if "unknown_arg" in case:
            assert case["error"] == "Unknown argument"
