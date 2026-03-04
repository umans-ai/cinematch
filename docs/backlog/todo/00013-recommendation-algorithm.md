# Recommendation Algorithm

## Goal
Implement collaborative filtering to suggest movies based on users' voting history, increasing the likelihood of finding matches that both participants will enjoy.

## Context
Currently, movies are shown in random or popularity order. Users waste time swiping through movies their partner would never like. A smart algorithm can learn from both users' preferences and prioritize movies with high match probability.

## Ship Criteria
- [ ] Implement collaborative filtering algorithm (cosine similarity or similar)
- [ ] Train model on user voting history (likes/dislikes)
- [ ] Predict ratings for unseen movies per user
- [ ] Aggregate predictions across room participants
- [ ] Sort movies by predicted match likelihood
- [ ] Retrain model periodically (every 30 min or on vote threshold)
- [ ] Fallback to popularity-based when insufficient data

## Technical Details

**Algorithm Approach:**
Use cosine similarity for user-based collaborative filtering:
1. Build user-movie rating matrix (+1 for like, -0.5 for dislike)
2. Calculate similarity between users based on overlapping ratings
3. For each candidate movie, predict rating as weighted average of similar users' ratings
4. Sort movies by average predicted score across room participants

**Model Training:**
- Trigger: After every 5 new votes, or every 30 minutes
- Retrain incrementally or full rebuild depending on performance
- Store similarity matrix in memory (small dataset)

**Prediction Formula:**
```
predicted_rating(user, movie) = Σ(similarity(user, other) * rating(other, movie)) / Σ(similarity(user, other))
```

**Cold Start Handling:**
- For new users: show popular movies first
- After 5+ votes: enable personalized recommendations
- For rooms with 1 participant: use individual preference prediction

## API Changes

**New endpoints:**
- `GET /api/v1/recommendations/room/{code}?n=10` - Get personalized recommendations
- `POST /api/v1/recommendations/retrain` - Force model retrain (admin)

**Updated endpoints:**
- `GET /api/v1/movies` - Return movies sorted by recommendation score

## Dependencies
- Requires TMDB integration (00003) for movie catalog
- Works best with Platform/Region Selection (00010) for filtering

## Performance Considerations
- Training: O(n²) where n = number of users with votes
- Prediction: O(n) per movie, can be batched
- With < 1000 users, can run synchronously; consider background jobs for scale

## Future Enhancements
- Content-based filtering (genre preferences)
- Hybrid approach combining collaborative + content-based
- Matrix factorization for larger user bases
- A/B testing framework to measure match rate improvement
