# Conventions

## Development Workflow

### Principles

- **Trunk-based development** with short-lived feature branches
- **Each commit is a release candidate** - main must always be deployable
- **Backlog on git** - work items tracked in `docs/backlog/`
- **Feedback-driven** - Use fast, trustworthy feedback to guide changes

### Backlog Structure

```
docs/backlog/
├── todo/         # Items to do (XXXXX-name.md)
├── in-progress/  # Currently being worked on
└── done/         # Completed increments
```

Files are named with 5-digit stable ID: `00001-mvp-static-movies.md`

The number is a **stable identifier**, not priority. Prioritization happens when picking the next item to work on, not through renaming files.

### Starting Work on an Increment

```bash
# 1. Move item to in-progress
git mv docs/backlog/todo/00001-mvp-static-movies.md docs/backlog/in-progress/

# 2. Commit to main (this is the real backlog state)
git commit -m "chore: start mvp-static-movies 🚀"

# 3. Push main immediately so others see it in-progress
git push origin main

# 4. Verify origin/main has the start commit
git fetch origin
git log --oneline origin/main -n 1

# 5. Create feature branch
git checkout -b mvp-static-movies
```

### Completing an Increment

```bash
# 1. On feature branch, move item to done
git mv docs/backlog/in-progress/00001-mvp-static-movies.md docs/backlog/done/

# 2. Commit
git commit -m "chore: complete mvp-static-movies ✅"

# 3. Switch to main and fast-forward merge
git checkout main
git merge --ff-only mvp-static-movies

# 4. Delete feature branch
git branch -d mvp-static-movies
```

### Merge Strategy: PR vs Direct Push

We use a hybrid approach based on risk and complexity:

| Approach | When to Use | Merge Mode |
|----------|-------------|------------|
| **Direct push** | Documentation, chores (backlog moves, ADRs), single-file fixes with passing tests | Fast-forward (`git merge --ff-only`) |
| **PR required** | Infra changes (Terraform, CI config), new features, complex refactors | **Always rebase** (`gh pr merge --rebase`) |

For **PR required** changes, always rebase and verify before merge:

```bash
git fetch origin
git rebase origin/main
just check
# verify preview on rebased head
gh pr merge --rebase
```

**Rationale:**
- PRs provide CI validation before merge for risky changes
- Direct push reduces friction for trivial, safe changes
- Rebase merge keeps a linear history for PRs
- CI on main still catches issues with direct pushes

### Implementation Workflow

#### Plan Before Code

The increment file in `docs/backlog/in-progress/` is the planning document. Before coding:

1. **If no plan exists** - Research and add an "Implementation Plan" section with phases and test lists
2. **If plan exists** - Review the test list for the current phase
3. **Resolve uncertainties** - Web search, read existing code, ask questions
4. **Only then** - Start writing code

Never jump into implementation without a plan in the increment file.

#### TDD Cycle

Each phase has a test list in the increment file. Follow red-green-refactor:

**0. Test List (planning)**

Create test list BEFORE implementation:

```markdown
## Implementation Plan
- [ ] test create room generates 4-digit code
- [ ] test join room adds participant
- [ ] test match found when both like same movie
```

**1. Red** - Write a failing test from the list

**2. Green** - Write minimal code to make it pass

**3. Refactor** - Clean up while keeping tests green

**4. Mark done** - Check off the test: `- [x]`

Run tests frequently: `just test` or `just test tests/specific_test.py -v`

## Commit Messages

Conventional commits with emoji at the end:

```
<type>: <description> <emoji>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`

Emojis:
- feat: ✨
- fix: 🐛
- docs: 📝
- style: 💄
- refactor: ♻️
- perf: ⚡
- test: ✅
- build: 📦
- ci: 🔧
- chore: 🧹

**Rule:** Never add `Co-Authored-By:` to commit messages.

## Just Targets

```bash
just check      # Run all checks (lint + typecheck + test)
just test       # Run tests only
just lint       # Run linters
just fmt        # Format code
just typecheck  # Run type checkers
just dev        # Start dev environment (docker-compose)

# Backend-specific
cd backend && just test

# Frontend-specific
cd frontend && just dev
```

Run `just -l` to see all available commands.

Keep `justfile` targets thin (one-liners). Complex logic goes in scripts.

## Fail Fast Principle

**CI must use just targets** - never duplicate check logic in `.github/workflows/`.

The order matters for fast feedback:
1. **Syntax** (fastest)
2. **Static analysis**
3. **Unit tests**
4. **Integration tests**

Always run `just check` before committing.

## Architecture Decision Records

ADRs live in `docs/architecture/decisions/` with sequential numbering: `NNN-title.md`

Create an ADR when making decisions that:
- Affect system structure
- Constrain future choices
- Are non-obvious or debated

Commit ADRs alongside implementation, not separately.

## Adding Backlog Items

Each increment must be:
- **Shippable** - can be deployed independently
- **Valuable** - delivers user or business value
- **Testable** - has clear verification criteria
- **Simple** - small enough to complete in one branch
- **Validating** - has explicit assumptions to confirm

Use next available 5-digit ID: `XXXXX-name.md`

## Operational CLI Defaults

- Assume `gh` and `aws` CLIs are available by default
- Use `gh` first for PR/CI checks, logs, and merges
- Use `aws` first for infra/runtime checks (ECS, logs)
- Do not ask if these CLIs can be used; run them directly
- If auth fails, run `gh auth status` or `aws sts get-caller-identity`, then report next login step
