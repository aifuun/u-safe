# Rules Index - Complete Catalog

> Central index for all 40+ technical rules in the AI Dev Framework

## Quick Navigation

- [Core Rules](#core-rules) (7) - Workflow, naming, debugging
- [Architecture Rules](#architecture-rules) (7) - Clean architecture, layers
- [Frontend Rules](#frontend-rules) (6) - React, Zustand, design
- [Backend Rules](#backend-rules) (5) - Saga, Lambda, APIs
- [Infrastructure Rules](#infrastructure-rules) (10) - CDK, Tauri, deployment
- [Development Rules](#development-rules) (2) - Testing, file creation
- [Language Rules](#language-rules) (3) - TypeScript patterns

**Total**: 40 Rules | [Quick Reference](./QUICK_REFERENCE.md) | [README](./README.md)

---

## Core Rules

### [workflow.md](./core/workflow.md)
**Purpose**: MVP, Issues, and Plans coordination system
**Triggers**: `.claude/plans/active/`, `docs/dev/MVP*.md`, `.claude/MEMORY.md`
**Related Pillars**: E (Orchestration), G (Traceability)
**Use When**: Starting new session, planning features, managing issues

### [naming.md](./core/naming.md)
**Purpose**: Naming conventions and single source of truth
**Triggers**: All files
**Related Pillars**: None (foundational)
**Use When**: Creating new features, files, or components

### [debugging.md](./core/debugging.md)
**Purpose**: Systematic debugging with semantic logging
**Triggers**: All files
**Related Pillars**: R (Observability), N (Context)
**Use When**: Investigating bugs, adding logs

### [docs.md](./core/docs.md)
**Purpose**: Documentation standards and structure
**Triggers**: `docs/**`
**Related Pillars**: None
**Use When**: Writing or updating documentation

### [memory-management.md](./core/memory-management.md)
**Purpose**: MEMORY.md management for AI context
**Triggers**: `.claude/MEMORY.md`
**Related Pillars**: None
**Use When**: Updating project memory, managing AI context

### [memory-protection.md](./core/memory-protection.md)
**Purpose**: MEMORY.md size control and cleanup
**Triggers**: `.claude/MEMORY.md`
**Related Pillars**: None
**Use When**: MEMORY.md exceeds size limits

### [planning-context.md](./core/planning-context.md)
**Purpose**: Planning file usage and context management
**Triggers**: `.claude/plans/**`
**Related Pillars**: E (Orchestration)
**Use When**: Creating or updating planning files

---

## Architecture Rules

### [clean-architecture.md](./architecture/clean-architecture.md)
**Purpose**: Enforce dependency inversion and layer separation
**Triggers**: All source files
**Related Pillars**: I (Firewalls), J (Locality), L (Headless)
**Use When**: Designing architecture, reviewing imports

### [layer-boundaries.md](./architecture/layer-boundaries.md)
**Purpose**: Prevent import violations and enforce boundaries
**Triggers**: All source files
**Related Pillars**: I (Firewalls)
**Use When**: Setting up ESLint, reviewing imports

### [dependency-rule.md](./architecture/dependency-rule.md)
**Purpose**: Dependencies MUST point inward
**Triggers**: All source files
**Related Pillars**: I (Firewalls)
**Use When**: Reviewing architecture, refactoring

### [headless.md](./architecture/headless.md)
**Purpose**: Logic-UI separation (No JSX in hooks)
**Triggers**: `**/headless/*.ts`
**Related Pillars**: L (Headless), D (FSM)
**Use When**: Creating React hooks, separating logic from UI

### [service-layer.md](./architecture/service-layer.md)
**Purpose**: Service orchestration with IO-first pattern
**Triggers**: `**/services/*.ts`
**Related Pillars**: E (Orchestration)
**Use When**: Creating services, orchestrating IO operations

### [adapters.md](./architecture/adapters.md)
**Purpose**: IO boundary with no business logic
**Triggers**: `**/adapters/*.ts`
**Related Pillars**: B (Airlock)
**Use When**: Creating API clients, IO operations

### [identity.md](./architecture/identity.md)
**Purpose**: User ID and device ID management
**Triggers**: All source files
**Related Pillars**: A (Nominal Typing)
**Use When**: Handling user/device identity

---

## Frontend Rules

### [zustand-hooks.md](./frontend/zustand-hooks.md)
**Purpose**: Zustand selector safety (prevent infinite loops)
**Triggers**: `**/stores/*.ts`, `**/hooks/**`
**Related Pillars**: L (Headless)
**Use When**: Using Zustand, creating selectors

### [stores.md](./frontend/stores.md)
**Purpose**: Vanilla store pattern without hooks
**Triggers**: `**/stores/*.ts`
**Related Pillars**: L (Headless)
**Use When**: Creating global state stores

### [design-system.md](./frontend/design-system.md)
**Purpose**: Component library standards
**Triggers**: `**/components/**`
**Related Pillars**: L (Headless)
**Use When**: Creating UI components

### [views.md](./frontend/views.md)
**Purpose**: View layer rules (thin, delegate to headless)
**Triggers**: `**/views/**`, `**/pages/**`
**Related Pillars**: L (Headless)
**Use When**: Creating views/pages

### [css.md](./frontend/css.md)
**Purpose**: CSS and styling conventions
**Triggers**: `**/*.css`, `**/*.scss`
**Related Pillars**: None
**Use When**: Writing styles

### [debug-panel.md](./frontend/debug-panel.md)
**Purpose**: Debug tools and development panels
**Triggers**: `**/debug/**`
**Related Pillars**: R (Observability)
**Use When**: Creating debug tools

---

## Backend Rules

### [saga.md](./backend/saga.md)
**Purpose**: Compensation pattern for distributed transactions
**Triggers**: `**/*Saga.ts`
**Related Pillars**: M (Saga), Q (Idempotency), F (Concurrency), R (Observability)
**Use When**: T3 operations, multi-step workflows, payments

### [lambda-typescript-esm.md](./backend/lambda-typescript-esm.md)
**Purpose**: Lambda + TypeScript + ESM configuration
**Triggers**: `**/lambda/**`
**Related Pillars**: None
**Use When**: Creating AWS Lambda functions

### [lambda-local-first.md](./backend/lambda-local-first.md)
**Purpose**: Test Lambda code locally before deployment
**Triggers**: `**/lambda/**`, `experiments/**`
**Related Pillars**: K (Testing)
**Use When**: Developing Lambda functions

### [query-transactions.md](./backend/query-transactions.md)
**Purpose**: DynamoDB query and transaction patterns
**Triggers**: `**/repositories/**`
**Related Pillars**: Q (Idempotency), F (Concurrency)
**Use When**: Querying DynamoDB, using transactions

### [external-api-integrations.md](./backend/external-api-integrations.md)
**Purpose**: Third-party API integration principles (SDK first)
**Triggers**: `**/adapters/**`
**Related Pillars**: B (Airlock), P (Circuit Breaker)
**Use When**: Integrating external services (Azure, AWS, etc.)

---

## Infrastructure Rules

### [cdk-deploy.md](./infrastructure/cdk-deploy.md)
**Purpose**: AWS CDK deployment workflow
**Triggers**: `infra/**`
**Related Pillars**: None
**Use When**: Deploying infrastructure changes

### [cdk-watch-testing.md](./infrastructure/cdk-watch-testing.md)
**Purpose**: CDK Watch for rapid Lambda testing
**Triggers**: `infra/**`
**Related Pillars**: K (Testing)
**Use When**: Testing Lambda changes rapidly

### [lambda-layer-deployment.md](./infrastructure/lambda-layer-deployment.md)
**Purpose**: Lambda Layers deployment and versioning
**Triggers**: `infra/lambda-layers/**`
**Related Pillars**: None
**Use When**: Deploying shared Lambda code

### [lambda-quick-reference.md](./infrastructure/lambda-quick-reference.md)
**Purpose**: Lambda troubleshooting and quick reference
**Triggers**: `**/lambda/**`
**Related Pillars**: R (Observability)
**Use When**: Debugging Lambda issues

### [tauri-stack.md](./infrastructure/tauri-stack.md)
**Purpose**: Tauri integration and IPC patterns
**Triggers**: `src-tauri/**`
**Related Pillars**: L (Headless)
**Use When**: Working with Tauri commands/IPC

### [secrets.md](./infrastructure/secrets.md)
**Purpose**: Secrets management (never hardcode)
**Triggers**: All source files
**Related Pillars**: None
**Use When**: Handling API keys, credentials

### [aws-services.md](./infrastructure/aws-services.md)
**Purpose**: AWS service usage patterns
**Triggers**: `infra/**`, `**/adapters/**`
**Related Pillars**: None
**Use When**: Using AWS services

### [diagnostic-export-logging.md](./infrastructure/diagnostic-export-logging.md)
**Purpose**: Structured logging and diagnostic export
**Triggers**: All source files
**Related Pillars**: R (Observability), N (Context)
**Use When**: Adding logs, creating diagnostics

### [time-handling.md](./infrastructure/time-handling.md)
**Purpose**: Timezone and timestamp handling
**Triggers**: All source files
**Related Pillars**: None
**Use When**: Working with dates/times

### [url-construction.md](./infrastructure/url-construction.md)
**Purpose**: URL building patterns
**Triggers**: All source files
**Related Pillars**: None
**Use When**: Constructing URLs

---

## Development Rules

### [infinite-loop-prevention.md](./development/infinite-loop-prevention.md)
**Purpose**: Prevent React infinite re-render loops
**Triggers**: `**/*.tsx`, `**/hooks/**`
**Related Pillars**: L (Headless)
**Use When**: Debugging infinite loops, creating hooks

### [file-creation.md](./development/file-creation.md)
**Purpose**: File creation restrictions and patterns
**Triggers**: All files
**Related Pillars**: None
**Use When**: Creating new files

---

## Language Rules

### [typescript-strict.md](./languages/typescript-strict.md)
**Purpose**: TypeScript strict mode and type safety
**Triggers**: `**/*.ts`, `**/*.tsx`
**Related Pillars**: A (Nominal Typing)
**Use When**: Writing TypeScript code

### [typescript-nominal-types.md](./languages/typescript-nominal-types.md)
**Purpose**: Branded types for ID safety
**Triggers**: `**/types/**`, `**/*.ts`
**Related Pillars**: A (Nominal Typing)
**Use When**: Defining IDs, creating branded types

### [typescript-esm.md](./languages/typescript-esm.md)
**Purpose**: ESM module usage in TypeScript
**Triggers**: `**/*.ts`
**Related Pillars**: None
**Use When**: Configuring TypeScript, using ESM

---

## Rules by Pillar

Quick lookup: Which Rules relate to which Pillars?

| Pillar | Related Rules |
|--------|---------------|
| **A: Nominal Typing** | typescript-nominal-types, typescript-strict, identity |
| **B: Airlock** | adapters, external-api-integrations |
| **D: FSM** | headless |
| **E: Orchestration** | workflow, service-layer, planning-context |
| **F: Concurrency** | saga, query-transactions |
| **G: Traceability** | workflow |
| **I: Firewalls** | clean-architecture, layer-boundaries, dependency-rule |
| **J: Locality** | clean-architecture |
| **K: Testing** | lambda-local-first, cdk-watch-testing |
| **L: Headless** | headless, views, design-system, stores, zustand-hooks, clean-architecture, infinite-loop-prevention, tauri-stack |
| **M: Saga** | saga |
| **N: Context** | debugging, diagnostic-export-logging |
| **P: Circuit Breaker** | external-api-integrations |
| **Q: Idempotency** | saga, query-transactions |
| **R: Observability** | debugging, diagnostic-export-logging, lambda-quick-reference, debug-panel, saga |

---

## Find Rules by Scenario

### "I'm writing a React component"
- [design-system.md](./frontend/design-system.md) - UI standards
- [headless.md](./architecture/headless.md) - Logic separation
- [zustand-hooks.md](./frontend/zustand-hooks.md) - State management
- [views.md](./frontend/views.md) - View layer rules

### "I'm writing a backend service"
- [service-layer.md](./architecture/service-layer.md) - Service pattern
- [adapters.md](./architecture/adapters.md) - IO boundaries
- [saga.md](./backend/saga.md) - If T3 operations
- [lambda-typescript-esm.md](./backend/lambda-typescript-esm.md) - If AWS Lambda

### "I'm deploying to AWS"
- [cdk-deploy.md](./infrastructure/cdk-deploy.md) - Deployment workflow
- [secrets.md](./infrastructure/secrets.md) - Secrets management
- [lambda-layer-deployment.md](./infrastructure/lambda-layer-deployment.md) - If using Layers
- [aws-services.md](./infrastructure/aws-services.md) - AWS patterns

### "I'm writing tests"
- [lambda-local-first.md](./backend/lambda-local-first.md) - Test locally
- [cdk-watch-testing.md](./infrastructure/cdk-watch-testing.md) - Rapid testing

### "I encountered a bug"
- [infinite-loop-prevention.md](./development/infinite-loop-prevention.md) - React loops
- [debugging.md](./core/debugging.md) - General debugging
- [lambda-quick-reference.md](./infrastructure/lambda-quick-reference.md) - Lambda issues

### "I'm starting a new feature"
- [workflow.md](./core/workflow.md) - Feature workflow
- [planning-context.md](./core/planning-context.md) - Planning
- [naming.md](./core/naming.md) - Naming conventions
- [clean-architecture.md](./architecture/clean-architecture.md) - Architecture

---

## Statistics

- **Total Rules**: 40
- **By Category**:
  - Core: 7 (18%)
  - Architecture: 7 (18%)
  - Frontend: 6 (15%)
  - Backend: 5 (13%)
  - Infrastructure: 10 (25%)
  - Development: 2 (5%)
  - Languages: 3 (8%)
- **Path-Triggered**: 35 (88%)
- **Manual-Only**: 5 (12%)
- **Related to Pillars**: 28 (70%)

---

## See Also

- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Top 20 most-used Rules
- **[README.md](./README.md)** - Rules system overview
- **[templates/RULE_TEMPLATE.md](./templates/RULE_TEMPLATE.md)** - Create new Rules
- **[../.prot-template/README.md](../.prot-template/README.md)** - AI_DEV_PROT Pillars

---

**Version**: 1.0
**Last Updated**: 2026-02-05
**Total Rules**: 40
