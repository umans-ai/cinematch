# ADR 001: Integration Testing with Testcontainers

## Status
Accepted

## Context
We need to test database persistence and migrations against a real PostgreSQL database. Using SQLite for tests doesn't catch PostgreSQL-specific issues (different SQL dialects, type handling, locking behavior).

Options considered:
1. **SQLite for all tests**: Fast but doesn't test real database behavior
2. **Shared PostgreSQL instance**: Requires manual setup, causes test pollution, hard to parallelize
3. **Testcontainers**: Spins up ephemeral PostgreSQL containers per test, provides true isolation

## Decision
Use testcontainers to run ephemeral PostgreSQL containers for integration tests.

### Key Design Decisions

1. **Function-scoped containers**: Each test gets a fresh container to ensure isolation
2. **Retry logic for startup**: Containers need time to initialize; we poll until PostgreSQL accepts connections
3. **Separate conftest.py for integration tests**: Keeps integration-specific fixtures isolated
4. **given/when/then naming**: Tests read like executable documentation

## Consequences

### Positive
- True database compatibility testing
- Complete isolation between tests
- No manual database setup required
- Tests are portable (Docker required)

### Negative
- Slower test execution (container startup time ~5s per test)
- Requires Docker daemon running
- More memory usage during test runs

## Implementation

```python
# tests/integration/conftest.py
@pytest.fixture(scope="function")
def postgres_container():
    postgres = PostgresContainer("postgres:16-alpine")
    postgres.start()

    # Wait for PostgreSQL to be ready
    port = postgres.get_exposed_port(5432)
    for _ in range(10):
        try:
            conn = psycopg2.connect(host="localhost", port=port, ...)
            conn.close()
            break
        except psycopg2.OperationalError:
            time.sleep(0.5)

    yield postgres
    postgres.stop()
```

## References
- [Testcontainers Python](https://testcontainers-python.readthedocs.io/)
- [Martin Fowler: Integration Tests](https://martinfowler.com/articles/microservice-testing/)
