---
category: "desktop"
title: "Tauri Security"
description: "Security best practices"
tags: [rust, tauri]
profiles: [tauri]
paths: ['**/*.rs']
version: "1.0.0"
last_updated: "2026-03-27"
---

# Tauri Security Rules

> **Goal**: Defense-in-depth security for desktop applications.
> **Pattern**: Restrict capabilities, validate inputs, enforce CSP, minimize attack surface.

---

## Quick Check (30 seconds)
- [ ] Content Security Policy (CSP) enabled in `tauri.conf.json`
- [ ] Command allowlist restricts exposed Rust functions
- [ ] File system scope limits access to specific directories
- [ ] No `shell` or `http` commands exposed without validation
- [ ] IPC inputs validated on Rust side (never trust frontend)
- [ ] Dangerous APIs (`fs.writeFile`, `shell.execute`) require explicit user consent

## Core Pattern: Capability Allowlist

**tauri.conf.json:**
```json
{
  "tauri": {
    "allowlist": {
      "all": false,
      "fs": {
        "all": false,
        "readFile": true,
        "writeFile": true,
        "scope": ["$APPDATA/*", "$DOWNLOAD/*"]
      },
      "shell": {
        "all": false,
        "execute": false,
        "open": true
      },
      "http": {
        "all": false,
        "request": true,
        "scope": ["https://api.example.com/*"]
      }
    }
  }
}
```

## Core Pattern: Input Validation

**Backend (Rust):**
```rust
use tauri::command;
use std::path::PathBuf;

#[command]
fn save_file(path: String, content: String) -> Result<(), String> {
    // ✅ Validate path is within allowed scope
    let path_buf = PathBuf::from(&path);
    if !path_buf.starts_with("/safe/directory") {
        return Err("Invalid path".to_string());
    }

    // ✅ Sanitize content
    if content.len() > 1_000_000 {
        return Err("Content too large".to_string());
    }

    std::fs::write(path_buf, content)
        .map_err(|e| e.to_string())
}
```

## Anti-Patterns

❌ **Disabling CSP for convenience**
```json
// BAD - Disables security
{ "security": { "csp": null } }
```

✅ **Proper CSP configuration**
```json
{
  "security": {
    "csp": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
  }
}
```

❌ **Unrestricted file system access**
```json
// BAD - Allows access to entire file system
{ "fs": { "all": true } }
```

❌ **Exposing shell commands without validation**
```rust
// BAD - Command injection vulnerability
#[command]
fn run_command(cmd: String) -> String {
    std::process::Command::new("sh")
        .arg("-c")
        .arg(&cmd) // ⚠️ Arbitrary command execution!
        .output()
        .unwrap()
}
```

## Related
- **Pillar I**: Firewalls (boundary protection)
- **Rule**: `security.md` (general security practices)
- **Tauri Docs**: https://tauri.app/security/
