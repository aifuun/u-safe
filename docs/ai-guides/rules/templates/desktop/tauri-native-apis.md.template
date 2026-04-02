---
category: "desktop"
title: "Tauri Native Apis"
description: "Native API access"
tags: [rust, tauri]
profiles: [tauri]
paths: ['**/*.rs']
version: "1.0.0"
last_updated: "2026-03-27"
---

# Tauri Native APIs Rules

> **Goal**: Safe wrappers for native platform APIs.
> **Pattern**: Use Tauri APIs instead of direct native calls, handle paths correctly, never block UI.

---

## Quick Check (30 seconds)
- [ ] Use Tauri `dialog` API instead of browser `<input type="file">`
- [ ] Path resolution uses `@tauri-apps/api/path` (never hardcode paths)
- [ ] Long file operations run in Rust backend (don't block React UI)
- [ ] System tray, notifications use Tauri plugins (not web APIs)
- [ ] Clipboard access via `@tauri-apps/api/clipboard` (not `navigator.clipboard` for desktop features)

## Core Pattern: File Dialog

**Frontend (TypeScript):**
```typescript
import { open, save } from '@tauri-apps/api/dialog';
import { readTextFile, writeTextFile } from '@tauri-apps/api/fs';
import { appDataDir } from '@tauri-apps/api/path';

async function openFile() {
  const selected = await open({
    multiple: false,
    filters: [{ name: 'Text', extensions: ['txt', 'md'] }]
  });

  if (selected) {
    const content = await readTextFile(selected as string);
    return content;
  }
}

async function saveToAppData(filename: string, data: string) {
  const appDir = await appDataDir();
  const filePath = `${appDir}/${filename}`;
  await writeTextFile(filePath, data);
}
```

## Core Pattern: System Tray

**Backend (Rust):**
```rust
use tauri::{CustomMenuItem, SystemTray, SystemTrayMenu, SystemTrayEvent};
use tauri::Manager;

fn create_system_tray() -> SystemTray {
    let quit = CustomMenuItem::new("quit".to_string(), "Quit");
    let show = CustomMenuItem::new("show".to_string(), "Show");
    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_item(quit);

    SystemTray::new().with_menu(tray_menu)
}

// Handle tray events
fn handle_system_tray_event(app: &tauri::AppHandle, event: SystemTrayEvent) {
    match event {
        SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
            "quit" => std::process::exit(0),
            "show" => {
                let window = app.get_window("main").unwrap();
                window.show().unwrap();
            }
            _ => {}
        },
        _ => {}
    }
}
```

## Anti-Patterns

❌ **Hardcoded paths**
```typescript
// BAD - Breaks cross-platform compatibility
const config = '/Users/alice/AppData/config.json';
```

✅ **Use path resolver**
```typescript
import { appConfigDir } from '@tauri-apps/api/path';
const configDir = await appConfigDir();
const config = `${configDir}/config.json`;
```

❌ **Blocking UI with long operations**
```typescript
// BAD - Freezes React UI
const data = await fs.readFile(largeFilePath);
setData(data); // UI frozen during read
```

✅ **Offload to Rust backend**
```rust
#[command]
async fn load_large_file(path: String) -> Result<String, String> {
    tokio::fs::read_to_string(path)
        .await
        .map_err(|e| e.to_string())
}
```

## Related
- **Pillar H**: Policy (access control patterns)
- **Rule**: `debugging.md` (error handling for file operations)
- **Tauri Docs**: https://tauri.app/develop/
