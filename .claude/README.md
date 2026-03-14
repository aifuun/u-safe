# Claude Code Workflow System

> Complete workflow system for AI-assisted development with Claude Code

## Overview

This directory contains:
- **Commands** (18): Workflow automation commands (`*resume`, `*issue pick`, `*plan`, etc.)
- **Rules** (40): Technical standards organized by category
- **Workflow** (13): Planning and development guides
- **Templates** (5): Planning templates (MVP, feature, issue, etc.)

## Quick Start

### 1. Copy to Your Project

```bash
cp -r .claude/ your-project/.claude/
```

### 2. Customize

- Update `MEMORY.md` with project decisions
- Configure `settings.json` permissions
- Enable relevant rules for your tech stack

### 3. Start Working

```
*resume         # Resume last work session
*status         # Check current status
*issue pick 1   # Pick issue #1 to work on
*next           # Get next task
```

## 🔄 Workflow System

### Entry Points
- **Start here**: [WORKFLOW.md](./WORKFLOW.md) - Quick navigation guide
- **Complete guide**: [workflow/MAIN.md](./workflow/MAIN.md) - Master workflow overview

### 4-Phase System

The framework uses a **4-Phase workflow** with **3-Layer planning**:

| Phase | Document | Purpose |
|-------|----------|---------|
| **A** | [Phase-A-Documentation.md](./workflow/Phase-A-Documentation.md) | Define what to build |
| **B** | [Phase-B-Planning.md](./workflow/Phase-B-Planning.md) | Plan how to build (Two-Step) |
| **C** | [Phase-C-Development.md](./workflow/Phase-C-Development.md) | Build it |
| **D** | [Phase-D-Release.md](./workflow/Phase-D-Release.md) | Ship it |

### 3-Layer Planning

```
Strategy Layer  → MVP Planning (40 min)         → GitHub Issues
Campaign Layer  → Issue Breakdown (1-2h/feature) → Dev Plans
Tactics Layer   → Active Tracking (real-time)   → plans/active/
```

See [workflow/](./workflow/) directory for detailed guides.

## Command System

All commands are in `commands/` directory.

### Session Management

| Command | Purpose |
|---------|---------|
| `*resume` | Resume last work session with context |
| `*status` | Show current work status and progress |

### Issue & Task Management

| Command | Purpose |
|---------|---------|
| `*issue pick <n>` | Pick issue #n from GitHub/project |
| `*issue close <n>` | Close issue #n |
| `*issue create <title>` | Create new issue |
| `*next` | Get next task from current plan |

### Planning

| Command | Purpose |
|---------|---------|
| `*plan` | Create feature plan from requirements |
| `*tier` | Classify feature tier (T1/T2/T3) |

### Development

| Command | Purpose |
|---------|---------|
| `*scaffold` | Generate code from templates |
| `*explain` | Explain code/pattern |
| `*tidy` | Clean up code formatting |

### Quality Assurance

| Command | Purpose |
|---------|---------|
| `*review` | Code review current changes |
| `*validate` | Framework validation (schemas, profiles, metadata) |
| `*lint-pillars` | Check Pillar compliance with AI_DEV_PROT v15 |
| `*check-naming` | Validate naming conventions and config |
| `*audit` | Run compliance audit (use `*lint-pillars` for new work) |
| `*pillar` | Check pillar compliance |

### Deployment

| Command | Purpose |
|---------|---------|
| `*cdk` | CDK deployment commands |
| `*release` | Release workflow |
| `*hotfix` | Hotfix workflow |
| `*bugfix` | Bug fix workflow |

### Workflow

| Command | Purpose |
|---------|---------|
| `*sync` | Sync with remote/design docs |
| `*approve` | Approve and merge PR |

See `commands/` directory for detailed documentation of each command.

## Rule System

Rules are organized by category in `rules/` directory.

### Core (7 rules)

Essential workflow and development rules:

| Rule | Purpose |
|------|---------|
| `workflow.md` | Core workflow principles |
| `naming.md` | Naming conventions |
| `debugging.md` | Debugging techniques |
| `docs.md` | Documentation standards |
| `memory-management.md` | Memory management |
| `memory-protection.md` | Memory protection |
| `planning-context.md` | Planning context rules |

### Architecture (7 rules)

Clean Architecture implementation:

| Rule | Purpose | ADR |
|------|---------|-----|
| `clean-architecture.md` | Clean Architecture principles | ADR-006 |
| `dependency-rule.md` | Dependency Inversion Principle | ADR-006 |
| `layer-boundaries.md` | Boundary enforcement | ADR-006 |
| `adapters.md` | Adapter pattern | - |
| `headless.md` | Logic-UI separation (Pillar L) | - |
| `identity.md` | Identity management | - |
| `service-layer.md` | Service layer pattern | - |

**New projects**: Enable `clean-architecture.md`, `dependency-rule.md`, `layer-boundaries.md`

### Languages (3 rules)

TypeScript-specific rules:

| Rule | Purpose | ADR |
|------|---------|-----|
| `typescript-strict.md` | Strict mode configuration | ADR-008 |
| `typescript-nominal-types.md` | Branded types (Pillar A) | ADR-008 |
| `typescript-esm.md` | ESM module patterns | ADR-008 |

**New TypeScript projects**: Enable all 3 rules

### Frontend (6 rules)

React/UI development:

| Rule | Purpose |
|------|---------|
| `design-system.md` | Design system integration |
| `css.md` | CSS/styling rules |
| `debug-panel.md` | Debug panel implementation |
| `views.md` | View component rules |
| `stores.md` | State store patterns |
| `zustand-hooks.md` | Zustand state management |

**New React projects**: Enable `design-system.md`, `views.md`, `zustand-hooks.md`

### Backend (5 rules)

Server-side development:

| Rule | Purpose |
|------|---------|
| `saga.md` | Saga pattern (Pillar M) |
| `lambda-local-first.md` | Local Lambda development |
| `lambda-typescript-esm.md` | Lambda ESM patterns |
| `query-transactions.md` | Query/transaction patterns |
| `external-api-integrations.md` | External API integration |

**New Lambda projects**: Enable `lambda-typescript-esm.md`, `saga.md`

### Infrastructure (10 rules)

AWS and deployment:

| Rule | Purpose | ADR |
|------|---------|-----|
| `aws-services.md` | AWS patterns (DynamoDB, S3, SQS, Lambda) | ADR-007 |
| `cdk-deploy.md` | CDK deployment | ADR-007 |
| `cdk-watch-testing.md` | CDK watch mode | ADR-007 |
| `lambda-layer-deployment.md` | Lambda layer deployment | - |
| `lambda-quick-reference.md` | Lambda quick reference | - |
| `tauri-stack.md` | Tauri stack patterns | - |
| `secrets.md` | Secret management | - |
| `diagnostic-export-logging.md` | Diagnostic logging | - |
| `time-handling.md` | Time handling | - |
| `url-construction.md` | URL construction | - |

**New AWS projects**: Enable `aws-services.md`, `cdk-deploy.md`

### Development (2 rules)

Development best practices:

| Rule | Purpose |
|------|---------|
| `file-creation.md` | File creation rules |
| `infinite-loop-prevention.md` | Loop prevention |

## Workflow Guides

Comprehensive guides in `workflow/` directory.

### Planning

| Guide | Purpose |
|-------|---------|
| `MAIN.md#strategy-layer-mvp-planning-40-minutes` | MVP planning (Strategy Layer) |
| `MAIN.md#campaign-layer-feature-planning-1-2-hours-per-feature` | Feature planning (Campaign Layer) |

### Development

| Guide | Purpose |
|-------|---------|
| `Phase-C-Development.md` | Development workflow |
| `feature-development.md` | Feature development guide |
| `branch-strategy.md` | Git branching strategy |

### Architecture

| Guide | Purpose |
|-------|---------|
| `architecture-core.md` | Core architecture principles |

### Other

| Guide | Purpose |
|-------|---------|
| `Phase-D-Release.md` | Release workflow |
| `Phase-A-Documentation.md` | Documentation workflow |
| `quick-reference.md` | Quick reference |
| `ISSUE_COMPLETION_CHECKLIST.md` | Issue completion checklist |

## Templates

Planning templates in `workflow/templates/`.

### 1. TEMPLATE-mvp.md
**Use for**: MVP planning at Strategy Layer
**Purpose**: Define product goals, user stories, success metrics

### 2. TEMPLATE-feature-plan.md
**Use for**: Feature implementation at Tactics Layer
**Purpose**: Technical implementation details, tier classification, dependencies

### 3. TEMPLATE-github-issue.md
**Use for**: Creating GitHub issues at Campaign Layer
**Purpose**: Task breakdown, acceptance criteria, priority

### 4. TEMPLATE-issue-triage.md
**Use for**: Triaging incoming issues
**Purpose**: Quick classification and priority assignment

### 5. TEMPLATE-todo.md
**Use for**: Quick task tracking
**Purpose**: Simple TODO list for current work

## 3-Layer Planning Architecture

```
Strategy Layer (40 minutes)
  ↓ TEMPLATE-mvp.md
  → Product goals, user stories, success metrics

Campaign Layer (1-2 hours)
  ↓ TEMPLATE-github-issue.md
  → Task breakdown, GitHub issues, milestones

Tactics Layer (Real-time)
  ↓ TEMPLATE-feature-plan.md
  → Implementation details, code structure, dependencies

Code Layer (Continuous)
  → TypeScript/Python/Go implementation
```

## Settings Configuration

### settings.json

Configure permissions and project type:

```json
{
  "template": "react",  // or "tauri", "node", "lambda"
  "version": "1.0.0",
  "created_at": "2025-02-05T00:00:00Z",
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": [
      "Bash",
      "Edit(/src/**/*)",
      "Edit(/infra/**/*)",
      "Edit(/docs/**/*)",
      "Edit(/.claude/**/*)",
      "Edit(/CLAUDE.md)"
    ],
    "deny": [
      "Read(.env)",
      "Read(.env.local)",
      "Read(.env.*.local)"
    ]
  }
}
```

## Tech Stack Enablement

### React + TypeScript Frontend

**Enable rules**:
- Core: `workflow.md`, `naming.md`, `debugging.md`
- Architecture: `clean-architecture.md`, `dependency-rule.md`, `headless.md`
- Languages: `typescript-strict.md`, `typescript-nominal-types.md`, `typescript-esm.md`
- Frontend: `design-system.md`, `views.md`, `zustand-hooks.md`

**Commands**: `*resume`, `*status`, `*issue`, `*plan`, `*review`

### Node.js + AWS Lambda Backend

**Enable rules**:
- Core: `workflow.md`, `naming.md`, `debugging.md`
- Architecture: `clean-architecture.md`, `dependency-rule.md`, `adapters.md`
- Languages: `typescript-strict.md`, `typescript-nominal-types.md`, `typescript-esm.md`
- Backend: `lambda-typescript-esm.md`, `saga.md`
- Infrastructure: `aws-services.md`, `cdk-deploy.md`

**Commands**: `*resume`, `*issue`, `*cdk`, `*release`

### Tauri + React Desktop App

**Enable rules**:
- Core: `workflow.md`, `naming.md`, `debugging.md`
- Architecture: `clean-architecture.md`, `dependency-rule.md`, `headless.md`, `service-layer.md`
- Languages: `typescript-strict.md`, `typescript-nominal-types.md`, `typescript-esm.md`
- Frontend: `design-system.md`, `views.md`, `zustand-hooks.md`
- Infrastructure: `tauri-stack.md`

**Commands**: `*resume`, `*issue`, `*plan`, `*review`

### Full-Stack (React + Lambda)

**Enable all rules** from both frontend and backend.

## File Structure

```
.claude/
├── commands/                       # 18 command files
├── rules/
│   ├── core/                       # 7 files
│   ├── architecture/               # 7 files (4 existing + 3 new)
│   ├── languages/                  # 3 files (new)
│   ├── frontend/                   # 6 files
│   ├── backend/                    # 5 files
│   ├── infrastructure/             # 10 files (9 existing + 1 new)
│   └── development/                # 2 files
├── workflow/                       # 13 files + templates/
├── plans/                          # active/, archive/, backlog/
├── MEMORY.md                       # Long-term project decisions
├── WORKFLOW.md                     # Workflow overview
├── README.md                       # This file
└── settings.json                   # Permissions and config
```

## Integration with .prot/

This workflow system works with AI_DEV_PROT v15 coding standards:

**.claude/** (workflow) + **.prot/** (standards) = **Complete AI Dev Framework**

- `.claude/` - How to work (commands, workflow)
- `.prot/` - How to code (18 Pillars, checklists)

Example workflow:
1. `*issue pick 3` - Pick issue
2. `*tier` - Classify as T2 (needs headless + adapters)
3. Read `.prot/pillar-l/headless.md` - Learn headless pattern
4. `*plan` - Create feature plan using TEMPLATE-feature-plan.md
5. Implement following `.prot/` pillars
6. `*review` - Code review
7. `*pillar L` - Check Pillar L compliance
8. `*issue close 3` - Close issue

## Related Documentation

### Framework Navigation
- **[Root README](../../README.md)** - Project overview and quick start
- **Pillars System** - AI_DEV_PROT v15 coding standards
- **[Profile System](../profiles/README.md)** - Tech stack configurations

### Implementation Guides
- **CLAUDE.md** - Project overview for AI assistants
- **[WORKFLOW.md](./WORKFLOW.md)** - Quick navigation guide
- **[workflow/MAIN.md](./workflow/MAIN.md)** - Complete workflow reference
- **[workflow/Phase-C-Development.md](./workflow/Phase-C-Development.md)** - Development process

### Reference Materials
- **FRAMEWORK_DESIGN.md** - Framework architecture decisions
- **workflow/quick-reference.md** - Quick command reference
- **rules/INDEX.md** - Complete rules catalog

---

**Framework**: AI_DEV v1.0
**License**: MIT
