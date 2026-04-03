---
name: update-guides
version: "1.3.1"
framework-only: true
description: Sync AI development guides and profiles between projects - ensures AI has latest reference standards.
triggers:
  - user wants to sync AI guides
  - user mentions "update guides"
  - user wants latest AI development standards
  - after framework AI guides are updated
do_not_trigger:
  - user wants to update skills/rules/pillars (use respective update-* skills)
  - user just wants to read guides documentation
last-updated: "2026-03-28"
---

# update-guides - Sync AI Development Guides

Synchronize AI development reference guides and profiles from framework to target projects.

## Overview

This skill syncs AI development reference standards (guides + profiles) between the framework and target projects.

**What it does:**
1. Detects framework's `.claude/guides/` directory
2. Deletes target project's `.claude/guides/` (if exists)
3. Copies all AI guides and profiles from framework to target
4. Creates `.ai-guides-version` tracking file
5. Generates detailed sync report

**Why it's needed:**
AI skills read these guides and profiles to get development standards and workflows. When guides are updated in the framework, projects need the latest versions to ensure AI uses current best practices.

**When to use:**
- After framework guides are updated
- Setting up a new project
- Ensuring AI has latest development standards
- As part of `/update-framework` meta-skill

## What Are AI Guides?

**AI Guides are reference documentation that AI reads during task execution.**

**Primary audience**: AI (Claude Code)
- AI skills read guides to get standards, templates, workflows
- Example: `/manage-adrs` reads `ADR_GUIDE.md` to get ADR templates
- Example: `/manage-claude-md` reads `CLAUDE_MD_GUIDE.md` for CLAUDE.md structure

**Secondary audience**: Humans
- Humans can also read guides to understand AI's decision-making
- Helps humans review AI-generated content
- Provides transparency into AI development standards

**Location**: `.claude/guides/` (same in framework and projects)

## Synced Content

**Directory structure**: `.claude/guides/` with 4 subdirectories, **20 files total**

### Workflow Guides (workflow/ - 6 files)

| File | Purpose | Used By Skills |
|------|---------|----------------|
| **README.md** | Index of workflow guides | - |
| **ADR_GUIDE.md** | AI 创建 ADR 的参考标准 | /manage-adrs |
| **CLAUDE_MD_GUIDE.md** | AI 维护 CLAUDE.md 的参考标准 | /manage-claude-md |
| **ISSUE_LIFECYCLE_GUIDE.md** | AI 执行 issue 工作流的参考标准 | /solve-issues, /auto-solve-issue |
| **PROJECT_PLANNING_GUIDE.md** | AI 规划项目的参考标准 | /plan |
| **SKILL_GUIDE.md** | AI 创建技能的参考标准 | /skill-creator |

### Doc Templates (doc-templates/ - 3 files)

| File | Purpose | Used By Skills |
|------|---------|----------------|
| **README.md** | Index of doc templates | - |
| **MANAGE_DOCS_GUIDE.md** | AI 管理文档的参考标准 | /manage-docs, /init-docs, /check-docs |
| **STACK_TAGS.md** | Tech stack tag definitions | /manage-docs |

### Rules Guides (rules/ - 5 files)

| File | Purpose | Used By Skills |
|------|---------|----------------|
| **README.md** | Index of rules guides | - |
| **RULES_GUIDE.md** | Rules management standards | /manage-rules |
| **RULES_MAPPING.md** | Profile-to-rules mapping | /manage-rules |
| **PROFILE_CONSISTENCY.md** | Profile consistency checks | /manage-rules |
| **MIGRATION_REPORT.md** | Rules migration documentation | Internal |

### Profiles (profiles/ - 4 files)

| File | Description | Used By Skills |
|------|-------------|----------------|
| **README.md** | Index of profiles | - |
| **tauri.md** | Desktop app (Tauri + React) | /manage-project, /manage-rules |
| **nextjs-aws.md** | Full-stack (Next.js + AWS) | /manage-project, /manage-rules |
| **tauri-aws.md** | Hybrid (Tauri + AWS) | /manage-project, /manage-rules |

**All guides and profiles are synced together** to ensure consistency across projects.

## Arguments

```bash
/update-guides --from FRAMEWORK_DIR [TARGET_PROJECT]
```

**Parameters:**
- `--from FRAMEWORK_DIR` - Path to framework directory (required)
- `TARGET_PROJECT` - Path to target project (default: current directory)
- `--skip-validation` - Skip path validation (used when called by update-framework)

**Common usage:**
```bash
# Sync from framework to specific project
/update-guides --from ~/dev/ai-dev ../u-safe

# Sync to current project
/update-guides --from ~/dev/ai-dev .

# Absolute paths
/update-guides --from /Users/woo/dev/ai-dev /Users/woo/dev/my-project

# Skip validation (when called by meta-skill)
/update-guides --from ~/dev/ai-dev ../u-safe --skip-validation
```

## Workflow Steps

### 1. Validate Framework Directory

```bash
# Check framework has .claude/guides/
if [ ! -d "$FRAMEWORK_DIR/.claude/guides" ]; then
    echo "❌ 错误：框架目录不存在 .claude/guides/"
    exit 1
fi

# Verify 4 subdirectories exist
for subdir in workflow doc-templates rules profiles; do
    if [ ! -d "$FRAMEWORK_DIR/.claude/guides/$subdir" ]; then
        echo "❌ 错误：缺少子目录 $subdir"
        exit 1
    fi
done

# Count total .md files (should be 18)
TOTAL_FILES=$(find "$FRAMEWORK_DIR/.claude/guides" -name "*.md" -type f | wc -l)
if [ $TOTAL_FILES -lt 18 ]; then
    echo "⚠️ 警告：仅找到 $TOTAL_FILES 个文件（期望 18 个）"
fi
```

### 2. Delete Existing Target Directory

```bash
# Remove old guides if present
if [ -d "$TARGET_DIR/.claude/guides" ]; then
    echo "🗑️ 删除现有 ai-guides 目录..."
    rm -rf "$TARGET_DIR/.claude/guides"
fi
```

**Why delete first:**
- Ensures complete sync (no stale files)
- Handles renamed/deleted guides
- Simpler than incremental sync

### 3. Copy AI Guides

```bash
# Create docs directory if needed
mkdir -p "$TARGET_DIR/docs"

# Copy all guides
cp -r "$FRAMEWORK_DIR/.claude/guides" "$TARGET_DIR/.claude/guides"

# Verify copy succeeded
if [ ! -d "$TARGET_DIR/.claude/guides" ]; then
    echo "❌ 错误：拷贝失败"
    exit 1
fi
```

### 4. Create Version Tracking File

```bash
# Record sync metadata
cat > "$TARGET_DIR/.claude/guides/.ai-guides-version" << EOF
framework_path: $FRAMEWORK_DIR
framework_commit: $(cd "$FRAMEWORK_DIR" && git rev-parse HEAD)
synced_at: $(date -Iseconds)
synced_by: update-guides.sh v1.3.0
file_count: 20
subdirs: workflow,doc-templates,rules,profiles
EOF
```

**Tracking file benefits:**
- Shows when guides were last synced
- Records source framework version (git commit)
- Helps debug outdated guides

### 5. Generate Sync Report

```bash
echo "✅ 同步完成 - 20 个文件已同步"
echo ""
echo "📁 workflow/ (6 files)"
echo "  ✅ README.md"
echo "  ✅ ADR_GUIDE.md - AI 创建 ADR 的参考标准"
echo "  ✅ CLAUDE_MD_GUIDE.md - AI 维护 CLAUDE.md 的参考标准"
echo "  ✅ ISSUE_LIFECYCLE_GUIDE.md - AI 执行 issue 工作流的参考标准"
echo "  ✅ PROJECT_PLANNING_GUIDE.md - AI 规划项目的参考标准"
echo "  ✅ SKILL_GUIDE.md - AI 创建技能的参考标准"
echo ""
echo "📁 doc-templates/ (3 files)"
echo "  ✅ README.md"
echo "  ✅ MANAGE_DOCS_GUIDE.md - AI 管理文档的参考标准"
echo "  ✅ STACK_TAGS.md - Tech stack tag definitions"
echo ""
echo "📁 rules/ (5 files)"
echo "  ✅ README.md"
echo "  ✅ RULES_GUIDE.md - Rules management standards"
echo "  ✅ RULES_MAPPING.md - Profile-to-rules mapping"
echo "  ✅ PROFILE_CONSISTENCY.md - Profile consistency checks"
echo "  ✅ MIGRATION_REPORT.md - Rules migration documentation"
echo ""
echo "📁 profiles/ (4 files)"
echo "  ✅ README.md"
echo "  ✅ tauri.md - Desktop app profile"
echo "  ✅ nextjs-aws.md - Full-stack profile"
echo "  ✅ tauri-aws.md - Hybrid profile"
echo ""
echo "AI 现在可以使用最新的开发参考标准（20 个文件，4 个子目录）"
```

## Examples

### Example 1: Basic Sync

**User says:**
> "sync AI guides from framework to u-safe"

**Command:**
```bash
/update-guides --from ~/dev/ai-dev ~/dev/u-safe
```

**Output:**
```
📋 同步 AI 开发指南
   框架: /Users/woo/dev/ai-dev/.claude/guides
   目标: /Users/woo/dev/u-safe/.claude/guides

🗑️ 删除现有 ai-guides 目录...
📋 拷贝 AI 开发指南...
📝 创建版本标记...

✅ 同步完成 - 20 个文件已同步

📁 workflow/ (6 files)
  ✅ README.md
  ✅ ADR_GUIDE.md - AI 创建 ADR 的参考标准
  ✅ CLAUDE_MD_GUIDE.md - AI 维护 CLAUDE.md 的参考标准
  ✅ ISSUE_LIFECYCLE_GUIDE.md - AI 执行 issue 工作流的参考标准
  ✅ PROJECT_PLANNING_GUIDE.md - AI 规划项目的参考标准
  ✅ SKILL_GUIDE.md - AI 创建技能的参考标准

📁 doc-templates/ (3 files)
  ✅ README.md
  ✅ MANAGE_DOCS_GUIDE.md - AI 管理文档的参考标准
  ✅ STACK_TAGS.md - Tech stack tag definitions

📁 rules/ (5 files)
  ✅ README.md
  ✅ RULES_GUIDE.md - Rules management standards
  ✅ RULES_MAPPING.md - Profile-to-rules mapping
  ✅ PROFILE_CONSISTENCY.md - Profile consistency checks
  ✅ MIGRATION_REPORT.md - Rules migration documentation

📁 profiles/ (4 files)
  ✅ README.md
  ✅ tauri.md - Desktop app profile
  ✅ nextjs-aws.md - Full-stack profile
  ✅ tauri-aws.md - Hybrid profile

AI 现在可以使用最新的开发参考标准（20 个文件，4 个子目录）
```

### Example 2: Error Handling - Framework Missing

**Command:**
```bash
/update-guides --from /invalid/path ../my-project
```

**Output:**
```
❌ 错误：框架目录不存在 AI guides
   期望路径: /invalid/path/.claude/guides

请确保框架目录包含 .claude/guides/ 并且包含 4 个子目录（workflow, doc-templates, rules, profiles）。
```

### Example 3: Warning - Incomplete Guides

**Scenario:** Framework only has 12 out of 20 files

**Output:**
```
⚠️ 警告：仅找到 12 个文件（期望 18 个）

📋 拷贝 AI 开发指南...
...
✅ 同步完成 - 12 个文件已同步
(缺失的文件将在报告中用 ❌ 标记)
```

## Integration

### With /update-framework Meta-Skill

```bash
# Complete framework sync
/update-framework ../target-project
  → Calls /update-pillars
  → Calls /update-skills
  → (Optional) /update-guides ← THIS SKILL

Note: /update-guides is now optional, not part of main framework sync
```

### With init-project.py

```python
# Optional: Sync guides during project initialization
if args.sync_guides:
    subprocess.run([
        ".claude/skills/update-guides/update-guides.sh",
        "--from", args.framework_path,
        project_path
    ])
```

### With Related Skills

**Skills that read AI guides:**
- `/manage-adrs` - Reads `ADR_GUIDE.md` for ADR templates and standards
- `/manage-claude-md` - Reads `CLAUDE_MD_GUIDE.md` for CLAUDE.md structure
- `/solve-issues` - Reads `ISSUE_LIFECYCLE_GUIDE.md` for workflow
- `/init-docs` - Reads `DOCS_GUIDE.md` for documentation structure
- `/check-docs` - Reads `DOCS_GUIDE.md` for validation standards
- `/skill-creator` - Reads `SKILL_GUIDE.md` for skill patterns

**Workflow:**
```
1. Update guides in framework: Edit .claude/guides/*.md
2. Sync to projects: /update-guides --from framework project
3. AI skills read guides: Skills use Read tool to access guides
4. AI executes with standards: Guides inform AI's decisions
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Framework path missing | --from not specified | Add --from argument |
| Framework guides missing | .claude/guides/ doesn't exist | Create guides in framework first |
| Missing subdirectory | One of 4 subdirectories missing | Check framework has workflow, doc-templates, rules, profiles |
| Target not writable | Permission denied | Check directory permissions |
| Copy failed | Disk full, permissions | Check disk space and permissions |
| Incomplete guides | <20 files found | Warning shown, continues anyway |

## Best Practices

1. **Sync after framework updates** - Run after creating/updating guides in framework
2. **Use absolute paths** - Avoid relative path confusion
3. **Check version file** - Use `.ai-guides-version` to track sync status
4. **Integrate with /update-framework** - Part of complete framework sync
5. **Test guides before sync** - Ensure guides are complete in framework

## Sync Strategy

**Complete replacement (not incremental):**
- ✅ Simple and reliable
- ✅ Handles renames and deletions
- ✅ Ensures target matches source exactly
- ✅ No complex diff logic needed

**Why not incremental:**
- Guides are documentation (not code with history)
- Complete replacement is simpler
- Sync is fast (18 markdown files across 4 subdirectories)
- No risk of partial updates

## Version Tracking

**File:** `.claude/guides/.ai-guides-version`

**Content:**
```yaml
framework_path: /Users/woo/dev/ai-dev
framework_commit: a1b2c3d4e5f6...
synced_at: 2026-03-28T10:00:00+08:00
synced_by: update-guides.sh v1.3.0
file_count: 20
subdirs: workflow,doc-templates,rules,profiles
```

**Usage:**
- Check when guides were last synced
- Verify source framework version
- Debug guide inconsistencies
- Track sync history

## Performance

- **Execution time:** <3 seconds (18 markdown files across 4 subdirectories)
- **Disk space:** ~100KB (all 20 files)
- **Network:** None (local file copy)

Fast because:
- Simple file copy operation
- No network requests
- No complex processing

## Output Mode Detection

**When called by update-framework:**
- Check environment variable: `CALLED_BY_UPDATE_FRAMEWORK`
- If set: Output simplified 1-2 line summary (e.g., "✅ Guides 同步完成: 20 个文件")
- If not set: Output full detailed report (current behavior)

This reduces total output length when update-framework orchestrates multiple sync operations.

## Related Skills

- **/update-framework** - Meta-skill that optionally calls this (guides sync is optional)
- **/update-pillars** - Sync Pillars documentation
- **/update-skills** - Sync skills
- **/manage-rules** - Generate project-specific rules (replaces deprecated /update-rules)
- **/manage-adrs** - Reads ADR_GUIDE.md for ADR creation
- **/manage-claude-md** - Reads CLAUDE_MD_GUIDE.md for CLAUDE.md maintenance

## Troubleshooting

**Q: Guides not syncing?**
- Check framework path exists
- Verify `.claude/guides/` in framework with 4 subdirectories
- Check file permissions

**Q: Missing guides after sync?**
- Check framework has all 4 subdirectories (workflow, doc-templates, rules, profiles)
- Verify expected file count: 18 total files
- Look for errors in sync output
- Verify target directory writable

**Q: Missing subdirectory after sync?**
- Check framework has the subdirectory
- Verify subdirectory contains expected files
- Check error messages for specific subdirectory failures

**Q: AI not using latest guides?**
- Check `.ai-guides-version` file
- Re-sync with /update-guides
- Verify AI skills read from correct path

**Q: How to verify guides are current?**
- Check `.ai-guides-version` timestamp
- Compare framework commit hash
- Re-sync if outdated

---

**Version:** 1.3.0
**Pattern:** Simple (SKILL.md + Bash script)
**Compliance:** ADR-001 ✅
**Last Updated:** 2026-03-28
**Changelog:**
- v1.3.0 (2026-03-28): Update ai-guides structure documentation - 4 subdirectories, 20 files total
- v1.2.0 (2026-03-27): Added profiles support
- v1.0.0 (2026-03-24): Initial release - sync 6 AI guides between projects
