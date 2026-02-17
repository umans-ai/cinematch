# ADR-001: Stack Choice - Next.js + FastAPI + PostgreSQL

## Status
Accepted

## Context
We need to build a web app for couples to quickly decide on a movie to watch. The team is comfortable with Next.js and Python, and wants the simplest stack possible.

## Decision

### Frontend: Next.js 14+ (App Router)
- **Why**: Team familiarity, SSR for SEO, easy deployment to Vercel/ECS
- **UI**: Tailwind CSS + shadcn/ui for rapid, beautiful UI

### Backend: FastAPI (Python)
- **Why**: Team knows Python, FastAPI is simple and fast, great for WebSocket support (real-time matching)
- **Alternative considered**: Next.js API routes only - rejected because we want clean separation and may need WebSockets

### Database: PostgreSQL
- **Why**: Reliable, team knows it, good JSON support for flexibility
- **Hosting**: RDS (same AWS account as other projects)

### Real-time: WebSocket (native)
- For live swipe updates between partners in the same room

## Consequences
- Two services to deploy (frontend + backend)
- Need to handle CORS
- WebSocket support requires sticky sessions or external Redis (deferred to later increment)

## Date
2025-02-17
