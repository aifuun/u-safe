# Skill Implementation Guide

> 新Skill开发完整指南 - 从设计到发布的标准流程

**Version**: 1.0.0
**Last Updated**: 2026-03-30
**Compliance**: ADR-001, ADR-014

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [4-Step Development Process](#4-step-development-process)
3. [Code Block Type Annotations](#code-block-type-annotations)
4. [Shared Logic Extraction Rules](#shared-logic-extraction-rules)
5. [Documentation Size Limits](#documentation-size-limits)
6. [Testing Requirements](#testing-requirements)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

**Before you start**, answer these questions:

1. **What problem does this skill solve?**
   - Define the core use case clearly

2. **How complex is the logic?**
   - Use [ADR-016 decision matrix](../docs/ADRs/016-skill-implementation-patterns.md) to score

3. **Which implementation mode?**
   - **Score 0-4**: AI-Executable (pure SKILL.md)
   - **Score 5-9**: Evaluate case-by-case
   - **Score 10-14**: Scripts-Based (Python files)

4. **Is similar functionality already implemented?**
   - Check `.claude/skills/` for existing skills
   - Review `_scripts/` for shared logic

---

## 4-Step Development Process

### Step 1: Design & Planning

#### 1.1 Define Scope

```markdown
## Skill Specification

**Name**: skill-name
**Category**: [workflow/utility/analysis/meta]
**Mode**: [AI-Executable / Scripts-Based]

**Purpose**:
[One-sentence description]

**Trigger Conditions**:
- User says: "..."
- Context: ...

**Input**: [What the skill needs]
**Output**: [What it produces]
**Side Effects**: [Files created, state changed, etc.]
```

#### 1.2 Score with Decision Matrix

Use [ADR-016 scoring matrix](../docs/ADRs/016-skill-implementation-patterns.md#决策矩阵-7个评估维度):

| Dimension | Score (0-2) | Justification |
|-----------|-------------|---------------|
| Code Lines | ? | Estimated lines |
| Execution Frequency | ? | How often used |
| Testing Requirements | ? | Risk level |
| Code Reusability | ? | Shared logic |
| Logic Complexity | ? | Algorithm complexity |
| External Dependencies | ? | Libraries needed |
| Error Handling | ? | Failure scenarios |
| **TOTAL** | **?/14** | **Mode Decision** |

#### 1.3 Create Skill Structure

**For AI-Executable (score 0-4):**
```bash
.claude/skills/<skill-name>/
├── SKILL.md              # All-in-one documentation
└── README.md             # Optional: Extended docs
```

**For Scripts-Based (score 10-14):**
```bash
.claude/skills/<skill-name>/
├── SKILL.md              # Usage guide (<500 lines)
├── scripts/
│   ├── <main>.py        # Main script
│   ├── <helper>.py      # Helper modules (optional)
│   └── tests/
│       └── test_main.py # Unit tests (required)
└── README.md             # Optional: Architecture docs
```

### Step 2: Implementation

#### 2.1 Copy Template

```bash
# Copy the standard template
cp .claude/skills/SKILL_TEMPLATE.md .claude/skills/<skill-name>/SKILL.md

# Edit and fill in all placeholders
```

**Delete the "Implementation Checklist" section** before publishing.

#### 2.2 Write Code (Scripts-Based Only)

**Main script template:**
```python
#!/usr/bin/env python3
\"\"\"
<skill-name> - One-line description

Usage:
    python scripts/<main>.py [args]

Examples:
    python scripts/<main>.py --example
\"\"\"

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add shared modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_scripts"))

from utils.fs import validate_path
from utils.json_handler import read_json, write_json


def main(args: argparse.Namespace) -> int:
    \"\"\"Main entry point\"\"\"
    try:
        # Implementation here
        result = do_work(args)

        print(f"✅ Success: {result}")
        return 0

    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 2


def do_work(args: argparse.Namespace):
    \"\"\"Core logic (separated for testability)\"\"\"
    # Implementation
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Skill description")
    parser.add_argument("arg1", help="Required argument")
    parser.add_argument("--option", help="Optional flag")

    args = parser.parse_args()
    sys.exit(main(args))
```

**Test file template:**
```python
import pytest
import sys
from pathlib import Path

# Add scripts to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

from <main> import do_work, main


class TestDoWork:
    def test_normal_case(self):
        \"\"\"Test typical usage\"\"\"
        result = do_work(mock_args)
        assert result == expected

    def test_error_case(self):
        \"\"\"Test error handling\"\"\"
        with pytest.raises(ValueError):
            do_work(invalid_args)

    def test_edge_case(self):
        \"\"\"Test boundary conditions\"\"\"
        # Edge case tests
        pass
```

#### 2.3 Use Shared Logic

**Check existing modules** before writing new code:

```python
# File system operations
from _scripts.utils.fs import (
    validate_path,        # Check file/directory exists
    ensure_directory,     # Create directory if needed
    safe_read_file,       # Read with error handling
)

# JSON handling
from _scripts.utils.json_handler import (
    read_json,            # Load JSON with validation
    write_json,           # Save JSON with backup
    merge_json,           # Merge JSON objects
)

# Git operations
from _scripts.utils.git import (
    get_current_branch,   # Get active branch
    is_clean_working_tree,# Check for uncommitted changes
)

# CLI utilities
from _scripts.utils.cli import (
    create_parser,        # Standard argument parser
    validate_args,        # Common validation
)

# Framework utilities
from _scripts.framework.issue_detector import detect_issue_number
from _scripts.framework.status_file import read_status, write_status
```

**If shared logic doesn't exist**, extract it (see [Step 4](#step-4-refine--extract)).

### Step 3: Documentation

#### 3.1 Annotate Code Blocks

Use **3 types** of code block annotations:

##### Type 1: AI-EXECUTABLE

```python
# AI-EXECUTABLE - AI can directly run this code
import sys
sys.path.insert(0, '.claude/skills/_scripts')
from framework.issue_detector import detect_issue_number

issue_num = detect_issue_number()
print(f"Detected issue: {issue_num}")
```

**When to use:**
- Code that AI should execute during skill orchestration
- Commands for direct Bash tool invocation
- Quick snippets for validation

**Requirements:**
- Must be self-contained (no undefined variables)
- Use shared modules where possible
- Include error handling

##### Type 2: EXAMPLE-ONLY

```python
# EXAMPLE-ONLY - Reference code, not for direct execution
def example_validation(value: str) -> bool:
    \"\"\"
    This shows the pattern - actual implementation is in
    _scripts/utils/validation.py
    \"\"\"
    if not value:
        raise ValueError("Value cannot be empty")
    return True
```

**When to use:**
- Illustrative code patterns
- Simplified versions of complex logic
- Conceptual examples

**Requirements:**
- Clearly state this is example-only
- Reference actual implementation location
- Don't duplicate production code

##### Type 3: SHARED-LOGIC

```python
# SHARED-LOGIC - This should be extracted to _scripts/
# Current location: SKILL.md
# Target location: _scripts/utils/validation.py

def validate_issue_number(num):
    \"\"\"
    Validate issue number format

    TODO: Extract to shared module if used in 3+ skills
    \"\"\"
    if not isinstance(num, int) or num <= 0:
        raise ValueError(f"Invalid issue number: {num}")
```

**When to use:**
- Logic repeated in 3+ skills
- Complex validation/processing functions
- Utilities that could benefit other skills

**Requirements:**
- Mark as SHARED-LOGIC
- Document target extraction location
- Create tracking issue for extraction

#### 3.2 Write Clear Instructions

**AI Execution Instructions section** must be:
- **Actionable**: Step-by-step, no ambiguity
- **Complete**: Cover all edge cases
- **Tested**: Verify AI can follow successfully

**Example structure:**
```markdown
## AI Execution Instructions

**CRITICAL: [Most important thing to remember]**

### Step 1: Detect Issue Number

**Use the shared detector:**
\`\`\`python
# AI-EXECUTABLE
import sys
sys.path.insert(0, '.claude/skills/_scripts')
from framework.issue_detector import detect_issue_number

issue_num = detect_issue_number(check_github=True, required=True)
\`\`\`

**Fallback if detector fails:**
1. Check branch name: `feature/123-title`
2. Look for active plans: `.claude/plans/active/issue-*.md`
3. Ask user if all fail

### Step 2: Validate Environment

**Check these conditions:**
\`\`\`bash
# Not on main branch
git rev-parse --abbrev-ref HEAD

# No uncommitted changes
git status --porcelain
\`\`\`

**If validation fails:**
- Main branch → Error: "Run /start-issue first"
- Uncommitted changes → Warn: "Stash or commit first"
```

#### 3.3 Document Size Management

**SKILL.md must be <500 lines**

If exceeding, split into:
1. **SKILL.md** (<500 lines): Core usage, common scenarios
2. **REFERENCE.md** (<1000 lines): Advanced topics, edge cases

**How to split:**
```markdown
<!-- In SKILL.md -->
## Advanced Topics

For detailed information on advanced usage:
- Architecture internals → [REFERENCE.md](./REFERENCE.md#architecture)
- Complex error scenarios → [REFERENCE.md](./REFERENCE.md#errors)
- Performance optimization → [REFERENCE.md](./REFERENCE.md#performance)

<!-- In REFERENCE.md -->
# Advanced Reference - Skill Name

## Architecture

[Detailed architecture documentation...]

## Complex Error Scenarios

[Edge cases and troubleshooting...]
```

### Step 4: Refine & Extract

#### 4.1 Identify Duplication

**After implementation**, scan for code used in 3+ places:

```bash
# Find repeated patterns
grep -r "your_function_name" .claude/skills --include="*.md" --include="*.py"

# If appears 3+ times → Extract to _scripts/
```

#### 4.2 Extract to Shared Modules

**Extraction decision tree:**

```
Is this logic used in 3+ skills?
├─ Yes → Extract to _scripts/
│   ├─ General utility? → _scripts/utils/<name>.py
│   ├─ Framework core? → _scripts/framework/<name>.py
│   └─ Git operation? → _scripts/git/<name>.py
└─ No → Keep in skill (but mark as SHARED-LOGIC for future)
```

**Extraction process:**
1. Create module in `_scripts/utils/` (or appropriate location)
2. Move function with type annotations and docstrings
3. Add unit tests in `_scripts/utils/tests/`
4. Update all consuming skills to import from shared module
5. Remove SHARED-LOGIC annotation from consuming skills

#### 4.3 Add Tests (Scripts-Based Only)

**Minimum test coverage: 60%**

**Test structure:**
```python
# tests/test_main.py
import pytest
from pathlib import Path

class TestMainFunction:
    \"\"\"Test the primary function\"\"\"

    def test_normal_case(self):
        \"\"\"Test typical usage\"\"\"
        # Arrange
        input_data = create_test_input()

        # Act
        result = main_function(input_data)

        # Assert
        assert result.status == "success"
        assert result.data == expected_data

    def test_error_handling(self):
        \"\"\"Test error scenarios\"\"\"
        with pytest.raises(ValueError, match="Invalid input"):
            main_function(invalid_input)

    def test_edge_cases(self):
        \"\"\"Test boundary conditions\"\"\"
        # Empty input
        result = main_function([])
        assert result.data == []

        # Maximum size
        large_input = ["item"] * 1000
        result = main_function(large_input)
        assert len(result.data) == 1000


class TestHelperFunctions:
    \"\"\"Test helper utilities\"\"\"

    def test_validation(self):
        assert validate_input("valid") == True
        assert validate_input("") == False
```

**Run tests:**
```bash
# Single skill
cd .claude/skills/<skill-name>
pytest scripts/tests/ -v

# All skills
pytest .claude/skills/*/scripts/tests/ --cov=.claude/skills --cov-report=term-missing
```

---

## Code Block Type Annotations

### Summary Table

| Type | Purpose | AI Action | Duplication Rules |
|------|---------|-----------|-------------------|
| **AI-EXECUTABLE** | Direct execution | Run as-is | Minimize (use shared modules) |
| **EXAMPLE-ONLY** | Illustration | Read only | OK to show patterns |
| **SHARED-LOGIC** | Future extraction | Mark for TODO | Extract if used 3+ times |

### Detailed Guidelines

#### AI-EXECUTABLE

**✅ Good examples:**
```python
# AI-EXECUTABLE
from _scripts.framework.issue_detector import detect_issue_number
issue_num = detect_issue_number()
```

```bash
# AI-EXECUTABLE
git status --porcelain
```

**❌ Bad examples:**
```python
# AI-EXECUTABLE - DON'T DO THIS
import some_non_existent_module  # ❌ Won't work
magic_function()  # ❌ Undefined
```

**Rules:**
- Must run without errors
- All imports must exist
- No undefined variables
- Prefer shared modules over inline code

#### EXAMPLE-ONLY

**✅ Good examples:**
```python
# EXAMPLE-ONLY - Pattern demonstration
# Actual implementation: _scripts/utils/validation.py

def validate_email(email: str) -> bool:
    \"\"\"Simplified example - real version has more checks\"\"\"
    return "@" in email and "." in email
```

**❌ Bad examples:**
```python
# ❌ Missing annotation
def some_function():  # ❌ AI might think this is executable
    pass

# ❌ Pretending to be executable
# AI-EXECUTABLE  # ❌ But code is incomplete
def incomplete_function(missing_params):
    # Missing implementation
```

**Rules:**
- Always annotate as EXAMPLE-ONLY
- Reference actual implementation
- Keep examples simple
- Explain deviations from production code

#### SHARED-LOGIC

**✅ Good examples:**
```python
# SHARED-LOGIC
# Current: SKILL.md (repeated in 3+ skills)
# Target: _scripts/utils/json_handler.py

def safe_read_json(file_path: str) -> dict:
    \"\"\"
    Read JSON with error handling

    TODO: Extract to shared module (used in 5 skills)
    \"\"\"
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")
```

**❌ Bad examples:**
```python
# SHARED-LOGIC - DON'T DO THIS
def one_off_function():  # ❌ Only used once, not shared
    pass

# ❌ Missing target location
# SHARED-LOGIC  # ❌ Where should this go?
def mystery_function():
    pass
```

**Rules:**
- Only for logic appearing 3+ times
- Document current and target location
- Include usage count
- Create tracking issue for extraction

---

## Shared Logic Extraction Rules

### When to Extract

| Usage Count | Action | Priority |
|-------------|--------|----------|
| 1-2 skills | Keep in skill, mark as SHARED-LOGIC | N/A |
| 3-5 skills | Extract to _scripts/ | 🟡 Medium |
| 6-10 skills | Extract immediately | 🔴 High |
| >10 skills | Critical duplication | 🔴 Urgent |

### Extraction Locations

#### _scripts/utils/ (General Utilities)

**For**: Cross-cutting concerns, reusable helpers

**Examples:**
- `fs.py` - File system operations
- `json_handler.py` - JSON read/write with validation
- `cli.py` - Argument parsing templates
- `validation.py` - Common validators
- `format.py` - String/data formatting

**Naming convention**: Descriptive nouns (json_handler, not json_utils)

#### _scripts/framework/ (Core Framework)

**For**: Framework-specific logic, workflow support

**Examples:**
- `issue_detector.py` - Issue number detection
- `status_file.py` - Workflow status management
- `worktree_helper.py` - Git worktree operations
- `plan_parser.py` - Plan file parsing

**Naming convention**: Domain-specific (issue_detector, not detect_utils)

#### _scripts/git/ (Git Operations)

**For**: Git command wrappers, repository operations

**Examples:**
- `worktree.py` - Worktree management
- `branch.py` - Branch operations
- `commit.py` - Commit utilities

**Naming convention**: Git concepts (worktree, not git_worktree_utils)

### Extraction Process

**6-step process:**

1. **Create module file**
```bash
touch _scripts/utils/new_module.py
```

2. **Move function with full context**
```python
# _scripts/utils/new_module.py
\"\"\"
New Module - Brief description

Usage:
    from _scripts.utils.new_module import function_name
\"\"\"

from typing import Optional


def extracted_function(param: str) -> bool:
    \"\"\"
    Function documentation

    Args:
        param: Parameter description

    Returns:
        bool: Return value description

    Raises:
        ValueError: Error conditions

    Example:
        >>> extracted_function("test")
        True
    \"\"\"
    # Implementation
    pass
```

3. **Add tests**
```python
# _scripts/utils/tests/test_new_module.py
import pytest
from _scripts.utils.new_module import extracted_function


def test_extracted_function():
    assert extracted_function("valid") == True

def test_error_handling():
    with pytest.raises(ValueError):
        extracted_function("")
```

4. **Update consuming skills**
```python
# Before (in SKILL.md)
# SHARED-LOGIC
def extracted_function(param):
    # Implementation

# After (in SKILL.md)
# AI-EXECUTABLE
from _scripts.utils.new_module import extracted_function
result = extracted_function("value")
```

5. **Run tests**
```bash
pytest _scripts/utils/tests/test_new_module.py -v
```

6. **Update CHANGELOG**
```markdown
## Shared Modules Changes

- Added `new_module.py`: Description
- Extracted from: skill1, skill2, skill3
```

---

## Documentation Size Limits

### Limits Table

| File Type | Soft Limit | Hard Limit | Action When Exceeded |
|-----------|------------|------------|----------------------|
| SKILL.md | 400 lines | 500 lines | Split to REFERENCE.md or migrate to scripts |
| REFERENCE.md | 800 lines | 1000 lines | Split by topic into multiple files |
| Python script | 250 lines | 300 lines | Extract helper modules |

### Splitting Strategies

#### Strategy 1: SKILL.md → REFERENCE.md

**Split when**: SKILL.md approaches 500 lines

**Keep in SKILL.md** (Core usage):
- Overview
- Arguments
- AI Execution Instructions (critical steps only)
- Common examples (2-3 scenarios)
- Error handling (top 3 errors)

**Move to REFERENCE.md** (Advanced topics):
- Detailed architecture explanations
- Edge case scenarios
- All examples beyond basic 2-3
- Performance optimization details
- Troubleshooting guide
- Internal implementation details

**Template:**
```markdown
<!-- SKILL.md -->
## Advanced Topics

For detailed information:
- [Architecture](./REFERENCE.md#architecture)
- [Error Scenarios](./REFERENCE.md#error-scenarios)
- [Performance](./REFERENCE.md#performance)
- [Troubleshooting](./REFERENCE.md#troubleshooting)

<!-- REFERENCE.md -->
# Reference - Skill Name

## Architecture
[Detailed explanations...]

## Error Scenarios
[Edge cases...]
```

#### Strategy 2: Migrate to Scripts-Based

**Migrate when**: Logic is too complex for pure AI execution

**Process:**
1. Score with ADR-014 matrix
2. If score >9, migrate to scripts
3. Create `scripts/<main>.py`
4. Move code from SKILL.md to Python
5. Simplify SKILL.md to usage guide
6. Add tests

**Result**: SKILL.md shrinks to <300 lines (usage only)

---

## Testing Requirements

### Scripts-Based Skills (Mandatory)

**Minimum coverage**: 60%

**Required tests:**
- ✅ Normal case (happy path)
- ✅ Error handling (expected failures)
- ✅ Edge cases (boundary conditions)
- ✅ Integration (if uses shared modules)

**Test structure:**
```
scripts/tests/
├── test_main.py           # Main script tests
├── test_helpers.py        # Helper function tests
└── fixtures/              # Test data
    ├── valid_input.json
    └── invalid_input.json
```

**Coverage command:**
```bash
pytest scripts/tests/ --cov=scripts --cov-report=term-missing --cov-fail-under=60
```

### AI-Executable Skills (Optional)

**Testing approach:**
- Manual verification through execution
- Document test scenarios in SKILL.md
- Use `/skill-creator` eval system for quality checks

---

## Best Practices

### DO's ✅

1. **Use SKILL_TEMPLATE.md** as starting point
2. **Score with ADR-014** before implementing
3. **Annotate all code blocks** (AI-EXECUTABLE/EXAMPLE-ONLY/SHARED-LOGIC)
4. **Extract shared logic** when used 3+ times
5. **Keep SKILL.md <500 lines** (split or migrate if larger)
6. **Write tests** for scripts-based skills (>60% coverage)
7. **Use type annotations** in Python code
8. **Handle errors gracefully** (no empty catch blocks)
9. **Document edge cases** in Error Handling section
10. **Version your skill** (semantic versioning)

### DON'Ts ❌

1. **Don't duplicate code** - use shared modules
2. **Don't omit annotations** - always tag code blocks
3. **Don't skip tests** for scripts-based skills
4. **Don't hardcode paths** - use Path() or shared utils
5. **Don't use sys.path.insert** - rely on PYTHONPATH
6. **Don't write >500 line SKILL.md** - split or migrate
7. **Don't guess at shared logic** - check _scripts/ first
8. **Don't forget versioning** - update changelog
9. **Don't ignore ADR-014** - follow decision matrix
10. **Don't leave TODOs** in production - extract or remove

---

## Troubleshooting

### Issue: "Where should I put this code?"

**Decision tree:**
```
Is this code used in 3+ skills?
├─ Yes → Extract to _scripts/
│   ├─ General utility? → _scripts/utils/
│   ├─ Framework feature? → _scripts/framework/
│   └─ Git operation? → _scripts/git/
└─ No → Keep in skill
    ├─ Will be used later? → Mark as SHARED-LOGIC
    └─ One-off code? → Keep inline, mark as AI-EXECUTABLE or EXAMPLE-ONLY
```

### Issue: "SKILL.md is too long (>500 lines)"

**Solutions** (in priority order):
1. **Split to REFERENCE.md** - Move advanced topics
2. **Migrate to scripts** - If score >9 in ADR-014
3. **Remove redundant content** - Delete unnecessary examples
4. **Extract shared logic** - Move duplicated code to _scripts/

### Issue: "Code block annotation confusion"

**Quick reference:**
- **AI will execute this** → AI-EXECUTABLE
- **Just showing a pattern** → EXAMPLE-ONLY
- **Should be in _scripts/** → SHARED-LOGIC

### Issue: "Test coverage too low (<60%)"

**Coverage boosting strategies:**
1. Test normal cases first (quick wins)
2. Add error case tests (raises exceptions)
3. Test edge cases (boundary conditions)
4. Mock external dependencies (filesystem, network)
5. Use parametrize for multiple inputs

---

## Appendix

### Related Documents

- [ADR-001: Official Skill Patterns](../docs/ADRs/001-official-skill-patterns.md)
- [ADR-016: Skill Implementation Patterns](../docs/ADRs/016-skill-implementation-patterns.md)
- [SKILL_TEMPLATE.md](./SKILL_TEMPLATE.md)
- [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)

### Tools

- `/skill-creator` - Generate new skills
- `pytest` - Run unit tests
- `wc -l` - Count lines in files

### Support

Questions or issues? Create an issue on GitHub with:
- Skill name and description
- ADR-014 score breakdown
- Specific question or problem

---

**Version:** 1.0.0
**Last Updated:** 2026-03-30
**Changelog:**
- v1.0.0: Initial release with 4-step process, 3 annotation types, extraction rules
