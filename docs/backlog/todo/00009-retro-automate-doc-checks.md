# [RETRO] Automate Documentation Checks

## Goal

Prevent forgetting to update documentation when making architecture or product changes. Automate the "Documentation Update Rule" verification.

## Context

From retrospective (2026-03-04): We identified that documentation updates were happening after the fact or being forgotten. The "Documentation Update Rule" was added to CLAUDE.md, but it's still manual.

## Ship Criteria

- [ ] Script or CI check detects when architecture files changed but docs/architecture/overview.md wasn't updated
- [ ] Script or CI check detects when DB models changed but no ADR/doc update
- [ ] Check runs on PR and warns (non-blocking) about potentially missing doc updates
- [ ] Zero false positives (don't warn when docs ARE updated)

## Implementation Plan

**Phase 1: Detection Script**
- Create `scripts/check-docs-updated.py`
- Compare files changed in PR against doc patterns
- Output warnings with suggested docs to update

**Phase 2: CI Integration**
- Add as non-blocking check in CI workflow
- Comment PR with warnings

## Uncertainties

- [ ] Can we make this accurate enough to be useful without being noisy?
- [ ] Should this be blocking or just advisory?

## Notes

Keep it lightweight. Better to miss some cases than to create friction.
