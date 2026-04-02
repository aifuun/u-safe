# Rules Mapping - Framework to Templates Migration

> Metadata for migrating 51 rules from `framework/.claude-template/rules/` to `.claude/guides/rules/templates/`

## Overview

This file contains complete metadata for all rules to enable:
- YAML frontmatter generation
- Category-based organization
- Profile-aware filtering (tauri: 23 rules, nextjs-aws: 44 rules)
- Pillar cross-references

## Rules Mapping Table

| # | Rule File | Category | Stack Tags | Profiles | Pillar Refs | Notes |
|---|-----------|----------|------------|----------|-------------|-------|
| 1 | workflow.md | core | typescript,react,rust | tauri,nextjs-aws,minimal | K | Core workflow patterns |
| 2 | naming.md | core | typescript,react,rust | tauri,nextjs-aws,minimal | - | Product name separation |
| 3 | debugging.md | core | typescript,react,rust | tauri,nextjs-aws,minimal | - | Debug strategies |
| 4 | docs.md | core | typescript,react,rust | tauri,nextjs-aws,minimal | - | Documentation standards |
| 5 | memory-management.md | core | typescript,react,rust | tauri,nextjs-aws,minimal | - | Memory optimization |
| 6 | memory-protection.md | core | typescript,react,rust | tauri,nextjs-aws,minimal | - | Memory safety patterns |
| 7 | planning-context.md | core | typescript,react,rust | tauri,nextjs-aws,minimal | - | Planning and context management |
| 8 | documentation-structure.md | core | typescript,react,rust | tauri,nextjs-aws,minimal | - | Doc structure standards |
| 9 | clean-architecture.md | architecture | typescript,react | tauri,nextjs-aws | L | Hexagonal architecture |
| 10 | dependency-rule.md | architecture | typescript,react | tauri,nextjs-aws | L | Dependency inversion |
| 11 | service-layer.md | architecture | typescript,react | tauri,nextjs-aws | L | Service layer patterns |
| 12 | headless.md | architecture | typescript,react | tauri,nextjs-aws | L | Headless component patterns |
| 13 | adapters.md | architecture | typescript,react | tauri,nextjs-aws | L | Adapter patterns |
| 14 | identity.md | architecture | typescript,react | tauri,nextjs-aws | A | Entity identity management |
| 15 | typescript-strict.md | languages | typescript | tauri,nextjs-aws,minimal | - | TypeScript strict mode |
| 16 | typescript-nominal-types.md | languages | typescript | tauri,nextjs-aws,minimal | A | Branded types with Zod |
| 17 | typescript-esm.md | languages | typescript | tauri,nextjs-aws,minimal | - | ESM module patterns |
| 18 | design-system.md | frontend | react,typescript | tauri,nextjs-aws | L | Component design system |
| 19 | zustand-hooks.md | frontend | react,typescript,zustand | tauri,nextjs-aws | - | Zustand hooks patterns |
| 20 | views.md | frontend | react,typescript | tauri,nextjs-aws | - | View layer organization |
| 21 | css.md | frontend | react,css | tauri,nextjs-aws | - | CSS-in-JS patterns |
| 22 | stores.md | frontend | react,typescript,zustand | tauri,nextjs-aws | - | Zustand store patterns |
| 23 | debug-panel.md | frontend | react,typescript | tauri,nextjs-aws | - | Debug UI component |
| 24 | nextjs-app-router.md | frontend | nextjs,react,typescript | nextjs-aws | - | Next.js 15 app router |
| 25 | nextjs-server-components.md | frontend | nextjs,react,typescript | nextjs-aws | - | React Server Components |
| 26 | nextjs-api-routes.md | frontend | nextjs,typescript | nextjs-aws | - | Next.js API routes |
| 27 | react-server-actions.md | frontend | nextjs,react,typescript | nextjs-aws | - | Server actions patterns |
| 28 | saga.md | backend | typescript,aws | nextjs-aws | M | Saga compensation pattern |
| 29 | lambda-typescript-esm.md | backend | typescript,aws,lambda | nextjs-aws | - | Lambda ESM setup |
| 30 | lambda-layer-deployment.md | backend | typescript,aws,lambda | nextjs-aws | - | Lambda layers |
| 31 | lambda-local-first.md | backend | typescript,aws,lambda | nextjs-aws | - | Local Lambda development |
| 32 | external-api-integrations.md | backend | typescript,aws | nextjs-aws | B | API integration patterns |
| 33 | query-transactions.md | backend | typescript,aws,dynamodb | nextjs-aws | C,M | Transaction patterns |
| 34 | cdk-deploy.md | infrastructure | typescript,aws,cdk | nextjs-aws | - | CDK deployment |
| 35 | cdk-watch-testing.md | infrastructure | typescript,aws,cdk | nextjs-aws | - | CDK watch mode |
| 36 | aws-services.md | infrastructure | typescript,aws | nextjs-aws | - | AWS service patterns |
| 37 | diagnostic-export-logging.md | infrastructure | typescript,aws,cloudwatch | nextjs-aws | R | CloudWatch logging |
| 38 | secrets.md | infrastructure | typescript,aws,secrets | tauri,nextjs-aws | - | Secrets management |
| 39 | time-handling.md | infrastructure | typescript,aws | nextjs-aws | - | Time zone handling |
| 40 | url-construction.md | infrastructure | typescript,aws | nextjs-aws | - | URL building patterns |
| 41 | lambda-quick-reference.md | infrastructure | typescript,aws,lambda | nextjs-aws | - | Lambda quick reference |
| 42 | tauri-stack.md | infrastructure | rust,tauri | tauri | - | Tauri stack setup |
| 43 | file-creation.md | development | typescript,react,rust | tauri,nextjs-aws,minimal | - | File creation conventions |
| 44 | infinite-loop-prevention.md | development | typescript,react,rust | tauri,nextjs-aws,minimal | - | Loop safety patterns |
| 45 | tauri-ipc.md | desktop | rust,tauri,typescript | tauri | - | Tauri IPC commands |
| 46 | tauri-native-apis.md | desktop | rust,tauri | tauri | - | Native API access |
| 47 | tauri-performance.md | desktop | rust,tauri | tauri | - | Performance optimization |
| 48 | tauri-security.md | desktop | rust,tauri | tauri | - | Security best practices |
| 49 | tauri-state-management.md | desktop | rust,tauri | tauri | - | Rust-side state |
| 50 | tauri-updates.md | desktop | rust,tauri | tauri | - | Auto-update system |
| 51 | tauri-window-management.md | desktop | rust,tauri | tauri | - | Window management |

## Category Summary

| Category | Count | Description |
|----------|-------|-------------|
| **core** | 8 | Universal rules (all profiles) |
| **architecture** | 6 | Clean architecture patterns |
| **languages** | 3 | TypeScript language-specific |
| **frontend** | 11 | React, Next.js, Zustand |
| **backend** | 6 | Lambda, API, transactions |
| **infrastructure** | 10 | AWS, CDK, secrets, logging |
| **development** | 2 | Dev workflows and safety |
| **desktop** | 7 | Tauri-specific patterns |
| **TOTAL** | **53** | (includes INDEX.md, README.md) |

## Profile Distribution

### Tauri Profile (23 rules)
- **core**: 8 rules (workflow, naming, debugging, docs, memory-management, memory-protection, planning-context, documentation-structure)
- **architecture**: 6 rules (clean-architecture, dependency-rule, service-layer, headless, adapters, identity)
- **languages**: 3 rules (typescript-strict, typescript-nominal-types, typescript-esm)
- **frontend**: 6 rules (design-system, zustand-hooks, views, css, stores, debug-panel)
- **infrastructure**: 2 rules (tauri-stack, secrets)
- **development**: 2 rules (file-creation, infinite-loop-prevention)
- **desktop**: 7 rules (all tauri-* rules)

**Note**: Tauri profile has 30 rules in the include list, but 7 rules don't exist yet or are excluded.

### Next.js-AWS Profile (44 rules)
- **core**: 8 rules (all core rules)
- **architecture**: 6 rules (all architecture rules)
- **languages**: 3 rules (all language rules)
- **frontend**: 11 rules (all frontend rules including Next.js-specific)
- **backend**: 6 rules (all backend rules)
- **infrastructure**: 10 rules (all infra rules except tauri-stack)
- **development**: 2 rules (all development rules)
- **desktop**: 0 rules (excluded)

**Note**: Next.js-AWS profile has 44 rules in the include list.

### Minimal Profile (13 rules)
- **core**: 8 rules (all core rules)
- **languages**: 3 rules (typescript-strict, typescript-nominal-types, typescript-esm)
- **development**: 2 rules (file-creation, infinite-loop-prevention)

## Pillar Cross-References

| Pillar | Rules Count | Rule Files |
|--------|-------------|------------|
| **A** (Nominal Types) | 2 | typescript-nominal-types, identity |
| **B** (Airlock) | 1 | external-api-integrations |
| **C** (Transaction Script) | 1 | query-transactions |
| **K** (Testing) | 1 | workflow |
| **L** (Headless) | 5 | clean-architecture, dependency-rule, service-layer, headless, adapters, design-system |
| **M** (Saga) | 2 | saga, query-transactions |
| **Q** (Idempotency) | 0 | (not yet implemented) |
| **R** (Logging) | 1 | diagnostic-export-logging |

## Migration Strategy

1. **Phase 1**: Migrate core + architecture (14 rules) - universal patterns
2. **Phase 2**: Migrate frontend (11 rules) - React/Next.js patterns
3. **Phase 3**: Migrate backend + infrastructure (16 rules) - AWS patterns
4. **Phase 4**: Migrate desktop + development (9 rules) - Tauri + dev patterns

## YAML Frontmatter Template

```yaml
---
category: {core|architecture|languages|frontend|backend|infrastructure|development|desktop}
title: "{Human-readable title}"
description: "{One-line description}"
tags: [{comma-separated stack tags}]
profiles: [{tauri,nextjs-aws,minimal}]
pillar_refs: [{A,B,C,K,L,M,Q,R}]
paths: ["**/*.{ts,tsx,rs}"]
version: "1.0.0"
last_updated: "2026-03-26"
---
```

## Notes

- **Total rules in framework**: 51 markdown files (excluding INDEX.md, README.md, QUICK_REFERENCE.md, RULE_TEMPLATE.md)
- **Profile counts**: Tauri (23), Next.js-AWS (44), Minimal (13)
- **No rules for**: Pillar Q (Idempotency) - needs separate implementation
- **Stack tags**: Used for filtering by technology (typescript, react, rust, aws, etc.)
- **Pillar refs**: Used for cross-referencing to deep-dive pillar documentation

---

**Generated**: 2026-03-27 | **For**: Issue #350 | **Part of**: ADR-013 Phase 1, Task 2
