# Fix Provider Availability Accuracy

## Goal
Movies should only display providers where they are actually available, not all providers selected for the room.

## Context
When fetching movies from TMDB's discover endpoint with multiple providers (e.g., `with_watch_providers=8|337|384`), TMDB returns movies available on **at least one** of those providers (OR logic). However, the backend records each movie as available on **all** selected providers. This causes every movie card to show all room provider badges, which is incorrect.

**Observed behavior:** Select Netflix + Disney+ + Prime + HBO + Apple TV → every movie shows all 5 provider badges.

**Expected behavior:** Each movie should only show the providers where it's actually available (e.g., "Dune" shows Netflix only).

## Root Cause
In `backend/app/routers/movies.py`, `_ensure_movies_in_pool()` iterates all `provider_ids` and records availability for each, instead of querying TMDB for the movie's actual providers.

Similarly, `_seed_static_movies()` adds all room providers to existing movies on subsequent room creations.

## Ship Criteria
- [ ] Movies fetched from TMDB only get providers they're actually available on
- [ ] Static fallback movies use round-robin assignment (not all providers)
- [ ] Provider badges on movie cards reflect real availability
- [ ] Tests document and verify the correct behavior

## Implementation Plan

### Phase 1: TMDB provider extraction
- [ ] Add `watch/providers` to `get_movie_details` append_to_response
- [ ] Create `_extract_available_providers()` helper to parse TMDB watch/providers data
- [ ] Test: TMDB details response includes watch/providers data

### Phase 2: Fix availability recording
- [ ] Fix `_ensure_movies_in_pool()` to record only actual providers
- [ ] Fix `_seed_static_movies()` to not blindly add all providers to existing movies
- [ ] Test: movie with known providers only gets those recorded
- [ ] Test: movie available on 1 of 3 room providers shows only that 1

### Phase 3: Verify end-to-end
- [ ] Test: room with 5 providers → movies show varied provider counts
- [ ] Test: provider badges match recorded availability
