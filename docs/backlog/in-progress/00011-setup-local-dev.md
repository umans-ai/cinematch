# setup-local-dev

## Goal
Avoir un setup local rapide et fiable qui active une feedback loop efficace pour n'importe quel contributeur, surtout pour les agents.

## Context
Le setup local actuel est trop lent et fragile:
- Docker compose rebuild les images à chaque changement
- Le backend attend inutilement (délai de 5min quand l'app est déjà prête)
- Pas de feedback clair sur l'état des services

Pour les agents en particulier, on a besoin d'une boucle de feedback rapide:
1. Démarrer les services < 10s
2. Savoir immédiatement si tout est OK
3. Pouvoir tester avec Playwright sans délai

On veut:
- Backing services (DB) dans Docker uniquement
- Code backend lancé direct avec `uv run` (hot reload)
- Code frontend lancé direct avec `pnpm dev` (hot reload)
- Un just target `just dev-local` qui démarre tout et donne le status

## Ship Criteria
- [ ] `just dev-local` démarre tout (DB + backend + frontend) en < 10s
- [ ] Affiche clairement l'état des services (ports, health check)
- [ ] Hot reload fonctionnel pour backend et frontend
- [ ] Playwright peut tester immédiatement (pas d'attente inutile)
- [ ] Un `just check-dev` vérifie que tout est up avant de continuer
- [ ] Documentation à jour pour les agents (workflow pas à pas)

## Uncertainties
- [ ] Le backend utilise `psycopg` mais l'erreur parlait de `psycopg2` - clarifier le driver
- [ ] Les migrations Alembic fonctionnent-elles avec ce setup?
- [ ] Faut-il un `.env.local` spécifique pour le dev?

## Implementation Plan

### Phase 1: Setup PostgreSQL
1. Créer `docker-compose.deps.yml` avec PostgreSQL 16
2. Démarrer le container
3. Vérifier la connexion avec `psql` ou un script Python

### Phase 2: Setup Backend
1. Vérifier les dépendances (`psycopg` vs `psycopg2`)
2. Configurer `DATABASE_URL=postgresql://...`
3. Lancer avec `uv run uvicorn app.main:app --reload`
4. Vérifier que les tables se créent

### Phase 3: Setup Frontend
1. Vérifier que `pnpm install` est à jour
2. Lancer avec `pnpm dev`
3. Vérifier que l'API est bien appelée sur localhost:8000

### Phase 4: Test E2E
1. Tester avec Playwright le flow création de room
2. Vérifier que tout fonctionne ensemble

## Notes
