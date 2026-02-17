# User Accounts and History

## Goal
Persistent user sessions and swipe history.

## Context
Currently anonymous rooms. Users want to save preferences and see history.

## Ship Criteria
- [ ] OAuth (Google) or magic link auth
- [ ] Save swipe history
- [ ] "Recommend based on past likes"
- [ ] Rejoin previous rooms

## Implementation Plan
- [ ] Choose auth provider (Auth0, Clerk, or DIY)
- [ ] Add User model
- [ ] Link votes to users
- [ ] History page

## Notes
Not needed for MVP validation. Room codes are simpler.
