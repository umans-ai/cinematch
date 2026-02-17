---
name: pr-merge
description: Merge PR with rebase workflow as required by CLAUDE.md
---

# PR Merge Workflow

Merge feature branches following the rebase workflow from CLAUDE.md.

## Usage

### `/pr-merge [pr-number]`

Without PR number: uses current branch, infers PR from `gh pr view`.
With PR number: uses specified PR.

## Workflow

1. **Verify clean state**
   - Must be on feature branch
   - Working directory clean

2. **Fetch latest**
   - `git fetch origin`

3. **Rebase**
   - `git rebase origin/main`
   - If conflicts: stop, instruct to resolve, then re-run

4. **Re-run checks**
   - `just check` (or equivalent)
   - Must pass before merge

5. **Merge**
   - `gh pr merge --rebase`
   - Verify merge succeeded

6. **Cleanup (optional)**
   - `git checkout main`
   - `git pull origin main`
   - `git branch -d <feature-branch>`

## Errors

- On main branch → "Error: Must be on feature branch. Current: main"
- Uncommitted changes → "Error: Uncommitted changes. Commit or stash first."
- Rebase conflicts → "Conflicts detected. Resolve: 1) fix files, 2) git add ., 3) git rebase --continue, 4) re-run /pr-merge"
- Checks fail → "Checks failed. Fix before merge."

## Success

"✅ Merged with rebase. Cleanup done."
