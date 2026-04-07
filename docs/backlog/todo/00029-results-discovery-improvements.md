# Results & Discovery Improvements

## Status
- **State**: todo
- **Created**: 2025-01-XX
- **Completed**: N/A

## Context

L'écran de fin ("finished") est actuellement très basique et rate une opportunité d'engagement:

1. **Liste de matches minimaliste** - Juste titre + année + genre, aucune affordance pour explorer
2. **Absence de call-to-action** - Pas de lien direct vers les plateformes de streaming
3. **Pas de découverte** - On ne montre pas les "near-misses" (films aimés par 1 seul)
4. **Manque de contexte** - Impossible de savoir pourquoi un film a matché (qui l'a liké?)
5. **Fin abrupte** - Seules options: "Start over" (destructif) ou quitter

Selon le product vision (value-proposition.md), le but est "Decision made in under 5 minutes". Actuellement, même après un match, l'utilisateur doit:
1. Noter le titre du film
2. Ouvrir Netflix/Prime/etc
3. Chercher manuellement le film
4. Espérer qu'il soit toujours disponible

## Value Proposition

**Pour** les utilisateurs qui ont trouvé un match
**Qui** veulent passer à l'action immédiatement
**CineMatch** offre un lien direct vers le film sur leur plateforme
**Contrairement à** l'écran actuel qui les abandonne après le match
**Notre solution** guide jusqu'au clic "Play" sur Netflix/Prime/etc

## Assumptions to Validate

1. La majorité des utilisateurs veulent regarder immédiatement après le match
2. Les "near-misses" peuvent convaincre l'indécis ("Regarde, celui-ci aussi est bien!")
3. Montrer qui a liké crée de la transparence et facilite la discussion
4. Un CTA clair vers streaming réduit la friction post-match

## Scope

### In Scope
- **Match cards enrichies** - Poster, note TMDB, badges providers avec deeplinks
- **Deeplinks streaming** - Bouton "Watch on Netflix" qui ouvre l'app/web
- **Near-misses section** - "You might also like" avec films likés par 1 seul
- **Participant insights** - Montrer qui a liké chaque match (icônes users)
- **Share match** - Bouton "Share" qui copie lien vers film TMDB ou génère image

### Out of Scope
- Intégration API directe streaming (besoin partenariats)
- Système de recommendation ML (increment futur)
- Historique des rooms précédentes (nécessite auth)
- Ratings post-visionnage (increment futur)

## Implementation Plan

### Phase 1: Enriched Match Cards (TDD)
**Objectif**: Rendre les matches exploitables

**Test list**:
- [ ] Chaque match affiche poster (fallback emoji si unavailable)
- [ ] Chaque match affiche rating TMDB (étoile + note)
- [ ] Chaque match affiche description tronquée (2 lignes)
- [ ] Click sur match ouvre modal détail (réutilise modal existant)
- [ ] Modal détail inclut bouton "Watch trailer" (YouTube)
- [ ] Badges providers affichés sur chaque match card
- [ ] Layout grid 1 colonne mobile, 2 colonnes desktop si > 2 matches

### Phase 2: Streaming Deeplinks (TDD)
**Objectif**: Réduire friction post-match

**Test list**:
- [ ] Bouton "Watch on {Provider}" pour chaque provider disponible
- [ ] Click ouvre URL JustWatch deeplink (ex: Netflix app)
- [ ] Fallback web URL si deeplink fails (Netflix.com/title/xxx)
- [ ] Icône provider sur bouton CTA (ex: logo Netflix)
- [ ] Message "Not available on your platforms" si aucun provider matché
- [ ] Bouton "Find where to watch" qui ouvre JustWatch search

**Backend changes needed**:
- Ajouter champ `watch_url` par provider dans Movie model
- Populate via JustWatch API (ou construct URL pattern si stable)
- Exemple: `https://www.netflix.com/title/{tmdb_id}` (à valider)

### Phase 3: Near-Misses Discovery (TDD)
**Objectif**: Donner une seconde chance aux films presque matchés

**Test list**:
- [ ] Section "You might also like" affichée si near-misses exist
- [ ] Near-miss = film liké par 1 seul participant
- [ ] Max 3 near-misses affichés (éviter overwhelming)
- [ ] Tri par rating TMDB desc (montrer les meilleurs d'abord)
- [ ] Badge "Liked by Alice" sur chaque near-miss
- [ ] Click ouvre modal détail
- [ ] Pas de CTA "Watch" sur near-misses (éviter confusion)

**Backend changes needed**:
- Endpoint `GET /api/v1/votes/near-misses?code={code}` retournant:
  ```json
  {
    "near_misses": [
      {
        "movie": {...},
        "liked_by": ["Alice"]
      }
    ]
  }
  ```

### Phase 4: Participant Insights (TDD)
**Objectif**: Transparence sur qui a voté quoi

**Test list**:
- [ ] Badge "Liked by Alice & Bob" sur chaque match
- [ ] Utilise initiales si noms > 10 chars (ex: "A.L. & B.M.")
- [ ] Badge "Liked by you & 1 other" si current user in list
- [ ] Icônes avatars colorés par participant (hash nom → couleur)
- [ ] Hover tooltip affiche noms complets si tronqués
- [ ] Ordre alphabétique des noms

**Backend changes needed**:
- Modifier endpoint `/votes/matches` pour inclure `participants` full names:
  ```json
  {
    "movie": {...},
    "participants": ["Alice", "Bob"]
  }
  ```
  (Actuellement retourne participants mais pas clair si noms ou IDs)

### Phase 5: Share Functionality (TDD)
**Objectif**: Faciliter le partage externe

**Test list**:
- [ ] Bouton "Share" sur chaque match card
- [ ] Click copie URL TMDB du film dans clipboard
- [ ] Toast "Link copied!" s'affiche
- [ ] URL format: `https://www.themoviedb.org/movie/{tmdb_id}`
- [ ] Fallback: copy plain text "{Title} ({Year})" si clipboard API fails
- [ ] Future: générer image OG via endpoint (phase 2 de cet increment)

## Definition of Done

- [ ] Toutes les phases implémentées et tests passants
- [ ] Backend endpoints `/votes/near-misses` GET
- [ ] Backend inclut `watch_url` par provider dans responses movies
- [ ] Deeplinks testés sur iOS (Netflix/Prime app) + Android + Desktop
- [ ] Modal réutilise composant existant (pas de duplication)
- [ ] Screenshots dans increment:
  - Matches enrichis avec posters + CTAs
  - Near-misses section
  - Modal avec boutons streaming
  - Share confirmation toast
- [ ] Performance: lazy load posters (IntersectionObserver)

## Success Metrics (Post-Deploy)

- **Quantitatif**:
  - Click-through rate "Watch on {Provider}" > 40% des matches
  - Taux d'usage "Share" > 10% des users avec matches
  - Taux de retry "Swipe again" augmente de 25%

- **Qualitatif**:
  - Feedback "super pratique le lien direct"
  - Réduction du sentiment "et maintenant je fais quoi?"

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Deeplinks cassés (providers changent URLs) | High | Medium | Graceful fallback JustWatch, monitoring errors |
| Near-misses créent pression sociale négative | Low | Medium | Wording neutre "might also like", pas "Bob disagreed" |
| Trop d'options (paradox of choice) | Low | Low | Limit 3 near-misses, highlight top match |
| Providers logos copyright issue | Low | High | Utiliser API officielle TMDB pour logos (licensed) |

## Open Questions

- [ ] Doit-on logger les clicks sur "Watch on Netflix" pour analytics? → **Décision**: Oui, event `watch_cta_clicked` avec provider
- [ ] Faut-il un bouton "Disagree" sur near-misses pour swiper de nouveau? → **Décision**: Non, trop complexe, focus sur matches
- [ ] Order des matches: chronologique ou par rating? → **Décision**: Par rating desc (montrer le meilleur d'abord)

## Dependencies

- TMDB API doit fournir `watch_providers` avec URLs (à vérifier)
- JustWatch deeplink format stable (research needed)
- Increment 00027 (onboarding) pour pattern loading states

## Notes

Cet increment transforme CineMatch d'un "matchmaker" en "guide jusqu'au play button". C'est le dernier mile de la value proposition "Decision made in under 5 minutes".

**Research needed avant implémentation**:
1. TMDB API response pour `watch_providers` - inclut-il des URLs?
2. Format deeplinks Netflix/Prime/Disney+ sur iOS/Android
3. JustWatch public API ou fallback web URLs

**Design inspiration**: Tinder match screen (célébration) + Spotify playlist CTA (action claire).
