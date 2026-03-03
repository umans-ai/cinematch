# ADR 006: UV Toolchain for Python Dependency Management

## Status
Accepted

## Context
The backend initially used pip with `requirements.txt` for dependency management. This approach has several friction points:

1. **Slow installs**: pip installs are slow, especially in CI and fresh clones
2. **No lock file**: `requirements.txt` pins top-level versions but not transitive dependencies, leading to "works on my machine" issues
3. **venv management**: Each developer manages their own virtual environment manually
4. **Agent friction**: Claude Code agents need to guess about venvs, pip vs pip3, and activation commands
5. **Separate tools**: linting (ruff), type checking (mypy), and package management (pip) are separate tools with separate configs

## Decision
Adopt the **Astral toolchain** (uv, ruff, ty) for Python development. Fast, reliable feedback loops for **both human contributors and AI agents**.

### Key aspects:
- **`pyproject.toml`**: Single source of truth, PEP 518 standard
- **`uv.lock`**: Reproducible lockfile (transitive dependencies locked)
- **`uv sync`**: One command → venv created + exact versions installed
- **`uv run`**: Execute in project environment without activation
- **ty**: Astral's Rust-based type checker (10-100x faster than mypy)

### Why Astral?

| Tool | Replaces | Speed | Benefit |
|------|----------|-------|---------|
| uv | pip + venv | 10-100x | Instant env setup |
| ruff | flake8 + black + isort | 10-100x | One tool, unified config |
| ty | mypy/pyright | 10-100x | Fast type feedback |

**Unified mental model**: Same CLI patterns, same config approach. Agents and humans learn once, apply everywhere.

**Reliable feedback**: `uv sync` → identical environment everywhere. No "works on my machine".

## Consequences

### Positive
- **10-100x faster installs**: uv is written in Rust, parallelizes downloads
- **Reproducible builds**: `uv.lock` ensures identical environments everywhere
- **Simpler agent workflow**: `uv sync` then `uv run` - no guesswork
- **Single file for config**: `pyproject.toml` replaces `setup.py`, `requirements.txt`, `requirements-dev.txt`
- **Standards compliant**: Uses official Python packaging standards

### Negative
- **New tool to learn**: Team needs to learn uv commands
- **Migration effort**: Need to convert existing requirements.txt
- **Lock file churn**: Dependabot/renovate may need configuration updates

## Migration Path

### For existing clones:
```bash
cd backend
# Remove old venv (optional but clean)
rm -rf .venv
# Sync with new setup
uv sync
```

### For agents/CI:
```bash
cd backend
uv sync  # Creates venv, installs from uv.lock
uv run pytest  # Run tests in isolated environment
```

## References
- [UV Documentation](https://docs.astral.sh/uv/)
- [PEP 518 - pyproject.toml](https://peps.python.org/pep-0518/)
- [Claude Code: Working with UV](./docs/conventions.md#uv-toolchain)
