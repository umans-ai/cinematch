# Watch Now Deep Links

## Goal
Close the match → watch loop: when two users match on a movie, one tap takes them to where they can actually start watching it. Deliver on the tagline *"Stop scrolling, start watching."*

## Context
CineMatch's value prop promises "Stop scrolling, start watching," but today the loop is open. The match modal (`frontend/app/room/[code]/page.tsx:487`) dead-ends at a single **Continue** button: it shows the matched movie's title/year/genre and `ProviderBadges` display where to watch as static text, but there is no way to start watching from CineMatch. Users must manually leave the app, open Netflix/Prime, search, and play.

The data to close most of this loop is **already fetched and discarded**. TMDB's `/movie/{id}/watch/providers` response includes a region-level `link` (a "where to watch" page for that movie + region, e.g. `https://www.themoviedb.org/movie/{tmdb_id}/watch?locale=US`). `backend/app/routers/movies.py:_extract_available_providers` reads `region_data["flatrate"]` for provider badges but throws away `region_data["link"]`. Storing it is the missing piece.

This also unlocks a success metric we currently cannot measure: **completion** (match → actually watching). Today's metrics (`docs/product/value-proposition.md`) stop at "match found."

### Honest scope note
TMDB provides a region-level `link`, **not** per-provider deep links (no `netflix.com/title/...`). The shipped CTA therefore opens TMDB's "where to watch" page, from which the user taps through to their provider. Direct per-provider deep links are an explicit Phase 2 (see Uncertainties) requiring JustWatch API or a provider-ID mapping.

## Ship Criteria
A matched movie can be opened in one tap from the match screen, using the TMDB region `link` already fetched, with graceful fallback when no link exists. The match modal no longer dead-ends at "Continue." Per-provider direct deep links (Netflix/Prime) are explicitly out of scope for this increment.

## Uncertainties (Validating assumptions)
- [ ] TMDB region `link` is present and region-correct for the top providers (8 Netflix, 9 Prime, 337 Disney+, 384 HBO, 350 Apple TV+, 15 Hulu) — verify across US / FR.
- [ ] Users accept the TMDB "where to watch" page as the "Watch now" target. If they expect a direct provider deep link, Phase 2 needs JustWatch.
- [ ] `link` is stable enough to cache on `MovieAvailability` (only changes when TMDB re-indexes the region).
- [ ] Mobile browsers correctly redirect from the TMDB watch page to the provider's app/web (deep-link vs web fallback).

## Implementation Plan

### Phase 1 — Backend: persist the TMDB region link (Red → Green → Refactor)
Test list:
- [x] `_extract_watch_link` exposes the region-level `link` from `watch/providers.results.<region>.link`
- [x] `MovieAvailability` gains a nullable `link` column; Alembic migration applies cleanly
- [x] `_record_movie_availability` stores `link` per (movie, region) when present
- [x] Re-sync updates `link` if TMDB changed it
- [x] Movies with no providers / unknown region store null `link` (no crash)
- [x] `/api/v1/movies` and the matches response include `watch_link` when present, `null` otherwise

Implemented in `backend/tests/test_watch_link.py` (5 tests). The `get_matches` refactor to
`_movie_to_response` also fixed a latent bug: matched movies now carry `available_providers`
(previously always empty in the matches response).

### Phase 2 — Frontend: match modal "Where to watch" CTA (Red → Green → Refactor)
Test list:
- [x] Match modal renders a primary "Where to watch" CTA when `watch_link` is present
- [x] CTA opens `watch_link` in a new tab (`target="_blank"`, `rel="noopener noreferrer"`)
- [x] No CTA rendered when `watch_link` is null (graceful fallback, modal still usable)
- [x] CTA is the most prominent action (above "Continue")
- [x] `ProviderBadges` remain visible alongside the CTA
- [x] Finished screen's match list also offers the CTA per matched movie

Implemented in `frontend/app/room/[code]/__tests__/watch-link-cta.test.tsx`.

### Phase 3 — Completion signal — DEFERRED (out of scope for this increment)
Marked "optional in this increment"; deferred by decision to keep this increment focused and
shippable. Will be a separate backlog item.
- [ ] `POST /api/v1/votes/matches/{movie_id}/watched` records a tap event (no auth needed, session-scoped)
- [ ] Event only recorded once per (participant, movie)
- [ ] New metric surfaced: match → watch tap rate (instrument only, do not optimize)

## UI Scenarios

Location: `docs/backlog/ui-previews/00028-watch-now-deep-links/`

| # | Scenario | Screenshot | Status |
|---|----------|------------|--------|
| 1 | Match modal with "Where to watch" CTA (link present) | 01-match-modal-with-watch-cta.png | ⬜ |
| 2 | Match modal with no providers (no CTA, graceful) | ⬜ | ⬜ |
| 3 | CTA tap opens TMDB where-to-watch page (mobile) | ⬜ | ⬜ |

> The shipped CTA label is **"Where to watch"** (Phase 1). The sketch's "Watch on Netflix" reflects the Phase 2 vision (direct provider deep links via JustWatch).

## Notes
- **Sketch**: `docs/backlog/ui-previews/00028-watch-now-deep-links/01-match-modal-with-watch-cta.png` — aspirational vision; Phase 1 uses the TMDB region `link`, not a per-provider deep link.
- **Dependencies**: TMDB integration (00003, done), Platform/Region selection (00012, done).
- **Complements**: recommendation algorithm (00013, todo) — better ordering + closed loop = higher completion.
- **Metric unlock**: first feature that lets us measure true completion (match → watch), not just match rate.
- **Out of scope**: per-provider direct deep links (Netflix/Prime) — requires JustWatch API or a provider-ID mapping. Separate increment if Phase 1 validation shows users need it.
