# Status Scripts

Modular project status reporting system.

## 📁 Directory Structure

```
scripts/status/
├── status.sh                    # Main entry point
├── lib/
│   └── common.sh               # Shared utilities (colors, logging, helpers)
├── modules/
│   ├── collect-git.sh          # Git status data collection
│   ├── collect-framework.sh    # Framework configuration analysis
│   ├── collect-work.sh         # Active plans and issues
│   ├── detect-patterns.sh      # Code pattern detection
│   ├── calculate-health.sh     # Health score calculation
│   └── format-terminal.sh      # Terminal output formatting
└── templates/
    └── combined-report.html    # HTML report template
```

## 🚀 Usage

```bash
# Full status report (terminal + HTML)
./scripts/status/status.sh

# Terminal only (faster)
./scripts/status/status.sh --text-only

# HTML only
./scripts/status/status.sh --html-only

# Generate without opening browser
./scripts/status/status.sh --no-open

# Help
./scripts/status/status.sh --help
```

## 📊 What It Collects

### 1. Git Status
- Current branch
- Latest commit
- Staged/unstaged/untracked files count

### 2. Framework Configuration
- Installed profile (minimal/node-lambda/react-aws)
- Enabled Pillars
- Rules and commands count

### 3. Active Work
- Active plans (in .claude/plans/active/)
- Open GitHub issues

### 4. Code Patterns
- Nominal types (branded IDs)
- Airlock validation
- Saga patterns
- Headless UI structure

### 5. Health Score (0-100)
- Framework installed: +20
- Has tests: +20
- Uses nominal types: +15
- Uses airlock: +15
- Has active plans: +10
- Clean git status: +10
- Has documentation: +10

## 🔧 Modular Design

Each module is self-contained and can be used independently:

```bash
# Use individual modules
source scripts/status/modules/collect-git.sh
git_data=$(collect_git_status)
echo "$git_data"

source scripts/status/modules/calculate-health.sh
score=$(calculate_health_score "react-aws" 50 '["nominal-types"]' '[]' 0 0)
echo "Health: $score/100"
```

## 📝 Adding New Modules

1. Create module in `modules/`:
   ```bash
   # modules/my-module.sh
   my_function() {
       # Your logic here
       echo "result"
   }
   ```

2. Source in `status.sh`:
   ```bash
   source "$SCRIPT_DIR/modules/my-module.sh"
   ```

3. Use in data collection phase:
   ```bash
   MY_DATA=$(my_function)
   ```

## 🎯 Benefits Over Legacy Version

| Legacy (327 lines) | New Modular |
|-------------------|-------------|
| Single monolithic file | 7 focused modules |
| Hard to test | Each module testable |
| Hard to extend | Easy to add modules |
| Mixed concerns | Separated concerns |
| In .claude/skills/legacy/ | In scripts/ (proper location) |

## 🔗 Integration with Skills

Update `.claude/skills/status/SKILL.md`:

```markdown
### Task #6: Generate HTML Report

Execute the status script:

\`\`\`bash
scripts/status/status.sh --no-open
\`\`\`
```

---

**Version:** 1.0.0
**Refactored from:** `.claude/skills/legacy/status/status.sh`
**Date:** 2026-03-07
