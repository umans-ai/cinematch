# Production VPC and PostgreSQL Migration

## Goal

Migrate production from legacy foundation VPC (SQLite) to per-environment VPC architecture with PostgreSQL, achieving:

- **Uniform architecture**: All environments (production, previews, staging) use identical infrastructure patterns
- **Zero legacy code**: Remove conditional logic for "foundation VPC" vs "per-environment VPC"
- **PostgreSQL everywhere**: SQLite completely eliminated from all environments
- **Automatic migrations**: Database migrations run automatically on deployment
- **Zero data loss**: Seamless migration of existing production data
- **Verified correctness**: Characterization tests prove functional equivalence before/after

## Motivation

Currently, production is a "special snowflake":

| Aspect | Production | Previews | Problem |
|--------|-----------|----------|---------|
| VPC | `00-foundation/vpc.tf` (shared) | `01-service/vpc.tf` (per-env) | Architecture divergence |
| Database | SQLite on EFS | PostgreSQL RDS | Different behavior, no concurrency |
| Code paths | `use_foundation_vpc = true` | `use_foundation_vpc = false` | Conditional complexity |

This violates our principle of **Répétabilité** (reproducibility). A preview is NOT an exact replica of production, leading to:
- "Works in preview, fails in prod" scenarios
- Untestable database migration paths
- Operational complexity (two ways to do everything)

## Success Criteria

- [ ] Production runs on `aws_vpc.cinematch` in `01-service` (not foundation VPC)
- [ ] Production uses PostgreSQL RDS (not SQLite)
- [ ] All production data migrated without loss
- [ ] `use_foundation_vpc` logic completely removed from codebase
- [ ] `00-foundation/vpc.tf` destroyed (only ECR, Route53, ACM remain)
- [ ] Characterization tests pass before and after migration
- [ ] Automated database migrations on deployment
- [ ] Rollback plan tested and documented

## Implementation Plan

### Phase 0: Preparation and Characterization Testing

#### 0.1 Create characterization tests with Playwright

Before touching infrastructure, establish baseline behavior:

```python
# tests/characterization/test_production_e2e.py
# These tests run against the LIVE production environment

"""
Characterization tests document current production behavior.
These are NOT acceptance tests - they capture "what is", not "what should be".
Any change in these tests after migration indicates a behavioral difference.
"""

import pytest
from playwright.sync_api import Page, expect

PRODUCTION_URL = "https://demo.cinematch.umans.ai"

class TestRoomLifecycle:
    """Characterization: Room creation and joining workflow"""

    def test_homepage_loads(self, page: Page):
        page.goto(PRODUCTION_URL)
        expect(page).to_have_title(/CineMatch/)
        expect(page.locator("text=Swipe-based movie picker")).to_be_visible()

    def test_create_room_flow(self, page: Page):
        """Capture: Room creation generates code, shows waiting screen"""
        page.goto(PRODUCTION_URL)
        page.click("text=Create Room")

        # Characterization: Room code format (4 digits? 6 alphanumeric?)
        room_code = page.locator("[data-testid='room-code']").inner_text()
        assert len(room_code) > 0  # Document actual format

        # Characterization: Waiting screen shows participant count
        expect(page.locator("text=Waiting for partner")).to_be_visible()

    def test_join_room_flow(self, page: Page):
        """Capture: Joining with code pairs participants"""
        # Create room in one context
        page.goto(PRODUCTION_URL)
        page.click("text=Create Room")
        room_code = page.locator("[data-testid='room-code']").inner_text()

        # Join from second context (incognito)
        # Characterization: What happens when 2nd participant joins?
        # - Both see movie swiping immediately?
        # - Any intermediate state?

    def test_voting_flow(self, page: Page):
        """Capture: Swipe interactions and match detection"""
        # Full flow: create room, join, swipe on movies
        # Characterization: Match notification behavior
        # Characterization: Vote persistence on refresh

class TestDataPersistence:
    """Characterization: Data survives page refreshes and sessions"""

    def test_votes_persist_after_refresh(self, page: Page):
        """Critical: SQLite vs PostgreSQL must behave identically"""
        pass

    def test_room_exists_after_creator_leaves(self, page: Page):
        """Characterization: Room lifecycle when participants disconnect"""
        pass

class TestAPIContracts:
    """Characterization: API response shapes"""

    def test_health_endpoint(self, api_context):
        """Capture: /health response format"""
        response = api_context.get(f"{PRODUCTION_URL}/health")
        assert response.status == 200
        body = response.json()
        # Document actual structure (may differ from docs)
        assert "status" in body

    def test_create_room_api(self, api_context):
        """Capture: POST /api/rooms response shape"""
        pass

    def test_get_votes_api(self, api_context):
        """Capture: GET /api/rooms/{code}/votes format"""
        pass
```

**Execution:**
```bash
# Run against production BEFORE migration
pytest tests/characterization/ -v --base-url=https://demo.cinematch.umans.ai
# Save results as baseline
pytest tests/characterization/ -v --base-url=https://demo.cinematch.umans.ai --json-report > characterization/baseline.json
```

#### 0.2 Export production data snapshot

```bash
# Create backup of current SQLite database
aws ecs execute-command \
  --cluster cinematch-production \
  --task <task-id> \
  --container backend \
  --command "sh -c 'sqlite3 /app/data/cinematch.db .dump > /tmp/backup-$(date +%Y%m%d).sql'"

# Copy to S3 for safekeeping
aws s3 cp s3://cinematch-backups/production/pre-migration/
```

### Phase 1: Dual-Path Infrastructure (Temporary)

Create temporary variable to support blue-green deployment:

```hcl
# operations/01-service/variables.tf
variable "create_new_vpc" {
  description = "Temporary: Create new VPC for production migration"
  type        = bool
  default     = false
}
```

```hcl
# operations/01-service/vpc.tf (temporary state)
locals {
  # During migration: can override for production
  use_foundation_vpc = terraform.workspace == "production" && !var.create_new_vpc
}
```

Apply with `create_new_vpc=true` to create parallel infrastructure:

```bash
cd operations/01-service
terraform workspace select production
terraform apply -var="create_new_vpc=true" -var="image_tag=<sha>"
```

**Created resources (green environment):**
- `aws_vpc.cinematch` (new, CIDR 10.x.0.0/16)
- `aws_subnet.private[*]` (for RDS)
- `aws_db_instance.cinematch` (PostgreSQL)
- New ALB (not yet receiving traffic)

**Unchanged (blue environment):**
- ECS services still on foundation VPC
- Route53 still pointing to old ALB
- SQLite still active

### Phase 2: Data Migration

#### 2.1 Prepare migration container

```bash
# Start a one-off task with the new image but migration command
aws ecs run-task \
  --cluster cinematch-production \
  --launch-type FARGATE \
  --task-definition cinematch-backend-production:<new-revision> \
  --network-configuration "awsvpcConfiguration={subnets=[<new-private-subnet>],securityGroups=[<new-rds-sg>]}" \
  --overrides '{
    "containerOverrides": [{
      "name": "backend",
      "command": ["python", "-m", "scripts.migrate_sqlite_to_postgres"]
    }]
  }'
```

#### 2.2 Migration script

```python
# backend/scripts/migrate_sqlite_to_postgres.py
"""One-time migration from SQLite to PostgreSQL."""

import sqlite3
import psycopg
import os

def migrate():
    # Connect to SQLite source
    sqlite_conn = sqlite3.connect('/tmp/source.db')
    sqlite_cursor = sqlite_conn.cursor()

    # Connect to PostgreSQL target
    pg_conn = psycopg.connect(os.environ['DATABASE_URL'])
    pg_cursor = pg_conn.cursor()

    # Migrate tables in dependency order
    tables = ['movies', 'rooms', 'participants', 'votes']
    for table in tables:
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        rows = sqlite_cursor.fetchall()
        for row in rows:
            pg_cursor.execute(f"INSERT INTO {table} VALUES (...)", row)

    pg_conn.commit()

    # Verify row counts match
    for table in tables:
        sqlite_count = sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        pg_count = pg_cursor.fetchone()[0]
        assert sqlite_count == pg_count, f"Count mismatch for {table}"

if __name__ == "__main__":
    migrate()
```

### Phase 3: Blue-Green Cutover

Switch Route53 to new ALB:

```hcl
resource "aws_route53_record" "cinematch" {
  alias {
    name = aws_lb.cinematch.dns_name  # NEW: was foundation ALB
  }
}
```

### Phase 4: Cleanup

- Remove `create_new_vpc` variable
- Destroy foundation VPC
- Update documentation

## Continuous Database Migrations

With PostgreSQL, migrations run automatically on every deployment using an entrypoint script:

```bash
# docker-entrypoint.sh
#!/bin/bash
set -e
if [ "$RUN_MIGRATIONS" = "true" ]; then
    python -c "from app.migrations import run_migrations_with_lock; run_migrations_with_lock()"
fi
exec "$@"
```

### Migration Concurrency Safety

With multiple ECS tasks, concurrent migrations are serialized using PostgreSQL advisory locks:

```python
# backend/app/migrations.py
import alembic.config
from sqlalchemy import create_engine, text

MIGRATION_LOCK_ID = 54291

def run_migrations_with_lock(max_wait_seconds=300):
    """Run Alembic migrations with PostgreSQL advisory locking."""
    engine = create_engine(os.environ['DATABASE_URL'])

    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT pg_try_advisory_lock({MIGRATION_LOCK_ID})"))
        acquired = result.scalar()

        if not acquired:
            conn.execute(text(f"SELECT pg_advisory_lock({MIGRATION_LOCK_ID})"))

        try:
            alembic.config.main(argv=['upgrade', 'head'])
        finally:
            conn.execute(text(f"SELECT pg_advisory_unlock({MIGRATION_LOCK_ID})"))
```

**Scenarios Handled:**

| Scenario | Behavior |
|----------|----------|
| Single instance | Acquires lock immediately, runs migrations |
| Rolling deployment | First instance runs migrations, second waits |
| Crash during migration | Lock released on connection close, next instance retries |

## Architecture: Current vs Target

### Current State

```
PRODUCTION (workspace)
├── 00-foundation VPC (vpc-06a28ad9b2a6ae19e, CIDR 10.1.0.0/16)
│   ├── ECS Backend (SQLite: /app/data/cinematch.db)
│   ├── ECS Frontend
│   └── EFS with SQLite file
│
└── ALB (uses foundation subnets)
    └── Route53: demo.cinematch.umans.ai

PREVIEW (e.g., pr-56)
├── 01-service VPC (dynamically created, CIDR 10.x.0.0/16)
│   ├── ECS Backend (PostgreSQL)
│   ├── ECS Frontend
│   └── RDS PostgreSQL
│
└── ALB (uses preview VPC)
    └── Route53: demo-pr-56.cinematch.umans.ai
```

### Target State

```
PRODUCTION (workspace)
├── 01-service VPC (new, CIDR 10.x.0.0/16)
│   ├── ECS Backend (PostgreSQL RDS)
│   ├── ECS Frontend
│   └── RDS PostgreSQL (data migrated from SQLite)
│
└── ALB (uses new VPC)
    └── Route53: demo.cinematch.umans.ai

00-FOUNDATION (destroyed)
❌ VPC vpc-06a28ad9b2a6ae19e - DESTROYED
❌ SQLite on EFS - DESTROYED (backup kept 7d)
✅ ECR Repositories - KEPT
✅ Route53 Zone - KEPT
✅ ACM Certificate - KEPT

UNIFORM: Production == Previews (VPC per environment + PostgreSQL)
```

## No Preview Environment Needed

**No preview environment is required for this migration.**

Preview environments already use the target architecture (per-environment VPC + PostgreSQL). This migration is specifically about bringing **production** in line with what previews already do.

## Documentation Updates Required

- [ ] Update `docs/architecture/overview.md` - remove foundation VPC references
- [ ] Update `docs/architecture/decisions/004-vpc-per-environment.md` - mark as "Implemented"
- [ ] Update `CLAUDE.md` - remove SQLite references from configuration section
- [ ] Create ADR: "005-production-postgresql-migration" documenting the cutover strategy

## Rollback Plan

| Scenario | Action | Recovery Time |
|----------|--------|---------------|
| Pre-cutover data issues | Destroy new VPC, retry migration | 10 min |
| Post-cutover functional issues | Revert Route53 to foundation ALB | 1 min |
| Data corruption post-cutover | Restore SQLite from backup, revert DNS | 15 min |

**Critical:** Keep SQLite backup for 7 days post-migration.}