# Fix Onboarding — Podman Machine Check

## Goal
Detect when the Podman machine is not started during onboarding and propose to start it, so integration tests pass without manual intervention.

## Context
The onboarding skill checks prerequisites (git, docker/podman, python, node) but does not verify that the Podman VM is actually running. If the machine is stopped, `docker-compose up` and integration tests that require a container runtime will fail silently or with a cryptic error, leaving the contributor stuck.

## Ship Criteria
- Onboarding detects whether the Podman machine is stopped
- Onboarding proposes to run `podman machine start` if needed
- Integration tests (`just check`) pass after the machine is started
- No regression when Docker (non-Podman) is used

## Uncertainties
- [ ] Is there a reliable cross-platform way to detect "Podman vs Docker" and check machine status?
- [ ] Should we auto-start silently or always ask the user first?

## Implementation Plan

### Phase 1 — Detection
- [ ] Add a step in Phase 2 (Prerequisites Check) to run `podman machine list` and detect stopped machines
- [ ] Distinguish Podman from Docker to avoid running podman commands on Docker setups

### Phase 2 — Recovery
- [ ] If a stopped machine is found, explain what it is and propose `podman machine start`
- [ ] After starting, re-check that `docker compose version` works before continuing

### Phase 3 — Tests
- [ ] Verify onboarding succeeds end-to-end with a stopped Podman machine
- [ ] Verify no regression with Docker

## Notes
The detection command: `podman machine list --format "{{.Name}} {{.LastUp}}"` — if output contains "Currently running" it's up, otherwise it needs to be started.
