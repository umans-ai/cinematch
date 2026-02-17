---
name: cli-release
description: CLI release workflow - bump version, run checks, commit, tag
---

# CLI Release Workflow

Complete release workflow for the CLI package.

## Usage

### `/cli-release bump [patch|minor|major]`

Bump version, run full checks, commit.

### `/cli-release publish`

Full release: bump patch → checks → commit → tag → push.

## Workflow: bump

1. **Read current version**
   - Parse version from `cli/pyproject.toml` or `cli/umans_cli/__init__.py`

2. **Calculate new version**
   - patch: 0.1.2 → 0.1.3
   - minor: 0.1.2 → 0.2.0
   - major: 0.1.2 → 1.0.0

3. **Update version files**
   - `cli/pyproject.toml`
   - `cli/umans_cli/__init__.py` (if __version__ defined)

4. **Run just cli-checks**
   - Must pass before commit

5. **Commit**
   ```
   chore: bump CLI version to X.Y.Z 📦
   ```

6. **Push**
   ```
   git push origin main
   ```

## Workflow: publish

1. Run `bump patch` workflow above
2. **Create tag**
   ```
   git tag cli-vX.Y.Z
   ```
3. **Push tag**
   ```
   git push origin cli-vX.Y.Z
   ```

## Safety Checks

- Must be on main branch
- Working directory clean
- All cli-checks must pass
- Version must be newer than current

## Examples

```
/cli-release bump patch
→ Bump 0.1.2 → 0.1.3
→ Run just cli-checks...
→ Commit: chore: bump CLI version to 0.1.3 📦
→ Push to origin/main

/cli-release publish
→ Full workflow: bump → checks → commit → tag → push
→ Created tag cli-v0.1.3
```

## Errors

- Not on main → "Error: Must be on main branch"
- Uncommitted changes → "Error: Working directory not clean"
- Checks fail → "Error: cli-checks failed. Fix before release."
- Version already exists → "Error: Version X.Y.Z already tagged"
