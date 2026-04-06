# Movie Provider Badges

## Goal
Display streaming provider logos/names on each movie card in the swipe interface.

## Context
Increment 24 added multi-provider selection, but users cannot see which provider offers each movie. This information helps users decide if a movie is accessible to them.

## Ship Criteria
- [ ] Provider badge/icon visible on each movie card
- [ ] Display available providers for the current movie
- [ ] Design consistent with existing UI

## Implementation Plan

### Phase 1: Backend - API Enhancement ✅
- [x] Update `MovieResponse` schema to include `available_providers: List[ProviderInfo]`
- [x] Query `MovieAvailability` for each movie returned by the swipe session
- [x] Optimize with a single SQL query (JOIN or subquery) to avoid N+1
- [x] Add `provider_logo_path` and `provider_name` to the response

### Phase 2: Frontend - Movie Card Component ✅
- [x] Create `ProviderBadge` component with logo + name
- [x] Integrate into `MovieCard` (as overlay or at bottom of card)
- [x] Handle display of multiple providers (max 3 visible, "+N" if more)
- [x] Fallback if logo unavailable (initials or generic icon)

### Phase 3: Styling & Polish ✅
- [x] Consistent positioning on the card (top-right corner)
- [x] Adapted style (white background, rounded badges)
- [x] Responsive on mobile

### Phase 4: Testing ✅
- [x] Unit test for ProviderBadge component
- [x] Integration test: verify display with 1, 2, 3+ providers
- [x] Verify performance with 50 movies (no N+1 on backend)
- [x] Visual test on preview environment

## Technical Notes

### TMDB Logo URLs
TMDB provides provider logos via:
`https://image.tmdb.org/t/p/original{logo_path}`

Stored in `watch_providers` table during TMDB fetch.

### Database Query Strategy
```sql
-- Avoid N+1 with grouped query
SELECT m.*, 
       json_group_array(
         json_object('id', wp.provider_id, 'name', wp.provider_name, 'logo', wp.logo_path)
       ) as providers
FROM movies m
JOIN movie_availability ma ON m.id = ma.movie_id
JOIN watch_providers wp ON ma.provider_id = wp.provider_id
WHERE ma.room_id = ?
GROUP BY m.id
```

### UI Inspiration
- Position: top-right corner or bottom banner
- Style: small rounded badges with logo
- Limit: max 3 providers displayed

## Estimation
- Backend: 2h
- Frontend: 3h
- Testing + polish: 1h
- **Total: ~6h**
