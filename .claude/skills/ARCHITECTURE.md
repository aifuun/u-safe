# Skill Architecture Guide

> Practical guide to the 3-layer skill architecture: when to use what, how to compose skills, and implementation patterns.

**For architectural decisions and rationale**, see [ADR-006: Skill Composition Pattern](../../docs/ADRs/006-skill-composition-pattern.md).

---

## Quick Reference

| Layer | Purpose | Tool/Pattern | Examples |
|-------|---------|--------------|----------|
| **Layer 1: Meta-Skills** | Orchestrate workflows | `Skill` tool | `/work-issue`, `/dev-issue` |
| **Layer 2: Atomic Skills** | Single operations | Python `import` | `/start-issue`, `/finish-issue`, `/eval-plan` |
| **Layer 3: Python Libraries** | Reusable code | Python modules | `worktree_manager.py`, `issue_detector.py` |

---

## 3-Layer Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Meta-Skills (Workflow Orchestration)              │
│                                                             │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│ │ /work-issue │  │ /dev-issue  │  │ Custom      │        │
│ │             │  │             │  │ Workflows   │        │
│ └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                │                │                │
│         └────────────────┴────────────────┘                │
│                          │                                  │
│         Uses: Skill tool (inter-skill communication)        │
└─────────────────────────┬───────────────────────────────────┘
                          │ Calls via Skill tool
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Atomic Skills (Single Operations)                 │
│                                                             │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│ │  start   │ │   eval   │ │ execute  │ │  finish  │      │
│ │  issue   │ │   plan   │ │   plan   │ │  issue   │      │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│      │            │            │            │               │
│      └────────────┴────────────┴────────────┘               │
│                          │                                   │
│         Uses: Python import (code reuse)                     │
└─────────────────────────┬────────────────────────────────────┘
                          │ Imports
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Python Libraries (Reusable Code)                  │
│                                                             │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│ │  worktree   │  │    issue    │  │    plan     │        │
│ │  manager    │  │  detector   │  │   parser    │        │
│ └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│ Pure Python modules - no Skill tool usage                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Decision Tree: Which Layer?

Use this decision tree when creating new functionality:

```
START: What are you building?
│
├─ Does it orchestrate multiple skills?
│  │
│  ├─ YES → Layer 1: Meta-Skill
│  │        - Create: .claude/skills/{name}/SKILL.md
│  │        - Use: Skill tool to call other skills
│  │        - Example: /work-issue orchestrates 5 skills
│  │
│  └─ NO → Continue...
│
├─ Does it perform a single, well-defined operation?
│  │
│  ├─ YES → Layer 2: Atomic Skill
│  │        - Create: .claude/skills/{name}/SKILL.md + scripts/
│  │        - Use: Python import for shared code
│  │        - Example: /start-issue creates branch + plan
│  │
│  └─ NO → Continue...
│
└─ Is it shared logic used by 2+ skills?
   │
   ├─ YES → Layer 3: Python Library
   │        - Create: .claude/skills/_scripts/framework/{name}.py
   │        - Use: Pure Python, imported by skills
   │        - Example: worktree_manager.py for worktree ops
   │
   └─ NO → Reconsider scope
            - Too narrow? → Add to existing skill
            - Too broad? → Break into multiple layers
```

---

## Composition Patterns

### Pattern 1: Meta-Skill → Atomic Skills (Skill Tool)

**When**: Orchestrating complete workflows

**How**: Use `Skill` tool in SKILL.md

**Example**: `/work-issue` orchestration
```markdown
# Meta-Skill: /work-issue

## Workflow

Phase 1: Start issue
→ Invoke: /start-issue #23 (via Skill tool)

Phase 2: Validate plan
→ Invoke: /eval-plan (via Skill tool)

Phase 3: Execute implementation
→ Invoke: /execute-plan #23 (via Skill tool)

Phase 4: Quality check
→ Invoke: /review (via Skill tool)

Phase 5: Finalize
→ Invoke: /finish-issue #23 (via Skill tool)
```

**Why Skill tool**: Each skill has independent context and state

### Pattern 2: Atomic Skill → Python Library (Import)

**When**: Reusing shared functionality

**How**: Python `import` statement

**Example**: `/start-issue` using worktree manager
```python
# .claude/skills/start-issue/scripts/start.py

import sys
from pathlib import Path

# Add shared scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_scripts"))

from framework.worktree_manager import create_worktree, list_worktrees
from framework.issue_detector import detect_issue_number

# Use imported functions
issue_num = detect_issue_number()
worktree_path = create_worktree(repo, issue_num, title)
```

**Why import**: Shared code logic, no separate user interface needed

### Pattern 3: Atomic Skill ↔ Atomic Skill (ANTI-PATTERN)

**When**: NEVER - this is an anti-pattern

**Problem**: Creates tight coupling between Atomic skills

**Wrong**:
```markdown
# ❌ WRONG: /start-issue calls /worktree internally
# Creates coupling, breaks single responsibility
```

**Correct Solutions**:

**Option A**: Extract to Layer 3 (Python library)
```python
# ✅ Both skills import worktree_manager.py
# /start-issue imports worktree_manager
# /worktree imports worktree_manager
```

**Option B**: Create Meta-Skill (Layer 1)
```markdown
# ✅ Create /my-workflow that orchestrates both
# /my-workflow calls /start-issue then /worktree
```

---

## Import Patterns

### Layer 1: Meta-Skills (No Imports)

**File Structure**:
```
.claude/skills/{meta-skill}/
├── SKILL.md           # Orchestration logic
└── (no scripts/)      # Pure documentation
```

**Usage in SKILL.md**:
```markdown
Invoke: /skill-name #arg (via Skill tool)
```

**No Python scripts**: Meta-skills are pure orchestration via documentation

### Layer 2: Atomic Skills (Import Layer 3)

**File Structure**:
```
.claude/skills/{atomic-skill}/
├── SKILL.md           # Documentation
├── scripts/           # Implementation
│   ├── main.py        # Entry point
│   └── utils.py       # Internal helpers (optional)
└── tests/             # Unit tests (optional)
```

**Import Pattern**:
```python
# scripts/main.py
import sys
from pathlib import Path

# Add framework scripts to Python path
FRAMEWORK_PATH = Path(__file__).parent.parent.parent / "_scripts"
sys.path.insert(0, str(FRAMEWORK_PATH))

# Import shared libraries (Layer 3)
from framework.worktree_manager import create_worktree
from framework.issue_detector import detect_issue_number
from framework.plan_parser import parse_plan

# Use imported modules
issue_num = detect_issue_number()
create_worktree(repo, issue_num, title)
```

**Key Points**:
- Always use `sys.path.insert(0, ...)` before imports
- Import from `framework.*` (convention)
- Graceful fallback if library missing (optional)

### Layer 3: Python Libraries (No Skill Tool)

**File Structure**:
```
.claude/skills/_scripts/framework/
├── __init__.py              # Makes it a package
├── worktree_manager.py      # Worktree operations
├── issue_detector.py        # Issue number detection
├── plan_parser.py           # Plan parsing
└── tests/                   # Unit tests
    ├── test_worktree.py
    └── test_detector.py
```

**Module Pattern**:
```python
# framework/worktree_manager.py
"""Worktree management utilities.

Used by: start-issue, finish-issue, worktree

Provides:
- create_worktree()
- list_worktrees()
- cleanup_worktree()
"""

def create_worktree(repo_path, issue_num, title):
    """Create git worktree for issue.

    Args:
        repo_path: Path to main repository
        issue_num: Issue number
        title: Issue title (kebab-case)

    Returns:
        str: Absolute path to worktree

    Raises:
        WorktreeError: If creation fails
    """
    # Implementation
    pass
```

**Key Points**:
- Docstrings document usage
- List consuming skills
- No Skill tool usage
- Testable in isolation

---

## Best Practices

### 1. Single Responsibility

**Each skill has ONE job**:
- ✅ `/start-issue` - Create branch + plan
- ✅ `/finish-issue` - Commit + PR + merge
- ❌ `/do-everything` - Too broad, split into multiple skills

### 2. Composition Over Complexity

**Prefer small, composable skills**:
- ✅ `/work-issue` = `/start-issue` + `/eval-plan` + `/execute-plan` + `/review` + `/finish-issue`
- ❌ One giant skill with all logic inline

### 3. Layer Separation

**Respect layer boundaries**:
- ✅ Meta-skill uses Skill tool
- ✅ Atomic skill imports Python library
- ❌ Python library calls Skill tool
- ❌ Atomic skill calls another Atomic skill

### 4. Documentation

**Each layer needs different docs**:
- **Layer 1**: Workflow sequence, checkpoints, integration
- **Layer 2**: Arguments, steps, examples, error handling
- **Layer 3**: Docstrings, usage examples, parameters, return values

### 5. Testing

**Test at appropriate layer**:
- **Layer 1**: Integration tests (full workflow)
- **Layer 2**: Skill tests (mocked Layer 3)
- **Layer 3**: Unit tests (pure functions)

---

## Common Patterns

### Pattern A: Sequential Workflow

**Use Case**: Multi-step process with dependencies

**Implementation**: Meta-skill (Layer 1) orchestrating Atomic skills (Layer 2)

**Example**: `/work-issue`
```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
(Linear dependency chain)
```

### Pattern B: Parallel Operations

**Use Case**: Independent operations that can run concurrently

**Implementation**: Meta-skill calling multiple Atomic skills in parallel

**Example**: `/sync-all` (hypothetical)
```
Branch 1: /sync-branch
Branch 2: /sync-dependencies
Branch 3: /sync-tests
(No dependencies between branches)
```

### Pattern C: Conditional Workflow

**Use Case**: Different paths based on conditions

**Implementation**: Meta-skill with decision logic

**Example**: `/work-issue --auto`
```
If eval-plan score > 90:
  → Skip checkpoint, proceed
Else:
  → Stop at checkpoint for review
```

### Pattern D: Shared Utilities

**Use Case**: Common code used by multiple skills

**Implementation**: Python library (Layer 3) imported by Atomic skills

**Example**: `issue_detector.py`
```
Used by:
- /start-issue
- /execute-plan
- /eval-plan
- /finish-issue
```

---

## Examples

### Example 1: Create Meta-Skill

**User Request**: "Automate complete issue lifecycle"

**Solution**: Create `/work-issue` (Layer 1)

**Steps**:
1. Identify Atomic skills: `/start-issue`, `/eval-plan`, `/execute-plan`, `/review`, `/finish-issue`
2. Create `.claude/skills/work-issue/SKILL.md`
3. Document workflow sequence
4. Define checkpoints (validation gates)
5. Use Skill tool for invocations

**Result**: User runs `/work-issue #23` → automated end-to-end workflow

### Example 2: Create Atomic Skill

**User Request**: "Validate implementation plan before execution"

**Solution**: Create `/eval-plan` (Layer 2)

**Steps**:
1. Create `.claude/skills/eval-plan/SKILL.md`
2. Create `.claude/skills/eval-plan/scripts/evaluate.py`
3. Import `plan_parser.py` (Layer 3) for parsing
4. Implement validation logic
5. Return score + recommendations

**Result**: User runs `/eval-plan` → plan quality report

### Example 3: Create Python Library

**User Request**: "Multiple skills need to detect issue number"

**Solution**: Create `issue_detector.py` (Layer 3)

**Steps**:
1. Create `.claude/skills/_scripts/framework/issue_detector.py`
2. Implement 4 detection strategies (branch, plan, worktree, user input)
3. Add docstrings and type hints
4. Write unit tests
5. Update consuming skills to import

**Result**: `/start-issue`, `/execute-plan`, `/eval-plan` all use `detect_issue_number()`

---

## Migration Guide

### Existing Skill Violates Architecture?

**Step 1: Identify Layer**
- Orchestrates skills? → Should be Layer 1
- Single operation? → Should be Layer 2
- Shared code? → Should be Layer 3

**Step 2: Refactor**

**If Atomic skill calls Atomic skill**:
```python
# Before (Layer 2 calling Layer 2)
# start-issue/scripts/start.py calls worktree skill

# After: Extract to Layer 3
# start-issue/scripts/start.py imports worktree_manager.py
# worktree/scripts/manage.py imports worktree_manager.py
```

**If Python library uses Skill tool**:
```python
# Before (Layer 3 using Skill tool)
# shared_lib.py calls /some-skill

# After: Create Layer 2 wrapper
# shared_lib.py provides function
# new_skill/scripts/main.py imports shared_lib, exposes via Skill
```

**Step 3: Test**
- Verify functionality unchanged
- Run existing tests
- Add new tests if needed

**Step 4: Document**
- Update SKILL.md to reflect layer
- Add composition pattern examples
- Link to this ARCHITECTURE.md

---

## Anti-Patterns

### Anti-Pattern 1: Mega-Skill

**Problem**: One skill does everything

**Example**:
```
/do-everything
├── Start issue
├── Plan
├── Execute
├── Review
├── Finish
└── Deploy
```

**Solution**: Split into Meta-skill + Atomic skills
```
/complete-workflow (Layer 1)
  → /start-issue (Layer 2)
  → /execute-plan (Layer 2)
  → /review (Layer 2)
  → /finish-issue (Layer 2)
```

### Anti-Pattern 2: Circular Dependencies

**Problem**: Skills depend on each other

**Example**:
```
/skill-a imports /skill-b
/skill-b imports /skill-a
```

**Solution**: Extract shared logic to Layer 3
```
/skill-a imports shared_lib.py (Layer 3)
/skill-b imports shared_lib.py (Layer 3)
```

### Anti-Pattern 3: Library Calling Skills

**Problem**: Python library uses Skill tool

**Example**:
```python
# shared_lib.py
def do_something():
    # ❌ WRONG: Library calling skill
    Skill("some-skill", args="...")
```

**Solution**: Invert dependency
```python
# shared_lib.py
def do_something():
    # ✅ CORRECT: Provide function
    return result

# some-skill/scripts/main.py
from framework.shared_lib import do_something
result = do_something()  # Call from skill, not library
```

### Anti-Pattern 4: Duplicated Code

**Problem**: Same logic in multiple skills

**Example**:
```
/start-issue/scripts/worktree.py (100 lines)
/finish-issue/scripts/worktree.py (100 lines, same code)
/worktree/scripts/manage.py (100 lines, same code)
```

**Solution**: Extract to Layer 3
```
.claude/skills/_scripts/framework/worktree_manager.py (100 lines)
All skills import worktree_manager.py
```

---

## References

- **[ADR-005](../../docs/ADRs/005-skill-shared-libraries-pattern.md)** - Skill Shared Libraries Pattern (code organization)
- **[ADR-006](../../docs/ADRs/006-skill-composition-pattern.md)** - Skill Composition Pattern (architectural decisions)
- **[WORKFLOW_PATTERNS.md](./WORKFLOW_PATTERNS.md)** - Workflow skill implementation patterns
- **[README.md](./README.md)** - Skills overview and index

---

**Maintained by**: AI Dev Framework Team
**Last Updated**: 2026-03-12
**Version**: 1.0.0
