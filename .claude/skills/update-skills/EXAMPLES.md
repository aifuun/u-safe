# Usage Examples - Common Scenarios

> Practical examples for update-skills in different situations

## Basic Scenarios

### Example 1: Pull Skills from Framework (Most Common)

**Scenario**: You have a project that needs the latest skills from ai-dev framework.

**Command**:
```bash
/update-skills --from ~/dev/ai-dev
```

**What happens**:
1. Deletes `.claude/skills/` in current project
2. Copies all skills from framework (excludes 7 framework-only skills)
3. Reports 28 skills synced

**Output**:
```
🔄 Syncing skills (complete replacement mode)

Source: ~/dev/ai-dev/.claude/skills/ (35 skills)
Target: ./.claude/skills/ (30 skills)

Removing target directory...
✅ Removed: .claude/skills/

Copying skills...
📊 Skills Analysis:
- Total source skills: 35
- Framework-only (excluded): 7
- Synced to target: 28

✅ Skills synced successfully!

Time: 2.3s
```

### Example 2: Preview Before Syncing

**Scenario**: Want to see what will change before actually syncing.

**Command**:
```bash
/update-skills --from ~/dev/ai-dev --dry-run
```

**Output**:
```
🔍 DRY RUN - Preview Mode

Source: ~/dev/ai-dev/.claude/skills/ (35 skills)
Target: ./.claude/skills/ (30 skills)

Would remove: .claude/skills/

Would sync: 28 skills (7 framework-only excluded)

Framework-only skills (excluded):
- update-framework
- update-skills
- update-pillars
- update-guides
- update-permissions
- update-doc-refs
- update-rules

No changes made (dry run mode).
```

### Example 3: Push Skills to Target Project

**Scenario**: You developed new skills in current project and want to push them to another project.

**Command**:
```bash
/update-skills --to ~/projects/my-app
```

**What happens**:
1. Deletes `.claude/skills/` in target project
2. Copies all skills from current project
3. Framework-only filtering applies

### Example 4: Incremental Sync with Version Detection

**Scenario**: Both projects have been modified, need version-aware sync.

**Command**:
```bash
/update-skills --from ~/dev/ai-dev --incremental
```

**Output**:
```
🔍 Scanning skills...

Source: ~/dev/ai-dev/.claude/skills/ (35 skills)
Target: ./.claude/skills/ (30 skills)

📊 Skills Analysis:
- Total source skills: 35
- Framework-only (excluded): 7
- Comparing: 28 skills

┌──────────────────┬─────────┬─────────┬──────────┬──────────┐
│ Skill            │ Source  │ Target  │ Status   │ Decision │
├──────────────────┼─────────┼─────────┼──────────┼──────────┤
│ adr              │ 1.5.0   │ 1.4.0   │ NEWER    │ Sync     │
│ status           │ 2.1.0   │ 2.1.0   │ SAME     │ Skip     │
│ review           │ 2.3.0   │ 2.4.0   │ OLDER    │ Skip     │
│ new-feature      │ 1.0.0   │ -       │ NEW      │ Sync     │
└──────────────────┴─────────┴─────────┴──────────┴──────────┘

Summary:
- NEW: 1 skill
- NEWER: 1 skill
- OLDER: 1 skill (target is newer, skipping)
- SAME: 25 skills

Total to sync: 2 skills

Continue? [Y/n]: Y

Syncing 2 skills...
✅ adr (1.4.0 → 1.5.0)
✅ new-feature (new)

✅ Skills synced successfully!
```

## Advanced Scenarios

### Example 5: Selective Skills Sync

**Scenario**: Only want to sync specific skills (adr, review, status).

**Command**:
```bash
/update-skills --from ~/dev/ai-dev --incremental --skills adr,review,status
```

**Output**:
```
🔍 Filtering skills: adr, review, status

Source skills (filtered): 3
Target skills: 30

┌──────────┬─────────┬─────────┬──────────┬──────────┐
│ Skill    │ Source  │ Target  │ Status   │ Decision │
├──────────┼─────────┼─────────┼──────────┼──────────┤
│ adr      │ 1.5.0   │ 1.4.0   │ NEWER    │ Sync     │
│ review   │ 2.3.0   │ 2.3.0   │ SAME     │ Skip     │
│ status   │ 2.1.0   │ 2.0.0   │ NEWER    │ Sync     │
└──────────┴─────────┴─────────┴──────────┴──────────┘

Total to sync: 2 skills (adr, status)

Continue? [Y/n]: Y

✅ Skills synced successfully!
```

### Example 6: Handling Version Conflicts

**Scenario**: Source and target have major version mismatches (breaking changes).

**Command**:
```bash
/update-skills --from ~/dev/ai-dev --incremental
```

**Output**:
```
⚠️  CONFLICT detected: custom-tool

Source version: 3.0.0
Target version: 2.5.0

Reason: Major version mismatch indicates breaking changes

Options:
1. Keep target version (2.5.0) - No action needed
2. Force update to source (3.0.0) - Review breaking changes first
3. Manually merge changes - Best for customizations

Recommended: Review changelog and decide manually

Skipping custom-tool (manual resolution required)
```

**Resolution**:
1. Check changelog: `cat ~/dev/ai-dev/.claude/skills/custom-tool/CHANGELOG.md`
2. Review breaking changes in v3.0.0
3. Manually merge if needed
4. Update version after testing

### Example 7: Smart Filter with Framework Config

**Scenario**: /update-framework calls update-skills with smart filtering.

**Command** (typically called by /update-framework):
```bash
/update-skills --from ~/dev/ai-dev --incremental --filter-config .claude/framework-config.json
```

**Config** (.claude/framework-config.json):
```json
{
  "filterConfig": {
    "skills": {
      "include": ["*"],
      "exclude": ["deploy-prod", "hotfix"]
    }
  }
}
```

**Output**:
```
📋 Smart Filter Active

Exclude list: deploy-prod, hotfix

⏭️  Excluding: deploy-prod (deployment skill)
⏭️  Excluding: hotfix (deployment skill)

Comparing: 26 skills (2 excluded by filter, 7 framework-only)

Result:
- Synced: 14 skills
- Skipped: 12 skills (up to date)
- Filtered: 2 skills (smart filter)
- Framework-only: 7 skills (auto-excluded)
```

## Workflow Integration

### Example 8: As Part of /update-framework

**Scenario**: Update entire framework (Pillars + Skills + Guides).

**Command**:
```bash
/update-framework ~/dev/ai-dev
```

**What happens**:
1. Sync Pillars: `update-pillars --from ~/dev/ai-dev`
2. **Sync Skills**: `update-skills --from ~/dev/ai-dev --incremental --filter-config ...`
3. Sync Guides: `update-guides --from ~/dev/ai-dev`

**update-skills part**:
```
📦 Step 2/3: Syncing Skills

/update-skills --from ~/dev/ai-dev --incremental --filter-config .claude/framework-config.json

[... incremental sync with smart filter ...]

✅ Skills synced: 14 skills (2 filtered, 7 framework-only excluded)
```

### Example 9: Monthly Framework Update Routine

**Scenario**: Regular maintenance - pull latest framework updates.

**Workflow**:
```bash
# 1. Preview changes first
/update-skills --from ~/dev/ai-dev --incremental --dry-run

# 2. Review what will change
# Check output for NEWER/NEW skills

# 3. Commit current state (safety)
git add .claude/skills/
git commit -m "chore: before framework update"

# 4. Sync with complete replacement (fast)
/update-skills --from ~/dev/ai-dev

# 5. Verify changes
git diff HEAD .claude/skills/

# 6. Test skills work
/status  # Quick sanity check

# 7. Commit updated skills
git add .claude/skills/
git commit -m "chore: update skills from framework"
```

### Example 10: Bidirectional Development

**Scenario**: Developing skills in both framework and project simultaneously.

**Workflow**:

**In framework (ai-dev)**:
```bash
# Develop new skill
cd ~/dev/ai-dev
# ... implement new-feature skill ...

# Push to project for testing
/update-skills --to ~/projects/my-app --incremental --skills new-feature
```

**In project (my-app)**:
```bash
# Test the skill
cd ~/projects/my-app
/new-feature  # Test functionality

# Make adjustments
# ... fix bugs in new-feature skill ...

# Push fixes back to framework
/update-skills --to ~/dev/ai-dev --incremental --skills new-feature
```

**In framework again**:
```bash
# Pull fixes
cd ~/dev/ai-dev
/update-skills --from ~/projects/my-app --incremental --skills new-feature

# Verify version bumped
cat .claude/skills/new-feature/SKILL.md | grep version
```

## Error Scenarios

### Example 11: Missing Framework-Only Field

**Scenario**: Skill has no `framework-only` field in YAML frontmatter.

**Behavior**:
- Defaults to `false` (included in sync)
- No error thrown
- Backward compatible

**Example**:
```yaml
---
name: custom-skill
version: "1.0.0"
# No framework-only field → defaults to false → synced normally
---
```

### Example 12: Invalid Semantic Version

**Scenario**: Skill has malformed version in YAML frontmatter.

**Example**:
```yaml
---
name: broken-skill
version: "v1.2"  # Invalid: missing patch version
---
```

**Behavior** (incremental mode):
```
⚠️  Warning: Invalid version format in broken-skill

Expected: MAJOR.MINOR.PATCH (e.g., 1.2.0)
Found: v1.2

Treating as NEW skill (will sync without version comparison)
```

### Example 13: Source Path Doesn't Exist

**Command**:
```bash
/update-skills --from ~/dev/nonexistent-project
```

**Output**:
```
❌ Error: Source path does not exist

Path: ~/dev/nonexistent-project/.claude/skills/
Expected: Valid project with .claude/skills/ directory

Fix: Check path spelling and ensure project exists
```

## Best Practices

### Practice 1: Always Preview First

```bash
# ✅ Good: Preview before syncing
/update-skills --from ~/dev/ai-dev --dry-run
# Review output
/update-skills --from ~/dev/ai-dev

# ❌ Bad: Sync blindly
/update-skills --from ~/dev/ai-dev  # No preview
```

### Practice 2: Commit Before Major Sync

```bash
# ✅ Good: Commit current state first
git add .claude/skills/
git commit -m "chore: before skills sync"
/update-skills --from ~/dev/ai-dev

# ❌ Bad: Sync with uncommitted changes
# (risk: can't easily rollback if something breaks)
```

### Practice 3: Use Complete Replacement for Framework Updates

```bash
# ✅ Good: Simple, fast, predictable
/update-skills --from ~/dev/ai-dev

# ❌ Overkill: Incremental for framework → project
/update-skills --from ~/dev/ai-dev --incremental
# (adds complexity without benefit for one-way sync)
```

### Practice 4: Use Incremental for Bidirectional Development

```bash
# ✅ Good: Version-aware, conflict detection
/update-skills --from ~/projects/my-app --incremental

# ❌ Bad: Complete replacement loses local changes
/update-skills --from ~/projects/my-app
# (deletes target .claude/skills/, loses your work!)
```

### Practice 5: Review Conflicts Manually

```bash
# When you see CONFLICT status:
# ✅ Good: Review and decide
cat .claude/skills/custom-tool/CHANGELOG.md
# Decide: keep target, force update, or manual merge

# ❌ Bad: Force update without review
# (risk: breaking changes may break your project)
```

---

**See also:**
- [SKILL.md](./SKILL.md): Core usage documentation
- [MODES.md](./MODES.md): Detailed mode explanations
- [FRAMEWORK_ONLY.md](./FRAMEWORK_ONLY.md): Framework-only filtering (Issue #401)
