# CineMatch

Swipe-based movie picker for couples. Stop scrolling, start watching.

## What it does

Two people join a room, swipe through movies, and find what they both want to watch. No more endless "what should we watch?" debates.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/umans-ai/cinematch.git
cd cinematch

# Start backend (terminal 1)
cd backend && just dev

# Start frontend (terminal 2)
cd frontend && just dev

# Or use docker-compose
docker-compose up
```

Open http://localhost:3000

## Usage

1. **Create a room** - Click "Create Room", get a 4-digit code
2. **Share the code** - Send it to your partner
3. **Both swipe** - Like or pass on movies
4. **Find a match** - Get notified when you both like the same movie

## Documentation

| Document | Purpose |
|----------|---------|
| [CLAUDE.md](CLAUDE.md) | Project conventions, workflows, and CLI guide |
| [docs/architecture/overview.md](docs/architecture/overview.md) | System architecture and C4 diagrams |
| [docs/SECURITY.md](docs/SECURITY.md) | Security analysis and isolation guarantees |
| [docs/backlog/](docs/backlog/) | Increment tracking (todo/in-progress/done) |
| [docs/architecture/decisions/](docs/architecture/decisions/) | Architecture Decision Records (ADRs) |

## Deployment

| Environment | URL | Trigger |
|-------------|-----|---------|
| Production | https://demo.cinematch.umans.ai | Push to `main` |
| Preview | https://demo-pr-{N}.cinematch.umans.ai | Pull Request #N |

## Project Structure

```
.
├── backend/           # FastAPI + SQLite
│   ├── app/          # Routes, models, database
│   └── tests/        # pytest suite
├── frontend/          # Next.js 14 + shadcn/ui
│   └── app/          # App router pages
├── operations/        # Terraform infrastructure
│   ├── 00-foundation/   # VPC, ECR, cert (manual)
│   └── 01-service/      # ECS, ALB per env (CI/CD)
└── docs/              # Documentation and backlog
```

## Key Technologies

- **Frontend**: Next.js 14, shadcn/ui, Tailwind CSS
- **Backend**: FastAPI, SQLAlchemy, SQLite (MVP)
- **Infrastructure**: AWS ECS Fargate, ALB, Route53
- **CI/CD**: GitHub Actions, Terraform Workspaces

## Contributing

This is a public repository. See [docs/SECURITY.md](docs/SECURITY.md) for isolation and security details.

### Skills Available

This repo includes Claude Code skills in `.claude/skills/`:

| Skill | Usage |
|-------|-------|
| `/backlog` | Create, start, complete backlog items |
| `/commit` | Generate conventional commits |
| `/tdd-check` | TDD cycle helper (test list → red → green → refactor) |
| `/check` | Run pre-commit checks |
| `/pr-merge` | Merge PRs with rebase workflow |

## License

MIT
