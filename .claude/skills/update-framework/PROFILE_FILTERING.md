# Update Framework - Profile-Based Filtering

Complete guide to automatic profile detection and rule filtering.

## Table of Contents

- [Overview](#overview)
- [How Profile Detection Works](#how-profile-detection-works)
- [Profile Configurations](#profile-configurations)
- [Filter Logic](#filter-logic)
- [Fallback to Questionnaire](#fallback-to-questionnaire)
- [Example Usage](#example-usage)

---

## Overview

**Problem**: Tech stack questionnaire was repetitive on every update. Users answered the same questions even though the project's profile doesn't change.

**Solution**: Auto-detect profile from `.framework-install` file and load rules from profile configuration.

**Benefits:**
- ✅ **No repetitive questions** - Profile already known from init-project
- ✅ **Consistent filtering** - Same rules every time based on profile
- ✅ **Automatic** - Works without user interaction
- ✅ **Fallback available** - Questionnaire used if config missing

---

## How Profile Detection Works

### Step 1: Read `.framework-install` File

The skill reads the `.framework-install` file from the target project:

```markdown
# Framework Installation

**Profile**: minimal
**Version**: 1.0.0
**Installed**: 2026-03-12
**Project**: my-library
```

### Step 2: Extract Profile Name

Parse the profile name from the markdown:

```bash
PROFILE=$(grep "^**Profile**:" .framework-install | sed 's/**Profile**: //')
# Returns: "minimal"
```

### Step 3: Load Profile Configuration

Load the corresponding profile JSON from the framework:

```bash
PROFILE_FILE="$FRAMEWORK_ROOT/.claude/profiles/$PROFILE.json"
cat "$PROFILE_FILE"
```

Example `minimal.json`:

```json
{
  "name": "Minimal (Learning)",
  "pillars": ["A", "B", "K"],
  "rules": [
    "workflow",
    "naming",
    "debugging",
    "typescript-strict",
    "typescript-nominal-types",
    "clean-architecture"
  ],
  ...
}
```

### Step 4: Extract Rules List

Get the `rules` array from the profile configuration:

```bash
PROFILE_RULES=$(jq -r '.rules[]' "$PROFILE_FILE")
# Returns:
# workflow
# naming
# debugging
# typescript-strict
# typescript-nominal-types
# clean-architecture
```

### Step 5: Filter During Sync

Only copy rules that exist in the profile's rules list:

```bash
for rule in $AVAILABLE_RULES; do
  if echo "$PROFILE_RULES" | grep -q "^$rule$"; then
    # Copy this rule
    cp "$SOURCE/.claude/rules/$rule.md" "$TARGET/.claude/rules/"
  else
    # Skip this rule (not in profile)
    echo "Skipped: $rule (not in $PROFILE profile)"
  fi
done
```

---

## Profile Configurations

### Minimal Profile

**Use case**: Learning projects, proof-of-concepts, simple libraries

**Pillars**: 3 (A, B, K)
**Rules**: ~15 rules

```json
{
  "name": "Minimal (Learning)",
  "pillars": ["A", "B", "K"],
  "rules": [
    "workflow",
    "naming",
    "debugging",
    "typescript-strict",
    "typescript-nominal-types",
    "clean-architecture"
  ]
}
```

**What gets synced**:
- ✅ Core workflow rules
- ✅ Basic TypeScript rules
- ✅ Clean architecture fundamentals
- ❌ Frontend rules (React, design system)
- ❌ Backend rules (Lambda, saga, API design)
- ❌ Infrastructure rules (AWS CDK, secrets, monitoring)

**Result**: ~52 items synced (37 items filtered out)

### Node-Lambda Profile

**Use case**: Backend APIs, serverless microservices

**Pillars**: 6 (A, B, K, M, Q, R)
**Rules**: ~20 rules

```json
{
  "name": "Node.js + AWS Lambda",
  "pillars": ["A", "B", "K", "M", "Q", "R"],
  "rules": [
    "workflow",
    "saga",
    "lambda-typescript-esm",
    "lambda-layer-deployment",
    "cdk-deploy",
    "naming",
    "debugging",
    "typescript-strict",
    "typescript-nominal-types",
    "clean-architecture",
    "service-layer",
    "diagnostic-export-logging"
  ]
}
```

**What gets synced**:
- ✅ Core workflow rules
- ✅ TypeScript rules
- ✅ Backend rules (saga, Lambda, API design)
- ✅ Infrastructure rules (AWS CDK, secrets, monitoring)
- ❌ Frontend rules (React, design system, state management)

**Result**: ~77 items synced (12 items filtered out)

### React-AWS Profile

**Use case**: Full-stack web applications

**Pillars**: 7 (A, B, K, L, M, Q, R)
**Rules**: ~25 rules

```json
{
  "name": "React + AWS Lambda",
  "pillars": ["A", "B", "K", "L", "M", "Q", "R"],
  "rules": [
    "workflow",
    "headless",
    "design-system",
    "zustand-hooks",
    "views",
    "saga",
    "lambda-typescript-esm",
    "lambda-layer-deployment",
    "cdk-deploy",
    "naming",
    "debugging",
    "typescript-strict",
    "typescript-nominal-types",
    "clean-architecture",
    "service-layer",
    "diagnostic-export-logging"
  ]
}
```

**What gets synced**:
- ✅ Core workflow rules
- ✅ TypeScript rules
- ✅ Frontend rules (React, design system, Zustand, headless UI)
- ✅ Backend rules (saga, Lambda, API design)
- ✅ Infrastructure rules (AWS CDK, secrets, monitoring)

**Result**: ~89 items synced (all rules included)

---

## Filter Logic

### Implementation

```bash
#!/bin/bash

# 1. Detect profile from .framework-install
detect_profile() {
  local target_dir="$1"
  local install_file="$target_dir/.framework-install"

  if [ -f "$install_file" ]; then
    grep "^**Profile**:" "$install_file" | sed 's/**Profile**: //'
  else
    echo ""  # Return empty if not found
  fi
}

# 2. Load profile configuration
load_profile_rules() {
  local profile="$1"
  local framework_root="$2"
  local profile_file="$framework_root/.claude/profiles/$profile.json"

  if [ -f "$profile_file" ]; then
    jq -r '.rules[]' "$profile_file"
  else
    echo ""  # Return empty if profile not found
  fi
}

# 3. Check if rule is in profile
rule_in_profile() {
  local rule="$1"
  local profile_rules="$2"

  echo "$profile_rules" | grep -q "^$rule$"
}

# 4. Filter rules during sync
sync_rules_with_filter() {
  local source_dir="$1"
  local target_dir="$2"
  local profile_rules="$3"

  local copied=0
  local skipped=0

  for rule_file in "$source_dir"/.claude/rules/*.md; do
    rule_name=$(basename "$rule_file" .md)

    if rule_in_profile "$rule_name" "$profile_rules"; then
      cp "$rule_file" "$target_dir/.claude/rules/"
      ((copied++))
    else
      echo "⏭️  Skipped: $rule_name (not in profile)"
      ((skipped++))
    fi
  done

  echo "✅ Copied: $copied rules"
  echo "⏭️  Skipped: $skipped rules (filtered by profile)"
}
```

### Usage Example

```bash
# Detect profile
PROFILE=$(detect_profile "/path/to/target/project")

if [ -n "$PROFILE" ]; then
  echo "Profile detected: $PROFILE"

  # Load profile rules
  PROFILE_RULES=$(load_profile_rules "$PROFILE" "$FRAMEWORK_ROOT")

  # Sync with filter
  sync_rules_with_filter "$SOURCE" "$TARGET" "$PROFILE_RULES"
else
  echo "No profile detected, using questionnaire fallback"
  # Run questionnaire logic
fi
```

---

## Fallback to Questionnaire

### When Fallback Triggers

The questionnaire fallback is used when:

1. **No `.framework-install` file** - Project initialized without framework
2. **Profile not recognized** - File exists but profile name invalid
3. **Profile JSON missing** - Profile name valid but JSON file doesn't exist in framework

### Fallback Behavior

```bash
if [ -z "$PROFILE" ]; then
  echo "ℹ️  No profile detected in .framework-install"
  echo "ℹ️  Using tech stack questionnaire for filtering"
  echo ""

  # Run original questionnaire logic
  run_tech_stack_questionnaire
  generate_filter_config
  save_framework_config
fi
```

### Questionnaire Questions

Same 5 questions as before:

1. What type of project? (Web app, Backend API, CLI tool, Desktop app, Mobile app, Library)
2. Frontend framework? (React, Vue, Svelte, None)
3. Backend? (Node.js Lambda, Python FastAPI, Go, None)
4. Cloud provider? (AWS, GCP, Azure, None)
5. Database? (DynamoDB, PostgreSQL, MongoDB, None)

**Result**: Generates `.claude/framework-config.json` with filter configuration

---

## Example Usage

### Example 1: Update Framework (Profile Auto-Detected)

```bash
$ cd ~/dev/ai-dev
$ /update-framework ../my-app

Profile detected: minimal
Loading profile configuration...
✅ Profile: Minimal (Learning) - 3 Pillars, 15 rules

Syncing framework components:
  📚 Pillars: 3 synced (15 skipped by profile)
  📋 Rules: 15 synced (25 skipped by profile)
  📖 Workflow: 5 synced
  ⚡ Skills: 12 synced

Total: 52 items synced (37 filtered out by profile)
```

### Example 2: Update Framework (No Profile, Uses Questionnaire)

```bash
$ cd ~/dev/ai-dev
$ /update-framework ~/projects/new-app

ℹ️  No profile detected in .framework-install
ℹ️  Using tech stack questionnaire for filtering

Tech Stack Questionnaire:
1. Project type: Web app
2. Frontend: React
3. Backend: Node.js Lambda
4. Cloud: AWS
5. Database: DynamoDB

Generated filter configuration:
  Include: react, lambda, aws-cdk, dynamodb
  Exclude: vue, python, gcp, mongodb

Syncing framework components:
  📚 Pillars: 7 synced
  📋 Rules: 25 synced (15 filtered by tech stack)
  📖 Workflow: 6 synced
  ⚡ Skills: 18 synced

Total: 89 items synced (filtered by questionnaire)
```

### Example 3: Force Questionnaire with --reconfigure

```bash
$ cd ~/dev/ai-dev
$ /update-framework ../my-app --reconfigure

Profile detected: minimal
⚠️  --reconfigure flag: Ignoring profile, using questionnaire

Tech Stack Questionnaire:
...
```

---

## Benefits Over Questionnaire

| Aspect | Questionnaire | Profile-Based |
|--------|--------------|---------------|
| **Initial setup** | 5 questions | Automatic |
| **Updates** | 5 questions every time | Automatic (0 questions) |
| **Consistency** | Depends on answers | 100% consistent |
| **Speed** | ~30 seconds | ~5 seconds |
| **User interaction** | Always required | None required |
| **Accuracy** | User may answer differently | Always correct |

---

## Migration Guide

### For Existing Projects (No .framework-install)

When you run `/update-framework` on a project without `.framework-install`:

1. Questionnaire automatically runs (fallback behavior)
2. After sync completes, consider adding `.framework-install`:

```markdown
# Framework Installation

**Profile**: node-lambda
**Version**: 1.0.0
**Installed**: 2026-03-12
**Project**: my-api
```

3. Future updates will auto-detect profile (no more questionnaire)

### For New Projects (From init-project)

Projects initialized with `init-project.sh` already have `.framework-install`:

1. Profile auto-detected on first update
2. No questionnaire needed
3. Consistent filtering based on profile

---

**Version**: 2.0.0 (Profile-based filtering)
**Last Updated**: 2026-03-12
**Replaces**: FILTERING.md (questionnaire-based approach)
