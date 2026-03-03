# Fix Matching Bug - False Positives

## Problem Statement
When two users play and try to match, matches occur even when both users haven't liked the same movie. The matching logic seems to trigger incorrectly.

## Investigation Required
1. Reproduce the bug with two browser sessions
2. Analyze the matching logic in backend and frontend
3. Identify root cause (likely in votes.py or frontend state management)
4. Fix and verify

## Acceptance Criteria
- [ ] Bug reproduced and documented
- [ ] Root cause identified
- [ ] Fix implemented
- [ ] Fix verified with manual test
- [ ] Unit test added to prevent regression

## Test Plan
- [ ] Create room with two participants
- [ ] User A likes movie 1, User B dislikes movie 1 → NO match
- [ ] User A likes movie 2, User B likes movie 2 → MATCH
- [ ] User A dislikes movie 3, User B likes movie 3 → NO match

## Notes
Do NOT start this until setup-uv is complete - need working dev environment.
