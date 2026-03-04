---
name: backlog
description: Backlog workflow management - new, start, done commands for incremental delivery. Supports both admin (main branch) and contributor (feature branch) workflows.
---

# Backlog Workflow

Manage incremental delivery items following project conventions (docs/backlog/todo/, docs/backlog/in-progress/, docs/backlog/done/).

## Workflow Modes

### Admin Mode (Umans AI team)
- Create and start items on `main` branch for team visibility
- Push to `main` after each step
- Create feature branch after starting item

### Contributor Mode (external contributors)
- Create branch first (cannot push to `main`)
- All backlog operations happen on the feature branch
- Everything merges to `main` via PR

## Commands

### `/backlog new <name> [description] [--ui]`

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
3. **UI flag (`--ui`)**: If present, add to template:
   - `## UI Scenarios` section with:
     ```markdown
     ## UI Scenarios

     Location: `docs/backlog/ui-previews/{ID}-{name}/`

     | # | Scenario | Screenshot | Status |
     |---|----------|------------|--------|
     | 1 | [describe view state] | ⬜ | ⬜ |
     | 2 | [describe interaction state] | ⬜ | ⬜ |
     ```
   - Create empty folder: `docs/backlog/ui-previews/{ID}-{name}/`
4. **Commit based on workflow**:
   - **Admin mode** (on `main` branch):
     - `git add . && git commit -m "chore: add {name} 📋"`
     - `git push origin main`
   - **Contributor mode** (on feature branch):
     - `git add . && git commit -m "chore: add {name} 📋"`
     - No push (user will push with other commits)
5. **Remind**: "Remember: Shippable, Valuable, Testable, Simple, Validating ✓"

**Errors**:
- Uncommitted changes → "Error: Uncommitted changes. Commit or stash first."
- Duplicate name → "Error: Item '{name}' exists in todo/ ({ID}-{name}.md)"

---

### `/backlog start <id-or-name> [--with-branch]`

Move item from `todo/` to `in-progress/`:

1. **Resolve item**: Match `id-or-name` against items in `todo/` (partial OK if unique)
2. **Validate state**:
   - Clean working directory
3. **Move**: `git mv todo/{file} in-progress/{file}`
4. **Commit**: `git commit -m "chore: start {name} 🚀"`
5. **Push based on workflow**:
   - **Admin mode** (on `main`): `git push origin main`
   - **Contributor mode** (on feature branch): No push yet
6. **Branch (optional, admin mode only)**:
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
2. **Verify CI status**: Run `gh pr checks` and ensure all checks pass
   - **NEVER merge a PR with failing pipeline** - fix first, then proceed
3. User runs `/backlog done` from feature branch
4. Auto-detect item from `in-progress/` or use `id-or-name`
5. **UI validation** (if `## UI Scenarios` section exists):
   - Parse scenarios table from item markdown
   - Verify folder `docs/backlog/ui-previews/{ID}-{name}/` exists
   - For each scenario with status ⬜, check screenshot file exists:
     - Expected: `docs/backlog/ui-previews/{ID}-{name}/{NN}-{scenario-name}.png`
   - **Error if mismatch**: "Error: UI scenarios incomplete. Missing: 03-filter-dropdown.png. Run agent-browser to capture."
6. Move: `git mv in-progress/{file} done/{file}`
7. Commit: `git commit -m "chore: complete {name} ✅"`
8. Push: `git push origin {branch}`
9. Confirm: "✅ Item marked complete. Ready to merge with `gh pr merge --rebase`"

**Direct push workflow (docs/chores only):**
1. Must be on main branch
2. `id-or-name` required
3. Move item: `git mv in-progress/{file} done/{file}`
4. Commit: `git commit -m "chore: complete {name} ✅"`
5. Push: `git push origin main`

**With continuous retro** (`--retro` flag, optional):
- Prompts: "What was harder?" / "What to improve?"
- Creates `docs/backlog/todo/{ID}-retro-{topic}.md` if answers provided

**Errors**:
- Multiple items in progress without id → "Error: Multiple items. Use: /backlog done <id-or-name>"
- No match → "Error: No item matching '{term}' in in-progress/."
- Uncommitted changes → "Warning: Uncommitted changes. Commit or stash first."
- UI scenarios incomplete → "Error: UI scenarios incomplete. Missing: {list}. Capture screenshots and update markdown."

---

### `/backlog status`

Show backlog state:
- List items in `todo/`
- List items in `in-progress/` (mark current branch with `*>`)
- List last 5 items in `done/`

---

## Principles

1. **Dual workflow support** - Admins use main branch for visibility; contributors do everything on feature branch (cannot push to main)
2. **Same git operations** - Both modes use `git add`, `git mv`, `git commit` identically; only the branch differs
3. **Direct push for docs/chores (admins only)** - Simple changes stay on main, no branch needed
4. **Branches for code changes** - Use branches for anything needing preview/validation
5. **Ship criteria is a statement** - What must be true, not a checklist of constraints
6. **Done before merge** - `/backlog done` captures "ready to ship", merge follows
7. **Never merge red pipelines** - Always verify CI passes before merging. Red pipeline = fix first, merge never
8. **Docs with code** - Update all impacted documentation before completing item
9. **Continuous retro** - Capture learnings as improvement items (type: `retro`)

---

## UI Workflow (with `--ui` flag)

For items involving user interface changes, use `--ui` flag on `/backlog new`:

### Convention
- **Folder naming**: `docs/backlog/ui-previews/{ID}-{name}/`
- **Screenshot naming**: `{NN}-{scenario-name}.png` (01-, 02-, etc.)
- **Markdown embed**: `![Scenario description](./ui-previews/{ID}-{name}/01-scenario.png)`

### Example workflow

```bash
# 1. Create UI item
/backlog new filter-ui "Add genre filter to movie list" --ui

# 2. During implementation, capture screenshots
# Place in docs/backlog/ui-previews/00009-filter-ui/
# Name: 01-landing-no-filter.png, 02-dropdown-open.png, etc.

# 3. Update item markdown with embeds
# Change ⬜ to ✅ in status column

# 4. Complete validates screenshots exist
/backlog done
```

### Validation rules
- Screenshots must exist for all scenarios marked ✅
- Folder name must match item filename (minus .md)
- Screenshot numbering must be sequential (no gaps)

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
