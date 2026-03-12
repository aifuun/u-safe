# Design Tokens Rules

> **CRITICAL**: Always use CSS variables from `app/src/styles.css`. Never hard-code values.

**Source**: `docs/spec/UI_UX_Design_System.md`
**Enforcement**: Stylelint + Pre-commit hooks

---

## Quick Check (30 seconds)

- [ ] All colors use `var(--color-*)` tokens
- [ ] All spacing uses `var(--space-*)` tokens
- [ ] All font sizes use `var(--text-*)` tokens
- [ ] All border radius uses `var(--radius-*)` tokens
- [ ] All shadows use `var(--shadow-*)` tokens
- [ ] No hard-coded hex colors (#...)
- [ ] No hard-coded pixel values (16px, 14px, etc.)

---

## Core Patterns

### Colors

```css
/* ❌ WRONG - Hard-coded */
color: #3B82F6;
background: #10B981;
border-color: #EF4444;

/* ✅ RIGHT - Tokens */
color: var(--color-primary);
background: var(--color-success);
border-color: var(--color-error);
```

### Spacing

```css
/* ❌ WRONG - Hard-coded */
padding: 16px;
margin: 12px 24px;
gap: 8px;

/* ✅ RIGHT - Tokens */
padding: var(--space-4);
margin: var(--space-3) var(--space-6);
gap: var(--space-2);
```

### Typography

```css
/* ❌ WRONG - Hard-coded */
font-size: 14px;
line-height: 20px;
font-weight: 600;

/* ✅ RIGHT - Tokens */
font-size: var(--text-sm);
line-height: var(--leading-sm);
font-weight: var(--font-weight-semibold);
```

### Border Radius

```css
/* ❌ WRONG - Hard-coded */
border-radius: 8px;

/* ✅ RIGHT - Token */
border-radius: var(--radius-md);
```

### Shadows

```css
/* ❌ WRONG - Hard-coded */
box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);

/* ✅ RIGHT - Token */
box-shadow: var(--shadow-md);
```

### Animations

```css
/* ❌ WRONG - Hard-coded */
transition: all 300ms ease-out;

/* ✅ RIGHT - Tokens + specific property */
transition: background var(--duration-base) var(--ease-out);
```

---

## Available Tokens

### Colors
- Primary: `--color-primary`, `--color-primary-hover`, `--color-primary-active`
- Semantic: `--color-success`, `--color-warning`, `--color-error`, `--color-info`
- Background: `--color-bg-app`, `--color-bg-surface`, `--color-bg-elevated`
- Text: `--color-text-primary`, `--color-text-secondary`, `--color-text-muted`
- Border: `--color-border`
- Encryption States: `--color-encrypted`, `--color-decrypted`, `--color-encrypting`

### Spacing (4px base unit)
- `--space-1` (4px), `--space-2` (8px), `--space-3` (12px), `--space-4` (16px)
- `--space-5` (20px), `--space-6` (24px), `--space-8` (32px), `--space-10` (40px)

### Typography
- Sizes: `--text-xs` to `--text-3xl`
- Line heights: `--leading-xs` to `--leading-3xl`
- Weights: `--font-weight-regular`, `--font-weight-medium`, `--font-weight-semibold`, `--font-weight-bold`
- Families: `--font-family-system`, `--font-family-mono`

### Border Radius
- `--radius-xs` (2px), `--radius-sm` (4px), `--radius-md` (8px)
- `--radius-lg` (12px), `--radius-xl` (16px), `--radius-full` (9999px)

### Shadows
- `--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-xl`, `--shadow-inset`

### Animation
- Duration: `--duration-instant`, `--duration-fast`, `--duration-base`, `--duration-slow`
- Easing: `--ease-out`, `--ease-in`, `--ease-in-out`

---

## Enforcement

### Automated (Blocks Commits)

Stylelint rules prevent:
- ❌ Hex colors (`#3B82F6`)
- ❌ RGB/HSL colors
- ❌ Hard-coded pixel values
- ❌ `transition: all`

**Run before commit:**
```bash
npm run lint:css
npm run lint:css:fix  # Auto-fix violations
```

### Pre-commit Hook

Automatically runs on every commit. Violations block the commit.

### Manual Code Review

PR checklist verifies:
- [ ] No hard-coded colors
- [ ] No hard-coded spacing
- [ ] No hard-coded font sizes
- [ ] Uses existing tokens

---

## Common Violations → Fixes

| Violation | Fix |
|-----------|-----|
| `color: #3B82F6` | `color: var(--color-primary)` |
| `background: white` | `background: var(--color-bg-app)` |
| `padding: 16px` | `padding: var(--space-4)` |
| `gap: 8px 12px` | `gap: var(--space-2) var(--space-3)` |
| `font-size: 14px` | `font-size: var(--text-sm)` |
| `border-radius: 8px` | `border-radius: var(--radius-md)` |
| `box-shadow: 0 4px...` | `box-shadow: var(--shadow-md)` |
| `transition: all 200ms` | `transition: background var(--duration-fast) var(--ease-out)` |

---

## When to Read Full Spec

- ❓ Need complete token list → Read `docs/spec/UI_UX_Design_System.md` Section 1
- ❓ Creating new component → Read Section 2 (Component Library)
- ❓ Platform-specific styles → Read Section 3 (Platform Adaptations)
- ❓ Animation patterns → Read Section 8 (Animation & Motion)
- ❓ Accessibility requirements → Read Section 6 (Accessibility)

---

## Related

- **Full Spec**: `docs/spec/UI_UX_Design_System.md`
- **Enforcement Guide**: `docs/spec/DESIGN_SYSTEM_ENFORCEMENT.md`
- **CSS Variables**: `app/src/styles.css`
- **Rule**: `.claude/rules/frontend/css.md` (spacing, shadows, radius)
- **Rule**: `.claude/rules/frontend/design-system.md` (component patterns)

---

**Last Updated**: 2026-03-12
**Status**: Active - Enforced by Stylelint
