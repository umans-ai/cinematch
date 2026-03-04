# 00019 - Mood-Based Filtering

## Problem
Movie preferences change based on time of day, weather, energy levels, but the app shows the same suggestions regardless of context.

## Solution
Dynamic mood-based filters:
- Quick mood selector before swiping: "What's the vibe?"
  - 🤣 Need a laugh
  - 😱 Want thrills
  - 🧠 Feeling thoughtful
  - 😴 Low energy / comfort watch
  - 🔥 High energy / action
- Optional: Auto-suggest mood based on:
  - Time of day (late = comfort movies)
  - Weather API (rainy = cozy movies)
  - Day of week (Friday = longer films)
- Filter movie catalog by mood before presenting swipe deck

## Value
- More relevant suggestions = higher match rate
- Respects users' current state
- Reduces "not in the mood for this" swipes
- Shows the app understands context

## Success Criteria
- [ ] Mood selector UI (5-7 moods)
- [ ] Map genres/tags to moods
- [ ] Filter swipe deck by selected mood
- [ ] Optional: Auto-detect mood from context
- [ ] Track which moods lead to most matches

## Assumptions to Validate
- Users want to specify mood vs just browse
- Mood categories resonate with users
- Auto-detection feels helpful vs creepy
- Filtering doesn't overly limit options
