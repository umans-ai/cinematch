# Auto-approve backlog management PRs

## Context

Issue de référence: #3 ( Proposal: Auto-approve backlog management PRs )
Auteur: @pierrelandry

## Problem Statement

Le workflow backlog actuel crée de la friction pour les contributeurs externes :

1. **Main protégée** : Les contributeurs ne peuvent pas push sur `main`
2. **Chore commits nécessaires** : Même un simple `git mv` (todo → in-progress → done) doit passer par une PR
3. **Approval manuel requis** : Chaque PR backlog nécessite une review maintainer

Cela crée un goulot d'étranglement inutile pour des changements administratifs purs (déplacement de fichiers markdown).

## Admin vs Contributor Workflow Analysis

### Admin workflow (actuel)
```bash
# Sur main
git mv docs/backlog/todo/XXXXX-item.md docs/backlog/in-progress/
git commit -m "chore: start XXXXX-item 🚀"
git push origin main  # ✅ Direct push possible
```

### Contributor workflow (actuel - friction)
```bash
# Sur feature branch
git mv docs/backlog/todo/XXXXX-item.md docs/backlog/in-progress/
git commit -m "chore: start XXXXX-item 🚀"
git push origin feature-branch
# → Créer PR
# → Attendre CI check
# → Attendre approval maintainer
# → Merge manuel
```

### Contributor workflow (après implémentation)
```bash
# Sur feature branch
git mv docs/backlog/todo/XXXXX-item.md docs/backlog/in-progress/
git commit -m "chore: start XXXXX-item 🚀"
git push origin feature-branch
# → PR créée
# → Auto-approval si critères respectés
# → Auto-merge activé
```

## Impact Analysis

### Workflow Admin
- **Pas de changement** : Continue à pouvoir push direct sur main si nécessaire
- **Bénéfice indirect** : Moins de PRs backlog à reviewer des contributeurs

### Workflow Contributor
- **Réduction de friction** : Plus besoin d'attendre un maintainer pour les tâches administratives
- **Autonomie accrue** : Le contributor contrôle son cycle backlog de bout en bout
- **Audit trail préservé** : Les commits sont toujours signés, l'historique git est intact

### Sécurité
- **Périmètre strict** : Uniquement `docs/backlog/**`, uniquement des renommages (0 additions, 0 deletions)
- **Association vérifiée** : Seuls les `COLLABORATOR` (write access) peuvent bénéficier de l'auto-approval
- **Pas de bypass de CI** : Le check `just check` doit toujours passer (même si pour du markdown il est trivial)

## Implementation Plan

### Phase 1: GitHub Actions Workflow
Créer `.github/workflows/auto-approve-backlog.yml` :

```yaml
name: Auto-approve backlog PRs

on:
  pull_request:
    types: [opened, synchronize]
    paths:
      - 'docs/backlog/**'

jobs:
  auto-approve:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - name: Check PR criteria
        id: check
        run: |
          # Vérifier que seul docs/backlog/ est modifié
          # Vérifier que c'est un rename (0 additions, 0 deletions)
          # Vérifier que l'auteur est COLLABORATOR
          # Vérifier que changed_files == 1
          echo "should_approve=true" >> $GITHUB_OUTPUT

      - name: Auto-approve
        if: steps.check.outputs.should_approve == 'true'
        uses: hmarr/auto-approve-action@v4

      - name: Enable auto-merge
        if: steps.check.outputs.should_approve == 'true'
        run: gh pr merge --auto --rebase "$PR_URL"
        env:
          PR_URL: ${{ github.event.pull_request.html_url }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Phase 2: Tests
- [ ] Créer une PR de test avec seulement un `git mv` dans docs/backlog/
- [ ] Vérifier l'auto-approval
- [ ] Vérifier l'auto-merge
- [ ] Créer une PR avec un fichier en dehors de docs/backlog/ → vérifier qu'elle n'est pas auto-approuvée

### Phase 3: Documentation
- [ ] Mettre à jour `CLAUDE.md` (section "Backlog Workflow")
- [ ] Mettre à jour `docs/conventions.md` si nécessaire
- [ ] Mettre à jour `CONTRIBUTING.md` pour expliquer l'auto-approval aux contributeurs

## Validation Criteria

- [ ] Une PR qui ne modifie qu'un fichier dans `docs/backlog/` (rename uniquement) est auto-approuvée
- [ ] L'auto-approval ne s'applique qu'aux collaborateurs avec write access
- [ ] Une PR avec des changements hors `docs/backlog/` nécessite toujours une review manuelle
- [ ] La documentation reflète le nouveau comportement

## References

- Issue #3 (cette issue sera fermée une fois ce backlog item créé)
- `CLAUDE.md` - Section "Backlog Workflow"
- `docs/conventions.md` - Workflow conventions
