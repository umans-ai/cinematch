# Migrate from SQLite to PostgreSQL

## Goal
Move from SQLite to PostgreSQL for production reliability and concurrent access.

## Context
MVP uses SQLite for speed. This increment adds proper database.

## Ship Criteria
- [ ] PostgreSQL RDS instance (or Supabase)
- [ ] Database migrations system (Alembic)
- [ ] Seamless data migration (export/import if needed)
- [ ] Works in preview environments too
- [ ] All migrations tested (up/down, rollback scenarios)
- [ ] Repository layer has persistence integration tests (testcontainers)
- [ ] Tests follow given/when/then pattern, readable as executable docs

## Uncertainties
- [ ] RDS or Supabase? (RDS for same-account consistency)
- [ ] Connection pooling needed? (Start simple, add PgBouncer if issues)

## Implementation Plan

### Infrastructure
- [ ] Add PostgreSQL to Terraform
- [ ] Set up Alembic for migrations
- [ ] Update SQLAlchemy connection string

### Testing Strategy (see ADR)
- [ ] Add testcontainers for PostgreSQL integration tests
- [ ] Create `tests/integration/` directory with dedicated `conftest.py`
- [ ] Design persistence integration tests: given/when/then style at repository interface level
- [ ] Test migrations (up/down, idempotency, data integrity)

### Documentation
- [ ] ADR: Repository pattern for data access
- [ ] ADR: Integration testing strategy with testcontainers
- [ ] ADR: Migration testing approach

## References
- Testing strategy: https://martinfowler.com/articles/microservice-testing/ (integration tests pattern)

## Notes
Blocker for scale, but not for MVP validation.

### Testing Philosophy
- **Integration tests** go in `tests/integration/` with their own `conftest.py`
- **Testcontainers** spins up real PostgreSQL for true integration testing
- **Repository pattern**: test through public interfaces only (add → get → assert equality)
- **Goal**: tests reveal intent, remain maintainable, read like executable documentation
- **Migration tests**: verify schema changes don't break data, rollbacks work, idempotency holds

### Directory Structure
```
tests/
  unit/              # Fast, isolated business logic tests
  integration/       # Requires testcontainers PostgreSQL
    conftest.py      # Shared fixtures (db container, session, repos)
    test_persistence/
      test_user_repo.py    # given: user_saved when: get_by_id then: retrieved_matches
      test_vote_repo.py
    test_migrations/
      test_001_initial.py
```

### Key Dependencies
- `testcontainers[postgres]` - ephemeral PostgreSQL in tests
- `alembic` - migration management
- `psycopg2-binary` - PostgreSQL driver

## Test List (TDD)

### Phase 1: Dependencies & Infrastructure ✅
- [x] testcontainers starts PostgreSQL container successfully
- [x] Alembic initializes with proper env.py configuration
- [x] Database connection works with PostgreSQL engine

### Phase 2: Repository Pattern ✅
- [x] RoomRepository.create returns room with generated code
- [x] RoomRepository.get_by_code returns saved room
- [x] RoomRepository.get_by_code returns None when not found
- [x] ParticipantRepository.add_to_room links participant to room
- [x] VoteRepository.record_vote stores vote correctly
- [x] VoteRepository.get_votes_for_room returns all room votes

### Phase 3: Migration Tests ✅
- [x] Migration upgrade_001 creates tables matching models
- [x] Migration downgrade_001 drops all tables
- [x] Upgrade then downgrade is idempotent
- [x] Migration with seed data preserves data integrity

### Phase 4: Integration ✅
- [x] Full flow: create room → join → vote → retrieve votes

## Implementation Progress

### Completed
- [x] Dependencies: psycopg2-binary, alembic, testcontainers[postgres]
- [x] Alembic configuration with env.py supporting test overrides
- [x] Initial migration (cdc82f99bace) with Room, Participant, Vote, Movie tables
- [x] Integration test structure: tests/integration/ with conftest.py
- [x] testcontainers-based PostgreSQL fixtures with retry logic
- [x] Persistence tests: given/when/then pattern for Room entity
- [x] Migration tests: upgrade/downgrade/idempotency/data integrity

## Infrastructure Restructuring Plan

### Problem
Current structure has VPC in `00-foundation` (shared), but VPC should be per-environment for:
- True reproducibility (preview = exact prod replica)
- Complete isolation between environments
- No convergence between envs

### Migration Strategy

#### Phase 1: Dual-Path (This PR)
Create VPC per-environment in `01-service` for NEW environments only.
Keep existing prod on current VPC to avoid risky migration.

```
01-service/vpc.tf       # NEW: per-env VPC (previews use this)
01-service/rds.tf       # NEW: PostgreSQL in per-env VPC
operations/00-foundation/vpc.tf  # KEEP: existing prod VPC
```

#### Phase 2: Foundation Cleanup (Future)
When ready to migrate prod:
1. Create new prod VPC in 01-service
2. Create RDS in new prod VPC
3. Migrate data (pg_dump/pg_restore)
4. Switch DNS to new ALB
5. Destroy old foundation VPC

#### Phase 3: Foundation Re-definition
00-foundation keeps only truly shared resources:
- ECR repositories
- Route53 zone
- ACM certificate (wildcard)

### Decision
**Preview environments** use new per-env VPC in 01-service.
**Production** stays on existing VPC until manual migration planned.

### Why This Approach
1. **No downtime risk** for existing prod
2. **Previews immediately benefit** from proper isolation
3. **Production migration** is a conscious, planned operation
4. **Incremental delivery** - we unblock PostgreSQL without blocking on prod migration

See ADR 004 for full rationale.
