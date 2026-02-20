# MVP: Static Movie List with Room Matching

## Goal
A working web app where two people can join a room and swipe through a static list of movies to find a match.

## Context
See initial conversation: we want to stop spending evenings choosing movies and actually watch something. Tinder-style swipe interface.

## Ship Criteria
- [x] Create room (generates 4-digit code)
- [x] Join room with code
- [x] Static list of 50 popular movies (hardcoded JSON)
- [x] Swipe left (pass) / right (like) interface
- [ ] Real-time sync: when both in room, see each other's progress (deferred to later increment)
- [x] Match notification when both like the same movie
- [x] Deployed at demo.cinematch.umans.ai

## Uncertainties
- [x] Will SQLite be enough for MVP? (Yes, works perfectly, migrate to PostgreSQL in increment 2)
- [x] Is WebSocket overkill? (Not implemented in MVP, simple polling works)

## Implementation Plan

### Phase 1: Backend skeleton ✅
- [x] FastAPI app with health endpoint
- [x] SQLite database with SQLAlchemy
- [x] Models: Room, Participant, Movie, Vote
- [x] Dockerfile

### Phase 2: Frontend skeleton ✅
- [x] Next.js app with shadcn/ui
- [x] Home page with "Create Room" / "Join Room"
- [x] Dockerfile

### Phase 3: Core features ✅
- [x] API: Create room (POST /api/v1/rooms)
- [x] API: Join room (POST /api/v1/rooms/{code}/join)
- [x] API: Get movies (GET /api/v1/movies?code={code})
- [x] API: Submit vote (POST /api/v1/votes)
- [x] API: Get matches (GET /api/v1/votes/matches)
- [x] UI: Room page with swipe cards
- [x] UI: Match overlay when mutual like

### Phase 4: Real-time (deferred)
- [ ] Server-Sent Events for live updates
- [ ] Show partner's swipe progress

### Phase 5: Deploy ✅
- [x] Terraform infrastructure (VPC, ECS, ALB, Route53)
- [x] GitHub Actions CI/CD
- [x] Deploy to demo.cinematch.umans.ai
- [x] HTTPS enabled with ACM certificate

## Completion Notes

**Completed:** 2026-02-17
**Deployed URL:** https://demo.cinematch.umans.ai

### What's Working
- Room creation with 4-digit codes
- Join rooms by code
- 50 static movies (classic/popular titles)
- Swipe interface (buttons for pass/like)
- Match detection when both partners like same movie
- HTTPS/SSL termination
- CI/CD pipeline green

### Technical Stack Used
- **Frontend:** Next.js 14 + shadcn/ui + Tailwind CSS
- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Infrastructure:** AWS ECS Fargate + ALB + Route53
- **CI/CD:** GitHub Actions + Terraform Workspaces

### Architecture Decisions Implemented
- Dedicated VPC (10.1.0.0/16) - complete isolation from other Umans AI projects
- Dedicated ECS cluster per environment (production, pr-N)
- Terraform workspaces for environment isolation
- Foundation/Service layer split (foundation applied manually, service by CI/CD)

### Deferred to Future Increments
- Real-time updates (WebSocket/SSE)
- PostgreSQL migration
- TMDB API integration
- User accounts/persistence

## Notes
Keep it simple. No authentication. No movie API integration yet (separate increment). No persistent sessions (if you refresh, you may need to re-enter room code).
