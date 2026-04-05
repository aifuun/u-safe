---
name: manage-adrs
description: |
  Manage Architecture Decision Records (ADRs) with profile-aware templates.

  TRIGGER when: User wants to create an ADR ("create adr", "manage adrs", "record decision"), list ADRs, show a specific ADR, or validate ADR format.

  DO NOT TRIGGER when: User is just asking about existing ADRs conceptually, viewing ADR documentation, or discussing decisions without creating/modifying ADRs.
version: "2.0.0"
argument-hint: "create <title> | list | show <number> | validate <number>"
allowed-tools: Read, Glob, Grep, Write, Edit, Bash
disable-model-invocation: false
user-invocable: true
---

# manage-adrs - ADR Management (Profile-Aware)

**Migrated from**: `/adr` v1.1.0

## What Changed

- ✅ **Renamed**: `adr` → `manage-adrs` (unified manage-* naming)
- ✅ **Profile Integration**: Reads `docs/project-profile.md` for pillars
- ✅ **Template Customization**: ADR templates adapt based on active pillars
- ✅ **Error Handling**: Graceful handling of missing configuration

## Purpose

Profile-aware ADR management with automatic template customization based on project pillars.

**Why This Skill Exists**:
- ✅ Ensures consistent ADR formatting across the project
- ✅ Automates mechanical tasks (numbering, indexing, metadata)
- ✅ **NEW**: Customizes ADR templates based on project pillars
- ✅ **NEW**: Validates profile configuration before operations
- ✅ Reduces human error (duplicate numbers, missing index updates)

---

## Usage

```bash
/manage-adrs create "<title>"       # Create new ADR with auto-assigned number
/manage-adrs list                   # List all ADRs with status
/manage-adrs show <number>          # Show ADR summary
/manage-adrs validate <number>      # Validate ADR completeness
```

---

## Profile Integration

**Reads from** `docs/project-profile.md`:

```yaml
---
name: tauri
pillars: [A, B, K, L]
---
```

**Template customization based on pillars**:

| Pillar | Section Added to Template |
|--------|---------------------------|
| **A** (Nominal Typing) | "Type Safety" section with branded type considerations |
| **B** (Schema Validation) | "Validation Strategy" section |
| **K** (Result Type) | "Error Handling" section with Result<T, E> patterns |
| **L** (Headless UI) | "UI Pattern" section for component decisions |
| **M** (Saga Pattern) | "Compensation Logic" section |
| **Q** (Idempotency) | "Idempotency" section for API decisions |
| **R** (Logging) | "Observability" section |

**Example**: If profile has pillars `[A, K, L]`, ADR template includes:
- Type Safety section (Pillar A)
- Error Handling section (Pillar K)
- UI Pattern section (Pillar L)

---

## Error Handling

All operations include graceful error handling:

### 1. Missing Project Profile

```bash
if [ ! -f "docs/project-profile.md" ]; then
  echo "❌ Error: Project profile not configured"
  echo "Please run: /manage-claude-md --configure-profile --select-profile"
  exit 1
fi
```

### 2. Invalid YAML Syntax

```bash
# Validate YAML before reading
if ! python3 -c "import yaml; yaml.safe_load(open('docs/project-profile.md'))" 2>/dev/null; then
  echo "❌ Error: Invalid YAML syntax in project-profile.md"
  exit 1
fi
```

### 3. Missing Pillars Field

```bash
# Graceful degradation if pillars not specified
pillars=$(grep "pillars:" docs/project-profile.md | sed 's/.*: \[//' | sed 's/\]//')

if [ -z "$pillars" ]; then
  echo "⚠️  Warning: No pillars specified in profile"
  echo "Using standard template without pillar-specific sections"
  # Continue with default template
fi
```

### 4. File I/O Errors

```bash
# Check write permissions before creating ADR
if [ ! -w "docs/ADRs/" ]; then
  echo "❌ Error: No write permission for docs/ADRs/ directory"
  echo "Check permissions: ls -la docs/ADRs/"
  exit 1
fi
```

---

## Commands

### 1. Create ADR

**Command**: `/manage-adrs create "Title of Decision"`

**What It Does**:
1. **Validate profile**: Check `docs/project-profile.md` exists and is valid
2. **Read pillars**: Extract pillars list from profile
3. **Auto-assign number**: Scans `docs/ADRs/` to find next sequential number
4. **Customize template**: Add pillar-specific sections to TEMPLATE.md
5. **Create file**: `docs/ADRs/{number}-{kebab-case-title}.md`
6. **Auto-fill metadata**: Number, Date, Author, Status
7. **Update index**: Add entry to `docs/ADRs/README.md` table
8. **Update checklist**: Add entry to `docs/ADRs/CHECKLIST.md`
9. **Return**: File path + pillar-specific guidance

**Example**:
```bash
User: /manage-adrs create "Use Zustand Vanilla Stores"

AI Response:
✅ Loaded profile: tauri (pillars: A, B, K, L)
✅ Created ADR-010: docs/ADRs/010-use-zustand-vanilla-stores.md
✅ Added pillar-specific sections:
   - Type Safety (Pillar A)
   - Error Handling (Pillar K)
   - UI Pattern (Pillar L)
✅ Updated index in docs/ADRs/README.md
✅ Updated checklist in docs/ADRs/CHECKLIST.md

Next steps:
1. Fill in Context section (why this decision?)
2. Document Decision details
3. **Type Safety**: How does this affect nominal types? (Pillar A)
4. **Error Handling**: What Result<T, E> patterns apply? (Pillar K)
5. **UI Pattern**: How does this work with headless components? (Pillar L)
6. List at least 2 Alternatives Considered
7. Add Consequences (positive + negative)
8. Change Status to "Accepted" when ready
```

**Workflow**:
1. **Validate profile** (Step 0):
   ```bash
   if [ ! -f "docs/project-profile.md" ]; then
     echo "❌ Error: Project profile not configured"
     echo "Run: /manage-claude-md --configure-profile --select-profile"
     exit 1
   fi
   ```

2. **Read pillars**:
   ```bash
   # Extract pillars from YAML frontmatter
   pillars=$(sed -n '/^---$/,/^---$/p' docs/project-profile.md | grep "pillars:" | sed 's/.*: \[//' | sed 's/\]//')
   echo "📋 Active pillars: $pillars"
   ```

3. **Read ADR standards** (from `.claude/guides/ADR_GUIDE.md`):
   - Standard structure requirements
   - YAML field requirements
   - Required sections
   - Length limits

4. **Find next ADR number** (scan `docs/ADRs/[0-9]*.md`)

5. **Convert title to kebab-case**

6. **Read base template**: `docs/ADRs/TEMPLATE.md`

7. **Customize template based on pillars**:
   ```bash
   # Add sections dynamically based on active pillars
   if [[ "$pillars" == *"A"* ]]; then
     add_section "## Type Safety (Pillar A)"
   fi
   if [[ "$pillars" == *"K"* ]]; then
     add_section "## Error Handling (Pillar K)"
   fi
   # ... for each active pillar
   ```

8. **Replace placeholders** in template

9. **Write to** `docs/ADRs/{number}-{kebab-title}.md`

10. **Update index** (`docs/ADRs/README.md`)

11. **Update checklist** (`docs/ADRs/CHECKLIST.md`)

12. **Quality check** (validate against ADR_GUIDE.md)

13. **Present file path and pillar-specific guidance**

---

### 2. List ADRs

**Command**: `/manage-adrs list`

Same as `/adr list` - no changes needed.

---

### 3. Show ADR

**Command**: `/manage-adrs show <number>`

Same as `/adr show` - no changes needed.

---

### 4. Validate ADR

**Command**: `/manage-adrs validate <number>`

**Enhanced validation** includes pillar-specific checks:

```bash
# Standard validation (from /adr)
- [ ] Context section not empty
- [ ] Decision has details
- [ ] At least 2 alternatives
- [ ] Consequences (positive + negative)

# NEW: Pillar-specific validation
if [[ "$pillars" == *"A"* ]]; then
  - [ ] Type Safety section addressed
fi
if [[ "$pillars" == *"K"* ]]; then
  - [ ] Error handling strategy documented
fi
# ... for each active pillar
```

---

## Template Customization Details

### Pillar Section Templates

**Pillar A (Nominal Typing)**:
```markdown
## Type Safety (Pillar A)

**Branded Types Affected**: [List types]

**Type Safety Considerations**:
- How does this decision affect nominal typing?
- Are new branded types needed?
- Does this maintain compile-time type safety?

**Implementation**:
```typescript
// Example branded type usage
type UserId = Brand<string, "UserId">;
```
```

**Pillar K (Result Type)**:
```markdown
## Error Handling (Pillar K)

**Error Scenarios**: [List expected errors]

**Result Type Strategy**:
- How does this decision handle failures?
- What Result<T, E> patterns apply?
- Are error types properly branded?

**Implementation**:
```typescript
// Example Result type usage
function operation(): Result<Data, OperationError> {
  // ...
}
```
```

**Pillar L (Headless UI)**:
```markdown
## UI Pattern (Pillar L)

**Component Architecture**: [Describe pattern]

**Headless Pattern Considerations**:
- How does this work with headless components?
- Are UI hooks separated from logic?
- Is the component testable without DOM?

**Implementation**:
```typescript
// Example headless hook
function useComponentLogic() {
  // Business logic only
}
```
```

*(Similar templates for M, Q, R pillars)*

---

## Migration from /adr

**Old command** → **New command**:
```bash
/adr create "Title"        → /manage-adrs create "Title"
/adr list                  → /manage-adrs list
/adr show 009              → /manage-adrs show 009
/adr validate 009          → /manage-adrs validate 009
```

**What's backward compatible**:
- ✅ All ADR files (no changes needed)
- ✅ Index and checklist format
- ✅ Command arguments

**What's new**:
- ✅ Profile-aware template customization
- ✅ Pillar-specific guidance
- ✅ Error handling for missing config

---

## Best Practices

### When to Create an ADR

Same criteria as `/adr` skill:
- ✅ Architectural decisions
- ✅ Technology choices
- ✅ Coding standards
- ✅ Process definitions

### ADR Lifecycle

Same as `/adr` skill:
1. Proposed → 2. Accepted → 3. Deprecated → 4. Superseded

---

## Integration with Workflow

### Reference ADRs in Code

```typescript
// Following ADR-009: Zustand Vanilla Store Pattern (Pillar L)
// Headless pattern: logic separated from UI
import { createStore } from 'zustand/vanilla';

export const taskStore = createStore<TaskStore>()((set, get) => ({
  // Implementation per ADR-009
}));
```

### Link ADRs in PRs

Same as `/adr` skill.

---

## Quick Reference

```bash
# Create ADR (profile-aware)
/manage-adrs create "Your Decision Title"

# List all ADRs
/manage-adrs list

# Show specific ADR
/manage-adrs show 009

# Validate ADR (with pillar checks)
/manage-adrs validate 009
```

---

## Related Documentation

- [ADR Template](../../docs/ADRs/TEMPLATE.md) - Base template
- [ADR Guide](../../.claude/guides/ADR_GUIDE.md) - Standards
- [ADR Index](../../docs/ADRs/README.md) - All ADRs
- [Project Profile](../../docs/project-profile.md) - Pillar configuration

---

## Notes for Claude

When user invokes `/manage-adrs create`:

1. **ALWAYS validate profile first**:
   - Check `docs/project-profile.md` exists
   - Validate YAML syntax
   - Extract pillars list
   - Show error if profile missing

2. **Customize template based on pillars**:
   - Add pillar-specific sections
   - Provide pillar-specific guidance
   - Validate pillar-specific requirements

3. **Graceful degradation**:
   - If no pillars specified → use standard template
   - If pillar not recognized → skip that section
   - Always continue operation with warnings

4. **Logging**:
   ```bash
   LOG_FILE=".claude/logs/manage-adrs-$(date +%Y%m%d).log"
   echo "[$(date)] Created ADR-010 with pillars: A, K, L" >> "$LOG_FILE"
   ```

---

**Version:** 2.0.0
**Pattern:** Profile-Aware Management Skill
**Last Updated:** 2026-03-27
**Changelog:**
- v2.0.0 (2026-03-27): Renamed from /adr, added profile integration and error handling
- v1.1.0 (2026-03-04): Legacy version (before rename)
- v1.0.0 (2026-03-04): Initial /adr release
