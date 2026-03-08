---
paths: "**/*Pattern.ts"
---
# [Rule Name]

> 📖 **Complete Guide**: `.prot/pillars/<quadrant>/<pillar>/<name>.md`
> [One-line description of what this Rule covers]

## Quick Check (30 seconds)
- [ ] [Most important pattern or requirement]
- [ ] [Common mistake to avoid]
- [ ] [Safety or correctness requirement]
- [ ] [Performance or maintainability consideration]
- [ ] [Integration or boundary concern]
- [ ] [Testing or validation requirement]
- [ ] [Optional: Additional check if needed]

## Core Pattern
```typescript
// [Language appropriate for the Rule]
// Concise, copy-paste ready code example
// Shows the "happy path" implementation
// Include comments explaining key decisions

// Example structure:
type State = { status: 'idle' | 'loading' | 'success' | 'error' };

function examplePattern() {
  // Step 1: Setup
  const [state, setState] = useState<State>({ status: 'idle' });

  // Step 2: Action
  const action = useCallback(() => {
    // Implementation
  }, []);

  // Step 3: Return
  return { state, action };
}
```

## When to Read Full Pillar?
- ❓ [Scenario requiring deep theoretical understanding] → Read Pillar [X]
- ❓ [Complex edge case or anti-pattern] → Read Pillar [Y]
- ❓ [Advanced pattern or optimization] → Read Pillar [Z]
- ❓ [Testing or debugging complex issues] → Read Pillar [W]

## Related
- **Pillar [X]**: `.prot/pillars/<quadrant>/<pillar>/<name>.md` (primary reference)
- **Pillar [Y]**: [Related pillar for complementary concepts]
- **Rule**: `[related-rule.md]` (related technical rule)
- **Rule**: `[another-rule.md]` (another related rule)

---

## Template Instructions (Delete this section when creating actual Rule)

### Naming Convention
- File name: `kebab-case.md` (e.g., `headless-hooks.md`, `saga-pattern.md`)
- Rule title: Title Case (e.g., "Headless Hook Rules", "Saga/Workflow Rules")

### Path Triggers
```yaml
---
paths: "**/*Pattern.ts"  # Or multiple: "**/*.ts,**/*.tsx"
---
```

Common patterns:
- `"**/headless/*.ts"` - Specific directory
- `"**/*Saga.ts"` - File naming pattern
- `"**/lambda/**"` - Directory with subdirectories
- `"**/*.ts,**/*.tsx"` - Multiple extensions

### Quick Check Guidelines
- **Length**: 5-8 items (target: 7)
- **Time**: Scannable in 30 seconds
- **Focus**: Most common mistakes and requirements
- **Format**: Checkbox list with brief descriptions
- **Order**: Priority order (most important first)

### Core Pattern Guidelines
- **Length**: 10-30 lines of code
- **Style**: Copy-paste ready, no placeholders
- **Comments**: Explain key decisions, not obvious syntax
- **Format**: Use appropriate language syntax highlighting
- **Example**: Show happy path, not edge cases

### "When to Read Full Pillar?" Guidelines
- **Purpose**: Help users decide if they need Pillar
- **Format**: Question format (❓) with action (→ Read Pillar X)
- **Content**: Scenarios requiring deep understanding
- **Count**: 3-5 scenarios

### Related Section Guidelines
- **Pillars**: List primary Pillar first, then related Pillars
- **Rules**: List complementary Rules (same domain/context)
- **Format**: Bold label + link + brief description

### Length Targets
- **Total**: 20-70 lines (target: 30-50 lines)
- **Quick Check**: 5-8 items
- **Core Pattern**: 10-30 lines
- **When to Read**: 3-5 scenarios
- **Related**: 2-5 links

### Writing Style
- **Imperative**: "Returns data", not "Should return data"
- **Concise**: Short sentences, active voice
- **Actionable**: Clear steps, no ambiguity
- **AI-friendly**: Explicit patterns, no implicit conventions

### Example Rules to Reference
- **Excellent**: `headless.md` (70 lines, clear structure)
- **Excellent**: `saga.md` (83 lines, comprehensive Quick Check)
- **Pattern**: `service-layer.md` (concise, actionable)

### Testing Your Rule
1. **Read time**: Can Quick Check be scanned in 30 seconds?
2. **Copy-paste**: Can Core Pattern be used immediately?
3. **Link**: Does Pillar link work?
4. **Path trigger**: Does file path pattern match your use case?
5. **Completeness**: Does "When to Read" cover common scenarios?

### Common Mistakes
- ❌ Too long (>70 lines) - extract to Pillar
- ❌ Too detailed - this is an index, not documentation
- ❌ No Pillar link - always link to source of truth
- ❌ Complex code - keep Core Pattern simple
- ❌ Missing Quick Check - always include
- ❌ Vague "When to Read" - be specific

### Issue #11 Context
This template was created as part of Issue #11 (Create Unified Rules Index System).

**Related files**:
- [INDEX.md](../INDEX.md) - Complete catalog of all 40 Rules
- [QUICK_REFERENCE.md](../QUICK_REFERENCE.md) - Top 20 most-used Rules
- [README.md](../README.md) - Rules system overview

**Design principle**: Rules are lightweight indexes that link to comprehensive Pillars. They provide quick validation and copy-paste patterns, not complete documentation.
