# [RETRO] Enhance /backlog Skill with Doc Suggestions

## Goal

Make the `/backlog` skill smarter by suggesting documentation updates based on the changes made in the branch.

## Context

From retrospective (2026-03-04): We now have a "Documentation Update Rule" that requires updating docs before completing an item. But knowing which docs to update requires understanding the changes.

## Ship Criteria

- [ ] `/backlog done` analyzes changed files and suggests which docs to update
- [ ] Suggestions based on file patterns (e.g., `operations/` → architecture docs)
- [ ] Shows a checklist before confirming completion
- [ ] Non-blocking - just advisory

## Implementation Plan

**Phase 1: Pattern Matching**
Add logic to the backlog skill:
```
if operations/*.tf changed:
  suggest "docs/architecture/overview.md"
if backend/app/models/*.py changed:
  suggest "ADR for data model" or "architecture overview"
if frontend/src/components/*.tsx changed:
  suggest "product specs if UI behavior changed"
```

**Phase 2: Integration**
- Run analysis when `/backlog done` is invoked
- Display suggestions as checkboxes
- User confirms they've considered each

## Uncertainties

- [ ] Will this add friction or be genuinely helpful?
- [ ] Should we integrate with `git diff --name-only` or parse the changes?

## Notes

This is about raising awareness, not enforcement. Keep it lightweight.
