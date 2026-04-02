# AI_DEV_PROT v15 - Coding Standards Template

> 18 Pillars of coding excellence for AI-assisted development

## What is AI_DEV_PROT?

AI_DEV_PROT v15 is a comprehensive coding standards framework covering:
- **Data Integrity** - Ensuring data correctness and validity
- **Concurrency Control** - Managing parallel operations safely
- **Architectural Boundaries** - Maintaining clean separation of concerns
- **Observability** - Making systems transparent and debuggable

## 18 Pillars Overview

| ID | Name | Quadrant | Purpose |
|----|------|----------|---------|
| **A** | Nominal Typing | Q1: Data Integrity | Branded types prevent ID confusion |
| **B** | Airlock | Q1: Data Integrity | Schema-first validation at boundaries |
| **C** | Mocking | Q1: Data Integrity | Test data generation and factories |
| **D** | FSM | Q1: Data Integrity | Finite State Machines prevent invalid states |
| **E** | Orchestration | Q2: Flow & Concurrency | Multi-step workflow coordination |
| **F** | Concurrency | Q2: Flow & Concurrency | CAS optimistic locking |
| **Q** | Idempotency | Q2: Flow & Concurrency | Safe retry and duplicate prevention |
| **G** | Traceability | Q3: Structure & Boundaries | @trigger/@listen event tracking |
| **H** | Policy | Q3: Structure & Boundaries | Auth/permission separation |
| **I** | Firewalls | Q3: Structure & Boundaries | Deep import prevention |
| **J** | Locality | Q3: Structure & Boundaries | State close to usage |
| **K** | Testing | Q3: Structure & Boundaries | 3-layer test pyramid |
| **L** | Headless | Q3: Structure & Boundaries | Logic-UI separation |
| **M** | Saga | Q4: Resilience & Observability | Step-by-step compensation |
| **N** | Context | Q4: Resilience & Observability | TraceId propagation |
| **O** | Async | Q4: Resilience & Observability | Long operations (202 + poll) |
| **P** | Circuit Breaker | Q4: Resilience & Observability | Failure isolation |
| **R** | Observability | Q4: Resilience & Observability | JSON semantic logging |

**See CHEATSHEET.md for quick reference.**

## Directory Structure

```
.claude/pillars/
├── README.md                    # This file
├── CHEATSHEET.md                # Quick reference
├── STRUCTURE.md                 # Detailed structure docs
│
├── checklists/                  # 3-Phase Development Checklist System
│   ├── README.md                # Checklist system overview
│   ├── pre-code.md              # Planning checklist (before coding)
│   ├── in-code.md               # Execution checklist (during coding)
│   ├── post-code.md             # Validation checklist (before PR)
│   └── PILLAR_CHECKLISTS.md     # Complete Pillar verification (future)
│
└── pillars/                     # 18 Pillars organized by quadrant
    ├── q1-data-integrity/       # A, B, C, D
    ├── q2-flow-concurrency/     # E, F, Q
    ├── q3-structure-boundaries/ # G, H, I, J, K, L
    └── q4-resilience-observability/  # M, N, O, P, R
```

Each Pillar directory contains:
- `{name}.md` - The law and rationale
- `{name}.ts` - TypeScript implementation
- `checklist.md` - Verification items
- `audit.ts` - Automated checks (optional)

## How to Use

### 1. Enable Pillars for Your Project

Not all projects need all 18 Pillars. Choose based on your needs:

**Minimal** (Simple CRUD):
- A (Nominal Typing), B (Airlock), K (Testing), L (Headless)

**Standard** (Production):
- Minimal + M (Saga), Q (Idempotency), R (Observability)

**Full** (Complex distributed):
- All 18 Pillars

### 2. Integrate with Your Tech Stack

Each Pillar includes examples for:
- **TypeScript** (primary), **Python**, **Go** (alternatives)

Adapt patterns to your framework:
- **React**: Pillar L (Headless)
- **AWS Lambda**: Pillars M, Q, R
- **Tauri**: Pillar L + Service Pattern

### 3. Use 3-Phase Checklist System

The framework provides structured quality gates at each development stage:

- **[Pre-Code](checklists/pre-code.md)**: Planning checklist (run BEFORE coding)
  - Task classification (T1/T2/T3)
  - Pattern selection
  - Architecture planning

- **[In-Code](checklists/in-code.md)**: Execution checklist (run DURING coding)
  - Real-time validation per task
  - Pillar compliance checks
  - Quick quality gates

- **[Post-Code](checklists/post-code.md)**: Validation checklist (run BEFORE PR)
  - Final quality audit
  - Test coverage verification
  - Security checks

See [checklists/README.md](checklists/README.md) for complete workflow guide.

### 4. Reference CHEATSHEET.md

Quick lookup for:
- Tier classification (T1/T2/T3)
- Common patterns and anti-patterns
- Key concepts (traceId vs intentId)

## AI-Friendly Design

This framework is designed for AI-assisted development:

✅ **Explicit > Abstract** - No implicit conventions
✅ **Clear > DRY** - AI generates repetitive code quickly
✅ **Concrete > Generic** - Specific types help AI reasoning
✅ **Simple > Clever** - Direct patterns work better

Each Pillar is self-contained with all documentation and examples.

## Progressive Adoption

**Start Simple**:
1. Enable Pillars A, B (Data Integrity)
2. Add Pillar K (Testing) for quality
3. Add Pillar L (Headless) for architecture

**Grow as Needed**:
4. Add Pillar M (Saga) for multi-step workflows
5. Add Pillar R (Observability) for debugging
6. Add other Pillars based on specific needs

## Examples by Project Type

| Project Type | Enable Pillars | Focus |
|--------------|----------------|-------|
| **Web Frontend** | A, B, L, K | Headless, nominal types |
| **Backend API** | A, B, M, Q, R | Saga, Idempotency, Observability |
| **Desktop App** | A, B, L, K, M | Headless, Service Layer, Saga |
| **Full-Stack** | A, B, L, K, M, Q, R | Complete architecture |

## Related Documentation

### Framework Navigation
- **[Root README](../../README.md)** - Project overview and quick start
- **[Workflow System](../.claude-template/README.md)** - Commands, rules, and development workflow
- **[Profile System](../profiles/README.md)** - Tech stack configurations and setup

### Pillars Resources
- **[PILLAR_INTERDEPENDENCIES.md](PILLAR_INTERDEPENDENCIES.md)**: **START HERE** - Understand pillar dependencies and combinations
- **CHEATSHEET.md**: Quick reference for daily use
- **STRUCTURE.md**: Detailed structure documentation
- **ADR-*** files: Architecture Decision Records

### Implementation
- **[.claude/rules/](../.claude-template/rules/)** - Technical rules and patterns (40+ rules)
- **Reference Project**: [yorutsuke-v2-3](https://github.com/aifuun/yorutsuke-v2-3)

---

**Version**: v15
**Last Updated**: 2026-02-05
**Status**: Template
