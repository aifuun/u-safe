# Design System Enforcement Guide

**Purpose**: Ensure all development follows the UI/UX Design System specifications

**Target**: Developers, Claude AI, Code Reviewers

**Status**: Implementation Guide

---

## Overview

This document outlines the tooling, automation, and workflow integration to enforce the UI/UX Design System during development.

### Enforcement Layers

1. **Prevention** - Make it easy to do the right thing (CSS variables, components)
2. **Detection** - Catch violations early (linting, pre-commit hooks)
3. **Correction** - Clear guidance on fixing issues (rules, checklists)
4. **Review** - Human validation (PR checklist, design review)

---

## 1. CSS Variables & Design Tokens (Prevention)

### Step 1: Implement Design Tokens

Create `/app/src/styles.css` with all design tokens:

```css
/* File: app/src/styles.css */

:root {
  /* === COLORS - Light Mode === */

  /* Primary */
  --color-primary: #3B82F6;
  --color-primary-hover: #2563EB;
  --color-primary-active: #1D4ED8;
  --color-primary-muted: #DBEAFE;

  /* Semantic Colors */
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
  --color-info: #06B6D4;

  /* Neutral Palette */
  --color-bg-app: #FFFFFF;
  --color-bg-surface: #F9FAFB;
  --color-bg-elevated: #FFFFFF;
  --color-border: #E5E7EB;
  --color-text-primary: #111827;
  --color-text-secondary: #6B7280;
  --color-text-muted: #9CA3AF;

  /* Encryption States */
  --color-encrypted: #10B981;
  --color-decrypted: #3B82F6;
  --color-encrypting: #F59E0B;

  /* === TYPOGRAPHY === */

  /* Font Families */
  --font-family-system: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'SF Pro Text', sans-serif;
  --font-family-mono: 'SF Mono', 'Consolas', 'Monaco', monospace;

  /* Font Sizes */
  --text-xs: 12px;
  --text-sm: 14px;
  --text-base: 16px;
  --text-lg: 18px;
  --text-xl: 20px;
  --text-2xl: 24px;
  --text-3xl: 30px;

  /* Line Heights */
  --leading-xs: 16px;
  --leading-sm: 20px;
  --leading-base: 24px;
  --leading-lg: 28px;
  --leading-xl: 28px;
  --leading-2xl: 32px;
  --leading-3xl: 36px;

  /* Font Weights */
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* === SPACING === */

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;

  /* === BORDER RADIUS === */

  --radius-xs: 2px;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;

  /* === SHADOWS === */

  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
  --shadow-inset: inset 0 2px 4px rgba(0, 0, 0, 0.06);

  /* === ANIMATION === */

  --duration-instant: 100ms;
  --duration-fast: 200ms;
  --duration-base: 300ms;
  --duration-slow: 500ms;

  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
}

/* === DARK MODE === */

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-app: #0F172A;
    --color-bg-surface: #1E293B;
    --color-bg-elevated: #334155;
    --color-border: #334155;
    --color-text-primary: #F1F5F9;
    --color-text-secondary: #94A3B8;
    --color-text-muted: #64748B;

    --color-encrypted: #34D399;
    --color-decrypted: #60A5FA;
    --color-encrypting: #FBBF24;
  }
}

/* === PLATFORM-SPECIFIC === */

.platform-windows {
  --font-family-system: 'Segoe UI', sans-serif;
}

.platform-darwin {
  --font-family-system: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
}

/* === BASE STYLES === */

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family-system);
  font-size: var(--text-base);
  line-height: var(--leading-base);
  color: var(--color-text-primary);
  background: var(--color-bg-app);
}

/* === REDUCED MOTION === */

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Usage**: Developers MUST use CSS variables, never hard-coded values.

---

## 2. CSS Linting Rules (Detection)

### Step 2: Configure Stylelint

Create `.stylelintrc.json`:

```json
{
  "extends": "stylelint-config-standard",
  "plugins": [
    "stylelint-no-unsupported-browser-features",
    "stylelint-use-logical-spec"
  ],
  "rules": {
    "color-no-hex": true,
    "declaration-property-value-disallowed-list": {
      "color": ["/^#/", "/^rgb/", "/^hsl/"],
      "background": ["/^#/", "/^rgb/", "/^hsl/"],
      "background-color": ["/^#/", "/^rgb/", "/^hsl/"],
      "border-color": ["/^#/", "/^rgb/", "/^hsl/"],
      "font-size": ["/px$/", "/rem$/", "/em$/"],
      "padding": ["/px$/", "/rem$/"],
      "margin": ["/px$/", "/rem$/"],
      "gap": ["/px$/", "/rem$/"],
      "border-radius": ["/px$/", "/rem$/"],
      "transition": ["/all/"]
    },
    "custom-property-pattern": "^(color|text|space|radius|shadow|duration|ease|font)-[a-z0-9-]+$",
    "selector-class-pattern": "^[a-z][a-z0-9]*(-[a-z0-9]+)*$"
  }
}
```

**What this does:**
- ❌ Blocks hard-coded colors (`#3B82F6` → must use `var(--color-primary)`)
- ❌ Blocks hard-coded sizes (`16px` → must use `var(--space-4)`)
- ❌ Blocks `transition: all` (performance issue)
- ✅ Enforces kebab-case for CSS classes
- ✅ Enforces token naming pattern

### Install Stylelint

```bash
cd app
npm install --save-dev stylelint stylelint-config-standard
```

### Add to package.json

```json
{
  "scripts": {
    "lint:css": "stylelint 'src/**/*.css'",
    "lint:css:fix": "stylelint 'src/**/*.css' --fix"
  }
}
```

---

## 3. Claude AI Rules (Prevention)

### Step 3: Update .claude/rules/frontend/design-system.md

**This rule already exists** and enforces design system compliance. Key sections:

```markdown
## Pre-Development Checklist (必读)

Before coding ANY component, read:

### Step 1: Identify Your Component Type
- [ ] Button/action? → Read BUTTON_QUICK_REFERENCE.md
- [ ] Form component? → Read FORMS.md
...

### Step 2: Identify Required Tokens
- [ ] Colors: Check COLOR.md (semantic tokens only)
- [ ] Typography: Use --text-sm, not 14px
- [ ] Spacing: Use --space-3, not 12px
...
```

**Enhancement**: Add specific reference to the new design system doc:

```markdown
## Design System Source of Truth

**Primary Reference**: `docs/spec/UI_UX_Design_System.md`

Before implementing ANY UI:
1. Read relevant section in design system doc
2. Copy token usage patterns exactly
3. Never hard-code values
```

### Step 4: Create Design System Quick Reference Rule

Create `.claude/rules/frontend/design-tokens.md`:

```markdown
# Design Tokens Rules

> CRITICAL: Always use CSS variables from app/src/styles.css

## Golden Rules

1. **NEVER hard-code colors** - Use `var(--color-*)`
2. **NEVER hard-code spacing** - Use `var(--space-*)`
3. **NEVER hard-code font sizes** - Use `var(--text-*)`
4. **NEVER hard-code border radius** - Use `var(--radius-*)`
5. **NEVER hard-code shadows** - Use `var(--shadow-*)`

## Quick Reference

### Colors
```css
/* ❌ WRONG */
color: #3B82F6;
background: #10B981;

/* ✅ RIGHT */
color: var(--color-primary);
background: var(--color-success);
```

### Spacing
```css
/* ❌ WRONG */
padding: 16px;
gap: 12px;

/* ✅ RIGHT */
padding: var(--space-4);
gap: var(--space-3);
```

### Typography
```css
/* ❌ WRONG */
font-size: 14px;
line-height: 20px;

/* ✅ RIGHT */
font-size: var(--text-sm);
line-height: var(--leading-sm);
```

## Enforcement

**Automated**: Stylelint blocks violations
**Manual**: Code review checklist

## See Full Spec

`docs/spec/UI_UX_Design_System.md`
```

---

## 4. Pre-Commit Hooks (Detection)

### Step 5: Add Husky + Lint-Staged

```bash
cd app
npm install --save-dev husky lint-staged
npx husky install
```

Create `.husky/pre-commit`:

```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

npx lint-staged
```

Add to `package.json`:

```json
{
  "lint-staged": {
    "*.css": [
      "stylelint --fix",
      "git add"
    ],
    "*.{ts,tsx}": [
      "eslint --fix",
      "git add"
    ]
  }
}
```

**Result**: Every commit automatically validates CSS tokens before allowing commit.

---

## 5. Component Library (Prevention)

### Step 6: Create Base Components

**Strategy**: Provide pre-built components that enforce design system.

#### Button Component

`app/src/components/Button/Button.tsx`:

```tsx
import './Button.css';

type ButtonVariant = 'primary' | 'secondary' | 'destructive' | 'ghost';
type ButtonSize = 'small' | 'medium' | 'large';

interface ButtonProps {
  variant?: ButtonVariant;
  size?: ButtonSize;
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  ariaLabel?: string;
}

export function Button({
  variant = 'primary',
  size = 'medium',
  children,
  onClick,
  disabled = false,
  type = 'button',
  ariaLabel
}: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      onClick={onClick}
      disabled={disabled}
      type={type}
      aria-label={ariaLabel}
    >
      {children}
    </button>
  );
}
```

`app/src/components/Button/Button.css`:

```css
/* Uses only design tokens */
.btn {
  font-family: var(--font-family-system);
  font-weight: var(--font-weight-medium);
  border: none;
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
  border-radius: var(--radius-sm);
}

.btn-primary {
  background: var(--color-primary);
  color: #FFFFFF;
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  background: transparent;
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

/* ... other variants */

.btn-small {
  height: 28px;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-xs);
}

.btn-medium {
  height: 36px;
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
}

.btn-large {
  height: 44px;
  padding: var(--space-3) var(--space-5);
  font-size: var(--text-base);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

**Benefit**: Developers use `<Button>` instead of writing custom buttons.

---

## 6. Code Review Checklist (Correction)

### Step 7: PR Template with Design System Checks

Create `.github/pull_request_template.md`:

```markdown
## Description
<!-- Brief description of changes -->

## Design System Compliance

### Visual Elements
- [ ] **No hard-coded colors** - All colors use `var(--color-*)`
- [ ] **No hard-coded spacing** - All spacing uses `var(--space-*)`
- [ ] **No hard-coded font sizes** - All text uses `var(--text-*)`
- [ ] **No hard-coded border radius** - Uses `var(--radius-*)`
- [ ] **No hard-coded shadows** - Uses `var(--shadow-*)`

### Components
- [ ] Uses existing components from `app/src/components/` when possible
- [ ] New components follow design system patterns
- [ ] Component props match design system variants

### Accessibility
- [ ] Color contrast meets WCAG AA (4.5:1 minimum)
- [ ] Focus indicators visible on all interactive elements
- [ ] ARIA labels on icon-only buttons
- [ ] Keyboard navigation works (Tab, Enter, Esc)

### Platform
- [ ] Platform detection applied if needed
- [ ] Platform-specific styles use `.platform-windows` / `.platform-darwin`

### Motion
- [ ] Animations use `var(--duration-*)` and `var(--ease-*)`
- [ ] `@media (prefers-reduced-motion)` respected

## Testing
- [ ] Tested in light mode
- [ ] Tested in dark mode
- [ ] Tested on Windows (or will test before merge)
- [ ] Tested on macOS (or will test before merge)

## Screenshots
<!-- Add before/after screenshots if UI changes -->

## Related
- Design System: `docs/spec/UI_UX_Design_System.md`
- Issue: #
```

---

## 7. VS Code Integration (Prevention)

### Step 8: Recommended Extensions

Create `.vscode/extensions.json`:

```json
{
  "recommendations": [
    "stylelint.vscode-stylelint",
    "dbaeumer.vscode-eslint",
    "bradlc.vscode-tailwindcss",
    "streetsidesoftware.code-spell-checker"
  ]
}
```

### Step 9: VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "css.validate": false,
  "less.validate": false,
  "scss.validate": false,
  "stylelint.enable": true,
  "stylelint.validate": ["css", "postcss"],
  "editor.codeActionsOnSave": {
    "source.fixAll.stylelint": true,
    "source.fixAll.eslint": true
  },
  "css.customData": [".vscode/css-custom-data.json"]
}
```

Create `.vscode/css-custom-data.json` for autocomplete:

```json
{
  "version": 1.1,
  "properties": [],
  "atDirectives": [],
  "pseudoClasses": [],
  "pseudoElements": []
}
```

**Benefit**: Auto-complete for CSS variables, auto-fix on save.

---

## 8. Documentation in Codebase (Correction)

### Step 10: Component Documentation

Use JSDoc comments referencing design system:

```tsx
/**
 * Primary action button following design system.
 *
 * @see docs/spec/UI_UX_Design_System.md#21-buttons
 *
 * @example
 * <Button variant="primary" size="medium" onClick={handleSave}>
 *   Save
 * </Button>
 */
export function Button({ ... }) { ... }
```

### Step 11: CSS Comments

```css
/**
 * Button component styles
 * Follows design system tokens from app/src/styles.css
 * @see docs/spec/UI_UX_Design_System.md#21-buttons
 */
.btn {
  /* Design tokens only - never hard-code */
  background: var(--color-primary);
  padding: var(--space-2) var(--space-4);
}
```

---

## 9. Automated Visual Regression (Detection)

### Step 12: Storybook + Chromatic (Future)

**Phase 3 Enhancement**: Add visual regression testing

```bash
npm install --save-dev @storybook/react chromatic
```

Create stories for each component:

```tsx
// Button.stories.tsx
export default {
  title: 'Components/Button',
  component: Button
};

export const Primary = () => <Button variant="primary">Primary</Button>;
export const Secondary = () => <Button variant="secondary">Secondary</Button>;
```

**Benefit**: Catch visual regressions automatically.

---

## 10. Enforcement Summary

### For Developers

| Stage | Tool | What It Does | Enforcement Level |
|-------|------|--------------|-------------------|
| **Write Code** | CSS Variables | Provides tokens | ✅ Prevention |
| **Write Code** | VS Code Extensions | Auto-complete, warnings | ⚠️ Suggestion |
| **Write Code** | Component Library | Pre-built components | ✅ Prevention |
| **Save File** | VS Code Auto-fix | Fix on save | ✅ Auto-fix |
| **Commit** | Pre-commit Hook | Block bad commits | 🚫 Blocking |
| **Commit** | Stylelint | Validate tokens | 🚫 Blocking |
| **Pull Request** | PR Template | Manual checklist | ⚠️ Manual Review |
| **Merge** | Code Review | Human validation | ⚠️ Manual Review |

### For Claude AI

Claude follows these rules automatically:

1. `.claude/rules/frontend/design-system.md` - General patterns
2. `.claude/rules/frontend/design-tokens.md` - Token usage
3. `.claude/rules/frontend/css.md` - CSS conventions
4. `docs/spec/UI_UX_Design_System.md` - Complete spec

**Trigger**: Path-based auto-loading when working on `**/*.css` or `**/components/**`

---

## 11. Quick Start Checklist

### Initial Setup (Do Once)

- [ ] Create `app/src/styles.css` with design tokens
- [ ] Install Stylelint: `npm install --save-dev stylelint stylelint-config-standard`
- [ ] Create `.stylelintrc.json` with rules
- [ ] Install Husky: `npm install --save-dev husky lint-staged`
- [ ] Setup pre-commit hook
- [ ] Create `.vscode/extensions.json` and `.vscode/settings.json`
- [ ] Create `.github/pull_request_template.md`
- [ ] Create base component library (Button, Input, etc.)
- [ ] Add `.claude/rules/frontend/design-tokens.md`

### Every New Component

- [ ] Check design system doc for patterns
- [ ] Use existing components if available
- [ ] Use only CSS variables (no hard-coded values)
- [ ] Test in light + dark modes
- [ ] Verify accessibility (focus, ARIA, keyboard nav)
- [ ] Run `npm run lint:css` before committing
- [ ] Fill out PR checklist

### Every Code Review

- [ ] Verify no hard-coded colors/spacing/fonts
- [ ] Check component props match design system
- [ ] Test on both platforms (Windows + macOS)
- [ ] Verify accessibility compliance
- [ ] Check reduced motion support

---

## 12. Common Violations & Fixes

| Violation | Detection | Fix |
|-----------|-----------|-----|
| Hard-coded color `#3B82F6` | Stylelint error | Use `var(--color-primary)` |
| Hard-coded spacing `padding: 16px` | Stylelint error | Use `var(--space-4)` |
| Hard-coded font size `font-size: 14px` | Stylelint error | Use `var(--text-sm)` |
| Missing focus indicator | Manual review | Add `:focus-visible { outline: ... }` |
| No dark mode support | Manual review | Use CSS variables (auto dark mode) |
| `transition: all` | Stylelint warning | Specify property: `transition: background ...` |
| Platform font not applied | Manual review | Use `var(--font-family-system)` |

---

## 13. Measuring Compliance

### Automated Metrics

```bash
# Check CSS violations
npm run lint:css

# Count hard-coded colors in codebase
grep -r "#[0-9A-Fa-f]\{6\}" app/src --include="*.css" | wc -l

# Count CSS variable usage
grep -r "var(--" app/src --include="*.css" | wc -l
```

### Manual Audit (Weekly)

- [ ] Review merged PRs for design system compliance
- [ ] Check component library adoption rate
- [ ] Verify accessibility standards met
- [ ] Update design system doc if new patterns emerge

---

## 14. Resources

### For Developers

- **Design System Spec**: `docs/spec/UI_UX_Design_System.md`
- **CSS Tokens**: `app/src/styles.css`
- **Component Library**: `app/src/components/`
- **Linting Rules**: `.stylelintrc.json`

### For Claude AI

- **Rules**: `.claude/rules/frontend/design-system.md`
- **Rules**: `.claude/rules/frontend/design-tokens.md`
- **Rules**: `.claude/rules/frontend/css.md`

### External References

- **Stylelint Docs**: https://stylelint.io/
- **WCAG 2.1**: https://www.w3.org/WAI/WCAG21/quickref/
- **Tauri Styling**: https://tauri.app/

---

**Status**: ✅ Ready for Implementation

**Next Steps**:
1. Complete initial setup checklist (Section 11)
2. Create first base component (Button)
3. Run enforcement tools on first PR
4. Iterate and improve based on feedback
