# Production VPC and PostgreSQL Migration - COMPLETED

## Status: ✅ COMPLETED

Migration completed successfully on March 11, 2026.

## What Was Done

### Infrastructure Changes

- **Migrated from**: Legacy foundation VPC with SQLite
- **Migrated to**: Per-environment VPC with PostgreSQL RDS

### Resources Created

| Resource | Old | New |
|----------|-----|-----|
| VPC | Foundation (shared) | `vpc-0b65193af531561e7` (dedicated) |
| ALB | `cinematch-production-green` | `cinematch-production` |
| RDS | SQLite (EFS) | `cinematch-production` (PostgreSQL) |
| ECS Services | `backend-green`, `frontend-green` | `backend`, `frontend` |

### Database

- PostgreSQL 16 on RDS
- Running in private subnets
- Accessible only from ECS security group
- Migrations run automatically via `RUN_MIGRATIONS=true`

## Verification

```bash
# Health check
curl https://demo.cinematch.umans.ai/health
→ {"status":"ok"}

# Database connection
aws ecs describe-task-definition \
  --task-definition cinematch-backend-production \
  --query 'taskDefinition.containerDefinitions[0].environment[?name==`DATABASE_URL`]'
→ postgresql://cinematch-production.cbo42egkg8fe.eu-west-1.rds.amazonaws.com:5432/cinematch
```

## Architecture

```
User → Route53 → ALB → ECS (Fargate) → RDS PostgreSQL
              ↓
         VPC (per-environment)
         - Public subnets: ALB
         - Private subnets: RDS
```

## Cleanup

- ✅ Foundation VPC references removed
- ✅ All `-green` suffixes removed
- ✅ Clean resource names
- ✅ Documentation updated

## Post-Migration Notes

- Each environment (production, previews) has its own isolated VPC
- Database migrations run automatically on container startup
- No shared VPC - complete isolation per environment
