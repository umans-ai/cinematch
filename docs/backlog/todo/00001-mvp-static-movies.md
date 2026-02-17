# MVP: Static Movie List with Room Matching

## Goal
A working web app where two people can join a room and swipe through a static list of movies to find a match.

## Context
See initial conversation: we want to stop spending evenings choosing movies and actually watch something. Tinder-style swipe interface.

## Ship Criteria
- [ ] Create room (generates 4-digit code)
- [ ] Join room with code
- [ ] Static list of 50 popular movies (hardcoded JSON)
- [ ] Swipe left (pass) / right (like) interface
- [ ] Real-time sync: when both in room, see each other's progress
- [ ] Match notification when both like the same movie
- [ ] Deployed at demo.cinematch.umans.ai

## Uncertainties
- [ ] Will SQLite be enough for MVP? (Yes, migrate to PostgreSQL later)
- [ ] Is WebSocket overkill? (Try Server-Sent Events first, simpler)

## Implementation Plan

### Phase 1: Backend skeleton
- [ ] FastAPI app with health endpoint
- [ ] SQLite database with SQLAlchemy
- [ ] Models: Room, Participant, Movie, Vote
- [ ] Dockerfile

### Phase 2: Frontend skeleton
- [ ] Next.js app with shadcn/ui
- [ ] Home page with "Create Room" / "Join Room"
- [ ] Dockerfile

### Phase 3: Core features
- [ ] API: Create room (POST /rooms)
- [ ] API: Join room (POST /rooms/{code}/join)
- [ ] API: Get movies (GET /rooms/{code}/movies)
- [ ] API: Submit vote (POST /rooms/{code}/vote)
- [ ] API: Get matches (GET /rooms/{code}/matches)
- [ ] UI: Room page with swipe cards
- [ ] UI: Match overlay when mutual like

### Phase 4: Real-time
- [ ] Server-Sent Events for live updates
- [ ] Show partner's swipe progress

### Phase 5: Deploy
- [ ] Terraform infrastructure (ECS, ALB, Route53)
- [ ] GitHub Actions CI/CD
- [ ] Deploy to demo.cinematch.umans.ai

## Notes
Keep it simple. No authentication. No movie API integration yet (separate increment). No persistent sessions (if you refresh, you may need to re-enter room code).
