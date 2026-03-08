# Workflow Master Index

> **Start here** for understanding the AI-Assisted Development Workflow

---

## 🎯 Quick Navigation (Intent-Based)

### "I'm new to this framework"
→ **[workflow/MAIN.md](./workflow/MAIN.md)** - Start with [Quick Start section](./workflow/MAIN.md#quick-start)

### "I want to plan a new MVP"
→ **[Strategy Layer](./workflow/MAIN.md#strategy-layer-mvp-planning-40-minutes)** - 40 minute MVP decomposition guide

### "I want to plan a feature"
→ **[Campaign Layer](./workflow/MAIN.md#campaign-layer-feature-planning-1-2-hours-per-feature)** - 1-2 hour feature planning guide

### "I want to start developing"
→ **[Phase C: Development](./workflow/Phase-C-Development.md)** - Feature implementation
→ Run: `*next` to get your first task

### "Which checklist should I use?"
→ **[CHECKLIST_BY_WORKFLOW.md](./workflow/CHECKLIST_BY_WORKFLOW.md)** - Find the right checklist for your task

### "I want to deploy/release"
→ **[Phase D: Release](./workflow/Phase-D-Release.md)** - Release and deployment

---

## 📊 Visual Overview

The framework uses a **4-Phase workflow** with **3-Layer planning**:

```
Strategy Layer (40 min)   → MVP Planning
Campaign Layer (1-2h)     → Feature Planning
Tactics Layer (real-time) → Task Tracking
Code Layer                → Implementation
```

See [workflow/MAIN.md](./workflow/MAIN.md#3-layer-planning-architecture) for detailed architecture.

---

## 🔄 4-Phase Workflow

| Phase | Purpose | Document |
|-------|---------|----------|
| **A: Documentation** | Define what to build | [Phase-A-Documentation.md](./workflow/Phase-A-Documentation.md) |
| **B: Planning** | Plan how to build | [Phase-B-Planning.md](./workflow/Phase-B-Planning.md) |
| **C: Development** | Build it | [Phase-C-Development.md](./workflow/Phase-C-Development.md) |
| **D: Release** | Ship it | [Phase-D-Release.md](./workflow/Phase-D-Release.md) |

See [workflow/MAIN.md](./workflow/MAIN.md#4-phase-workflow-system) for full details.

---

## ⚡ Key Commands

| Command | Purpose |
|---------|---------|
| `*resume` | Resume previous work session |
| `*status` | Show current status and active tasks |
| `*plan` | Create MVP or feature plan |
| `*next` | Get next task from active plan |
| `*issue pick <n>` | Pick and start working on issue #n |
| `*review` | Run code review |
| `*deploy` | Deploy to environment |
| `*release` | Create release version |

**Full list**: See [commands/](./commands/) directory

---

## 🧭 Core Principles (One-Liner Summary)

- **Branch-First**: Always create feature branches before coding
- **Issue-Driven**: Every task tracked as GitHub Issue
- **PR Target**: Always PR to development (not master)
- **Branch Cleanup**: Delete branches after merge

→ See [workflow/MAIN.md#core-principles](./workflow/MAIN.md#core-principles) for detailed explanations

---

## 🔗 Directory Structure

```
.claude-template/
├── WORKFLOW.md (this file)          # Navigation hub
├── workflow/MAIN.md                 # 📖 Comprehensive guide
├── workflow/Phase-A-Documentation.md # Define what to build
├── workflow/Phase-B-Planning.md      # Plan how to build
├── workflow/Phase-C-Development.md   # Build it
├── workflow/Phase-D-Release.md       # Ship it
├── workflow/templates/               # Planning templates
├── commands/                         # 20+ workflow commands
└── rules/                            # 35+ technical rules
```

---

## 💡 Tips

### For New Users
- Start with [workflow/MAIN.md](./workflow/MAIN.md)
- Run `*next` frequently to stay on track

### For Planning
- MVP planning: 40 minutes
- Feature planning: 1-2 hours
- Plan features just-in-time

### For Development
- Always create feature branches first
- Use `plans/active/` for real-time tracking
- Commit frequently with clear messages (#XXX)

### For Quality
- Write tests for all features
- Run `*review` before creating PRs
- Document decisions in MEMORY.md

---

**Framework Version**: AI_DEV v1.0
**Based on**: yorutsuke-v2-3 workflow system
**Last Updated**: 2026-02-25
