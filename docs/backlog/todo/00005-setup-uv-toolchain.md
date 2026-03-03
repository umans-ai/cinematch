# Setup UV Toolchain

## Goal
Migrate backend dependency management from pip/requirements.txt to uv with pyproject.toml for reproducible, fast installs.

## Why
- **Speed**: uv is 10-100x faster than pip
- **Reproducibility**: uv.lock ensures exact versions across all environments
- **Modern standard**: pyproject.toml is the PEP 518 standard
- **Unified toolchain**: uv + ruff + mypy all in one tool
- **Agent experience**: `uv sync` just works, no guesswork about venvs

## Acceptance Criteria
- [ ] `pyproject.toml` with all dependencies
- [ ] `uv.lock` generated and committed
- [ ] `justfile` updated to use `uv sync` and `uv run`
- [ ] ADR created explaining the choice
- [ ] CLAUDE.md or skills updated for discoverability
- [ ] Old `requirements.txt` removed

## Test Plan
- [ ] `uv sync` works in fresh clone
- [ ] `just backend-dev` starts server
- [ ] `just check` passes
- [ ] CI still works (or updated)

## Notes
Don't break existing Docker setup - can coexist during transition.
