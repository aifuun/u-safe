# init-docs Skill

Auto-generate standard documentation structure for projects.

## Quick Start

```bash
/init-docs                    # Auto-detect profile
/init-docs --profile tauri    # Specify profile
/init-docs --dry-run          # Preview
```

## What It Does

Creates a complete documentation structure with:
- Standard directories (ADRs, architecture, api, guides, diagrams)
- Template files (README, PRD, ARCHITECTURE, SCHEMA, API, SETUP, TEST_PLAN, DEPLOYMENT)
- Profile-specific customization (tauri, tauri-aws, nextjs-aws)
- Variable substitution (projectName, profile, techStack)

## Files

- `SKILL.md` - Complete skill documentation (read this for full details)

## Dependencies

- Requires: `.framework-install` (for profile auto-detection)
- Requires: `framework/.prot-template/docs-templates/` (template source - from issue #224)
- Works with: `/check-docs` (validation counterpart)

## Status

- **Version:** 1.0.0
- **Pattern:** Tool-Reference
- **Compliance:** ADR-001 ✅
- **Created:** 2026-03-15
