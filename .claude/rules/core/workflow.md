---
paths:
  - .claude/plans/active/
  - .claude/MEMORY.md
---

# Workflow Rule

> 📖 **Complete Guide**: [workflow/MAIN.md](../../workflow/MAIN.md)
> 📋 **Planning System**: [workflow/Phase-B-Planning.md](../../workflow/Phase-B-Planning.md)

This rule provides quick checks for maintaining proper workflow discipline. For comprehensive workflow guidance, see the complete documentation above.

---

## Quick Check - Branch Management

Before starting ANY code changes, verify:

- [ ] **NOT** on `development` or `master` branch
- [ ] Branch name follows convention: `feature/#XXX-description`, `bugfix/#XXX-description`, or `hotfix/#XXX-description`
- [ ] Branch created from latest `development` or `main`

**Commands:**
```bash
# Check current branch
git branch --show-current

# Create feature branch (if needed)
git checkout main
git pull origin main
git checkout -b feature/XXX-description
```

**Why?** Feature branches enable safe experimentation, easy rollback, clean history, and parallel development.

---

## Quick Check - Issue Tracking

For every Issue being worked on, verify:

- [ ] Issue has corresponding plan file: `.claude/plans/active/#XXX.md`
- [ ] Plan file has clear steps with checkboxes
- [ ] Current step is marked with `←` indicator
- [ ] Progress is updated in real-time

**Plan file structure:**
```markdown
---
issue: XXX
status: in-progress
---

# Issue #XXX: Title

### Steps
- [x] Completed step
- [ ] **In progress** ← Current
- [ ] Next step
```

**Template**: `workflow/templates/TEMPLATE-feature-plan.md`

---

## Quick Check - PR Target Branch

Before creating or submitting a Pull Request, verify:

- [ ] PR **targets** `development` branch (NOT `master`)
- [ ] PR **source** is `feature/XXX-*` or `bugfix/XXX-*`
- [ ] PR title matches Issue title
- [ ] PR description includes `Closes #XXX`

**Correct command:**
```bash
# ✅ CORRECT - Target development
gh pr create --base development --head feature/XXX-description

# ❌ WRONG - Never target master directly
gh pr create --base master --head feature/XXX-description
```

**Why target development?**
- Master only receives stable, tested code from development
- Integration testing happens in development first
- Master always represents last known good state
- Workflow: `feature → development → master → production`

---

## Quick Check - Branch Cleanup

After an Issue is closed and merged, verify:

- [ ] Feature branch deleted locally: `git branch -d feature/XXX-*`
- [ ] Feature branch deleted on GitHub: `git push origin --delete feature/XXX-*`
- [ ] Stale branches cleaned: `git branch -v | grep "gone" | awk '{print $1}' | xargs git branch -d`
- [ ] Plan file archived: `plans/active/#XXX.md` → `plans/archive/`

**Why clean up?**
- Prevents branch clutter (only active work visible)
- Clear development history
- Easier session resumption with `*resume`
- Better PR hygiene (one branch = one PR = one Issue)

---

## Issue Plans - Tactics Layer

When working on an Issue, use `.claude/plans/active/#XXX.md` to track progress:

**Key principles:**
- One GitHub Issue = one plan file
- Copy tasks from Feature Plan to plan file
- Update progress in real-time (check boxes)
- Archive plan when Issue is complete
- Create ADR for important architectural decisions

**Workflow:**
1. Pick an Issue: `*issue pick XXX`
2. Create/update plan file: `.claude/plans/active/#XXX.md`
3. Mark tasks as complete during development
4. Close Issue when done: `*issue close XXX`
5. Archive plan: `mv plans/active/#XXX.md plans/archive/`

---

## Three-Layer Architecture

The framework uses a hierarchical planning system:

```
Strategy Layer: MVP Planning (40 min)
    ↓
Campaign Layer: GitHub Issues (1-2h per feature)
    ↓
Tactics Layer: Issue Plans (real-time tracking)
```

**See**:
- [workflow/MAIN.md](../../workflow/MAIN.md) - Complete overview
- [workflow/Phase-B-Planning.md](../../workflow/Phase-B-Planning.md) - Two-step planning system

---

## Core Commands

- `*next` - Get next task from active plan
- `*issue pick <n>` - Start working on Issue #n
- `*issue close <n>` - Complete Issue #n
- `*plan` - Create MVP or feature plan
- `*review` - Run code review

**Full command list**: See [commands/](../../commands/) directory

---

## AI Workflow Phases

### Phase A: Documentation
Define what to build (MVP goals, acceptance criteria)

### Phase B: Planning
- **Step 1**: MVP-level decomposition (40 min) → GitHub Issues
- **Step 2**: Feature-level planning (1-2h) → Dev Plan + Test Cases

### Phase C: Development
- Pick Issue
- Create plan file
- Execute and track progress
- Close Issue and archive plan

### Phase D: Release
- Merge to development
- Integration testing
- Deploy to production
- Verify release

**See**: [workflow/MAIN.md](../../workflow/MAIN.md) for complete workflow guide

---

## Best Practices

### Single Source of Truth
- Technical details live in GitHub Issues
- MVP files are indexes, not duplicates
- Plan files are temporary (archive when done)

### Minimal Maintenance
- Update progress in plan files only
- Close Issues when complete (GitHub records timestamps)
- Archive important decisions to ADRs or MEMORY.md

### Clean Git History
- One Issue = one feature branch
- Clear commit messages with Issue references (#XXX)
- Delete branches after merge

---

## Related Documentation

- **[workflow/MAIN.md](../../workflow/MAIN.md)** - Complete workflow overview
- **[workflow/Phase-B-Planning.md](../../workflow/Phase-B-Planning.md)** - Two-step planning system
- **[workflow/MAIN.md#strategy-layer-mvp-planning-40-minutes](../../workflow/MAIN.md#strategy-layer-mvp-planning-40-minutes)** - MVP decomposition guide
- **[workflow/MAIN.md#campaign-layer-feature-planning-1-2-hours-per-feature](../../workflow/MAIN.md#campaign-layer-feature-planning-1-2-hours-per-feature)** - Feature planning guide
- **[commands/next.md](../../commands/next.md)** - `*next` command details
- **[commands/issue.md](../../commands/issue.md)** - Issue management commands

---

## Paths Trigger

This rule is automatically loaded when working with:
- `.claude/plans/active/` directory
- `.claude/MEMORY.md` file
- Starting a new development session
- Planning a new MVP or feature
