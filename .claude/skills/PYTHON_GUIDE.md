# Python Skill Development Guide

**Version**: 1.0.0
**Last Updated**: 2026-03-09
**Policy**: [ADR-003: Python-Only for Skill Scripts](../docs/ADRs/003-python-only-for-skill-scripts.md)

## Overview

This guide provides comprehensive documentation for developing Claude Code skills using Python. All skill scripts must be written in Python 3.9+ following the patterns and standards documented here.

**Why Python-Only?**
- ✅ Type safety with type hints
- ✅ Better error handling and debugging
- ✅ Cross-platform compatibility (Windows, macOS, Linux)
- ✅ Rich standard library for testing
- ✅ Easier maintenance and collaboration
- ✅ IDE support with autocomplete and type checking

**Migration Complete**: As of 2026-03-09, all skill scripts have been migrated from Bash to Python (3,088 lines of type-hinted Python code).

---

## Table of Contents

1. [Requirements](#requirements)
2. [Skill Script Template](#skill-script-template)
3. [Type Hints Guide](#type-hints-guide)
4. [Using Shared Utilities](#using-shared-utilities)
5. [Testing Patterns](#testing-patterns)
6. [Error Handling](#error-handling)
7. [Debugging Tips](#debugging-tips)
8. [Best Practices](#best-practices)
9. [Common Patterns](#common-patterns)
10. [Migration from Bash](#migration-from-bash)

---

## Requirements

### Python Version

**Minimum**: Python 3.9+

**Why 3.9?**
- Type hints with `list[str]` instead of `List[str]`
- Dictionary merge operator `|`
- String methods improvements
- Better error messages

**Check version:**
```bash
python3 --version
# Should show: Python 3.9.x or higher
```

### Standard Library Only

**Policy**: Skills should use **only** the Python standard library.

**Allowed modules:**
- `sys`, `os`, `pathlib` - File system operations
- `subprocess` - Running external commands
- `json` - JSON parsing
- `argparse` - CLI argument parsing
- `typing` - Type hints
- `dataclasses` - Data structures
- `re` - Regular expressions
- `datetime` - Date/time handling

**Exception**: Jinja2 was briefly considered but removed. Use string templates or JSON injection instead.

### Environment Configuration

**PYTHONPATH Setup**: Instead of using `sys.path.insert()` in individual scripts, configure PYTHONPATH at the environment level.

**Recommended: direnv auto-loading**
```bash
# Create .envrc file (already exists in project root)
# Run once:
direnv allow

# PYTHONPATH is automatically set when you cd into the directory
```

**Alternative: Manual setup**
```bash
# Source the setup script
source setup_env.sh

# Or export manually
export PYTHONPATH="${PWD}/.claude/skills:${PYTHONPATH}"
```

**Why this approach?**
- ✅ Cleaner code (no `sys.path.insert()` boilerplate)
- ✅ Consistent across all scripts
- ✅ IDE integration works better
- ✅ Easier to maintain

**Before (deprecated):**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / '_scripts'))

from utils.git import get_current_branch  # ❌ Don't do this anymore
```

**After (recommended):**
```python
# Just import directly - PYTHONPATH is already configured
from utils.git import get_current_branch  # ✅ Clean and simple
```

### Shared Utilities

**Location**: `.claude/skills/_scripts/`

**Available utilities:**
- `git_utils.py` - Git operations (status, sync, commits)
- `fs_utils.py` - File system operations (safe read/write, find files)
- `format_utils.py` - Output formatting (colors, emojis, tables)

**Import pattern:**
```python
import sys
from pathlib import Path

# Add shared utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent / '_scripts'))

from git_utils import check_sync_status, get_current_branch
from fs_utils import safe_read_file, safe_write_file
from format_utils import success, error, warning
```

---

## Skill Script Template

### Basic Template

```python
#!/usr/bin/env python3
"""
Skill Name - Brief Description

Detailed description of what this script does.

Usage:
    ./script_name.py [OPTIONS]

Example:
    ./script_name.py --format=json
    ./script_name.py --output=file.txt
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Add shared utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent / '_scripts'))

from git_utils import check_sync_status
from format_utils import success, error


def main_function(input_data: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main processing function.

    Args:
        input_data: Input data to process
        options: Configuration options

    Returns:
        Dictionary with results

    Raises:
        ValueError: If input_data is invalid
        IOError: If file operations fail

    Example:
        >>> result = main_function("test", {"format": "json"})
        >>> print(result['status'])
        'success'
    """
    # Implementation here
    return {
        'status': 'success',
        'data': input_data,
        'message': 'Processing complete'
    }


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Brief description of what this script does',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --format=json
  %(prog)s --output=result.txt
        """
    )

    parser.add_argument(
        '--format',
        choices=['json', 'text'],
        default='text',
        help='Output format (default: text)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (optional)'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    try:
        args = parse_arguments()

        # Process
        result = main_function("input", {'format': args.format})

        # Output
        if args.output:
            Path(args.output).write_text(str(result), encoding='utf-8')
            print(success(f"Output saved to: {args.output}"))
        else:
            print(result)

        sys.exit(0)

    except KeyboardInterrupt:
        print("\n" + error("Interrupted by user"))
        sys.exit(130)
    except Exception as e:
        print(error(f"Error: {e}"))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### Make Script Executable

```bash
chmod +x script_name.py
```

---

## Type Hints Guide

### Basic Types

```python
from typing import Dict, List, Tuple, Optional, Any, Union

# Simple types
def process_string(text: str) -> str:
    return text.upper()

def count_items(items: list[str]) -> int:
    return len(items)

# Optional (can be None)
def find_user(user_id: int) -> Optional[Dict[str, Any]]:
    if user_id == 0:
        return None
    return {'id': user_id, 'name': 'John'}

# Union types (multiple possible types)
def parse_input(value: Union[str, int]) -> str:
    return str(value)
```

### Complex Types

```python
from typing import Dict, List, Callable

# Nested structures
UserData = Dict[str, Any]  # Type alias
ConfigDict = Dict[str, Union[str, int, bool]]

def process_users(users: List[UserData]) -> Dict[str, List[str]]:
    """Group users by role."""
    result: Dict[str, List[str]] = {}
    for user in users:
        role = user.get('role', 'unknown')
        if role not in result:
            result[role] = []
        result[role].append(user['name'])
    return result

# Callable types (function parameters)
def apply_transform(data: str, transform: Callable[[str], str]) -> str:
    return transform(data)
```

### Dataclasses

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class GitStatus:
    """Git repository status."""
    branch: str
    commit: str
    staged: int
    unstaged: int
    untracked: int
    message: Optional[str] = None

    def is_clean(self) -> bool:
        """Check if working directory is clean."""
        return self.staged == 0 and self.unstaged == 0 and self.untracked == 0

# Usage
status = GitStatus(
    branch='main',
    commit='abc123',
    staged=0,
    unstaged=2,
    untracked=1
)

if status.is_clean():
    print("Clean working directory")
```

---

## Using Shared Utilities

### Git Utilities (`git_utils.py`)

```python
from git_utils import (
    check_sync_status,
    get_current_branch,
    get_current_commit,
    has_uncommitted_changes,
    get_recent_commits
)

# Check if branch is synced with remote
sync_status = check_sync_status()
if sync_status['is_synced']:
    print("✅ Branch is synced")
else:
    print(f"⚠️ {sync_status['ahead']} commits ahead, {sync_status['behind']} behind")

# Get current branch
branch = get_current_branch()
print(f"Current branch: {branch}")

# Check for uncommitted changes
if has_uncommitted_changes():
    print("⚠️ You have uncommitted changes")

# Get recent commits
commits = get_recent_commits(limit=5)
for commit in commits:
    print(f"{commit['hash'][:7]} - {commit['message']}")
```

### File System Utilities (`fs_utils.py`)

```python
from fs_utils import (
    safe_read_file,
    safe_write_file,
    find_files,
    ensure_directory
)

# Safe file reading (handles errors gracefully)
content = safe_read_file('path/to/file.txt')
if content is None:
    print("File not found or unreadable")
else:
    print(f"Read {len(content)} bytes")

# Safe file writing
success = safe_write_file('output.txt', 'content')
if not success:
    print("Failed to write file")

# Find files by pattern
py_files = find_files('.', pattern='*.py', recursive=True)
print(f"Found {len(py_files)} Python files")

# Ensure directory exists
ensure_directory('.claude/plans/active')
```

### Format Utilities (`format_utils.py`)

```python
from format_utils import (
    success,
    error,
    warning,
    info,
    header,
    format_table
)

# Colored output
print(success("✅ Operation successful"))
print(error("❌ Operation failed"))
print(warning("⚠️ Warning message"))
print(info("ℹ️ Info message"))

# Headers
print(header("Section Title"))

# Tables
data = [
    {'name': 'Alice', 'age': 30, 'role': 'Developer'},
    {'name': 'Bob', 'age': 25, 'role': 'Designer'}
]
print(format_table(data, columns=['name', 'age', 'role']))
```

---

## Testing Patterns

### Test Structure

```python
#!/usr/bin/env python3
"""Tests for my_script.py"""

import sys
from pathlib import Path

# Add script directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from my_script import main_function


def test_basic_functionality():
    """Test basic function operation."""
    result = main_function("test input", {'format': 'json'})

    assert result['status'] == 'success'
    assert 'data' in result
    assert result['data'] == "test input"


def test_error_handling():
    """Test error handling."""
    try:
        main_function("", {'format': 'invalid'})
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected


def test_with_options():
    """Test with different options."""
    result = main_function("input", {'format': 'text', 'verbose': True})
    assert result is not None
```

### Mocking Subprocess

```python
from unittest.mock import patch, MagicMock
import subprocess

def test_git_command():
    """Test function that calls git."""
    with patch('subprocess.run') as mock_run:
        # Mock successful git command
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='main\n',
            stderr=''
        )

        # Test function that uses subprocess
        result = my_function_that_calls_git()

        # Verify subprocess was called correctly
        mock_run.assert_called_once()
        assert result == 'main'
```

### Mocking File System

```python
from unittest.mock import patch, mock_open

def test_file_reading():
    """Test function that reads files."""
    mock_file_content = "test content"

    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        result = my_function_that_reads_file('dummy.txt')
        assert result == "test content"
```

### Integration Tests

```python
import tempfile
import shutil
from pathlib import Path

def test_end_to_end():
    """Test complete workflow with real files."""
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test files
        input_file = tmpdir_path / 'input.txt'
        input_file.write_text('test data')

        # Run function
        result = process_file(input_file)

        # Verify output
        output_file = tmpdir_path / 'output.txt'
        assert output_file.exists()
        assert output_file.read_text() == 'processed: test data'
```

### Running Tests

```bash
# Run all tests in directory
pytest tests/

# Run specific test file
pytest tests/test_my_script.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=. tests/
```

---

## Error Handling

### Exception Patterns

```python
def process_data(data: str) -> Dict[str, Any]:
    """
    Process input data.

    Raises:
        ValueError: If data is empty or invalid
        IOError: If file operations fail
    """
    if not data:
        raise ValueError("Data cannot be empty")

    if not data.isalnum():
        raise ValueError(f"Invalid data format: {data}")

    return {'processed': data.upper()}


def safe_operation():
    """Perform operation with comprehensive error handling."""
    try:
        result = risky_operation()
        return result

    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return None

    except PermissionError as e:
        print(f"❌ Permission denied: {e}")
        return None

    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed (exit {e.returncode}): {e.cmd}")
        print(f"   stderr: {e.stderr}")
        return None

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None
```

### Subprocess Error Handling

```python
import subprocess

def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """
    Run command and capture output.

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # Prevent hanging
        )
        return result.returncode, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out after 30 seconds"

    except FileNotFoundError:
        return 1, "", f"Command not found: {cmd[0]}"
```

---

## Debugging Tips

### Print Debugging

```python
import sys

def debug_print(message: str, **kwargs):
    """Print debug message to stderr."""
    print(f"[DEBUG] {message}", file=sys.stderr)
    if kwargs:
        for key, value in kwargs.items():
            print(f"  {key} = {value}", file=sys.stderr)

# Usage
debug_print("Processing user", user_id=123, name="Alice")
```

### Using pdb

```python
import pdb

def complex_function(data):
    result = process_step1(data)

    # Set breakpoint here
    pdb.set_trace()

    result = process_step2(result)
    return result

# When breakpoint hits:
# - 'n' for next line
# - 's' for step into function
# - 'c' for continue
# - 'p variable' to print variable
# - 'q' to quit
```

### Logging

```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('skill.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usage
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
```

### Common Issues

**Issue**: `ModuleNotFoundError` for shared utilities

**Solution**:
```python
# Add this at top of script
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / '_scripts'))
```

**Issue**: Subprocess hanging indefinitely

**Solution**:
```python
# Add timeout parameter
result = subprocess.run(cmd, timeout=30, capture_output=True)
```

**Issue**: File encoding errors

**Solution**:
```python
# Always specify encoding
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()
```

---

## Best Practices

### 1. Type Hints Everywhere

```python
# ✅ Good
def process_user(user_id: int, options: Dict[str, Any]) -> Optional[Dict[str, str]]:
    ...

# ❌ Bad
def process_user(user_id, options):
    ...
```

### 2. Comprehensive Docstrings

```python
# ✅ Good
def calculate_score(data: Dict[str, Any]) -> int:
    """
    Calculate health score from project data.

    Args:
        data: Project data with keys: git, framework, tests

    Returns:
        Health score (0-100)

    Raises:
        ValueError: If data is missing required keys

    Example:
        >>> score = calculate_score({'git': {...}, 'framework': {...}})
        >>> print(score)
        85
    """
    ...
```

### 3. Use pathlib

```python
from pathlib import Path

# ✅ Good
config_path = Path.home() / '.config' / 'app' / 'config.json'
if config_path.exists():
    content = config_path.read_text()

# ❌ Bad
import os
config_path = os.path.join(os.path.expanduser('~'), '.config', 'app', 'config.json')
if os.path.exists(config_path):
    with open(config_path) as f:
        content = f.read()
```

### 4. Explicit Error Messages

```python
# ✅ Good
if not Path('config.json').exists():
    print("❌ Configuration file not found: config.json")
    print("   Create it with: cp config.json.example config.json")
    sys.exit(1)

# ❌ Bad
assert Path('config.json').exists()
```

### 5. Use sys.exit() with Codes

```python
# ✅ Good
sys.exit(0)    # Success
sys.exit(1)    # General error
sys.exit(130)  # Interrupted (Ctrl+C)

# ❌ Bad
exit()  # Don't use built-in exit()
```

---

## Common Patterns

### CLI with Subcommands

```python
def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Add subcommand
    add_parser = subparsers.add_parser('add', help='Add item')
    add_parser.add_argument('name', type=str)

    # List subcommand
    list_parser = subparsers.add_parser('list', help='List items')

    args = parser.parse_args()

    if args.command == 'add':
        add_item(args.name)
    elif args.command == 'list':
        list_items()
```

### JSON Input/Output

```python
import json

def process_json_input(input_file: str) -> Dict[str, Any]:
    """Process JSON input file."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)

def output_json(data: Dict[str, Any], output_file: Optional[str] = None):
    """Output data as JSON."""
    json_str = json.dumps(data, indent=2, ensure_ascii=False)

    if output_file:
        Path(output_file).write_text(json_str, encoding='utf-8')
    else:
        print(json_str)
```

### Progress Indicators

```python
import sys

def show_progress(current: int, total: int, prefix: str = ''):
    """Show progress bar."""
    percent = int(100 * current / total)
    bar_length = 40
    filled = int(bar_length * current / total)
    bar = '█' * filled + '░' * (bar_length - filled)

    print(f'\r{prefix} [{bar}] {percent}%', end='', file=sys.stderr)
    if current == total:
        print(file=sys.stderr)  # Newline at end

# Usage
for i in range(1, 101):
    show_progress(i, 100, 'Processing')
    # do work
```

---

## Migration from Bash

### Common Conversions

| Bash | Python |
|------|--------|
| `if [ -f "$file" ]` | `Path(file).is_file()` |
| `if [ -d "$dir" ]` | `Path(dir).is_dir()` |
| `mkdir -p "$dir"` | `Path(dir).mkdir(parents=True, exist_ok=True)` |
| `cat file.txt` | `Path('file.txt').read_text()` |
| `echo "text" > file` | `Path('file').write_text('text')` |
| `find . -name "*.py"` | `list(Path('.').rglob('*.py'))` |
| `basename "$path"` | `Path(path).name` |
| `dirname "$path"` | `Path(path).parent` |
| `$(command)` | `subprocess.run(['command'], capture_output=True).stdout` |
| `$?` (exit code) | `result.returncode` |

### Example Migration

**Before (Bash)**:
```bash
#!/bin/bash
check_tests() {
    if [ ! -f "package.json" ]; then
        echo "No tests"
        return 0
    fi

    if npm test &>/dev/null; then
        echo "✅ Tests passing"
        return 0
    else
        echo "❌ Tests failing"
        return 1
    fi
}
```

**After (Python)**:
```python
#!/usr/bin/env python3
import subprocess
from pathlib import Path

def check_tests() -> int:
    """Check if tests pass."""
    if not Path('package.json').exists():
        print("No tests")
        return 0

    result = subprocess.run(
        ['npm', 'test'],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ Tests passing")
        return 0
    else:
        print("❌ Tests failing")
        return 1
```

---

## References

- **ADR-003**: [Python-Only Policy](../docs/ADRs/003-python-only-for-skill-scripts.md)
- **Shared Utilities**: [.claude/skills/_scripts/README.md](_scripts/README.md)
- **Python Docs**: https://docs.python.org/3.9/
- **Type Hints (PEP 484)**: https://peps.python.org/pep-0484/
- **pytest Documentation**: https://docs.pytest.org/

---

**Questions?** Check ADR-003 or the shared utilities documentation.

**Contributing**: All skill scripts must follow this guide. PRs with Bash scripts will be rejected by CI.
