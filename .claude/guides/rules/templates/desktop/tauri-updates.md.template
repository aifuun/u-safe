---
category: "desktop"
title: "Tauri Updates"
description: "Auto-update system"
tags: [rust, tauri]
profiles: [tauri]
paths: ['**/*.rs']
version: "1.0.0"
last_updated: "2026-03-27"
---

# Tauri Auto-Update Rules

> **Goal**: Automatic updates with user control and rollback capability.
> **Pattern**: Check on startup, download in background, prompt user, install on restart.

---

## Quick Check (30 seconds)
- [ ] Tauri updater plugin configured in `tauri.conf.json`
- [ ] Update check runs on app startup (not blocking)
- [ ] User prompted before installing updates (no forced updates)
- [ ] Download progress tracked and displayed
- [ ] Fallback mechanism if update fails

## Core Pattern: Update Check

**Frontend:**
```typescript
import { checkUpdate, installUpdate } from '@tauri-apps/api/updater';
import { relaunch } from '@tauri-apps/api/process';

async function checkForUpdates() {
  try {
    const { shouldUpdate, manifest } = await checkUpdate();

    if (shouldUpdate) {
      const userConfirmed = confirm(
        `Version ${manifest?.version} available. Update now?`
      );

      if (userConfirmed) {
        await installUpdate();
        await relaunch();
      }
    }
  } catch (error) {
    console.error('Update check failed:', error);
  }
}
```

**tauri.conf.json:**
```json
{
  "updater": {
    "active": true,
    "endpoints": [
      "https://releases.example.com/{{target}}/{{current_version}}"
    ],
    "dialog": false,
    "pubkey": "YOUR_PUBLIC_KEY"
  }
}
```

## Anti-Patterns

❌ **Forced updates without consent**
```typescript
// BAD - No user control
await installUpdate(); // Installs immediately
await relaunch();
```

❌ **Blocking UI during check**
```typescript
// BAD - Freezes app on startup
const update = await checkUpdate(); // Blocks render
```

## Related
- **Pillar M**: Saga (update workflow orchestration)
- **Rule**: `performance.md` (background tasks)
