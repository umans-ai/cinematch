# Migrate from SQLite to PostgreSQL

## Goal
Move from SQLite to PostgreSQL for production reliability and concurrent access.

## Context
MVP uses SQLite for speed. This increment adds proper database.

## Ship Criteria
- [ ] PostgreSQL RDS instance (or Supabase)
- [ ] Database migrations system (Alembic)
- [ ] Seamless data migration (export/import if needed)
- [ ] Works in preview environments too

## Uncertainties
- [ ] RDS or Supabase? (RDS for same-account consistency)
- [ ] Connection pooling needed? (Start simple, add PgBouncer if issues)

## Implementation Plan
- [ ] Add PostgreSQL to Terraform
- [ ] Set up Alembic for migrations
- [ ] Update SQLAlchemy connection string
- [ ] Test migration path

## Notes
Blocker for scale, but not for MVP validation.
