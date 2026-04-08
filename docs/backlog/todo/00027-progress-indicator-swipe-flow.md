# Progress Indicator for Movie Swiping

## Problem Statement

Users swiping through movies have no visual indication of their progress through the 50-movie list. This creates uncertainty and anxiety during the decision-making process, potentially leading users to abandon before completing their votes or finding matches.

## Context

The value proposition promises "Decision made in under 5 minutes", but without progress feedback:
- Users don't know how many movies remain
- No sense of accomplishment as they progress
- Uncertainty about whether they're "almost done" or just starting
- May cause premature abandonment before matches are found

This affects the core swipe experience, which is the primary interaction in the app.

## Expected Behavior

Display a clear, unobtrusive progress indicator showing:
- Current movie number (e.g., "12 of 50")
- Placement: Top of screen near room code or bottom near action buttons
- Updates immediately after each vote
- Persists across page refreshes (based on currentIndex state)

## Acceptance Criteria

- [ ] Progress counter displays "X of Y" format
- [ ] Updates after each like/dislike vote
- [ ] Counter reflects actual remaining movies (handles refresh scenario)
- [ ] Visual design matches minimalistic UI aesthetic
- [ ] Works on mobile and desktop viewports
- [ ] Counter disappears when user reaches "All done" state
- [ ] Existing tests pass
- [ ] New tests added for progress display logic

## Implementation Plan

### Phase 1: Frontend UI Component

**Location**: `frontend/app/room/[code]/page.tsx`

**Changes needed**:
1. Add progress display to existing movie card UI
2. Calculate progress: `${currentIndex + 1} of ${movies.length}`
3. Position near existing room info (top) or vote buttons (bottom)
4. Use existing shadcn/ui components for consistency

**Test list**:
- [ ] Displays "1 of 50" on first movie
- [ ] Updates to "2 of 50" after first vote
- [ ] Shows correct count after page refresh
- [ ] Hides when finished === true
- [ ] Handles edge case: 0 movies available

### Phase 2: Visual Design

**Considerations**:
- Match minimalistic design from issue #00008
- Use muted text color (text-muted-foreground)
- Small, unobtrusive typography
- Consider adding subtle animation on update

**Placement options**:
1. **Top placement** (recommended): Near room code, shows "Movie 12/50"
2. **Bottom placement**: Above vote buttons, integrated with controls
3. **Card placement**: Directly on movie card backdrop

### Phase 3: Enhanced Features (Optional)

Future improvements to consider:
- [ ] Progress bar visualization (horizontal bar)
- [ ] Percentage display alongside count
- [ ] Time estimate based on voting speed
- [ ] "Almost there!" message at 80% completion

## Success Metrics

- Reduced abandonment rate during swiping
- Increased completion rate (users who vote on all 50 movies)
- Lower average time to first match (due to user confidence to continue)

## Dependencies

None. Can be implemented independently.

## Estimated Effort

**Size**: Small (1-2 hours)
- Simple state display using existing variables
- No backend changes required
- Minimal testing needed

## Design Reference

Similar pattern used in:
- Tinder swipe progress
- Survey completion indicators
- Multi-step form progress

Keep it simple and unobtrusive - users should focus on movies, not the counter.
