---
name: tidy
description: |
  Clean up and organize project files, memory, and documentation.
  Archive completed plans, remove clutter, optimize space.
allowed-tools: Read, Glob, Bash(find *), Bash(mv *), Bash(rm *)
---

# Project Tidykeeper

Clean up project files and memory for long-term sustainability.

## Task

Identify and archive:
1. **Completed plans** - Move from `/active/` to `/archive/`
2. **Old code** - Identify unused files (with confirmation)
3. **Memory bloat** - Archive old notes and MEMORY.md entries
4. **Documentation** - Clean up outdated docs
5. **Dependencies** - Identify unused packages

## Cleanup Areas

### Plans
```
.claude/plans/active/
  ├── completed-feature.md    ← Move to archive/
  ├── old-refactor.md         ← Move to archive/
  └── current-feature.md      ← Keep
```

### Code
```
src/
  ├── old-implementation.ts   ← Identify for removal
  ├── unused-util.ts          ← Identify for removal
  └── current-code.ts         ← Keep
```

### Memory
```
.claude/
  MEMORY.md (5000+ lines)     ← Archive old sections
  plans/archive/              ← Store old plans
```

### Documentation
```
docs/
  ├── outdated-api-spec.md    ← Archive
  ├── old-deployment-guide.md ← Archive
  └── current-readme.md       ← Keep
```

## Output

```markdown
# Project Cleanup Report

## Summary
- Plans archived: 3
- Code files identified: 2
- Memory cleaned: 1200 lines removed
- Docs archived: 4

## Breakdown

### Completed Plans Archived
- [ ] feature-authentication.md → archive/
- [ ] fix-database-schema.md → archive/
- [ ] update-dependencies.md → archive/

### Unused Code Files (needs confirmation)
- src/old-auth-system.ts (1200 lines, no imports)
- src/unused-utils.ts (300 lines, no imports)

Confirm removal? Y/N

### Memory Cleaned
- Removed 1200 lines of old notes
- Archived sections:
  - "2026-01 Architecture decisions" → archive/
  - "Old debugging notes" → archive/

### Documentation Archived
- docs/api-v1-deprecated.md
- docs/old-deployment.md

## Space Saved
- Plans: 45 KB
- Docs: 120 KB
- Code: 1.5 MB (if confirmed)
- Total: ~1.7 MB

## Recommendations
1. Confirm deletion of unused code (run: `tidy confirm`)
2. Review archived plans monthly
3. Keep MEMORY.md under 3000 lines
```

---

This skill helps maintain:
- Clean project structure
- Efficient long-term work
- Clear active vs. completed tasks
- Manageable file sizes
