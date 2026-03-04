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

3. **Explain**: "J'ai créé une issue pour demander l'accès. Un mainteneur va t'ajouter bientôt. Tu recevras une invitation par email à accepter."

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
- "Docker n'est pas installé. C'est ce qui va faire tourner l'application en local. Tu peux l'installer depuis docker.com"
- "Python 3.11+ est requis. On utilise FastAPI pour le backend. Installe-le depuis python.org"

**Continue only when all prerequisites are present.**

### Phase 3: CLI Tools Setup

**Goal**: Install GitHub CLI and verify Playwright MCP.

**GitHub CLI (gh)**:
```bash
# Check if installed
gh --version

# If not, explain: "gh te permet d'interagir avec GitHub depuis le terminal - créer des PRs, voir les checks, etc."
# Provide install instructions for their OS
```

**Authentication check**:
```bash
gh auth status || gh auth login
```

**Explain**: "L'authentification gh permet de créer des PRs et voir le status des checks sans quitter le terminal."

### Phase 4: Repository Setup

**Goal**: Clone and setup the codebase.

**If not already in the repo**:
```bash
git clone https://github.com/umans-ai/cinematch.git
cd cinematch
```

**Explain**: "On clone directement (pas de fork) car avec l'accès write, tes PRs auront accès aux previews AWS."

### Phase 5: Backend Setup

**Goal**: Get Python dependencies installed with uv.

```bash
cd backend

# Check uv
uv --version || echo "uv not installed"
```

**If uv missing**, explain:
> "uv est un gestionnaire de packages Python ultra-rapide écrit en Rust. On l'utilise à la place de pip."
> "Installe-le : `curl -LsSf https://astral.sh/uv/install.sh | sh`"

**Sync dependencies**:
```bash
uv sync --group dev
```

**Explain**: "`uv sync` lit le `uv.lock` et recrée exactement l'environnement attendu. C'est comme `npm install` mais pour Python."

### Phase 6: Frontend Setup

**Goal**: Get Node dependencies installed.

```bash
cd frontend
npm install
```

**Explain**: "Le frontend utilise Next.js. `npm install` télécharge toutes les dépendances listées dans `package.json`."

### Phase 7: Verification

**Goal**: Run the full check suite.

```bash
# From repo root
just check
```

**Explain what happens**:
> "`just check` exécute tous les contrôles du projet :"
> "- Linting (ruff pour Python, eslint pour JS)"
> "- Type checking (ty pour Python, tsc pour TS)"
> "- Tests (pytest)"

**If checks pass**: "Parfait ! Tout est en place."

**If checks fail**: "Il y a des erreurs. Voyons ensemble..." (analyze and help fix)

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

**Explain**: "Docker Compose lance le backend (port 8000) et le frontend (port 3000). C'est le moyen le plus simple de tout faire tourner ensemble."

**Stop after verification**:
```bash
docker-compose down
```

### Phase 9: Project Orientation

**Goal**: Give a high-level overview without overwhelming.

**Product (30 secondes)**:
> "CineMatch est un 'Tinder pour les films à deux'. Un couple swipe sur des films, et l'app trouve les matchs."
> "Ça résout le problème : 'Qu'est-ce qu'on regarde ce soir ?'"

**Architecture (30 secondes)**:
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Next.js   │────▶│   FastAPI   │────▶│   SQLite    │
│  (frontend) │◀────│  (backend)  │     │   (local)   │
└─────────────┘     └─────────────┘     └─────────────┘
```
> "Frontend React (Next.js) ↔ Backend API (FastAPI) ↔ Base de données (SQLite en local, PostgreSQL en prod)"

**Workflow (30 secondes)**:
> "1. Créer un backlog item dans `docs/backlog/todo/`"
> "2. Le déplacer vers `in-progress/` quand on commence"
> "3. Créer une branche, committer, ouvrir une PR"
> "4. La PR crée automatiquement un environnement de preview"
> "5. Review → merge avec rebase"

**Key conventions to remember**:
- **Conventional commits**: `feat:`, `fix:`, `docs:` avec emoji à la fin
- **Just targets**: `just check`, `just dev` - jamais de commandes longues en dur
- **Backlog-driven**: toujours un fichier dans `docs/backlog/` pour suivre le travail

### Phase 10: Deep Dive Offer

**Goal**: Let them explore what interests them.

> "Tu veux que je creuse un aspect en particulier ?"

**Options**:
1. **"Le workflow de contribution"** - Créer un item backlog, branch, PR, preview
2. **"L'architecture backend"** - Structure FastAPI, modèles, endpoints
3. **"L'architecture frontend"** - Next.js app router, composants, state
4. **"Le système de preview"** - Comment AWS déploie automatiquement les PRs
5. **"Rien, je vais explorer seul"** - Terminer ici

## Pedagogical Principles

1. **Explain before doing** - Always say what we're about to do and why
2. **No confirmation spam** - Don't ask "OK to proceed?" at every step
3. **Contextual help** - If something fails, explain what it is and how to fix it
4. **French explanations** - Keep technical terms in English but explanations in French
5. **30-second rule** - No explanation longer than 30 seconds of reading

## Error Handling

| Situation | Response |
|-----------|----------|
| Tool not installed | Explain what it does + install link |
| Check fails | Show error, explain likely cause, suggest fix |
| Already set up | Skip gracefully, mention "Déjà prêt !" |
| Network issues | Suggest retry, explain offline alternatives |

## Success Criteria

Onboarding is complete when:
- [ ] Access request created (or already has access)
- [ ] All prerequisites installed
- [ ] `just check` passes
- [ ] `docker-compose up` starts successfully
- [ ] Contributor understands the 3-sentence summary of product/arch/workflow
