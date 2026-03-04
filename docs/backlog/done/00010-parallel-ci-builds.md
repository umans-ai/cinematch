# Parallelize CI Builds

## Goal

Run check, backend build, and frontend build in parallel to reduce total pipeline time.

## Context

Current workflow is sequential:
```
check (1m) → deploy (build back + build front + terraform)
```

With BuildKit cache, the builds are faster but still sequential.

## Proposed Architecture

```
        ┌→ check ──────┐
        ├→ build back ─┼→ deploy
        └→ build front─┘
```

All three jobs run in parallel. Deploy waits for all three to succeed.

## Ship Criteria

- [ ] Check, build-backend, build-frontend jobs run in parallel
- [ ] Deploy job waits for all three
- [ ] Total pipeline time reduced by ~20-30s
- [ ] Fail-fast: if check fails, deploy doesn't run
- [ ] Preview deployments still work

## Uncertainties

- [ ] Will the extra parallel jobs increase CI costs significantly?

## Implementation Plan

1. Split deploy job into 3 parallel jobs:
   - `check` (existing)
   - `build-backend` (new - docker build/push)
   - `build-frontend` (new - docker build/push)

2. Create new `deploy` job that depends on all three:
   ```yaml
   needs: [check, build-backend, build-frontend]
   ```

3. Move AWS auth and ECR login to build jobs

4. Deploy job only does Terraform apply

## Notes

Estimated gain: ~20-30s on total pipeline time.
