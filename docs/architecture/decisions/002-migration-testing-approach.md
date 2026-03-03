# ADR 002: Migration Testing Approach

## Status
Accepted

## Context
Database migrations are risky operations that can break production if not tested properly. We need a strategy to verify migrations work correctly before deployment.

Risks we need to mitigate:
- Migration fails mid-way leaving database in broken state
- Downgrade doesn't properly revert schema changes
- Data loss during migration
- Migration isn't idempotent (running twice causes errors)

## Decision
Test migrations with four key scenarios against ephemeral PostgreSQL containers.

### Test Scenarios

1. **Upgrade creates expected schema**
   ```python
   def test_upgrade_creates_all_tables():
       # given: empty database
       # when: run alembic upgrade head
       # then: all expected tables exist
   ```

2. **Downgrade removes schema**
   ```python
   def test_downgrade_removes_all_tables():
       # given: migrated database
       # when: run alembic downgrade -1
       # then: application tables removed
   ```

3. **Idempotency**
   ```python
   def test_upgrade_is_idempotent():
       # given: already migrated database
       # when: run upgrade again
       # then: no errors, state unchanged
   ```

4. **Data integrity**
   ```python
   def test_upgrade_preserves_data_integrity():
       # given: migrated database with data
       # when: query data
       # then: data is valid and accessible
   ```

### Implementation Details

- Migrations run against testcontainers PostgreSQL (not SQLite)
- `alembic_cfg` fixture overrides database URL per test
- `env.py` checks if URL already configured before using default:
  ```python
  if not config.get_main_option("sqlalchemy.url"):
      config.set_main_option("sqlalchemy.url", DATABASE_URL)
  ```

## Consequences

### Positive
- Catches migration errors before production
- Tests downgrade path (often neglected)
- Verifies idempotency for retry scenarios
- Validates data integrity constraints

### Negative
- Adds ~30s to test suite (5 migration tests × container startup)
- Requires maintenance when migrations change

## References
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Testcontainers for Database Testing](https://www.testcontainers.org/)
