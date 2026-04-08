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
- [x] Movies fetched from TMDB only get providers they're actually available on
- [x] Static fallback movies use round-robin assignment (not all providers)
- [x] Provider badges on movie cards reflect real availability
- [x] Tests document and verify the correct behavior

## Implementation Plan

### Phase 1: TMDB provider extraction
- [x] Add `watch/providers` to `get_movie_details` append_to_response
- [x] Create `_extract_available_providers()` helper to parse TMDB watch/providers data
- [x] Test: TMDB details response includes watch/providers data

### Phase 2: Fix availability recording
- [x] Fix `_ensure_movies_in_pool()` to record only actual providers
- [x] Fix `_seed_static_movies()` to not blindly add all providers to existing movies
- [x] Test: movie with known providers only gets those recorded
- [x] Test: movie available on 1 of 3 room providers shows only that 1

### Phase 3: Verify end-to-end
- [x] Test: room with 5 providers → movies show varied provider counts
- [x] Test: provider badges match recorded availability

## Changes Made

### `backend/app/services/tmdb.py`
- Added `watch/providers` to `append_to_response` in `get_movie_details()` — no extra API call needed, data comes with the existing details fetch

### `backend/app/routers/movies.py`
- **New helper** `_extract_available_providers()`: parses TMDB's `watch/providers` response to get the intersection of actual flatrate providers and room providers
- **Fixed** `_ensure_movies_in_pool()`: uses `_extract_available_providers()` to record only real providers (falls back to first room provider if TMDB data unavailable)
- **Fixed** `_seed_static_movies()`: no longer adds all room providers to existing movies; instead, assigns via round-robin only for movies with no availability for the current room's providers

### `backend/tests/test_provider_availability.py` (5 new tests)
- `test_movie_only_gets_actual_providers` — Netflix-only movie doesn't get Disney+ badge
- `test_existing_movie_preserves_providers_across_rooms` — second room doesn't corrupt first room's movies
- `test_provider_badges_reflect_real_availability` — 5-provider room shows varied counts
- `test_static_movies_dont_get_all_providers` — fallback uses round-robin, not "all providers"
- `test_second_room_does_not_corrupt_existing_providers` — static fallback cross-room integrity
