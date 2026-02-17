# Architecture Overview

## Intent

Help couples quickly decide on a movie to watch together. Stop endless scrolling through streaming services, start actually watching.

The core insight: choosing a movie is a matching problem, not a discovery problem. Two people each have preferences — the goal is to find the intersection, not optimize for either individually.

## Responsibilities

### 1. Room-Based Matching

- Create ephemeral rooms with 4-digit codes
- Join via code (no accounts, no passwords)
- Real-time sync of partner's progress
- Match notification when both like the same movie

### 2. Movie Discovery

- Static list for MVP (50 popular movies)
- Swipe left (pass) / right (like) interface
- Show progress ("Movie 12 of 50")
- Display matches immediately

### 3. Session Management

- Browser-based sessions (cookies)
- No persistent user accounts
- Re-join room via code if disconnected

## System Context (C4 Level 1)

Shows how CineMatch enables couples to find movies they both want to watch.

```mermaid
flowchart TD
    P1["👤 Partner 1<br/><i>[Person]</i><br/>Wants to find a movie"]
    P2["👤 Partner 2<br/><i>[Person]</i><br/>Wants to find a movie"]

    subgraph CineMatch ["🎬 CineMatch"]
        CM["CineMatch App<br/><i>[System]</i><br/>Movie matching for couples"]
    end

    P1 -->|"Create room<br/>Share 4-digit code"| CM
    P2 -->|"Join room with code<br/>Start swiping"| CM
    P1 <-->|"Both swipe on movies<br/>Find mutual likes"| CM
    P2 <-->|"See match notification<br/>Start watching"| CM

    classDef person fill:#1f4e79,stroke:#0f2e4f,color:#fff,stroke-width:2px
    classDef system fill:#9b59b6,stroke:#8e44ad,color:#fff,stroke-width:3px

    class P1,P2 person
    class CM system
```

## Container Diagram (C4 Level 2)

Shows the internal structure of CineMatch.

```mermaid
flowchart TB
    P1["👤 Partner 1<br/>Browser/Mobile"]
    P2["👤 Partner 2<br/>Browser/Mobile"]

    subgraph CineMatch ["CineMatch System"]
        FE["🖥️ Frontend<br/><i>[Container: Next.js]</i><br/>Serves UI<br/>Handles swipes"]
        BE["⚡ Backend API<br/><i>[Container: FastAPI]</i><br/>Room management<br/>Vote matching"]
        DB[("🗄️ Database<br/><i>[Container: SQLite]</i><br/>Rooms, movies, votes")]
    end

    P1 -->|"HTTPS<br/>Create/join room"| FE
    P2 -->|"HTTPS<br/>Join room, swipe"| FE
    FE -->|"REST API<br/>/api/v1/*"| BE
    BE -->|"SQLAlchemy ORM"| DB

    classDef external fill:#999,stroke:#666,color:#fff,stroke-width:2px
    classDef container fill:#5b9bd5,stroke:#2e75b5,color:#fff,stroke-width:2px
    classDef db fill:#27ae60,stroke:#1e8449,color:#fff,stroke-width:2px
    classDef person fill:#1f4e79,stroke:#0f2e4f,color:#fff,stroke-width:2px

    class P1,P2 person
    class FE,BE container
    class DB db
```

### Container Responsibilities

| Container | Technology | Responsibility |
|-----------|------------|----------------|
| **Frontend** | Next.js 14 + shadcn/ui | Serves the swipe UI, handles room creation/joining, displays matches |
| **Backend API** | FastAPI + SQLAlchemy | Manages rooms, participants, movies, votes; calculates matches |
| **Database** | SQLite (MVP) | Stores rooms, movies, votes, participants |

## Component Diagram (C4 Level 3) - Backend

```mermaid
flowchart TB
    subgraph BackendAPI ["Backend API (FastAPI)"]
        subgraph Routers ["API Routers"]
            R1["🏠 rooms.py<br/>POST /api/v1/rooms<br/>POST /api/v1/rooms/{code}/join<br/>GET /api/v1/rooms/{code}"]
            R2["🎬 movies.py<br/>GET /api/v1/movies<br/>GET /api/v1/movies/unvoted"]
            R3["👍 votes.py<br/>POST /api/v1/votes<br/>GET /api/v1/votes/matches"]
        end

        subgraph Models ["SQLAlchemy Models"]
            M1["Room<br/>id, code, is_active"]
            M2["Participant<br/>id, room_id, name, session_id"]
            M3["Movie<br/>id, title, year, genre, description"]
            M4["Vote<br/>id, room_id, participant_id, movie_id, liked"]
        end

        DB[("SQLite Database")]
    end

    R1 --> M1
    R1 --> M2
    R2 --> M3
    R3 --> M4
    M1 --> DB
    M2 --> DB
    M3 --> DB
    M4 --> DB

    classDef router fill:#e67e22,stroke:#d35400,color:#fff,stroke-width:2px
    classDef model fill:#3498db,stroke:#2980b9,color:#fff,stroke-width:2px
    classDef db fill:#27ae60,stroke:#1e8449,color:#fff,stroke-width:2px

    class R1,R2,R3 router
    class M1,M2,M3,M4 model
    class DB db
```

## Execution Flow

### Creating a Room and Finding a Match

```mermaid
sequenceDiagram
    actor P1 as Partner 1
    actor P2 as Partner 2
    participant FE as Frontend
    participant BE as Backend
    participant DB as SQLite

    Note over P1,P2: Room Creation
    P1->>FE: Click "Create Room"
    FE->>BE: POST /api/v1/rooms
    BE->>DB: INSERT room (code: 1234)
    DB-->>BE: Room created
    BE-->>FE: {code: "1234"}
    FE-->>P1: Show code, redirect to room
    P1->>P2: "Join with code 1234"

    Note over P1,P2: Partner Joins
    P2->>FE: Enter name, code "1234"
    FE->>BE: POST /api/v1/rooms/1234/join
    BE->>DB: INSERT participant
    DB-->>BE: Participant created
    BE-->>FE: {name: "Partner 2"}
    FE-->>P2: Redirect to room

    Note over P1,P2: Swiping
    P1->>FE: Swipe right on "The Matrix"
    FE->>BE: POST /api/v1/votes<br/>{movie_id: 8, liked: true}
    BE->>DB: INSERT vote
    DB-->>BE: Vote recorded
    BE-->>FE: Success

    P2->>FE: Swipe right on "The Matrix"
    FE->>BE: POST /api/v1/votes<br/>{movie_id: 8, liked: true}
    BE->>DB: INSERT vote
    DB-->>BE: Vote recorded
    BE->>DB: SELECT matches (both liked)
    DB-->>BE: Match found!
    BE-->>FE: Vote response + match
    FE-->>P2: Show "It's a Match!"
    FE-->>P1: Show "It's a Match!"
```

## Infrastructure

CineMatch runs on AWS with complete isolation from other products.

### Deployment Architecture

```mermaid
flowchart TB
    subgraph AWS ["AWS Cloud (eu-west-1)"]
        DNS["Route 53<br/>demo.cinematch.umans.ai"]
        ALB["Application Load Balancer<br/>HTTPS → HTTP"]

        subgraph ECS ["ECS Fargate Cluster"]
            FE["Frontend Service<br/>Next.js Container"]
            BE["Backend Service<br/>FastAPI Container"]
        end

        ECR["ECR Repositories"]
    end

    User["👤 User"] --> DNS
    DNS --> ALB
    ALB --> FE
    ALB --> BE
    FE -.->|Internal API| BE

    ECR -.->|Pull images| FE
    ECR -.->|Pull images| BE

    classDef aws fill:#ff9900,stroke:#e68a00,color:#000,stroke-width:2px
    classDef container fill:#5b9bd5,stroke:#2e75b5,color:#fff,stroke-width:2px

    class DNS,ALB,ECS,ECR aws
    class FE,BE container
```

### Environment Isolation

| Environment | Domain | Purpose |
|-------------|--------|---------|
| `production` | demo.cinematch.umans.ai | Live site |
| `pr-N` | demo-pr-N.cinematch.umans.ai | Preview for PR #N |

Each environment is a Terraform workspace with dedicated:
- ECS cluster
- ALB
- Security groups
- IAM roles

### Isolation Guarantees

- ✅ Dedicated VPC (10.1.0.0/16) - completely isolated network
- ✅ Dedicated ECS cluster per environment
- ✅ Dedicated ALB per environment
- ✅ Resource naming: all prefixed with `cinematch-*`
- ✅ No shared resources except Route53 zone (read-only)

## Data Flow

```
User → Route53 → ALB → ECS Service → Container
```

1. DNS resolves to ALB
2. ALB routes `/api/*` to backend (port 8000), everything else to frontend (port 3000)
3. Frontend talks to backend via internal API calls
4. Backend uses SQLite (ephemeral, per-container in MVP)

## Deployment Flow

### Production (push to main)

```
1. Run checks (lint, test, typecheck)
2. Build Docker images
3. Push to ECR with SHA tag
4. terraform workspace select production
5. terraform apply -var="image_tag=<sha>"
```

### Preview (pull request)

```
1. Run checks
2. Build Docker images
3. Push to ECR with pr-N tag
4. terraform workspace new pr-N
5. terraform apply
6. Comment PR with URL
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, shadcn/ui, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy, SQLite |
| Infrastructure | AWS ECS Fargate, ALB, Route53 |
| CI/CD | GitHub Actions, Terraform Workspaces |

## Key Decisions

See ADRs in `docs/architecture/decisions/`:
- **ADR-001**: Stack choice (Next.js + FastAPI)
- **ADR-002**: Same AWS account, isolated resources
- **ADR-003**: Preview environments with Terraform workspaces
- **ADR-004**: Project initialization from conversation
- **ADR-005**: Infrastructure isolation
