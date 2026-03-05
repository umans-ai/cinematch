# 00015 - Fix dev-local-stop port cleanup

## Problem

`just dev-local-stop` did not kill orphan frontend processes still listening on port 3000.
Additionally, the `dev-local` wait loop used a wrong container name (`cinematch-main-postgres-1` instead of `cinematch-postgres-1`), causing an infinite hang.

## Solution

- Kill processes listening on frontend ports (3000, 3001) on stop
- Fix PostgreSQL container name in wait loop

## Verification

- `just dev-local` starts cleanly without hanging
- `just dev-local-stop` stops all services including orphan frontend ports

## Status

PR #26 open — pending merge.
