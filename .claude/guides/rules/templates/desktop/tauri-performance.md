---
category: "desktop"
title: "Tauri Performance"
description: "Performance optimization"
tags: [rust, tauri]
profiles: [tauri]
paths: ['**/*.rs']
version: "1.0.0"
last_updated: "2026-03-27"
---

# Tauri Performance Optimization Rules

> **Goal**: Minimize bundle size and startup time for desktop apps.
> **Pattern**: Strip unused features, optimize Rust release builds, lazy load heavy dependencies.

---

## Quick Check (30 seconds)
- [ ] Bundle size < 100MB (smaller is better)
- [ ] Cold start < 3 seconds
- [ ] Only required Tauri features enabled in `Cargo.toml`
- [ ] Frontend code split (lazy load routes)
- [ ] Rust compiled with `release` profile optimizations
- [ ] Assets (images, fonts) optimized

## Core Pattern: Optimize Rust Build

**Cargo.toml:**
```toml
[profile.release]
opt-level = "z"     # Optimize for size
lto = true          # Link-time optimization
codegen-units = 1   # Single codegen unit (slower build, faster runtime)
panic = "abort"     # Smaller binary
strip = true        # Remove debug symbols
```

## Core Pattern: Feature Stripping

**Cargo.toml:**
```toml
[dependencies.tauri]
version = "1.5"
features = [
  "shell-open",      # Only enable what you need
  "dialog-all",
  "fs-read-file",
  "fs-write-file"
]
# Don't enable:
# "shell-execute"   ❌ (security risk)
# "http-all"        ❌ (unless needed)
```

## Core Pattern: Frontend Code Splitting

**React:**
```typescript
import { lazy, Suspense } from 'react';

const SettingsPage = lazy(() => import('./pages/Settings'));
const AnalyticsPage = lazy(() => import('./pages/Analytics'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
      </Routes>
    </Suspense>
  );
}
```

## Anti-Patterns

❌ **Including all Tauri features**
```toml
# BAD - Bloated binary
[dependencies.tauri]
features = ["all"] # ❌ 50MB+ bundle
```

❌ **No code splitting**
```typescript
// BAD - Loads all code upfront
import SettingsPage from './pages/Settings';
import AnalyticsPage from './pages/Analytics';
// ... 20 more imports → Slow startup
```

## Related
- **Pillar K**: Testing (performance benchmarks)
- **Rule**: `performance.md` (general optimization)
