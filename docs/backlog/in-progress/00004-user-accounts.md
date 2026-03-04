# User Accounts and History

## Goal
Persistent user sessions and swipe history via Clerk Auth.

## Context
Auth provider: **Clerk** (Google OAuth + magic links, Next.js 14 App Router support).

- Frontend: `@clerk/nextjs` SDK (ClerkProvider, useUser, useAuth hooks)
- Backend: Clerk JWT verified via JWKS (`PyJWT[crypto]`). Extracts `sub` as persistent user ID.
- DB: Nullable `clerk_user_id` on `participants` table. No separate User model.
- Backward compat: Anonymous rooms still work.

## Ship Criteria
- [x] OAuth (Google) or magic link auth
- [x] Save swipe history
- [ ] "Recommend based on past likes" (future increment)
- [x] Rejoin previous rooms

## Implementation Plan

### Phase 1 — Clerk setup & wiring ✅
- [x] `uv add PyJWT[crypto] cryptography httpx`
- [x] `backend/app/auth.py`: `get_optional_user_id(request) -> str | None`
- [x] Env var: `CLERK_JWKS_URL`
- [x] `pnpm add @clerk/nextjs`
- [x] Wrap `app/layout.tsx` with `<ClerkProvider>`
- [x] `frontend/middleware.ts` — protect `/history` route
- [x] `frontend/app/lib/api.ts` — auth-aware fetch helper

### Phase 2 — Link participants to Clerk users ✅
- [x] Alembic migration: `clerk_user_id VARCHAR(100) NULLABLE` on `participants`
- [x] `Participant` model updated
- [x] `POST /rooms/{code}/join` stores `clerk_user_id`
- [x] `ParticipantResponse` includes `clerk_user_id`
- [x] Landing page: pre-fill name from `user.fullName`, show Sign In button

### Phase 3 — History & Rejoin endpoints ✅
- [x] `backend/app/routers/users.py`: `GET /api/v1/users/me/history`, `GET /api/v1/users/me/rooms`
- [x] `frontend/app/history/page.tsx` — liked movies list
- [x] Landing page: "Your rooms" section with previous room codes

## Tests
- [x] `test_auth.py`: valid token, expired token, missing header
- [x] `test_rooms.py`: join with/without clerk_user_id
- [x] `test_users.py`: history endpoint, rooms endpoint, 401 when unauthenticated

## Env Vars Required
| Var | Description |
|-----|-------------|
| `CLERK_JWKS_URL` | e.g. `https://<clerk-domain>/.well-known/jwks.json` |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk publishable key |
| `CLERK_SECRET_KEY` | Clerk secret key |
