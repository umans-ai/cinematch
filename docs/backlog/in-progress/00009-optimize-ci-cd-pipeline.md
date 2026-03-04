# Optimiser la pipeline CI/CD : pnpm + BuildKit cache

## Contexte

Le build du frontend est le goulot d'étranglement de la pipeline CI/CD :
- Build frontend : **~1m24s** (rebuild complet à chaque run)
- Build backend : **~20s** (cache efficace, layers déjà existants)

Le frontend utilise `npm ci` et build from scratch sans cache entre les runs.

## Motivations

### 1. Temps de déploiement
Chaque PR attend ~4 minutes pour le preview. En réduisant le build frontend, on améliore le feedback loop du développement.

### 2. Coût
GitHub Actions facture par minute. Moins de temps = moins de coûts.

### 3. Developer Experience
Des builds rapides encouragent les petits commits et les itérations fréquentes.

## Solution proposée

### 1. Migration de npm vers pnpm
**Pourquoi pnpm ?**
- Store partagé avec hardlinks (pas de duplication de fichiers)
- Installation parallèle plus agressive
- Lockfile (`pnpm-lock.yaml`) plus rapide à parser que `package-lock.json`
- Compatible avec l'écosystème npm existant

### 2. Cache Docker avec BuildKit
**Pourquoi BuildKit + cache GHA ?**
- GitHub Actions fournit un cache natif (`type=gha`) pour les layers Docker
- Permet de réutiliser `node_modules` et le build Next.js entre les runs
- Gain estimé : **~60-70 secondes** sur le build frontend

### 3. `.dockerignore` optimisé
**Pourquoi ?**
- Réduit la taille du contexte de build envoyé au daemon Docker
- Accélère le COPY dans le Dockerfile
- Évite d'invalider le cache inutilement

## Implémentation

### Changements requis

1. **Workflow CI/CD** (`.github/workflows/ci-cd.yml`)
   - Ajouter `docker/setup-buildx-action@v3`
   - Remplacer les commandes docker CLI par `docker/build-push-action@v5`
   - Configurer `cache-from: type=gha` et `cache-to: type=gha,mode=max`

2. **Dockerfile frontend**
   - Activer pnpm via corepack
   - Utiliser `pnpm install --frozen-lockfile`

3. **Fichiers à créer/supprimer**
   - Créer `frontend/.dockerignore`
   - Supprimer `frontend/package-lock.json`
   - Créer `frontend/pnpm-lock.yaml`

4. **Check job**
   - Remplacer `npm ci` par `pnpm install` avec `pnpm/action-setup`

## Critères d'acceptation

- [ ] Pipeline CI/CD complète en moins de 2m30s (vs 4m+ actuellement)
- [ ] Build frontend en moins de 30s avec cache chaud
- [ ] Build frontend en moins de 60s avec cache froid
- [ ] Preview deployments fonctionnent toujours
- [ ] Pas de régression sur le build backend

## Estimation

- **Complexité** : Moyenne
- **Risque** : Faible (changements isolés à la CI/CD)
- **Temps estimé** : 2-3 heures
