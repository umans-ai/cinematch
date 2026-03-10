# Production VPC and PostgreSQL Migration - FINAL CUTOVER

## Current Situation (Post-Recovery)

After the failed migration attempt on March 10, 2026, the production environment is in a transitional state:

- **Blue environment**: Effectively destroyed (no ALB, no ECS services running)
- **Foundation VPC**: Still exists but has no active services
- **Route53**: Currently points to non-existent ALB
- **Data**: SQLite database backup exists in EFS

## Simplified Cutover Strategy

Since there's no active "blue" environment to maintain, we will:

1. **Create green environment** as the new production
2. **Migrate data** from SQLite backup to PostgreSQL
3. **Update Route53** to point to new ALB
4. **Verify** everything works

## Execution Steps

### Step 1: Create Green Environment

```bash
cd operations/01-service
terraform workspace select production

# Create GREEN environment (this becomes production)
terraform apply -var="create_new_vpc=true" -var="image_tag=bf60f25816d6c30ad6b8dbcd0a6d179b43a8d490"
```

**Expected resources created:**
- VPC: `cinematch-production-green`
- ALB: `cinematch-production-green`
- ECS Services: `backend-green`, `frontend-green`
- RDS: `cinematch-production-green` (PostgreSQL)
- Security Groups, Subnets, IGW, etc.

### Step 2: Verify Green Environment Health

```bash
# Get new ALB DNS
green_alb=$(aws elbv2 describe-load-balancers \
  --names cinematch-production-green \
  --query 'LoadBalancers[0].DNSName' --output text)

# Test health endpoint
curl -k https://$green_alb/health

# Check ECS services
aws ecs describe-services \
  --cluster cinematch-production \
  --services backend-green frontend-green
```

### Step 3: Migrate Data from SQLite to PostgreSQL

```bash
# Run migration task
aws ecs run-task \
  --cluster cinematch-production \
  --launch-type FARGATE \
  --task-definition cinematch-backend-production:<revision> \
  --network-configuration "awsvpcConfiguration={subnets=[<private-subnet-ids>],securityGroups=[<rds-sg-id>]}" \
  --overrides '{
    "containerOverrides": [{
      "name": "backend",
      "command": ["python", "-m", "scripts.migrate_sqlite_to_postgres"]
    }]
  }'
```

### Step 4: Update Route53 DNS

After verifying green environment is healthy and data is migrated:

```bash
# Terraform will update Route53 to point to new ALB
terraform apply -var="create_new_vpc=true" -var="image_tag=bf60f25816d6c30ad6b8dbcd0a6d179b43a8d490"
```

This updates the Route53 record `demo.cinematch.umans.ai` to point to the new ALB.

### Step 5: Verify Production

```bash
# Wait for DNS propagation (up to 60 seconds)
sleep 60

# Test production URL
curl https://demo.cinematch.umans.ai/health
```

### Step 6: Cleanup (After Verification)

Once production is verified working on PostgreSQL:

```bash
# Remove create_new_vpc variable
# Destroy foundation VPC (if no longer needed)
# Update documentation
```

## Rollback Plan

If issues occur:

1. **Before Route53 update**: Simply destroy green environment and recreate blue from backup
2. **After Route53 update**: Update Route53 manually to point back to foundation ALB (if recreated)

## Critical Notes

- There will be **brief downtime** during this migration (~5-10 minutes)
- SQLite data backup must be restored to EFS before migration
- The migration script handles the SQLite → PostgreSQL data transfer
- All commits have been made to preserve history
