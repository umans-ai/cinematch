# ADR-007: Trunk-Based Development

## Status
Proposed

## Context
Currently, the project uses a feature branch workflow where contributors work on branches and merge to `main` via pull requests. While this approach works, we want to optimize for:

1. **Faster integration** - Reduce the time code spends in isolation
2. **Continuous deployment readiness** - Every commit on `main` should be deployable
3. **Reduced merge conflicts** - Smaller, more frequent integrations
4. **Better collaboration** - Team sees changes faster, easier to coordinate

The project already has strong foundations for trunk-based development:
- Comprehensive test suite (29 tests with integration coverage)
- CI/CD pipeline with automated checks
- Preview environments for validation
- `just check` enforces quality before commits

## Decision

We adopt **Trunk-Based Development** with the following principles:

### Core Practices

1. **Short-lived feature branches** (max 1-2 days)
   - Work on small, incremental changes
   - Merge to `main` multiple times per day when possible
   - Delete branches immediately after merge

2. **Main is always deployable**
   - All commits pass `just check`
   - CI pipeline validates every commit
   - Production deploys directly from `main`

3. **Feature flags for incomplete features**
   - Use environment variables or feature flags for work-in-progress
   - Ship code that's not yet user-facing
   - Enable features when ready, not when code merges

4. **Pull requests remain, but are smaller**
   - PRs are for code review, not long-term isolation
   - Review and merge within hours, not days
   - Each PR should be independently valuable

### Workflow Changes

**Before (Current):**
```bash
# Feature branch lives for days/weeks
git checkout -b feature-big-thing
# ... days of work ...
# ... multiple commits ...
git push origin feature-big-thing
# PR sits waiting for review
```

**After (Trunk-Based):**
```bash
# Break work into small increments
git checkout -b add-movie-api-endpoint
# ... 1-2 hours of work ...
just check
git push origin add-movie-api-endpoint
# PR created, reviewed, merged same day

git checkout main && git pull
git checkout -b add-movie-api-tests
# ... next increment ...
```

### Protection Mechanisms

1. **`just check` is mandatory** - No commits bypass checks
2. **Feature flags** - For incomplete user-facing features
3. **Preview environments** - Validate changes before production
4. **Automated rollback** - Quick revert if issues detected

### Contributor vs Admin Workflow

The backlog workflow remains the same:
- **Admins**: Can push backlog state changes to `main` directly
- **Contributors**: Everything (including backlog) via PR on their branch

Both follow trunk-based principles: small PRs, quick merges, frequent integration.

## Alternatives Considered

### 1. Long-lived feature branches (status quo)
**Rejected because:**
- Increases merge conflict risk
- Delays feedback and integration issues
- Code review becomes overwhelming
- Slows down delivery

### 2. Direct commits to main (no PRs)
**Rejected because:**
- Loses code review benefits
- Higher risk for contributors
- No preview environment validation

### 3. Gitflow (develop branch)
**Rejected because:**
- Adds unnecessary complexity
- Delays integration even more
- Not suited for continuous deployment

## Consequences

### Positive
- ✅ Faster feedback loops
- ✅ Reduced merge conflicts
- ✅ More deployable commits
- ✅ Better team coordination
- ✅ Easier to track progress (smaller PRs)
- ✅ Forces breaking work into valuable increments

### Negative
- ⚠️ Requires discipline to keep changes small
- ⚠️ May need feature flags for larger features
- ⚠️ Team must adapt to faster review cycles

### Neutral
- The backlog workflow (todo/in-progress/done) is unchanged
- CI/CD pipeline already supports this model
- Preview environments remain the validation gate

## Implementation Plan

### Phase 1: Documentation (This ADR)
- [x] Document trunk-based principles
- [ ] Update CLAUDE.md with workflow examples
- [ ] Add feature flag guidelines

### Phase 2: Tooling
- [ ] Add feature flag system (simple env vars for MVP)
- [ ] Document "how to break down work" guide
- [ ] Update PR template to encourage small changes

### Phase 3: Team Adoption
- [ ] Team workshop on trunk-based development
- [ ] Monitor PR size and merge frequency
- [ ] Celebrate quick merges, flag long-lived branches

## References
- [Trunk-Based Development](https://trunkbaseddevelopment.com/)
- [Google's Engineering Practices](https://google.github.io/eng-practices/)
- [Feature Flags for Trunk-Based Development](https://www.split.io/blog/trunk-based-development-feature-flags/)

## Date
2026-03-04
