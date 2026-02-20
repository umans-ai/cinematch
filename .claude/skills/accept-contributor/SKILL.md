---
name: accept-contributor
description: Accept a new contributor with write access and close their request issue
---

# Accept Contributor

Streamlined workflow for accepting new contributors to the CineMatch project.

## Usage

### `/accept-contributor USERNAME [ISSUE_NUMBER]`

Or use the just target directly:

```bash
just accept USERNAME [ISSUE_NUMBER]
```

## What It Does

1. **Adds contributor** with `push` permission (can create branches, open PRs)
2. **Posts welcome comment** with next steps
3. **Closes the issue** (if issue number provided)

## Examples

```
/accept-contributor johndoe 42
→ Adds @johndoe, comments on #42, closes #42

just accept johndoe 42
→ Same result via just

just accept johndoe
→ Adds @johndoe, no issue to close
```

## Permission Levels

| Permission | Can Do | Use Case |
|------------|--------|----------|
| `pull` | Read code | Not used |
| `push` ✅ | Push branches, PRs | **Default for contributors** |
| `maintain` | Merge to main, manage issues | Core team |
| `admin` | Full control | Repo owners |

## Notes

- Contributor must **accept the email invitation** before they can push
- `push` permission does NOT allow direct push to `main` (branch protection)
- Contributor can create branches and get preview deployments
