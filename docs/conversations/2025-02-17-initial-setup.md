# Conversation: Initial Setup of CineMatch

**Date:** 2026-02-17
**Participants:** User (Product Owner), Claude (AI Assistant)

## Context

Creation of a new project "CineMatch" - a Tinder-style movie picker for couples to quickly decide on movies. The goal is to "stop scrolling, start watching."

## Key Requirements

### Functional Requirements
- Deploy on `demo.cinematch.umans.ai`
- Create/join rooms with 4-digit codes
- Static list of 50 movies (MVP)
- Swipe left (pass) / right (like) interface
- Match notification when both like the same movie

### Technical Requirements
- **Frontend:** Next.js 14 + shadcn/ui + Tailwind
- **Backend:** FastAPI + SQLite (MVP) → PostgreSQL (increment 2)
- **Infrastructure:** AWS ECS Fargate with Terraform
- **Isolation:** COMPLETE ISOLATION from other Umans AI projects (different VPC, dedicated ECS clusters)

## Critical Decisions Made

### Architecture
1. **Foundation/Service Layer Split**
   - Foundation (00-foundation): VPC, ECR, ACM cert - applied manually ONCE
   - Service (01-service): ALB, ECS cluster, services - applied by CI/CD per environment

2. **Environment Isolation**
   - Terraform workspaces for environments (production, pr-123)
   - Dedicated ECS cluster per environment (no shared cluster)
   - Dedicated ALB per environment
   - VPC 10.1.0.0/16 (distinct from other internal ranges)

3. **Preview Environments**
   - PR → preview deployment at `demo-pr-{N}.cinematch.umans.ai`
   - Cleanup on PR close

### Repository Setup
- Public repo: `github.com/umans-ai/cinematch`
- Same workflow as other Umans AI projects (CLAUDE.md, ADRs, backlog, justfile)
- GitHub Actions with OIDC for AWS auth

## Implementation Log

### Phase 1: Project Structure
- Created backend/ with FastAPI, SQLAlchemy models (Room, Participant, Movie, Vote)
- Created frontend/ with Next.js 14, shadcn/ui
- Created operations/ with Terraform foundation and service layers
- Created docs/ with ADRs, backlog, architecture overview

### Phase 2: Infrastructure
- Applied foundation layer (VPC, ECR, ACM certificate)
- Created dedicated ECS cluster per environment
- Set up ALB with HTTPS (port 443) and HTTP→HTTPS redirect
- Configured Route53 DNS records

### Phase 3: CI/CD Fixes
Multiple iterations to fix CI/CD pipeline:
1. Added missing IAM permissions (DynamoDB, S3, IAM for ECS roles)
2. Fixed frontend Docker build (added public/ folder)
3. Fixed backend tests (added httpx, init_db before tests)
4. Fixed ruff lint errors (unused imports, type ignores)

### Phase 4: HTTPS & Production
- Added HTTPS listener to ALB
- Configured HTTP→HTTPS redirect
- Verified deployment with Playwright
- Production live at: https://demo.cinematch.umans.ai

## Key Files Created

```
backend/
  app/
    main.py           # FastAPI app with CORS
    database.py       # SQLite/SQLAlchemy setup
    models.py         # Room, Participant, Movie, Vote
    routers/
      rooms.py        # Create/join rooms
      movies.py       # Get movies, seed static list
      votes.py        # Submit votes, get matches
frontend/
  app/
    page.tsx          # Home with create/join
    room/[code]/page.tsx  # Room with swipe cards
operations/
  00-foundation/      # VPC, ECR, ACM (manual)
  01-service/         # ALB, ECS, IAM (CI/CD)
```

## Security & Isolation

### Isolation from Other Umans AI Projects
- ✅ Different VPC CIDR from other internal infrastructure
- ✅ Different ECS cluster names (cinematch-* vs other naming conventions)
- ✅ Different ALB names
- ✅ Different security group names
- ✅ Different IAM role names
- ✅ Separate ECR repositories
- ✅ Separate Route53 records (different subdomain)

### Public Repo Safety
- ✅ No hardcoded secrets in code
- ✅ AWS credentials via OIDC (no long-lived keys)
- ✅ .gitignore excludes .env, terraform state
- ✅ Secrets referenced via AWS Secrets Manager (if needed)

## Current Status

- ✅ Production deployed: https://demo.cinematch.umans.ai
- ✅ HTTPS enabled
- ✅ CI/CD pipeline green
- ✅ Backlog items need updating (move from todo → done/in-progress)

## Next Steps

1. Update backlog (mark MVP as done, move PostgreSQL to in-progress)
2. Add architecture diagrams (C4 style)
3. Document conversation history
4. Add component and sequence diagrams

## Issues Encountered & Fixed

1. **Terraform state lock** → Force-unlocked manually
2. **ECR repos already existed** → Imported into Terraform state
3. **Duplicate locals in Terraform** → Removed from logs.tf and ecs-services.tf
4. **Frontend Docker build failed** → Created public/ folder
5. **Backend SQLAlchemy error** → Added missing movie relationship to Vote model
6. **CI/CD IAM permissions** → Added DynamoDB, S3, IAM inline policies to GitHubActionsCinematchRole
7. **SQLite path in container** → Changed to sqlite:////tmp/cinematch.db (4 slashes)
