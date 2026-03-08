# Phase A: Documentation

> Part of the 4-Phase AI-Assisted Development Workflow
> See: [MAIN.md](./MAIN.md) for complete overview

**Load when**: Updating docs/, README, or specification documents

## When to Use

- Updating project documentation
- Writing/revising specifications
- Creating architecture documents
- API documentation updates

## Workflow

1. **Identify scope** - Which docs need update? Is it new or revision?
2. **Check source of truth** - REQUIREMENTS.md, ARCHITECTURE.md, SCHEMA.md, DESIGN.md, INTERFACES.md, README.md
3. **Update documentation** - Keep consistent with code, update headers, cross-reference related docs
4. **Verify** - Links work, examples are current, no outdated information

## Commands

| Command | Description |
|---------|-------------|
| `*sync` | Save and push changes |

## Document Creation Order

```
REQUIREMENTS.md     # 1. What to build
       │
       ▼
ARCHITECTURE.md     # 2. How to organize
       │
       ├────────────────┐
       ▼                ▼
SCHEMA.md          DESIGN.md       # 3. Data model & UI
       │                │
       └────────┬───────┘
                ▼
        INTERFACES.md              # 4. API contracts
```

**Update triggers**:
- Requirements change → cascade to others
- New entity added → SCHEMA → INTERFACES
- New screen added → DESIGN → INTERFACES
- Architecture refactor → all downstream

## Best Practices

- Update docs alongside code changes
- Keep examples executable
- Date major revisions
- Link to related docs

## Handoff to Phase B

When documentation is ready, transition to planning (Phase B):

**Checklist before Phase B**:
- [ ] REQUIREMENTS.md has user stories with acceptance criteria
- [ ] ARCHITECTURE.md defines module boundaries
- [ ] SCHEMA.md lists entities
- [ ] DESIGN.md has screen inventory

See [Phase-B-Planning.md](./Phase-B-Planning.md) for next steps.

---

**Part of**: 4-Phase Workflow (A → B → C → D)
