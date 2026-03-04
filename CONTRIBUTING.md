# Contribuer à CineMatch

> 🎬 *Swipe-based movie picker for couples. Stop scrolling, start watching.*

## 🎯 Objectif de ce projet

CineMatch est un projet **open source éducatif** pour apprendre et s'améliorer en développement logiciel, avec ou sans l'aide de l'IA.

- **Stack moderne** : FastAPI, Next.js, Terraform, AWS
- **Déploiement continu** : chaque PR crée un environnement de preview
- **Apprentissage collaboratif** : discutons des choix techniques, pas seulement du code

---

## 🚀 Pour commencer (5 minutes)

### Prérequis

- Git
- Docker + Docker Compose
- Python 3.11+ (pour le backend natif)
- Node.js 20+ (pour le frontend natif)

### 1. Obtenir l'accès write

**Pour les contributeurs externes** : ouvre une issue avec le titre `Request access: @ton-github`.

Un mainteneur Umans AI t'ajoutera avec les permissions **Triage** (issues/PRs) ou **Write** (branches) selon ta contribution prévue.

> 💡 **Pourquoi pas de fork ?** Avec l'accès write, tes PRs bénéficient des previews automatiques sur notre infrastructure AWS sponsorisée.

### 2. Cloner et lancer

```bash
# Clone direct (pas de fork nécessaire)
git clone https://github.com/umans-ai/cinematch.git
cd cinematch

# Lancer l'environnement de dev
docker-compose up

# Ou en natif pour itérer plus vite
# Terminal 1: cd backend && uvicorn app.main:app --reload
# Terminal 2: cd frontend && npm run dev
```

L'application est disponible sur http://localhost:3000

---

## 🏗️ Architecture en 30 secondes

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Next.js   │────▶│   FastAPI   │────▶│   SQLite    │
│  (frontend) │◀────│  (backend)  │     │   (local)   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                        │
       └────────────────────────────────────────┘
              Même repo, code colocalisé
```

| Environnement | Commande | URL |
|---------------|----------|-----|
| Local | `docker-compose up` | http://localhost:3000 |
| Preview (PR) | Automatique | https://demo-pr-{N}.cinematch.umans.ai |
| Production | Merge vers `main` | https://demo.cinematch.umans.ai |

---

## 📝 Workflow de contribution

### Avant de coder

1. **Lire les conventions** : `docs/conventions.md` et `CLAUDE.md`
2. **Comprendre l'architecture** : `docs/architecture/overview.md`
3. **Créer une branche** : `git checkout -b 00005-ma-feature`
4. **Créer un backlog item** : `docs/backlog/todo/XXXXX-nom-feature.md`
5. **Déplacer vers in-progress** sur ta branche :
   ```bash
   git add docs/backlog/todo/00005-ma-feature.md
   git commit -m "chore: add ma-feature 📋"
   git mv docs/backlog/todo/00005-ma-feature.md docs/backlog/in-progress/
   git commit -m "chore: start ma-feature 🚀"
   ```

> 💡 **Pourquoi pas de push sur `main` ?** Les contributeurs externes ne peuvent pas pousser sur `main`. Tu fais tout sur ta branche, et tout arrive sur `main` via la PR.

### Pendant le développement

- **Utilise l'IA** (Claude, Cursor, Copilot...) mais **vérifie et comprends** ce qu'elle propose
- **Test-driven** quand possible : écris le test d'abord
- **Petits commits** : un concept = un commit
- **Conventional commits** : `feat:`, `fix:`, `docs:`, etc. (voir `docs/conventions.md`)

### Pull Request

```bash
# Créer la branche
git checkout -b 00005-ma-feature

# Commiter et pusher
git add .
git commit -m "feat: ajoute la recherche de films ✨"
git push origin 00005-ma-feature

# Créer la PR via GitHub CLI ou l'interface web
gh pr create --title "feat: recherche de films" --body "Closes #XX"
```

**Ce qui se passe ensuite :**
- ✅ CI exécute les tests et le linting
- 🚀 Preview se déploie automatiquement (commentaire sur la PR)
- 👀 Un mainteneur Umans AI review et approuve
- 🔄 Rebase puis merge vers `main`

---

## 🔒 Ce que tu peux / ne peux pas faire

| ✅ Tu PEUX | ❌ Tu NE PEUX PAS |
|-----------|------------------|
| Modifier le code backend/frontend | Modifier `operations/` (infrastructure AWS) |
| Créer des migrations SQLite | Pousser directement sur `main` |
| Voir ta preview déployée automatiquement | Accéder aux credentials AWS |
| Proposer des changements d'architecture | Modifier les secrets GitHub |
| Ouvrir des issues et des discussions | Merger sans approbation |

> **Pourquoi ces limites ?** L'infrastructure AWS est sponsorisée par Umans AI. Seuls les membres de l'organisation ont les droits pour éviter les coûts imprévus et garantir la sécurité.

---

## 🎓 Ressources pédagogiques

### Documentation interne

- [Architecture Overview](docs/architecture/overview.md) — Vue d'ensemble technique
- [Conventions](docs/conventions.md) — Workflow, commits, TDD
- [CLAUDE.md](CLAUDE.md) — Comment l'IA est utilisée dans ce projet
- [ADR](docs/architecture/decisions/) — Décisions architecturales passées

### Discussion et apprentissage

- **Questions techniques** : Ouvre une issue avec le label `question`
- **Propositions d'architecture** : Ouvre une issue avec le label `discussion`
- **Bug reports** : Ouvre une issue avec le label `bug` et le template

> 💡 **Mentorat implicite** : Les PRs sont des opportunités d'apprentissage. N'hésite pas à poser des questions sur les choix techniques dans tes PRs.

---

## 🛠️ Guide par type de contribution

### 🐛 Bug fix

1. Crée une issue décrivant le bug
2. Mentionne `Fixes #XX` dans ta PR
3. Ajoute un test qui reproduit le bug si possible

### ✨ Nouvelle feature

1. Discute de l'approche dans une issue avant de coder
2. Suivre le workflow backlog (fichier dans `docs/backlog/`)
3. Mettre à jour le README si la feature change l'UX

### 📝 Documentation

1. Docs techniques → `docs/`
2. README → à la racine
3. Commentaires dans le code → seulement si le "pourquoi" n'est pas évident

### ♻️ Refactoring

1. Une seule chose à la fois
2. Tests verts avant et après
3. Expliquer le "pourquoi" dans le message de commit

---

## ❓ FAQ

**Q: Puis-je utiliser mon propre compte AWS pour déployer ?**

A: Oui, mais ce n'est pas nécessaire. Les previews automatiques couvrent 99% des besoins. Si tu veux vraiment tester l'infra toi-même, fork le repo et configure tes propres secrets AWS.

**Q: L'IA est-elle obligatoire pour contribuer ?**

A: Non. L'IA est un outil recommandé mais pas obligatoire. L'important est d'apprendre, que ce soit en écrivant le code toi-même ou en validant les propositions de l'IA.

**Q: Je ne comprends pas une décision architecturale.**

A: Parfait ! Ouvre une issue `discussion` pour challenger la décision. Les ADRs ne sont pas gravés dans le marbre — ils documentent le contexte au moment de la décision.

**Q: Puis-je ajouter une feature qui n'est pas dans le backlog ?**

A: Ouvre d'abord une issue pour en discuter. Le backlog reflète la vision produit, mais les bonnes idées externes sont les bienvenues.

---

## 🤝 Code de conduite

- **Soyez bienveillants** : On est ici pour apprendre ensemble
- **Questions bienvenues** : Pas de questions "stupides" en développement
- **Feedback constructif** : Sur le code, pas sur la personne
- **Partagez vos apprentissages** : Si tu découvres quelque chose, documente-le

---

## 🚦 Besoin d'aide ?

| Problème | Solution |
|----------|----------|
| Environnement local ne démarre pas | Ouvre une issue avec `setup` label |
| Pas sûr de ton approche | Ouvre une issue avec `discussion` label |
| Bug mystérieux | Ouvre une issue avec les logs |
| Question sur l'IA | Mentionne `@maintainer` dans ta PR |

---

*CineMatch est un projet de la communauté Umans AI. Merci de contribuer !* 🎬
