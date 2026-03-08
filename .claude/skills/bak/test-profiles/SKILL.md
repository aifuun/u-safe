---
name: test-profiles
description: |
  Test all framework profiles - verify init-project.sh correctly filters by profile.
  Quality assurance for profile system.
allowed-tools: Bash(bash *), Bash(npm *)
---

# Profile Tester

Verify framework profiles work correctly.

## Task

Test that profiles initialize correctly:
1. **Run init** - Initialize each profile
2. **Verify structure** - Check directories created
3. **Count pillars** - Verify correct count
4. **Count rules** - Verify correct count
5. **Report** - Show results

## Command

Execute: `bash scripts/verify-profiles.sh`

## What It Tests

For each of 6 profiles:
- ✅ Project initializes
- ✅ Correct directory structure
- ✅ Right pillars installed
- ✅ Right rules installed
- ✅ Config files present
- ✅ Installation marker correct

## Output Example

```
╔═══════════════════════════════════════════════╗
║  AI Development Framework - Profile Tests    ║
╚═══════════════════════════════════════════════╝

Testing Profile: minimal
✓ init-project.sh succeeds
✓ Directory .claude exists
✓ Directory .prot exists
✓ Pillar A installed
✓ Pillar B installed
✓ Pillar K installed
✓ Config files present

Testing Profile: react-aws
[...similar for each profile...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tests run:    72
Tests passed: 72
All tests passed! ✅
```

---

Ensures:
- Profiles initialize correctly
- Pillar filtering works
- Framework integrity
- Safe for distribution
