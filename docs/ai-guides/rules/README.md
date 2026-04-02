# Rules Guide

> Template-based technical rules system for profile-aware development standards

## Overview

This directory contains template-based technical rules organized by category. Each template defines coding standards, patterns, and best practices that AI assistants use during development.

**Purpose**: Provide quick-reference technical rules that adapt to project profiles (tauri, nextjs-aws) while maintaining consistency across the framework.

**How it works**:
- **Templates** define rules with YAML frontmatter and markdown content
- **Profile filtering** includes/excludes rules based on tech stack
- **AI integration** with manage-* skills for automated rule generation

## Directory Structure

```
docs/ai-guides/rules/
├── README.md                    # This file (quick reference)
├── RULES_GUIDE.md              # Complete guide (200+ lines)
└── templates/                  # Rule templates by category
    ├── core/                   # Core programming rules
    ├── architecture/           # System design patterns
    ├── languages/              # Language-specific standards
    ├── frontend/               # UI/UX development rules
    ├── backend/                # Server-side patterns
    ├── infrastructure/         # DevOps and deployment
    └── development/            # Development workflow
```

## Rule Categories

### 1. Core (Essential)
**Path**: `templates/core/`
**Focus**: Fundamental programming principles applicable to all projects

**Examples**: Error handling, logging, code organization, naming conventions

---

### 2. Architecture (System Design)
**Path**: `templates/architecture/`
**Focus**: System design patterns and architectural principles

**Examples**: Clean architecture, dependency injection, module boundaries, API design

---

### 3. Languages (Tech-Specific)
**Path**: `templates/languages/`
**Focus**: Language-specific standards and idioms

**Examples**: TypeScript best practices, Rust patterns, Python conventions

---

### 4. Frontend (UI/UX)
**Path**: `templates/frontend/`
**Focus**: Frontend development standards

**Examples**: React patterns, state management, component design, accessibility

---

### 5. Backend (Server-Side)
**Path**: `templates/backend/`
**Focus**: Server-side development patterns

**Examples**: API endpoints, database access, authentication, caching

---

### 6. Infrastructure (DevOps)
**Path**: `templates/infrastructure/`
**Focus**: Deployment and operations standards

**Examples**: Docker configuration, CI/CD pipelines, monitoring, security

---

### 7. Development (Workflow)
**Path**: `templates/development/`
**Focus**: Development process and tooling

**Examples**: Git workflow, testing strategy, code review, documentation

---

## Quick Usage

### For AI Assistants
Read the complete guide for rule generation and management:
```markdown
1. Read RULES_GUIDE.md for full instructions
2. Use manage-docs skill to generate rules
3. Apply profile filtering automatically
```

### For Developers
Browse templates to understand project standards:
```bash
# View all rules in a category
ls templates/core/

# Read a specific rule template
cat templates/architecture/clean-architecture.md
```

## Profile System

Rules adapt to your project profile:

| Profile | Rule Count | Categories |
|---------|-----------|------------|
| **tauri** | 23 rules | Core + Architecture + Rust + Frontend + Infrastructure |
| **nextjs-aws** | 30 rules | Core + Architecture + TypeScript + Frontend + Backend + AWS |

**Note**: Core and Architecture rules apply to all profiles. Additional rules added based on tech stack.

## Related Documentation

- **[RULES_GUIDE.md](RULES_GUIDE.md)** - Complete guide (200+ lines)
- **Framework Rules**: `framework/.claude-template/rules/` (generated output)
- **ADR-013**: Architecture decision for template-based system

---

**Last Updated**: 2026-03-26
**Version**: 1.0.0
**Maintained By**: AI Development Framework Team
