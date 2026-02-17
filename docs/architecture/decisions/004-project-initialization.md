# ADR-004: Project Initialization from Conversation

## Status
Accepted

## Context
This project was initiated from a conversation with the product owner about solving the "Netflix and chill" problem - spending too much time choosing movies and ending up watching nothing.

## Initial Requirements (from conversation)

### The Problem
- Couples spend evenings scrolling through streaming options
- Decision paralysis leads to watching nothing
- Need a quick, fun way to find mutual movie interests

### Solution Approach
- Tinder-style swipe interface for movies
- Real-time matching when both partners like the same movie
- Simple, fast, no-frills experience

### Technical Decisions Made

1. **Name**: CineMatch
   - Short, memorable, clearly communicates purpose

2. **Domain**: demo.cinematch.umans.ai
   - Leverages existing umans.ai infrastructure
   - Wildcard SSL certificate already in place

3. **Stack**:
   - Next.js + FastAPI + SQLite (MVP)
   - PostgreSQL migration planned (increment 2)
   - Team familiarity prioritized

4. **Features Priority**:
   - MVP: Static movie list, room codes, basic swiping
   - Increment 2: PostgreSQL + migrations
   - Increment 3: TMDB API integration
   - Increment 4: User accounts

5. **Infrastructure**:
   - Same AWS account as other Umans projects
   - Terraform workspaces for preview/production
   - ECS Fargate for container orchestration
   - GitHub Actions for CI/CD

## Conversation Notes

Key insights from initial discussion:
- Speed over perfection for MVP
- Aesthetic matters but functionality first
- Anonymous rooms preferred over accounts initially
- SQLite acceptable for MVP validation

## Date
2025-02-17
