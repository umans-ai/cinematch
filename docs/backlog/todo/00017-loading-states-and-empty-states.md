# Loading States and Empty States UX

## Problem Statement

Critical UX gaps when the app is waiting for data or has no content to show:

1. **No loading skeleton on room page**: When entering a room, users see only "Loading movies..." spinner - no visual structure
2. **No empty state when finished**: After swiping all movies, users see "No more movies" text without clear next steps
3. **No feedback while voting**: Button clicks feel unresponsive - no visual confirmation vote was registered
4. **No participant count indicator**: Users don't know if their partner has joined the room yet

## Expected Behavior

### Loading Skeleton (Room Page)
Instead of blank screen + spinner, show:
- Gray placeholder card with shimmer animation
- Mock buttons in their final positions
- Progress bar skeleton
- Header structure visible

### Empty State (All Movies Swiped)
Replace plain text with card showing:
- Icon (empty popcorn bucket or film reel)
- Primary message: "You've seen all the movies!"
- If matches > 0: "Check your matches above"
- If matches = 0: "No matches yet - try selecting more providers or ask for more movies"
- CTA button: "Load More Movies" (if available)

### Vote Feedback
- Brief scale animation on Like/Pass button when clicked
- Subtle haptic feedback (mobile)
- Card swipe animation (optional enhancement)

### Participant Indicator
Small badge in header showing:
- "👤 1/2 participants" (red/yellow)
- "👥 2/2 participants ready" (green)
- Updates in real-time via existing fetch logic

## Implementation Plan

### Phase 1: Loading Skeleton
- Create `<MovieCardSkeleton>` component with shimmer effect
- Replace loading spinner in `room/[code]/page.tsx`
- Match final card dimensions exactly

### Phase 2: Empty State
- Create `<EmptyState>` component with icon + message + CTA
- Conditional rendering based on `finished` state and `matches.length`
- Wire up "Load More Movies" button to existing `fetchMoreMovies()`

### Phase 3: Vote Feedback
- Add `scale-95` animation class to buttons on click
- Optional: implement card swipe animation with Framer Motion

### Phase 4: Participant Count
- Add `participants` count to room API response
- Display badge in header with color-coded status
- Fetch with existing room/matches polling

## Acceptance Criteria

- [ ] Loading skeleton displays immediately on room entry
- [ ] Empty state shows helpful message and next steps
- [ ] Buttons provide immediate visual feedback on click
- [ ] Participant count visible and updates in real-time
- [ ] No layout shift between loading → content → empty states
- [ ] All existing tests pass

## Success Metrics

- Reduced perceived loading time (skeleton vs spinner)
- Clearer call-to-action when finished swiping
- Users understand room status (waiting for partner vs ready)
- Improved perceived responsiveness

## Priority: CRITICAL

**Why this is the most important UX increment:**

1. **Reduces anxiety**: Loading states prevent "is it broken?" moments
2. **Sets expectations**: Users know what's coming before content loads
3. **Provides guidance**: Empty states tell users what to do next
4. **Increases perceived speed**: Skeleton makes app feel 2-3x faster
5. **Improves discoverability**: Users learn they can load more movies

This addresses the #1 UX issue in modern web apps: **communicating system status**. Without it, users feel lost and uncertain.
