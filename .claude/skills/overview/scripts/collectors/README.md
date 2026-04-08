# Overview Data Collectors

Python-based data collection modules for the overview skill (replaces Bash scripts per ADR-003).

## Overview

This package contains 5 collector modules that gather project data:

| Module | Replaces | Lines | Purpose |
|--------|----------|-------|---------|
| **git_collector** | collect-git.sh | 41 | Git status, commits, changes |
| **project_collector** | collect-project-info.sh | 220 | Project metadata, files, tech stack |
| **work_collector** | collect-work.sh | 48 | Active plans, tasks, issues |
| **framework_collector** | collect-framework.sh | 64 | Framework config, Pillars, rules |
| **pattern_detector** | detect-patterns.sh | 37 | Detected patterns (architecture, testing) |

## Architecture

**Key Design Principles:**
- Return structured dicts (not string output)
- Type hints on all functions
- Comprehensive docstrings
- Error handling with graceful fallbacks
- Leverage shared utilities from `_scripts/`

**Module Structure:**
```
collectors/
├── __init__.py              # Base interface, collect_all()
├── git_collector.py         # Git data collection
├── project_collector.py     # Project metadata
├── work_collector.py        # Active work status
├── framework_collector.py   # Framework configuration
├── pattern_detector.py      # Pattern detection
└── README.md                # This file
```

## Usage

### Individual Collectors

```python
from collectors import git_collector

# Collect git status
git_data = git_collector.collect_git_status()
print(f"Branch: {git_data['branch']}")
print(f"Staged files: {git_data['staged']}")

# Collect recent commits
commits = git_collector.collect_recent_commits()
for commit in commits:
    print(f"{commit['hash']}: {commit['message']}")
```

### All Collectors at Once

```python
from collectors import collect_all

data = collect_all()
print(f"Git branch: {data['git']['branch']}")
print(f"Pillar count: {data['framework']['pillarCount']}")
print(f"Active plans: {len(data['work']['activePlans'])}")
print(f"Patterns: {', '.join(data['patterns'])}")
```

### JSON Output

```python
import json
from collectors import collect_all

data = collect_all()
print(json.dumps(data, indent=2))
```

## Return Structures

### git_collector.collect_git_status()

```python
{
    "branch": "main",
    "commit": "abc123",
    "commitMessage": "feat: add feature X",
    "staged": 2,
    "unstaged": 1,
    "untracked": 0
}
```

### project_collector.collect_project_info()

```python
{
    "description": "AI-assisted development framework",
    "coreConcept": "Universal framework for Claude Code",
    "initialized": "2026-02-26",
    "techStack": {
        "frontend": "React + TypeScript",
        "backend": "Node.js + Lambda",
        "auth": "AWS Cognito",
        "iac": "AWS CDK"
    },
    "documentation": ["CLAUDE.md", "README.md"],
    "fileStats": {
        "typescript": 42,
        "javascript": 8,
        "python": 15
    }
}
```

### work_collector.collect_work_info()

```python
{
    "activePlans": [
        {"file": "issue-85-plan.md", "title": "Migrate collectors"}
    ],
    "tasks": {
        "pending": 5,
        "inProgress": 2,
        "completed": 12
    },
    "currentIssue": {
        "number": 85,
        "title": "Migrate overview data collection"
    }
}
```

### framework_collector.collect_framework_info()

```python
{
    "profile": "react-aws",
    "pillars": ["A", "B", "K", "L", "M", "Q", "R"],
    "pillarCount": 7,
    "ruleCount": 42,
    "commandCount": 18
}
```

### pattern_detector.detect_patterns()

```python
[
    "Clean Architecture",
    "Jest Testing",
    "Zustand State Management",
    "AWS CDK Infrastructure"
]
```

## Error Handling

All collectors handle errors gracefully:

**No git repository:**
```python
git_data = git_collector.collect_git_status()
# Returns: {"branch": "unknown", "commit": "N/A", ...}
```

**No framework installed:**
```python
framework_data = framework_collector.collect_framework_info()
# Returns: {"profile": "Not installed", "pillars": [], ...}
```

**No active plans:**
```python
work_data = work_collector.collect_work_info()
# Returns: {"activePlans": [], "tasks": {...}, ...}
```

## Integration with Overview Skill

The collectors are called by `overview.sh`:

```bash
# Old way (Bash)
source modules/collect-git.sh
git_data=$(collect_git_status)

# New way (Python)
git_data=$(uv run collectors/git_collector.py)
```

Or directly from Python:

```python
#!/usr/bin/env python3
import json
from collectors import collect_all

if __name__ == '__main__':
    data = collect_all()
    print(json.dumps(data, indent=2))
```

## Testing

Unit tests for each collector:

```bash
cd .claude/skills/overview/script/collectors
pytest tests/
```

## References

- [ADR-003: Python-Only Policy](../../../../../docs/ADRs/003-python-only-for-skill-scripts.md)
- [Issue #85: Phase 3 - Migrate collectors](https://github.com/aifuun/ai-dev/issues/85)
- [Shared Utilities](../../../_scripts/README.md)

---

**Version**: 1.0.0
**Created**: 2026-03-09
**Part of**: Issue #85 (Phase 3 of Bash-to-Python migration)
