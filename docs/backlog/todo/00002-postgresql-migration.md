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
- `pytest-asyncio` - if using async SQLAlchemy
