---
name: backlog
description: Backlog workflow management - new, start, done commands for incremental delivery
---

# Backlog Workflow

Manage incremental delivery items following project conventions (docs/backlog/todo/, docs/backlog/in-progress/, docs/backlog/done/).

## Commands

### `/backlog new <name> [description]`

Create a new backlog item in `docs/backlog/todo/`:

1. **Find next ID**: Scan `todo/`, `in-progress/`, and `done/` for highest 5-digit ID, increment by 1
2. **Create file**: `docs/backlog/todo/{ID}-{name}.md` with template:
   ```markdown
   # {Name}

   ## Goal
   {description or "TODO: what we're trying to achieve"}

   ## Context
   TODO: background and constraints

   ## Ship Criteria
   TODO: what must be true to consider this complete?

   ## Uncertainties
   - [ ] TODO: what might we be wrong about?

   ## Implementation Plan

   ## Notes
   ```
3. **Commit to main**:
   - Must be on `main` branch with clean working directory
   - `git add . && git commit -m "chore: add {name} 📋"`
   - `git push origin main` (team visibility)
4. **Remind**: "Remember: Shippable, Valuable, Testable, Simple, Validating ✓"

**Errors**:
- Not on main → "Error: Must be on main. Current: {branch}. Run: git checkout main"
- Uncommitted changes → "Error: Uncommitted changes. Commit or stash first."
- Duplicate name → "Error: Item '{name}' exists in todo/ ({ID}-{name}.md)"

---

### `/backlog start <id-or-name> [--with-branch]`

Move item from `todo/` to `in-progress/`:

1. **Resolve item**: Match `id-or-name` against items in `todo/` (partial OK if unique)
2. **Validate state**:
   - Must be on `main` branch (error if on feature branch: "Error: Already on '{branch}'. Checkout main first.")
   - Clean working directory
3. **Move**: `git mv todo/{file} in-progress/{file}`
4. **Commit**: `git commit -m "chore: start {name} 🚀"`
5. **Push**: `git push origin main`
6. **Branch (optional)**:
   - Without `--with-branch`: Stay on main (direct push workflow)
   - With `--with-branch`: `git checkout -b {name}`

**Errors**:
- Not found → "Error: No match for '{term}' in todo/. Try: /backlog status"
- Multiple matches → "Error: Multiple matches: {list}. Use full ID."
- Branch exists → "Error: Branch '{name}' exists. Delete or choose different name."

---

### `/backlog done [id-or-name] [--retro]`

Complete an in-progress item. **Use AFTER verification, BEFORE merge**:

**PR workflow (after preview verified):**
1. PR created, pipeline passed, preview tested
2. User runs `/backlog done` from feature branch
3. Auto-detect item from `in-progress/` or use `id-or-name`
4. Switch to main, pull latest
5. Move: `git mv in-progress/{file} done/{file}`
6. Commit: `git commit -m "chore: complete {name} ✅"`
7. Push: `git push origin main`
8. Return to branch: `git checkout {branch}`
9. Confirm: "✅ Item marked complete. Ready to merge with `gh pr merge --rebase`"

**Direct push workflow (docs/chores):**
1. User on main branch
2. `id-or-name` required
3. Move item, commit, push
4. Then merge: `git merge --ff-only {branch}`

**With continuous retro** (`--retro` flag, optional):
- Prompts: "What was harder?" / "What to improve?"
- Creates `docs/backlog/todo/XXXXX-retro-{topic}.md` if answers provided

**Errors**:
- Multiple items in progress without id → "Error: Multiple items. Use: /backlog done <id-or-name>"
- No match → "Error: No item matching '{term}' in in-progress/."
- Uncommitted changes → "Warning: Uncommitted changes. Commit or stash first."

---

### `/backlog status`

Show backlog state:
- List items in `todo/`
- List items in `in-progress/` (mark current branch with `*>`)
- List last 5 items in `done/`

---

## Principles

1. **Every state change commits to main** - team visibility
2. **Direct push default** - stay on main, no branch needed
3. **Branches only for preview env** - use `--with-branch` for infra/arch changes needing validation
4. **Ship criteria is a statement** - what must be true, not a checklist of constraints
5. **Done before merge** - `/backlog done` captures "ready to ship", merge follows
6. **Docs with code** - update all impacted documentation before completing item
7. **Continuous retro** - capture learnings as improvement items (type: `retro`)

---

## Backlog Item Types

### Standard Items
Format: `XXXXX-name.md` (5-digit ID)

Used for features, fixes, refactors, etc.

### Retro/Improvement Items
Format: `XXXXX-retro-{topic}.md` or `XXXXX-improvement-{area}.md`

Created during `/backlog done --retro` to capture:
- Process improvements
- Documentation gaps discovered
- Tooling frustrations
- Architecture insights

These are **optional** and **non-blocking** - add them when there's something concrete to improve.
