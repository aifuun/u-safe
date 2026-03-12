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
python3 scripts/init-project.py --profile=minimal --name=my-library

# Backend project (Pillars A, B, K, M, Q, R)
python3 scripts/init-project.py --profile=node-lambda --name=my-api

# Full-stack project (All 7 Pillars)
python3 scripts/init-project.py --profile=react-aws --name=my-app
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
| **Rules (40+)** | ✅ Complete | Organized by category, fully documented |
| **Profiles (3)** | ✅ Complete | minimal, node-lambda, react-aws |
| **Init Script** | ✅ Complete | `scripts/init-project.py` (Python) |
| **Evaluation System** | ✅ Phase 1 | 8 test cases, Anthropic-compliant format |

## 🚀 How to Use This Framework

### Option 1: Initialize New Project (Recommended)

```bash
# Minimal project - Pillars A, B, K (learning/POC)
python3 scripts/init-project.py --profile=minimal --name=my-library

# Node Lambda - Pillars A, B, K, M, Q, R (backend/API)
python3 scripts/init-project.py --profile=node-lambda --name=my-api

# React AWS - All 7 Pillars (full-stack)
python3 scripts/init-project.py --profile=react-aws --name=my-app
```

**What happens**:
1. Creates project directory structure
2. Installs `.claude/` (commands + rules)
3. Installs `.prot/` (pillar documentation)
4. Creates `package.json`, `tsconfig.json`, etc.
5. Marks installation in `.framework-install`
6. **Configures permissions for work-issue auto mode** (skip with `--no-configure-permissions`)

**Permission Configuration:**

The `--configure-permissions` flag (enabled by default) sets up `.claude/settings.json` with required permissions for seamless work-issue auto mode execution:

- ✅ All git operations (add, commit, push, checkout, branch, fetch, merge, worktree)
- ✅ GitHub CLI operations (gh issue, gh pr)
- ✅ Profile-specific operations (npm test/lint/build for Node.js, pytest for Python)

**Result:** `work-issue --auto` runs without permission prompts.

**Manual configuration** (for existing projects):
```bash
# Configure current project
/configure-permissions

# Configure target project
/configure-permissions ../u-safe

# Preview changes
/configure-permissions --dry-run
```

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
| **Rules Index** | 40+ rules organized by category | [framework/.claude-template/rules/](framework/.claude-template/rules/) |
| **Pillars Guide** | 18 deep-dive standards | [framework/.prot-template/](framework/.prot-template/) |
| **Profiles** | Smart template presets | [framework/profiles/README.md](framework/profiles/README.md) |
| **Evaluation System** | Skill quality assurance | [.claude/skills/.evals/README.md](.claude/skills/.evals/README.md) |
| **Architecture** | Complete system design | [FRAMEWORK_DESIGN.md](FRAMEWORK_DESIGN.md) |

---

## 💡 Common Use Cases

### Use Case 1: Starting a New Project

**Choose profile based on tech stack:**

```bash
# Building a library or learning framework basics
python3 scripts/init-project.py --profile=minimal --name=my-library
# → Pillars: A (Types), B (Validation), K (Testing)

# Building a serverless API
python3 scripts/init-project.py --profile=node-lambda --name=my-api
# → Pillars: A, B, K + M (Saga), Q (Idempotency), R (Logs)

# Building a full-stack web app
python3 scripts/init-project.py --profile=react-aws --name=my-app
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
