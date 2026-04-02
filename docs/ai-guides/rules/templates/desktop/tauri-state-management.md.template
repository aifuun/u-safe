---
category: "desktop"
title: "Tauri State Management"
description: "Rust-side state"
tags: [rust, tauri]
profiles: [tauri]
paths: ['**/*.rs']
version: "1.0.0"
last_updated: "2026-03-27"
---

# Tauri State Management Rules

> **Goal**: Synchronized state between React frontend and Rust backend.
> **Pattern**: Frontend state for UI, backend state for business logic, events for sync.

---

## Quick Check (30 seconds)
- [ ] UI state (theme, selected tab) lives in React/Zustand
- [ ] Business logic state (app config, data) lives in Rust
- [ ] Use events for backend → frontend state updates
- [ ] Use commands for frontend → backend state changes
- [ ] Persistent state uses Tauri Store plugin or Rust file I/O
- [ ] Avoid duplicating state in both frontend and backend

## Core Pattern: Frontend UI State

**Frontend (Zustand):**
```typescript
import { create } from 'zustand';

interface UIStore {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  setTheme: (theme: 'light' | 'dark') => void;
  toggleSidebar: () => void;
}

export const useUIStore = create<UIStore>((set) => ({
  theme: 'light',
  sidebarOpen: true,
  setTheme: (theme) => set({ theme }),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
}));
```

## Core Pattern: Backend Business State

**Backend (Rust):**
```rust
use tauri::State;
use std::sync::Mutex;

struct AppState {
    config: Mutex<AppConfig>,
}

#[command]
fn get_config(state: State<AppState>) -> Result<AppConfig, String> {
    let config = state.config.lock().unwrap();
    Ok(config.clone())
}

#[command]
fn update_config(
    state: State<AppState>,
    new_config: AppConfig,
    app: tauri::AppHandle
) -> Result<(), String> {
    let mut config = state.config.lock().unwrap();
    *config = new_config.clone();

    // Notify frontend
    app.emit_all("config-updated", &new_config).unwrap();
    Ok(())
}
```

## Core Pattern: Event-Driven Sync

**Backend emits, Frontend listens:**
```typescript
import { listen } from '@tauri-apps/api/event';
import { useEffect } from 'react';

function useConfigSync() {
  const [config, setConfig] = useState<AppConfig | null>(null);

  useEffect(() => {
    const unlisten = listen<AppConfig>('config-updated', (event) => {
      setConfig(event.payload);
    });

    return () => { unlisten.then(fn => fn()); };
  }, []);

  return config;
}
```

## Anti-Patterns

❌ **Duplicating state**
```typescript
// BAD - Same data in frontend and backend
const [users, setUsers] = useState([]);  // Frontend
// + Rust backend also has users list → Out of sync!
```

✅ **Single source of truth**
```typescript
// Good - Backend is source of truth
const users = await invoke('get_users'); // Fetch from Rust
```

❌ **No state sync**
```typescript
// BAD - Backend state changes, frontend doesn't know
await invoke('update_settings', { theme: 'dark' });
// UI still shows 'light' theme!
```

## Related
- **Pillar E**: Orchestration (state coordination)
- **Rule**: `state-management.md` (React state patterns)
- **Rule**: `zustand-hooks.md` (frontend store usage)
