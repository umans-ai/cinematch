# Pre-commit Hooks

## Goal
Add git hooks to enforce code quality and prevent pushing failing code, supporting trunk-based development workflow.

## User Value
- Developers catch issues before committing, reducing CI failures
- Main branch stays clean with all commits being potentially shippable
- Faster feedback loop (local checks before remote CI)

## Requirements
- Run full checks (lint + typecheck + tests) before commits
- Prevent pushing code that doesn't pass checks
- Use simple bash scripts (no additional frameworks)
- Easy installation with single command
- Well-documented in README and CLAUDE.md

## Implementation Plan

### Phase 1: Core Hooks
- Create `.githooks/` directory
- Implement `pre-commit` hook that runs `just check`
- Implement `pre-push` hook as safety net
- Make hooks executable

**Tests:**
- [ ] pre-commit hook runs and passes on clean code
- [ ] pre-commit hook fails on syntax errors
- [ ] pre-commit hook fails on test failures
- [ ] pre-push hook runs as safety net

### Phase 2: Installation Script
- Create `scripts/install-hooks.sh`
- Configure git to use `.githooks` directory
- Make hooks executable
- Display helpful messages

**Tests:**
- [ ] Installation script configures git correctly
- [ ] `git config core.hooksPath` shows `.githooks`
- [ ] Hooks are executable after installation

### Phase 3: Documentation
- Update `README.md` with setup instructions
- Update `CLAUDE.md` with hooks workflow
- Update `docs/conventions.md` with hooks usage
- Verify `.gitignore` excludes `.git/hooks/`

**Tests:**
- [ ] README explains hooks clearly
- [ ] CLAUDE.md documents hooks in workflow
- [ ] conventions.md includes hooks section
- [ ] .gitignore properly configured

## Verification
1. Install hooks: `./scripts/install-hooks.sh`
2. Create breaking change and attempt commit - should fail
3. Fix and commit - should pass
4. Test bypass with `--no-verify`
5. Test pre-push hook

## Assumptions to Validate
- `just check` runs fast enough for pre-commit (~30-60s acceptable)
- Team members can install hooks manually (one-time)
- Bash scripts work across macOS/Linux environments

## Success Criteria
- Pre-commit hook blocks commits with failing checks
- Installation is single command
- Documentation is clear and complete
- CI still runs as final gate
