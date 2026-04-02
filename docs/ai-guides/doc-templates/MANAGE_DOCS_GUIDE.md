# MANAGE_DOCS_GUIDE.md - Master Documentation Guide

---
guide_type: master
audience: AI
purpose: Documentation creation and management
last_updated: 2026-03-26
depends_on:
  - STACK_TAGS.md
  - docs/ai-guides/doc-templates/README.md
---

> Master guide for AI to create/update project documentation using the modular guides + templates system

## Table of Contents

1. [Overview](#1-overview)
2. [Module Reference](#2-module-reference)
3. [AI Execution Instructions](#3-ai-execution-instructions)
4. [Stack Tag Processing](#4-stack-tag-processing)
5. [Variable Substitution](#5-variable-substitution)
6. [Profile-Specific Behavior](#6-profile-specific-behavior)
7. [Error Handling](#7-error-handling)
8. [Usage Examples](#8-usage-examples)
9. [Module-Specific Instructions](#9-module-specific-instructions)

---

## 1. Overview

### What is the Modular Docs Management System?

The modular docs management system is a **framework-based approach** to project documentation that:

- **Organizes documentation by domain** (PRD, Architecture, Design, Dev, QA, Ops)
- **Uses template-based generation** with variable substitution and stack tags
- **Supports profile-specific content** (tauri, nextjs-aws, tauri-aws)
- **Provides AI-executable guides** for each module

### When to Use `/manage-docs`

Use the `/manage-docs` skill when you need to:

1. **Initialize documentation** for a new project (first-time setup)
2. **Update specific modules** (partial regeneration)
3. **Apply stack tag changes** after adding/removing technologies
4. **Migrate profiles** (e.g., tauri → tauri-aws)
5. **Refresh templates** after framework updates

### Module Structure

```
docs/ai-guides/doc-templates/
├── README.md                    # Doc templates overview
├── STACK_TAGS.md               # Stack tag specification
├── MANAGE_DOCS_GUIDE.md        # This file
│
├── meta/                       # Special: outputs to docs/ root
│   ├── meta.guide
│   └── templates/
│       └── DOCUMENTATION_MANUAL.md.template  # 912-line standards manual
│
├── prd/
│   ├── prd.guide               # Module-specific instructions
│   └── templates/
│       └── PRD.md.template     # Template file
│
├── architecture/
│   ├── arch.guide
│   └── templates/
│       ├── ARCHITECTURE.md.template
│       ├── API.md.template
│       └── SCHEMA.md.template
│
├── design/                     # Special: has submodules
│   ├── design.guide
│   └── templates/
│       ├── DESIGN.md.template
│       ├── ui/foundation/      # 6 templates
│       ├── ui/components/      # 4 templates
│       └── ux/                 # 3 templates
│
├── dev/
│   ├── dev.guide
│   └── templates/
│       └── SETUP.md.template
│
├── qa/
│   ├── qa.guide
│   └── templates/
│       └── TEST_PLAN.md.template
│
└── ops/                        # Profile-specific
    ├── ops.guide
    └── templates/
        └── DEPLOYMENT.md.template
```

**Key concepts:**
- **Module**: A documentation domain (prd, architecture, design, dev, qa, ops)
- **Guide**: AI instructions for processing a module (`.guide` files)
- **Template**: Source file with variables and stack tags (`.md.template` files)
- **Generated file**: Final documentation in project's `docs/` directory

---

## 2. Module Reference

### Complete Module List

| Module | Guide File | Templates | Generated Files | Profiles |
|--------|-----------|-----------|-----------------|----------|
| **meta** | `meta/meta.guide` | `templates/DOCUMENTATION_MANUAL.md.template` | `docs/DOCUMENTATION_MANUAL.md` | All |
| **prd** | `prd/prd.guide` | `templates/PRD.md.template` | `docs/product/PRD.md` | All |
| **architecture** | `architecture/arch.guide` | `templates/ARCHITECTURE.md.template`<br>`templates/API.md.template`<br>`templates/SCHEMA.md.template` | `docs/architecture/ARCHITECTURE.md`<br>`docs/architecture/API.md`<br>`docs/architecture/SCHEMA.md` | All |
| **design** | `design/design.guide` | `templates/DESIGN.md.template`<br>`templates/ui/foundation/*` (6)<br>`templates/ui/components/*` (4)<br>`templates/ux/*` (3) | `docs/design/DESIGN.md`<br>`docs/design/ui/foundation/*` (6)<br>`docs/design/ui/components/*` (4)<br>`docs/design/ux/*` (3) | All |
| **dev** | `dev/dev.guide` | `templates/SETUP.md.template` | `docs/dev/SETUP.md` | All |
| **qa** | `qa/qa.guide` | `templates/TEST_PLAN.md.template` | `docs/qa/TEST_PLAN.md` | All |
| **ops** | `ops/ops.guide` | `templates/DEPLOYMENT.md.template` | `docs/ops/DEPLOYMENT.md` | nextjs-aws, tauri-aws |

### Module Details

**Foundational module:**
- meta: Documentation structure standards manual (912 lines, Divio-based)

**Standard modules (all profiles):**
- prd: Product requirements documentation
- architecture: System design, API specs, data schemas
- design: UI/UX design system (14 submodules)
- dev: Development setup and environment
- qa: Testing strategy and plans

**Profile-specific modules:**
- ops: Deployment and operations (only for cloud profiles: nextjs-aws, tauri-aws)

**Special cases:**
- **meta module** outputs to docs/ root (not docs/meta/), always included first
- **design module** has submodules (ui/foundation/, ui/components/, ux/)
- **ops module** is excluded for tauri profile (desktop-only, no cloud deployment)

---

## 3. AI Execution Instructions

### Algorithm 1: Detect Project Context

**Purpose:** Extract project metadata needed for template processing

**Input:** Project directory (current working directory)

**Output:** `{profile, stacks, variables}`

**Steps:**
```python
def detect_project_context():
    # Step 1: Read profile
    if exists('.framework-install'):
        profile = json.load('.framework-install')['profile']
    else:
        profile = ask_user("Which profile?", ["tauri", "nextjs-aws", "tauri-aws"])

    # Step 2: Read package.json
    if exists('package.json'):
        pkg = json.load('package.json')
        projectName = pkg['name']
        projectDescription = pkg.get('description', '')

        # Extract stacks from dependencies
        deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
        stacks = detect_stacks_from_dependencies(deps)
    else:
        projectName = ask_user("Project name?")
        projectDescription = ask_user("Project description?")
        stacks = []

    # Step 3: Derive tech stack from profile
    techStack = get_tech_stack_for_profile(profile)

    # Step 4: Get current year
    year = datetime.now().year

    return {
        'profile': profile,
        'stacks': stacks,
        'variables': {
            'projectName': projectName,
            'projectDescription': projectDescription,
            'profile': profile,
            'techStack': techStack,
            'year': year
        }
    }
```

**Example output:**
```python
{
    'profile': 'tauri',
    'stacks': ['react', 'tailwind', 'rust'],
    'variables': {
        'projectName': 'my-app',
        'projectDescription': 'My desktop application',
        'profile': 'tauri',
        'techStack': 'Tauri + React',
        'year': 2026
    }
}
```

---

### Algorithm 2: Determine Modules to Process

**Purpose:** Decide which modules to generate/update

**Input:** `{profile, mode}`
- mode: `"full"` (all modules) or `"partial"` (specific modules)

**Output:** List of module names

**Steps:**
```python
def determine_modules(profile, mode):
    # All possible modules
    all_modules = ['prd', 'architecture', 'design', 'dev', 'qa', 'ops']

    # Step 1: Filter by profile
    if profile == 'tauri':
        # Desktop-only: no ops module
        available_modules = ['prd', 'architecture', 'design', 'dev', 'qa']
    elif profile in ['nextjs-aws', 'tauri-aws']:
        # Cloud profiles: include ops
        available_modules = all_modules

    # Step 2: Filter by mode
    if mode == 'full':
        return available_modules
    elif mode == 'partial':
        # Ask user which modules or detect from args
        selected = ask_user("Which modules?", available_modules)
        return selected

    return available_modules
```

**Example outputs:**
```python
# tauri, full mode
['prd', 'architecture', 'design', 'dev', 'qa']

# nextjs-aws, full mode
['prd', 'architecture', 'design', 'dev', 'qa', 'ops']

# any profile, partial mode with design selected
['design']
```

---

### Algorithm 3: Process Single Module

**Purpose:** Generate documentation files for one module

**Input:** `{module_name, profile, stacks, variables}`

**Output:** List of generated file paths

**Steps:**
```python
def process_module(module_name, profile, stacks, variables):
    generated_files = []

    # Step 1: Read module guide
    guide_path = f'docs/ai-guides/doc-templates/{module_name}/{module_name}.guide'
    guide = read_file(guide_path)

    # Step 2: Get module-specific instructions from guide
    # (Each .guide file contains processing instructions)

    # Step 3: Find all templates for this module
    template_dir = f'docs/ai-guides/doc-templates/{module_name}/templates'
    template_files = glob(f'{template_dir}/**/*.md.template', recursive=True)

    # Step 4: Process each template
    for template_file in template_files:
        # Read template content
        content = read_file(template_file)

        # Process stack tags (see Algorithm 5)
        content = process_stack_tags(content, stacks)

        # Substitute variables (see Algorithm 6)
        content = substitute_variables(content, variables)

        # Determine output path
        # Remove '/templates/' and '.template' from path
        relative_path = template_file.replace(f'{template_dir}/', '')
        output_path = f'docs/{module_name}/{relative_path}'.replace('.template', '')

        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Write generated file
        write_file(output_path, content)
        generated_files.append(output_path)

    # Step 5: Verify all expected files generated
    expected_count = get_expected_file_count(module_name)
    if len(generated_files) != expected_count:
        log_warning(f'Expected {expected_count} files, generated {len(generated_files)}')

    return generated_files
```

**Example:**
```python
# Input
module_name = 'prd'
profile = 'tauri'
stacks = ['react']
variables = {'projectName': 'my-app', ...}

# Output
['docs/product/PRD.md']
```

---

### Algorithm 4: Process All Modules

**Purpose:** Execute full or partial documentation generation

**Input:** `{modules, profile, stacks, variables}`

**Output:** Summary of generated files

**Steps:**
```python
def process_all_modules(modules, profile, stacks, variables):
    all_generated = []
    errors = []

    # Process each module sequentially
    for module_name in modules:
        try:
            log_info(f'Processing module: {module_name}')

            # Special handling for design module (has submodules)
            if module_name == 'design':
                files = process_design_module(profile, stacks, variables)
            else:
                files = process_module(module_name, profile, stacks, variables)

            all_generated.extend(files)
            log_success(f'✅ {module_name}: {len(files)} files')

        except Exception as e:
            errors.append({'module': module_name, 'error': str(e)})
            log_error(f'❌ {module_name}: {e}')
            # Continue with next module (graceful degradation)

    # Summary
    return {
        'generated_files': all_generated,
        'total_count': len(all_generated),
        'errors': errors,
        'success': len(errors) == 0
    }
```

---

## 4. Stack Tag Processing

### Overview

Stack tags allow conditional content based on project technology stack. They use HTML comment syntax:

```html
<!-- @stack:react -->
React-specific content here
<!-- @stack:react -->
```

**Reference:** See `docs/ai-guides/doc-templates/STACK_TAGS.md` for complete specification.

### Processing Rules Summary

| Tag Pattern | Logic | Example |
|-------------|-------|---------|
| `@stack:all` | Always include | `<!-- @stack:all -->` |
| `@stack:tech` | Include if `tech` in stacks | `<!-- @stack:react -->` |
| `@stack:!tech` | Exclude if `tech` in stacks | `<!-- @stack:!vue -->` |
| `@stack:tech1,tech2` | Include if ALL in stacks (AND logic) | `<!-- @stack:react,tailwind -->` |

### Processing Algorithm

**Algorithm 5: Process Stack Tags**

**Input:** `{content, stacks}`
- content: Template file content (string)
- stacks: List of project technology stacks

**Output:** Processed content (string)

**Steps:**
```python
def process_stack_tags(content, stacks):
    import re

    # Pattern: <!-- @stack:requirement --> content <!-- @stack:requirement -->
    pattern = r'<!-- @stack:([^>]+) -->(.*?)<!-- @stack:\1 -->'

    def should_include(requirement):
        # Parse requirement
        if requirement == 'all':
            return True

        # Negation: @stack:!vue
        if requirement.startswith('!'):
            excluded_stack = requirement[1:]
            return excluded_stack not in stacks

        # Multiple stacks (AND logic): @stack:react,tailwind
        if ',' in requirement:
            required_stacks = requirement.split(',')
            return all(s in stacks for s in required_stacks)

        # Single stack: @stack:react
        return requirement in stacks

    # Replace matched blocks
    def replacer(match):
        requirement = match.group(1)
        block_content = match.group(2)

        if should_include(requirement):
            # Include content without tags
            return block_content
        else:
            # Remove entire block
            return ''

    # Process all stack tag blocks
    result = re.sub(pattern, replacer, content, flags=re.DOTALL)

    return result
```

**Example:**
```python
# Input
content = '''
Base content

<!-- @stack:react -->
React-specific section
<!-- @stack:react -->

<!-- @stack:!vue -->
Not for Vue projects
<!-- @stack:!vue -->
'''

stacks = ['react', 'tailwind']

# Output
'''
Base content

React-specific section

Not for Vue projects
'''
```

---

## 5. Variable Substitution

### Standard Variables

| Variable | Source | Example Value |
|----------|--------|---------------|
| `{{projectName}}` | `package.json` → `name` | `"my-app"` |
| `{{projectDescription}}` | `package.json` → `description` | `"My cool application"` |
| `{{profile}}` | `.framework-install` → `profile` | `"tauri"` |
| `{{techStack}}` | Derived from profile | `"Tauri + React"` |
| `{{year}}` | Current year | `2026` |

### Tech Stack Derivation

```python
def get_tech_stack_for_profile(profile):
    if profile == 'tauri':
        return 'Tauri + React'
    elif profile == 'nextjs-aws':
        return 'Next.js + AWS'
    elif profile == 'tauri-aws':
        return 'Tauri + React + AWS'
    else:
        return 'Unknown'
```

### Substitution Algorithm

**Algorithm 6: Substitute Variables**

**Input:** `{content, variables}`
- content: Template content (string)
- variables: Dictionary of variable values

**Output:** Content with variables replaced (string)

**Steps:**
```python
def substitute_variables(content, variables):
    result = content

    # Replace each variable
    for var_name, var_value in variables.items():
        placeholder = f'{{{{{var_name}}}}}'  # {{variableName}}
        result = result.replace(placeholder, str(var_value))

    return result
```

**Example:**
```python
# Input
content = '''
# {{projectName}}

> {{projectDescription}}

Profile: {{profile}}
Tech Stack: {{techStack}}
Copyright {{year}}
'''

variables = {
    'projectName': 'my-app',
    'projectDescription': 'My cool app',
    'profile': 'tauri',
    'techStack': 'Tauri + React',
    'year': 2026
}

# Output
'''
# my-app

> My cool app

Profile: tauri
Tech Stack: Tauri + React
Copyright 2026
'''
```

---

## 6. Profile-Specific Behavior

### Profile Comparison

| Feature | tauri | nextjs-aws | tauri-aws |
|---------|-------|------------|-----------|
| **Total Modules** | 6 | 7 | 7 |
| **Total Files** | 21 | 22 | 22 |
| **Includes meta/** | ✅ | ✅ | ✅ |
| **Includes ops/** | ❌ | ✅ | ✅ |
| **Desktop docs** | ✅ | ❌ | ✅ |
| **AWS docs** | ❌ | ✅ | ✅ |
| **DEPLOYMENT.md** | ❌ | ✅ | ✅ |
| **Tech Stack** | Tauri + React | Next.js + AWS | Tauri + React + AWS |

### Module Filtering Logic

```python
def get_modules_for_profile(profile):
    # meta is always first - foundational document
    base_modules = ['meta', 'prd', 'architecture', 'design', 'dev', 'qa']

    if profile == 'tauri':
        # Desktop-only: no cloud deployment
        return base_modules

    elif profile in ['nextjs-aws', 'tauri-aws']:
        # Cloud-enabled: includes deployment
        return base_modules + ['ops']

    else:
        # Minimal/unknown: all modules except ops
        return base_modules
```

### Profile-Specific Content Examples

**tauri profile:**
- Generates 6 modules (21 files)
- Includes `docs/DOCUMENTATION_MANUAL.md` (meta module)
- `docs/desktop/` directory (desktop-specific docs)
- No `docs/ops/` or `DEPLOYMENT.md`

**nextjs-aws profile:**
- Generates 7 modules (22 files)
- Includes `docs/DOCUMENTATION_MANUAL.md` (meta module)
- `docs/aws/` directory (cloud infrastructure docs)
- `docs/ops/DEPLOYMENT.md` (deployment procedures)

**tauri-aws profile:**
- Generates 7 modules (22 files)
- Includes `docs/DOCUMENTATION_MANUAL.md` (meta module)
- Both `docs/desktop/` and `docs/aws/`
- `docs/ops/DEPLOYMENT.md` (hybrid deployment)

---

## 7. Error Handling

### Common Errors and Recovery

| Error | Cause | Recovery Strategy |
|-------|-------|-------------------|
| **Template not found** | Missing `.md.template` file | Log warning, create stub file with placeholder content |
| **Variable missing** | `package.json` incomplete or malformed | Use default value or prompt user for input |
| **Stack tag invalid** | Malformed `<!-- @stack: -->` syntax | Skip tag processing, log warning, include raw content |
| **Permission denied** | Cannot write to `docs/` directory | Create directory with proper permissions, retry operation |
| **Overwrite conflict** | `docs/` already exists with custom content | Ask user: [O]verwrite, [M]erge, [S]kip |
| **Guide file missing** | Module `.guide` file not found | Use default processing (template copy + substitution) |

### Error Handling Algorithm

```python
def process_module_with_error_handling(module_name, profile, stacks, variables):
    try:
        # Attempt normal processing
        return process_module(module_name, profile, stacks, variables)

    except TemplateNotFoundError as e:
        log_warning(f'Template missing for {module_name}: {e.template_path}')
        # Create stub file
        stub_path = get_output_path_for_template(e.template_path)
        create_stub_file(stub_path, f'# {module_name}\n\n[Template not found: {e.template_path}]')
        return [stub_path]

    except VariableMissingError as e:
        log_warning(f'Variable missing: {e.variable_name}')
        # Use default or ask user
        default_value = get_default_value(e.variable_name)
        variables[e.variable_name] = default_value
        # Retry with default
        return process_module(module_name, profile, stacks, variables)

    except PermissionError as e:
        log_error(f'Permission denied: {e.filename}')
        # Try to create directory with correct permissions
        os.makedirs(os.path.dirname(e.filename), exist_ok=True, mode=0o755)
        # Retry
        return process_module(module_name, profile, stacks, variables)

    except StackTagInvalidError as e:
        log_warning(f'Invalid stack tag: {e.tag}')
        # Skip stack tag processing, use raw content
        return process_module_without_stack_tags(module_name, profile, stacks, variables)

    except Exception as e:
        log_error(f'Unexpected error processing {module_name}: {e}')
        # Re-raise for global error handler
        raise
```

### Graceful Degradation

**Principle:** Continue processing other modules even if one fails.

```python
def process_all_modules_gracefully(modules, profile, stacks, variables):
    results = []
    errors = []

    for module in modules:
        try:
            files = process_module_with_error_handling(module, profile, stacks, variables)
            results.append({'module': module, 'files': files, 'status': 'success'})
        except Exception as e:
            errors.append({'module': module, 'error': str(e)})
            results.append({'module': module, 'files': [], 'status': 'failed'})
            # Continue with next module

    return results, errors
```

---

## 8. Usage Examples

### Example 1: First-Time Init (tauri profile)

**Scenario:** New tauri project, empty `docs/` directory

**Command:**
```bash
/manage-docs --mode=full
```

**Context:**
- Profile: `tauri`
- Stacks: `['react', 'tailwind', 'rust']`
- `docs/` directory: Empty

**Execution:**
1. Detect context → profile=tauri, 6 modules
2. Process meta → `docs/DOCUMENTATION_MANUAL.md` (912 lines)
3. Process prd → `docs/product/PRD.md`
4. Process architecture → 3 files (`ARCHITECTURE.md`, `API.md`, `SCHEMA.md`)
5. Process design → 15 files (1 main + 14 submodules)
6. Process dev → `docs/dev/SETUP.md`
7. Process qa → `docs/qa/TEST_PLAN.md`

**Output:**
```
✅ Module processing complete

Generated files:
  meta: 1 file
  prd: 1 file
  architecture: 3 files
  design: 15 files
  dev: 1 file
  qa: 1 file
  Total: 22 files

docs/
├── DOCUMENTATION_MANUAL.md      ← meta module (standards manual)
├── product/
│   └── PRD.md
├── architecture/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── SCHEMA.md
├── design/
│   ├── DESIGN.md
│   ├── ui/foundation/    (6 files)
│   ├── ui/components/    (4 files)
│   └── ux/               (3 files)
├── dev/
│   └── SETUP.md
└── qa/
    └── TEST_PLAN.md
```

---

### Example 2: First-Time Init (nextjs-aws profile)

**Scenario:** New Next.js + AWS project

**Command:**
```bash
/manage-docs --mode=full
```

**Context:**
- Profile: `nextjs-aws`
- Stacks: `['react', 'nextjs', 'tailwind', 'aws']`

**Execution:**
1. Detect context → profile=nextjs-aws, 7 modules (includes meta and ops)
2. Process meta → `docs/DOCUMENTATION_MANUAL.md`
3. Process prd, architecture, design, dev, qa (same as tauri)
4. Process ops → `docs/ops/DEPLOYMENT.md`

**Output:**
```
✅ Module processing complete

Generated files:
  meta: 1 file
  prd: 1 file
  architecture: 3 files
  design: 15 files
  dev: 1 file
  qa: 1 file
  ops: 1 file  ← Additional module
  Total: 22 files

docs/
├── product/PRD.md
├── architecture/      (3 files)
├── design/            (15 files)
├── dev/SETUP.md
├── qa/TEST_PLAN.md
└── ops/               ← New directory
    └── DEPLOYMENT.md
```

---

### Example 3: Update Single Module (architecture)

**Scenario:** Architecture templates updated, need to regenerate

**Command:**
```bash
/manage-docs --module=architecture
```

**Context:**
- Profile: `tauri`
- Existing `docs/` with custom content
- Only regenerate architecture module

**Execution:**
1. Detect context → profile=tauri
2. Ask user about overwrite → [O]verwrite, [M]erge, [S]kip
3. Process architecture module only
4. Regenerate 3 architecture files

**Output:**
```
⚠️  docs/architecture/ already exists

Choose action:
  [O] Overwrite (replace all files)
  [M] Merge (update only architecture)
  [S] Skip (cancel operation)

> M (Merge selected)

✅ Architecture module updated

Updated files:
  docs/architecture/ARCHITECTURE.md
  docs/architecture/API.md
  docs/architecture/SCHEMA.md

Other modules untouched:
  docs/product/PRD.md (preserved)
  docs/design/* (preserved)
```

---

### Example 4: Update Meta Module (Documentation Standards)

**Scenario:** Documentation standards manual needs to be updated or regenerated

**Command:**
```bash
/manage-docs --instant --module=meta
```

**Context:**
- Profile: Any (meta module is profile-agnostic)
- Only regenerate DOCUMENTATION_MANUAL.md
- All other docs unchanged

**Execution:**
1. Detect context → profile detected
2. Process meta module only
3. Generate/update `docs/DOCUMENTATION_MANUAL.md`

**Output:**
```
✅ Meta module updated

Generated files:
  docs/DOCUMENTATION_MANUAL.md

Other modules untouched:
  docs/product/ (preserved)
  docs/architecture/ (preserved)
  docs/design/ (preserved)
  docs/dev/ (preserved)
  docs/qa/ (preserved)
```

**Use cases:**
- Update standards manual after framework changes
- Add DOCUMENTATION_MANUAL.md to existing projects
- Sync latest documentation guidelines

---

### Example 5: Stack Tag Processing (React + Tailwind)

**Scenario:** Project uses React and Tailwind, template has conditional content

**Template content:**
```markdown
## Styling

<!-- @stack:tailwind -->
This project uses Tailwind CSS for styling.
See `tailwind.config.js` for configuration.
<!-- @stack:tailwind -->

<!-- @stack:!tailwind -->
This project uses custom CSS.
See `src/styles/` for stylesheets.
<!-- @stack:!tailwind -->
```

**Context:**
- Stacks: `['react', 'tailwind']`

**Generated output:**
```markdown
## Styling

This project uses Tailwind CSS for styling.
See `tailwind.config.js` for configuration.
```

**Explanation:**
- `@stack:tailwind` → Included (tailwind in stacks)
- `@stack:!tailwind` → Excluded (negation failed)

---

### Example 5: Handle Missing Template

**Scenario:** `DEPLOYMENT.md.template` file missing

**Command:**
```bash
/manage-docs --module=ops
```

**Execution:**
1. Try to read `docs/ai-guides/doc-templates/ops/templates/DEPLOYMENT.md.template`
2. File not found → TemplateNotFoundError
3. Error handler creates stub file

**Output:**
```
⚠️  Template not found: ops/templates/DEPLOYMENT.md.template

Creating stub file...
✅ Stub created: docs/ops/DEPLOYMENT.md

docs/ops/DEPLOYMENT.md content:
---
# Deployment Guide

[Template not found: ops/templates/DEPLOYMENT.md.template]

Please create this file manually or update the template.
---
```

---

### Example 6: Profile Migration (tauri → tauri-aws)

**Scenario:** Project changed from desktop-only to desktop + cloud

**Steps:**
1. Update `.framework-install`:
   ```json
   {
     "profile": "tauri-aws"  // Changed from "tauri"
   }
   ```

2. Run full regeneration:
   ```bash
   /manage-docs --mode=full
   ```

**Execution:**
1. Detect context → profile=tauri-aws (6 modules now)
2. Regenerate all modules
3. **ops module now included** (was excluded before)

**Output:**
```
✅ Module processing complete

Profile changed: tauri → tauri-aws
Modules changed: 5 → 6

New files generated:
  docs/ops/DEPLOYMENT.md  ← New module

All modules regenerated:
  prd: 1 file
  architecture: 3 files
  design: 15 files
  dev: 1 file
  qa: 1 file
  ops: 1 file (NEW)
  Total: 22 files
```

---

### Example 7: Partial Update (design module only)

**Scenario:** Design system templates updated, regenerate design docs

**Command:**
```bash
/manage-docs --module=design
```

**Execution:**
1. Detect context → profile=tauri
2. Process design module only
3. Handle design submodules (ui/foundation, ui/components, ux)

**Output:**
```
✅ Design module updated

Generated files (15 total):
  docs/design/DESIGN.md
  docs/design/ui/foundation/
    ├── COLOR.md
    ├── TYPOGRAPHY.md
    ├── SPACING.md
    ├── SHADOWS.md
    ├── RADIUS.md
    └── MOTION.md
  docs/design/ui/components/
    ├── BUTTONS.md
    ├── FORMS.md
    ├── FEEDBACK.md
    └── ACCESSIBILITY.md
  docs/design/ux/
    ├── USER_FLOWS.md
    ├── USER_JOURNEYS.md
    └── SCENARIOS.md

Other modules untouched.
```

---

### Example 8: Overwrite Protection

**Scenario:** `docs/` exists with custom content

**Command:**
```bash
/manage-docs --mode=full
```

**Execution:**
1. Detect existing `docs/` directory
2. Prompt user for action

**Interaction:**
```
⚠️  WARNING: docs/ directory already exists

This operation will regenerate all documentation files.
Custom changes may be lost.

docs/ directory contents:
  - docs/product/PRD.md (modified 2 days ago)
  - docs/architecture/* (custom notes added)
  - docs/design/* (updated with brand colors)

Choose action:
  [O] Overwrite all (delete and regenerate)
  [M] Merge (regenerate templates, keep custom files)
  [B] Backup first (create docs.backup/, then regenerate)
  [C] Cancel

> B (Backup selected)

Creating backup...
✅ Backup created: docs.backup/

Regenerating documentation...
✅ All modules processed

Original content preserved in: docs.backup/
```

---

### Example 9: Stack-Specific Content (React + Tailwind + AWS)

**Scenario:** Next.js + AWS project with specific tech stack

**Context:**
- Profile: `nextjs-aws`
- Stacks: `['react', 'nextjs', 'tailwind', 'aws', 'postgresql']`

**Template snippet:**
```markdown
## Technology Stack

<!-- @stack:react,tailwind -->
Frontend: React + Tailwind CSS
<!-- @stack:react,tailwind -->

<!-- @stack:aws -->
Infrastructure: AWS (see ops/DEPLOYMENT.md)
<!-- @stack:aws -->

<!-- @stack:postgresql -->
Database: PostgreSQL
<!-- @stack:postgresql -->
```

**Generated output:**
```markdown
## Technology Stack

Frontend: React + Tailwind CSS

Infrastructure: AWS (see ops/DEPLOYMENT.md)

Database: PostgreSQL
```

**Explanation:**
- `@stack:react,tailwind` → Included (both in stacks, AND logic)
- `@stack:aws` → Included
- `@stack:postgresql` → Included

---

### Example 10: Error Recovery (Permission Denied)

**Scenario:** Cannot write to `docs/` due to permissions

**Command:**
```bash
/manage-docs --mode=full
```

**Execution:**
1. Try to create `docs/product/PRD.md`
2. PermissionError → Cannot write
3. Error handler creates directory with correct permissions
4. Retry operation

**Output:**
```
❌ Permission denied: docs/product/PRD.md

Attempting to fix permissions...
Creating directory: docs/product/ (mode: 0755)
✅ Directory created

Retrying operation...
✅ docs/product/PRD.md created

Module processing continues...
```

---

## 9. Module-Specific Instructions

### Design Module Special Handling

The **design module** is unique because it has **submodules** organized in a tree structure:

```
design/
├── DESIGN.md.template          # Main design doc
└── templates/
    ├── ui/
    │   ├── foundation/         # 6 templates
    │   │   ├── COLOR.md.template
    │   │   ├── TYPOGRAPHY.md.template
    │   │   ├── SPACING.md.template
    │   │   ├── SHADOWS.md.template
    │   │   ├── RADIUS.md.template
    │   │   └── MOTION.md.template
    │   └── components/         # 4 templates
    │       ├── BUTTONS.md.template
    │       ├── FORMS.md.template
    │       ├── FEEDBACK.md.template
    │       └── ACCESSIBILITY.md.template
    └── ux/                     # 3 templates
        ├── USER_FLOWS.md.template
        ├── USER_JOURNEYS.md.template
        └── SCENARIOS.md.template
```

### Algorithm: Process Design Module

```python
def process_design_module(profile, stacks, variables):
    generated_files = []

    # Step 1: Process main design template
    main_template = 'docs/ai-guides/doc-templates/design/templates/DESIGN.md.template'
    main_content = read_file(main_template)
    main_content = process_stack_tags(main_content, stacks)
    main_content = substitute_variables(main_content, variables)
    write_file('docs/design/DESIGN.md', main_content)
    generated_files.append('docs/design/DESIGN.md')

    # Step 2: Process ui/foundation/ submodule (6 files)
    foundation_templates = [
        'COLOR.md.template',
        'TYPOGRAPHY.md.template',
        'SPACING.md.template',
        'SHADOWS.md.template',
        'RADIUS.md.template',
        'MOTION.md.template'
    ]

    for template_name in foundation_templates:
        template_path = f'docs/ai-guides/doc-templates/design/templates/ui/foundation/{template_name}'
        content = read_file(template_path)
        content = process_stack_tags(content, stacks)
        content = substitute_variables(content, variables)

        output_path = f'docs/design/ui/foundation/{template_name.replace(\".template\", \"\")}'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        write_file(output_path, content)
        generated_files.append(output_path)

    # Step 3: Process ui/components/ submodule (4 files)
    component_templates = [
        'BUTTONS.md.template',
        'FORMS.md.template',
        'FEEDBACK.md.template',
        'ACCESSIBILITY.md.template'
    ]

    for template_name in component_templates:
        template_path = f'docs/ai-guides/doc-templates/design/templates/ui/components/{template_name}'
        content = read_file(template_path)
        content = process_stack_tags(content, stacks)
        content = substitute_variables(content, variables)

        output_path = f'docs/design/ui/components/{template_name.replace(\".template\", \"\")}'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        write_file(output_path, content)
        generated_files.append(output_path)

    # Step 4: Process ux/ submodule (3 files)
    ux_templates = [
        'USER_FLOWS.md.template',
        'USER_JOURNEYS.md.template',
        'SCENARIOS.md.template'
    ]

    for template_name in ux_templates:
        template_path = f'docs/ai-guides/doc-templates/design/templates/ux/{template_name}'
        content = read_file(template_path)
        content = process_stack_tags(content, stacks)
        content = substitute_variables(content, variables)

        output_path = f'docs/design/ux/{template_name.replace(\".template\", \"\")}'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        write_file(output_path, content)
        generated_files.append(output_path)

    # Total: 1 + 6 + 4 + 3 = 14 files
    assert len(generated_files) == 15, f'Expected 15 design files, got {len(generated_files)}'

    return generated_files
```

### Expected File Counts by Module

| Module | File Count | Notes |
|--------|------------|-------|
| prd | 1 | PRD.md |
| architecture | 3 | ARCHITECTURE.md, API.md, SCHEMA.md |
| design | 15 | 1 main + 6 foundation + 4 components + 3 ux = 14 (wait, recount) |
| dev | 1 | SETUP.md |
| qa | 1 | TEST_PLAN.md |
| ops | 1 | DEPLOYMENT.md |
| **Total (all profiles)** | **22** | nextjs-aws, tauri-aws |
| **Total (tauri)** | **21** | No ops module |

**Correction for design module count:**
- 1 DESIGN.md
- 6 ui/foundation/
- 4 ui/components/
- 3 ux/
- **Total: 14 files** (not 15 as stated earlier)

**Updated totals:**
- tauri: 20 files (1+3+14+1+1)
- nextjs-aws, tauri-aws: 21 files (1+3+14+1+1+1)

---

## Summary

This guide provides complete instructions for AI to create and update project documentation using the modular guides + templates system.

**Key takeaways:**
1. **Use unified paths** from Issue #337 (`docs/ai-guides/doc-templates/`)
2. **Follow 6 algorithms** for systematic processing
3. **Handle profile differences** (tauri vs cloud profiles)
4. **Process stack tags** using STACK_TAGS.md specification
5. **Gracefully handle errors** and continue processing
6. **Special handling for design module** (14 submodules)

**Ready for:** Issue #310 (`/manage-docs` skill implementation)

---

**Last Updated:** 2026-03-26 (Issue #309)
**Maintained By:** AI Development Framework Team
