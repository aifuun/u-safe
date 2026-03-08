---
name: validate
description: |
  Validate framework configuration - schemas, profiles, and project metadata.
  Runs 3-phase validation with detailed error reporting and fix suggestions.
allowed-tools: Read, Glob, Grep, Bash(npm *)
---

# Framework Validator

You are a configuration validator ensuring framework integrity and correctness.

## Your Task

Validate framework configuration in 3 phases:
1. **Schema Validation** - JSON schemas are valid JSON Schema Draft 2020-12
2. **Profile Validation** - Profiles match schema and reference valid pillars/rules
3. **Metadata Validation** - Project metadata is consistent and up-to-date

## Implementation

### Phase 1: Schema Validation

**Check**: All `.schema.json` files in `framework/schemas/`

For each schema file:
```
1. Read the file (must be valid JSON)
2. Verify required fields:
   - $schema: "https://json-schema.org/draft/2020-12/schema"
   - type: (object, array, string, etc.)
   - title: (descriptive name)
3. Validate schema syntax (proper property definitions)
4. Check for common errors:
   - Missing $schema
   - Invalid property definitions
   - Circular references
```

**Expected Schemas**:
- `profile.schema.json` - Profile configuration schema
- `metadata.schema.json` - Framework installation metadata schema
- Others in `framework/schemas/`

**Output Example**:
```
✓ profile.schema.json
  Title: Profile Configuration Schema
  Properties: 10 (pillars, rules, estimatedSize, etc.)
  Status: Valid

✓ metadata.schema.json
  Title: Framework Installation Metadata
  Properties: 8 (profile, version, installDate, etc.)
  Status: Valid

Summary: 2 schemas valid, 0 invalid
```

### Phase 2: Profile Validation

**Check**: All `.json` files in `framework/profiles/`

For each profile:
```
1. Read profile JSON
2. Validate against profile.schema.json
3. Check referenced pillars exist:
   - For each pillar code in pillars array
   - Verify directory exists in .prot-template/pillars/
   - Verify pillar-*.md files exist
4. Check referenced rules exist:
   - For each rule in rules array
   - Verify rule file exists in .claude-template/rules/
5. Verify size consistency:
   - estimatedSize vs actual pillar/rule count
   - Compare with similar profiles
```

**Expected Profiles**:
- `minimal.json` - 3 pillars, ~12 rules
- `react-frontend.json` - 4 pillars, ~9 rules
- `node-lambda.json` - 6 pillars, ~11 rules
- `python-fastapi.json` - 4 pillars, ~10 rules
- `react-aws.json` - 7 pillars, ~14 rules
- `nextjs-aws.json` - 15+ pillars, ~16 rules

**Output Example**:
```
✓ minimal.json
  Name: Minimal Starter
  Pillars: 3/18 (A, B, K)
  Rules: 6
  Size: small
  Status: Valid

✓ react-aws.json
  Name: React + AWS Full-Stack
  Pillars: 7/18
  Rules: 14
  Size: large
  Status: Valid

Summary: 6 profiles valid, 0 invalid
```

### Phase 3: Metadata Validation

**Check**: `.ai-dev-meta.json` files (if project initialized with tracking)

Only runs if `.ai-dev-meta.json` exists AND not in `--quick` mode.

```
1. Read metadata file
2. Validate against metadata.schema.json
3. Check version compatibility:
   - Metadata framework version vs current
   - Any breaking changes?
4. Verify file hashes:
   - Track integrity of critical files
   - Detect unauthorized modifications
5. Validate update history:
   - Timestamps are ordered
   - No gaps or anomalies
```

**Output Example**:
```
✓ Project Metadata Valid
  Framework Version: 1.0.0
  Profile: nextjs-aws
  Last Updated: 2026-02-27
  File Hash: matched
  Status: Up-to-date
```

## Usage Modes

### Default (Full Validation)
```
All 3 phases, detailed output, ~1 second
```

### Quick Mode (`--quick`)
```
Phases 1-2 only (schemas + profiles)
Skips metadata validation, ~0.3 seconds
```

### Specific Check (`validate schemas` or `validate profiles`)
```
Single phase only, detailed focus, ~0.1-0.3 seconds
```

## Error Handling

### Schema Error Example
```
❌ FAILED: metadata.schema.json
  Line 15: Invalid type definition
  Error: "type" must be string or array, got object
  Fix: Change type definition to valid value
```

### Profile Error Example
```
❌ FAILED: python-fastapi.json
  Referenced pillar "pillar-x" does not exist
  Valid Pillar IDs: A-R (18 total)
  Fix: Use valid pillar ID or verify pillar exists
```

### Metadata Error Example
```
⚠️ WARNING: .ai-dev-meta.json is outdated
  Last updated: 2 weeks ago
  Current metadata: 2 days old
  Fix: Run update-metadata.sh
```

## Output Format

### Success Case
```markdown
## Validation Results ✅

**Scope**: All
**Time**: 0.8s

| Component | Status | Count | Issues |
|-----------|--------|-------|--------|
| Schemas   | ✅ Pass | 3     | 0      |
| Profiles  | ✅ Pass | 6     | 0      |
| Metadata  | ✅ Pass | 1     | 0      |

Total: 3/3 Pass

✅ Framework configuration is valid!
```

### Failure Case
```markdown
## Validation Results ⚠️

**Scope**: All
**Time**: 0.6s

| Component | Status | Count | Issues |
|-----------|--------|-------|--------|
| Schemas   | ✅ Pass | 3     | 0      |
| Profiles  | ❌ Fail | 6     | 1      |
| Metadata  | ⏭️ Skipped | - | -      |

### Failures Detail

#### Profiles (1 error)

- `python-fastapi.json:15` - Referenced pillar "pillar-s" does not exist
  - **Fix**: Remove invalid pillar or use valid ID (A-R)
  - **Valid IDs**: A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R

### Recommended Actions

1. Fix profile validation error
2. Re-run: `validate profiles`
3. Then proceed with workflow
```

## Implementation Notes

- **Offline**: Works without network (validation only, no external calls)
- **Idempotent**: Safe to run multiple times
- **Non-destructive**: Only reads files, no modifications
- **Fast**: Designed for pre-commit hooks or CI/CD

---

This command ensures framework integrity. Use before:
- Creating new profiles
- Updating framework configuration
- Initializing projects
- CI/CD pipeline validation
