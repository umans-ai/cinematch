---
name: just
description: Intelligent just target wrapper with context-aware suggestions
---

# Just Helper

Smart wrapper for just targets with context detection.

## Usage

### `/just [target]`

Without target: detects context and suggests appropriate target.
With target: runs just <target>, verifies target exists first.

## Context Detection

| Context | Suggested Target |
|---------|------------------|
| Modified tests/ | `just test tests/<modified> -v` |
| Modified CLI code | `just cli-checks` |
| Modified justfile | `just check` |
| No changes staged | `just check` (full verification) |
| On feature branch, pre-commit | `just check` |
| After git add | `just check` before commit |

## Commands

### `/just`
Analyze context and suggest:
```
Detected: Modified cli/ code
Suggested: just cli-checks
Run? [Y/n/custom target]
```

### `/just <target>`
Verify target exists in justfile, then run:
```
/just cli-checks
→ Running: just cli-checks...
```

### `/just list`
Show all available targets with descriptions.

### `/just logs`
Show recent just output from current session.

## Common Targets Reference

- `just check` - Full check suite (lint + typecheck + test + cli-checks)
- `just test` - Run all tests
- `just test tests/specific.py -v` - Run specific test verbose
- `just cli-checks` - CLI syntax + static + runtime checks
- `just cli-syntax` - Fast syntax validation
- `just dev` - Start dev server
- `just fake` - Start fake upstream
- `just obs-5xx-by-route` - Observability: 5xx errors by route

## Errors

- Target not found → "Error: Target '<name>' not in justfile. Run: /just list"
- just not installed → "Error: just not found. Install: brew install just"
