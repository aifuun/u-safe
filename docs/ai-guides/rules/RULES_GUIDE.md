# RULES_GUIDE.md - Template-Based Rules Management

---
guide_type: master
audience: AI
purpose: Rules creation and management
last_updated: 2026-03-26
depends_on:
  - docs/ADRs/013-template-based-rules-management.md
  - docs/ai-guides/doc-templates/MANAGE_DOCS_GUIDE.md
---

> Master guide for AI to create/update technical rules using the template-based rules system

## Table of Contents

1. [Overview](#1-overview)
2. [Rule Categories](#2-rule-categories)
3. [Profile System](#3-profile-system)
4. [Template Format](#4-template-format)
5. [Usage Guide](#5-usage-guide)
6. [Integration](#6-integration)
7. [Migration from update-rules](#7-migration-from-update-rules)
8. [Examples](#8-examples)

---

## 1. Overview

### What is the Template-Based Rules System?

The template-based rules system is a **framework-based approach** to technical rules that:

- **Organizes rules by category** (core, architecture, languages, frontend, backend, infrastructure, development)
- **Uses template-based generation** with YAML frontmatter and markdown content
- **Supports profile-specific filtering** (tauri: 23 rules, nextjs-aws: 30 rules)
- **Provides AI-executable guides** for each category
- **Maintains single source of truth** in `docs/ai-guides/rules/templates/`

### Why Template-Based Rules?

**Architecture consistency**:
- Docs use `manage-docs` skill
- ADRs use `manage-adrs` skill
- Rules use `manage-rules` skill (same pattern)

**Eliminates redundancy**:
- Old approach: `update-framework` → `update-rules` (batch sync, 30-50% redundant rules)
- New approach: Generate on-demand with profile filtering (<10% redundancy)

**Modular updates**:
- Old: Update one rule → sync entire framework (affects Pillars too)
- New: `manage-rules --category core` → update only core rules

**Profile-aware**:
- tauri profile: 23 rules (Core + Architecture + Rust + Frontend + Infrastructure)
- nextjs-aws profile: 30 rules (Core + Architecture + TypeScript + Frontend + Backend + AWS)

### When to Use `/manage-rules`

Use the `/manage-rules` skill when you need to:

1. **Initialize rules** for a new project (first-time setup)
2. **Update specific categories** (partial regeneration)
3. **Apply profile changes** after tech stack updates
4. **Refresh templates** after framework updates
5. **Add custom rules** for project-specific patterns

---

## 2. Rule Categories

The system organizes rules into 7 categories with different scopes:

### Core (Essential)

**Path**: `templates/core/`
**Applies to**: ALL profiles
**Rule count**: ~5-8 rules
**Pillar reference**: Data Integrity, Resilience & Observability

**Focus**: Fundamental programming principles applicable to all projects

**Topics**:
- Error handling patterns
- Logging and monitoring
- Code organization and naming
- Testing fundamentals
- Security basics

**Example templates**:
- `error-handling.md` - Try/catch patterns, error propagation
- `logging.md` - Structured logging, log levels
- `naming-conventions.md` - Variables, functions, files
- `testing-basics.md` - Unit test structure, mocking

---

### Architecture (System Design)

**Path**: `templates/architecture/`
**Applies to**: ALL profiles
**Rule count**: ~4-6 rules
**Pillar reference**: Structure & Boundaries

**Focus**: System design patterns and architectural principles

**Topics**:
- Clean architecture layers (UI → Domain → Data)
- Dependency direction (inward only)
- Module boundaries
- API design patterns
- Data flow

**Example templates**:
- `clean-architecture.md` - Layer separation, dependency rules
- `module-boundaries.md` - Public/private APIs, cohesion
- `api-design.md` - RESTful patterns, error responses
- `data-flow.md` - Unidirectional flow, state management

---

### Languages (Tech-Specific)

**Path**: `templates/languages/`
**Applies to**: Profile-dependent (tauri → Rust, nextjs-aws → TypeScript)
**Rule count**: ~3-5 rules per language
**Pillar reference**: All (language-specific applications)

**Focus**: Language-specific standards and idioms

**Topics**:
- TypeScript: Strict types, generics, utility types
- Rust: Ownership, lifetimes, error handling (Result<T, E>)
- Python: Type hints, async/await, decorators

**Example templates**:
- `typescript/strict-types.md` - No any, type guards, branded types
- `rust/ownership.md` - Borrowing rules, lifetime annotations
- `python/type-hints.md` - mypy configuration, protocol types

---

### Frontend (UI/UX)

**Path**: `templates/frontend/`
**Applies to**: Profiles with UI (tauri, nextjs-aws)
**Rule count**: ~5-8 rules
**Pillar reference**: Structure & Boundaries, Resilience & Observability

**Focus**: Frontend development standards

**Topics**:
- React/Vue patterns (hooks, composition)
- State management (Context, Zustand, Redux)
- Component design (atomic design, prop drilling)
- Accessibility (ARIA, keyboard navigation)
- Performance (memoization, lazy loading)

**Example templates**:
- `react/hooks-patterns.md` - Custom hooks, useEffect dependencies
- `state-management.md` - When to use local vs global state
- `component-design.md` - Props vs children, composition patterns
- `accessibility.md` - ARIA labels, focus management

---

### Backend (Server-Side)

**Path**: `templates/backend/`
**Applies to**: Profiles with server components (nextjs-aws, tauri-aws)
**Rule count**: ~6-10 rules
**Pillar reference**: Data Integrity, Flow & Concurrency, Resilience & Observability

**Focus**: Server-side development patterns

**Topics**:
- API endpoints (REST, GraphQL)
- Database access (ORM, raw SQL, transactions)
- Authentication (JWT, sessions, OAuth)
- Caching (Redis, in-memory, CDN)
- Background jobs (queues, workers)

**Example templates**:
- `api-endpoints.md` - Route naming, request validation, error responses
- `database-access.md` - Query optimization, N+1 prevention, transactions
- `authentication.md` - Token storage, refresh logic, RBAC
- `caching.md` - Cache invalidation, TTL strategies

---

### Infrastructure (DevOps)

**Path**: `templates/infrastructure/`
**Applies to**: Profile-dependent (AWS → CDK, Docker → containers)
**Rule count**: ~3-5 rules
**Pillar reference**: Resilience & Observability

**Focus**: Deployment and operations standards

**Topics**:
- Docker configuration (multi-stage builds, layer caching)
- CI/CD pipelines (GitHub Actions, build caching)
- Monitoring (CloudWatch, logs aggregation)
- Security (secrets management, IAM policies)

**Example templates**:
- `docker.md` - Multi-stage builds, .dockerignore, healthchecks
- `ci-cd.md` - Workflow optimization, artifact caching
- `monitoring.md` - Metrics collection, alerting thresholds
- `secrets.md` - AWS Secrets Manager, environment variables

---

### Development (Workflow)

**Path**: `templates/development/`
**Applies to**: ALL profiles
**Rule count**: ~3-5 rules
**Pillar reference**: All (process standards)

**Focus**: Development process and tooling

**Topics**:
- Git workflow (branching, commit messages, PR templates)
- Testing strategy (unit, integration, e2e coverage)
- Code review (review checklist, approval criteria)
- Documentation (README, API docs, ADRs)

**Example templates**:
- `git-workflow.md` - Branch naming, commit format, merge strategy
- `testing-strategy.md` - Coverage goals, test pyramid, mocking
- `code-review.md` - Review checklist, automated checks
- `documentation.md` - When to write docs, template usage

---

## 3. Profile System

### Profile Definitions

**tauri** (Desktop app with Rust + React):
```yaml
profile: tauri
tech_stack:
  - rust
  - typescript
  - react
  - tauri
categories:
  - core          # 5-8 rules
  - architecture  # 4-6 rules
  - languages     # rust (3-5), typescript (3-5)
  - frontend      # 5-8 rules
  - infrastructure # 3-5 rules (Docker, CI/CD)
  - development   # 3-5 rules
total_rules: ~23-30 rules
```

**nextjs-aws** (Full-stack web app with Next.js + AWS):
```yaml
profile: nextjs-aws
tech_stack:
  - typescript
  - react
  - nextjs
  - aws
  - lambda
  - dynamodb
categories:
  - core          # 5-8 rules
  - architecture  # 4-6 rules
  - languages     # typescript (3-5)
  - frontend      # 5-8 rules
  - backend       # 6-10 rules (API, DB, Auth)
  - infrastructure # 3-5 rules (AWS CDK, CloudWatch)
  - development   # 3-5 rules
total_rules: ~30-40 rules
```

### Profile Filtering Logic

**Rule inclusion criteria**:
```python
def should_include_rule(rule: dict, profile: str) -> bool:
    """
    决定是否在项目中包含此规则

    Args:
        rule: 规则模板（包含 YAML frontmatter）
        profile: 项目 profile（tauri, nextjs-aws等）

    Returns:
        True if rule应包含，False otherwise
    """
    # 1. Category check
    if rule.category in ['core', 'architecture', 'development']:
        return True  # Always include

    # 2. Tech stack check
    profile_stack = PROFILE_TECH_STACKS[profile]
    rule_tags = rule.metadata.get('tags', [])

    # OR logic: 任一 tag 匹配即包含
    return any(tag in profile_stack for tag in rule_tags)

# Example
rule = {
    'category': 'languages',
    'metadata': {
        'tags': ['rust', 'ownership']
    }
}

profile = 'tauri'
PROFILE_TECH_STACKS['tauri'] = ['rust', 'typescript', 'react', 'tauri']

should_include_rule(rule, profile)  # → True (rust matches)
```

### Custom Rules (Project-Specific)

Projects can add custom rules that override or extend framework rules:

**Location**: `.claude/rules/custom/` (generated, not synced)

**Use cases**:
- Company-specific coding standards
- Domain-specific patterns (e.g., financial calculations)
- Team conventions (e.g., folder structure)

**Example**:
```yaml
# .claude/rules/custom/financial-calculations.md
---
category: custom
priority: high
tags: [finance, domain]
---

# Financial Calculations

Use Decimal type for all monetary calculations to avoid floating-point errors.

## Examples

```typescript
// ✅ CORRECT
import { Decimal } from 'decimal.js';
const total = new Decimal('19.99').plus('0.01');

// ❌ WRONG
const total = 19.99 + 0.01;  // → 20.000000000000004
```
```

---

## 4. Template Format

### YAML Frontmatter

All rule templates use YAML frontmatter for metadata:

```yaml
---
category: architecture          # Required: core, architecture, languages, etc.
title: Clean Architecture      # Required: Display title
tags: [layering, boundaries]   # Required: Tech/topic tags for filtering
priority: high                  # Optional: high, medium, low
pillar: structure-boundaries    # Optional: Reference to Pillar file
applies_to: [all]              # Optional: Profile filter (default: all)
last_updated: 2026-03-26       # Required: Maintenance tracking
---
```

### Markdown Content Structure

```markdown
# {Title}

**Pillar Reference**: {pillar-name} (if applicable)
**Applies to**: {profiles or "all projects"}

## Overview

Brief explanation (1-2 sentences) of what this rule covers.

## Key Principles

- Principle 1
- Principle 2
- Principle 3

## Examples

### ✅ Good Example

```language
// Show correct implementation
```

**Why this works**: Explanation

### ❌ Bad Example

```language
// Show incorrect implementation
```

**Why this fails**: Explanation

## Common Pitfalls

1. **Pitfall 1**: Description and how to avoid
2. **Pitfall 2**: Description and how to avoid

## Related Rules

- [Rule 1](../category/rule1.md)
- [Rule 2](../category/rule2.md)

## Related Pillars

- [Pillar Name](../../../../.prot/pillar-file.md) - Deep dive into X
```

### Template Variables

Templates support variable substitution:

```markdown
Project: {{PROJECT_NAME}}
Profile: {{PROFILE}}
Tech Stack: {{TECH_STACK}}
```

**Replaced during generation** by `manage-rules` skill.

---

## 5. Usage Guide

### AI Execution: Generate Rules

**Command**: `/manage-rules --init` or `/manage-rules --category core`

**Algorithm**:
```python
def generate_rules(profile: str, categories: list = None):
    """
    生成规则文件到 .claude/rules/

    Steps:
    1. Read profile configuration
    2. Load template files from docs/ai-guides/rules/templates/
    3. Filter templates by profile (should_include_rule)
    4. Apply variable substitution
    5. Write to .claude/rules/{category}/{rule-name}.md
    """

    # 1. Read profile
    profile_config = read_profile(f"framework/profiles/{profile}.yaml")
    tech_stack = profile_config['tech_stack']

    # 2. Load templates
    template_dirs = glob('docs/ai-guides/rules/templates/*/')

    # 3. Filter by category if specified
    if categories:
        template_dirs = [d for d in template_dirs if d.name in categories]

    # 4. Process each template
    for template_dir in template_dirs:
        for template_file in template_dir.glob('*.md'):
            # Parse YAML frontmatter
            metadata, content = parse_template(template_file)

            # Filter by profile
            if not should_include_rule(metadata, profile):
                continue

            # Apply variable substitution
            content = substitute_variables(content, {
                'PROJECT_NAME': project_name,
                'PROFILE': profile,
                'TECH_STACK': ', '.join(tech_stack)
            })

            # Write to output
            category = metadata['category']
            output_path = f".claude/rules/{category}/{template_file.name}"
            write_file(output_path, content)

            print(f"✅ Generated: {output_path}")
```

### Update Specific Category

```bash
# Update only core rules
/manage-rules --category core

# Update multiple categories
/manage-rules --category core,architecture
```

### Add Custom Rule

```bash
# Create custom rule (not synced from framework)
/manage-rules --custom --name financial-calculations
```

---

## 6. Integration

### With manage-docs Skill

Rules reference documentation templates:

```markdown
<!-- In manage-docs generated ARCHITECTURE.md -->

See [Clean Architecture Rule](.claude/rules/architecture/clean-architecture.md) for layer separation standards.
```

### With manage-adrs Skill

ADRs reference rules for decisions:

```markdown
<!-- In ADR -->

This decision follows [API Design Rule](.claude/rules/backend/api-design.md).
```

### With update-guides Skill

**Purpose**: Sync guides and rule templates from framework to project

**Command**: `/update-guides ~/path/to/ai-dev`

**What it syncs**:
- `docs/ai-guides/` directory (guides + templates)
- Including `docs/ai-guides/rules/templates/`

**What it does NOT sync**:
- Generated rules (`.claude/rules/` - these are project-specific)
- Pillars (use `/update-framework` for Pillars)

**Workflow**:
```bash
# Framework developer updates rule template
vi docs/ai-guides/rules/templates/core/error-handling.md

# Project uses /update-guides to get latest templates
/update-guides ~/dev/ai-dev

# Project regenerates rules
/manage-rules --category core
```

### With update-framework Skill

**OLD behavior** (before ADR-013):
```bash
/update-framework ~/ai-dev
  → Syncs Pillars
  → Syncs Rules (via update-rules)  # REMOVED
  → Syncs Workflow
```

**NEW behavior** (after ADR-013):
```bash
/update-framework ~/ai-dev
  → Syncs Pillars ONLY

# Rules now synced separately
/update-guides ~/ai-dev
  → Syncs docs/ai-guides/ (including rules/templates/)

/manage-rules --init
  → Generates .claude/rules/ from templates
```

---

## 7. Migration from update-rules

### Old Workflow (Framework Sync)

```bash
# In framework repo
vi framework/.claude-template/rules/architecture/clean-architecture.md

# In project repo
/update-framework ~/dev/ai-dev
  → Copies ALL rules from framework/.claude-template/rules/
  → Result: 40 rules, 30-50% redundant for profile
```

**Problems**:
- Rules coupled with Pillars (can't update independently)
- Batch sync (all or nothing)
- High redundancy (nextjs-aws project gets Rust rules)

### New Workflow (Template Generation)

```bash
# In framework repo
vi docs/ai-guides/rules/templates/architecture/clean-architecture.md

# In project repo
/update-guides ~/dev/ai-dev
  → Syncs docs/ai-guides/ (templates only, no generated files)

/manage-rules --category architecture
  → Generates .claude/rules/architecture/ from templates
  → Filtered by profile (tauri: 23 rules, nextjs-aws: 30 rules)
  → Result: <10% redundancy
```

**Benefits**:
- Rules independent from Pillars
- Modular updates (per category)
- Profile-aware filtering (minimal redundancy)

### Migration Checklist for Existing Projects

```markdown
- [ ] 1. Backup current .claude/rules/ directory
- [ ] 2. Run /update-guides to get rule templates
- [ ] 3. Run /manage-rules --init to regenerate rules
- [ ] 4. Compare old vs new rules (check for custom rules)
- [ ] 5. Migrate custom rules to .claude/rules/custom/
- [ ] 6. Delete backup after verification
- [ ] 7. Update .gitignore: add .claude/rules/ (generated files)
```

---

## 8. Examples

### Example 1: Initialize Rules for Tauri Project

```bash
# Step 1: Ensure templates are synced
/update-guides ~/dev/ai-dev

# Step 2: Generate rules
/manage-rules --init

# Output:
✅ Generated: .claude/rules/core/error-handling.md
✅ Generated: .claude/rules/core/logging.md
✅ Generated: .claude/rules/architecture/clean-architecture.md
✅ Generated: .claude/rules/languages/rust/ownership.md
✅ Generated: .claude/rules/languages/typescript/strict-types.md
✅ Generated: .claude/rules/frontend/react/hooks-patterns.md
...
📊 Total: 23 rules generated for tauri profile
```

### Example 2: Update Core Rules After Template Change

```bash
# Framework updated error-handling template
# Get latest templates
/update-guides ~/dev/ai-dev

# Regenerate only core rules
/manage-rules --category core

# Output:
✅ Updated: .claude/rules/core/error-handling.md
✅ Updated: .claude/rules/core/logging.md
✅ Updated: .claude/rules/core/naming-conventions.md
📊 3 core rules updated
```

### Example 3: Add Custom Financial Rule

```bash
# Create custom rule
/manage-rules --custom --name financial-calculations

# AI generates:
# .claude/rules/custom/financial-calculations.md
# With template structure and project-specific content
```

---

## Related Documentation

- **ADR-013**: [Template-Based Rules Management](../../ADRs/013-template-based-rules-management.md)
- **MANAGE_DOCS_GUIDE.md**: Sister guide for documentation templates
- **Pillars**: `framework/.prot-template/` (deep technical knowledge, 200-300 lines)
- **Rules**: `.claude/rules/` (quick reference, 20-70 lines)

---

## Appendix: Rule vs Pillar

**When to use Rules**:
- Quick reference during coding
- Copy-paste patterns
- 20-70 lines (1-2 minute read)
- Multiple per category

**When to use Pillars**:
- Deep understanding needed
- Comprehensive coverage of a domain
- 200-300 lines (10-15 minute read)
- One per major topic (18 total)

**Example**:
- **Rule**: `error-handling.md` (30 lines) - "Use try/catch, return Result<T,E>"
- **Pillar**: `05-error-handling.md` (250 lines) - Error recovery strategies, propagation patterns, custom error types, logging integration

---

**Last Updated**: 2026-03-26
**Version**: 1.0.0
**Maintained By**: AI Development Framework Team
