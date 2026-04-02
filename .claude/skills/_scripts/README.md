# Shared Python Libraries for Skills

Centralized Python code shared across multiple skills for better organization and maintainability.

## Purpose

This directory contains all reusable Python code used by skills, organized by domain. It provides:
- **Self-containment** - All shared code in `.claude/skills/`
- **Shorter imports** - 2 levels instead of 5 (`../_scripts` vs `../../../../scripts`)
- **Clear organization** - Domain-based structure
- **Easier distribution** - Copy `.claude/skills/` once

## Structure

```
_scripts/
├── __init__.py                 # Root module
├── github/                     # GitHub operations
│   ├── __init__.py
│   ├── api.py                  # GitHub API wrapper
│   ├── issues.py               # Issue management
│   └── labels.py               # Label operations
├── git/                        # Git operations
│   ├── __init__.py
│   └── worktree.py             # Worktree management
├── framework/                  # Framework operations
│   ├── __init__.py
│   ├── sync.py                 # Framework sync utilities
│   └── profiles.py             # Profile management
└── utils/                      # Generic utilities
    ├── __init__.py
    ├── git.py                  # Git utilities
    ├── fs.py                   # File system utilities
    ├── format.py               # Formatting utilities
    └── test.py                 # Testing utilities
```

## Usage

### Import Pattern

From a skill script (`.claude/skills/{skill}/scripts/script.py`):

```python
import sys
from pathlib import Path

# Add _scripts to path (2 levels up)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_scripts"))

# Import from domain modules
from git.worktree import create_worktree, list_worktrees
from utils.git import check_sync_status
from utils.format import success, error, info
```

### Before (Old Pattern)

```python
# 5 levels up to scripts/
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))
from worktree_manager import create_worktree
```

### After (New Pattern)

```python
# 2 levels up to _scripts/
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_scripts"))
from git.worktree import create_worktree
```

## Modules

### git.worktree

Worktree management for parallel issue development.

**Functions:**
- `create_worktree(issue_number, issue_title, branch_name)` - Create worktree
- `list_worktrees()` - List all worktrees with metadata
- `detect_current_worktree()` - Detect if in a worktree
- `cleanup_worktree(issue_number)` - Remove worktree
- `prune_worktrees()` - Clean up stale worktrees
- `slugify(text, max_length)` - Convert to kebab-case
- `get_repo_name()` - Get repository name

**Used by:** start-issue, finish-issue, worktree

### utils.git

Git utility functions.

**Functions:**
- `check_sync_status()` - Check if branch synced with main
- `get_current_branch()` - Get current branch name
- `is_clean_working_tree()` - Check for uncommitted changes

**Used by:** finish-issue, sync

### utils.fs

File system utilities.

**Functions:**
- `find_files(pattern, path)` - Find files matching pattern
- `read_json(file_path)` - Read and parse JSON
- `write_json(file_path, data)` - Write JSON with formatting

**Used by:** Various skills

### utils.format

Terminal formatting utilities.

**Functions:**
- `success(message)` - Format success message (green)
- `error(message)` - Format error message (red)
- `info(message)` - Format info message (blue)
- `warning(message)` - Format warning message (yellow)
- `header(message)` - Format header (bold)

**Used by:** Most skills

### utils.test

Testing utilities.

**Functions:**
- `run_tests(test_path)` - Run tests and return results
- `check_coverage(min_coverage)` - Check test coverage
- `format_test_results(results)` - Format test output

**Used by:** finish-issue, review

## Adding New Shared Code

### When to Add

Add code to `_scripts/` when:
- ✅ Used by 2+ skills
- ✅ Reusable across different contexts
- ✅ Well-defined interface
- ✅ Domain-specific or utility function

**Don't add** to `_scripts/` when:
- ❌ Used by only one skill → Keep in skill's `scripts/`
- ❌ Tightly coupled to one workflow → Keep local
- ❌ Experimental or unstable → Keep in skill until proven

### How to Add

1. **Choose correct domain module:**
   - GitHub operations → `github/`
   - Git operations → `git/`
   - Framework operations → `framework/`
   - Generic utilities → `utils/`

2. **Create or update module:**
   ```bash
   # Create new module
   touch .claude/skills/_scripts/github/api.py

   # Or update existing
   vim .claude/skills/_scripts/utils/git.py
   ```

3. **Update importing skills:**
   ```python
   # Update import path
   from github.api import create_issue
   ```

4. **Document in this README:**
   - Add to Modules section
   - List functions and usage

5. **Test the import:**
   ```bash
   python3 -c "import sys; sys.path.insert(0, '.claude/skills/_scripts'); from git.worktree import list_worktrees; print('OK')"
   ```

## Migration from Old Structure

**Old locations (deprecated):**
- ❌ `scripts/worktree_manager.py`
- ❌ `.claude/skills/_scripts/`

**New locations:**
- ✅ `.claude/skills/_scripts/git/worktree.py`
- ✅ `.claude/skills/_scripts/utils/*.py`

**Import path changes:**
```python
# Old
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))
from worktree_manager import create_worktree

# New
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_scripts"))
from git.worktree import create_worktree
```

## Benefits

| Aspect | Old Structure | New Structure |
|--------|--------------|---------------|
| **Self-contained** | ❌ Depends on `scripts/` | ✅ All in `.claude/skills/` |
| **Import depth** | 5 levels | 2 levels |
| **Organization** | Flat files | Domain-based |
| **Distribution** | Copy 2 dirs | Copy 1 dir |
| **Discovery** | Unclear where code lives | Clear domain structure |

## Related

- **ADR-005**: Skill Shared Libraries Pattern
- **Issue #137**: Migration to `_scripts/`
- **Issue #138**: 3-layer architecture documentation

---

**Version:** 1.0.0
**Last Updated:** 2026-03-12
**Maintained by:** Framework Team
