# CineMatch

Swipe-based movie picker for couples. Stop scrolling, start watching.

## Rules

- Never add `Co-Authored-By` to commit messages
- Keep `CLAUDE.md` and `docs/` in sync
- Each commit is a release candidate - keep main deployable
- SQLite for MVP, PostgreSQL comes in increment 2

## Terraform Layer Conventions

| Layer | Lifecycle | Scope | Examples |
|-------|-----------|-------|----------|
| `00-foundation` | Months/years | Global/shared | ECR, Route53 zone, ACM certificate |
| `01-service` | Hours/days | Per-environment (workspace) | VPC, ECS, ALB, RDS, IAM roles |

**Rule of thumb:** If it's workspace-dependent (`terraform.workspace`), it goes in `01-service`.

**Key principle (Répétabilité):** Every environment (preview, staging, production) must use identical architecture. No "shared VPC" - each workspace creates its own isolated VPC.

## Documentation Update Rule

Before completing any backlog item, update **all impacted documentation**:

| Change Type | Docs to Update |
|-------------|----------------|
| Architecture changes | `docs/architecture/overview.md`, relevant ADR |
| Database changes | `docs/architecture/overview.md`, migration ADR |
| API changes | Backend docstrings (auto-generated) |
| Product features | `docs/product/value-proposition.md`, `docs/product/specs/*.md` |
| Workflow changes | `CLAUDE.md`, `docs/conventions.md` |

**Checklist before `/backlog done`:**
- [ ] Code implemented and tested
- [ ] Architecture docs updated (if structural changes)
- [ ] Product docs updated (if user-facing changes)

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

**PR workflow (recommended for most changes):**

1. **Code ready**: Implementation + tests + docs updated
   - Run `just check` locally
   - Update increment file with screenshots if UI changes
2. **Create PR**: `gh pr create --title "..." --body "..."`
   - Include walkthrough in PR description
3. **Verify pipeline**: Wait for checks and preview deployment
4. **Test preview**: Verify at `demo-pr-{N}.cinematch.umans.ai`
5. **`/backlog done` on branch**: Mark item ready to merge
   ```bash
   # From feature branch, after all verification
   git checkout main
   git pull origin main
   git mv docs/backlog/in-progress/XXXXX-name.md docs/backlog/done/
   git commit -m "chore: complete <name> ✅"
   git push origin main
   git checkout <branch>
   ```
6. **Merge**: `gh pr merge --rebase`
7. **Verify production**: `git checkout main && git pull`, check `demo.cinematch.umans.ai`

**Direct push workflow (docs, chores, trivial fixes only):**

1. Code ready on branch
2. Fast-forward merge: `git checkout main && git merge --ff-only <branch>`
3. `/backlog done`: Move item to done on main
4. Push: `git push origin main`

**Continuous Retro** (optional, during step 5):
- What was harder than expected?
- What would improve next time?
- Add `retro:` items to todo/ if concrete

### Adding backlog items

Each increment must be:
- **Shippable** - can be deployed independently
- **Valuable** - delivers user or business value
- **Testable** - has clear verification criteria
- **Simple** - small enough to complete in one branch
- **Validating** - has explicit assumptions to confirm

Use next available 5-digit ID: `XXXXX-name.md`

### Admin vs Contributor Workflow

**Check your role**: Run `just check-role` to see if you're an admin or contributor.

| | **Admin (Umans AI team)** | **Contributor (external)** |
|---|---|---|
| **Backlog creation** | On `main` branch | On feature branch |
| **Push to main** | ✅ Yes | ❌ No (protected) |
| **Workflow** | `git add` → commit → push to main → create branch | Create branch → `git add` → commit → push branch |
| **Visibility** | Items visible on main immediately | Items visible after PR merge |

**Both use identical git operations** (`git add`, `git mv`, `git commit`), only the branch differs.

## Architecture Decision Records

ADRs live in `docs/architecture/decisions/` with sequential numbering: `NNN-title.md`

Create an ADR when making decisions that:
- Affect system structure
- Constrain future choices
- Are non-obvious or debated

Commit ADRs alongside implementation, not separately.

## Tool Management (mise)

The project uses [mise](https://mise.jdx.dev/) to manage tool versions (Python, Node, Terraform, etc.). This eliminates "works on my machine" issues and avoids cluttering global environments.

### Setup

```bash
# Install mise (one-time)
curl https://mise.run | sh

# Enter project directory - tools auto-install
cd cinematch

# Verify setup
mise doctor
mise list
```

All required tools and versions are defined in `.mise.toml` and match CI/CD exactly.

### For Agents

When working with this codebase:
1. **Assume mise is available** - Don't ask about tool installation
2. **Tools are project-scoped** - Commands like `python`, `node`, `terraform` use mise-managed versions
3. **No need to install tools manually** - mise handles it automatically

## Python Toolchain (UV)

The backend uses the [Astral toolchain](https://astral.sh/): uv for packages, ruff for linting, ty for type checking.

### Quick Reference

```bash
cd backend

# Sync dependencies (creates venv + installs from uv.lock)
uv sync --group dev

# Run commands in project environment
uv run pytest
uv run uvicorn app.main:app --reload

# Add dependency
uv add <package>

# Add dev dependency (to dependency-groups.dev)
uv add --group dev <package>

# Update lockfile after manual pyproject.toml edits
uv lock
```

### Agent Guidelines

1. **Always `uv sync --group dev` first** - Ensures environment matches lockfile
2. **Use `uv run`** instead of activating venvs manually
3. **Commit `uv.lock`** changes alongside `pyproject.toml`
4. **Don't use pip** - Use `uv add` or edit `pyproject.toml` + `uv lock`
5. **Type checking with ty** - Astral's Rust-based type checker, 10-100x faster than mypy

See [ADR 006](docs/architecture/decisions/006-uv-toolchain.md) for rationale.

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

# Backend-specific (uses uv)
cd backend && just sync    # First time / after dependency changes
cd backend && just dev     # Start dev server
cd backend && just test    # Run tests

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

## CI/CD Pipeline Safety

**Before pushing to main:**
1. **Check pipeline status** - Run `gh run list` and verify no runs are in progress
2. **Wait for completion** - Never push if a deploy job is running (Terraform lock risk)
3. **Batch changes** - Avoid rapid successive pushes; wait for CI to complete

**Pipeline triggers (paths):**
- CI runs on: `backend/**`, `frontend/**`, `operations/**`, `.github/workflows/**`
- CI skips on: `docs/**`, `*.md` (unless workflow files changed)

See `.github/workflows/ci-cd.yml` for exact path filters.

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
| `/accept-contributor` | Accept contributor, close issue, post welcome |

## Key Paths

- `docs/architecture/decisions/` - ADRs
- `docs/architecture/overview.md` - system architecture (C4 diagrams)
- `docs/product/` - product documentation (value prop, specs)
- `docs/conventions.md` - full workflow documentation
- `docs/backlog/` - incremental delivery roadmap
- `backend/` - FastAPI application
- `frontend/` - Next.js application
- `operations/` - Terraform with workspace-based environments
- `operations/00-foundation/` - shared infrastructure (ECR, Route53, ACM)
- `operations/01-service/` - per-environment infrastructure (VPC, ECS, RDS)
