# Swipe Feedback & Engagement Improvements

## Status
- **State**: todo
- **Created**: 2025-01-XX
- **Completed**: N/A

## Context

L'expérience de swipe actuelle (page room) manque de feedback immédiat et de "game feel". Observations:

1. **Aucune animation de vote** - Le film disparaît instantanément, pas de feedback visuel sur l'action Like/Pass
2. **Pas d'indication de synchronisation** - L'utilisateur ne sait pas si son partenaire est en train de swiper
3. **Match notification fade trop rapide** - La notification de match peut être manquée si l'utilisateur swipe rapidement
4. **Aucun undo** - Pas de moyen d'annuler un swipe accidentel (friction majeure)
5. **Progression statique** - La barre de progression ne donne pas de sentiment d'accomplissement

## Value Proposition

**Pour** les utilisateurs en train de swiper
**Qui** veulent une expérience engageante et sans erreur
**CineMatch** offre un feedback visuel riche et la possibilité d'annuler
**Contrairement à** l'expérience actuelle qui se sent mécanique et stressante
**Notre solution** célèbre chaque vote, affiche l'activité du partenaire, et permet de corriger les erreurs

## Assumptions to Validate

1. Les utilisateurs swipent plus vite avec un feedback visuel positif (gamification)
2. Le sentiment de "jouer ensemble" augmente l'engagement (voir activité partenaire)
3. La peur de "rater un bon film" par erreur génère de l'anxiété
4. Les micro-célébrations (animations de match) augmentent la satisfaction même sans match final

## Scope

### In Scope
- **Animations de swipe** - Carte sort vers gauche (Pass) ou droite (Like) avec rotation
- **Undo button** - Annuler le dernier vote (max 1 action back)
- **Match celebration** - Confetti animation + son (opt-in) lors d'un match
- **Partner activity indicator** - Pastille "Partner is swiping..." en haut
- **Swipe gestures** - Support touch swipe left/right sur mobile (en plus des boutons)

### Out of Scope
- Undo illimité (complexité backend + game design)
- Chat entre utilisateurs (increment futur)
- Statistiques détaillées ("vous avez aimé 60% des films")
- Swipe par drag & drop desktop (nice-to-have mais pas MVP)

## Implementation Plan

### Phase 1: Swipe Animations (TDD)
**Objectif**: Rendre chaque vote satisfaisant

**Test list**:
- [ ] Carte translate(-100%, 0) + rotate(-15deg) en 300ms au Pass
- [ ] Carte translate(100%, 0) + rotate(15deg) en 300ms au Like
- [ ] Nouvelle carte fade-in opacity 0 → 1 en 200ms après animation sortie
- [ ] Boutons Like/Pass disabled pendant animation (prevent spam)
- [ ] Animation skip si user clique pendant l'animation précédente (prevent queue)
- [ ] Classe CSS `.swiping-left` appliquée au Pass
- [ ] Classe CSS `.swiping-right` appliquée au Like

### Phase 2: Undo Functionality (TDD)
**Objectif**: Réduire l'anxiété du "mauvais clic"

**Test list**:
- [ ] Bouton "Undo" apparaît après un vote
- [ ] Bouton "Undo" disparaît après 5 secondes (auto-hide)
- [ ] Bouton "Undo" disparaît après un nouveau vote
- [ ] Click sur "Undo" revient au film précédent
- [ ] Click sur "Undo" annule le vote backend (DELETE /votes/{vote_id})
- [ ] Max 1 undo à la fois (pas de stack infini)
- [ ] Undo disabled si déjà au premier film
- [ ] Message toast "Vote cancelled" s'affiche au undo

**Backend changes needed**:
- Endpoint `DELETE /api/v1/votes/{vote_id}` pour annuler un vote
- Response doit inclure le `vote_id` au POST /votes pour permettre le DELETE

### Phase 3: Touch Gestures (TDD)
**Objectif**: Support swipe natif mobile

**Test list**:
- [ ] Swipe left (touchmove < -50px) déclenche Pass
- [ ] Swipe right (touchmove > 50px) déclenche Like
- [ ] Carte suit le doigt pendant le drag (transform: translateX)
- [ ] Swipe annulé si release avant threshold (50px)
- [ ] Rotation proportionnelle au drag distance (max 15deg)
- [ ] Haptic feedback (vibration) au dépassement threshold (mobile only)
- [ ] Pas de conflit avec scroll vertical
- [ ] Works avec React onTouchStart/Move/End

### Phase 4: Match Celebration (TDD)
**Objectif**: Célébrer les succès

**Test list**:
- [ ] Confetti animation s'affiche au match (canvas-confetti library)
- [ ] Confetti couleurs primary + white
- [ ] Confetti duration 2.5s puis auto-cleanup
- [ ] Modal match reste visible 3s minimum (was instantané)
- [ ] Bouton "Continue" dans modal match
- [ ] Sound effect "ding" opt-in (localStorage preference)
- [ ] Setting toggle "Sound effects" dans header (future: settings page)

### Phase 5: Partner Activity (TDD)
**Objectif**: Sentiment de présence

**Test list**:
- [ ] Badge "Waiting for partner..." si 1 seul user dans room
- [ ] Badge "Partner is swiping..." si partner actif < 30s
- [ ] Badge disparaît si partner inactif > 30s
- [ ] Polling `/api/v1/rooms/{code}/activity` toutes les 5s
- [ ] Backend track `last_activity_at` par user
- [ ] Animation pulse sur badge activité

**Backend changes needed**:
- Endpoint `GET /api/v1/rooms/{code}/activity` retournant:
  ```json
  {
    "participants": [
      {"name": "Alice", "last_activity_at": "2025-01-15T10:30:00Z"},
      {"name": "Bob", "last_activity_at": "2025-01-15T10:29:45Z"}
    ]
  }
  ```
- Mise à jour `last_activity_at` à chaque vote

## Definition of Done

- [ ] Toutes les phases implémentées et tests passants
- [ ] Backend endpoints `/votes/{id}` DELETE et `/rooms/{code}/activity` GET
- [ ] Pas de régression sur swipe flow existant
- [ ] Tests gestures sur mobile réel (iOS + Android)
- [ ] Performance: 60 FPS pendant animations (Chrome DevTools)
- [ ] Screenshots/GIF dans increment file:
  - Animation swipe left/right
  - Undo button apparition
  - Match confetti
  - Partner activity badge
- [ ] Documentation gesture API (si pattern réutilisable)

## Success Metrics (Post-Deploy)

- **Quantitatif**:
  - Temps moyen par swipe diminue de 20% (plus fluide = plus rapide)
  - Taux d'usage undo < 15% des votes (valide que les erreurs existent)
  - Taux de complétion (finish screen) augmente de 10%

- **Qualitatif**:
  - Feedback utilisateur mentionne "fun", "smooth", "jeu"
  - Réduction des plaintes "j'ai cliqué par erreur"

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Gestures conflictent avec scroll mobile | Medium | High | Désactiver swipe si mouvement vertical > 20px |
| Animations laggy sur ancien mobile | Low | Medium | Utiliser `transform` (GPU-accelerated), tester iPhone 8/Android 8 |
| Undo abuse pour "espionner" liste complète | Low | Low | Limit 1 undo, rate-limit backend si abuse détecté |
| Confetti library trop lourde (bundle size) | Low | Medium | Lazy load, alternatives: react-confetti (17kb) ou custom CSS |

## Open Questions

- [ ] Doit-on afficher un compteur de swipes du partenaire ("Bob liked 12/20")? → **Décision**: Non, crée une pression compétitive négative
- [ ] Le son de match doit-il être opt-in ou opt-out? → **Décision**: Opt-in pour éviter surprise en public
- [ ] Faut-il vibrer au Like uniquement ou aussi au Pass? → **Décision**: Like uniquement (positive reinforcement)

## Dependencies

- Increment 00027 (onboarding) doit être merged avant (partagent le state loading/error)
- Backend doit supporter DELETE vote et track activity (API changes)

## Notes

Cet increment transforme CineMatch d'un "outil utilitaire" en "expérience ludique". L'objectif est de créer du plaisir même quand il n'y a pas de match final. Les animations doivent être rapides (< 300ms) pour ne pas ralentir les power users qui swipent vite.

**Trade-off conscient**: On limite undo à 1 action pour garder la simplicité backend et éviter les abus. Si forte demande utilisateur, on étendra dans un futur increment.
