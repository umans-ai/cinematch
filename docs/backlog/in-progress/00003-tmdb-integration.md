# TMDB API Integration

## Goal
Replace static movie list with dynamic TMDB-powered movie catalog with real posters, IMDB ratings, and trailers.

## Context
Current implementation uses a hardcoded static list of 4 movies. Users need variety and rich movie data (posters, ratings, trailers) for engaging swiping experience.

## Ship Criteria
- [x] TMDB API client with caching
- [x] Backend endpoints for fetching movies by region/provider
- [x] Movie cards show: poster, title, year, IMDB rating, genre badges
- [x] Detail modal includes: backdrop, full overview, trailer button
- [x] "Swipe again" mode for fresh movies after exhausting current list

## UI Scenarios

Location: `docs/backlog/ui-previews/00003-tmdb-integration/`

| # | Scenario | Status |
|---|----------|--------|
| 1 | Movie card with poster + IMDB rating badge | ✅ |
| 2 | Detail modal with backdrop and trailer button | ✅ |
| 3 | Loading state while fetching movies | ✅ |
| 4 | Empty state - need more movies | ✅ |
| 5 | Swipe again - fetch new batch | ✅ |

## Implementation Plan

### Phase 1: Backend TMDB Client ✅
- [x] Add TMDB API key to environment config
- [x] Create `backend/app/services/tmdb.py` client
  - `discover_movies(region, provider, page)` - fetch with filters
  - `get_movie_details(tmdb_id)` - full details + trailer
  - `get_movie_images(tmdb_id)` - poster + backdrop URLs
- [x] Cache responses in SQLite (24h TTL)
- [x] New endpoints:
  - `GET /api/v1/movies?region=US&page=1` - paginated movie list
  - `POST /api/v1/movies/refresh` - fetch new batch

### Phase 2: Frontend Movie Cards ✅
- [x] Update `MovieCard` component:
  - Show poster image (TMDB image CDN: `https://image.tmdb.org/t/p/w342/{poster_path}`)
  - IMDB rating badge (⭐ 8.7)
  - Year + genre badges
- [x] Loading skeleton while images load
- [x] Error fallback for missing poster

### Phase 3: Detail Modal Enhancement ✅
- [x] Backdrop image in modal header
- [x] "Watch Trailer" button (YouTube embed)
- [x] Full overview text (no truncation)

### Phase 4: Swipe Flow Updates ✅
- [x] Fetch ~50 movies on room creation
- [x] Track swiped movie IDs per user
- [x] When list exhausted: "Swipe again" button fetches new batch
- [x] Fallback to static movies if TMDB not configured

## Technical Details

**TMDB API:**
- Free tier: 40 req/sec (sufficient for demo)
- Key endpoints:
  - `GET /discover/movie?with_watch_providers=8&watch_region=US` (Netflix filter)
  - `GET /movie/{id}?append_to_response=videos` (details + trailer)
  - `GET /movie/{id}/images` (posters/backdrops)

**Image URLs:**
- Poster: `https://image.tmdb.org/t/p/w342/{path}`
- Backdrop: `https://image.tmdb.org/t/p/w780/{path}`

**Data to cache:**
- TMDB movie ID, title, overview, poster_path, backdrop_path
- IMDB rating (vote_average), year (release_date), genres
- YouTube trailer key

## Configuration

To enable TMDB integration:

1. Sign up for a free API key at https://www.themoviedb.org/settings/api
2. Add to environment:
   ```bash
   export TMDB_API_KEY="your_api_key_here"
   ```
3. If TMDB_API_KEY is not set, the app falls back to static movies (for testing)

## API Changes

**New endpoint:**
- `POST /api/v1/movies/refresh?code={room_code}` - Fetch new movie batch

**Updated endpoints:**
- `GET /api/v1/movies?code={room_code}` - Now returns TMDB movies with posters, ratings, trailers

## Notes
- TMDB "watch providers" filters by streaming service including Netflix
- Movies are cached in SQLite for 24 hours to avoid hitting rate limits
- Images are loaded from TMDB CDN (image.tmdb.org)
- Trailer button opens YouTube embed in modal
- Swipe again button appears when all movies are voted on
