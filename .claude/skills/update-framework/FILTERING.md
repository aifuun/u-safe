# Update Framework - Smart Filtering with Tech Stack Questionnaire

**⚠️ DEPRECATED**: This questionnaire-based approach has been replaced by profile-based filtering in Issue #135.

**New approach**: See [PROFILE_FILTERING.md](PROFILE_FILTERING.md) for automatic profile detection from `.framework-install`.

**This document is kept** as reference for the fallback questionnaire mechanism when `.framework-install` is not found.

---

Complete guide to intelligent filtering based on tech stack configuration (FALLBACK ONLY).

## Table of Contents

- [Overview](#overview)
- [When to Run Questionnaire](#when-to-run-questionnaire)
- [Questionnaire Questions](#questionnaire-questions)
- [Generate Filter Configuration](#generate-filter-configuration)
- [Example Filter Results](#example-filter-results)
- [Display Filter Summary](#display-filter-summary)
- [Filter Implementation Details](#filter-implementation-details)

---

## Overview

**⚠️ Note**: Profile-based filtering is now the primary method. This questionnaire is used only as fallback.

**Problem**: Syncing all 89 framework items to every project wastes context and clutters navigation. A Tauri desktop app doesn't need AWS Lambda rules. A CLI tool doesn't need React documentation.

**Old Solution (Fallback)**: Tech stack questionnaire generates smart filter configuration that only syncs relevant items.

**New Solution (Primary)**: Auto-detect profile from `.framework-install` → See [PROFILE_FILTERING.md](PROFILE_FILTERING.md)

**Benefits:**
- ✅ Cleaner codebase (only relevant documentation)
- ✅ Faster context (Claude loads fewer files)
- ✅ Better navigation (less clutter)
- ✅ Lower maintenance (fewer irrelevant updates)

---

## When to Run Questionnaire (Fallback Scenarios)

**⚠️ Primary Method**: Profile-based auto-detection from `.framework-install` → See [PROFILE_FILTERING.md](PROFILE_FILTERING.md)

**Questionnaire runs only when**:
1. No `.framework-install` file found in target project
2. Profile name in `.framework-install` is invalid/unrecognized
3. Profile JSON file missing in framework
4. User explicitly uses `--reconfigure` flag

### 1. Fallback for Projects Without Profile

When `.framework-install` doesn't exist:

```bash
cd ~/dev/ai-dev && /update-framework ~/projects/legacy-app
```

**What happens:**
1. Tries to detect profile from `.framework-install` → **NOT FOUND**
2. Falls back to tech stack questionnaire
3. Runs 5 questions to determine tech stack
4. Generates filter configuration
5. Saves to `.claude/framework-config.json`
6. Applies filters during sync

**Note**: Projects initialized with `init-project.sh` always have `.framework-install`, so questionnaire is rarely needed.

### 2. No Questionnaire for Profile-Based Projects

When `.framework-install` exists:

```bash
cd ~/dev/ai-dev && /update-framework ../my-app
```

**What happens:**
1. Reads `.framework-install` → Profile detected (e.g., "minimal")
2. Loads `.claude/profiles/minimal.json`
3. Extracts rules array from profile
4. **Skips questionnaire** (uses profile filtering)
5. Applies profile-based filters during sync

### 3. Reconfigure Tech Stack (Force Questionnaire)

When tech stack changes or initial config was wrong:

```bash
cd ~/dev/ai-dev && /update-framework ~/projects/app --reconfigure
cd ~/dev/ai-dev && /update-framework ../my-app --reconfigure
```

**What happens:**
1. **Ignores** existing config
2. Runs questionnaire again
3. Generates new filter configuration
4. **Overwrites** previous config
5. Applies new filters during sync

**When to use --reconfigure:**
- Project migrated from Vue to React
- Started using AWS (need cloud rules now)
- Removed backend (don't need API rules anymore)
- Initial questionnaire answers were incorrect

---

## Questionnaire Questions

Use **AskUserQuestion** tool with these 5 questions:

### Question 1: Project Type

```
header: "Project Type"
question: "What type of project is this?"
options:
  - label: "Web Application"
    description: "Browser-based app with frontend and backend"
  - label: "Desktop Application (Tauri)"
    description: "Cross-platform desktop app using Tauri + Rust"
  - label: "Desktop Application (Electron)"
    description: "Cross-platform desktop app using Electron + Node"
  - label: "Mobile Application"
    description: "iOS/Android mobile app"
  - label: "Backend API"
    description: "Headless API service without frontend"
  - label: "CLI Tool"
    description: "Command-line interface tool"
  - label: "Library/Framework"
    description: "Reusable library or framework (npm package, etc.)"
```

### Question 2: Frontend Framework

```
header: "Frontend"
question: "Which frontend framework does this project use?"
options:
  - label: "React 19"
    description: "React 19 with modern patterns (Zustand, React Query, etc.)"
  - label: "Vue 3"
    description: "Vue 3 with Composition API"
  - label: "Svelte 5"
    description: "Svelte 5 with runes"
  - label: "Vanilla TypeScript"
    description: "No framework, just TypeScript"
  - label: "No frontend"
    description: "Backend-only or CLI project"
```

### Question 3: Backend Technology

```
header: "Backend"
question: "Which backend technology does this project use?"
options:
  - label: "Node.js + TypeScript"
    description: "Node.js backend with TypeScript"
  - label: "Tauri (Rust)"
    description: "Tauri backend (Rust commands)"
  - label: "Python + FastAPI"
    description: "Python backend with FastAPI framework"
  - label: "Go"
    description: "Go backend"
  - label: "Rust"
    description: "Pure Rust backend (not Tauri)"
  - label: "No backend"
    description: "Frontend-only or static site"
```

### Question 4: Cloud Provider

```
header: "Cloud"
question: "Which cloud provider(s) does this project use?"
multiSelect: true
options:
  - label: "AWS"
    description: "Amazon Web Services (Lambda, DynamoDB, S3, etc.)"
  - label: "GCP"
    description: "Google Cloud Platform"
  - label: "Azure"
    description: "Microsoft Azure"
  - label: "Self-hosted"
    description: "Self-hosted infrastructure"
  - label: "No cloud"
    description: "Local-only or desktop app"
```

### Question 5: Database

```
header: "Database"
question: "Which database(s) does this project use?"
multiSelect: true
options:
  - label: "PostgreSQL"
    description: "PostgreSQL relational database"
  - label: "MongoDB"
    description: "MongoDB document database"
  - label: "DynamoDB"
    description: "AWS DynamoDB NoSQL database"
  - label: "SQLite"
    description: "SQLite embedded database"
  - label: "Redis"
    description: "Redis cache/data store"
  - label: "No database"
    description: "Stateless or in-memory only"
```

---

## Generate Filter Configuration

Based on questionnaire answers, generate this JSON structure:

```json
{
  "version": "1.0",
  "generated": "2024-03-08T12:00:00Z",
  "techStack": {
    "projectType": "<user answer>",
    "frontend": "<user answer>",
    "backend": "<user answer>",
    "cloud": ["<user answers>"],
    "database": ["<user answers>"]
  },
  "filterConfig": {
    "rules": {
      "include_categories": ["<categories>"],
      "include_files": ["<specific files>"],
      "exclude_patterns": ["<patterns>"]
    },
    "skills": {
      "exclude": ["<skill names>"]
    }
  }
}
```

### Filter Generation Logic

**Step 1: Determine included rule categories**

```python
include_categories = ["core", "architecture"]  # Always include

if frontend != "No frontend":
    include_categories.append("frontend")

if backend != "No backend":
    include_categories.append("backend")

include_categories.append("languages")  # Always include

if "AWS" in cloud or "GCP" in cloud or "Azure" in cloud:
    include_categories.append("infrastructure")
```

**Step 2: Add tech-specific includes**

```python
include_files = []

if "Tauri" in backend or "Tauri" in projectType:
    include_files.append("infrastructure/tauri-stack.md")

if "SQLite" in database:
    include_files.append("backend/sqlite-*.md")
```

**Step 3: Generate exclude patterns**

```python
exclude_patterns = []

# Exclude cloud providers not used
if "AWS" not in cloud:
    exclude_patterns.extend([
        "backend/lambda-*.md",
        "infrastructure/aws-*.md",
        "infrastructure/cdk-*.md"
    ])

if "GCP" not in cloud:
    exclude_patterns.append("infrastructure/gcp-*.md")

if "Azure" not in cloud:
    exclude_patterns.append("infrastructure/azure-*.md")

# Exclude unused frontend frameworks
if frontend != "React 19":
    exclude_patterns.append("frontend/react-*.md")

if frontend != "Vue 3":
    exclude_patterns.append("frontend/vue-*.md")
```

**Step 4: Save configuration**

```bash
# Write to target project
echo "$CONFIG_JSON" > <target>/.claude/framework-config.json
```

---

## Example Filter Results

### Example 1: Tauri Desktop App

**Questionnaire answers:**
- Project Type: Desktop Application (Tauri)
- Frontend: React 19
- Backend: Tauri (Rust)
- Cloud: No cloud
- Database: SQLite

**Generated config:**

```json
{
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
        "infrastructure/cdk-*.md",
        "infrastructure/gcp-*.md",
        "infrastructure/azure-*.md"
      ]
    },
    "skills": {
      "exclude": []
    }
  }
}
```

**Result:**
- ✅ Include: 25 rules (core 7, architecture 6, frontend 6, languages 3, tauri 1, development 2)
- ⏭️  Exclude: 18 rules (backend/lambda 3, infrastructure/aws 5, infrastructure/cdk 3, infrastructure/gcp 4, infrastructure/azure 3)
- **Total: 71 items synced** (vs 89 without filtering)

### Example 2: Backend API + AWS

**Questionnaire answers:**
- Project Type: Backend API
- Frontend: No frontend
- Backend: Node.js + TypeScript
- Cloud: AWS
- Database: DynamoDB, PostgreSQL

**Generated config:**

```json
{
  "techStack": {
    "projectType": "Backend API",
    "frontend": "No frontend",
    "backend": "Node.js + TypeScript",
    "cloud": ["AWS"],
    "database": ["DynamoDB", "PostgreSQL"]
  },
  "filterConfig": {
    "rules": {
      "include_categories": ["core", "architecture", "backend", "languages", "infrastructure"],
      "exclude_patterns": [
        "frontend/*",
        "infrastructure/gcp-*.md",
        "infrastructure/azure-*.md",
        "infrastructure/tauri-*.md"
      ]
    }
  }
}
```

**Result:**
- ✅ Include: 31 rules (core, architecture, backend, languages, infrastructure/aws)
- ⏭️  Exclude: 12 rules (frontend 6, infrastructure/gcp 4, infrastructure/azure 2)
- **Total: 77 items synced**

### Example 3: CLI Tool

**Questionnaire answers:**
- Project Type: CLI Tool
- Frontend: No frontend
- Backend: No backend
- Cloud: No cloud
- Database: No database

**Generated config:**

```json
{
  "techStack": {
    "projectType": "CLI Tool",
    "frontend": "No frontend",
    "backend": "No backend",
    "cloud": ["No cloud"],
    "database": ["No database"]
  },
  "filterConfig": {
    "rules": {
      "include_categories": ["core", "architecture", "languages", "development"],
      "exclude_patterns": [
        "frontend/*",
        "backend/*",
        "infrastructure/*"
      ]
    }
  }
}
```

**Result:**
- ✅ Include: 16 rules (core 7, architecture 6, languages 3)
- ⏭️  Exclude: 27 rules (frontend 6, backend 5, infrastructure 16)
- **Total: 52 items synced** (42% reduction)

---

## Display Filter Summary

After generating config, show this summary:

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

Result: ~25 rules will be synced (18 excluded as not relevant)

Skills: All 16 skills (no filtering)
Pillars: All 18 pillars (no filtering)
Workflow: All 12 files (no filtering)

Total: ~71 items (vs 89 without filtering)

✅ Configuration saved to .claude/framework-config.json
```

---

## Filter Implementation Details

### How Filters are Applied

**1. Rules Filtering** (update-rules skill)

```python
def should_include_rule(rule_path, filter_config):
    # Check if in included categories
    category = rule_path.split('/')[0]
    if category in filter_config['include_categories']:
        # Check if excluded by pattern
        for pattern in filter_config['exclude_patterns']:
            if fnmatch(rule_path, pattern):
                return False
        return True

    # Check if in explicitly included files
    if rule_path in filter_config['include_files']:
        return True

    return False
```

**2. Skills Filtering** (update-skills skill)

```python
def should_include_skill(skill_name, filter_config):
    # Check if in exclude list
    if skill_name in filter_config['skills']['exclude']:
        return False
    return True
```

**3. Pillars & Workflow** (no filtering)

```python
# Always sync all pillars
# Always sync all workflow files
# These are universal, not tech-specific
```

### Filter Priority Order

```
1. Explicit include_files (highest priority)
   ↓
2. include_categories
   ↓
3. exclude_patterns (override categories)
   ↓
4. skills.exclude
```

**Example:**
- If `infrastructure/tauri-stack.md` is in `include_files`
- AND `infrastructure/*` is in `exclude_patterns`
- → File is **INCLUDED** (explicit include wins)

---

**See also:**
- **[PROFILE_FILTERING.md](PROFILE_FILTERING.md)** - ⭐ NEW PRIMARY METHOD - Profile-based auto-detection
- [SKILL.md](SKILL.md) - Main skill documentation
- [ADVANCED.md](ADVANCED.md) - Orchestration logic and execution patterns

---

**Version:** 1.0.0 (DEPRECATED - Use PROFILE_FILTERING.md for primary method)
**Last Updated:** 2026-03-10
**Deprecated:** 2026-03-12 (Issue #135 - Profile-based filtering)
