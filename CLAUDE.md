# CineMatch

Swipe-based movie picker for couples. Stop scrolling, start watching.

## Rules

- Never add `Co-Authored-By` to commit messages
- Keep `CLAUDE.md` and `docs/` in sync
- Each commit is a release candidate - keep main deployable
- SQLite for MVP, PostgreSQL comes in increment 2

## Operational CLI Defaults

- Assume `gh` and `aws` CLIs are available by default
- Use `gh` first for PR/CI checks, logs, and merges
- Use `aws` first for infra/runtime checks
- Do not ask if these CLIs can be used; run them directly
- If auth fails, run `gh auth status` or `aws sts get-caller-identity`

## Commit Messages

Conventional commits with emoji at the end:

```
<type>: <description> <emoji>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`

Emojis:
- feat: ✨
- fix: 🐛
- docs: 📝
- style: 💄
- refactor: ♻️
- perf: ⚡
- test: ✅
- build: 📦
- ci: 🔧
- chore: 🧹

## Backlog Workflow

Backlog lives in `docs/backlog/` with three states:

```
todo/         → items to do (XXXXX-name.md)
in-progress/  → currently being worked on
done/         → completed
```

The 5-digit number is a **stable ID**, not priority.

### Starting work

1. Create file in `todo/`: `XXXXX-name.md`
2. Commit to main: `chore: add <name> 📋`
3. Push main immediately: `git push origin main`
4. Verify `origin/main` includes that commit
5. Move item from `todo/` to `in-progress/`
6. Commit to main: `chore: start <name> 🚀`
7. Push main immediately: `git push origin main`
8. Verify `origin/main` includes that commit
9. Create feature branch: `git checkout -b <name>`

### Completing work

1. Move item from `in-progress/` to `done/`
2. Commit on branch
3. Merge to main:
   - **Direct push** (docs, chores, single-file fixes): `git merge --ff-only <branch>`
   - **PR required** (infra, features, complex refactors): create PR, merge with **rebase**

For PR-required changes, always rebase and verify before merge:
1. `git fetch origin`
2. `git rebase origin/main`
3. Re-run checks/preview verification on rebased head
4. Merge with `gh pr merge --rebase`

### Adding backlog items

Each increment must be:
- **Shippable** - can be deployed independently
- **Valuable** - delivers user or business value
- **Testable** - has clear verification criteria
- **Simple** - small enough to complete in one branch
- **Validating** - has explicit assumptions to confirm

Use next available 5-digit ID: `XXXXX-name.md`

## Architecture Decision Records

ADRs live in `docs/architecture/decisions/` with sequential numbering: `NNN-title.md`

Create an ADR when making decisions that:
- Affect system structure
- Constrain future choices
- Are non-obvious or debated

Commit ADRs alongside implementation, not separately.

## Development Workflow

### Plan Before Code

The increment file in `docs/backlog/in-progress/` is the planning document. Before coding:

1. **If no plan exists** - Research and add an "Implementation Plan" section with phases and test lists
2. **If plan exists** - Review the test list for the current phase
3. **Resolve uncertainties** - Web search, read existing code, ask questions
4. **Only then** - Start writing code

Never jump into implementation without a plan in the increment file.

### TDD Cycle

Each phase has a test list in the increment file. Follow red-green-refactor:

1. **Red** - Write a failing test from the list
2. **Green** - Write minimal code to make it pass
3. **Refactor** - Clean up while keeping tests green
4. **Mark done** - Check off the test in the increment file: `- [x]`

Run tests frequently: `just test` or `just test tests/specific_test.py -v`

### Just Targets

```bash
just check      # Run all checks (lint + typecheck + test)
just test       # Run tests only
just lint       # Run linters
just fmt        # Format code
just typecheck  # Run type checkers
just dev        # Start dev environment (docker-compose)
just dev-logs   # Tail dev logs

# Backend-specific
cd backend && just test

# Frontend-specific
cd frontend && just dev
```

Run `just -l` to see all available commands.

Keep `justfile` targets thin (one-liners). Complex logic goes in scripts.

### Fail Fast Principle

**CI must use just targets** - never duplicate check logic in `.github/workflows/`.

The order matters for fast feedback:
1. **Syntax** (fastest)
2. **Static analysis**
3. **Unit tests**
4. **Integration tests**

Always run `just check` before committing.

## Deployment

### Environments

| Environment | Trigger | URL |
|-------------|---------|-----|
| Preview | Pull request | `https://demo-pr-{N}.cinematch.umans.ai` |
| Production | Push to main | `https://demo.cinematch.umans.ai` |

### Deployment Workflow

1. **Create PR** → triggers preview deployment
2. **Verify preview** at `demo-pr-{N}.cinematch.umans.ai`
3. **Merge to main** → triggers production deployment
4. **Verify production** at `demo.cinematch.umans.ai`

## Configuration

### Backend (.env)
```
DATABASE_URL=sqlite:///./cinematch.db
CORS_ORIGINS=http://localhost:3000,https://demo.cinematch.umans.ai
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Claude Code Skills

This repository includes shared skills in `.claude/skills/`:

| Skill | Description |
|-------|-------------|
| `/backlog` | Create, start, and complete backlog items |
| `/commit` | Generate conventional commits with emoji |
| `/check` | Run pre-commit checks |
| `/pr-merge` | Merge PRs with rebase workflow |
| `/just` | Context-aware just target suggestions |
| `/tdd-check` | TDD cycle helper - test list, red-green-refactor |

## Key Paths

- `docs/architecture/decisions/` - ADRs
- `docs/conventions.md` - full workflow documentation
- `docs/backlog/` - incremental delivery roadmap
- `backend/` - FastAPI application
- `frontend/` - Next.js application
- `operations/` - Terraform with workspace-based environments
