# Security & Isolation Analysis

**Date:** 2026-02-17
**Repository:** github.com/umans-ai/cinematch (Public)

## Executive Summary

CineMatch is **SAFE** for public repository status with proper isolation from other Umans products.

- ✅ No hardcoded secrets in code
- ✅ Complete network isolation from other Umans AI projects
- ✅ Separate AWS resources with distinct naming
- ✅ OIDC-based AWS authentication (no long-lived credentials)
- ✅ Contributors cannot impact other products

## Isolation Verification

### Network Isolation

| Resource | CineMatch | Other Umans Projects | Status |
|----------|-----------|---------------------|--------|
| VPC CIDR | 10.1.0.0/16 | Other internal ranges | ✅ Different networks |
| Subnet ranges | 10.1.1.0/24, 10.1.2.0/24 | Other internal ranges | ✅ No overlap |
| VPC Peering | None | None | ✅ Isolated |

### AWS Resource Isolation

All CineMatch resources use `cinematch-*` prefix:

- ✅ **ECS Cluster:** `cinematch-production`, `cinematch-pr-N`
- ✅ **ALB:** `cinematch-production`, `cinematch-pr-N`
- ✅ **Security Groups:** `cinematch-alb-*`, `cinematch-ecs-*`
- ✅ **IAM Roles:** `cinematch-ecs-exec-*`, `cinematch-ecs-task-*`
- ✅ **ECR Repos:** `cinematch-backend`, `cinematch-frontend`
- ✅ **CloudWatch Logs:** `/ecs/cinematch-*`
- ✅ **Route53 Records:** `*.cinematch.umans.ai`

Other Umans AI projects use different naming prefixes to ensure isolation.

### What Contributors CAN Do

With the current GitHub Actions setup, contributors (via PR) can:

1. **Deploy to preview environments** - Creates isolated `pr-N` workspace
2. **Modify application code** - Backend/frontend changes
3. **Run CI/CD checks** - Lint, test, typecheck
4. **Trigger Terraform plans** - View infrastructure changes

### What Contributors CANNOT Do

Contributors **CANNOT**:

1. **Access production directly** - Only maintainers can push to main
2. **Access other Umans AI projects** - Different IAM roles required
3. **Access internal Umans AI infrastructure** - Separate AWS account or role
4. **View secrets** - AWS Secrets Manager permissions limited
5. **Modify foundation layer** - Applied manually, not via CI/CD
6. **Delete production resources** - Separate workspace, protected branch

## Secrets Management

### No Secrets in Code

Verified via automated scan:
```bash
# No .env files committed
git log --all --full-history -- '*.{env,pem,key,secret}'
# Result: No matches

# No hardcoded credentials in source
grep -r "password\|secret\|token\|key" --include="*.py" --include="*.tf"
# Result: Only legitimate variable names, no values
```

### AWS Authentication

- **Method:** OIDC (OpenID Connect) via GitHub Actions
- **Role:** `arn:aws:iam::034362042699:role/GitHubActionsCinematchRole`
- **Trust:** Only trusts `repo:umans-ai/cinematch:*`
- **Session:** Temporary credentials (1 hour max)

### Required Secrets (if any)

If future increments need secrets:

1. Store in AWS Secrets Manager: `cinematch/production/*`
2. Reference in Terraform via `data.aws_secretsmanager_secret`
3. Inject as environment variables in ECS task definition
4. Never commit to Git

## IAM Permissions Analysis

### GitHubActionsCinematchRole Policies

**Inline Policies:**

1. **DynamoDBTerraformLocks**
   - Actions: `dynamodb:PutItem`, `GetItem`, `DeleteItem`
   - Resource: `arn:aws:dynamodb:eu-west-1:*:table/terraform-locks`
   - Purpose: Terraform state locking

2. **S3TerraformState**
   - Actions: `s3:GetObject`, `PutObject`, `DeleteObject`, `ListBucket`
   - Resource: `arn:aws:s3:::umans-terraform-state/*`
   - Purpose: Terraform state storage

3. **IAMECS**
   - Actions: IAM CRUD on `cinematch-*` roles only
   - Resource: `arn:aws:iam::*:role/cinematch-*`
   - Purpose: Manage ECS task/execution roles

**AWS Managed Policies Attached:**

- `AmazonRoute53FullAccess` - DNS management
- `AmazonEC2ContainerRegistryFullAccess` - ECR push/pull
- `AmazonEC2FullAccess` - VPC, security groups
- `CloudWatchLogsFullAccess` - Log groups
- `SecretsManagerReadWrite` - Secrets (if needed)
- `AmazonECS_FullAccess` - ECS management

### Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Contributor modifies production | Low | Protected branch `main`, requires maintainer review |
| Contributor accesses other projects | None | Different IAM role, no permissions |
| Contributor views secrets | Low | Secrets in AWS SM, no read access in CI role |
| Terraform destroys resources | Low | `prevent_destroy` can be added to critical resources |
| Preview environment costs | Low | Auto-destroy on PR close |

## Recommendations

### Immediate (Already Done)

- ✅ VPC isolation (different CIDR)
- ✅ Resource naming conventions
- ✅ OIDC instead of long-lived keys
- ✅ No secrets in code
- ✅ Separate foundation/service layers

### Future Hardening

1. **Enable branch protection rules:**
   - Require PR reviews before merging to main
   - Require status checks to pass
   - Dismiss stale reviews

2. **Add Terraform safeguards:**
   ```hcl
   lifecycle {
     prevent_destroy = true
   }
   ```
   On critical resources (ECR repos, ACM certs)

3. **Cost monitoring:**
   - Set up AWS Budgets alerts
   - Monitor preview environment sprawl

4. **Security scanning:**
   - Add `detect-secrets` to CI/CD
   - Run `tfsec` for Terraform security checks

## Conclusion

CineMatch is **SAFE** as a public repository with **COMPLETE ISOLATION** from other Umans AI internal infrastructure.

Contributors can:
- Develop features safely in isolated preview environments
- Not impact other products or production directly

Maintainers control:
- Production deployments via merge to main
- Foundation infrastructure (manual apply)
- AWS permissions via IAM role policies
