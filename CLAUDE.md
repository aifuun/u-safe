# AI Development Framework

> Universal AI-assisted development framework for Claude Code integration. Combines 18 coding pillars, 20+ workflow commands, 40+ technical rules, and intelligent template system.

## 🎯 What Is This Project?

**This is a framework template library** - not an application you run directly.

Think of it as **coding standards library + workflow system** that you install into your projects:

```
ai-dev/ (THIS REPO)              Your Projects
├── Pillars (18)                 ├── .claude/  ← Installed from framework
├── Rules (40+)        [COPY] →  ├── .prot/    ← Installed from framework
├── Commands (20+)               └── src/      ← Your code
├── Profiles (3)
└── Init Script
```

### Two Ways to Use This

| Role | You Work | Purpose |
|------|----------|---------|
| **Framework Developer** | IN this repo | Maintain/extend Pillars, Rules, Commands |
| **Framework User** | WITH this repo | Initialize new projects using framework |

### Quick Start

**Initialize a new project:**
```bash
# Minimal project (Pillars A, B, K)
./scripts/init-project.sh --profile=minimal --name=my-library

# Backend project (Pillars A, B, K, M, Q, R)
./scripts/init-project.sh --profile=node-lambda --name=my-api

# Full-stack project (All 7 Pillars)
./scripts/init-project.sh --profile=react-aws --name=my-app
```

**Or copy manually:**
```bash
cp -r framework/.claude-template/ your-project/.claude/
cp -r framework/.prot-template/ your-project/.prot/
```

### What This Framework Solves

**Problem**: Every project starts from scratch with inconsistent patterns and repeated mistakes.

**Solution**:
- ✅ Reusable coding patterns (18 Pillars)
- ✅ Automated workflows (20+ Commands)
- ✅ Quick reference guides (40+ Rules)
- ✅ Tech-stack presets (Profiles)
- ✅ One-command initialization

---

## 📊 Current Status

| Component | Status | Details |
|-----------|--------|---------|
| **Pillars (18)** | 🔄 P0 | Architecture extraction in progress |
| **Commands (18)** | ✅ Complete | Ready for use in `.claude-template/commands/` |
| **Skills (13)** | ✅ Complete | Issue lifecycle, framework sync, ADR management |
| **Rules (40+)** | ✅ Complete | Organized by category, fully documented |
| **Profiles (3)** | ✅ Complete | minimal, node-lambda, react-aws |
| **Init Script** | ✅ Complete | `scripts/init-project.sh` works perfectly |

## 🚀 How to Use This Framework

### Option 1: Initialize New Project (Recommended)

```bash
# Minimal project - Pillars A, B, K (learning/POC)
./scripts/init-project.sh --profile=minimal --name=my-library

# Node Lambda - Pillars A, B, K, M, Q, R (backend/API)
./scripts/init-project.sh --profile=node-lambda --name=my-api

# React AWS - All 7 Pillars (full-stack)
./scripts/init-project.sh --profile=react-aws --name=my-app
```

**What happens**:
1. Creates project directory structure
2. Installs `.claude/` (commands + rules)
3. Installs `.prot/` (pillar documentation)
4. Creates `package.json`, `tsconfig.json`, etc.
5. Marks installation in `.framework-install`

### Option 2: Manual Copy (Existing Projects)

```bash
cd your-existing-project
cp -r /path/to/ai-dev/framework/.claude-template .claude
cp -r /path/to/ai-dev/framework/.prot-template .prot
```

Then selectively enable rules based on your tech stack.

### Option 3: Explore Framework First

```bash
# Browse Pillars (coding standards)
ls framework/.prot-template/pillars/

# Browse Rules (quick reference)
ls framework/.claude-template/rules/

# Browse Commands (workflow automation)
ls framework/.claude-template/commands/

# Check available profiles
ls framework/profiles/
```

---

## 📁 Repository Structure

```
ai-dev/
├── framework/                    # Framework Source Files
│   ├── .claude-template/         # → Installed to .claude/
│   │   ├── commands/             # 20+ workflow commands
│   │   ├── rules/                # 40+ technical rules
│   │   ├── skills/               # Custom workflow automation (optional)
│   │   └── workflow/             # Planning templates
│   ├── .prot-template/           # → Installed to .prot/
│   │   └── pillars/              # 18 coding standards
│   ├── profiles/                 # Tech-stack presets
│   │   ├── minimal.json          # Beginner (3 Pillars)
│   │   ├── node-lambda.json      # Backend (6 Pillars)
│   │   └── react-aws.json        # Full-stack (7 Pillars)
│   └── schemas/                  # JSON Schema definitions
│
├── scripts/                      # Automation Scripts
│   └── init-project.sh           # ✅ Project initialization (chosen approach)
│
├── examples/                     # Complete Runnable Examples
│   ├── minimal-example/          # Beginner: 3 Pillars (A, B, K)
│   │   ├── src/                  # User management library
│   │   ├── tests/                # 24 passing tests
│   │   └── docs/EXAMPLE.md       # Pattern explanation
│   ├── node-lambda-example/      # Intermediate: 6 Pillars (Backend)
│   │   ├── src/patterns/         # Saga, idempotency
│   │   └── tests/                # Integration tests
│   └── react-aws-example/        # Advanced: 7 Pillars (Full-stack)
│       ├── packages/frontend/    # React + Zustand
│       ├── packages/backend/     # Lambda + API Gateway
│       └── infrastructure/       # AWS CDK
│
├── cli/                          # CLI Tool (Optional)
│   └── src/                      # 📋 Not necessary (script works well)
│
├── CLAUDE.md                     # This file
└── README.md                     # Project documentation
```

## 🏗️ Core Architecture (Two-Tier System)

### Layer 1: Pillars (18 files, 200-300 lines each)
**Purpose**: Deep knowledge, single source of truth

| Quadrant | Pillars | Purpose |
|----------|---------|---------|
| **Q1: Data Integrity** | A, B, C, D | Nominal typing, schema-first, mocking, FSM |
| **Q2: Flow & Concurrency** | E, F, Q | Orchestration, optimistic locking, idempotency |
| **Q3: Structure & Boundaries** | G, H, I, J, K, L | Traceability, policy, firewalls, locality, testing, headless |
| **Q4: Resilience & Observability** | M, N, O, P, R | Saga, context, async, circuit breaker, logging |

👉 **Location**: [framework/.prot-template/](framework/.prot-template/)

### Layer 2: Rules (40+ files, 20-70 lines each)
**Purpose**: Quick reference, copy-paste patterns

| Category | Count | Examples |
|----------|-------|----------|
| **Core** | 7 | workflow, naming, debugging, docs |
| **Architecture** | 7 | clean-architecture, dependency-rules, layer-boundaries |
| **Languages** | 3 | typescript, python, go |
| **Frontend** | 6 | react, design-system, state-management |
| **Backend** | 5 | lambda, saga, api-design |
| **Infrastructure** | 10 | aws-cdk, secrets, monitoring |
| **Development** | 2 | performance, security |

👉 **Location**: [framework/.claude-template/rules/](framework/.claude-template/rules/)

---

## ⚡ Commands System (20+ Commands)

| Category | Commands | Purpose |
|----------|----------|---------|
| **Session** | `*resume`, `*status` | Manage work sessions |
| **Planning** | `*plan`, `*tier`, `*next` | Create and execute plans |
| **Issues** | `*issue pick`, `*issue create`, `*issue close` | GitHub issue management |
| **Development** | `*scaffold`, `*explain`, `*tidy` | Code generation and cleanup |
| **Quality** | `*review`, `*audit`, `*pillar` | Code review and validation |
| **Deployment** | `*cdk`, `*release`, `*hotfix`, `*bugfix` | Cloud deployment |
| **Workflow** | `*sync`, `*approve` | Git and PR management |

👉 **Full list**: [framework/.claude-template/commands/](framework/.claude-template/commands/)

---

## 🎨 Skills System (Custom Workflows)

Skills extend the framework with project-specific automation. This project uses 13 custom skills for issue lifecycle, framework management, and workflow automation.

### 🔥 High Frequency Skills (Daily Use)

| Skill | Purpose | Usage |
|-------|---------|-------|
| **next** | Get next task from active plan | `/next` |
| **adr** | Create Architecture Decision Records | `/adr create "title"` |
| **overview** | Project status and metrics | `/overview` |
| **sync** | Sync branch with main | `/sync` |

### 📅 Issue Lifecycle Management

| Skill | Purpose | Usage |
|-------|---------|-------|
| **start-issue** | Begin work on GitHub issue | `/start-issue #23` |
| **finish-issue** | Complete issue workflow | `/finish-issue #23` |

**Complete workflow**:
```bash
/start-issue #23    # → Create branch, generate plan, setup env
/next               # → Get first task from plan
# ... implement feature ...
/sync               # → Sync with main branch
/finish-issue #23   # → Commit, PR, merge, close issue
```

### 🔧 Framework Management

| Skill | Purpose | Usage |
|-------|---------|-------|
| **update-framework** | Sync all framework components | `/update-framework --from <path>` |
| **update-pillars** | Sync Pillars only | `/update-pillars --from <path>` |
| **update-rules** | Sync Rules only | `/update-rules --from <path>` |
| **update-workflow** | Sync Workflow only | `/update-workflow --from <path>` |
| **update-skills** | Sync Skills only | `/update-skills --from <path>` |

**Example - One-command framework update**:
```bash
# Update entire framework from ai-dev repo
/update-framework --from ~/dev/ai-dev

# Or selective updates
/update-pillars --from ~/dev/ai-dev --pillars A,B,K
/update-rules --from ~/dev/ai-dev --categories core,architecture
```

### 🛠️ Skill Development

| Skill | Purpose | Usage |
|-------|---------|-------|
| **skill-creator** | Create and optimize skills | `/skill-creator` |

**Features**:
- Create new skills from templates
- Modify existing skills
- Run performance evaluations
- Optimize skill triggers

### Skills vs Commands

| Aspect | Commands | Skills |
|--------|----------|--------|
| **Location** | `.claude-template/commands/` | `.claude/skills/` |
| **Scope** | Framework-wide, generic | Project-specific |
| **Customization** | Template-based | Fully customizable |
| **Invocation** | `*command-name` | `/skill-name` |
| **Examples** | `*plan`, `*review` | `/start-issue`, `/adr` |

👉 **Skills location**: `.claude/skills/`
👉 **Skills documentation**: `.claude/skills/README.md`

---

```
Strategy Layer (40 min)   → MVP Planning
    ↓ Link
Campaign Layer (1-2h)    → GitHub Issues
    ↓ Link
Tactics Layer (Real-time)→ Issue Plans + Commands
    ↓ Execute
Code Layer               → Implementation
```

👉 **Detailed workflow**: [framework/.claude-template/workflow/MAIN.md](framework/.claude-template/workflow/MAIN.md)

---

## 🎯 Project Status & Roadmap

**Current**: Phase 2 Verification Complete ✅

For issue tracking and planning:
- 🔗 **[GitHub Issues](https://github.com/aifuun/ai-dev/issues)** - Active issue tracking and project management
- 📋 **[Issue #37](https://github.com/aifuun/ai-dev/issues/37)** - Overall project cleanup (umbrella issue)

**Phases**:
- ✅ **Phase 1** (P0): Architecture, Pillars, Commands, Rules, Workflow - Complete
- ✅ **Phase 2** (P1): Profiles, Init Script - Complete
- 📋 **Phase 3** (P2): CLI Tool - Optional (init script is sufficient)

---

## 📚 Directory Structure

```
framework/
├── .claude-template/              # Claude Code workflow templates
│   ├── commands/                  # 20+ workflow commands
│   ├── rules/                     # 40+ technical rules (by category)
│   ├── skills/                    # Custom workflow automation (13 skills)
│   │   ├── start-issue/           # Issue lifecycle: start
│   │   ├── finish-issue/          # Issue lifecycle: complete
│   │   ├── next/                  # Task navigation
│   │   ├── adr/                   # Architecture Decision Records
│   │   ├── sync/                  # Branch synchronization
│   │   ├── overview/              # Project status
│   │   ├── update-framework/      # Framework sync (meta-skill)
│   │   ├── update-pillars/        # Pillars sync
│   │   ├── update-rules/          # Rules sync
│   │   ├── update-workflow/       # Workflow sync
│   │   ├── update-skills/         # Skills sync
│   │   ├── skill-creator/         # Skill development tool
│   │   └── README.md              # Skills documentation
│   ├── workflow/                  # Planning and execution guides
│   ├── WORKFLOW.md                # Quick start entry point
│   └── README.md                  # Full documentation
│
├── .prot-template/                # 18 Pillars (coding standards)
│   ├── pillar-A.md through pillar-R.md
│   └── README.md
│
├── profiles/                      # Tech-stack presets (P1)
│   ├── minimal.json
│   ├── react-aws.json
│   └── python-fastapi.json
│
└── schemas/                       # JSON Schema definitions
    ├── metadata.schema.json
    ├── profile.schema.json
    └── metadata.types.ts
```

---

## 📖 Key Documentation

| Document | Purpose | Link |
|----------|---------|------|
| **WORKFLOW.md** | Entry point for Claude Code | [framework/.claude-template/WORKFLOW.md](framework/.claude-template/WORKFLOW.md) |
| **Commands Guide** | All 20+ commands documented | [framework/.claude-template/commands/](framework/.claude-template/commands/) |
| **Skills Guide** | 13 custom skills for workflow automation | [.claude/skills/README.md](.claude/skills/README.md) |
| **Rules Index** | 40+ rules organized by category | [framework/.claude-template/rules/](framework/.claude-template/rules/) |
| **Pillars Guide** | 18 deep-dive standards | [framework/.prot-template/](framework/.prot-template/) |
| **Profiles** | Smart template presets | [framework/profiles/README.md](framework/profiles/README.md) |
| **Architecture** | Complete system design | [FRAMEWORK_DESIGN.md](FRAMEWORK_DESIGN.md) |

---

## 💡 Common Use Cases

### Use Case 1: Starting a New Project

**Choose profile based on tech stack:**

```bash
# Building a library or learning framework basics
./scripts/init-project.sh --profile=minimal --name=my-library
# → Pillars: A (Types), B (Validation), K (Testing)

# Building a serverless API
./scripts/init-project.sh --profile=node-lambda --name=my-api
# → Pillars: A, B, K + M (Saga), Q (Idempotency), R (Logs)

# Building a full-stack web app
./scripts/init-project.sh --profile=react-aws --name=my-app
# → Pillars: All 7 (A, B, K, L, M, Q, R)
```

### Use Case 2: Adding Framework to Existing Project

```bash
# Copy framework files
cd your-existing-project
cp -r /path/to/ai-dev/framework/.claude-template .claude
cp -r /path/to/ai-dev/framework/.prot-template .prot

# Selectively enable rules for your stack
# Edit: .claude/rules/ - keep only relevant rules
```

### Use Case 3: Learning Best Practices

```bash
# Study coding patterns (deep dive)
cat framework/.prot-template/pillars/q1-data-integrity/pillar-a/nominal-typing.md
cat framework/.prot-template/pillars/q4-resilience-observability/pillar-m/saga.md

# Quick reference during coding
cat framework/.claude-template/rules/languages/typescript-nominal-types.md
cat framework/.claude-template/rules/backend/saga.md
```

### Use Case 4: Contributing to Framework

```bash
# Add new patterns
vim framework/.prot-template/pillars/new-pattern.md

# Add quick reference rules
vim framework/.claude-template/rules/category/new-rule.md

# Create profiles for new tech stacks
vim framework/profiles/python-fastapi.json
```

### Use Case 5: Daily Development with Skills

```bash
# Start your day - check project status
/overview

# Pick up work from GitHub
/start-issue #42
# → Creates branch: feature/42-add-auth
# → Generates implementation plan
# → Sets up environment

# Get next task from plan
/next
# → Shows: "Task #1: Install OAuth packages"

# Work on the task...
# Periodically sync with main
/sync

# Record architectural decisions
/adr create "Use OAuth 2.0 with PKCE flow"

# When done, complete the issue
/finish-issue #42
# → Commits changes
# → Creates PR
# → Merges to main
# → Closes issue
```

### Use Case 6: Cross-Project Framework Management

```bash
# Working on multiple projects using the framework
# Keep them all in sync with one command

# Update project A from framework source
cd ~/projects/project-a
/update-framework --from ~/dev/ai-dev

# Update project B (selective sync)
cd ~/projects/project-b
/update-pillars --from ~/dev/ai-dev --pillars A,B,K
/update-rules --from ~/dev/ai-dev --categories core,architecture

# Push framework improvements back to source
cd ~/dev/ai-dev
/update-framework --to ~/projects/project-a
```

---

## 🔗 Related Documents

- **[FRAMEWORK_DESIGN.md](./FRAMEWORK_DESIGN.md)** - Detailed system design
- **[PROJECT_ARCHITECTURE_USAGE_GUIDE.md](./PROJECT_ARCHITECTURE_USAGE_GUIDE.md)** - Usage walkthrough
- **[Issues #18-23](https://github.com/aifuun/ai-dev/issues?q=is%3Aissue+label%3AP0)** - Smart template implementation

---

## 📋 Architecture Decision Records (ADRs)

**Official ADR Location**: `docs/ADRs/`

All Architecture Decision Records (ADRs) for this project are stored in the single canonical location:

```bash
docs/ADRs/
```

**Important Notes**:
- ✅ This is the **ONLY** location for ADRs in this project
- ❌ Do NOT create ADR directories elsewhere
- 📝 Use `/adr` skill (in legacy) for ADR management if needed
- 🔗 ADRs document important architectural decisions and rationale

### Current ADRs

| # | Title | Status | Summary |
|---|-------|--------|---------|
| [001](docs/ADRs/001-official-skill-patterns.md) | Official Skill Patterns | ✅ Accepted | Skill structure standards from Anthropic patterns |
| [002](docs/ADRs/002-skill-creation-workflow.md) | Skill Creation Workflow | ✅ Accepted | Use `/skill-creator` + simplified testing |

**Full Index**: [docs/ADRs/README.md](docs/ADRs/README.md)
