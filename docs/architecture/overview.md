# CineMatch Architecture Overview

## Project Goal
Tinder-style movie picker for couples. Stop scrolling, start watching.

## Stack
- **Frontend**: Next.js 14 + shadcn/ui + Tailwind
- **Backend**: FastAPI + SQLite (MVP) → PostgreSQL (increment 2)
- **Infrastructure**: AWS ECS Fargate + ALB + Route53
- **CI/CD**: GitHub Actions + Terraform Workspaces

## Repository Structure

```
.
├── backend/           # FastAPI application
│   ├── app/          # Main application code
│   └── tests/        # Test suite
├── frontend/          # Next.js application
│   ├── app/          # App router pages
│   └── components/   # React components
├── operations/        # Terraform infrastructure
│   ├── 00-foundation/   # Shared resources (VPC, ECS, ECR, cert)
│   └── 01-service/      # Per-environment resources (ALB, services)
├── docs/
│   ├── architecture/decisions/   # ADRs
│   └── backlog/                  # Increment tracking
└── .github/workflows/   # CI/CD pipelines
```

## Infrastructure Layers

### 00-foundation (One-time setup)
Applied manually, contains resources shared across ALL environments:

| File | Purpose |
|------|---------|
| `vpc.tf` | VPC (10.1.0.0/16), subnets, IGW, route tables |
| `ecs.tf` | ECS Cluster "cinematch" (shared) |
| `ecr.tf` | ECR repositories for backend/frontend images |
| `cert.tf` | ACM certificate for *.cinematch.umans.ai |

**NOT deployed by CI/CD** - Run once manually.

### 01-service (Per-environment)
Applied by CI/CD for each environment (production, pr-123, etc.):

| File | Purpose |
|------|---------|
| `alb.tf` | Application Load Balancer |
| `ecs-services.tf` | ECS services and task definitions |
| `security-groups.tf` | Security groups for ALB and ECS |
| `route53.tf` | DNS records per workspace |
| `iam.tf` | IAM roles per workspace |
| `logs.tf` | CloudWatch log groups |

**Deployed by CI/CD** - Automatically on push/PR.

## Environment Isolation

Each environment is a Terraform workspace:

| Workspace | Domain | Purpose |
|-----------|--------|---------|
| `production` | demo.cinematch.umans.ai | Live site |
| `pr-123` | demo-pr-123.cinematch.umans.ai | Preview for PR #123 |

Isolation guarantees:
- ✅ Dedicated ALB per environment
- ✅ Dedicated security groups per environment
- ✅ Separate ECS services per environment
- ✅ Shared: VPC, ECS Cluster, ECR, ACM certificate

## Isolation from llm-gateway

CineMatch is COMPLETELY ISOLATED from llm-gateway:

| Resource | CineMatch | llm-gateway |
|----------|-----------|-------------|
| VPC | 10.1.0.0/16 | 10.0.0.0/16 |
| ECS Cluster | cinematch | llm-gateway |
| ALB | Separate | Separate |
| Security Groups | cinematch-* | llm-gateway-* |
| IAM Roles | cinematch-* | llm-gateway-* |

Only shared: Route53 zone (umans.ai) - READ-ONLY reference.

## Data Flow

```
User → Route53 (cinematch.umans.ai) → ALB → ECS Service → Container
```

1. DNS resolves to ALB
2. ALB routes to target groups (frontend:3000, backend:8000)
3. Frontend talks to backend via `/api/*` routes (ALB routing)
4. Backend uses SQLite (MVP) or PostgreSQL (increment 2)

## Deployment Flow

### Production (push to main)
```
1. Run checks (lint, test, typecheck)
2. Build Docker images
3. Push to ECR with SHA tag
4. terraform workspace select production
5. terraform apply
```

### Preview (pull request)
```
1. Run checks
2. Build Docker images
3. Push to ECR with pr-N tag
4. terraform workspace new pr-N
5. terraform apply
6. Comment PR with URL
```

### Cleanup (PR closed)
```
1. terraform workspace select pr-N
2. terraform destroy
3. terraform workspace delete pr-N
```

## Increment Planning

See `docs/backlog/` for planned increments:
1. MVP with static movies (IN PROGRESS)
2. PostgreSQL migration
3. TMDB API integration
4. User accounts

## Key Decisions

- **SQLite for MVP**: Speed of development, migrate to PostgreSQL later
- **Workspace-based environments**: Simple, effective isolation
- **Shared ECS Cluster**: Cost-effective, still isolated services
- **Separate VPC**: Maximum isolation from llm-gateway
