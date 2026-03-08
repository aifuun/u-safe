# ⚠️ DEPRECATED - Backup Directory

This directory contains **deprecated legacy skills** that should **NOT** be used.

## ❌ DO NOT USE

All files in this directory are kept for **reference only** and should not be executed or imported.

## ✅ Use Instead

| Deprecated (bak/) | Use Instead |
|-------------------|-------------|
| `bak/status/status.sh` | `scripts/status/status.sh` |
| `bak/update-*/update-*.sh` | `scripts/update-*/update-*.sh` (future) |
| Other legacy skills | Updated skills in `.claude/skills/` |

## 📁 Current Directory Structure

```
.claude/skills/
├── bak/                    # ❌ DEPRECATED - DO NOT USE
│   ├── status/            # Replaced by scripts/status/
│   ├── update-*/          # Shell scripts to be moved to scripts/
│   └── ...                # Old skill versions
│
├── <active-skills>/       # ✅ Use these
│   ├── status/
│   ├── review/
│   ├── plan/
│   └── ...
```

## 🚮 Future Action

This directory may be removed in a future cleanup once all legacy scripts have been:
1. Migrated to `scripts/` (for shell scripts)
2. Updated in `.claude/skills/` (for skill definitions)
3. Verified to be no longer referenced

## 📝 Migration History

- **2026-03-07**: Renamed from `legacy/` to `bak/` to clearly mark as deprecated
- **2026-03-07**: Refactored `status/` to modular `scripts/status/`
- **Future**: Migrate remaining shell scripts to `scripts/`

---

**Last Updated**: 2026-03-07
**Status**: DEPRECATED - Reference Only
