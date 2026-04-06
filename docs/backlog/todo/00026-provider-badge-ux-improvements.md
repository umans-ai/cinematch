# Provider Badge UX Improvements

## Problem Statement

Three UX issues identified with provider badges and movie display:

1. **Static logo images failing**: TMDB logo URLs return 404, causing broken image icons
2. **Cannot submit name with Enter key**: Users must click "Create room" button instead of pressing Enter
3. **Movies appear sequentially by provider**: Movies seem to be grouped by provider rather than shuffled

## Steps to Reproduce

### Issue 1: Broken provider logos
1. Create a room with any providers
2. Look at movie cards
3. Provider badges show broken image icons instead of logos

### Issue 2: Enter key not working
1. Go to homepage
2. Type name in input field
3. Press Enter - nothing happens (expected: proceed to platform selection)

### Issue 3: Sequential provider display
1. Create room with multiple providers (e.g., HBO Max, Apple TV+, Hulu)
2. Swipe through movies
3. Notice movies appear to be grouped by provider rather than mixed

## Expected Behavior

1. Provider badges show reliable icons (static colored icons per platform)
2. Pressing Enter in name field proceeds to next step
3. Movies are shuffled randomly across all selected providers

## Implementation Notes

### Provider Icons
Replace external TMDB logo URLs with static colored icons:
- Netflix: Red background with "N"
- Prime Video: Blue background with "prime"
- Disney+: Dark blue background with "D+"
- HBO Max: Purple background with "HBO"
- Apple TV+: Dark background with "TV+"
- Hulu: Green background with "hulu"

### Enter Key Support
Add `onKeyDown` handler to name input field to detect Enter key and proceed.

### Movie Shuffle
Add random shuffle to movie query results before returning response.

## Acceptance Criteria

- [ ] Provider badges display correctly without broken images
- [ ] Pressing Enter on homepage submits name and proceeds
- [ ] Movies appear in random order (not grouped by provider)
- [ ] All existing tests pass

## Verification

Test with combination of providers including less common ones (HBO Max, Apple TV+, Hulu) to ensure proper mixing.
