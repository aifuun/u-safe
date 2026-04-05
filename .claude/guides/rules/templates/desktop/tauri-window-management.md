---
category: "desktop"
title: "Tauri Window Management"
description: "Window management"
tags: [rust, tauri]
profiles: [tauri]
paths: ['**/*.rs']
version: "1.0.0"
last_updated: "2026-03-27"
---

# Tauri Window Management Rules

> **Goal**: Multi-window architecture with proper lifecycle management.
> **Pattern**: Create windows in Rust backend, communicate via events, clean up listeners.

---

## Quick Check (30 seconds)
- [ ] Windows created via Rust commands (not in React components)
- [ ] Each window has unique label
- [ ] Event listeners cleaned up when window closes
- [ ] Main window vs utility windows clearly separated
- [ ] Window state (size, position) persisted if needed

## Core Pattern: Create Window

**Frontend:**
```typescript
import { invoke } from '@tauri-apps/api';

async function openSettings() {
  await invoke('create_settings_window');
}
```

**Backend (Rust):**
```rust
use tauri::{Manager, Window, WindowBuilder};

#[command]
fn create_settings_window(app: tauri::AppHandle) -> Result<(), String> {
    if app.get_window("settings").is_some() {
        return Ok(()); // Already exists
    }

    WindowBuilder::new(
        &app,
        "settings",
        tauri::WindowUrl::App("/settings".into())
    )
    .title("Settings")
    .inner_size(600.0, 400.0)
    .resizable(false)
    .build()
    .map_err(|e| e.to_string())?;

    Ok(())
}
```

## Anti-Patterns

❌ **Creating windows in React**
```typescript
// BAD - Window creation should be in Rust
const SettingsButton = () => {
  const openWindow = () => {
    new WebviewWindow('settings'); // ❌ Frontend control
  };
};
```

❌ **Not cleaning up listeners**
```typescript
// BAD - Memory leak
listen('window-event', handler); // No cleanup
```

## Related
- **Pillar G**: Traceability (window lifecycle tracking)
- **Rule**: `tauri-ipc.md` (window communication)
