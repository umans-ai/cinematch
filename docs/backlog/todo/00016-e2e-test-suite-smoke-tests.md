# E2E Test Suite & Smoke Tests

## Goal
Implement a focused E2E testing strategy following the test pyramid: fast unit tests at the base, minimal but critical E2E tests at the top.

## Context
Current test situation:
- **Unit tests**: ✅ Good coverage (backend + frontend)
- **Integration tests**: ✅ Strong (TestClient with SQLite/PostgreSQL)
- **E2E tests**: ❌ Weak - Playwright installed but underutilized
- **Smoke tests**: ❌ None - No post-deployment validation

The risk: Without E2E tests, we discover integration issues (like the psycopg driver bug) only in production.

## Ship Criteria
- [ ] One complete "happy path" E2E test (< 30s execution)
- [ ] Smoke test script for post-deployment validation
- [ ] CI pipeline runs E2E tests on PR (not blocking merge)
- [ ] Production smoke test runs after each deployment

## Scope (Intentionally Limited)

### E2E Test Coverage (1 scenario only)
**Alice & Bob Journey**:
1. Alice creates a room
2. Bob joins the room
3. Both swipe and find a match
4. Verify match appears for both

**NOT in scope**: Error cases, edge cases, all UI variations (covered by unit tests)

### Smoke Test Coverage
Quick validation (< 10s):
- Health endpoint responds
- Can create room
- Can join room
- Basic API contract respected

## Technical Approach

### Tools
- **E2E**: Playwright (already in project)
- **Smoke**: Simple curl/bash script
- **Runner**: GitHub Actions (parallel to existing CI)

### Test Isolation
Each E2E test gets:
- Fresh room (unique code)
- Isolated browser contexts
- Cleanup after test

### Performance Target
- E2E test: < 30 seconds
- Smoke test: < 10 seconds

## Implementation Plan

### Phase 1: E2E Infrastructure
- [ ] Configure Playwright for CI environment
- [ ] Create test data factories (rooms, movies)
- [ ] Setup test database reset between runs

### Phase 2: Happy Path Test
- [ ] Write "Alice & Bob find a match" test
- [ ] Handle async operations (match detection)
- [ ] Add assertions for UI state changes

### Phase 3: Smoke Tests
- [ ] Create `scripts/smoke-test.sh`
- [ ] Add to CI/CD pipeline (post-deploy)
- [ ] Slack/email notification on failure

### Phase 4: CI Integration
- [ ] Run E2E tests on PRs (non-blocking)
- [ ] Run smoke tests on staging/production
- [ ] Dashboard/reporting for test results

## Files to Create
- `frontend/e2e/happy-path.spec.ts` - Main E2E test
- `scripts/smoke-test.sh` - Production smoke test
- `.github/workflows/e2e.yml` - E2E CI pipeline
- `docs/testing/e2e-guide.md` - Documentation

## Success Metrics
- E2E test runs in < 30s
- Smoke test runs in < 10s
- False positive rate < 5%
- Developer can run E2E locally in one command

## Related
- Current tests: `backend/tests/`, `frontend/app/__tests__/`
- Playwright config: `frontend/playwright.config.ts`
