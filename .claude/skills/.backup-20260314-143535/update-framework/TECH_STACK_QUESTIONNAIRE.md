# Tech Stack Questionnaire & Filter Configuration

## Questionnaire Design

### Question 1: Project Type
**Header**: "Project Type"
**Question**: "What type of project is this?"
**MultiSelect**: false (single choice)

**Options**:
1. **Web Application** - Full-stack web app or SPA
2. **Desktop Application (Tauri)** - Cross-platform desktop app using Tauri
3. **Desktop Application (Electron)** - Cross-platform desktop app using Electron
4. **Mobile Application** - React Native or native mobile
5. **Backend API** - REST/GraphQL API service only
6. **CLI Tool** - Command-line tool
7. **Library/Framework** - Reusable library or framework

### Question 2: Frontend Framework
**Header**: "Frontend"
**Question**: "Which frontend framework are you using?"
**MultiSelect**: false

**Options**:
1. **React 19** - React with hooks and modern patterns
2. **Vue 3** - Vue 3 with Composition API
3. **Svelte 5** - Svelte with runes
4. **Vanilla TypeScript** - No framework, pure TS
5. **No frontend** - Backend-only or CLI project

### Question 3: Backend Technology
**Header**: "Backend"
**Question**: "Which backend technology are you using?"
**MultiSelect**: false

**Options**:
1. **Node.js + TypeScript** - Express, Fastify, or similar
2. **Tauri (Rust)** - Desktop app backend
3. **Python + FastAPI** - Python async framework
4. **Go** - Go backend services
5. **Rust** - Rust backend (non-Tauri)
6. **No backend** - Frontend-only or static site

### Question 4: Cloud Provider
**Header**: "Cloud"
**Question**: "Which cloud provider are you using?"
**MultiSelect**: true (can use multiple)

**Options**:
1. **AWS** - AWS services (Lambda, CDK, DynamoDB, S3, etc.)
2. **GCP** - Google Cloud Platform
3. **Azure** - Microsoft Azure
4. **Self-hosted** - Own servers or VPS
5. **No cloud** - Local application or no deployment yet

### Question 5: Database
**Header**: "Database"
**Question**: "Which database(s) are you using?"
**MultiSelect**: true

**Options**:
1. **PostgreSQL** - Relational database
2. **MongoDB** - Document database
3. **DynamoDB** - AWS NoSQL database
4. **SQLite** - Embedded database
5. **Redis** - Cache and data structure store
6. **No database** - Stateless or file-based storage

## Filter Configuration Mapping

### Project Type Filters

#### Web Application
```json
{
  "include_categories": ["core", "architecture", "frontend", "backend", "languages", "infrastructure"],
  "exclude_patterns": []
}
```

#### Desktop Application (Tauri)
```json
{
  "include_categories": ["core", "architecture", "frontend", "desktop", "languages"],
  "include_files": ["infrastructure/tauri-stack.md"],
  "exclude_patterns": [
    "backend/lambda-*.md",
    "backend/external-api-*.md",
    "backend/saga.md",
    "infrastructure/aws-*.md",
    "infrastructure/cdk-*.md",
    "infrastructure/lambda-*.md",
    "infrastructure/cloudwatch-*.md"
  ]
}
```

#### Desktop Application (Electron)
```json
{
  "include_categories": ["core", "architecture", "frontend", "backend", "languages"],
  "exclude_patterns": [
    "infrastructure/aws-*.md",
    "infrastructure/cdk-*.md",
    "infrastructure/lambda-*.md",
    "infrastructure/tauri-*.md"
  ]
}
```

#### Backend API
```json
{
  "include_categories": ["core", "architecture", "backend", "languages", "infrastructure"],
  "exclude_patterns": [
    "frontend/*.md"
  ]
}
```

#### CLI Tool
```json
{
  "include_categories": ["core", "architecture", "languages"],
  "exclude_patterns": [
    "frontend/*.md",
    "backend/*.md",
    "infrastructure/*.md"
  ]
}
```

#### Library/Framework
```json
{
  "include_categories": ["core", "architecture", "languages", "development"],
  "exclude_patterns": [
    "frontend/*.md",
    "backend/*.md",
    "infrastructure/*.md"
  ]
}
```

### Frontend Framework Filters

#### React
```json
{
  "include_patterns": ["frontend/stores.md", "frontend/views.md", "frontend/zustand-*.md"],
  "exclude_patterns": []
}
```

#### Vue
```json
{
  "include_patterns": ["frontend/design-system.md", "frontend/css.md"],
  "exclude_patterns": ["frontend/zustand-*.md", "frontend/stores.md"]
}
```

#### Svelte
```json
{
  "include_patterns": ["frontend/design-system.md", "frontend/css.md"],
  "exclude_patterns": ["frontend/zustand-*.md", "frontend/stores.md"]
}
```

#### No Frontend
```json
{
  "exclude_patterns": ["frontend/*.md"]
}
```

### Backend Technology Filters

#### Node.js + TypeScript
```json
{
  "include_patterns": [
    "backend/*.md",
    "languages/typescript-*.md"
  ]
}
```

#### Tauri (Rust)
```json
{
  "include_patterns": [
    "infrastructure/tauri-stack.md"
  ],
  "exclude_patterns": [
    "backend/lambda-*.md",
    "backend/saga.md"
  ]
}
```

#### Python
```json
{
  "include_patterns": [
    "backend/*.md"
  ],
  "exclude_patterns": [
    "backend/lambda-typescript-*.md",
    "languages/typescript-*.md"
  ]
}
```

#### No Backend
```json
{
  "exclude_patterns": ["backend/*.md"]
}
```

### Cloud Provider Filters

#### AWS
```json
{
  "include_patterns": [
    "infrastructure/aws-*.md",
    "infrastructure/cdk-*.md",
    "infrastructure/lambda-*.md",
    "infrastructure/secrets.md",
    "infrastructure/diagnostic-*.md"
  ]
}
```

#### No Cloud
```json
{
  "exclude_patterns": [
    "infrastructure/aws-*.md",
    "infrastructure/cdk-*.md",
    "infrastructure/lambda-*.md",
    "backend/lambda-*.md"
  ]
}
```

### Database Filters

#### PostgreSQL/MongoDB
```json
{
  "include_patterns": [
    "backend/query-transactions.md"
  ]
}
```

#### DynamoDB
```json
{
  "include_patterns": [
    "backend/query-transactions.md",
    "infrastructure/aws-services.md"
  ]
}
```

#### No Database
```json
{
  "exclude_patterns": [
    "backend/query-transactions.md"
  ]
}
```

## Filter Merging Logic

1. Start with base filters from Project Type
2. Merge Frontend framework filters
3. Merge Backend technology filters
4. Merge Cloud provider filters
5. Merge Database filters
6. Resolve conflicts (exclude takes precedence over include)

### Example: Tauri + React + No Cloud + SQLite

**Step 1 - Project Type (Tauri)**:
- Include: core, architecture, frontend, languages
- Include files: infrastructure/tauri-stack.md
- Exclude: backend/lambda-*, infrastructure/aws-*, infrastructure/cdk-*, infrastructure/lambda-*

**Step 2 - Frontend (React)**:
- Include: frontend/stores.md, frontend/views.md, frontend/zustand-*.md

**Step 3 - Backend (Tauri)**:
- Include: infrastructure/tauri-stack.md
- Exclude: backend/lambda-*, backend/saga.md

**Step 4 - Cloud (No Cloud)**:
- Exclude: infrastructure/aws-*, infrastructure/cdk-*, infrastructure/lambda-*, backend/lambda-*

**Step 5 - Database (SQLite)**:
- (No specific filters)

**Final Result**:
```json
{
  "rules": {
    "include_categories": ["core", "architecture", "frontend", "languages"],
    "include_files": [
      "infrastructure/tauri-stack.md",
      "frontend/stores.md",
      "frontend/views.md",
      "frontend/zustand-hooks.md",
      "frontend/design-system.md",
      "frontend/css.md"
    ],
    "exclude_patterns": [
      "backend/lambda-*.md",
      "backend/saga.md",
      "backend/external-api-*.md",
      "infrastructure/aws-*.md",
      "infrastructure/cdk-*.md",
      "infrastructure/lambda-*.md"
    ]
  },
  "skills": {
    "exclude": []
  }
}
```

**Expected Rules Count**: ~25-28 rules (instead of 43)

## Implementation Notes

1. Use AskUserQuestion tool with the 5 questions above
2. Capture answers in structured format
3. Apply filter logic sequentially
4. Generate final filter configuration
5. Pass to component skills via --filter-config parameter
6. Save configuration to `.claude/framework-config.json` for future updates
