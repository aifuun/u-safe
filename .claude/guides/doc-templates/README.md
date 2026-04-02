# Framework Guides

> Comprehensive documentation guides and templates for AI-assisted project documentation

## Overview

This directory contains modular documentation guides paired with reusable templates. Each module focuses on a specific documentation aspect (PRD, Architecture, Development, etc.) and includes:

- **`.guide` file** - Instructions for creating/updating documentation
- **`templates/` directory** - Reusable markdown templates

## Master Guide

**[MANAGE_DOCS_GUIDE.md](MANAGE_DOCS_GUIDE.md)** - Complete guide for AI to create/update documentation

This master guide provides:
- AI execution algorithms for documentation generation
- Module reference with all 6 modules
- Stack tag processing rules
- Profile-specific behavior
- Error handling strategies
- 10+ usage examples

**When to use:** See MANAGE_DOCS_GUIDE.md when implementing `/manage-docs` skill or updating documentation templates.

## Module Navigation

### 📋 Product Requirements (PRD)
**Path**: [prd/](prd/)
**Guide**: [prd.guide](prd/prd.guide)
**Templates**: [prd/templates/](prd/templates/)

Define product features, user stories, and success criteria.

---

### 🎨 Design System
**Path**: [design/](design/)
**Guide**: [design.guide](design/design.guide)
**Templates**: [design/templates/](design/templates/)

Document UI/UX standards, design tokens, components, and user flows.

**Sub-modules**:
- **Foundation** (6 templates): COLOR, TYPOGRAPHY, SPACING, RADIUS, SHADOWS, MOTION
- **Components** (4 templates): BUTTONS, FORMS, FEEDBACK, ACCESSIBILITY
- **UX** (3 templates): USER_JOURNEYS, USER_FLOWS, SCENARIOS

---

### 🏗️ Architecture
**Path**: [architecture/](architecture/)
**Guide**: [arch.guide](architecture/arch.guide)
**Templates**: [architecture/templates/](architecture/templates/)

Document system design, API contracts, and data schemas.

**Templates**:
- `ARCHITECTURE.md.template` - System architecture
- `API.md.template` - API endpoints
- `SCHEMA.md.template` - Data models

---

### 💻 Developer Documentation
**Path**: [dev/](dev/)
**Guide**: [dev.guide](dev/dev.guide)
**Templates**: [dev/templates/](dev/templates/)

Guide developers through setup, configuration, and contribution.

---

### ✅ Quality Assurance
**Path**: [qa/](qa/)
**Guide**: [qa.guide](qa/qa.guide)
**Templates**: [qa/templates/](qa/templates/)

Define testing strategy, test cases, and coverage goals.

---

### 🚀 Operations (Deployment)
**Path**: [ops/](ops/)
**Guide**: [ops.guide](ops/ops.guide)
**Templates**: [ops/templates/](ops/templates/)

Document deployment procedures, infrastructure, and monitoring.

**Note**: Only needed for projects with cloud components (nextjs-aws, tauri-aws profiles).

---

## How to Use

### For AI Assistants
1. **Read the guide** for the documentation type you need (e.g., `prd/prd.guide`)
2. **Use the template** from the corresponding `templates/` directory
3. **Follow quality standards** defined in the guide
4. **Link related docs** as specified in the guide

### For Developers
1. **Browse modules** to understand what documentation is needed
2. **Use templates** to create consistent documentation
3. **Reference guides** for writing standards and best practices

### Relationship Between .guide and .template

```
prd.guide (Instructions)          →    PRD.md.template (Structure)
  ├─ When to create                     ├─ ## Product Overview
  ├─ What to include                    ├─ ## Features
  ├─ Quality standards                  ├─ ## Success Metrics
  └─ Examples                           └─ ## Out of Scope
```

**Guide** = "How to write it"
**Template** = "What structure to use"

---

## Quick Reference

| Documentation Type | Guide | Template(s) | When to Create |
|-------------------|-------|-------------|----------------|
| Product Requirements | [prd.guide](prd/prd.guide) | PRD.md.template | Before development |
| Design System | [design.guide](design/design.guide) | 14 templates | Before frontend dev |
| Architecture | [arch.guide](architecture/arch.guide) | ARCHITECTURE, API, SCHEMA | After PRD, before dev |
| Developer Setup | [dev.guide](dev/dev.guide) | SETUP.md.template | During project init |
| QA/Testing | [qa.guide](qa/qa.guide) | TEST_PLAN.md.template | After architecture |
| Deployment | [ops.guide](ops/ops.guide) | DEPLOYMENT.md.template | Before production |

---

## Template Count

- **PRD**: 1 template
- **Design**: 14 templates (1 overview + 6 foundation + 4 components + 3 ux)
- **Architecture**: 3 templates
- **Dev**: 1 template
- **QA**: 1 template
- **Ops**: 1 template
- **Shared**: 1 template (README.md)

**Total**: 22 templates

---

## Stack Tags (Conditional Content)

Templates support **stack tags** for technology-specific content. This allows templates to include/exclude sections based on the project's tech stack.

### Syntax

```markdown
<!-- @stack: tag1, tag2 -->
Content that's only included if the project uses tag1 OR tag2
<!-- @end -->
```

### Supported Tags

- **Platforms**: `tauri`, `nextjs`, `react`, `vue`
- **Backend**: `aws`, `lambda`, `api-gateway`, `dynamodb`, `rds`, `rust`
- **Frontend**: `react`, `typescript`, `tailwindcss`, `animations`
- **Features**: `auth`, `api`, `realtime`, `offline`, `i18n`
- **Testing**: `unit`, `e2e`, `integration`
- **Deployment**: `vercel`, `cloudflare`, `github-actions`

### Examples

```markdown
<!-- @stack: aws -->
## AWS Deployment

Use AWS CDK to deploy Lambda functions...
<!-- @end -->

<!-- @stack: animations -->
## Motion Design

Animation tokens and Framer Motion setup...
<!-- @end -->
```

### How It Works

1. **Tag detection**: Automatic based on profile + project inspection
   - `tauri` profile → `['tauri', 'rust', 'desktop']`
   - `nextjs-aws` → `['nextjs', 'react', 'typescript', 'aws', 'lambda', 'dynamodb']`
   - Check `package.json` for additional tags (e.g., `framer-motion` → `animations`)

2. **Tag resolution**: OR logic (any tag matches → include content)
   - Project has `['react', 'typescript']`
   - `@stack: react, vue` → ✅ Included (react matches)
   - `@stack: vue, angular` → ❌ Excluded (no match)

3. **Processing**: `scripts/init-project.py` handles tag resolution during project initialization

### Full Guide

See [STACK_TAGS.md](STACK_TAGS.md) for complete documentation, tag list, and usage examples.

---

## Migration Notes

### From Old Structure

If you're migrating from the previous structure:

**Old locations**:
- `.claude/guides/DOCS_GUIDE.md` (monolithic guide)
- `.claude/pillars/docs-templates/` (flat template directory)

**New structure**:
- Guides split into 6 modules: `framework/guides/{prd,design,architecture,dev,qa,ops}/`
- Each module has `.guide` + `templates/` subdirectory
- Design system expanded to 14 templates (was 1)

**Backward compatibility**:
- Old templates remain in place (deprecated)
- See deprecation warnings in old locations

---

## Related Documentation

- **MANAGE_DOCS_GUIDE.md** - Master documentation management guide (Issue #4)
- **Framework README**: [../README.md](../README.md)
- **AI Guides**: [../../.claude/guides/](../../.claude/guides/)

---

**Last Updated**: 2026-03-26
**Maintained By**: AI Development Framework Team
**Version**: 1.0.0
