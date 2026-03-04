# Auto-destroy Preview on PR Close

## Problem

Currently, when a PR is closed (merged or abandoned), the preview environment is **not** automatically destroyed. This leads to:

- **Orphaned AWS resources** running and incurring costs
- **Manual cleanup required** (like we just did for pr-2 and pr-4)
- **Terraform state locks** when multiple deploys run concurrently

## Goal

Automatically trigger the `destroy-preview` job when a PR is closed, ensuring all preview resources are cleaned up immediately.

## Current State

The workflow has a `destroy-preview` job that only runs on:
```yaml
if: github.event_name == 'pull_request' && github.event.action == 'closed'
```

But since we now use **path filters** to skip CI for docs changes, the workflow may not trigger at all when closing a PR with only docs changes. Also, the workflow needs to handle both:
1. PR closed (merged or not)
2. Manual workflow dispatch for cleanup

## Proposed Solution

### Option A: Always trigger on PR close
Remove path filters for `pull_request.closed` events to ensure destroy always runs:

```yaml
on:
  pull_request:
    types: [closed]  # Always run destroy on close
    paths-ignore: []  # Override: no path filters for close
```

### Option B: Separate destroy workflow
Create a dedicated `destroy-preview.yml` workflow that only triggers on PR close:

```yaml
name: Destroy Preview
on:
  pull_request:
    types: [closed]
jobs:
  destroy:
    if: github.event.pull_request.merged == true || github.event.pull_request.state == 'closed'
    steps:
      - Destroy logic from current ci-cd.yml
```

### Option C: Cleanup scheduled job
Add a scheduled workflow that destroys stale previews (workspaces without open PRs):

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2am
```

## Recommendation

**Option A** is simplest - modify the existing workflow to ensure `destroy-preview` always runs on PR close, regardless of path changes. This keeps all logic in one place.

## Acceptance Criteria

- [ ] When a PR is closed (merged or not), the preview environment is destroyed
- [ ] The `destroy-preview` job runs even if the PR only had docs changes
- [ ] The workspace is deleted from Terraform state
- [ ] No orphaned AWS resources remain

## Test Plan

- [ ] Create a test PR
- [ ] Verify preview deploys
- [ ] Close the PR without merging
- [ ] Verify destroy job runs
- [ ] Verify workspace is deleted
- [ ] Verify AWS resources are gone

## Notes

Related to the CI/CD safety improvements we just made. Should be implemented before the next batch of PRs to avoid manual cleanup.
