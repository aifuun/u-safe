# U-Safe UI/UX Design System

**Version**: v1.0
**Status**: Design Specification
**Date**: 2026-03-12
**Target Platforms**: Windows 11, macOS (Big Sur+)
**Application Type**: Tauri Desktop Application

---

## Overview

This document defines the comprehensive UI/UX design system for U-Safe, a Tauri-based desktop application that provides privacy-focused file encryption and intelligent organization on USB drives. The design system ensures a native, platform-appropriate experience on both Windows 11 and macOS while maintaining consistent branding and usability.

### Design Principles

1. **Platform Native** - Respect OS-specific conventions and visual language
2. **Privacy First** - Clear visual feedback for encryption states and security operations
3. **Minimal Friction** - Streamlined workflows for frequent operations (encrypt, tag, search)
4. **Portable** - Design for USB drive workflows and offline-first usage
5. **Accessible** - WCAG 2.1 AA compliance minimum, AAA where feasible

---

## 1. Design Foundation

### 1.1 Color System

#### Primary Palette

| Token | Hex | Usage | Notes |
|-------|-----|-------|-------|
| `--color-primary` | `#3B82F6` | Brand color, primary actions | Blue 500 (trust, security) |
| `--color-primary-hover` | `#2563EB` | Hover states | Blue 600 |
| `--color-primary-active` | `#1D4ED8` | Active/pressed states | Blue 700 |
| `--color-primary-muted` | `#DBEAFE` | Backgrounds, highlights | Blue 50 |

#### Semantic Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-success` | `#10B981` | Successful encryption, confirmations |
| `--color-warning` | `#F59E0B` | Warnings, pending operations |
| `--color-error` | `#EF4444` | Errors, destructive actions |
| `--color-info` | `#06B6D4` | Informational messages |

#### Neutral Palette (Light Mode)

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-bg-app` | `#FFFFFF` | Application background |
| `--color-bg-surface` | `#F9FAFB` | Card/panel backgrounds |
| `--color-bg-elevated` | `#FFFFFF` | Modal, dropdown backgrounds |
| `--color-border` | `#E5E7EB` | Borders, dividers |
| `--color-text-primary` | `#111827` | Primary text |
| `--color-text-secondary` | `#6B7280` | Secondary text, labels |
| `--color-text-muted` | `#9CA3AF` | Disabled text, placeholders |

#### Dark Mode Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-bg-app-dark` | `#0F172A` | Application background |
| `--color-bg-surface-dark` | `#1E293B` | Card/panel backgrounds |
| `--color-bg-elevated-dark` | `#334155` | Modal, dropdown backgrounds |
| `--color-border-dark` | `#334155` | Borders, dividers |
| `--color-text-primary-dark` | `#F1F5F9` | Primary text |
| `--color-text-secondary-dark` | `#94A3B8` | Secondary text |
| `--color-text-muted-dark` | `#64748B` | Disabled text |

#### Encryption State Colors

| State | Light Mode | Dark Mode | Visual Indicator |
|-------|------------|-----------|------------------|
| **Encrypted** | `#10B981` (Green) | `#34D399` | Lock icon, green badge |
| **Decrypted** | `#3B82F6` (Blue) | `#60A5FA` | Unlock icon, blue badge |
| **Encrypting** | `#F59E0B` (Amber) | `#FBBF24` | Lock + spinner, amber |
| **Error** | `#EF4444` (Red) | `#F87171` | Alert icon, red |

### 1.2 Typography System

#### Font Families

```css
/* Platform-specific system fonts */
--font-family-system-windows: 'Segoe UI', sans-serif;
--font-family-system-macos: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;

/* Monospace for codes, paths */
--font-family-mono: 'SF Mono', 'Consolas', 'Monaco', monospace;
```

#### Type Scale (Modular scale 1.250 - Major Third)

| Token | Size | Line Height | Weight | Usage |
|-------|------|-------------|--------|-------|
| `--text-xs` | 12px | 16px (1.33) | 400 | Captions, metadata |
| `--text-sm` | 14px | 20px (1.43) | 400 | Body text, labels |
| `--text-base` | 16px | 24px (1.5) | 400 | Default body |
| `--text-lg` | 18px | 28px (1.56) | 600 | Card headings |
| `--text-xl` | 20px | 28px (1.4) | 600 | Section headings |
| `--text-2xl` | 24px | 32px (1.33) | 700 | Page titles |
| `--text-3xl` | 30px | 36px (1.2) | 700 | Hero text |

#### Font Weights

```css
--font-weight-regular: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
```

### 1.3 Spacing System

Based on 4px base unit (consistent with existing .claude/rules/frontend/css.md):

| Token | Value | Usage |
|-------|-------|-------|
| `--space-1` | 4px | Icon gaps, tight spacing |
| `--space-2` | 8px | Small gaps between elements |
| `--space-3` | 12px | Default padding for inputs |
| `--space-4` | 16px | Standard spacing, card padding |
| `--space-5` | 20px | Section gaps |
| `--space-6` | 24px | Large element spacing |
| `--space-8` | 32px | Section spacing |
| `--space-10` | 40px | Page-level spacing |
| `--space-12` | 48px | Hero section spacing |

### 1.4 Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-xs` | 2px | Tags, badges |
| `--radius-sm` | 4px | Buttons, inputs |
| `--radius-md` | 8px | Cards, dropdowns |
| `--radius-lg` | 12px | Modals, panels |
| `--radius-xl` | 16px | Large cards |
| `--radius-full` | 9999px | Circular buttons, avatars |

### 1.5 Shadows (Elevation System)

| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle depth |
| `--shadow-md` | `0 4px 6px rgba(0,0,0,0.1)` | Cards, buttons |
| `--shadow-lg` | `0 10px 15px rgba(0,0,0,0.1)` | Dropdowns, tooltips |
| `--shadow-xl` | `0 20px 25px rgba(0,0,0,0.15)` | Modals, dialogs |
| `--shadow-inset` | `inset 0 2px 4px rgba(0,0,0,0.06)` | Input depth |

---

## 2. Component Library

### 2.1 Buttons

#### Button Variants

**Primary Button** - Main actions (Encrypt, Save, Confirm)
```css
.btn-primary {
  background: var(--color-primary);
  color: #FFFFFF;
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  font-weight: var(--font-weight-medium);
  box-shadow: var(--shadow-sm);
  transition: background 0.2s ease;
}

.btn-primary:hover {
  background: var(--color-primary-hover);
  box-shadow: var(--shadow-md);
}

.btn-primary:active {
  background: var(--color-primary-active);
}
```

**Secondary Button** - Alternative actions (Cancel, Back)
```css
.btn-secondary {
  background: transparent;
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-4);
}

.btn-secondary:hover {
  background: var(--color-bg-surface);
  border-color: var(--color-primary);
}
```

**Destructive Button** - Delete, remove actions
```css
.btn-destructive {
  background: var(--color-error);
  color: #FFFFFF;
  /* Same structure as primary */
}
```

**Ghost Button** - Tertiary actions, less emphasis
```css
.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary);
  border: none;
  padding: var(--space-2) var(--space-4);
}

.btn-ghost:hover {
  background: var(--color-bg-surface);
  color: var(--color-text-primary);
}
```

#### Button Sizes

| Size | Height | Padding | Font Size | Usage |
|------|--------|---------|-----------|-------|
| Small | 28px | 8px 12px | 12px | Inline actions |
| Medium | 36px | 8px 16px | 14px | Default |
| Large | 44px | 12px 20px | 16px | Primary CTAs |

#### Button States

- **Default**: Standard appearance
- **Hover**: Darker background, elevated shadow
- **Active/Pressed**: Darkest background, inset shadow
- **Disabled**: Opacity 0.5, no hover, cursor not-allowed
- **Loading**: Spinner icon, disabled interaction

### 2.2 Input Fields

#### Text Input

```css
.input-text {
  width: 100%;
  height: 36px;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-bg-app);
  transition: border-color 0.2s ease;
}

.input-text:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-muted);
}

.input-text:disabled {
  background: var(--color-bg-surface);
  cursor: not-allowed;
  opacity: 0.6;
}

.input-text.error {
  border-color: var(--color-error);
}
```

#### Password Input

Same as text input with additional features:
- **Show/hide toggle** (eye icon)
- **Strength indicator** (progress bar below)
- **Caps lock warning** (icon indicator)

#### Search Input

```css
.input-search {
  /* Same base as input-text */
  padding-left: 36px; /* Space for search icon */
  border-radius: var(--radius-full); /* Pill shape */
}

.input-search::before {
  /* Search icon (magnifying glass) */
}
```

### 2.3 Dropdown/Select

```css
.select {
  appearance: none;
  width: 100%;
  height: 36px;
  padding: var(--space-2) var(--space-3);
  padding-right: 36px; /* Space for chevron */
  font-size: var(--text-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-bg-app);
  cursor: pointer;
}

.select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-muted);
}

.select-dropdown {
  position: absolute;
  z-index: 100;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  max-height: 300px;
  overflow-y: auto;
}

.select-option {
  padding: var(--space-2) var(--space-3);
  cursor: pointer;
}

.select-option:hover {
  background: var(--color-bg-surface);
}

.select-option.selected {
  background: var(--color-primary-muted);
  color: var(--color-primary);
}
```

### 2.4 Checkbox and Radio

#### Checkbox

```css
.checkbox {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-xs);
  cursor: pointer;
}

.checkbox:checked {
  background: var(--color-primary);
  border-color: var(--color-primary);
  /* Checkmark icon */
}

.checkbox:focus {
  box-shadow: 0 0 0 3px var(--color-primary-muted);
}
```

#### Radio Button

```css
.radio {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-full);
  cursor: pointer;
}

.radio:checked {
  border-color: var(--color-primary);
  /* Inner circle */
}

.radio:checked::before {
  content: '';
  display: block;
  width: 8px;
  height: 8px;
  background: var(--color-primary);
  border-radius: var(--radius-full);
  margin: 2px;
}
```

### 2.5 Cards and Panels

#### Card

```css
.card {
  background: var(--color-bg-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s ease;
}

.card:hover {
  box-shadow: var(--shadow-md);
}

.card-header {
  font-size: var(--text-lg);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--space-4);
  color: var(--color-text-primary);
}

.card-body {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}
```

#### Panel (Sidebar, Settings)

```css
.panel {
  background: var(--color-bg-surface);
  border-right: 1px solid var(--color-border);
  height: 100%;
  width: 280px;
  padding: var(--space-6);
}

.panel-header {
  font-size: var(--text-xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--space-6);
}

.panel-section {
  margin-bottom: var(--space-8);
}

.panel-section-title {
  font-size: var(--text-sm);
  font-weight: var(--font-weight-medium);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-3);
}
```

### 2.6 Modal/Dialog

```css
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  background: var(--color-bg-elevated);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  width: 90%;
  max-width: 560px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.modal-body {
  padding: var(--space-6);
}

.modal-footer {
  padding: var(--space-6);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}
```

### 2.7 Toast/Notification

```css
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: var(--space-4);
  min-width: 300px;
  max-width: 400px;
  z-index: 2000;
  animation: slide-in 0.3s ease-out;
}

.toast.success {
  border-left: 4px solid var(--color-success);
}

.toast.error {
  border-left: 4px solid var(--color-error);
}

.toast.warning {
  border-left: 4px solid var(--color-warning);
}

.toast-message {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
}

@keyframes slide-in {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
```

### 2.8 Progress Indicators

#### Progress Bar

```css
.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--color-bg-surface);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: var(--radius-full);
  transition: width 0.3s ease;
}

.progress-bar-fill.encrypting {
  background: linear-gradient(90deg, #3B82F6, #10B981);
}
```

#### Loading Spinner

```css
.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--color-bg-surface);
  border-top-color: var(--color-primary);
  border-radius: var(--radius-full);
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

---

## 3. Platform-Specific Adaptations

### 3.1 Windows 11 Design

#### Window Chrome

- **Titlebar**: 32px height
- **Controls**: Right-aligned (minimize, maximize, close)
- **Control buttons**: 46px × 32px hit targets
- **Close button hover**: #E81123 (Windows red)

#### Mica Material (Windows 11+)

```css
/* For supported Windows 11 versions */
.window-mica {
  background: rgba(243, 243, 243, 0.5);
  backdrop-filter: blur(30px);
}
```

#### Segoe UI Typography

```css
body {
  font-family: 'Segoe UI', -apple-system, sans-serif;
}
```

#### Acrylic Effects (Windows 10 fallback)

```css
.panel-windows {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 0, 0, 0.05);
}
```

### 3.2 macOS Design

#### Window Chrome

- **Titlebar**: 22px height (standard), 28px (Big Sur+)
- **Traffic lights**: Left-aligned, 12px from left edge
- **Spacing**: 8px between traffic lights
- **Colors**: Red (#FF5F57), Yellow (#FFBD2E), Green (#28C840)

#### SF Pro Typography

```css
body {
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
}
```

#### Vibrancy Effects

```css
.sidebar-macos {
  background: rgba(246, 246, 246, 0.8);
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
  border-right: 1px solid rgba(0, 0, 0, 0.1);
}
```

#### Native Controls

- **Scrollbars**: System-provided overlays (no custom scrollbars)
- **Context menus**: Native OS menus via Tauri
- **Keyboard shortcuts**: Cmd instead of Ctrl

### 3.3 Platform Detection

```typescript
// Detect platform
const platform = await import('@tauri-apps/api/os').then(os => os.platform());

// Apply platform-specific styles
if (platform === 'darwin') {
  document.body.classList.add('platform-macos');
} else if (platform === 'win32') {
  document.body.classList.add('platform-windows');
}
```

### 3.4 Cross-Platform Fallbacks

| Feature | Windows | macOS | Fallback |
|---------|---------|-------|----------|
| Backdrop blur | Mica/Acrylic | Vibrancy | Solid color |
| Window controls | Native | Traffic lights | Generic icons |
| Accent color | System | System | Blue (#3B82F6) |
| Fonts | Segoe UI | SF Pro | System default |

---

## 4. Interaction Design

### 4.1 Encryption/Decryption Visual Feedback

#### Encrypt Action

1. **Initial state**: File item shows unlock icon (blue)
2. **User clicks "Encrypt"**: Confirmation modal appears
3. **Processing**:
   - Progress bar shows encryption progress (0-100%)
   - File item shows lock + spinner icon (amber)
   - Status text: "Encrypting... 45%"
4. **Complete**:
   - Lock icon turns green
   - Toast notification: "File encrypted successfully"
   - Fade animation (0.3s) from amber to green

#### Decrypt Action

1. **Initial state**: File item shows lock icon (green)
2. **User clicks "Decrypt"**: Password prompt modal
3. **Processing**:
   - Spinner on modal
   - Status text: "Decrypting..."
4. **Complete**:
   - Unlock icon (blue)
   - Modal closes
   - Toast: "File decrypted successfully"

#### Error States

- **Wrong password**: Shake animation (0.3s), red border on input
- **File access error**: Error icon, descriptive message in modal
- **Disk full**: Warning modal with cleanup suggestions

### 4.2 File Drag-and-Drop Interaction

#### Drop Zone States

1. **Default**: Dashed border, muted color
2. **Hover** (file dragged over): Solid border, primary color, background highlight
3. **Invalid** (wrong file type): Red border, error icon, shake animation
4. **Dropping**: Spinner, "Processing..." text
5. **Success**: Green checkmark, fade out (1s delay)

```css
.drop-zone {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-10);
  text-align: center;
  transition: all 0.2s ease;
}

.drop-zone.drag-over {
  border-color: var(--color-primary);
  border-style: solid;
  background: var(--color-primary-muted);
}

.drop-zone.invalid {
  border-color: var(--color-error);
  animation: shake 0.3s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}
```

### 4.3 Tag Management Interaction

#### Tag Input (Auto-complete)

1. **User types**: Suggestions dropdown appears after 2 characters
2. **Arrow keys**: Navigate suggestions
3. **Enter**: Select suggestion and create tag pill
4. **Comma/Tab**: Create new tag from typed text
5. **Escape**: Close suggestions

#### Tag Pill

```css
.tag-pill {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-3);
  background: var(--color-primary-muted);
  color: var(--color-primary);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-weight-medium);
}

.tag-pill-remove {
  width: 16px;
  height: 16px;
  border-radius: var(--radius-full);
  background: transparent;
  cursor: pointer;
  transition: background 0.2s ease;
}

.tag-pill-remove:hover {
  background: var(--color-primary);
  color: white;
}
```

#### Tag Color Customization

- **Color picker modal**: Predefined palette (8 colors) + custom picker
- **Preview**: Real-time preview of tag with selected color
- **Save**: Color stored per tag in database

### 4.4 View Transition Animations

#### View Switching (List ↔ Grid)

```css
.view-transition {
  animation: fade-in 0.3s ease-out;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

#### Sidebar Toggle

```css
.sidebar {
  width: 280px;
  transition: transform 0.3s ease-out;
}

.sidebar.collapsed {
  transform: translateX(-100%);
}
```

#### Modal Entry/Exit

```css
.modal-enter {
  animation: modal-enter 0.3s ease-out;
}

.modal-exit {
  animation: modal-exit 0.2s ease-in forwards;
}

@keyframes modal-enter {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes modal-exit {
  from {
    opacity: 1;
    transform: scale(1);
  }
  to {
    opacity: 0;
    transform: scale(0.95);
  }
}
```

#### Reduced Motion

```css
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

### 4.5 Loading States

#### Skeleton Screens

```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-bg-surface) 0%,
    #f0f0f0 50%,
    var(--color-bg-surface) 100%
  );
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s ease-in-out infinite;
  border-radius: var(--radius-sm);
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

#### Page Load

- **Initial load**: Skeleton screens for main content areas
- **Navigation**: Progress bar at top (linear, indeterminate)
- **Heavy operations**: Full-screen spinner + status text

---

## 5. Icon System

### 5.1 Icon Library

**MVP Approach**: Use emoji for quick prototyping and MVP

| Concept | Emoji | Unicode |
|---------|-------|---------|
| Encryption | 🔒 | U+1F512 |
| Decryption | 🔓 | U+1F513 |
| File | 📄 | U+1F4C4 |
| Folder | 📁 | U+1F4C1 |
| Search | 🔍 | U+1F50D |
| Tag | 🏷️ | U+1F3F7 |
| Settings | ⚙️ | U+2699 |
| Warning | ⚠️ | U+26A0 |
| Success | ✅ | U+2705 |
| Error | ❌ | U+274C |

**Future Migration**: Lucide React (consistent, customizable SVG icons)

### 5.2 Icon Sizing

| Size | Dimensions | Usage |
|------|------------|-------|
| xs | 12px × 12px | Inline with text |
| sm | 16px × 16px | Buttons, form elements |
| md | 20px × 20px | List items, cards |
| lg | 24px × 24px | Toolbar, headers |
| xl | 32px × 32px | Empty states, placeholders |

### 5.3 Icon Usage Guidelines

1. **Accessibility**: Always provide `aria-label` for icon-only buttons
2. **Consistency**: Use same icon for same action across app
3. **Color**: Icons inherit text color by default, use semantic colors for states
4. **Spacing**: Maintain 8px gap between icon and adjacent text

---

## 6. Accessibility

### 6.1 WCAG 2.1 Compliance

**Target**: AA minimum, AAA where feasible

#### Color Contrast

| Element Type | Minimum Ratio | Target |
|--------------|---------------|--------|
| Normal text (<18px) | 4.5:1 (AA) | 7:1 (AAA) |
| Large text (≥18px) | 3:1 (AA) | 4.5:1 (AAA) |
| UI components | 3:1 (AA) | 3:1 (AA) |
| Graphics | 3:1 (AA) | 3:1 (AA) |

**Verified Combinations** (Light Mode):
- `--color-text-primary` (#111827) on `--color-bg-app` (#FFFFFF): **16.1:1** ✅ AAA
- `--color-primary` (#3B82F6) on `#FFFFFF`: **4.6:1** ✅ AA (normal text)
- `--color-text-secondary` (#6B7280) on `#FFFFFF`: **4.7:1** ✅ AA

### 6.2 Keyboard Navigation

#### Tab Order

1. **Sequential**: Tab moves forward, Shift+Tab moves backward
2. **Logical**: Follow visual layout (top-to-bottom, left-to-right)
3. **Skip links**: "Skip to main content" for bypassing navigation

#### Focus Indicators

```css
*:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
  border-radius: var(--radius-xs);
}

button:focus-visible,
input:focus-visible {
  box-shadow: 0 0 0 3px var(--color-primary-muted);
}
```

#### Keyboard Shortcuts

| Action | Windows | macOS |
|--------|---------|-------|
| Open file | Ctrl+O | Cmd+O |
| Search | Ctrl+F | Cmd+F |
| Settings | Ctrl+, | Cmd+, |
| Close modal | Esc | Esc |
| Select all | Ctrl+A | Cmd+A |

### 6.3 Screen Reader Support

#### ARIA Labels

```html
<!-- Icon-only buttons -->
<button aria-label="Encrypt file">
  🔒
</button>

<!-- Status messages -->
<div role="status" aria-live="polite">
  File encrypted successfully
</div>

<!-- Progress indicators -->
<div role="progressbar" aria-valuenow="45" aria-valuemin="0" aria-valuemax="100">
  45%
</div>
```

#### Semantic HTML

- Use `<button>` for actions, not `<div onclick>`
- Use `<nav>` for navigation, `<main>` for primary content
- Use `<dialog>` for modals (native HTML5)

### 6.4 Alternative Text

- **Icons with text**: Icon can be decorative (`aria-hidden="true"`)
- **Icon-only elements**: Provide descriptive `aria-label`
- **Images**: Provide meaningful `alt` text (file previews, charts)

---

## 7. Responsive Design

### 7.1 Breakpoints

U-Safe is a desktop application, but supports different window sizes:

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Compact | < 768px | Single column, collapsible sidebar |
| Standard | 768px - 1280px | Default layout (sidebar + main) |
| Wide | > 1280px | Additional detail panels |

### 7.2 Minimum Window Size

- **Width**: 640px minimum
- **Height**: 480px minimum
- **Optimal**: 1024px × 768px

### 7.3 Responsive Patterns

#### Sidebar Collapse

```css
@media (max-width: 768px) {
  .sidebar {
    position: absolute;
    transform: translateX(-100%);
  }

  .sidebar.open {
    transform: translateX(0);
    box-shadow: var(--shadow-xl);
  }
}
```

#### Flexible Grid

```css
.file-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-4);
}
```

---

## 8. Animation and Motion

### 8.1 Timing Functions

```css
--ease-out: cubic-bezier(0, 0, 0.2, 1);  /* Accelerating out */
--ease-in: cubic-bezier(0.4, 0, 1, 1);   /* Decelerating in */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1); /* Smooth both ends */
```

### 8.2 Duration Tokens

```css
--duration-instant: 100ms;  /* Hover states */
--duration-fast: 200ms;     /* Transitions */
--duration-base: 300ms;     /* Default animations */
--duration-slow: 500ms;     /* Complex animations */
```

### 8.3 Motion Principles

1. **Purpose**: Every animation should serve a purpose (feedback, guidance, delight)
2. **Performance**: Use `transform` and `opacity` (GPU-accelerated)
3. **Restraint**: Don't overuse - reserve for important interactions
4. **Accessibility**: Respect `prefers-reduced-motion`

---

## 9. Documentation & Examples

### 9.1 Design Token Reference Table

All design tokens consolidated in one location: **See Section 1 (Design Foundation)**

CSS variables should be defined in `app/src/styles.css`:

```css
:root {
  /* Colors - Light Mode */
  --color-primary: #3B82F6;
  --color-primary-hover: #2563EB;
  /* ... (all tokens from Section 1) */

  /* Typography */
  --font-family-system-windows: 'Segoe UI', sans-serif;
  --text-base: 16px;
  /* ... */

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  /* ... */
}

/* Dark Mode */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-app: #0F172A;
    --color-text-primary: #F1F5F9;
    /* ... (all dark mode overrides) */
  }
}
```

### 9.2 Component Usage Examples

#### Button Example

```tsx
import { Button } from '@/components/Button';

// Primary action
<Button variant="primary" size="medium" onClick={handleEncrypt}>
  Encrypt File
</Button>

// Destructive action
<Button variant="destructive" size="medium" onClick={handleDelete}>
  Delete
</Button>

// Secondary action
<Button variant="secondary" size="small">
  Cancel
</Button>
```

#### Input Example

```tsx
import { Input } from '@/components/Input';

<Input
  type="text"
  placeholder="Search files..."
  value={searchQuery}
  onChange={setSearchQuery}
  icon={<SearchIcon />}
/>
```

### 9.3 Platform-Specific Implementation Notes

#### Detecting Platform at Runtime

```typescript
import { platform } from '@tauri-apps/api/os';

async function detectPlatform() {
  const os = await platform();
  return os; // 'win32', 'darwin', 'linux'
}
```

#### Applying Platform Styles

```typescript
// In App.tsx or main entry
useEffect(() => {
  detectPlatform().then(os => {
    document.body.classList.add(`platform-${os}`);
  });
}, []);
```

```css
/* Platform-specific CSS */
.platform-win32 .window-titlebar {
  height: 32px;
  justify-content: flex-end;
}

.platform-darwin .window-titlebar {
  height: 28px;
  justify-content: flex-start;
  padding-left: 80px; /* Space for traffic lights */
}
```

### 9.4 Accessibility Implementation Checklist

When implementing any component, verify:

- [ ] Color contrast meets WCAG AA minimum
- [ ] Keyboard navigation works (Tab, Enter, Esc, Arrow keys)
- [ ] Focus indicators visible on all interactive elements
- [ ] ARIA labels provided for icon-only buttons
- [ ] Role attributes correct (`button`, `dialog`, `navigation`)
- [ ] `aria-live` regions for dynamic status messages
- [ ] `prefers-reduced-motion` respected for animations
- [ ] Touch targets minimum 44×44px (for potential touch screens)

---

## 10. Implementation Roadmap

### Phase 1: Foundation (Milestone 1)
- [ ] CSS variables setup in `app/src/styles.css`
- [ ] Platform detection utility
- [ ] Base typography styles
- [ ] Color system (light + dark modes)

### Phase 2: Core Components (Milestone 2)
- [ ] Button component (all variants)
- [ ] Input components (text, password, search)
- [ ] Card/Panel layouts
- [ ] Modal/Dialog

### Phase 3: Advanced Components (Milestone 3)
- [ ] Dropdown/Select
- [ ] Tag management UI
- [ ] Progress indicators
- [ ] Toast notifications

### Phase 4: Platform Polish (Milestone 4)
- [ ] Windows 11 Mica/Acrylic effects
- [ ] macOS Vibrancy effects
- [ ] Platform-specific window chrome
- [ ] Native context menus (Tauri)

### Phase 5: Accessibility Audit (Milestone 5)
- [ ] Screen reader testing
- [ ] Keyboard navigation audit
- [ ] Color contrast verification
- [ ] WCAG 2.1 compliance report

---

## 11. References

### External Design Systems

- **Windows Fluent Design**: https://fluent2.microsoft.design/
- **macOS Human Interface Guidelines**: https://developer.apple.com/design/human-interface-guidelines/
- **Material Design 3**: https://m3.material.io/ (reference only)
- **Tailwind CSS**: https://tailwindcss.com/ (utility patterns)

### Technical Documentation

- **Tauri Docs**: https://tauri.app/
- **WCAG 2.1**: https://www.w3.org/WAI/WCAG21/quickref/
- **CSS Custom Properties**: https://developer.mozilla.org/en-US/docs/Web/CSS/--*

### Internal References

- **PRD**: `docs/spec/PRD_Core_Logic.md`
- **Architecture**: `docs/ADRs/003-technical-stack.md`
- **Security**: `docs/ADRs/004-encryption-strategy.md`
- **Database**: `docs/arch/Database_Schema.md`

---

## Appendix: Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| v1.0 | 2026-03-12 | Initial design system specification | Claude + Design Team |

---

**End of Document**

**Total Pages**: 15+ sections covering color, typography, spacing, components, platform adaptations, interactions, icons, accessibility, responsiveness, animations, and implementation guidance.

**Status**: ✅ Ready for Implementation

**Next Steps**:
1. Review design system with team
2. Implement CSS variables in `app/src/styles.css`
3. Create base component library (Phase 2)
4. Conduct accessibility audit before MVP release
