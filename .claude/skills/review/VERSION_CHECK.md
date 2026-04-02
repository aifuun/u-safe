# Skill Version Check - Prevent Version Conflicts

Automated version number validation for skill modifications.

## Overview

**CRITICAL CHECK**: When SKILL.md files are modified, verify version numbers are updated.

**Why this matters:**
- Developers often forget to update version numbers when modifying skills
- Outdated versions cause CONFLICT状态 during `/update-skills` sync (Issue #285)
- Early detection prevents sync issues and wasted debugging time

**When to run:**
- Triggered when git diff shows changes to any `.claude/skills/*/SKILL.md` file
- Skip if no SKILL.md files were modified (performance optimization)

## Implementation (AI-EXECUTABLE)

### Step 1: Detect Modified SKILL.md Files

```bash
# Get list of modified SKILL.md files
git diff --name-only HEAD | grep '.claude/skills/.*/SKILL.md' > /tmp/modified-skills.txt

# If empty, skip version check
if [ ! -s /tmp/modified-skills.txt ]; then
  echo "ℹ️ No SKILL.md files modified, skipping version check"
  exit 0
fi
```

### Step 2: Compare Versions for Each Modified Skill

```bash
while read skill_file; do
  # Extract current version from YAML frontmatter
  CURRENT_VERSION=$(grep '^version:' "$skill_file" | sed 's/version: *"\(.*\)"/\1/')

  # Extract previous version from HEAD
  OLD_VERSION=$(git show HEAD:"$skill_file" | grep '^version:' | sed 's/version: *"\(.*\)"/\1/')

  # Compare versions
  if [ "$CURRENT_VERSION" = "$OLD_VERSION" ]; then
    # Content changed but version unchanged - record issue
    echo "⚠️ Version not updated: $skill_file"
    echo "   Current: $CURRENT_VERSION"
    echo "   Content: CHANGED"
    echo "   Action: NEEDS_VERSION_BUMP"

    # Detect change type and suggest version bump
    DIFF=$(git diff HEAD -- "$skill_file")
    if echo "$DIFF" | grep -qE "BREAKING|removed|deleted"; then
      SUGGESTED="major bump ($(semver_increment "$CURRENT_VERSION" major))"
    elif echo "$DIFF" | grep -qE "added|new feature|enhance"; then
      SUGGESTED="minor bump ($(semver_increment "$CURRENT_VERSION" minor))"
    else
      SUGGESTED="patch bump ($(semver_increment "$CURRENT_VERSION" patch))"
    fi

    echo "   Suggested: $SUGGESTED"
    echo ""
  fi
done < /tmp/modified-skills.txt
```

### Step 3: Version Increment Helper

```bash
function semver_increment() {
  local version=$1
  local part=$2

  # Parse semantic version (major.minor.patch)
  IFS='.' read -r major minor patch <<< "$version"

  case $part in
    major)
      echo "$((major + 1)).0.0"
      ;;
    minor)
      echo "$major.$((minor + 1)).0"
      ;;
    patch)
      echo "$major.$minor.$((patch + 1))"
      ;;
  esac
}
```

## Change Type Detection

**Keywords to detect version bump type:**

### Major Bump (Breaking Changes)
- Keywords: "BREAKING", "removed", "deleted parameter", "incompatible"
- Examples: Removed arguments, changed behavior, API breakage
- Version: X.0.0 → (X+1).0.0

### Minor Bump (New Features)
- Keywords: "added", "new feature", "new parameter", "enhance"
- Examples: New functionality, new options, backward-compatible changes
- Version: X.Y.0 → X.(Y+1).0

### Patch Bump (Bug Fixes/Docs)
- Default for all other changes
- Examples: Bug fixes, documentation updates, typo corrections
- Version: X.Y.Z → X.Y.(Z+1)

## Output Format

### Interactive Mode
```markdown
## 3. Skill版本检查 ✅/⚠️

**修改的Skills**: 2个

✅ `.claude/skills/eval-plan/SKILL.md`
   版本: 1.1.0 → 1.2.0 (minor bump)
   变更: 添加auto-fix功能

⚠️ `.claude/skills/review/SKILL.md`
   版本: 2.2.0 (未更新) ← 内容已变化
   建议: minor bump → 2.3.0
   原因: 添加了版本检查功能

   修复方法:
   1. Edit .claude/skills/review/SKILL.md
   2. Change: version: "2.2.0"
   3. To: version: "2.3.0"
   4. Re-run /review
```

### Auto Mode (2 lines max)
```
Skill version check: 1 issue found
⚠️ review/SKILL.md unchanged (2.2.0) - suggest 2.3.0
```

## Integration with Review Status

Add to `.claude/.review-status.json`:

```json
{
  "skill_version_check": {
    "modified_skills": 2,
    "version_issues": 1,
    "issues": [
      {
        "file": ".claude/skills/review/SKILL.md",
        "current_version": "2.2.0",
        "suggested_version": "2.3.0",
        "change_type": "minor",
        "reason": "Added version check feature"
      }
    ],
    "status": "NEEDS_IMPROVEMENT"
  }
}
```

## Pass/Fail Logic

```javascript
if (version_issues.length > 0) {
  return {
    status: 'NEEDS_IMPROVEMENT',
    blocking: true,
    reason: 'Skill version numbers not updated',
    fix: 'Update version numbers in YAML frontmatter'
  };
}
```

## Performance Optimization

- Only runs when `.claude/skills/*/SKILL.md` files are modified
- Uses `git diff --name-only` for fast file detection
- Skips check entirely if no skills modified

## Example Scenario (Issue #285)

```
修改了 .claude/skills/update-skills/SKILL.md
- 内容: 添加了 --clean 默认行为
- 版本: 2.4.0 (未更新)
- 检测: ⚠️ Breaking change detected
- 建议: major bump → 3.0.0
- 原因: 默认行为改变是破坏性变更
```

## Related

- **Parent skill**: `/review` - Main code review skill
- **Issue #401**: Original implementation of version checking
- **Issue #285**: Conflict detection problem this solves

---

**Version:** 1.0.0
**Last Updated:** 2026-03-30
**Part of:** review skill v2.4.0
**Pattern:** AI-EXECUTABLE bash logic
