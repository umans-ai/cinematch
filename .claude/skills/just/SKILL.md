---
name: just
description: Intelligent just target wrapper with context-aware suggestions for CineMatch
---

# Just Helper

Smart wrapper for just targets with context detection for CineMatch.

## Usage

### `/just [target]`

Without target: detects context and suggests appropriate target.
With target: runs just <target>, verifies target exists first.

## Context Detection

| Context | Suggested Target |
|---------|------------------|
| Modified tests/ | `just test tests/<modified> -v` |
| Modified justfile | `just check` |
| No changes staged | `just check` (full verification) |
| On feature branch, pre-commit | `just check` |
| After git add | `just check` before commit |
| Need to start dev | `just dev-local` |
| Check if services running | `just dev-local-status` |

## Commands

### `/just`
Analyze context and suggest:
```
Detected: Modified backend tests
Suggested: just test tests/test_rooms.py -v
Run? [Y/n/custom target]
```

### `/just <target>`
Verify target exists in justfile, then run:
```
/just dev-local
→ Running: just dev-local...
```

### `/just list`
Show all available targets with descriptions.

### `/just status`
Check if dev services are running.

## Common Targets Reference

### Root-level
- `just check` - Full check suite (backend + frontend)
- `just test` - Run backend tests only
- `just dev-local` - Start dev environment (PostgreSQL + backend + frontend)
- `just dev-local-status` - Check if services are running
- `just dev-local-logs` - View combined logs
- `just dev-local-stop` - Stop all services

### Backend (cd backend)
- `just check` - lint + fmt + typecheck + test + audit
- `just test` - Run tests
- `just lint` - ruff check
- `just fmt` - ruff format
- `just typecheck` - ty check
- `just dev-local` - Start backend only
- `just sync` - Sync dependencies

### Frontend (cd frontend)
- `just check` - lint + typecheck
- `just lint` - eslint
- `just typecheck` - tsc
- `just dev` - Start dev server
- `just build` - Build for production

## Errors

- Target not found → "Error: Target '<name>' not in justfile. Run: /just list"
- just not installed → "Error: just not found. Install: brew install just"
