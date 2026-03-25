---
name: update-guides
version: "1.1.0"
description: Sync 6 AI development guides between projects - ensures AI has latest reference standards.
triggers:
  - user wants to sync AI guides
  - user mentions "update guides"
  - user wants latest AI development standards
  - after framework AI guides are updated
do_not_trigger:
  - user wants to update skills/rules/pillars (use respective update-* skills)
  - user just wants to read guides documentation
last-updated: "2026-03-24"
---

# update-guides - Sync AI Development Guides

Synchronize 6 AI development reference guides from framework to target projects.

## Overview

This skill syncs AI development reference standards (guides) between the framework and target projects.

**What it does:**
1. Detects framework's `docs/ai-guides/` directory
2. Deletes target project's `docs/ai-guides/` (if exists)
3. Copies all 6 AI guides from framework to target
4. Creates `.ai-guides-version` tracking file
5. Generates detailed sync report

**Why it's needed:**
AI skills read these guides to get development standards and workflows. When guides are updated in the framework, projects need the latest versions to ensure AI uses current best practices.

**When to use:**
- After framework guides are updated
- Setting up a new project
- Ensuring AI has latest development standards
- As part of `/update-framework` meta-skill

## What Are AI Guides?

**AI Guides are reference documentation that AI reads during task execution.**

**Primary audience**: AI (Claude Code)
- AI skills read guides to get standards, templates, workflows
- Example: `/adr` reads `ADR_GUIDE.md` to get ADR templates
- Example: `/maintain-project` reads `CLAUDE_MD_GUIDE.md` for CLAUDE.md structure

**Secondary audience**: Humans
- Humans can also read guides to understand AI's decision-making
- Helps humans review AI-generated content
- Provides transparency into AI development standards

**Location**: `docs/ai-guides/` (same in framework and projects)

## The 6 AI Guides

| Guide | Purpose | Used By Skills |
|-------|---------|----------------|
| **ADR_GUIDE.md** | AI 创建 ADR 的参考标准 | /adr, /maintain-project |
| **CLAUDE_MD_GUIDE.md** | AI 维护 CLAUDE.md 的参考标准 | /maintain-project |
| **ISSUE_LIFECYCLE_GUIDE.md** | AI 执行 issue 工作流的参考标准 | /solve-issues, /auto-solve-issue |
| **DOCS_GUIDE.md** | AI 组织文档的参考标准 | /init-docs, /check-docs |
| **PROJECT_PLANNING_GUIDE.md** | AI 规划项目的参考标准 | /plan (if exists) |
| **SKILL_GUIDE.md** | AI 创建技能的参考标准 | /skill-creator |

**All 6 guides are synced together** to ensure consistency.

## Arguments

```bash
/update-guides --from FRAMEWORK_DIR [TARGET_PROJECT]
```

**Parameters:**
- `--from FRAMEWORK_DIR` - Path to framework directory (required)
- `TARGET_PROJECT` - Path to target project (default: current directory)

**Common usage:**
```bash
# Sync from framework to specific project
/update-guides --from ~/dev/ai-dev ../u-safe

# Sync to current project
/update-guides --from ~/dev/ai-dev .

# Absolute paths
/update-guides --from /Users/woo/dev/ai-dev /Users/woo/dev/my-project
```

## Workflow Steps

### 1. Validate Framework Directory

```bash
# Check framework has docs/ai-guides/
if [ ! -d "$FRAMEWORK_DIR/docs/ai-guides" ]; then
    echo "❌ 错误：框架目录不存在 docs/ai-guides/"
    exit 1
fi

# Count guides (should be 6)
GUIDE_COUNT=$(find "$FRAMEWORK_DIR/docs/ai-guides" -name "*.md" -type f | wc -l)
if [ $GUIDE_COUNT -lt 6 ]; then
    echo "⚠️ 警告：仅找到 $GUIDE_COUNT 个 guide 文件（期望 6 个）"
fi
```

### 2. Delete Existing Target Directory

```bash
# Remove old guides if present
if [ -d "$TARGET_DIR/docs/ai-guides" ]; then
    echo "🗑️ 删除现有 ai-guides 目录..."
    rm -rf "$TARGET_DIR/docs/ai-guides"
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
cp -r "$FRAMEWORK_DIR/docs/ai-guides" "$TARGET_DIR/docs/ai-guides"

# Verify copy succeeded
if [ ! -d "$TARGET_DIR/docs/ai-guides" ]; then
    echo "❌ 错误：拷贝失败"
    exit 1
fi
```

### 4. Create Version Tracking File

```bash
# Record sync metadata
cat > "$TARGET_DIR/docs/ai-guides/.ai-guides-version" << EOF
framework_path: $FRAMEWORK_DIR
framework_commit: $(cd "$FRAMEWORK_DIR" && git rev-parse HEAD)
synced_at: $(date -Iseconds)
synced_by: update-guides.sh v1.0.0
guide_count: 6
EOF
```

**Tracking file benefits:**
- Shows when guides were last synced
- Records source framework version (git commit)
- Helps debug outdated guides

### 5. Generate Sync Report

```bash
echo "✅ 同步完成"
echo ""
echo "| Guide | 状态 | 用途 |"
echo "|-------|------|------|"
echo "| ADR_GUIDE.md | ✅ | AI 创建 ADR 的参考标准 |"
echo "| CLAUDE_MD_GUIDE.md | ✅ | AI 维护 CLAUDE.md 的参考标准 |"
echo "| ISSUE_LIFECYCLE_GUIDE.md | ✅ | AI 执行 issue 工作流的参考标准 |"
echo "| DOCS_GUIDE.md | ✅ | AI 组织文档的参考标准 |"
echo "| PROJECT_PLANNING_GUIDE.md | ✅ | AI 规划项目的参考标准 |"
echo "| SKILL_GUIDE.md | ✅ | AI 创建技能的参考标准 |"
echo ""
echo "AI 现在可以使用最新的开发参考标准"
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
   框架: /Users/woo/dev/ai-dev/docs/ai-guides
   目标: /Users/woo/dev/u-safe/docs/ai-guides

🗑️ 删除现有 ai-guides 目录...
📋 拷贝 AI 开发指南...
📝 创建版本标记...

✅ 同步完成

| Guide | 状态 | 用途 |
|-------|------|------|
| ADR_GUIDE.md | ✅ | AI 创建 ADR 的参考标准 |
| CLAUDE_MD_GUIDE.md | ✅ | AI 维护 CLAUDE.md 的参考标准 |
| ISSUE_LIFECYCLE_GUIDE.md | ✅ | AI 执行 issue 工作流的参考标准 |
| DOCS_GUIDE.md | ✅ | AI 组织文档的参考标准 |
| PROJECT_PLANNING_GUIDE.md | ✅ | AI 规划项目的参考标准 |
| SKILL_GUIDE.md | ✅ | AI 创建技能的参考标准 |

AI 现在可以使用最新的开发参考标准
```

### Example 2: Error Handling - Framework Missing

**Command:**
```bash
/update-guides --from /invalid/path ../my-project
```

**Output:**
```
❌ 错误：框架目录不存在 AI guides
   期望路径: /invalid/path/docs/ai-guides

请确保框架目录包含 docs/ai-guides/ 并且已创建所有 6 大 guides。
```

### Example 3: Warning - Incomplete Guides

**Scenario:** Framework only has 4 out of 6 guides

**Output:**
```
⚠️ 警告：框架中仅找到 4 个 guide 文件（期望 6 个）

📋 拷贝 AI 开发指南...
...
✅ 同步完成 (with missing guides marked ❌)
```

## Integration

### With /update-framework Meta-Skill

```bash
# Complete framework sync
/update-framework ../target-project
  → Calls /update-pillars
  → Calls /update-rules
  → Calls /update-workflow
  → Calls /update-skills
  → Calls /update-guides ← THIS SKILL
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
- `/adr` - Reads `ADR_GUIDE.md` for ADR templates and standards
- `/maintain-project` - Reads `CLAUDE_MD_GUIDE.md` for CLAUDE.md structure
- `/solve-issues` - Reads `ISSUE_LIFECYCLE_GUIDE.md` for workflow
- `/init-docs` - Reads `DOCS_GUIDE.md` for documentation structure
- `/check-docs` - Reads `DOCS_GUIDE.md` for validation standards
- `/skill-creator` - Reads `SKILL_GUIDE.md` for skill patterns

**Workflow:**
```
1. Update guides in framework: Edit docs/ai-guides/*.md
2. Sync to projects: /update-guides --from framework project
3. AI skills read guides: Skills use Read tool to access guides
4. AI executes with standards: Guides inform AI's decisions
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Framework path missing | --from not specified | Add --from argument |
| Framework guides missing | docs/ai-guides/ doesn't exist | Create guides in framework first |
| Target not writable | Permission denied | Check directory permissions |
| Copy failed | Disk full, permissions | Check disk space and permissions |
| Incomplete guides | <6 guides found | Warning shown, continues anyway |

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
- Sync is fast (6 markdown files)
- No risk of partial updates

## Version Tracking

**File:** `docs/ai-guides/.ai-guides-version`

**Content:**
```yaml
framework_path: /Users/woo/dev/ai-dev
framework_commit: a1b2c3d4e5f6...
synced_at: 2026-03-24T10:00:00+08:00
synced_by: update-guides.sh v1.0.0
guide_count: 6
```

**Usage:**
- Check when guides were last synced
- Verify source framework version
- Debug guide inconsistencies
- Track sync history

## Performance

- **Execution time:** <2 seconds (6 markdown files)
- **Disk space:** ~50KB (all 6 guides)
- **Network:** None (local file copy)

Fast because:
- Simple file copy operation
- No network requests
- No complex processing

## Related Skills

- **/update-framework** - Meta-skill that calls this (complete sync)
- **/update-pillars** - Sync Pillars documentation
- **/update-rules** - Sync technical rules
- **/update-skills** - Sync skills
- **/update-workflow** - Sync workflow documentation
- **/adr** - Reads ADR_GUIDE.md
- **/maintain-project** - Reads CLAUDE_MD_GUIDE.md

## Troubleshooting

**Q: Guides not syncing?**
- Check framework path exists
- Verify `docs/ai-guides/` in framework
- Check file permissions

**Q: Missing guides after sync?**
- Check framework has all 6 guides
- Look for errors in sync output
- Verify target directory writable

**Q: AI not using latest guides?**
- Check `.ai-guides-version` file
- Re-sync with /update-guides
- Verify AI skills read from correct path

**Q: How to verify guides are current?**
- Check `.ai-guides-version` timestamp
- Compare framework commit hash
- Re-sync if outdated

---

**Version:** 1.0.0
**Pattern:** Simple (SKILL.md + Bash script)
**Compliance:** ADR-001 ✅
**Last Updated:** 2026-03-24
**Changelog:**
- v1.0.0 (2026-03-24): Initial release - sync 6 AI guides between projects
