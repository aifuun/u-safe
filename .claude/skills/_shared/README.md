# Shared Utilities for Claude Code Skills

> Python utilities library providing common functionality for skill scripts

This package provides reusable Python utilities for Claude Code skill scripts, eliminating code duplication and establishing consistent patterns across all skills per [ADR-003](../../../docs/ADRs/003-python-only-for-skill-scripts.md).

## Overview

The `_shared` package contains four utility modules:

| Module | Purpose | Functions |
|--------|---------|-----------|
| **git_utils** | Git operations | 5 functions for git commands, branch info, commit data |
| **fs_utils** | File system | 4 functions for file checks, searching, frontmatter parsing |
| **format_utils** | Output formatting | 3 functions for status emojis, tables, text truncation |
| **test_utils** | Testing helpers | Context managers for temp directories and mock repos |

All utilities follow Python 3.9+ standards with type hints and comprehensive docstrings.

## Installation

No installation needed - utilities are part of the skills directory structure.

**Dependencies**: Python 3.9+ standard library only (except `pytest` and `pyyaml` for testing)

```bash
# Install testing dependencies
pip install pytest pyyaml
```

## Usage

### Importing from Skill Scripts

Add the `_shared` directory to your Python path:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add _shared to path
sys.path.insert(0, str(Path(__file__).parent.parent / '_shared'))

# Import utilities
from git_utils import get_current_branch, get_commit_info
from fs_utils import find_files, check_file_exists
from format_utils import format_status, format_table
```

## API Reference

### git_utils

#### `run_git_command(args: list[str]) -> Tuple[int, str, str]`

Execute git command and return exit code, stdout, stderr.

```python
from git_utils import run_git_command

code, stdout, stderr = run_git_command(['status', '--short'])
if code == 0:
    print(f"Git status:\n{stdout}")
```

#### `get_current_branch() -> str`

Get current git branch name.

```python
from git_utils import get_current_branch

branch = get_current_branch()
print(f"On branch: {branch}")
# Output: On branch: feature/83-create-shared-python-utilities
```

#### `check_sync_status() -> bool`

Check if current branch is synced with origin/main.

```python
from git_utils import check_sync_status

if check_sync_status():
    print("✅ Branch is synced")
else:
    print("⚠️  Need to sync with origin/main")
```

#### `get_commit_info(ref: str = 'HEAD') -> Dict[str, str]`

Get commit information (hash, author, date, message).

```python
from git_utils import get_commit_info

info = get_commit_info('HEAD')
print(f"Last commit: {info['message']}")
print(f"Author: {info['author']}")
print(f"Date: {info['date']}")
```

#### `get_branch_commits(base: str = 'origin/main', head: str = 'HEAD') -> List[Dict[str, str]]`

Get list of commits between two refs.

```python
from git_utils import get_branch_commits

commits = get_branch_commits('origin/main', 'HEAD')
print(f"Branch has {len(commits)} commits:")
for commit in commits:
    print(f"- {commit['message']}")
```

### fs_utils

#### `check_file_exists(path: str) -> bool`

Check if file or directory exists.

```python
from fs_utils import check_file_exists

if check_file_exists('package.json'):
    print("✅ Found package.json")
```

#### `find_files(pattern: str, root: str = '.') -> List[str]`

Find files matching glob pattern.

```python
from fs_utils import find_files

# Find all Python files recursively
py_files = find_files('**/*.py', '.claude/skills')
print(f"Found {len(py_files)} Python files")

# Find markdown files in current directory
md_files = find_files('*.md')
```

#### `read_yaml_frontmatter(file: str) -> Dict[str, Any]`

Parse YAML frontmatter from markdown file.

```python
from fs_utils import read_yaml_frontmatter

metadata = read_yaml_frontmatter('.claude/skills/sync/SKILL.md')
print(f"Skill: {metadata['name']}")
print(f"Version: {metadata.get('version', 'unknown')}")
```

#### `count_files(directory: str, pattern: str = '*') -> int`

Count files matching pattern (non-recursive).

```python
from fs_utils import count_files

ts_count = count_files('src', '*.ts')
js_count = count_files('src', '*.js')
print(f"TypeScript: {ts_count}, JavaScript: {js_count}")
```

### format_utils

#### `format_status(status: str) -> str`

Format status with emoji indicator.

```python
from format_utils import format_status

print(format_status("success"))   # ✅ success
print(format_status("error"))     # ❌ error
print(format_status("warning"))   # ⚠️  warning
print(format_status("pending"))   # ⏳ pending
```

**Supported statuses**:
- ✅ Success: `success`, `pass`, `passed`, `ok`, `done`, `complete`, `synced`
- ❌ Failure: `fail`, `failed`, `error`, `failure`
- ⚠️  Warning: `warning`, `warn`, `need sync`, `outdated`
- ⏳ Pending: `pending`, `waiting`, `in progress`, `running`
- ℹ️  Info: `info`, `note`, `no tests`

#### `format_table(headers: List[str], rows: List[List[Any]]) -> str`

Format data as ASCII table.

```python
from format_utils import format_table

headers = ['Module', 'Functions', 'Status']
rows = [
    ['git_utils.py', 5, 'Done'],
    ['fs_utils.py', 4, 'Done'],
    ['format_utils.py', 3, 'Done']
]

print(format_table(headers, rows))
```

Output:
```
Module           | Functions | Status
-----------------|-----------|-------
git_utils.py     | 5         | Done
fs_utils.py      | 4         | Done
format_utils.py  | 3         | Done
```

#### `truncate_text(text: str, max_len: int, suffix: str = '...') -> str`

Truncate text to max length with ellipsis.

```python
from format_utils import truncate_text

long_message = "This is a very long commit message that needs truncation"
short = truncate_text(long_message, 30)
print(short)  # This is a very long comm...
```

### test_utils

#### `temp_directory() -> Generator[Path, None, None]`

Create temporary directory (context manager).

```python
from test_utils import temp_directory

with temp_directory() as tmpdir:
    test_file = tmpdir / 'test.txt'
    test_file.write_text('content')
    assert test_file.exists()
# tmpdir is automatically cleaned up
```

#### `mock_git_repo() -> Generator[Path, None, None]`

Create temporary git repository (context manager).

```python
from test_utils import mock_git_repo

with mock_git_repo() as repo:
    # Repo is initialized with initial commit
    # Create and commit test files
    test_file = repo / 'test.txt'
    test_file.write_text('content')
    subprocess.run(['git', 'add', '.'], cwd=repo)
    subprocess.run(['git', 'commit', '-m', 'test'], cwd=repo)
# repo is automatically cleaned up
```

#### `create_test_markdown(path: Path, frontmatter: dict = None, content: str = '')`

Create test markdown file with YAML frontmatter.

```python
from test_utils import temp_directory, create_test_markdown

with temp_directory() as tmpdir:
    test_file = tmpdir / 'test.md'
    create_test_markdown(
        test_file,
        frontmatter={'name': 'test-skill', 'version': '1.0.0'},
        content='## Overview\n\nTest content.'
    )
```

## Testing

Run tests with pytest:

```bash
cd .claude/skills/_shared
pytest
```

Run with coverage:

```bash
pytest --cov=. --cov-report=term-missing
```

Run specific test file:

```bash
pytest tests/test_git_utils.py -v
```

## Code Standards (Per ADR-003)

All utility functions follow these standards:

### ✅ Required

- **Python 3.9+** compatibility
- **Type hints** on all functions (using `typing` module)
- **Docstrings** with Args, Returns, Example sections
- **Proper exit codes** (0 = success for command-line scripts)
- **No external dependencies** (stdlib only, except pytest/pyyaml for tests)
- **Return structured data** (dicts/lists/tuples, not print to stdout)

### Example Function Template

```python
#!/usr/bin/env python3
"""Module docstring describing purpose."""

from typing import Tuple, Dict, List

def example_function(arg1: str, arg2: int = 0) -> Tuple[bool, str]:
    """
    One-line summary of what function does.

    Longer description if needed, explaining behavior,
    edge cases, or important notes.

    Args:
        arg1: Description of first argument
        arg2: Description of second argument (default: 0)

    Returns:
        Tuple of (success flag, result message)

    Example:
        >>> success, message = example_function("test", 42)
        >>> if success:
        ...     print(message)
        Success: test processed with 42
    """
    # Implementation here
    return True, f"Success: {arg1} processed with {arg2}"
```

## Directory Structure

```
.claude/skills/_shared/
├── __init__.py           # Package initialization
├── git_utils.py          # Git operations (5 functions)
├── fs_utils.py           # File system utilities (4 functions)
├── format_utils.py       # Output formatting (3 functions)
├── test_utils.py         # Testing helpers (3 functions)
├── pytest.ini            # Pytest configuration
├── README.md             # This file
└── tests/
    ├── __init__.py
    ├── test_git_utils.py     # Git utilities tests
    ├── test_fs_utils.py      # File system tests
    └── test_format_utils.py  # Formatting tests
```

## Error Handling Patterns

### Graceful Failures

All utilities handle errors gracefully and return meaningful values rather than crashing:

```python
from git_utils import get_current_branch, run_git_command
from fs_utils import check_file_exists

# Git operations return empty string on error
branch = get_current_branch()  # Returns "" if not in git repo

# File checks return False for missing files
exists = check_file_exists('nonexistent.txt')  # Returns False

# run_git_command returns exit code
code, stdout, stderr = run_git_command(['status'])
if code != 0:
    print(f"Git command failed: {stderr}")
```

### Exception Handling

When using utilities in skill scripts:

```python
try:
    from git_utils import get_commit_info
    commit = get_commit_info('HEAD')
    print(f"Last commit: {commit['message']}")

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
```

### Subprocess Errors

Utilities that run external commands handle subprocess failures:

```python
from git_utils import run_git_command

# Returns (exit_code, stdout, stderr)
code, stdout, stderr = run_git_command(['invalid-command'])

if code != 0:
    # Handle error appropriately
    print(f"Command failed (exit {code}): {stderr}")
```

## Performance Notes

### Git Operations

- `get_current_branch()` - Fast (~10ms)
- `check_sync_status()` - Moderate (~100ms, requires fetch)
- `get_branch_commits()` - Fast (~20ms for typical branches)

**Optimization tip**: Cache branch name if calling multiple times:

```python
branch = get_current_branch()
# Use branch multiple times without repeated git calls
```

### File Operations

- `check_file_exists()` - Very fast (~1ms)
- `find_files()` - Depends on directory size (use specific patterns)
- `read_yaml_frontmatter()` - Fast (~5ms per file)

**Optimization tip**: Use specific glob patterns to reduce file scanning:

```python
# ❌ Slow - searches entire filesystem
find_files('**/*.py', '/')

# ✅ Fast - limited scope
find_files('**/*.py', '.claude/skills')
```

## Troubleshooting

### ImportError: No module named 'git_utils'

**Problem**: Python can't find shared utilities.

**Solution**: Ensure `_shared` is in sys.path:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / '_shared'))
```

### Git commands fail with "not a git repository"

**Problem**: Script running outside git repository.

**Solution**: Check return values gracefully:

```python
from git_utils import get_current_branch

branch = get_current_branch()
if not branch:
    print("⚠️ Not in a git repository")
    sys.exit(1)
```

### Type errors with mypy

**Problem**: Type checker complains about utility functions.

**Solution**: Ensure you're using Python 3.9+ type hints:

```python
# ✅ Python 3.9+
def process(items: list[str]) -> dict[str, int]:
    ...

# ❌ Python 3.8 (requires typing.List, typing.Dict)
from typing import List, Dict
def process(items: List[str]) -> Dict[str, int]:
    ...
```

### YAML parsing fails

**Problem**: `read_yaml_frontmatter()` returns empty dict.

**Solution**: Ensure file has proper YAML frontmatter format:

```markdown
---
name: skill-name
version: 1.0.0
---

Content here...
```

## Migration from Bash

### Common Patterns

Replace Bash patterns with Python utilities:

| Bash Pattern | Python Utility | Example |
|--------------|----------------|---------|
| `git rev-parse --abbrev-ref HEAD` | `get_current_branch()` | `branch = get_current_branch()` |
| `git rev-parse HEAD` | `get_commit_info('HEAD')['hash']` | `commit = get_commit_info()['hash']` |
| `[ -f "$file" ]` | `check_file_exists(file)` | `if check_file_exists('file.txt'):` |
| `find . -name "*.py"` | `find_files('**/*.py')` | `files = find_files('**/*.py')` |
| `git status --short \| wc -l` | `run_git_command(['status', '--short'])` | `code, out, _ = run_git_command([...])` |

### Example Migration

**Before (Bash)**:
```bash
#!/bin/bash
check_branch() {
    BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
    if [ "$BRANCH" = "main" ]; then
        echo "On main branch"
        return 0
    else
        echo "Not on main: $BRANCH"
        return 1
    fi
}
```

**After (Python with utilities)**:
```python
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / '_shared'))

from git_utils import get_current_branch

def check_branch() -> int:
    """Check if on main branch."""
    branch = get_current_branch()

    if branch == "main":
        print("On main branch")
        return 0
    else:
        print(f"Not on main: {branch}")
        return 1

if __name__ == '__main__':
    sys.exit(check_branch())
```

**Benefits**:
- ✅ Type-safe with return type hints
- ✅ Graceful error handling (empty string on git errors)
- ✅ Cross-platform (works on Windows)
- ✅ Testable (easy to mock `get_current_branch()`)

## Integration with Skills

### Example: Using in finish-issue Skill

```python
#!/usr/bin/env python3
"""Check if tests pass."""

import sys
from pathlib import Path

# Add _shared to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / '_shared'))

from fs_utils import check_file_exists
from format_utils import format_status
import subprocess

def check_tests() -> int:
    """Check if npm tests pass."""
    if not check_file_exists('package.json'):
        print(format_status('no tests'))
        return 0

    result = subprocess.run(['npm', 'test'], capture_output=True)

    if result.returncode == 0:
        print(format_status('pass'))
    else:
        print(format_status('fail'))

    return result.returncode

if __name__ == '__main__':
    sys.exit(check_tests())
```

## Contributing

When adding new utilities:

1. **Follow ADR-003** standards (type hints, docstrings, examples)
2. **Add comprehensive tests** (80%+ coverage)
3. **Update this README** with API documentation
4. **Use stdlib only** (no external dependencies except for tests)
5. **Return structured data** (don't print to stdout)

## References

- [ADR-003: Python-Only Policy](../../../docs/ADRs/003-python-only-for-skill-scripts.md)
- [ADR-001: Official Skill Patterns](../../../docs/ADRs/001-official-skill-patterns.md)
- [Issue #82: Bash-to-Python Migration](https://github.com/aifuun/ai-dev/issues/82)
- [Issue #83: Phase 1 - Shared Utilities](https://github.com/aifuun/ai-dev/issues/83)

---

**Version**: 1.0.0
**Last Updated**: 2026-03-09
**Maintained by**: AI Dev Framework Team
