---
name: release
description: |
  Create a new release - bump version, tag, publish to npm/cargo.
  Automates versioning, changelog, and package publishing.
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash(git *), Bash(npm *), Bash(cargo *)
context: fork
agent: general-purpose
---

# Release Manager

Create and publish new releases.

## Task

Automate release process:
1. **Determine version** - major, minor, patch
2. **Bump version** - package.json, Cargo.toml, VERSION file
3. **Create changelog** - Summarize changes since last release
4. **Git tag** - Tag commit with version
5. **Publish** - npm publish, cargo publish, etc.

## Versioning

Follows Semantic Versioning (MAJOR.MINOR.PATCH):
- `patch`: Bug fixes, small improvements (1.0.0 → 1.0.1)
- `minor`: New features, backwards compatible (1.0.0 → 1.1.0)
- `major`: Breaking changes (1.0.0 → 2.0.0)

## Process

Execute: `bash scripts/release.sh [patch|minor|major]`

```
$ release.sh patch

🚀 Creating v1.0.1 release

Changes since v1.0.0:
- fix: auth token expiration
- fix: database connection pooling
- docs: update API docs

Create changelog? (Y/n)
[Generated changelog...]

Tag commit as v1.0.1? (Y/n)
Publish to npm? (Y/n)

✅ Release v1.0.1 published!
```

---

Ensures:
- Proper versioning
- Documented changes
- Git history
- Published artifacts
