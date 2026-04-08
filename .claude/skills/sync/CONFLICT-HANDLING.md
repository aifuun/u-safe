# Conflict Handling Guide

Detailed guide for resolving merge conflicts during branch synchronization.

## Overview

This document provides comprehensive conflict resolution strategies for the `/sync` skill. For basic sync workflow, see [SKILL.md](SKILL.md).

**When conflicts occur:**
- Git cannot automatically merge changes from main into your branch
- Manual intervention required to choose which changes to keep
- Usually occurs when same lines modified in both branches

## Quick Resolution Steps

### 1. Identify Conflicted Files

\`\`\`bash
git status

# Output shows:
# Unmerged paths:
#   both modified:   src/auth.ts
#   both modified:   src/types.ts
\`\`\`

### 2. Understand Conflict Markers

Conflicts are marked in files with these markers:

\`\`\`typescript
<<<<<<< HEAD (your branch)
export function login(user: string, pass: string) {
  return authenticate(user, pass);
}
=======
export async function login(email: string, password: string) {
  return await authenticate({ email, password });
}
>>>>>>> origin/main
\`\`\`

**Sections:**
- \`<<<<<<< HEAD\` to \`=======\` - Your branch's version
- \`=======\` to \`>>>>>>> origin/main\` - Main branch's version

### 3. Resolve Manually

**Option A: Keep your changes**
\`\`\`typescript
export function login(user: string, pass: string) {
  return authenticate(user, pass);
}
\`\`\`

**Option B: Keep main's changes**
\`\`\`typescript
export async function login(email: string, password: string) {
  return await authenticate({ email, password });
}
\`\`\`

**Option C: Merge both (most common)**
\`\`\`typescript
export async function login(email: string, password: string) {
  // Keep async from main, keep our function logic
  return await authenticate(email, password);
}
\`\`\`

### 4. Mark as Resolved and Commit

\`\`\`bash
# After editing all conflicted files
git add src/auth.ts src/types.ts

# Commit with descriptive message
CONFLICTS=\$(git diff --name-only --diff-filter=U | tr '\\n' ', ' | sed 's/,\$//')
git commit -m "resolve: merge conflicts in \${CONFLICTS}

Strategy: Manual resolution
Files: \${CONFLICTS}"
\`\`\`

## Special Cases

### package-lock.json Conflicts

**Problem:** Always conflicts on dependency updates

**Solution:** Regenerate instead of manually resolving

\`\`\`bash
# Delete the conflicted file
rm package-lock.json

# Accept main's package.json
git checkout --theirs package.json

# Regenerate lock file
npm install

# Stage and commit
git add package.json package-lock.json
git commit -m "resolve: regenerate package-lock.json after merge"
\`\`\`

### Binary Files Conflicts

**Problem:** Cannot manually edit binary files (images, PDFs)

**Solution:** Choose one version entirely

\`\`\`bash
# Keep your version
git checkout --ours path/to/image.png

# Or keep main's version
git checkout --theirs path/to/image.png

# Stage and continue
git add path/to/image.png
\`\`\`

## Conflict Prevention Tips

### 1. Sync Frequently

\`\`\`bash
# Sync daily or before starting new work
/sync

# Prevents large conflict accumulation
\`\`\`

### 2. Communicate with Team

\`\`\`bash
# Before refactoring shared code
"Hey team, I'm refactoring auth.ts today"

# Coordinate to avoid simultaneous edits
\`\`\`

## Best Practices

1. **Understand both changes** before choosing resolution
2. **Test after resolving** each conflict
3. **Commit frequently** during complex resolutions
4. **Ask for help** if unsure about correct resolution
5. **Document** why you chose specific resolution in commit message

## Related Documentation

- **[SKILL.md](SKILL.md)** - Main sync workflow
- **[SYNC-STRATEGIES.md](SYNC-STRATEGIES.md)** - Advanced sync scenarios

---

**Version:** 1.0.0
**Last Updated:** 2026-04-07
**Pattern:** Reference Guide
