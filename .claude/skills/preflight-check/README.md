# Preflight Check Skill

Pre-execution environment validator for work-issue workflow.

## Quick Start

```bash
# Run preflight check
/preflight-check

# Check specific category
/preflight-check --category git

# Report without auto-fix
/preflight-check --no-fix
```

## What It Does

Validates environment configuration before work-issue execution:

1. **Permissions** - .claude/settings.json configured
2. **Framework** - .claude/, .prot/ directories exist
3. **Git** - Repository valid, branch correct, working directory clean
4. **GitHub** - gh CLI installed and authenticated
5. **Project** - package.json, src/, .gitignore exist
6. **Dependencies** - Node.js, npm, node_modules installed
7. **Quality** - Test and lint scripts configured

## Auto-Fix Capabilities

| Priority | Auto-Fix | Examples | Confirmation |
|----------|----------|----------|--------------|
| **P1 - Fast** | ✅ Yes | Create directories, create files | ❌ No |
| **P2 - Slow** | ✅ Yes | configure-permissions, git stash, npm install | ✅ Yes |
| **P3 - Manual** | ❌ No | gh auth login, install Node.js | N/A |

## Files

```
.claude/skills/preflight-check/
├── SKILL.md           # Main documentation
├── README.md          # This file
├── INTEGRATION.md     # work-issue integration guide
├── scripts/
│   └── preflight.py   # Main check script
└── tests/
    └── README.md      # Test documentation
```

## Usage Examples

### Example 1: Clean Environment

```bash
$ /preflight-check

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Preflight Check Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ All checks passed (7/7)

Status: ✅ READY
Time: 2.8s

Proceed with: /work-issue [issue-number]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Example 2: Auto-Fix

```bash
$ /preflight-check

Checking environment...

🔧 Auto-fixing issues:
  🔧 Permissions not configured → /configure-permissions --safe (2s)
  🔧 .claude/plans/ missing → Creating directories (0.1s)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Preflight Check Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Passed (5/7)
🔧 Auto-Fixed (2/7):
  🔧 Permissions configured
  🔧 Framework directories created

Status: ✅ READY
Time: 3.2s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Example 3: Blocked

```bash
$ /preflight-check

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Preflight Check Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Passed (5/7)
❌ Blocked (2/7):
  ❌ GitHub CLI not authenticated
     Fix: gh auth login

  ❌ Git remote 'origin' not configured
     Fix: git remote add origin <url>

Status: ❌ BLOCKED
Time: 3.1s

Fix issues above and re-run: /preflight-check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Integration with work-issue

Automatically called at Phase 0 of work-issue workflow:

```
/work-issue #23

→ Phase 0: /preflight-check... ✅ (3.2s)
→ Phase 1: /start-issue... ✅
→ Phase 1.5: /eval-plan... ✅
→ Phase 2: /execute-plan... ✅
→ Phase 2.5: /review... ✅
→ Phase 3: /finish-issue... ✅
```

See [INTEGRATION.md](INTEGRATION.md) for implementation details.

## Troubleshooting

### Common Issues

**1. "Permission denied" when running script**
```bash
chmod +x .claude/skills/preflight-check/scripts/preflight.py
```

**2. "GitHub CLI not authenticated"**
```bash
gh auth login
```

**3. "npm install failed"**
```bash
# Check package.json exists
ls package.json

# Try manual install
npm install
```

**4. "Git remote not configured"**
```bash
git remote add origin https://github.com/user/repo.git
```

## Performance

- **Execution time**: 2-5 seconds (parallel checks)
- **Auto-fix time**: +0-50 seconds (depending on issues)
- **Optimization**: 50% faster than serial execution (8-10s → 3-5s)

## Development

### Running Directly

```bash
# From project root
python .claude/skills/preflight-check/scripts/preflight.py

# With options
python .claude/skills/preflight-check/scripts/preflight.py --no-fix
python .claude/skills/preflight-check/scripts/preflight.py --category git
```

### Testing

```bash
cd .claude/skills/preflight-check/tests
# Read test scenarios
cat README.md
```

## Related Skills

- **/configure-permissions** - Fix permission configuration
- **/work-issue** - Calls this skill at Phase 0
- **/overview** - Comprehensive project status

## Version

**1.0.0** - Initial release (2026-03-18)

## License

MIT - Part of AI Development Framework
