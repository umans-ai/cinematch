# Onboarding UX Improvements

## Status
- **State**: todo
- **Created**: 2025-01-XX
- **Completed**: N/A

## Context

L'onboarding actuel de CineMatch est fonctionnel mais présente plusieurs frictions UX qui impactent le temps de création de room (actuellement > 30 secondes vs objectif < 10 secondes):

1. **Manque de feedback visuel** - Aucune indication que l'app charge les données, pas de transitions entre étapes
2. **Process créatif rigide** - Impossible de revenir en arrière depuis l'étape platform sans perdre ses sélections
3. **Validation silencieuse** - Pas de feedback immédiat sur les erreurs (ex: nom vide, aucune plateforme sélectionnée)
4. **Absence de guidage** - L'utilisateur ne sait pas combien d'étapes restent ni ce qui l'attend

## Value Proposition

**Pour** les nouveaux utilisateurs
**Qui** veulent créer une room rapidement
**CineMatch** offre un onboarding fluide et rassurant
**Contrairement à** l'expérience actuelle qui génère de l'anxiété et des abandons
**Notre solution** guide visuellement, valide en temps réel, et permet de corriger sans perdre le contexte

## Assumptions to Validate

1. Les utilisateurs abandonnent s'ils ne voient pas d'indication de progression
2. Le manque de feedback visuel crée une perception de lenteur même quand l'API est rapide
3. Pouvoir revenir en arrière augmente la confiance et réduit l'anxiété de "faire un mauvais choix"
4. Des messages d'erreur clairs réduisent les tentatives invalides de création de room

## Scope

### In Scope
- **Progress indicator** visible sur toutes les étapes (1/3, 2/3, 3/3)
- **Validation temps réel** avec messages d'erreur inline
- **Préservation du contexte** lors des retours en arrière (nom, platforms sélectionnées)
- **Loading states** explicites pour toutes les actions async (Create room, Join room)
- **Micro-animations** de transition entre étapes (fade-in/slide)

### Out of Scope
- Refonte complète du design visuel (on garde l'identité actuelle)
- Ajout de nouvelles étapes (on optimise le flow existant)
- Onboarding tutoriel/walkthrough (future increment)
- Analytics tracking (future increment)

## Implementation Plan

### Phase 1: Validation & Feedback (TDD)
**Objectif**: Rassurer l'utilisateur à chaque interaction

**Test list**:
- [ ] Affiche "1 of 3" sur l'étape name
- [ ] Affiche "2 of 3" sur l'étape platform selection
- [ ] Affiche "Creating room..." au lieu de "Creating..." avec spinner
- [ ] Affiche message d'erreur inline si nom vide au submit
- [ ] Affiche message d'erreur inline si aucune platform au submit
- [ ] Affiche message d'erreur inline si aucune région au submit
- [ ] Désactive le bouton "Create room" si formulaire invalide
- [ ] Change le curseur en "not-allowed" sur bouton disabled

### Phase 2: Navigation Fluide (TDD)
**Objectif**: Permettre la correction sans friction

**Test list**:
- [ ] Bouton "Back" depuis platform préserve le nom saisi
- [ ] Bouton "Back" depuis platform préserve les platforms sélectionnées
- [ ] Bouton "Back" depuis platform préserve la région sélectionnée
- [ ] Transition fade-in (300ms) lors du passage name → platform
- [ ] Transition fade-in (300ms) lors du retour platform → name
- [ ] Enter key sur champ nom passe à l'étape suivante
- [ ] Enter key sur champ room code lance le join

### Phase 3: Error Handling (TDD)
**Objectif**: Gérer gracieusement les cas d'erreur

**Test list**:
- [ ] Affiche toast "Room not found" si code invalide au join
- [ ] Affiche toast "Room is full" si room complète au join
- [ ] Affiche toast "Network error" si échec API au create
- [ ] Reset loading state après erreur
- [ ] Permet de retry après erreur sans perdre les données
- [ ] Log erreurs dans console avec contexte (room code, timestamp)

### Phase 4: Polish & Micro-interactions (TDD)
**Objectif**: Rendre l'expérience délicieuse

**Test list**:
- [ ] Bouton "Create room" pulse légèrement quand actif (1.5s interval)
- [ ] Champ nom a auto-focus au mount
- [ ] Champ room code a auto-focus à l'affichage du formulaire join
- [ ] Platforms sélectionnées ont animation scale-up (0.95 → 1.0)
- [ ] Success check-mark vert s'affiche 500ms après copy code
- [ ] Spinner de création a la couleur primary

## Definition of Done

- [ ] Toutes les phases implémentées et tests passants
- [ ] Pas de régression sur les tests existants
- [ ] Documentation à jour (CONTRIBUTING.md si nouveau pattern)
- [ ] Screenshots dans cet increment file montrant:
  - Progress indicator à chaque étape
  - Messages d'erreur inline
  - Loading states
  - Navigation retour avec preservation du contexte
- [ ] Testé manuellement sur mobile (responsive)
- [ ] Performance: temps de création room reste < 2s (mesure Network tab)

## Success Metrics (Post-Deploy)

- **Quantitatif** (à mesurer via logs backend):
  - Taux d'abandon entre étapes < 10%
  - Temps moyen de création room < 10 secondes
  - Taux d'erreur room code invalide < 5%

- **Qualitatif** (feedback utilisateurs):
  - Perception de fluidité améliorée
  - Réduction des questions "est-ce que ça marche?"

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Animations ralentissent UX sur mobile bas de gamme | Medium | High | Utiliser `prefers-reduced-motion` CSS, tester sur device réel |
| Trop de validations agacent l'utilisateur | Low | Medium | Valider uniquement au submit, pas keystroke-by-keystroke |
| Préservation contexte augmente complexité state | Low | Low | Déjà géré par React state, juste éviter reset |

## Open Questions

- [ ] Doit-on auto-uppercase le room code pendant la saisie ou seulement au submit? (→ **Décision**: au onChange pour feedback immédiat, déjà implémenté ligne 203)
- [ ] Faut-il un timeout sur les spinners (ex: après 10s, afficher "Taking longer than expected...")? (→ **Décision**: Phase 1, oui pour UX, timeout 8s)

## Notes

Ce increment vise le "low-hanging fruit" UX sans refonte majeure. L'objectif est d'éliminer les frictions identifiées par observation utilisateur, pas de réinventer l'onboarding. Les animations doivent être subtiles, jamais bloquantes.
