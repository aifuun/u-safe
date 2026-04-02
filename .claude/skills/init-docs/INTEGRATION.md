# init-docs Integration Guide

## Cross-Skill Workflow

### With /check-docs (Issue #223)

**Workflow:**
```
1. /init-docs              # Create documentation structure
2. Customize templates     # Add project-specific content
3. /check-docs             # Validate compliance with standards
4. Fix issues if needed    # Address validation errors
5. /check-docs --fix       # Auto-fix minor issues (if available)
```

**What init-docs creates:**
- `docs/` directory structure
- 8 template files with placeholders
- ADR index (docs/ADRs/README.md)
- Profile-specific directories

**What check-docs validates:**
- All required directories exist
- All mandatory files present
- Naming conventions followed
- ADR numbering correct
- Compliance score (0-100)

### With init-project.py

**Workflow:**
```
1. python3 scripts/init-project.py --profile=tauri --name=my-app
   # Creates .framework-install with profile

2. /init-docs
   # Auto-detects profile from .framework-install
   # Creates docs/ with tauri-specific structure

3. /check-docs
   # Validates compliance
```

**Why this order:**
- init-project.py sets the profile
- init-docs reads the profile
- check-docs validates the result

### With /adr (ADR Creation)

**Workflow:**
```
1. /init-docs              # Creates docs/ADRs/ directory
2. /adr "Use React hooks"  # Creates docs/ADRs/001-use-react-hooks.md
3. /check-docs             # Validates ADR numbering and structure
```

## Data Flow

```
.framework-install (profile)
        ↓
    /init-docs
        ↓
    docs/ structure
        ↓
   /check-docs
        ↓
  Compliance report
```

## File Dependencies

**init-docs reads:**
- `.framework-install` - Profile detection
- `package.json` - Project name, description
- `.claude/pillars/docs-templates/` - Template source

**init-docs creates:**
- `docs/` - All subdirectories
- `docs/*.md` - Template files
- `docs/ADRs/README.md` - ADR index

**check-docs reads:**
- `docs/` - Validates structure
- `.framework-install` - Profile-specific requirements
- `.claude/rules/documentation-structure.md` - Standards

## Profile-Specific Behavior

### tauri Profile
- Creates `docs/desktop/` for desktop app docs
- Templates include Tauri-specific sections
- No AWS/deployment sections

### tauri-aws Profile
- Creates `docs/desktop/` + `docs/aws/` + `docs/deployment/`
- Templates include both desktop and cloud sections
- AWS infrastructure docs

### nextjs-aws Profile
- Creates `docs/aws/` + `docs/deployment/`
- Templates include web app + cloud sections
- No desktop-specific docs

## Error Scenarios

### Scenario 1: check-docs finds missing directory

```
/init-docs              # Forgot to run
/check-docs             # ❌ Missing docs/ADRs/

Fix: /init-docs --force
```

### Scenario 2: Manual docs/ conflicts with init-docs

```
mkdir docs/             # Manual creation
/init-docs              # ❌ docs/ already exists

Fix: /init-docs --force  # Overwrite
```

### Scenario 3: Wrong profile used

```
/init-docs --profile tauri        # Wrong profile
/check-docs                       # ⚠️ Missing aws/ directory

Fix: /init-docs --profile tauri-aws --force
```

## Future Enhancements

- **Bidirectional sync**: Update templates when check-docs finds issues
- **Template versioning**: Track template updates across framework versions
- **Custom templates**: Allow project-specific template overrides
- **Auto-fix integration**: check-docs --fix calls init-docs to recreate missing files
