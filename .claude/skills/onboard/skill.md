---
name: onboard
description: Onboard a new contributor to the CineMatch project - setup environment, verify tools, and explain the project
---

# Onboard New Contributor

Guide new contributors through complete environment setup and project orientation.

## Usage

### `/onboard [github-username]`

If no username provided, will prompt for it. The skill handles the entire onboarding journey from access request to running local dev environment.

## What It Does

### Phase 1: Access Request

**Goal**: Get the contributor write access to the repo.

1. **Check if already a collaborator**:
   ```bash
   gh api repos/umans-ai/cinematch/collaborators/{username} --silent 2>/dev/null && echo "Already has access"
   ```

2. **If no access, create issue**:
   ```bash
   gh issue create --title "Request access: @{username}" --body "Requesting write access to contribute to CineMatch."
   ```

3. **Explain**: "I've created an issue to request access. A maintainer will add you soon. You'll receive an email invitation to accept."

### Phase 2: Prerequisites Check

**Goal**: Verify all required tools are installed.

**Check each tool with pedagogical explanation:**

| Tool | Check Command | Why We Need It |
|------|---------------|----------------|
| Git | `git --version` | Version control - we use trunk-based development |
| Docker | `docker --version && docker compose version` | Local dev environment - runs backend + frontend together |
| Python 3.11+ | `python3 --version` | Backend runtime - FastAPI app |
| Node.js 20+ | `node --version` | Frontend runtime - Next.js app |

**For each missing tool**, explain what it does and how to install it:
- "Docker is not installed. This runs the application locally. Install from docker.com"
- "Python 3.11+ is required. We use FastAPI for the backend. Install from python.org"

**Continue only when all prerequisites are present.**

### Phase 3: CLI Tools Setup

**Goal**: Install GitHub CLI and verify Playwright MCP.

**GitHub CLI (gh)**:
```bash
# Check if installed
gh --version

# If not, explain: "gh lets you interact with GitHub from the terminal - create PRs, check status, etc."
# Provide install instructions for their OS
```

**Authentication check**:
```bash
gh auth status || gh auth login
```

**Explain**: "gh authentication lets you create PRs and check CI status without leaving the terminal."

### Phase 4: Repository Setup

**Goal**: Clone and setup the codebase.

**If not already in the repo**:
```bash
git clone https://github.com/umans-ai/cinematch.git
cd cinematch
```

**Explain**: "We clone directly (no fork needed) because with write access, your PRs get automatic AWS previews."

### Phase 5: Backend Setup

**Goal**: Get Python dependencies installed with uv.

```bash
cd backend

# Check uv
uv --version || echo "uv not installed"
```

**If uv missing**, explain:
> "uv is a fast Python package manager written in Rust. We use it instead of pip."
> "Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`"

**Sync dependencies**:
```bash
uv sync --group dev
```

**Explain**: "`uv sync` reads `uv.lock` and recreates the exact environment. Like `npm install` but for Python."

### Phase 6: Frontend Setup

**Goal**: Get Node dependencies installed with pnpm.

```bash
cd frontend

# Check pnpm
pnpm --version || echo "pnpm not installed"
```

**If pnpm missing**, explain:
> "pnpm is a fast Node.js package manager. It uses hardlinks to avoid duplicating files."
> "Install: `npm install -g pnpm`"

**Install dependencies**:
```bash
pnpm install
```

**Explain**: "The frontend uses Next.js. `pnpm install` reads `pnpm-lock.yaml` and recreates the exact environment. Like `uv sync` but for the frontend."

### Phase 7: Verification

**Goal**: Run the full check suite.

```bash
# From repo root
just check
```

**Explain what happens**:
> "`just check` runs all project checks:"
> "- Linting (ruff for Python, eslint for JS)"
> "- Type checking (ty for Python, tsc for TS)"
> "- Tests (pytest)"

**If checks pass**: "Perfect! Everything is set up."

**If checks fail**: "There are errors. Let's look together..." (analyze and help fix)

### Phase 8: Test Local Dev

**Goal**: Verify the app starts correctly.

```bash
# Quick test with Docker
docker-compose up -d
```

**Wait a few seconds, then check**:
```bash
curl -s http://localhost:8000/health || echo "Backend not ready"
```

**Explain**: "Docker Compose starts the backend (port 8000) and frontend (port 3000). This is the easiest way to run everything together."

**Stop after verification**:
```bash
docker-compose down
```

### Phase 9: Detect Role and Project Orientation

**Goal**: Determine if user is admin or contributor, then give high-level overview.

**Auto-detect role**:
```bash
just check-role
```

**Explain based on result**:
- If Admin: "You're an admin. Use main branch for backlog items, push to main after each step."
- If Contributor: "You're a contributor. Cannot push to main - do everything on your feature branch."

**Product (30 seconds)**:
> "CineMatch is 'Tinder for movies for couples'. A couple swipes on movies, and the app finds their matches."
> "It solves the problem: 'What do we watch tonight?'"

**Architecture (30 seconds)**:
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Next.js   │────▶│   FastAPI   │────▶│   SQLite    │
│  (frontend) │◀────│  (backend)  │     │   (local)   │
└─────────────┘     └─────────────┘     └─────────────┘
```
> "React frontend (Next.js) ↔ API backend (FastAPI) ↔ Database (SQLite locally, PostgreSQL in prod)"

**Contribution workflow (30 seconds)** - **Contributor mode**:
> "**Important: You cannot push to `main`**, only create branches and PRs."
>
> "**Your simplified workflow:**"
> ```
> git checkout -b 00005-my-feature                    # Create branch directly
> git add docs/backlog/todo/00005.md                  # Create in todo/
> git commit -m "chore: add my-feature 📋"
> git mv docs/backlog/todo/00005.md docs/backlog/in-progress/  # Move to in-progress/
> git commit -m "chore: start my-feature 🚀"
> # ... development ...
> git mv docs/backlog/in-progress/00005.md docs/backlog/done/  # Move to done/
> git commit -m "chore: complete my-feature ✅"
> git push origin 00005-my-feature                    # Push + PR
> ```
> "The PR deploys a preview. Review → merge → everything lands on `main`."
> "Only difference: you never push to `main`, everything happens on your branch."

**Admin workflow (alternative)** - **Admin mode**:
> "**Admin workflow on `main` branch:**"
> ```
> # On main branch
> git add docs/backlog/todo/00005.md
> git commit -m "chore: add my-feature 📋"
> git push origin main
> git mv docs/backlog/todo/00005.md docs/backlog/in-progress/
> git commit -m "chore: start my-feature 🚀"
> git push origin main
> git checkout -b 00005-my-feature
> # ... development ...
> git mv docs/backlog/in-progress/00005.md docs/backlog/done/
> git commit -m "chore: complete my-feature ✅"
> git push origin 00005-my-feature
> gh pr create --title "feat: ..." --body "..."
> ```
> "Items are visible on main immediately; done commit travels with PR."

**Key conventions to remember**:
- **Conventional commits**: `feat:`, `fix:`, `docs:` with emoji at the end
- **Just targets**: `just check`, `just dev` - never long commands inline
- **Backlog-driven**: always a file in `docs/backlog/` to track work

### Phase 10: Deep Dive Offer

**Goal**: Let them explore what interests them.

> "Want me to deep dive on any of these?"

**Options**:
1. **"The contribution workflow"** - Create a backlog item, branch, PR, preview
2. **"Backend architecture"** - FastAPI structure, models, endpoints
3. **"Frontend architecture"** - Next.js app router, components, state
4. **"The preview system"** - How AWS auto-deploys PRs
5. **"Nothing, I'll explore on my own"** - Finish here

## Pedagogical Principles

1. **Explain before doing** - Always say what we're about to do and why
2. **No confirmation spam** - Don't ask "OK to proceed?" at every step
3. **Contextual help** - If something fails, explain what it is and how to fix it
4. **English throughout** - Keep all explanations in English (consistent with project)
5. **30-second rule** - No explanation longer than 30 seconds of reading

## Error Handling

| Situation | Response |
|-----------|----------|
| Tool not installed | Explain what it does + install link |
| Check fails | Show error, explain likely cause, suggest fix |
| Already set up | Skip gracefully, mention "Already ready!" |
| Network issues | Suggest retry, explain offline alternatives |

## Success Criteria

Onboarding is complete when:
- [ ] Access request created (or already has access)
- [ ] All prerequisites installed
- [ ] `just check` passes
- [ ] `docker-compose up` starts successfully
- [ ] Contributor understands the 3-sentence summary of product/arch/workflow
