# ADR-001: Design Token System with CSS Variables

## Status

Accepted

## Date

2026-03-12

## Context

U-Safe is a Tauri-based desktop application that must provide native platform experiences on both Windows 11 and macOS (Big Sur+). The application has several critical requirements:

1. **Platform-Native Feel**: Must adapt visual appearance to match OS conventions
   - Windows 11: Mica material, Segoe UI font, window controls on right
   - macOS: Vibrancy effects, SF Pro font, traffic light buttons on left

2. **Runtime Theme Switching**: Users expect dark/light mode to switch instantly without restart
   - Must respond to OS-level theme changes
   - Should support manual override

3. **Offline-First USB Drive Usage**: Application runs from USB drives without internet
   - No CDN dependencies for fonts or styles
   - All assets must be bundled
   - Fast startup time critical

4. **Maintainability**: Design system must be enforceable and consistent
   - Developers need clear guidelines
   - AI-assisted development (Claude Code) should auto-enforce
   - Easy to update (single source of truth)

### Problem

Traditional approaches have limitations:

- **Sass/Less variables**: Compile-time only, can't switch themes at runtime
- **CSS-in-JS (styled-components)**: Bundle size overhead, React-specific, slower
- **Tailwind**: Class explosion, hard to maintain design tokens, no runtime theming
- **Hardcoded values**: No consistency, impossible to maintain

### Requirements

1. Runtime theme switching (light/dark mode)
2. Platform-specific values (fonts, spacing adjustments)
3. No build step dependencies (must work offline)
4. Browser-native (no external libraries)
5. Type-safe (TypeScript integration)
6. Enforceable (linting, pre-commit hooks)

## Decision

We will use **CSS Custom Properties (CSS Variables)** as the foundation for our design token system.

### Implementation

**1. Define tokens in `app/src/styles.css`:**

```css
:root {
  /* Color tokens */
  --color-primary: #3B82F6;
  --color-success: #10B981;
  --color-error: #EF4444;

  /* Spacing tokens (4px base unit) */
  --space-1: 4px;
  --space-2: 8px;
  --space-4: 16px;

  /* Typography tokens */
  --text-sm: 14px;
  --text-base: 16px;
  --text-lg: 18px;

  /* Platform-specific fonts */
  --font-family-system-windows: 'Segoe UI', sans-serif;
  --font-family-system-macos: -apple-system, 'SF Pro Text', sans-serif;
}

/* Dark mode overrides */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-app: #0F172A;
    --color-text-primary: #F1F5F9;
  }
}
```

**2. Use tokens in components:**

```css
.button {
  padding: var(--space-3) var(--space-4);
  background: var(--color-primary);
  font-size: var(--text-sm);
  border-radius: var(--radius-md);
}
```

**3. Platform-specific application:**

```typescript
// Detect platform and apply appropriate font family
const platform = await platform();
document.documentElement.style.setProperty(
  '--font-family-system',
  platform === 'win32'
    ? 'var(--font-family-system-windows)'
    : 'var(--font-family-system-macos)'
);
```

**4. Enforcement:**

- **Stylelint**: Block hard-coded colors and pixel values
- **Pre-commit hooks**: Validate token usage before commit
- **Claude AI rules**: `.claude/rules/frontend/design-tokens.md` auto-enforces
- **Documentation**: `docs/spec/UI_UX_Design_System.md` (1,329 lines)
- **Enforcement guide**: `docs/spec/DESIGN_SYSTEM_ENFORCEMENT.md` (802 lines)

### Token Categories

1. **Colors**: Primary, semantic, neutral, dark mode, encryption states
2. **Spacing**: 4px base unit (`--space-1` to `--space-10`)
3. **Typography**: Font sizes, weights, line heights, families
4. **Border Radius**: `--radius-xs` to `--radius-full`
5. **Shadows**: Elevation system (`--shadow-1` to `--shadow-4`)
6. **Motion**: Duration and easing (`--duration-fast`, `--ease-out`)

## Alternatives Considered

### 1. Sass Variables

**Pros:**
- Mature ecosystem
- Mixins and functions
- Well-documented

**Cons:**
- ❌ Compile-time only (no runtime theming)
- ❌ Requires build step
- ❌ Can't respond to OS theme changes
- ❌ Platform-specific values need separate builds

**Why rejected:** Runtime theme switching is a hard requirement.

### 2. CSS-in-JS (styled-components, Emotion)

**Pros:**
- Type-safe
- Scoped styles
- Dynamic styling

**Cons:**
- ❌ Bundle size overhead (~15KB)
- ❌ React-specific (doesn't work in Rust/Tauri layer)
- ❌ Runtime performance cost
- ❌ Complex setup for SSR (not applicable but overhead remains)

**Why rejected:** Performance and platform constraints (Tauri multi-process).

### 3. Tailwind CSS

**Pros:**
- Utility-first
- Fast development
- Good documentation

**Cons:**
- ❌ Class explosion (100+ classes per component)
- ❌ Design tokens buried in config
- ❌ Hard to enforce consistency
- ❌ Customization requires complex config
- ❌ Runtime theme switching requires JIT mode (build step)

**Why rejected:** Design token enforcement and runtime theming limitations.

### 4. Design Tokens with JSON + Code Generation

**Pros:**
- Single source of truth
- Can generate for multiple platforms
- Type-safe

**Cons:**
- ❌ Requires build tooling
- ❌ Complex setup
- ❌ Still needs CSS variables at runtime for theming
- ❌ Extra abstraction layer

**Why rejected:** Adds complexity without solving runtime theming.

## Consequences

### Positive

✅ **Runtime theme switching**: Instant light/dark mode without restart
✅ **Platform-native**: Can apply Windows 11 Mica or macOS Vibrancy at runtime
✅ **Browser-native**: No external dependencies, works offline
✅ **Type-safe**: Can generate TypeScript types from tokens
✅ **Enforceable**: Stylelint rules prevent violations
✅ **Maintainable**: Single source of truth in `styles.css`
✅ **Fast**: No runtime JS overhead, browser-native performance
✅ **AI-assisted**: Claude Code auto-enforces via rules
✅ **Accessible**: Easy to implement WCAG-compliant color contrast

### Negative

❌ **Browser support**: Requires modern browsers (IE11 not supported)
  - **Mitigation**: Tauri uses Chromium/WebKit (full support)

❌ **No computed values in tokens**: Can't do `--space-5: calc(var(--space-4) * 1.25)`
  - **Mitigation**: Pre-compute all values, use modular scale

❌ **Verbose syntax**: `var(--color-primary)` vs `$primary`
  - **Mitigation**: VS Code snippets, AI auto-completion

❌ **Learning curve**: Developers used to Sass/Less need adjustment
  - **Mitigation**: Comprehensive docs + Claude AI enforcement

### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Developers hard-code values | High | High | Stylelint + pre-commit hooks block commits |
| Token proliferation | Medium | Medium | Regular audits, consolidate similar tokens |
| Performance (too many variables) | Low | Low | Modern browsers handle 100+ vars efficiently |
| Token naming inconsistency | Medium | Medium | Naming convention in docs, enforced by rules |

## Implementation Plan

### Phase 1: Foundation (Complete ✅)
- [x] Define token system in `docs/spec/UI_UX_Design_System.md`
- [x] Create CSS variables in `app/src/styles.css`
- [x] Document enforcement in `DESIGN_SYSTEM_ENFORCEMENT.md`
- [x] Create Claude AI rules (`design-tokens.md`)

### Phase 2: Enforcement (Next)
- [ ] Configure Stylelint with token validation rules
- [ ] Set up pre-commit hooks (Husky + lint-staged)
- [ ] Add VS Code extensions (Stylelint, CSS Variable Autocomplete)
- [ ] Create PR template with design system checklist

### Phase 3: Migration (After Phase 2)
- [ ] Audit existing codebase for hard-coded values
- [ ] Migrate components to use tokens
- [ ] Update component library (buttons, inputs, cards)
- [ ] Run compliance audit

### Phase 4: Platform Adaptation (After Phase 3)
- [ ] Implement Windows 11 Mica material
- [ ] Implement macOS Vibrancy effects
- [ ] Platform detection and font switching
- [ ] Test on both platforms

### Phase 5: Optimization (Ongoing)
- [ ] Performance monitoring (CSS variable overhead)
- [ ] Token consolidation (remove unused)
- [ ] Documentation updates
- [ ] Developer training

## References

### Documentation
- [UI/UX Design System Specification](../spec/UI_UX_Design_System.md) - Complete design token definitions
- [Design System Enforcement Guide](../spec/DESIGN_SYSTEM_ENFORCEMENT.md) - Implementation strategy
- [Claude AI Rule: Design Tokens](./../.claude/rules/frontend/design-tokens.md) - AI enforcement

### Standards
- [CSS Custom Properties Specification](https://www.w3.org/TR/css-variables-1/) - W3C standard
- [WCAG 2.1 Color Contrast](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html) - Accessibility
- [Material Design 3 Tokens](https://m3.material.io/foundations/design-tokens/overview) - Industry reference

### Platform Guidelines
- [Windows 11 Fluent Design](https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/design-principles) - Mica material
- [macOS Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/macos) - SF Pro fonts, Vibrancy

### Related ADRs
- ADR-002: Component Library Architecture (planned)
- ADR-003: Platform-Specific Styling Strategy (planned)

---

**Approved by**: Design Team, Engineering Team
**Implemented in**: Issue #6 (UI/UX Design System)
**Last Reviewed**: 2026-03-12
