# Phase D: Release

> Part of the 4-Phase AI-Assisted Development Workflow
> See: [MAIN.md](./MAIN.md) for complete overview

**Load when**: Preparing a new version release

## When to Use

- Releasing a new version
- Creating release notes
- Publishing to npm/crates.io
- Deploying infrastructure changes

## Release Process

| Version Type | When | Example |
|--------------|------|---------|
| `patch` | Bug fixes | 0.1.0 → 0.1.1 |
| `minor` | New features | 0.1.0 → 0.2.0 |
| `major` | Breaking changes | 0.1.0 → 1.0.0 |

### Release Workflow

```bash
*release [patch|minor|major]
```

**Steps**:
1. Bump version in package.json
2. Update CHANGELOG.md
3. Create release commit
4. Tag release
5. Push to remote
6. Deploy if needed

---

## Post-Release

- [ ] Verify deployment/publish
- [ ] Announce release (if needed)
- [ ] Update MEMORY.md with release notes
- [ ] Close milestone

---

## Hotfix Workflow

For urgent production bugs:

### 1. Create hotfix branch
```bash
git checkout main
git pull
git checkout -b hotfix/issue-description
```

### 2. Fix and test
- Minimal change to fix the issue
- Run tests: `npm test`

### 3. Release
```bash
*release patch
```

### 4. Merge back
```bash
git checkout main
git merge hotfix/issue-description
git push
git branch -d hotfix/issue-description
```

### 5. Deploy immediately
```bash
*cdk deploy  # if infrastructure affected
```

---

## Best Practices

- Keep hotfixes minimal (single bug fix)
- Test thoroughly before release
- Update documentation after release
- Announce breaking changes in release notes

---

**Part of**: 4-Phase Workflow (A → B → C → **D**)
