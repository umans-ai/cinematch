# TMDB API Integration

## Goal
Replace static movie list with dynamic TMDB-powered movie catalog with real posters, IMDB ratings, and trailers.

## Context
Current implementation uses a hardcoded static list of 4 movies. Users need variety and rich movie data (posters, ratings, trailers) for engaging swiping experience.

## Ship Criteria
- [ ] TMDB API client with caching
- [ ] Backend endpoints for fetching movies by region/provider
- [ ] Movie cards show: poster, title, year, IMDB rating, genre badges
- [ ] Detail modal includes: backdrop, full overview, trailer button
- [ ] "Swipe again" mode for fresh movies after exhausting current list

## UI Scenarios

Location: `docs/backlog/ui-previews/00003-tmdb-integration/`

| # | Scenario | Screenshot | Status |
|---|----------|------------|--------|
| 1 | Movie card with poster + IMDB rating badge | ⬜ | ⬜ |
| 2 | Detail modal with backdrop and trailer button | ⬜ | ⬜ |
| 3 | Loading state while fetching movies | ⬜ | ⬜ |
| 4 | Empty state - need more movies | ⬜ | ⬜ |
| 5 | Swipe again - fetch new batch | ⬜ | ⬜ |

## Implementation Plan

### Phase 1: Backend TMDB Client
- [ ] Add TMDB API key to environment config
- [ ] Create `backend/app/services/tmdb.py` client
  - `discover_movies(region, provider, page)` - fetch with filters
  - `get_movie_details(tmdb_id)` - full details + trailer
  - `get_movie_images(tmdb_id)` - poster + backdrop URLs
- [ ] Cache responses in SQLite (24h TTL)
- [ ] New endpoints:
  - `GET /api/v1/movies?region=US&page=1` - paginated movie list
  - `GET /api/v1/movies/{id}` - single movie details

### Phase 2: Frontend Movie Cards
- [ ] Update `MovieCard` component:
  - Show poster image (TMDB image CDN: `https://image.tmdb.org/t/p/w342/{poster_path}`)
  - IMDB rating badge (⭐ 8.7)
  - Year + genre badges
- [ ] Loading skeleton while images load
- [ ] Error fallback for missing poster

### Phase 3: Detail Modal Enhancement
- [ ] Backdrop image in modal header
- [ ] "Watch Trailer" button (YouTube embed)
- [ ] Full overview text (no truncation)
- [ ] Cast list (top 3 actors)

### Phase 4: Swipe Flow Updates
- [ ] Fetch ~50 movies on room creation
- [ ] Track swiped movie IDs per user
- [ ] When list exhausted: "Swipe again" button fetches new batch
- [ ] Remove hardcoded `MOVIES` constant

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

## Notes
- TMDB "watch providers" filters by streaming service including Netflix
- Need to handle images that fail to load gracefully
- Consider pagination vs infinite scroll for movie list
