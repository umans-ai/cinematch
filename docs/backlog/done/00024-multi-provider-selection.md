# Multi-Provider Streaming Selection

## Goal
Permettre aux utilisateurs de sélectionner plusieurs providers de streaming simultanément.

## Context
Actuellement, les utilisateurs ne peuvent choisir qu'un seul provider de streaming à la fois. Les utilisateurs veulent pouvoir sélectionner plusieurs services auxquels ils sont abonnés (ex: Netflix + Disney+ + Canal+) pour élargir le catalogue de films proposés.

## Ship Criteria
- [x] UI permettant la sélection multiple de providers
- [x] Filtrage des films disponibles sur AU MOINS un des providers sélectionnés
- [x] Persistance de la sélection dans la room/session
- [ ] Affichage visuel des providers associés à chaque film (dépriorisé)

## Implementation Plan

### Phase 1: Database Schema (TDD - Red) ✅
- [x] Write migration test for provider_ids JSON column
- [x] Create Alembic migration to add `provider_ids` JSON column to rooms
- [x] Create migration to convert existing `provider_id` → `provider_ids`
- [x] Update Room model to use `provider_ids` (List[int])
- [x] Update MovieAvailability queries to use IN operator for multiple providers

### Phase 2: Backend API (TDD - Green) ✅
- [x] Update RoomCreate schema: `provider_id: int` → `provider_ids: List[int]`
- [x] Update RoomResponse schema
- [x] Update rooms router to handle list of providers
- [x] Update TMDB service: `discover_movies()` to accept `provider_ids: List[int]`
- [x] Update movies router filtering logic (MovieAvailability.provider_id IN provider_ids)
- [x] Add provider_ids validation (min 1, max 5 providers)

### Phase 3: Frontend UI ✅
- [x] Update PlatformSelector to support multiple selection (checkbox mode)
- [x] Update page.tsx to handle `selectedProviderIds: number[]`
- [x] Update API call to send `provider_ids` array
- [x] Display selected providers count in UI
- [x] Add visual feedback for multi-selection

### Phase 4: Movie Display Enhancement (TODO - future)
- [ ] Update MovieResponse to include available_providers list
- [ ] Query MovieAvailability for each movie to get providers
- [ ] Show provider icons on movie cards
- [ ] Update swipe interface with provider badges

### Phase 5: Testing & Validation ✅
- [x] Backend tests for multi-provider rooms
- [x] Frontend tests for multi-selection UI
- [x] E2E test: create room with 2+ providers, verify movies from all providers
- [x] Test migration of existing rooms

## Technical Design

### Database Changes
```sql
-- New column for storing multiple provider IDs as JSON array
ALTER TABLE rooms ADD COLUMN provider_ids JSON DEFAULT '[8]';

-- Migrate existing data
UPDATE rooms SET provider_ids = JSON_ARRAY(provider_id) WHERE provider_ids IS NULL;

-- Optional: drop old column after migration
-- ALTER TABLE rooms DROP COLUMN provider_id;
```

### API Changes
```python
# RoomCreate schema
class RoomCreate(BaseModel):
    region: str = "US"
    provider_ids: List[int] = [8]  # Changed from provider_id: int

# TMDB discover with multiple providers
def discover_movies(
    db: Session,
    region: str = "US",
    provider_ids: List[int] | None = None,  # Changed from provider_id: int | None
    page: int = 1,
) -> dict:
    # TMDB API supports pipe-separated provider IDs
    if provider_ids:
        params["with_watch_providers"] = "|".join(str(p) for p in provider_ids)
```

### TMDB API Behavior
- Multiple providers use OR logic: `with_watch_providers=8|337` returns movies on Netflix OR Disney+
- This matches our requirement: "films disponibles sur AU MOINS un des providers"

## Test Results

### Local API Test
```bash
curl -X POST http://localhost:8000/api/v1/rooms \
  -H "Content-Type: application/json" \
  -d '{"region": "FR", "provider_ids": [8, 337, 9]}'
```
Response:
```json
{
  "id": 1,
  "code": "9005",
  "region": "FR",
  "provider_ids": [8, 337, 9]
}
```

### E2E Test (Preview)
- ✅ Room created with 3 providers (Netflix, Prime Video, Disney+)
- ✅ 50 movies returned
- ✅ UI shows "3 platforms selected"
- ✅ Checkmarks on selected providers

## Notes
- SQLite supports JSON columns natively (JSON1 extension)
- PostgreSQL has native JSON/JSONB support
- Keep backward compatibility during migration
- Security dependencies updated (aiohttp, pygments, requests)

## Deployment
- Preview: https://demo-pr-61.cinematch.umans.ai
- Production: https://demo.cinematch.umans.ai
