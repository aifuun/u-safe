# Filter Implementation Guide

## Overview

This document explains how to implement intelligent filtering in the update-framework skill based on tech stack questionnaire responses.

## Filter Configuration Structure

```typescript
interface FilterConfig {
  rules: {
    include_categories?: string[];     // e.g., ["core", "architecture", "frontend"]
    include_files?: string[];          // e.g., ["infrastructure/tauri-stack.md"]
    include_patterns?: string[];       // e.g., ["frontend/react-*.md"]
    exclude_patterns?: string[];       // e.g., ["backend/lambda-*.md"]
  };
  skills: {
    include?: string[];                // e.g., ["adr", "plan", "review"]
    exclude?: string[];                // e.g., []
  };
  pillars: {
    // Always sync all pillars (no filtering)
  };
  workflow: {
    // Always sync all workflow (no filtering)
  };
}
```

## Implementation Steps

### Step 0A: Check for Existing Configuration

Before showing questionnaire, check if target project already has configuration:

```bash
# Check if .claude/framework-config.json exists
if [ -f ../u-safe/.claude/framework-config.json ]; then
  echo "Found existing configuration"
  # Option 1: Use existing config
  # Option 2: Ask if user wants to reconfigure
fi
```

### Step 0B: Show Tech Stack Questionnaire

Use AskUserQuestion tool with 5 questions:

```typescript
{
  questions: [
    {
      question: "What type of project is this?",
      header: "Project Type",
      multiSelect: false,
      options: [
        {
          label: "Web Application",
          description: "Full-stack web app or SPA"
        },
        {
          label: "Desktop Application (Tauri)",
          description: "Cross-platform desktop app using Tauri"
        },
        // ... other options
      ]
    },
    // ... other 4 questions
  ]
}
```

### Step 0C: Generate Filter Configuration

Based on questionnaire answers, generate filter config:

```typescript
function generateFilterConfig(answers: Answers): FilterConfig {
  const config: FilterConfig = {
    rules: {
      include_categories: [],
      include_files: [],
      include_patterns: [],
      exclude_patterns: []
    },
    skills: {
      include: [],
      exclude: []
    }
  };

  // Step 1: Apply project type filters
  applyProjectTypeFilters(config, answers.projectType);

  // Step 2: Apply frontend filters
  applyFrontendFilters(config, answers.frontend);

  // Step 3: Apply backend filters
  applyBackendFilters(config, answers.backend);

  // Step 4: Apply cloud filters
  applyCloudFilters(config, answers.cloud);

  // Step 5: Apply database filters
  applyDatabaseFilters(config, answers.database);

  return config;
}
```

### Step 0D: Apply Filter Logic

#### Project Type Mapping

```typescript
function applyProjectTypeFilters(config: FilterConfig, projectType: string) {
  switch (projectType) {
    case "Desktop Application (Tauri)":
      config.rules.include_categories = ["core", "architecture", "frontend", "languages"];
      config.rules.include_files = ["infrastructure/tauri-stack.md"];
      config.rules.exclude_patterns = [
        "backend/lambda-*.md",
        "backend/external-api-*.md",
        "infrastructure/aws-*.md",
        "infrastructure/cdk-*.md",
        "infrastructure/lambda-*.md"
      ];
      break;

    case "Backend API":
      config.rules.include_categories = ["core", "architecture", "backend", "languages", "infrastructure"];
      config.rules.exclude_patterns = ["frontend/*.md"];
      break;

    case "CLI Tool":
    case "Library/Framework":
      config.rules.include_categories = ["core", "architecture", "languages", "development"];
      config.rules.exclude_patterns = [
        "frontend/*.md",
        "backend/*.md",
        "infrastructure/*.md"
      ];
      break;

    default: // Web Application
      config.rules.include_categories = ["core", "architecture", "frontend", "backend", "languages", "infrastructure"];
      break;
  }
}
```

#### Frontend Framework Mapping

```typescript
function applyFrontendFilters(config: FilterConfig, frontend: string) {
  switch (frontend) {
    case "React 19":
      config.rules.include_patterns?.push(
        "frontend/stores.md",
        "frontend/views.md",
        "frontend/zustand-*.md",
        "frontend/design-system.md",
        "frontend/css.md"
      );
      break;

    case "Vue 3":
    case "Svelte 5":
      config.rules.include_patterns?.push(
        "frontend/design-system.md",
        "frontend/css.md"
      );
      config.rules.exclude_patterns?.push(
        "frontend/zustand-*.md",
        "frontend/stores.md"
      );
      break;

    case "No frontend":
      config.rules.exclude_patterns?.push("frontend/*.md");
      break;
  }
}
```

#### Backend Technology Mapping

```typescript
function applyBackendFilters(config: FilterConfig, backend: string) {
  switch (backend) {
    case "Tauri (Rust)":
      config.rules.include_files?.push("infrastructure/tauri-stack.md");
      config.rules.exclude_patterns?.push(
        "backend/lambda-*.md",
        "backend/saga.md",
        "backend/external-api-*.md"
      );
      break;

    case "No backend":
      config.rules.exclude_patterns?.push("backend/*.md");
      break;

    // Other backends keep default backend rules
  }
}
```

#### Cloud Provider Mapping

```typescript
function applyCloudFilters(config: FilterConfig, cloud: string[]) {
  if (cloud.includes("AWS")) {
    config.rules.include_patterns?.push(
      "infrastructure/aws-*.md",
      "infrastructure/cdk-*.md",
      "infrastructure/lambda-*.md"
    );
  }

  if (cloud.includes("No cloud")) {
    config.rules.exclude_patterns?.push(
      "infrastructure/aws-*.md",
      "infrastructure/cdk-*.md",
      "infrastructure/lambda-*.md",
      "backend/lambda-*.md"
    );
  }
}
```

### Step 0E: Save Configuration

Save generated config to target project:

```bash
# Save to .claude/framework-config.json
mkdir -p ../u-safe/.claude
cat > ../u-safe/.claude/framework-config.json << 'EOF'
{
  "version": "1.0",
  "generated": "2024-03-08T12:00:00Z",
  "techStack": {
    "projectType": "Desktop Application (Tauri)",
    "frontend": "React 19",
    "backend": "Tauri (Rust)",
    "cloud": ["No cloud"],
    "database": ["SQLite"]
  },
  "filterConfig": {
    "rules": {
      "include_categories": ["core", "architecture", "frontend", "languages"],
      "include_files": ["infrastructure/tauri-stack.md"],
      "exclude_patterns": [
        "backend/lambda-*.md",
        "infrastructure/aws-*.md",
        "infrastructure/cdk-*.md"
      ]
    },
    "skills": {
      "exclude": []
    }
  }
}
EOF
```

## Applying Filters During Sync

### For update-rules

```bash
# Read filter config
FILTER_CONFIG=$(cat ../u-safe/.claude/framework-config.json)

# Extract rules to sync
INCLUDE_CATEGORIES=$(echo "$FILTER_CONFIG" | jq -r '.filterConfig.rules.include_categories[]')
EXCLUDE_PATTERNS=$(echo "$FILTER_CONFIG" | jq -r '.filterConfig.rules.exclude_patterns[]')

# Iterate through source rules
for rule in framework/.claude-template/rules/**/*.md; do
  # Check if rule matches include categories
  category=$(dirname "$rule" | xargs basename)

  if [[ " $INCLUDE_CATEGORIES " =~ " $category " ]]; then
    # Check if not excluded
    excluded=false
    for pattern in $EXCLUDE_PATTERNS; do
      if [[ "$rule" == *"$pattern"* ]]; then
        excluded=true
        break
      fi
    done

    if [ "$excluded" = false ]; then
      # Copy this rule
      echo "✅ Including: $rule"
      cp "$rule" "../u-safe/.claude/rules/$rule"
    else
      echo "⏭️  Excluding: $rule (matches exclusion pattern)"
    fi
  else
    echo "⏭️  Skipping: $rule (category not included)"
  fi
done
```

### For update-skills

Skills filtering is simpler - usually sync all unless specific exclusions:

```bash
# Read filter config
EXCLUDE_SKILLS=$(echo "$FILTER_CONFIG" | jq -r '.filterConfig.skills.exclude[]')

# Iterate through source skills
for skill_dir in .claude/skills/*/; do
  skill_name=$(basename "$skill_dir")

  if [[ " $EXCLUDE_SKILLS " =~ " $skill_name " ]]; then
    echo "⏭️  Excluding skill: $skill_name"
  else
    echo "✅ Including skill: $skill_name"
    cp -r "$skill_dir" "../u-safe/.claude/skills/"
  fi
done
```

## Display Filter Summary

Before executing sync, show what will be filtered:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Tech Stack Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project Type: Desktop Application (Tauri)
Frontend: React 19
Backend: Tauri (Rust)
Cloud: No cloud
Database: SQLite

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Smart Filtering Active
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Rules:
  ✅ Including: core (7), architecture (6), frontend (6), languages (3)
  ✅ Including: infrastructure/tauri-stack.md
  ⏭️  Excluding: backend/lambda-* (3 files)
  ⏭️  Excluding: infrastructure/aws-* (5 files)
  ⏭️  Excluding: infrastructure/cdk-* (3 files)

Result: 25 rules will be synced (18 excluded as not relevant)

Skills:
  ✅ Including: All 16 skills

Pillars:
  ✅ Including: All 18 pillars

Workflow:
  ✅ Including: All 12 workflow files

Total: 71 items (vs 89 without filtering)
```

## Reconfiguration Support

Add flag to reconfigure:

```bash
cd ~/dev/ai-dev
/update-framework ../u-safe --reconfigure

# This will:
1. Ignore existing .claude/framework-config.json
2. Show questionnaire again
3. Generate new configuration
4. Save and apply new filters
```

## Testing

Test filter logic with different tech stacks:

1. **Tauri + React**: Should exclude AWS/Lambda, include Tauri
2. **Backend API + AWS**: Should exclude frontend, include AWS
3. **CLI Tool**: Should exclude frontend/backend/infrastructure
4. **Web App + Vue**: Should exclude React-specific, include Vue patterns

## Error Handling

- If questionnaire is cancelled, abort sync
- If no answers provided, use default (sync everything)
- If invalid filter config, warn and sync everything
- If filter excludes everything, warn user

## Performance

- Filtering adds ~5-10 seconds to analysis phase
- But reduces sync time by skipping irrelevant files
- Overall time should be similar or faster
- User benefit: Cleaner project with only relevant rules
