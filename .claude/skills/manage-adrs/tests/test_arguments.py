"""
Argument validation tests for manage-adrs.

Tests argument parsing and validation:
- Valid arguments accepted
- Invalid arguments rejected
- Missing required arguments detected
- Optional arguments handled correctly
"""

import pytest
from pathlib import Path


@pytest.mark.arguments
def test_create_command_requires_title():
    """Test that create command requires title argument."""
    from ...scripts.create_adr import parse_args

    with pytest.raises(SystemExit):
        parse_args(['create'])  # Missing title


@pytest.mark.arguments
def test_create_command_accepts_valid_title():
    """Test that create command accepts valid title."""
    from ...scripts.create_adr import parse_args

    args = parse_args(['create', 'Use React for Frontend'])

    assert args.command == 'create'
    assert args.title == 'Use React for Frontend'


@pytest.mark.arguments
def test_list_command_no_arguments():
    """Test that list command works without arguments."""
    from ...scripts.list_adrs import parse_args

    args = parse_args(['list'])

    assert args.command == 'list'


@pytest.mark.arguments
def test_show_command_requires_number_or_file():
    """Test that show command requires ADR number or file path."""
    from ...scripts.show_adr import parse_args

    with pytest.raises(SystemExit):
        parse_args(['show'])  # Missing number/file


@pytest.mark.arguments
def test_show_command_accepts_number():
    """Test that show command accepts ADR number."""
    from ...scripts.show_adr import parse_args

    args = parse_args(['show', '1'])

    assert args.command == 'show'
    assert args.number == 1


@pytest.mark.arguments
def test_show_command_accepts_file_path():
    """Test that show command accepts file path."""
    from ...scripts.show_adr import parse_args

    args = parse_args(['show', '--file', 'docs/ADRs/001-example.md'])

    assert args.command == 'show'
    assert args.file == 'docs/ADRs/001-example.md'


@pytest.mark.arguments
def test_validate_command_accepts_all_flag():
    """Test that validate command accepts --all flag."""
    from ...scripts.validate_adr import parse_args

    args = parse_args(['validate', '--all'])

    assert args.command == 'validate'
    assert args.all is True


@pytest.mark.arguments
def test_invalid_command_rejected():
    """Test that invalid commands are rejected."""
    from ...scripts.main import parse_args

    with pytest.raises(SystemExit):
        parse_args(['invalid-command'])


@pytest.mark.arguments
def test_create_with_custom_template_path():
    """Test that create accepts custom template path."""
    from ...scripts.create_adr import parse_args

    args = parse_args(['create', 'Test Title', '--template', 'custom_template.md'])

    assert args.template == 'custom_template.md'


@pytest.mark.arguments
def test_create_with_status_option():
    """Test that create accepts status option."""
    from ...scripts.create_adr import parse_args

    args = parse_args(['create', 'Test Title', '--status', 'Accepted'])

    assert args.status == 'Accepted'


@pytest.mark.arguments
def test_list_with_filter_status():
    """Test that list accepts status filter."""
    from ...scripts.list_adrs import parse_args

    args = parse_args(['list', '--status', 'Proposed'])

    assert args.status == 'Proposed'


@pytest.mark.arguments
def test_help_flag_shows_usage():
    """Test that --help flag shows usage information."""
    from ...scripts.main import parse_args

    with pytest.raises(SystemExit) as exc_info:
        parse_args(['--help'])

    assert exc_info.value.code == 0  # Help exits with 0
