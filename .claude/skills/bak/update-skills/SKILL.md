---
name: update-skills
description: |
  Sync skills between projects - copy from or push to other projects.
  Detects new/updated skills, shows diffs, handles conflicts intelligently.
  Essential for maintaining skill consistency across multiple projects.
disable-model-invocation: true
user-invocable: true
argument-hint: "--from <project> | --to <project> [--dry-run] [--skills skill1,skill2]"
allowed-tools: Read, Glob, Bash(cp *), Bash(diff *), Bash(find *), Bash(wc *), Write
context: fork
agent: general-purpose
---

# Update Skills - Project Skills Synchronization

Sync skills between ai-dev framework and other projects bidirectionally.

## Purpose

**Why This Skill Exists**:
- ✅ Maintain skill consistency across multiple projects
- ✅ Easily update project skills from framework updates
- ✅ Promote local skills to framework (like adr, create-issues)
- ✅ Detect new/updated skills automatically
- ✅ Preview changes before applying (--dry-run)
- ✅ Handle version conflicts intelligently

---

## Usage

### Pull skills from another project
```bash
/update-skills --from ../buffer2
/update-skills --from ../buffer2 --dry-run
/update-skills --from ../buffer2 --skills adr,status
```

### Push skills to another project
```bash
/update-skills --to ../buffer
/update-skills --to ../buffer --dry-run
/update-skills --to ../buffer --skills create-issues,start-issue,finish-issue
```

---

## Commands

### 1. Pull Skills (--from)

**Command**: `/update-skills --from <project-path>`

**What It Does**:
1. **Scan source project**: Find all skills in `<project>/.claude/skills/`
2. **Compare with current**: Check which skills are new or updated
3. **Detect changes**: Compare file sizes, modification times, content
4. **Show diff**: Display what will change
5. **Confirm**: Ask user to proceed (unless --dry-run)
6. **Copy**: Update current project with new/updated skills
7. **Report**: Show what was copied/updated

**Example**:
```bash
User: /update-skills --from ../buffer2

AI Response:
📥 Pulling skills from ../buffer2

Scanning skills...
✅ Found 22 skills in ../buffer2/.claude/skills/
✅ Found 21 skills in current project

📊 Analysis:
┌─────────────────┬────────┬──────────────────┐
│ Skill           │ Status │ Action           │
├─────────────────┼────────┼──────────────────┤
│ adr             │ NEWER  │ Update (443 vs 408 lines) │
│ create-issues   │ NEW    │ Copy (617 lines) │
│ start-issue     │ NEW    │ Copy (554 lines) │
│ finish-issue    │ NEW    │ Copy (557 lines) │
│ status          │ SAME   │ Skip             │
│ (15 others)     │ SAME   │ Skip             │
└─────────────────┴────────┴──────────────────┘

Summary:
- New skills: 3
- Updated skills: 1
- Unchanged: 18
- Total to copy: 4 skills (2,171 lines)

Proceed? (y/n)
```

**Implementation Steps**:
1. Resolve paths (handle relative paths like `../buffer2`)
2. Verify source exists: `[ -d "$SOURCE/.claude/skills" ]`
3. Scan source skills: `find "$SOURCE/.claude/skills" -name "SKILL.md"`
4. For each skill:
   - Check if exists locally
   - Compare modification time: `stat -f %m`
   - Compare file size: `wc -l`
   - Detect status: NEW, NEWER, OLDER, SAME
5. Build comparison table
6. If --dry-run: show table and exit
7. Ask confirmation
8. Copy updated/new skills: `cp -r "$SOURCE/.claude/skills/$skill" .claude/skills/`
9. Report results

---

### 2. Push Skills (--to)

**Command**: `/update-skills --to <project-path>`

**What It Does**:
1. **Scan current skills**: Find all skills in current project
2. **Compare with target**: Check which skills are new or updated
3. **Show diff**: Display what will change in target project
4. **Confirm**: Ask user to proceed
5. **Copy**: Update target project with new/updated skills
6. **Report**: Show what was pushed

**Example**:
```bash
User: /update-skills --to ../buffer --skills create-issues,start-issue

AI Response:
📤 Pushing skills to ../buffer

Selected skills: create-issues, start-issue

Checking target project...
✅ Target exists: ../buffer/.claude/skills/

📊 Analysis:
┌─────────────────┬────────┬──────────────────┐
│ Skill           │ Status │ Action           │
├─────────────────┼────────┼──────────────────┤
│ create-issues   │ NEW    │ Add (617 lines)  │
│ start-issue     │ NEW    │ Add (554 lines)  │
└─────────────────┴────────┴──────────────────┘

Summary:
- New skills: 2
- Total to push: 2 skills (1,171 lines)

⚠️  Warning: This will modify ../buffer/.claude/skills/

Proceed? (y/n)
```

---

### 3. Dry Run Mode (--dry-run)

**Flag**: `--dry-run`

**What It Does**:
- Shows what would happen WITHOUT making changes
- Perfect for previewing updates
- No confirmation required
- Safe to run anytime

**Example**:
```bash
User: /update-skills --from ../buffer2 --dry-run

AI Response:
📥 DRY RUN: Pulling skills from ../buffer2

[Same analysis as above]

Summary:
- New skills: 3
- Updated skills: 1
- Unchanged: 18
- Total to copy: 4 skills (2,171 lines)

🔍 DRY RUN MODE - No changes made
Run without --dry-run to apply changes
```

---

### 4. Selective Update (--skills)

**Flag**: `--skills skill1,skill2,skill3`

**What It Does**:
- Only sync specified skills
- Comma-separated list
- Ignores other skills

**Example**:
```bash
User: /update-skills --from ../buffer2 --skills adr,status

AI Response:
📥 Pulling skills from ../buffer2

Selected skills: adr, status

📊 Analysis:
┌─────────────────┬────────┬──────────────────┐
│ Skill           │ Status │ Action           │
├─────────────────┼────────┼──────────────────┤
│ adr             │ NEWER  │ Update (443 vs 408 lines) │
│ status          │ SAME   │ Skip             │
└─────────────────┴────────┴──────────────────┘

Summary:
- New skills: 0
- Updated skills: 1
- Skipped: 1 (unchanged)

Proceed? (y/n)
```

---

## Conflict Resolution

### Version Detection

When comparing skills, check:
1. **Modification time**: `stat -f %m file.md` (newer = updated)
2. **File size**: `wc -l file.md` (different = changed)
3. **Content hash**: `md5 file.md` (same hash = identical)

**Status Logic**:
```bash
if target doesn't exist:
  status = NEW
elif source_mtime > target_mtime:
  status = NEWER
elif source_mtime < target_mtime:
  status = OLDER
elif source_size != target_size:
  status = CONFLICT (manual review needed)
else:
  status = SAME
```

### Handling OLDER/CONFLICT

**OLDER** (source is older than target):
```
⚠️  Warning: Source skill is OLDER than target

Skill: status
Source: 2026-03-01 (220 lines)
Target: 2026-03-04 (223 lines)

Options:
1. Skip (recommended) - Keep newer version
2. Overwrite - Replace with older version
3. Diff - Show differences

Choice (1/2/3):
```

**CONFLICT** (modification times equal, but content differs):
```
❌ Conflict detected

Skill: adr
Source: modified 2026-03-04 14:59 (443 lines)
Target: modified 2026-03-04 14:59 (408 lines)

This means both versions were modified at the same time but have different content.

Options:
1. Skip - Keep current version
2. Show diff - Compare line by line
3. Overwrite - Use source version
4. Manual merge - Open both files

Choice (1/2/3/4):
```

---

## Advanced Features

### 1. Diff View

**Show detailed differences**:
```bash
When conflicts detected, offer to show diff:

$ diff -u target/adr/SKILL.md source/adr/SKILL.md

--- target/adr/SKILL.md
+++ source/adr/SKILL.md
@@ -1,5 +1,5 @@
 ---
 name: adr
-description: Create and manage ADRs
+description: Create and manage Architecture Decision Records (ADRs) with standardized workflow.
+  Handles numbering, formatting, indexing automatically.
...

Lines changed: +35, -0
```

### 2. Backup Before Overwrite

**Automatic backup**:
```bash
Before overwriting any skill:

✅ Creating backup: .claude/skills/adr.backup-2026-03-04/
✅ Backed up: adr/SKILL.md

Now updating adr...
✅ Updated: adr (408 → 443 lines)

Rollback available: .claude/skills/adr.backup-2026-03-04/
```

### 3. Batch Operations

**Update multiple projects**:
```bash
# Push to multiple projects
/update-skills --to ../buffer,../buffer2,../project3 --skills adr
```

---

## Common Use Cases

### Use Case 1: Update project from framework
```bash
# In your project
cd ~/projects/my-app

# Pull latest skills from framework
/update-skills --from ~/dev/ai-dev

# Preview first
/update-skills --from ~/dev/ai-dev --dry-run

# Update specific skills
/update-skills --from ~/dev/ai-dev --skills status,adr
```

### Use Case 2: Promote project skills to framework
```bash
# In framework repo
cd ~/dev/ai-dev

# Pull new skills from project
/update-skills --from ~/projects/my-app --skills custom-deploy,custom-test

# Or push framework updates to project
/update-skills --to ~/projects/my-app
```

### Use Case 3: Sync between projects
```bash
# Copy skills from buffer2 to buffer
cd ~/dev/buffer

/update-skills --from ../buffer2 --skills create-issues,start-issue,finish-issue
```

### Use Case 4: Framework maintenance
```bash
# Update all example projects with latest skills
cd ~/dev/ai-dev

/update-skills --to examples/minimal-example
/update-skills --to examples/node-lambda-example
/update-skills --to examples/react-aws-example
```

---

## Implementation Details

### Directory Structure

**Source Detection**:
```bash
# Resolve source project
SOURCE=$(cd "$ARG_PATH" && pwd)
SOURCE_SKILLS="$SOURCE/.claude/skills"

# Verify exists
if [ ! -d "$SOURCE_SKILLS" ]; then
  echo "❌ Error: $SOURCE_SKILLS not found"
  exit 1
fi
```

**Skill Enumeration**:
```bash
# Find all skills (directories with SKILL.md)
find "$SOURCE_SKILLS" -maxdepth 1 -type d | while read dir; do
  if [ -f "$dir/SKILL.md" ]; then
    skill_name=$(basename "$dir")
    # Process skill...
  fi
done
```

### Comparison Algorithm

```bash
compare_skill() {
  local skill=$1
  local source_file="$SOURCE_SKILLS/$skill/SKILL.md"
  local target_file=".claude/skills/$skill/SKILL.md"

  # Check existence
  if [ ! -f "$target_file" ]; then
    echo "NEW"
    return
  fi

  # Compare modification time
  source_mtime=$(stat -f %m "$source_file" 2>/dev/null || stat -c %Y "$source_file")
  target_mtime=$(stat -f %m "$target_file" 2>/dev/null || stat -c %Y "$target_file")

  # Compare size
  source_lines=$(wc -l < "$source_file")
  target_lines=$(wc -l < "$target_file")

  if [ $source_mtime -gt $target_mtime ]; then
    echo "NEWER"
  elif [ $source_mtime -lt $target_mtime ]; then
    echo "OLDER"
  elif [ $source_lines -ne $target_lines ]; then
    echo "CONFLICT"
  else
    echo "SAME"
  fi
}
```

### Copy Operation

```bash
copy_skill() {
  local skill=$1
  local source_dir="$SOURCE_SKILLS/$skill"
  local target_dir=".claude/skills/$skill"

  # Backup if exists
  if [ -d "$target_dir" ]; then
    backup_dir=".claude/skills/${skill}.backup-$(date +%Y-%m-%d-%H%M%S)"
    cp -r "$target_dir" "$backup_dir"
    echo "✅ Backed up to: $backup_dir"
  fi

  # Copy entire skill directory (includes SKILL.md, scripts, templates, etc.)
  cp -r "$source_dir" "$target_dir"

  # Report
  lines=$(wc -l < "$target_dir/SKILL.md")
  echo "✅ Copied: $skill ($lines lines)"
}
```

---

## Error Handling

### Invalid Source/Target
```
❌ Error: Project not found

Path: ../nonexistent
Expected: ../nonexistent/.claude/skills/

Please check:
1. Path is correct
2. Project has .claude/skills/ directory
3. You have read permissions
```

### No Skills to Update
```
✅ All skills are up to date!

No new or updated skills found in source.
Current project has all latest versions.
```

### Permission Issues
```
❌ Error: Permission denied

Cannot write to: ../buffer/.claude/skills/

Please check:
1. You have write permissions
2. Directory is not read-only
3. No other process is locking the directory
```

---

## Best Practices

### 1. Always dry-run first
```bash
# Preview before applying
/update-skills --from ../buffer2 --dry-run
# Then apply if looks good
/update-skills --from ../buffer2
```

### 2. Selective updates for safety
```bash
# Update only specific skills you trust
/update-skills --from ../buffer2 --skills adr,status
```

### 3. Keep framework as source of truth
```bash
# In projects: pull from framework
/update-skills --from ~/dev/ai-dev

# In framework: pull innovations from projects
/update-skills --from ~/projects/buffer2 --skills create-issues,start-issue
```

### 4. Document custom skills
```bash
# Before pushing custom skills to framework, ensure:
- [ ] Skill has complete YAML config
- [ ] Documentation is detailed (200+ lines recommended)
- [ ] Examples are comprehensive
- [ ] Follows framework conventions
- [ ] No project-specific hardcoded paths
```

---

## Output Examples

### Success Output
```
📥 Pulling skills from ../buffer2

Scanning skills...
✅ Found 22 skills in ../buffer2
✅ Found 21 skills in current project

📊 Analysis complete

Copying 4 skills:
✅ adr (443 lines) - Updated
✅ create-issues (617 lines) - New
✅ start-issue (554 lines) - New
✅ finish-issue (557 lines) - New

Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total processed: 4 skills
Total lines: 2,171
Time: 2.3s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Skills updated successfully!

Next steps:
1. Review changes: git diff .claude/skills/
2. Test skills: /adr list, /create-issues --dry-run
3. Commit if satisfied: git add .claude/skills/
```

---

## Related Skills

- **/status** - Check project status after updating skills
- **/validate** - Validate skill configurations
- **/tidy** - Clean up backup files

---

## Quick Reference

```bash
# Pull from framework
/update-skills --from ~/dev/ai-dev

# Push to project
/update-skills --to ~/projects/my-app

# Dry run
/update-skills --from ../buffer2 --dry-run

# Specific skills
/update-skills --from ../buffer2 --skills adr,status

# Multiple targets
/update-skills --to ../buffer,../buffer2
```

---

**Last Updated**: 2026-03-04
**Version**: 1.0
**Status**: Production Ready
