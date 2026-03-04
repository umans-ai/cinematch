# Fix Room Session and Match Notification Bugs

## Goal
Fix two critical bugs affecting core user experience:
1. Users cannot join multiple rooms (session constraint issue)
2. Match modal doesn't appear when both participants like the same movie

## Context
During E2E testing, two serious bugs were discovered:

### Bug 1: Room Session Constraint
**Symptom**: "Invalid room code or room is full" error when trying to join a room, even with only 1 participant.

**Root Cause**: The `participants.session_id` column has a global UNIQUE constraint. When a user with an existing session tries to join a new room, the database rejects it because their session_id already exists in another room's participant record.

**Impact**: Users cannot participate in multiple movie sessions without clearing cookies or using incognito mode.

### Bug 2: Missing Match Notification
**Symptom**: When both participants like the same movie, no match modal appears. Users only see the match count update in the header.

**Root Cause**: The frontend fetches matches after each vote (`fetchMatches()`), but the `showMatch` state is never automatically set when a new match is detected. The modal only exists in the JSX but isn't triggered.

**Impact**: Users miss the celebratory "It's a match!" moment and may not notice they found a match until finishing all movies.

## Ship Criteria
- [ ] User can join multiple different rooms with the same browser session
- [ ] Second participant can successfully join an existing room with 1 user
- [ ] Match modal automatically appears when backend returns a new match
- [ ] Both participants see the match modal (or at least the current voter)
- [ ] Match state is consistent between both participants
- [ ] E2E tests pass demonstrating both fixes

## Technical Details

### Bug 1 Fix: Database Schema Change
**File**: `backend/app/models.py`

Change:
```python
session_id = Column(String(100), unique=True)  # Current (BROKEN)
```

To:
```python
session_id = Column(String(100))  # Fixed - unique constraint removed
```

**Migration Required**: Yes, need to drop the unique index on session_id.

**Alternative**: Keep uniqueness per room only:
```python
session_id = Column(String(100))
__table_args__ = (UniqueConstraint('room_id', 'session_id'),)
```

### Bug 2 Fix: Frontend State Management
**File**: `frontend/app/room/[code]/page.tsx`

Current logic:
```typescript
const [showMatch, setShowMatch] = useState<Match | null>(null);

const fetchMatches = useCallback(async () => {
  const response = await fetch(`/api/v1/votes/matches?code=${code}`);
  const data = await response.json();
  setMatches(data);  // Only updates count, not modal
}, [code]);
```

Fixed logic:
```typescript
const [showMatch, setShowMatch] = useState<Match | null>(null);
const [previousMatches, setPreviousMatches] = useState<Match[]>([]);

const fetchMatches = useCallback(async () => {
  const response = await fetch(`/api/v1/votes/matches?code=${code}`);
  const data = await response.json();
  setMatches(data);

  // Check for new matches
  const newMatches = data.filter((m: Match) =>
    !previousMatches.some(pm => pm.movie.id === m.movie.id)
  );

  if (newMatches.length > 0) {
    setShowMatch(newMatches[0]);  // Show first new match
  }
  setPreviousMatches(data);
}, [code, previousMatches]);
```

## Implementation Plan

### Phase 1: Fix Room Session (Backend)
1. Update `Participant` model to remove global UNIQUE constraint
2. Add composite unique constraint on `(room_id, session_id)` if needed
3. Create database migration
4. Run backend tests to verify

### Phase 2: Fix Match Notification (Frontend)
1. Update `fetchMatches` to track previous match state
2. Detect new matches by comparing with previous
3. Auto-trigger `setShowMatch()` when new match detected
4. Run frontend tests to verify

### Phase 3: E2E Verification
1. Run agent-browser E2E test
2. Verify two users can join same room
3. Verify match modal appears for both
4. Verify user can join multiple rooms

## Test Files
- `backend/tests/test_room_participation.py` - Tests for room joining
- `backend/tests/test_multi_room_session.py` - Tests for multi-room
- `backend/tests/test_match_notification.py` - Tests for match detection
- `frontend/app/__tests__/match-notification.test.tsx` - Frontend tests

## Notes
- Both bugs have failing tests on branch `test/room-session-and-match-detection`
- Database migration needed for Bug 1
- No API changes needed for Bug 2 (pure frontend fix)
- Consider adding polling or WebSocket for real-time match updates in future
