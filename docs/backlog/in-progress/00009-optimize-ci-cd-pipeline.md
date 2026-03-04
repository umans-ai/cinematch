# Optimize CI/CD Pipeline: pnpm + BuildKit Cache

## Problem

The frontend build is the bottleneck of our CI/CD pipeline:
- Frontend build: **~1m24s** (full rebuild every run)
- Backend build: **~20s** (efficient layer caching)

The frontend uses `npm ci` and builds from scratch without cache between CI runs.

## Motivation

### Fast, Reliable Feedback
Every PR waits ~4 minutes for preview deployment. Faster builds mean:
- Developers stay in flow (no context switching while waiting)
- Quicker iteration cycles
- Earlier detection of issues

### Effective Development
Slow pipelines discourage small commits and frequent pushes. Fast builds encourage:
- Small, focused PRs
- Continuous integration
- Rapid experimentation

## Proposed Solution

### 1. Migrate npm to pnpm
**Why pnpm?**
- Shared content-addressable store (hardlinks, no file duplication)
- More aggressive parallel installation
- Faster lockfile parsing (`pnpm-lock.yaml` vs `package-lock.json`)
- Drop-in replacement for npm

### 2. Docker BuildKit with GitHub Actions Cache
**Why BuildKit + GHA cache?**
- Native GitHub Actions cache (`type=gha`) for Docker layers
- Reuses `node_modules` and Next.js build between runs
- Estimated gain: **~60-70 seconds** on frontend builds

### 3. Optimized `.dockerignore`
**Why?**
- Smaller build context sent to Docker daemon
- Faster COPY operations in Dockerfile
- Prevents unnecessary cache invalidation

## Implementation

### Required Changes

1. **CI/CD Workflow** (`.github/workflows/ci-cd.yml`)
   - Add `docker/setup-buildx-action@v3`
   - Replace docker CLI commands with `docker/build-push-action@v5`
   - Configure `cache-from: type=gha` and `cache-to: type=gha,mode=max`
   - Use `pnpm/action-setup` for pnpm in check job

2. **Frontend Dockerfile**
   - Enable pnpm via corepack
   - Use `pnpm install --frozen-lockfile`

3. **New/Modified Files**
   - Update `frontend/.dockerignore`
   - Remove `frontend/package-lock.json`
   - Add `frontend/pnpm-lock.yaml`

## Acceptance Criteria

- [ ] Full CI/CD pipeline completes in under 2m30s (vs 4m+ currently)
- [ ] Frontend build under 30s with warm cache
- [ ] Frontend build under 60s with cold cache
- [ ] Preview deployments remain reliable
- [ ] No regression on backend builds

## Estimation

- **Complexity**: Medium
- **Risk**: Low (isolated CI/CD changes)
- **Estimated Time**: 2-3 hours
