# Architecture Decision Records (ADRs)

## Overview

This directory contains Architecture Decision Records (ADRs) for U-Safe. ADRs document important architectural decisions, their context, alternatives considered, and consequences.

## ADR Index

| # | Title | Status | Date |
|---|-------|--------|------|
| [001](./001-design-token-system-css-variables.md) | Design Token System with CSS Variables | Accepted | 2026-03-12 |

**Total ADRs**: 1
**Last Updated**: 2026-03-12

## Status Definitions

- **Proposed**: Under discussion, not yet implemented
- **Accepted**: Decision approved and being implemented
- **Deprecated**: No longer recommended, kept for historical context
- **Superseded**: Replaced by a newer ADR (link provided)

## How to Use ADRs

### Creating a New ADR

Use the `/adr` skill:

```bash
/adr create "Your Decision Title"
```

Or manually:
1. Copy `TEMPLATE.md`
2. Assign next sequential number (002, 003, etc.)
3. Fill in all sections
4. Update this README index
5. Submit for review

### Referencing ADRs

In code:
```typescript
// Following ADR-001: Design Token System
import './styles.css'; // Contains CSS variables
```

In pull requests:
```markdown
## References
- Implements [ADR-001: Design Token System](../docs/ADRs/001-design-token-system-css-variables.md)
```

### ADR Lifecycle

1. **Proposed** → Draft, under discussion
2. **Accepted** → Implemented and active
3. **Deprecated** → No longer recommended (with reason)
4. **Superseded** → Replaced by newer ADR (with link)

## Best Practices

### When to Create an ADR

✅ **Do create ADR for:**
- Architectural patterns (layers, boundaries)
- Technology choices (libraries, frameworks)
- Coding standards (TypeScript strict mode)
- Design systems (tokens, components)
- Infrastructure decisions (deployment, CI/CD)

❌ **Don't create ADR for:**
- Implementation details within a module
- Temporary experiments
- Easily reversible choices
- Personal preferences

### ADR Quality Checklist

Before marking as "Accepted":

- [ ] Context explains the problem clearly
- [ ] Decision section has implementation details
- [ ] At least 2 alternatives documented
- [ ] Consequences include both positive AND negative
- [ ] References section complete
- [ ] Reviewed by team

## Related Documentation

- [ADR Template](./TEMPLATE.md) - Template for new ADRs
- [ADR Skill](../../.claude/skills/adr/) - Automated ADR management
- [Design System Specification](../spec/UI_UX_Design_System.md) - Implementation of ADR-001

---

**Maintained by**: Engineering Team
**Process Owner**: Technical Lead
