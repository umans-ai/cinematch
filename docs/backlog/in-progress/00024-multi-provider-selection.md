# Multi-Provider Streaming Selection

## Goal
Permettre aux utilisateurs de sélectionner plusieurs providers de streaming simultanément.

## Context
Actuellement, les utilisateurs ne peuvent choisir qu'un seul provider de streaming à la fois (ou la sélection est limitée). Les utilisateurs veulent pouvoir sélectionner plusieurs services auxquels ils sont abonnés (ex: Netflix + Disney+ + Canal+) pour élargir le catalogue de films proposés.

## Ship Criteria
- [ ] UI permettant la sélection multiple de providers
- [ ] Filtrage des films disponibles sur AU MOINS un des providers sélectionnés
- [ ] Persistance de la sélection dans la room/session
- [ ] Affichage visuel des providers associés à chaque film

## Implementation Plan
- [ ] Modifier le modèle de données pour supporter une liste de providers
- [ ] Adapter l'API TMDB pour filtrer avec plusieurs `watch_region` + `with_watch_providers`
- [ ] Mettre à jour l'UI de sélection (checkboxes ou multi-select)
- [ ] Migrer les données existantes (provider unique → liste)

## Notes
Nécessite probablement une évolution du schéma de base de données.
