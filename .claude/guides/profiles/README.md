# Project Profiles

Profile-aware configuration system for tech-stack-specific settings.

## Overview

Profiles define project configuration including active Pillars, rules, tech stack, and documentation structure. They enable the framework to adapt to different tech stacks (desktop, web, hybrid) automatically.

**What profiles contain:**
- **Active Pillars** (4-7 from 18 total) - Core architectural standards
- **Rules configuration** (23-43 rules) - Tech-stack-specific patterns
- **Tech stack metadata** - Frontend, backend, infrastructure details
- **Documentation structure** - Profile-specific doc templates

## Available Profiles

| Profile | Stack | Pillars | Rules | Use Case |
|---------|-------|---------|-------|----------|
| **tauri** | Rust + React | 4 (A, B, K, L) | 23 | Desktop apps (local-first) |
| **nextjs-aws** | Next.js + AWS | 15 (A-E, G-K, M, N, Q, R) | 43 | Web apps (cloud-native, full-stack) |
| **tauri-aws** | Rust + React + AWS | 7 (A, B, K, L, M, Q, R) | 30 | Desktop + cloud hybrid |

### Tauri Profile

**Best for**: Desktop applications with local-first architecture

**Tech Stack**:
- Frontend: React + TypeScript
- Backend: Rust (Tauri)
- Desktop: Tauri APIs
- State: Zustand

**Key Pillars**:
- **A** (Nominal Typing) - Type-safe IDs and values
- **B** (Airlock) - Schema validation at boundaries
- **K** (Testing) - Test pyramid with Vitest
- **L** (Headless) - UI decoupled from business logic

### Next.js + AWS Profile

**Best for**: Full-stack web applications with serverless backend

**Tech Stack**:
- Frontend: Next.js 15 + React + TypeScript
- Backend: AWS Lambda + Node.js
- Infrastructure: AWS CDK + Vercel
- Database: DynamoDB

**Key Pillars**:
- All Tauri pillars (A, B, K, L)
- **M** (Saga) - Distributed transaction compensation
- **Q** (Idempotency) - Safe retry logic
- **R** (Observability) - Structured logging and tracing
- Plus: C, D, E, G, H, I, J, N

### Tauri + AWS Profile

**Best for**: Hybrid desktop applications with cloud backend

**Tech Stack**:
- Frontend: Tauri + React + TypeScript
- Backend: AWS Lambda + TypeScript
- Desktop: Rust + Tauri APIs
- Infrastructure: AWS CDK

**Key Pillars**:
- Desktop: A, B, K, L (from Tauri)
- Cloud: M, Q, R (from Next.js + AWS)

## Activation

### During Project Initialization

```bash
# Auto-activates profile during init
python3 scripts/init-project.py --profile=tauri --name=my-app

# Creates docs/project-profile.md automatically
```

**What happens**:
1. Framework syncs profiles to `.claude/guides/profiles/`
2. Init script copies selected profile to `docs/project-profile.md`
3. All manage-* skills read from this single source of truth

### Change Profile After Init

```bash
# Interactive profile selection
/manage-project --select-profile

# List available profiles
/manage-project --list-profiles

# Show current active profile
/manage-project --show-profile
```

## Usage by Skills

All manage-* skills read from `docs/project-profile.md` as the single source of truth:

| Skill | What It Reads | Purpose |
|-------|---------------|---------|
| **/manage-rules** | `rules.include` array | Filters rules based on profile whitelist |
| **/manage-adrs** | `pillars` array | References active pillars in ADRs |
| **/manage-claude-md** | Metadata fields | Updates CLAUDE.md project info |
| **/manage-docs** | Documentation structure | Generates profile-specific docs |

**Key benefit**: Single configuration file (`docs/project-profile.md`) instead of multiple scattered configs.

## File Format

Profiles use Markdown with YAML frontmatter:

```markdown
---
name: tauri
description: Desktop application (Tauri + React, local-first)
category: desktop
version: 1.0.0
---

# Tauri Profile

## Overview

Desktop application (Tauri + React, local-first)

## Pillars

- **A** (Nominal Typing)
- **B** (Airlock)
- **K** (Testing)
- **L** (Headless)

## Rules Configuration

```yaml
rules:
  - workflow
  - naming
  - debugging
  - clean-architecture
  - typescript-strict
  - design-system
  - tauri-stack
  - ... (23 total)
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React + TypeScript |
| **Backend** | Rust (Tauri) |
| **Desktop** | Tauri |
| **State** | Zustand |
| **Build** | Vite |

## Use Cases

Best suited for desktop applications with Tauri stack. Optimized for local-first architecture with offline capabilities.
```

## File Locations

| Location | Purpose | Synced By |
|----------|---------|-----------|
| `.claude/guides/profiles/*.md` | Profile templates (3 files) | `/update-guides` |
| `docs/project-profile.md` | Active profile (single source of truth) | `/manage-project` |

**Why two locations?**
- `profiles/` = templates (synced from framework)
- `project-profile.md` = activated config (copied from template)

This allows switching profiles without re-syncing framework.

## Workflow

### Initial Setup (Framework Developer)

```bash
# 1. Create profile in framework
vim framework/.claude/guides/profiles/new-profile.md

# 2. Test locally
python3 scripts/init-project.py --profile=new-profile --name=test-project

# 3. Verify activation
cat test-project/docs/project-profile.md
```

### Project Initialization (Framework User)

```bash
# 1. Initialize project with profile
python3 scripts/init-project.py --profile=tauri --name=my-app

# 2. Verify active profile
cd my-app
/manage-project --show-profile

# 3. Generate rules from profile
/manage-rules --instant
```

### Profile Switch (During Development)

```bash
# 1. List available profiles
/manage-project --list-profiles

# 2. Select new profile
/manage-project --select-profile
# (Choose profile interactively)

# 3. Regenerate rules for new profile
/manage-rules --instant

# 4. Update CLAUDE.md if needed
/manage-claude-md --instant
```

## Best Practices

1. **Choose profile during init** - Profiles affect Pillars, rules, and documentation
2. **Use /update-guides regularly** - Keeps profile templates up-to-date
3. **Document profile switches** - Note in git commit when changing profiles
4. **Regenerate rules after switch** - Run `/manage-rules --instant`
5. **Test after profile change** - Verify no breaking changes

## Creating Custom Profiles

### Step 1: Create Profile File

```bash
# In framework
vim .claude/guides/profiles/custom.md
```

### Step 2: Define Profile Content

```markdown
---
name: custom
description: Custom profile description
category: custom
version: 1.0.0
---

# Custom Profile

## Pillars
- **A**
- **B**
- **K**

## Rules Configuration
```yaml
rules:
  - workflow
  - naming
  - custom-rule-1
  - custom-rule-2
```

## Tech Stack
...
```

### Step 3: Test Profile

```bash
# Test initialization
python3 scripts/init-project.py --profile=custom --name=test-custom

# Verify rules generated
ls test-custom/.claude/rules/
```

### Step 4: Sync to Projects

```bash
# In target project
/update-guides ~/dev/ai-dev

# Activate custom profile
/manage-project --select-profile
# (Choose "custom")
```

## Troubleshooting

### Profile Not Found

```
❌ Profile not found: .claude/guides/profiles/tauri.md

Fix: Run /update-guides to sync profiles from framework
```

**Solution**: Profiles are synced via `/update-guides`, not stored in projects by default.

### Invalid YAML Frontmatter

```
❌ Failed to parse profile: invalid YAML

Fix: Check YAML syntax in profile file
```

**Solution**: Ensure frontmatter has valid YAML (name, description, category, version required).

### Rules Not Generated

```
❌ /manage-rules failed: profile not activated

Fix: Activate profile first with /manage-project
```

**Solution**: Run `/manage-project --select-profile` before `/manage-rules`.

## Migration Guide

### From docs/project-profile.md to docs/project-profile.md

**Old approach** (pre-v3.0.0):
```
docs/project-profile.md (profile: tauri)
.claude/profiles/tauri.json
```

**New approach** (v3.0.0+):
```
docs/project-profile.md (single source of truth)
.claude/guides/profiles/tauri.md (template)
```

**Migration steps**:
1. Run `/update-guides` to sync profiles
2. Run `/manage-project --select-profile` to activate
3. Remove `docs/project-profile.md` (optional, backward compatible)

### From Multiple Config Files

**Old**:
```
docs/project-profile.md
.claude/framework-config.json
```

**New**:
```
docs/project-profile.md (single file)
```

**Benefits**:
- Single source of truth
- Simpler to maintain
- Easier to switch profiles
- No framework directory dependency

## Related Documentation

- [init-project.py](../../scripts/init-project.py) - Profile activation during init
- [/manage-project](../../.claude/skills/manage-project/SKILL.md) - Profile selection skill
- [/manage-rules](../../.claude/skills/manage-rules/SKILL.md) - Rule generation from profile
- [/update-guides](../../.claude/skills/update-guides/SKILL.md) - Profile sync from framework

---

**Version**: 1.0.0
**Last Updated**: 2026-03-27
**Related Issue**: #370 (Simplify profile management)
