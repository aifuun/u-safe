---
category: "desktop"
title: "Tauri Ipc"
description: "Tauri IPC commands"
tags: [rust, tauri, typescript]
profiles: [tauri]
paths: ['**/*.{ts,tsx}']
version: "1.0.0"
last_updated: "2026-03-27"
---

# Tauri IPC (Inter-Process Communication) Rules

> **Goal**: Type-safe command/event contracts between React frontend and Rust backend.
> **Pattern**: Frontend invokes Rust commands, Rust emits events to frontend.

---

## Quick Check (30 seconds)
- [ ] All `invoke()` calls have matching Rust `#[tauri::command]`
- [ ] All commands use Result<T, E> return types
- [ ] Frontend types match Rust types (via type generation or manual sync)
- [ ] Event listeners cleaned up in `useEffect` return
- [ ] No complex objects passed without `serde` serialization
- [ ] Error handling present for all `invoke()` calls

## Core Pattern: Command (Frontend → Backend)

**Frontend (TypeScript):**
```typescript
import { invoke } from '@tauri-apps/api';

// Type-safe command invocation
interface SaveFileArgs {
  path: string;
  content: string;
}

async function saveFile(args: SaveFileArgs): Promise<void> {
  try {
    await invoke<void>('save_file', args);
  } catch (error) {
    console.error('Save failed:', error);
    throw error;
  }
}
```

**Backend (Rust):**
```rust
use tauri::command;

#[command]
async fn save_file(path: String, content: String) -> Result<(), String> {
    std::fs::write(&path, content)
        .map_err(|e| e.to_string())
}
```

## Core Pattern: Events (Backend → Frontend)

**Backend (Rust):**
```rust
use tauri::{AppHandle, Manager};

#[command]
async fn start_task(app: AppHandle) -> Result<(), String> {
    // Emit progress events
    app.emit_all("task-progress", 0.5).unwrap();
    app.emit_all("task-complete", "Done!").unwrap();
    Ok(())
}
```

**Frontend (TypeScript):**
```typescript
import { listen } from '@tauri-apps/api/event';

useEffect(() => {
  const unlisten = listen<number>('task-progress', (event) => {
    setProgress(event.payload);
  });

  return () => { unlisten.then(fn => fn()); }; // Cleanup!
}, []);
```

## Anti-Patterns

❌ **Missing error handling**
```typescript
// BAD - no try/catch
await invoke('delete_file', { path });
```

✅ **Good - handle errors**
```typescript
try {
  await invoke('delete_file', { path });
} catch (error) {
  showToast('Delete failed');
}
```

❌ **Synchronous expectations**
```typescript
// BAD - IPC is always async
const result = invoke('get_data'); // Wrong!
```

❌ **Forgetting event cleanup**
```typescript
// BAD - memory leak
listen('my-event', handler); // Never unlistens
```

## Related
- **Pillar A**: Nominal Types (brand command types)
- **Rule**: `typescript-nominal-types.md`
- **Tauri Docs**: https://tauri.app/develop/calling-rust/
