# Platform & Region Selection

## Goal
Allow users to select their streaming platform and region when creating a room, so they only see movies available on their chosen platform in their region.

## Context
Currently, CineMatch shows the same movies to all users regardless of where they are or what streaming services they have. Users need to see relevant movies that are actually available to them.

## Ship Criteria
- [ ] Platform selection UI with provider logos (Netflix, Disney+, Prime Video, HBO Max, Apple TV+, Hulu)
- [ ] GPS-based region detection with manual override
- [ ] Region dropdown with major markets (US, FR, GB, DE, ES, IT, CA, AU, JP, BR)
- [ ] Store region + provider_id in room model
- [ ] Fetch movies matching selected region and platform from TMDB
- [ ] Show platform logo by each movie card indicating availability

## UI Scenarios

### Scenario 1: Landing Page with Platform Selection
When user clicks "Create room" after entering their name:
- Show platform selection grid with provider logos
- Show region dropdown with "Detect" button for GPS
- Clicking "Detect" uses browser geolocation to auto-select region

### Scenario 2: Movie Card with Platform Badge
Each movie card shows:
- Platform logo (Netflix N, Disney+ logo, etc.) indicating where it's available
- If movie is available on multiple platforms, show primary one or "Multiple"

## Technical Details

**TMDB Watch Providers API:**
- `GET /discover/movie?with_watch_providers={provider_id}&watch_region={region_code}`
- Provider IDs: Netflix=8, Prime=9, Disney+=337, HBO Max=384, Apple TV+=350, Hulu=15

**GPS Region Detection:**
- Use browser `navigator.geolocation.getCurrentPosition()`
- Fallback to rough lat/long bounds for major regions
- Endpoint: `POST /api/v1/providers/detect-region?lat={}&lng={}`

**Data Model Changes:**
```python
class Room:
    region: str  # "US", "FR", etc.
    provider_id: int  # 8 for Netflix, etc.
```

## API Changes

**New endpoints:**
- `GET /api/v1/providers` - List available streaming platforms
- `GET /api/v1/providers/regions` - List available regions
- `POST /api/v1/providers/detect-region` - GPS region detection

**Updated endpoints:**
- `POST /api/v1/rooms` - Accept `region` and `provider_id`
- `GET /api/v1/movies` - Filter by room's region and provider

## Dependencies
- Requires TMDB integration (00003) to be complete

## Notes
- TMDB "watch providers" filters by streaming service
- Movies availability varies by region due to licensing
- Consider caching provider availability per region
- Platform logos from TMDB: `https://image.tmdb.org/t/p/original/{logo_path}`
