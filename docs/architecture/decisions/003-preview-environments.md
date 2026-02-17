# ADR-003: Preview Environments with Terraform Workspaces

## Status
Accepted

## Context
We need to test changes (especially database migrations) before production deployment.

## Decision
Use **Terraform workspaces** for environment isolation:
- `default` workspace = production
- `preview-*` workspaces = temporary preview environments

## Implementation

### DNS
- Production: `demo.cinematch.umans.ai`
- Preview: `demo-pr-{N}.cinematch.umans.ai`

### Infrastructure per environment
- Separate ECS services
- Separate RDS database (or schema)
- Separate S3 buckets if needed
- Shared: Route53 zone, ACM certificates (wildcard)

### Database Strategy
- Each preview gets its own database instance (small t3.micro)
- Or use schema-per-preview on shared RDS (cheaper, more complex)
- **MVP**: Start with SQLite for speed, migrate to PostgreSQL in increment 2

### Cleanup
Preview environments destroyed when PR is merged/closed.

## Date
2025-02-17
