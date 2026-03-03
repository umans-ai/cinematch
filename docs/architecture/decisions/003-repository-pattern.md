# ADR 003: Repository Pattern for Data Access

## Status
Accepted

## Context
Currently, data access is mixed with business logic in FastAPI route handlers. This creates several issues:
- Business logic is hard to test without database
- Route handlers know too much about database structure
- Code duplication for common queries
- Hard to swap database implementations

## Decision
Introduce Repository pattern to abstract data access.

### Structure

```
app/
  repositories/
    __init__.py
    base.py          # Abstract base class
    room.py          # RoomRepository
    participant.py   # ParticipantRepository
    vote.py          # VoteRepository
```

### Interface Design

Repositories expose intent-revealing methods:

```python
class RoomRepository:
    def create(self) -> Room: ...
    def get_by_code(self, code: str) -> Room | None: ...
    def get_by_id(self, id: int) -> Room | None: ...
    def update(self, room: Room) -> Room: ...
```

### Testing Strategy

Tests use given/when/then pattern at repository interface:

```python
def test_given_room_saved_when_get_by_id_then_retrieved_matches_saved():
    # given
    room = Room(code="1234", is_active=True)
    repository.save(room)

    # when
    retrieved = repository.get_by_id(room.id)

    # then
    assert retrieved.code == "1234"
    assert retrieved.is_active is True
```

Integration tests verify repository behavior against real PostgreSQL.
Unit tests use in-memory fakes for business logic testing.

## Consequences

### Positive
- Clear separation between business logic and data access
- Database changes isolated to repository layer
- Easier to test business logic with fake repositories
- Repository interfaces document available data operations

### Negative
- More abstraction layers (indirection)
- Need to maintain repository + model + schema mappings

## Implementation Notes

Current increment sets up test infrastructure. Repository implementation will follow in next increment when we:
1. Create base repository class
2. Implement concrete repositories for each entity
3. Migrate route handlers to use repositories
4. Create fake repositories for unit testing

## References
- [Repository Pattern (Martin Fowler)](https://martinfowler.com/eaaCatalog/repository.html)
- [Ports and Adapters Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
