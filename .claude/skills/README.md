# Claude Code Skills System

**Version**: 4.0.0 (Streamlined Edition)
**Last Updated**: 2026-03-18
**Active Skills**: 21
**Policy**: Python-only ([ADR-003](../../docs/ADRs/003-python-only-for-skill-scripts.md))

> **Purpose**: Navigation hub for Claude Code skills - quick reference and links to detailed documentation.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [Active Skills Reference](#active-skills-reference)
4. [Core Policies](#core-policies)
5. [File Structure](#file-structure)
6. [Getting Help](#getting-help)

---

## Quick Start

### Essential Daily Workflow (4 Skills)

```bash
/status    # Check project health + generate HTML report
/next      # Get next task from active plan
/plan      # Create implementation plan for new feature
/adr       # Record architectural decision
```

### Complete Issue Lifecycle

```bash
# 1. Start working on issue
/start-issue #42
  → Creates feature branch
  → Generates implementation plan
  → Syncs with main

# 2. Implement (loop)
/next              # Get current task
# ... code ...
/adr create "..."  # Record decisions
/review           # Self-review code

# 3. Complete issue
/finish-issue #42
  → Commits changes
  → Creates PR
  → Merges and closes issue
```

### Framework Management

```bash
# Sync entire framework (recommended)
/update-framework --from ~/dev/ai-dev

# Or sync individual components
/update-skills --from ~/dev/ai-dev
/update-pillars --from ~/dev/ai-dev
/update-rules --from ~/dev/ai-dev
/update-workflow --from ~/dev/ai-dev
```

---

## Architecture

### 3-Layer Skill Architecture

Skills follow a **3-layer architecture** for clear separation of concerns:

| Layer | Purpose | Tool/Pattern | Examples |
|-------|---------|--------------|----------|
| **Layer 1: Meta-Skills** | Orchestrate workflows | `Skill` tool | `/solve-issues`, `/auto-solve-issue`, `/dev-issue` |
| **Layer 2: Atomic Skills** | Single operations | Python `import` | `/start-issue`, `/finish-issue`, `/eval-plan` |
| **Layer 3: Python Libraries** | Reusable code | Python modules | `worktree_manager.py`, `issue_detector.py` |

**Quick Decision Tree**:
```
Orchestrate multiple skills? → Meta-skill (Layer 1, use Skill tool)
Perform single operation? → Atomic skill (Layer 2, may import Layer 3)
Shared code logic? → Python library (Layer 3, imported by Layer 2)
```

**Composition Rules**:
- ✅ Meta-skills call Atomic skills via Skill tool
- ✅ Atomic skills import Python libraries
- ❌ Never: Atomic skill calls Atomic skill (use Meta-skill or extract to Layer 3)
- ❌ Never: Python library calls Skill tool (breaks separation)

**See**:
- [ARCHITECTURE.md](ARCHITECTURE.md) - Complete implementation guide with decision trees, patterns, and examples
- [ADR-006](../../docs/ADRs/006-skill-composition-pattern.md) - Architectural decision record
- [ADR-005](../../docs/ADRs/005-skill-shared-libraries-pattern.md) - Code organization patterns

---

## Active Skills Reference

**21 skills** organized by usage frequency. Each skill has detailed `SKILL.md` documentation.

### 🔥 High Frequency (Daily/Weekly)

| Skill | Purpose | Command | Details |
|-------|---------|---------|---------|
| **status** | Project health check + HTML report | `/status` | [SKILL.md](status/SKILL.md) |
| **overview** | Comprehensive project overview | `/overview` | [SKILL.md](overview/SKILL.md) |
| **next** | Get next task from plan | `/next` | [SKILL.md](next/SKILL.md) |
| **plan** | Create implementation plans | `/plan "feature"` | [SKILL.md](plan/SKILL.md) |
| **adr** | Manage Architecture Decision Records | `/adr create "title"` | [SKILL.md](adr/SKILL.md) |

### 📅 Medium Frequency (Weekly)

| Skill | Purpose | Command | Details |
|-------|---------|---------|---------|
| **start-issue** | Begin GitHub issue workflow | `/start-issue #N` | [SKILL.md](start-issue/SKILL.md) |
| **eval-plan** | Validate plan before execution | `/eval-plan [#N]` | [SKILL.md](eval-plan/SKILL.md) |
| **execute-plan** | Execute implementation plan step-by-step | `/execute-plan #N` | [SKILL.md](execute-plan/SKILL.md) |
| **finish-issue** | Complete issue (commit + PR + merge) | `/finish-issue #N` | [SKILL.md](finish-issue/SKILL.md) |
| **solve-issues** | Batch wrapper for single/multiple issues | `/solve-issues #N` or `/solve-issues [N, M]` | [SKILL.md](solve-issues/SKILL.md) |
| **auto-solve-issue** | Core implementation with Task dependencies + Subagents | `/auto-solve-issue #N [--auto]` | [SKILL.md](auto-solve-issue/SKILL.md) |
| **work-issue** | ⚠️ DELETED in v2.1.0 - use `/solve-issues` or `/auto-solve-issue` | N/A | See [Migration Guide](../../CLAUDE.md#-migration-guide-work-issue--solve-issues) |
| **review** | Code quality review | `/review [file/branch]` | [SKILL.md](review/SKILL.md) |
| **sync** | Sync branch with main | `/sync` | [SKILL.md](sync/SKILL.md) |
| **dev-issue** | ⚠️ DEPRECATED - use `/execute-plan` | `/dev-issue #N` | [SKILL.md](dev-issue/SKILL.md) |

### 🔧 Framework Management

| Skill | Purpose | Command | Details |
|-------|---------|---------|---------|
| **update-framework** | Sync all framework components | `/update-framework --from <path>` | [SKILL.md](update-framework/SKILL.md) |
| **update-skills** | Sync skills only | `/update-skills --from <path>` | [SKILL.md](update-skills/SKILL.md) |
| **update-pillars** | Sync Pillars only | `/update-pillars --from <path>` | [SKILL.md](update-pillars/SKILL.md) |
| **update-rules** | Sync rules only | `/update-rules --from <path>` | [SKILL.md](update-rules/SKILL.md) |
| **update-workflow** | Sync workflow docs | `/update-workflow --from <path>` | [SKILL.md](update-workflow/SKILL.md) |

### 🛠️ Specialized Tools

| Skill | Purpose | Command | Details |
|-------|---------|---------|---------|
| **init-docs** | Auto-generate documentation structure | `/init-docs [--profile]` | [SKILL.md](init-docs/SKILL.md) |
| **check-docs** | Validate documentation structure compliance | `/check-docs [--fix]` | [SKILL.md](check-docs/SKILL.md) |
| **skill-creator** | Create/update skills with evals | `/skill-creator "create..."` | [SKILL.md](skill-creator/SKILL.md) |
| **refers** | Official Anthropic skills reference (non-invocable) | N/A | [SKILL.md](refers/SKILL.md) |

**Note**: Each skill's `SKILL.md` contains:
- Detailed usage instructions
- Examples and best practices
- Troubleshooting guide
- Integration with other skills

---

## Core Policies

### 3-Layer Architecture ([ADR-006](../../docs/ADRs/006-skill-composition-pattern.md))

**All skills MUST follow the 3-layer architecture** for composition and code organization.

**Layer Guidelines**:
- **Layer 1 (Meta-Skills)**: Orchestration via SKILL.md, use Skill tool
- **Layer 2 (Atomic Skills)**: Single operations, may import Layer 3 libraries
- **Layer 3 (Python Libraries)**: Reusable code in `.claude/skills/_scripts/framework/`

**Composition Patterns**:
- Meta-skill → Atomic skills: Use Skill tool
- Atomic skill → Python libraries: Use Python import
- Avoid: Atomic ↔ Atomic (create Meta-skill or extract to Layer 3)

**See**: [ARCHITECTURE.md](ARCHITECTURE.md) for complete implementation guide

### Python-Only Policy ([ADR-003](../../docs/ADRs/003-python-only-for-skill-scripts.md))

**All skill scripts MUST use Python 3.9+** - Bash is prohibited.

**Why Python?**
- ✅ Type safety with type hints
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Better error handling and debugging
- ✅ Rich testing ecosystem (pytest, unittest)
- ✅ IDE support with autocomplete

**Migration Status**: ✅ Complete (2026-03-09)
- 1,182 lines Bash → 3,088 lines Python
- 58 passing unit tests
- CI enforcement active

**Resources**:
- [PYTHON_GUIDE.md](PYTHON_GUIDE.md) - Complete development guide
- [Shared Libraries](_scripts/README.md) - Reusable modules (git, github, framework, utils)
- [ADR-003](../../docs/ADRs/003-python-only-for-skill-scripts.md) - Policy rationale

### Skill Patterns ([ADR-001](../../docs/ADRs/001-official-skill-patterns.md))

**Required Structure**:
```
skill-name/
├── SKILL.md              # Documentation (required)
└── scripts/              # Python scripts (optional)
    ├── main_script.py
    └── tests/
        └── test_*.py
```

**YAML Frontmatter** (in SKILL.md):
```yaml
---
name: skill-name
description: |
  What it does.
  TRIGGER when: [conditions]
  DO NOT TRIGGER when: [exclusions]
version: "1.0.0"           # Semantic version (major.minor.patch)
allowed-tools: Read, Write, Bash(git *)
---
```

**Version Field** (Required as of ADR-008):
- Format: `"major.minor.patch"` (string with quotes)
- Enables semantic version comparison in `/update-skills`
- Also add `**Version:** X.Y.Z` at bottom of SKILL.md for backward compatibility

**Quality Standards**:
- Simple: <200 lines | Standard: 200-350 lines | Complex: >400 lines
- Python 3.9+ with type hints (mandatory)
- Workflow skills must use TaskCreate/TaskUpdate (see below)

**Workflow Skills Pattern**:

Multi-step skills (start-issue, finish-issue, sync) have special requirements:
1. **TaskCreate** at start - Create todo list for progress tracking
2. **TaskUpdate** during execution - Update task status as work progresses
3. **Verification checklist** - Final validation before completion

This pattern enables:
- Real-time progress visibility in Claude Code UI
- Clear task dependencies and sequencing
- Consistent user experience across workflow skills

**See**:
- [WORKFLOW_PATTERNS.md](WORKFLOW_PATTERNS.md) - Complete implementation guide (travels with skills)
- [ADR-001](../../docs/ADRs/001-official-skill-patterns.md) - Official pattern specification

### Skill Management ([ADR-002](../../docs/ADRs/002-skill-creation-workflow.md))

**Creating/Updating Skills**:
1. Use `/skill-creator` for new skills or updates
2. Follow ADR-001 patterns
3. Update this README if adding/removing skills
4. Verify with 3-level testing (Quick/Basic/Full)

**This README is the single source of truth** for:
- Active skills inventory
- Directory structure standards
- File organization patterns

**See**: [ADR-002](../../docs/ADRs/002-skill-creation-workflow.md) for workflow details

---

## File Structure

### Overview

```
.claude/skills/
├── README.md                    # This file - navigation hub
├── PYTHON_GUIDE.md              # Complete Python development guide
│
├── _scripts/                    # Shared libraries (all skills)
│   ├── README.md                # Library documentation
│   ├── github/                  # GitHub operations
│   ├── git/                     # Git operations (worktree, etc.)
│   ├── framework/               # Framework sync utilities
│   └── utils/                   # Generic utilities (git, fs, format, test)
│
├── {skill-name}/                # 17 active skills
│   ├── SKILL.md                 # Skill documentation
│   └── scripts/                 # Python scripts (optional)
│       ├── *.py
│       └── tests/
```

### Example: Overview Skill (Python Structure)

```
overview/
├── SKILL.md
└── scripts/
    ├── overview.py              # Main entry point
    ├── collectors/              # Data collection modules
    │   ├── git_collector.py
    │   ├── project_collector.py
    │   ├── framework_collector.py
    │   ├── pattern_detector.py
    │   └── work_collector.py
    ├── formatters/              # Output formatting
    │   ├── health_calculator.py
    │   ├── terminal_formatter.py
    │   └── html_formatter.py
    ├── templates/               # HTML templates
    └── tests/                   # Integration tests
```

**All scripts are Python** - zero Bash scripts exist (verified by CI).

### Shared Libraries Usage

```python
#!/usr/bin/env python3
"""Example skill script using shared libraries."""

import sys
from pathlib import Path

# Add _scripts to path (2 levels up)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / '_scripts'))

from utils.git import get_current_branch, check_sync_status
from utils.fs import safe_read_file, safe_write_file
from utils.format import success, error, info
from git.worktree import create_worktree, list_worktrees

def main() -> int:
    """Main entry point."""
    try:
        branch = get_current_branch()
        print(info(f"Current branch: {branch}"))

        if check_sync_status():
            print(success("✅ Branch is synced"))
        else:
            print(error("❌ Branch out of sync"))

        return 0
    except Exception as e:
        print(error(f"Error: {e}"))
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

**See**: [_scripts/README.md](_scripts/README.md) for complete API reference

---

## Getting Help

### Finding Information

| Need | Location |
|------|----------|
| **Skill usage** | `.claude/skills/{skill-name}/SKILL.md` |
| **Python development** | [PYTHON_GUIDE.md](PYTHON_GUIDE.md) |
| **Shared libraries API** | [_scripts/README.md](_scripts/README.md) |
| **Skill patterns** | [ADR-001](../../docs/ADRs/001-official-skill-patterns.md) |
| **Creation workflow** | [ADR-002](../../docs/ADRs/002-skill-creation-workflow.md) |
| **Python-only policy** | [ADR-003](../../docs/ADRs/003-python-only-for-skill-scripts.md) |

### Common Issues

**Skill not triggering?**
- Check `description` field in SKILL.md has clear TRIGGER/DO NOT TRIGGER conditions
- Verify YAML frontmatter is valid
- See: [ADR-001](../../docs/ADRs/001-official-skill-patterns.md) for triggering patterns

**Python import errors?**
- Verify _scripts path: `sys.path.insert(0, str(Path(__file__).parent.parent.parent / '_scripts'))`
- Check Python version: `python3 --version` (requires 3.9+)
- See: [PYTHON_GUIDE.md](PYTHON_GUIDE.md) troubleshooting section

**Need to add/modify skills?**
- Use `/skill-creator` for guided workflow
- Update this README if inventory changes
- See: [ADR-002](../../docs/ADRs/002-skill-creation-workflow.md)

### Quick Reference

```bash
# View skill documentation
cat .claude/skills/{skill-name}/SKILL.md

# List all skills
ls -1 .claude/skills/ | grep -v "^_" | grep -v "\.md$"

# Test shared libraries (example)
python3 -c "import sys; sys.path.insert(0, '.claude/skills/_scripts'); from git.worktree import list_worktrees; print('OK')"

# Verify Python-only (should show 0)
find .claude/skills -name "*.sh" | wc -l
```

---

## Contributing

### Adding New Skills

1. **Use skill-creator**: `/skill-creator "create {skill-name}"`
2. **Follow patterns**: See [ADR-001](../../docs/ADRs/001-official-skill-patterns.md)
3. **Use Python**: All scripts must be Python 3.9+ ([ADR-003](../../docs/ADRs/003-python-only-for-skill-scripts.md))
4. **Update this README**: Add to appropriate frequency category
5. **Test**: Follow [ADR-002](../../docs/ADRs/002-skill-creation-workflow.md) 3-level testing

### Updating Existing Skills

1. **Use skill-creator**: `/skill-creator "improve {skill-name}"`
2. **Test changes**: Quick validation (5-15 min)
3. **Update README**: If usage or structure changed
4. **Document**: Update SKILL.md with new examples

### Maintenance

**This README should be**:
- ✅ Navigation hub with links to detailed docs
- ✅ Accurate skill inventory (verify with `ls`)
- ✅ Quick reference for common tasks
- ✅ Updated when skills added/removed/reorganized

**This README should NOT**:
- ❌ Duplicate SKILL.md content
- ❌ Include exhaustive examples (link to them)
- ❌ Maintain extensive historical information
- ❌ Explain policies in detail (link to ADRs)

---

## References

### Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - 3-layer skill architecture implementation guide
- [PYTHON_GUIDE.md](PYTHON_GUIDE.md) - Python development guide (493 lines)
- [WORKFLOW_PATTERNS.md](WORKFLOW_PATTERNS.md) - Workflow skill implementation patterns
- [_scripts/README.md](_scripts/README.md) - Shared libraries API reference
- Individual SKILL.md files - Detailed usage per skill

### Architecture Decision Records

- [ADR-001](../../docs/ADRs/001-official-skill-patterns.md) - Official skill patterns
- [ADR-002](../../docs/ADRs/002-skill-creation-workflow.md) - Skill creation workflow
- [ADR-003](../../docs/ADRs/003-python-only-for-skill-scripts.md) - Python-only policy
- [ADR-005](../../docs/ADRs/005-skill-shared-libraries-pattern.md) - Skill shared libraries pattern (code organization)
- [ADR-006](../../docs/ADRs/006-skill-composition-pattern.md) - Skill composition pattern (how skills compose)

### Related

- [Framework CLAUDE.md](../../CLAUDE.md) - Overall framework documentation
- [Issue #82](https://github.com/aifuun/ai-dev/issues/82) - Bash-to-Python migration (completed)
- [Issue #93](https://github.com/aifuun/ai-dev/issues/93) - This README rewrite

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 4.0.0 | 2026-03-10 | Complete rewrite - streamlined from 696 to 392 lines |
| 3.0.0 | 2026-03-04 | Streamlined edition (696 lines) |
| 2.x | 2026-02 | Python migration period |
| 1.x | 2025 | Original Bash-based implementation |

---

**Status**: Production Ready 🚀
**Philosophy**: Less is More - Navigation over Duplication
**Feedback**: [Open an issue](https://github.com/aifuun/ai-dev/issues)
